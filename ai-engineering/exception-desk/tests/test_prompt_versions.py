"""Prompt versioning.

The claim being tested is not "prompts are versioned" — it is "changing the prompt changes the
answer, and you can show which version produced which answer". A versioning scheme that cannot
demonstrate a difference is documentation, not engineering.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.domain.prompt_loader import (
    PromptNotFound,
    available_prompts,
    available_versions,
    load_prompt,
    prompt_exists,
    render,
)
from app.llm import make_client
from app.llm.mock import MockClient
from app.pipeline.ingest import ingest
from app.pipeline.triage import triage
from app.pipeline.worker import Worker

#: The message that separates the two calibrations. It says "zero on hand" — alarming phrasing
#: — about a part that has 5 weeks of cover and 62 days of slippage.
TRAP_NOTE = (
    "Control board PCB-CTRL-M4K is at zero on hand with 4 allocated to service jobs. "
    "Vektor has quoted 90 days and we are seeing 152 days actual."
)


def _settings(version: str) -> Settings:
    settings = Settings(llm_provider="mock")
    settings.prompt_version = version
    return settings


async def _triage(note: str, version: str):
    client = MockClient(prompt_version=version)
    return await triage(note, client=client, settings=_settings(version))


# --------------------------------------------------------------------------------------
# The files
# --------------------------------------------------------------------------------------


def test_every_version_is_complete() -> None:
    """A version is only usable if all three prompts exist — the pipeline renders all three."""
    for version in available_versions("triage_system"):
        for name in ("triage_system", "triage_extract", "repair"):
            assert prompt_exists(name, version), f"{name}.{version}.md is missing"


def test_both_versions_are_available() -> None:
    assert available_versions("triage_system") == ["v1", "v2"]
    assert "triage_extract.v2" in available_prompts()


def test_the_versions_genuinely_differ() -> None:
    """If v2 were a copy of v1 the comparison would prove nothing."""
    for name in ("triage_system", "triage_extract"):
        assert load_prompt(name, "v1") != load_prompt(name, "v2"), f"{name} v1 and v2 are identical"


def test_v2_forbids_the_keyword_shortcut() -> None:
    """The change has to be legible in the prompt, not just in the outcome."""
    assert "zero on hand" in load_prompt("triage_system", "v2")
    assert "never from the wording" in load_prompt("triage_system", "v2")


def test_an_unknown_version_fails_loudly() -> None:
    with pytest.raises(PromptNotFound, match="Available:"):
        load_prompt("triage_system", "v9")
    assert not prompt_exists("triage_system", "v9")


def test_rendering_still_substitutes() -> None:
    prompt = render("triage_extract", "v2", message="hello", evidence="(none)")
    assert "hello" in prompt
    assert "by this rule and no other" in prompt


# --------------------------------------------------------------------------------------
# The difference
# --------------------------------------------------------------------------------------


async def test_v1_escalates_on_alarming_phrasing() -> None:
    """v1 treats "zero on hand" as a severity signal, whatever the numbers say."""
    outcome = await _triage(TRAP_NOTE, "v1")
    assert outcome.record.severity == "critical"
    # The numbers it was looking at do not support critical.
    assert outcome.record.weeks_of_cover == 5.0
    assert outcome.record.lead_time_impact_days == 62


async def test_v2_calibrates_from_the_numbers() -> None:
    """v2 requires both a coverage problem and material slippage for critical. This part has
    heavy slippage and comfortable cover, so it is high, not critical."""
    outcome = await _triage(TRAP_NOTE, "v2")
    assert outcome.record.severity == "high"


async def test_the_two_versions_disagree_on_the_same_input() -> None:
    """The demonstration. Same message, same tools, same data — different verdict, and the
    record says which prompt produced it."""
    v1 = await _triage(TRAP_NOTE, "v1")
    v2 = await _triage(TRAP_NOTE, "v2")

    assert v1.record.severity != v2.record.severity
    assert (v1.record.severity, v2.record.severity) == ("critical", "high")

    # Everything else about the extraction is unchanged, which is what makes it a calibration
    # change rather than a rewrite.
    assert v1.record.sku == v2.record.sku
    assert v1.record.root_cause == v2.record.root_cause
    assert v1.record.weeks_of_cover == v2.record.weeks_of_cover
    assert v1.record.lead_time_impact_days == v2.record.lead_time_impact_days


async def test_a_genuinely_critical_record_is_critical_under_both() -> None:
    """v2 is stricter, not blind: a part that is out of runway *and* waiting on a late
    supplier still comes out critical.

    The SKU code has to be in the message. The offline provider matches codes, not prose, so
    "the M 4K25 RGB" without "(CHR-M4K25-RGB)" resolves to UNKNOWN and no position is checked
    at all — see the README's note on what offline mode cannot tell you.
    """
    note = (
        "M 4K25 RGB (CHR-M4K25-RGB) — on hand 3, but 12 are already allocated to the Toronto "
        "showroom install. Nordlicht has pushed the quoted 45-day lead time out to 68 days."
    )
    v1 = await _triage(note, "v1")
    v2 = await _triage(note, "v2")
    assert v1.record.severity == "critical"
    assert v2.record.severity == "critical"


# --------------------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------------------


async def test_the_version_is_recorded_on_the_outcome() -> None:
    outcome = await _triage(TRAP_NOTE, "v2")
    assert outcome.prompt_version == "v2"
    assert all(call.prompt_version == "v2" for call in outcome.calls)


async def test_the_version_reaches_the_database(session: AsyncSession) -> None:
    """A version recorded only in memory cannot answer 'which prompt produced this record'."""
    from app.db import repo

    outcome = await ingest(session, text=TRAP_NOTE, source_kind="supplier_email")
    worker = Worker(
        client=MockClient(prompt_version="v2"), settings=_settings("v2")
    )
    assert (await worker.run_once()).done == 1

    record = await repo.get_exception(session, outcome.exception_id)
    assert record is not None
    assert record.prompt_version == "v2"
    assert record.severity == "high"
    assert all(call.prompt_version == "v2" for call in record.llm_calls)


async def test_the_version_is_visible_through_the_api(session: AsyncSession) -> None:
    """Recorded in the database is not enough — 'which prompt produced this?' has to be
    answerable from the API, or the comparison is only visible to someone with a psql shell."""
    from httpx import ASGITransport, AsyncClient

    from app.main import create_app

    app = create_app()
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            created = (await client.post("/exceptions", json={"text": TRAP_NOTE})).json()
            worker = Worker(
                client=MockClient(prompt_version="v2"), settings=_settings("v2")
            )
            assert (await worker.run_once()).done == 1

            record = (await client.get(f"/exceptions/{created['exception_id']}")).json()

    assert record["provenance"]["prompt_version"] == "v2"
    assert record["severity"] == "high"
    assert record["provenance"]["llm_calls"] == 2


def test_make_client_passes_the_version_to_the_mock() -> None:
    """Otherwise a v2 run would still be graded by v1's rules and the comparison would be a
    lie."""
    settings = Settings(llm_provider="mock")
    settings.prompt_version = "v2"
    client = make_client("mock", settings=settings)
    assert isinstance(client, MockClient)
    assert client.prompt_version == "v2"


async def test_the_worker_cli_can_switch_version(session: AsyncSession) -> None:
    """Adding a prompt file is the mechanism; a flag is how you exercise it."""
    from app.pipeline.worker import build_parser

    args = build_parser().parse_args(["--once", "--prompt-version", "v2"])
    assert args.prompt_version == "v2"
