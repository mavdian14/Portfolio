"""Exception endpoints.

Week 1 serves the synchronous path: ``POST /triage`` runs the pipeline inline and persists
the result. That is the right shape for a demo and for the eval harness, and the wrong shape
for production — which is why week 2 adds ``POST /exceptions`` returning ``202`` plus a
worker, and this endpoint stays as the synchronous affordance.
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import ClientDep, SessionDep, SettingsDep, require_api_key
from app.db import repo
from app.db.models import ExceptionRow
from app.domain.inventory import source_kind_for
from app.domain.models import (
    EvidenceOut,
    ProvenanceOut,
    QueueItem,
    QueuePage,
    TriageRecordOut,
    TriageRequest,
)
from app.pipeline.triage import TriageOutcome, triage

logger = logging.getLogger(__name__)

# Auth sits on the router, not on each handler: a per-route dependency would need an
# unused parameter on every signature, and one forgotten route would be unguarded.
router = APIRouter(tags=["exceptions"], dependencies=[Depends(require_api_key)])


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
        duplicate=duplicate,
        error=row.error,
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
    # could produce a different verdict for the same input.
    if duplicate and row.status not in ("pending", "failed"):
        return _to_record(row, duplicate=True)

    await repo.mark_triaging(session, row.id)
    try:
        outcome: TriageOutcome = triage(payload.text, client=client, settings=settings)
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
