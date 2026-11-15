"""The human decision, and the audit trail it leaves.

The premise of the whole service is "the model recommends, a human commits". These tests are
about the second half of that sentence: that approving *does* something, that rejecting does
not, and that a second decision cannot quietly overwrite the first.
"""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.config import Settings
from app.db import repo
from app.domain import inventory
from app.llm.mock import MockClient
from app.pipeline.worker import Worker

NOTE = (
    "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is "
    "fully committed through December, so we cannot confirm the Nov 14 date."
)
UNKNOWN_SKU_NOTE = "The supplier has not replied about anything at all this week."


def _worker() -> Worker:
    settings = Settings(llm_provider="mock")
    settings.worker_concurrency = 4
    return Worker(client=MockClient(), settings=settings)


async def _triaged(client: AsyncClient, note: str = NOTE) -> dict:
    """Post a message, run one worker batch, and return the finished record."""
    created = (await client.post("/exceptions", json={"text": note})).json()
    await _worker().run_once()
    return (await client.get(f"/exceptions/{created['exception_id']}")).json()


@pytest.fixture(autouse=True)
def clear_flag_ledger() -> None:
    """The domain's side-effect ledger is process-global, so each test starts empty."""
    inventory._FLAGGED.clear()


# --------------------------------------------------------------------------------------
# Preconditions
# --------------------------------------------------------------------------------------


async def test_deciding_an_unknown_exception_is_404(client: AsyncClient) -> None:
    r = await client.post(
        f"/exceptions/{uuid.uuid4()}/decision",
        json={"outcome": "approved", "final_action": "do something"},
    )
    assert r.status_code == 404


async def test_deciding_a_record_that_has_not_been_triaged_is_409(client: AsyncClient) -> None:
    """There is no recommendation to decide on yet, and 409 says 'wrong state' rather than
    'bad request'."""
    created = (await client.post("/exceptions", json={"text": NOTE})).json()
    r = await client.post(
        f"/exceptions/{created['exception_id']}/decision",
        json={"outcome": "approved", "final_action": "expedite"},
    )
    assert r.status_code == 409
    assert "no recommendation" in r.json()["detail"]


async def test_an_empty_action_is_rejected(client: AsyncClient) -> None:
    record = await _triaged(client)
    r = await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": ""},
    )
    assert r.status_code == 422


# --------------------------------------------------------------------------------------
# Approving
# --------------------------------------------------------------------------------------


async def test_approving_executes_the_action_through_the_tool_layer(client: AsyncClient) -> None:
    record = await _triaged(client)

    r = await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": record["recommended_action"]},
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["outcome"] == "approved"
    assert body["status"] == "decided"
    assert body["executed"] is not None
    assert body["executed"]["tool"] == "flag_exception"
    assert body["executed"]["ok"] is True
    assert body["executed"]["result"]["result"]["flagged"]["sku"] == "CHR-M4K25-RGB"


async def test_approving_lands_in_the_domain_layer(client: AsyncClient) -> None:
    """Verify the side effect, not the response. The response is a claim; `_FLAGGED` is what
    actually happened."""
    record = await _triaged(client)
    assert inventory._FLAGGED == []

    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "Expedite PO-88411"},
    )

    assert len(inventory._FLAGGED) == 1
    flagged = inventory._FLAGGED[0]
    assert flagged["sku"] == "CHR-M4K25-RGB"
    assert flagged["reason"] == "Expedite PO-88411"
    assert flagged["severity"] == record["severity"]


async def test_editing_executes_the_edited_action(client: AsyncClient) -> None:
    record = await _triaged(client)
    edited = "Pull 4 units from the EMEA buffer instead of expediting"

    body = (
        await client.post(
            f"/exceptions/{record['id']}/decision",
            json={"outcome": "edited", "final_action": edited, "note": "cheaper than freight"},
        )
    ).json()

    assert body["outcome"] == "edited"
    assert body["final_action"] == edited
    assert body["note"] == "cheaper than freight"
    # What ran is what the human wrote, not what the model proposed.
    assert inventory._FLAGGED[0]["reason"] == edited
    assert body["executed"]["result"]["result"]["flagged"]["reason"] == edited


async def test_the_record_moves_to_decided(client: AsyncClient) -> None:
    record = await _triaged(client)
    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "expedite"},
    )

    fetched = (await client.get(f"/exceptions/{record['id']}")).json()
    assert fetched["status"] == "decided"


async def test_the_decision_is_visible_in_the_audit_view(client: AsyncClient) -> None:
    """One request should tell you the verdict, the evidence, the provenance and the decision."""
    record = await _triaged(client)
    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={
            "outcome": "approved",
            "final_action": "expedite",
            "note": "checked with the planner",
        },
    )

    fetched = (await client.get(f"/exceptions/{record['id']}")).json()
    assert fetched["decision"] is not None
    assert fetched["decision"]["outcome"] == "approved"
    assert fetched["decision"]["note"] == "checked with the planner"
    assert fetched["decision"]["executed"]["tool"] == "flag_exception"


# --------------------------------------------------------------------------------------
# Rejecting
# --------------------------------------------------------------------------------------


