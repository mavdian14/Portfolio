"""Exception endpoints.

Week 1 serves the synchronous path: ``POST /triage`` runs the pipeline inline and persists
the result. That is the right shape for a demo and for the eval harness, and the wrong shape
for production — which is why week 2 adds ``POST /exceptions`` returning ``202`` plus a
worker, and this endpoint stays as the synchronous affordance.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.api.deps import ClientDep, SessionDep, SettingsDep, require_api_key
from app.config import Settings
from app.db import repo
from app.db.models import DecisionRow, ExceptionRow
from app.db.session import get_sessionmaker
from app.domain.inventory import VALID_SEVERITIES, run_tool, source_kind_for
from app.domain.models import (
    DecisionOut,
    DecisionOutcome,
    DecisionRequest,
    EvidenceOut,
    ExecutedActionOut,
    IngestResponse,
    ProvenanceOut,
    QueueItem,
    QueuePage,
    TriageRecordOut,
    TriageRequest,
)
from app.pipeline.ingest import PENDING_STATUSES, ingest
from app.pipeline.triage import TriageOutcome, triage

logger = logging.getLogger(__name__)

#: Statuses that mean the record has stopped moving, so the stream can close.
#: `pending` and `triaging` are transient; these three are not.
STREAM_TERMINAL_STATUSES = ("needs_review", "failed", "decided")

#: The one side-effecting tool in the domain. Approving runs this; rejecting runs nothing.
COMMIT_TOOL = "flag_exception"

# Auth sits on the router, not on each handler: a per-route dependency would need an
# unused parameter on every signature, and one forgotten route would be unguarded.
router = APIRouter(tags=["exceptions"], dependencies=[Depends(require_api_key)])


def _decision_out(decision: DecisionRow, *, status: str) -> DecisionOut:
    """Render a stored decision, including what its approval actually did."""
    executed: ExecutedActionOut | None = None
    if decision.executed_tool:
        result = decision.executed_result or {}
        executed = ExecutedActionOut(
            tool=decision.executed_tool,
            # The tool layer returns errors as data, so a refusal shows up here rather than
            # having raised out of the request.
            ok="error" not in result,
            result=result,
        )
    return DecisionOut(
        exception_id=decision.exception_id,
        status=status,
        decided_by=decision.decided_by,
        outcome=cast(DecisionOutcome, decision.outcome),
        final_action=decision.final_action,
        note=decision.note,
        decided_at=decision.decided_at,
        executed=executed,
    )


def _to_record(row: ExceptionRow, *, duplicate: bool = False) -> TriageRecordOut:
    """Assemble the audit view: the verdict, the evidence behind it, and its provenance."""
    calls = list(row.llm_calls or [])
    provenance = None
    if row.provider:
        provenance = ProvenanceOut(
            prompt_version=row.prompt_version or "unknown",
            provider=row.provider,
            model=row.model or "unknown",
            llm_calls=len(calls),
            input_tokens=sum(c.input_tokens for c in calls),
            output_tokens=sum(c.output_tokens for c in calls),
            cost_usd=row.cost_usd if row.cost_usd is not None else Decimal("0"),
            latency_ms=sum(c.latency_ms for c in calls),
            retries=sum(c.retries for c in calls),
        )

    return TriageRecordOut(
        id=row.id,
        status=row.status,
        source_kind=row.source_kind,
        raw_text=row.raw_text,
        received_at=row.received_at,
        triaged_at=row.triaged_at,
        sku=row.sku,
        severity=row.severity,
        root_cause=row.root_cause,
        weeks_of_cover=float(row.weeks_of_cover) if row.weeks_of_cover is not None else None,
        lead_time_impact_days=row.lead_time_impact_days,
        recommended_action=row.recommended_action,
        requires_escalation=row.requires_escalation,
        confidence=float(row.confidence) if row.confidence is not None else None,
        rationale=row.rationale,
        evidence=[
            EvidenceOut(
                round=e.round,
                tool=e.tool,
                arguments=e.arguments,
                result=e.result,
                is_error=e.is_error,
            )
            for e in (row.evidence or [])
        ],
        provenance=provenance,
        decision=(
            _decision_out(row.decisions[-1], status=row.status) if row.decisions else None
        ),
        duplicate=duplicate,
        error=row.error,
    )


@router.post(
    "/exceptions",
    response_model=IngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue one inbound message for triage",
    responses={202: {"description": "Accepted — a worker will triage it"}},
)
async def ingest_endpoint(
    payload: TriageRequest,
    session: SessionDep,
    settings: SettingsDep,
) -> IngestResponse:
    """Store the message and queue it, then return immediately.

    ``202`` rather than ``200`` because the work has not happened yet: a tool-calling request
    takes 5-30 seconds, and no proxy or client will hold a connection open that long. The
    response carries the job id for correlation; ``GET /exceptions/{id}`` reports the verdict
    once a worker has produced it.

    Safe to repeat. Identical text returns the same exception, and an exception that already
    has a queued or running job is not queued twice — enforced by a partial unique index, not
    just by application logic.
    """
    outcome = await ingest(session, text=payload.text, source_kind=payload.source_kind)
    return IngestResponse(
        exception_id=outcome.exception_id,
        job_id=outcome.job_id,
        status=outcome.status,
        duplicate=outcome.duplicate,
    )


@router.post(
    "/triage",
    response_model=TriageRecordOut,
    summary="Triage one inbound message, synchronously",
    responses={502: {"description": "The provider call failed"}},
)
async def triage_endpoint(
    payload: TriageRequest,
    session: SessionDep,
    client: ClientDep,
    settings: SettingsDep,
) -> TriageRecordOut:
    """Run the full pipeline on one message and persist the result.

    Re-posting identical text returns the existing record with ``duplicate: true`` rather
    than triaging it twice — the idempotency guarantee, visible in one call.
    """
    kind = payload.source_kind
    if kind == "unknown":
        kind = source_kind_for(payload.text)

    row, duplicate = await repo.create_or_get_exception(
        session, text=payload.text, source_kind=kind
    )

    # An already-triaged duplicate is returned as-is: re-running would double the cost and
    # could produce a different verdict for the same input. Shares the rule with ingest.py so
    # the sync and async paths cannot disagree about what "already done" means.
    if duplicate and row.status not in PENDING_STATUSES:
        return _to_record(row, duplicate=True)

    await repo.mark_triaging(session, row.id)
    try:
        outcome: TriageOutcome = await triage(payload.text, client=client, settings=settings)
    except Exception as exc:  # noqa: BLE001 - surfaced to the caller and recorded
        logger.exception("triage failed for exception %s", row.id)
        await repo.mark_failed(session, row.id, f"{type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"triage failed: {type(exc).__name__}",
        ) from exc

    saved = await repo.save_triage(
        session,
        row.id,
        record=outcome.record,
        evidence=outcome.evidence,
        calls=outcome.calls,
        provider=outcome.provider,
        model=outcome.model,
        prompt_version=outcome.prompt_version,
        cost_usd=outcome.cost_usd,
        latency_ms=outcome.latency_ms,
    )
    return _to_record(saved, duplicate=duplicate)


@router.get("/exceptions", response_model=QueuePage, summary="The triage queue")
async def list_endpoint(
    session: SessionDep,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    severity: Annotated[str | None, Query()] = None,
    sku: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> QueuePage:
    rows = await repo.list_exceptions(
        session, status=status_filter, severity=severity, sku=sku, limit=limit, offset=offset
    )
    return QueuePage(
        items=[
            QueueItem(
                id=r.id,
                status=r.status,
                source_kind=r.source_kind,
                sku=r.sku,
                severity=r.severity,
                root_cause=r.root_cause,
                confidence=float(r.confidence) if r.confidence is not None else None,
                received_at=r.received_at,
                cost_usd=r.cost_usd,
            )
            for r in rows
        ],
        count=len(rows),
    )




# --------------------------------------------------------------------------------------
# Live progress
# --------------------------------------------------------------------------------------


def _sse(event: str, data: dict[str, Any]) -> str:
    """One Server-Sent Events frame.

    The blank line is the frame terminator. Omit it and the client buffers everything until
    the connection closes, which looks exactly like a broken stream.
    """
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


async def _stream_events(exception_id: uuid.UUID, settings: Settings) -> AsyncIterator[str]:
    """Poll the record and emit a frame whenever something changes.

    Polling, not pub/sub, and deliberately so. The triage runs in a *separate process*, so the
    API has nothing to subscribe to: the worker commits to a table and this reads it. Making
    that push instead would mean LISTEN/NOTIFY, Redis or a broker — new infrastructure for a
    latency improvement measured in milliseconds against a job that takes seconds.
    """
    last_status: str | None = None
    deadline = time.monotonic() + settings.stream_max_seconds
    last_beat = time.monotonic()

    while True:
        # A session per poll, NOT the request's session. This generator outlives the request
        # dependency's scope, and holding one pooled connection open for the life of a browser
        # tab would exhaust the pool after a handful of viewers.
        async with get_sessionmaker()() as session:
            row = await repo.get_exception(session, exception_id)

        if row is None:
            yield _sse("error", {"detail": "the exception disappeared"})
            return

        if row.status != last_status:
            last_status = row.status
            yield _sse(
                "status",
                {"status": row.status, "sku": row.sku, "severity": row.severity},
            )

        if row.status in STREAM_TERMINAL_STATUSES:
            yield _sse("record", _to_record(row).model_dump(mode="json"))
            yield _sse("done", {"status": row.status})
            return

        now = time.monotonic()
        if now > deadline:
            yield _sse(
                "timeout",
                {
                    "status": row.status,
                    "waited_s": round(settings.stream_max_seconds, 1),
                    "detail": "still queued; reconnect to keep watching",
                },
            )
            return

        # A comment frame keeps intermediaries from closing an idle connection. Only sent on
        # the heartbeat cadence, so a fast-changing record is not padded with noise.
        if now - last_beat >= settings.stream_heartbeat_s:
            last_beat = now
            yield ": keepalive\n\n"

        await asyncio.sleep(settings.stream_poll_interval_s)


@router.get(
    "/exceptions/{exception_id}/stream",
    summary="Watch a record until it is triaged",
    response_class=StreamingResponse,
    responses={404: {"description": "No such exception"}},
)
async def stream_endpoint(
    exception_id: uuid.UUID,
    session: SessionDep,
    settings: SettingsDep,
) -> StreamingResponse:
    """Server-Sent Events carrying status changes, then the finished record.

    Events: ``status`` on every change, ``record`` with the full audit view once terminal,
    ``done`` as the terminator, and ``timeout`` if the record never settles. A record that is
    already terminal emits its events immediately and closes, so connecting late is not a
    special case.
    """
    # Check existence up front. Without this a bad id produces an empty stream that closes
    # immediately, which a client cannot distinguish from "nothing happened yet".
    if await repo.get_exception(session, exception_id) is None:
        raise HTTPException(status_code=404, detail=f"no exception {exception_id}")

    return StreamingResponse(
        _stream_events(exception_id, settings),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # nginx buffers proxied responses by default, which would hold every frame until
            # the stream ended. This header is the standard opt-out.
            "X-Accel-Buffering": "no",
        },
    )


# --------------------------------------------------------------------------------------
# The human decision
# --------------------------------------------------------------------------------------


def _execute_action(row: ExceptionRow, action: str) -> dict[str, Any]:
    """Run an approved action through the domain tool layer.

    Through ``run_tool`` rather than calling ``flag_exception`` directly, on purpose: the tool
    layer returns errors as data, so a refusal — an unknown SKU, an invalid severity — is
    *recorded* in the audit trail rather than raising out of the request. A decision whose
    consequence failed is still a decision, and both halves belong in the record.
    """
    severity = row.severity if row.severity in VALID_SEVERITIES else "medium"
    return run_tool(
        COMMIT_TOOL,
        {"sku": row.sku or "UNKNOWN", "reason": action, "severity": severity},
    )


@router.post(
    "/exceptions/{exception_id}/decision",
    response_model=DecisionOut,
    summary="Commit a human decision on a triaged record",
    responses={
        404: {"description": "No such exception"},
        409: {"description": "Not triaged yet, or already decided"},
    },
)
async def decide_endpoint(
    exception_id: uuid.UUID,
    payload: DecisionRequest,
    session: SessionDep,
    settings: SettingsDep,
    reviewer: Annotated[str | None, Header(alias="X-Reviewer")] = None,
) -> DecisionOut:
    """Approve, edit or reject the recommendation. One decision per record.

    ``approved`` and ``edited`` both execute ``final_action`` through the domain tool layer —
    the difference is only whether the human changed the wording first. ``rejected`` executes
    nothing, because the point of a rejection is that no action is taken.

    The decision is a one-time human act, so a second attempt is a ``409`` rather than an
    overwrite. Silently replacing an audit record would defeat the point of having one.
    """
    row = await repo.get_exception(session, exception_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"no exception {exception_id}")

    if row.status in ("pending", "triaging"):
        raise HTTPException(
            status_code=409,
            detail=f"the record is {row.status} — there is no recommendation to decide on yet",
        )

    if row.decisions:
        first = row.decisions[-1]
        raise HTTPException(
            status_code=409,
            detail=(
                f"already decided {first.outcome} by {first.decided_by} "
                f"at {first.decided_at.isoformat()}"
            ),
        )

    decided_by = (reviewer or "").strip() or settings.default_reviewer

    executed_tool: str | None = None
    executed_result: dict[str, Any] | None = None
    if payload.outcome in ("approved", "edited"):
        executed_tool = COMMIT_TOOL
        executed_result = _execute_action(row, payload.final_action)
        if "error" in executed_result:
            logger.warning(
                "decision on %s executed with an error: %s",
                exception_id,
                executed_result["error"],
            )

    decision = await repo.create_decision(
        session,
        exception_id,
        decided_by=decided_by,
        outcome=payload.outcome,
        final_action=payload.final_action,
        note=payload.note,
        executed_tool=executed_tool,
        executed_result=executed_result,
    )
    logger.info(
        "exception %s decided %s by %s (executed=%s)",
        exception_id,
        payload.outcome,
        decided_by,
        executed_tool or "nothing",
    )
    return _decision_out(decision, status="decided")


@router.get(
    "/exceptions/{exception_id}",
    response_model=TriageRecordOut,
    summary="One record, with the evidence behind it",
)
async def get_endpoint(
    exception_id: uuid.UUID,
    session: SessionDep,
) -> TriageRecordOut:
    row = await repo.get_exception(session, exception_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"no exception {exception_id}")
    return _to_record(row)
