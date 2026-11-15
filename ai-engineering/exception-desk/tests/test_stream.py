"""Server-Sent Events.

The stream is the one place in the API that outlives its own request, so most of these tests
are about the edges: a record that is already finished, one that never finishes, and one that
does not exist.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from httpx import AsyncClient

from app.api.exceptions import _sse, _stream_events
from app.config import Settings
from app.db import repo
from app.db.session import get_sessionmaker
from app.llm.mock import MockClient
from app.pipeline.ingest import ingest
from app.pipeline.worker import Worker

NOTE = (
    "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is "
    "fully committed through December, so we cannot confirm the Nov 14 date."
)


def _worker() -> Worker:
    settings = Settings(llm_provider="mock")
    settings.worker_concurrency = 4
    return Worker(client=MockClient(), settings=settings)


async def _collect(client: AsyncClient, exception_id: str) -> list[tuple[str, dict[str, Any]]]:
    """Read a stream to exhaustion, returning (event, payload) pairs."""
    frames: list[tuple[str, dict[str, Any]]] = []
    async with client.stream("GET", f"/exceptions/{exception_id}/stream") as response:
        assert response.status_code == 200, await response.aread()
        assert response.headers["content-type"].startswith("text/event-stream")
        event: str | None = None
        async for line in response.aiter_lines():
            if line.startswith("event: "):
                event = line.removeprefix("event: ")
            elif line.startswith("data: ") and event:
                frames.append((event, json.loads(line.removeprefix("data: "))))
                event = None
    return frames


async def test_stream_404s_on_an_unknown_exception(client: AsyncClient) -> None:
    """Without an up-front check a bad id yields an empty stream that closes immediately,
    which a client cannot tell apart from 'nothing has happened yet'."""
    r = await client.get(f"/exceptions/{uuid.uuid4()}/stream")
    assert r.status_code == 404


async def test_stream_reports_status_changes_then_the_record(client: AsyncClient) -> None:
    created = (await client.post("/exceptions", json={"text": NOTE})).json()
    exception_id = created["exception_id"]

    async def triage_shortly() -> None:
        await asyncio.sleep(0.15)
        await _worker().run_once()

    worker_task = asyncio.create_task(triage_shortly())
    frames = await _collect(client, exception_id)
    await worker_task

    names = [name for name, _ in frames]
    assert names[0] == "status"
    assert names[-1] == "done", f"the stream must terminate with `done`, got {names}"
    assert "record" in names

    statuses = [payload["status"] for name, payload in frames if name == "status"]
    assert statuses[0] == "pending"
    assert "needs_review" in statuses, f"expected the terminal status in {statuses}"

    record = next(payload for name, payload in frames if name == "record")
    assert record["sku"] == "CHR-M4K25-RGB"
    assert record["evidence"], "the record frame must carry the audit view, not just the verdict"
    assert record["provenance"]["llm_calls"] >= 2

    done = next(payload for name, payload in frames if name == "done")
    assert done["status"] == "needs_review"


async def test_stream_on_an_already_triaged_record_closes_at_once(client: AsyncClient) -> None:
    """Connecting late is not a special case: the terminal state is emitted immediately."""
    created = (await client.post("/exceptions", json={"text": NOTE})).json()
    await _worker().run_once()

    frames = await asyncio.wait_for(_collect(client, created["exception_id"]), timeout=5)

    assert [name for name, _ in frames] == ["status", "record", "done"]
    assert frames[0][1]["status"] == "needs_review"


async def test_stream_emits_nothing_repeatedly(client: AsyncClient) -> None:
    """One `status` frame per change, not one per poll."""
    created = (await client.post("/exceptions", json={"text": NOTE})).json()
    await _worker().run_once()

    frames = await _collect(client, created["exception_id"])
    statuses = [p["status"] for n, p in frames if n == "status"]
    assert statuses == ["needs_review"], f"expected one status frame, got {statuses}"


async def test_stream_times_out_on_a_record_that_never_settles(session: Any) -> None:
    """Driven directly, because the alternative is a ten-second test."""
    outcome = await ingest(session, text=NOTE, source_kind="supplier_email")
    assert outcome.job_id is not None  # queued, and no worker will run

    settings = Settings(llm_provider="mock")
    settings.stream_max_seconds = 0.25
    settings.stream_poll_interval_s = 0.05
    settings.stream_heartbeat_s = 10.0

    frames = [frame async for frame in _stream_events(outcome.exception_id, settings)]

    assert any("event: timeout" in frame for frame in frames)
    assert not any("event: done" in frame for frame in frames)
    assert "reconnect" in frames[-1]


async def test_stream_stops_polling_once_terminal(session: Any) -> None:
    """The generator returns rather than looping forever — an open stream is a polling cost."""
    outcome = await ingest(session, text=NOTE, source_kind="supplier_email")
    await _worker().run_once()

    settings = Settings(llm_provider="mock")
    settings.stream_max_seconds = 10.0
    settings.stream_poll_interval_s = 0.05

    frames = [frame async for frame in _stream_events(outcome.exception_id, settings)]

    assert frames[-1].startswith("event: done")


async def test_frames_are_well_formed_sse() -> None:
    """A frame missing its terminating blank line makes the client buffer everything."""
    frame = _sse("status", {"status": "pending"})
    assert frame.startswith("event: status\n")
    assert frame.endswith("\n\n")
    assert json.loads(frame.split("data: ", 1)[1].strip()) == {"status": "pending"}


async def test_the_stream_does_not_hold_a_database_connection(session: Any) -> None:
    """One session per poll, not the request's. A pooled connection held for the life of a
    browser tab exhausts the pool after a handful of viewers."""
    outcome = await ingest(session, text=NOTE, source_kind="supplier_email")
    await _worker().run_once()

    settings = Settings(llm_provider="mock")
    settings.stream_max_seconds = 5.0
    settings.stream_poll_interval_s = 0.05

    # Hold every pooled connection, then drain a stream. If the stream kept one open for its
    # lifetime, this would deadlock rather than complete.
    frames = [frame async for frame in _stream_events(outcome.exception_id, settings)]
    assert frames

    async with get_sessionmaker()() as probe:
        assert await repo.get_exception(probe, outcome.exception_id) is not None