async def test_rejecting_executes_nothing(client: AsyncClient) -> None:
    """The point of a rejection is that no action is taken."""
    record = await _triaged(client)

    body = (
        await client.post(
            f"/exceptions/{record['id']}/decision",
            json={
                "outcome": "rejected",
                "final_action": "no action",
                "note": "duplicate of PO-88410",
            },
        )
    ).json()

    assert body["outcome"] == "rejected"
    assert body["executed"] is None, "a rejection must not execute anything"
    assert inventory._FLAGGED == [], "a rejection must not touch the domain layer"
    # The decision is still recorded — the audit trail is the deliverable.
    assert body["note"] == "duplicate of PO-88410"


async def test_a_rejected_record_still_reports_the_decision(client: AsyncClient) -> None:
    record = await _triaged(client)
    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "rejected", "final_action": "no action"},
    )
    fetched = (await client.get(f"/exceptions/{record['id']}")).json()
    assert fetched["decision"]["outcome"] == "rejected"
    assert fetched["decision"]["executed"] is None


# --------------------------------------------------------------------------------------
# One decision only
# --------------------------------------------------------------------------------------


async def test_a_second_decision_is_a_409(client: AsyncClient) -> None:
    """Silently replacing an audit record defeats the point of having one."""
    record = await _triaged(client)
    first = await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "expedite"},
    )
    assert first.status_code == 200

    second = await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "rejected", "final_action": "no action"},
    )
    assert second.status_code == 409
    assert "already decided" in second.json()["detail"]


async def test_a_second_decision_does_not_execute_again(client: AsyncClient) -> None:
    record = await _triaged(client)
    payload = {"outcome": "approved", "final_action": "expedite"}
    await client.post(f"/exceptions/{record['id']}/decision", json=payload)
    await client.post(f"/exceptions/{record['id']}/decision", json=payload)

    assert len(inventory._FLAGGED) == 1, "a refused second decision must not act twice"


async def test_a_decided_record_is_not_requeued_by_a_repeat_post(client: AsyncClient) -> None:
    """`decided` is not a pending status, so a repost must not start the triage over."""
    record = await _triaged(client)
    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "expedite"},
    )

    again = (await client.post("/exceptions", json={"text": NOTE})).json()
    assert again["duplicate"] is True
    assert again["job_id"] is None
    assert again["status"] == "decided"
    assert (await _worker().run_once()).claimed == 0


# --------------------------------------------------------------------------------------
# Attribution and refusal
# --------------------------------------------------------------------------------------


async def test_the_reviewer_header_attributes_the_decision(client: AsyncClient) -> None:
    record = await _triaged(client)
    body = (
        await client.post(
            f"/exceptions/{record['id']}/decision",
            json={"outcome": "approved", "final_action": "expedite"},
            headers={"X-Reviewer": "m.avdian"},
        )
    ).json()
    assert body["decided_by"] == "m.avdian"


async def test_the_default_reviewer_is_used_when_no_header_is_sent(client: AsyncClient) -> None:
    record = await _triaged(client)
    body = (
        await client.post(
            f"/exceptions/{record['id']}/decision",
            json={"outcome": "approved", "final_action": "expedite"},
        )
    ).json()
    assert body["decided_by"] == "demo-reviewer"


async def test_a_blank_reviewer_header_falls_back(client: AsyncClient) -> None:
    record = await _triaged(client)
    body = (
        await client.post(
            f"/exceptions/{record['id']}/decision",
            json={"outcome": "approved", "final_action": "expedite"},
            headers={"X-Reviewer": "   "},
        )
    ).json()
    assert body["decided_by"] == "demo-reviewer"


async def test_a_refused_execution_is_recorded_rather_than_raising(client: AsyncClient) -> None:
    """The tool layer returns errors as data. A message naming no SKU cannot be flagged, and
    that has to end up in the audit trail instead of a 500."""
    record = await _triaged(client, UNKNOWN_SKU_NOTE)
    assert record["sku"] == "UNKNOWN"

    r = await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "ask the sender which part"},
    )

    assert r.status_code == 200, "a refused consequence must not fail the decision"
    body = r.json()
    assert body["executed"]["ok"] is False
    assert "unknown SKU" in body["executed"]["result"]["error"]
    # And the decision itself still stands.
    fetched = (await client.get(f"/exceptions/{record['id']}")).json()
    assert fetched["status"] == "decided"
    assert fetched["decision"]["executed"]["ok"] is False


async def test_the_executed_result_is_persisted(client: AsyncClient, session) -> None:
    """Reading it back from the database is the check that it was stored, not just echoed."""
    record = await _triaged(client)
    await client.post(
        f"/exceptions/{record['id']}/decision",
        json={"outcome": "approved", "final_action": "expedite"},
    )

    decision = await repo.get_decision(session, uuid.UUID(record["id"]))
    assert decision is not None
    assert decision.executed_tool == "flag_exception"
    assert decision.executed_result is not None
    assert decision.executed_result["result"]["flagged"]["sku"] == "CHR-M4K25-RGB"
