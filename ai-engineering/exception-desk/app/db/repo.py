"""Every query in the service lives here. No route handler writes SQL.

The reason is testability and reviewability: the persistence behaviour of the service can be
read in one file, and a change to it is obviously a change to the data layer.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import EvidenceRow, ExceptionRow, IngestJobRow, LlmCallRow

# normalise/source_hash are domain rules — what makes two messages "the same" is a property
# of the message, not of the database — so they live with the inventory master data.
from app.domain.inventory import normalise, source_hash
from app.domain.models import InventoryException
from app.llm.base import LlmCallRecord, ToolCallRecord

__all__ = [
    "claim_next_job",
    "cost_summary",
    "count_exceptions",
    "create_or_get_exception",
    "enqueue",
    "finish_job",
    "get_by_hash",
    "get_exception",
    "get_job",
    "list_exceptions",
    "mark_failed",
    "mark_pending",
    "mark_triaging",
    "normalise",
    "reclaim_stale_jobs",
    "requeue_job",
    "save_triage",
    "source_hash",
]


async def create_or_get_exception(
    session: AsyncSession,
    *,
    text: str,
    source_kind: str,
) -> tuple[ExceptionRow, bool]:
    """Insert an exception, or return the existing one. Returns ``(row, was_duplicate)``.

    ``ON CONFLICT DO NOTHING ... RETURNING`` yields no row on conflict, which is how the
    duplicate is detected without a race: two concurrent posts of the same text cannot both
    insert, because the unique index decides.
    """
    digest = source_hash(text)
    stmt = (
        pg_insert(ExceptionRow)
        .values(
            source_hash=digest,
            source_kind=source_kind,
            raw_text=normalise(text),
            status="pending",
        )
        .on_conflict_do_nothing(index_elements=["source_hash"])
        .returning(ExceptionRow.id)
    )
    result = await session.execute(stmt)
    new_id = result.scalar_one_or_none()
    await session.commit()

    if new_id is None:
        existing = await get_by_hash(session, digest)
        if existing is None:  # pragma: no cover - conflict implies a row exists
            raise RuntimeError(f"conflict on {digest} but no row found")
        return existing, True

    row = await get_exception(session, new_id)
    if row is None:  # pragma: no cover
        raise RuntimeError(f"inserted {new_id} but could not read it back")
    return row, False


async def get_by_hash(session: AsyncSession, digest: str) -> ExceptionRow | None:
    stmt = (
        select(ExceptionRow)
        .where(ExceptionRow.source_hash == digest)
        .options(selectinload(ExceptionRow.evidence), selectinload(ExceptionRow.llm_calls))
    )
    return (await session.execute(stmt)).scalar_one_or_none()


# --------------------------------------------------------------------------------------
# Triage lifecycle
# --------------------------------------------------------------------------------------


async def mark_triaging(session: AsyncSession, exception_id: uuid.UUID) -> None:
    row = await session.get(ExceptionRow, exception_id)
    if row is not None:
        row.status = "triaging"
        row.error = None
        await session.commit()


async def mark_pending(session: AsyncSession, exception_id: uuid.UUID) -> None:
    """Return a record to the queue after its job was requeued.

    Without this the record keeps saying ``triaging`` while nothing is triaging it, and
    ``GET /exceptions?status=triaging`` reports work in progress that is not happening.
    """
    row = await session.get(ExceptionRow, exception_id)
    if row is not None:
        row.status = "pending"
        await session.commit()


async def save_triage(
    session: AsyncSession,
    exception_id: uuid.UUID,
    *,
    record: InventoryException,
    evidence: Sequence[ToolCallRecord],
    calls: Sequence[LlmCallRecord],
    provider: str,
    model: str,
    prompt_version: str,
    cost_usd: Decimal,
    latency_ms: int,
    status: str = "needs_review",
) -> ExceptionRow:
    """Write the verdict, the evidence behind it, and the cost of getting there."""
    row = await session.get(ExceptionRow, exception_id)
    if row is None:
        raise LookupError(f"no exception {exception_id}")

    row.sku = record.sku
    row.severity = record.severity
    row.root_cause = record.root_cause
    row.weeks_of_cover = Decimal(str(record.weeks_of_cover))
    row.lead_time_impact_days = record.lead_time_impact_days
    row.recommended_action = record.recommended_action
    row.requires_escalation = record.requires_escalation
    row.confidence = Decimal(str(record.confidence))
    row.rationale = record.rationale

    row.provider = provider
    row.model = model
    row.prompt_version = prompt_version
    row.cost_usd = cost_usd
    row.triaged_at = datetime.now(UTC)
    row.status = status
    row.error = None

    session.add_all(
        EvidenceRow(
            exception_id=exception_id,
            round=call.round,
            tool=call.name,
            arguments=call.arguments,
            result=call.result,
            is_error=call.failed,
        )
        for call in evidence
    )
    session.add_all(
        LlmCallRow(
            exception_id=exception_id,
            provider=c.provider,
            model=c.model,
            prompt_version=c.prompt_version,
            input_tokens=c.input_tokens,
            output_tokens=c.output_tokens,
            cost_usd=c.cost_usd,
            latency_ms=c.latency_ms,
            retries=c.retries,
            outcome=c.outcome,
            error_class=c.error_class,
        )
        for c in calls
    )
    await session.commit()
    refreshed = await get_exception(session, exception_id)
    if refreshed is None:  # pragma: no cover
        raise RuntimeError(f"lost exception {exception_id} after save")
    return refreshed


async def mark_failed(session: AsyncSession, exception_id: uuid.UUID, error: str) -> None:
    row = await session.get(ExceptionRow, exception_id)
    if row is not None:
        row.status = "failed"
        row.error = error[:2000]
        await session.commit()


# --------------------------------------------------------------------------------------
# Reads
# --------------------------------------------------------------------------------------


async def get_exception(session: AsyncSession, exception_id: uuid.UUID) -> ExceptionRow | None:
    """Load one exception with its evidence, calls and decisions.

    ``populate_existing`` is required, not decorative: the row is already in this session's
    identity map from the ingest step, and without it SQLAlchemy returns the cached instance
    with the relationship collections still empty from before the triage was written. The
    symptom is a correct database and an API response claiming zero evidence.
    """
    stmt = (
        select(ExceptionRow)
        .where(ExceptionRow.id == exception_id)
        .options(
            selectinload(ExceptionRow.evidence),
            selectinload(ExceptionRow.llm_calls),
            selectinload(ExceptionRow.decisions),
        )
        .execution_options(populate_existing=True)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


async def list_exceptions(
    session: AsyncSession,
    *,
    status: str | None = None,
    severity: str | None = None,
    sku: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ExceptionRow]:
    stmt = select(ExceptionRow).order_by(ExceptionRow.received_at.desc())
    if status:
        stmt = stmt.where(ExceptionRow.status == status)
    if severity:
        stmt = stmt.where(ExceptionRow.severity == severity)
    if sku:
        stmt = stmt.where(ExceptionRow.sku == sku)
    stmt = stmt.limit(min(limit, 200)).offset(max(offset, 0))
    return list((await session.execute(stmt)).scalars().all())


async def count_exceptions(session: AsyncSession, *, status: str | None = None) -> int:
    stmt = select(func.count()).select_from(ExceptionRow)
    if status:
        stmt = stmt.where(ExceptionRow.status == status)
    return int((await session.execute(stmt)).scalar_one())


# --------------------------------------------------------------------------------------
# Cost
# --------------------------------------------------------------------------------------


async def cost_summary(session: AsyncSession, *, days: int = 7) -> list[dict[str, Any]]:
    """Tokens and USD grouped by provider and model over a rolling window."""
    since = datetime.now(UTC) - timedelta(days=max(days, 1))
    stmt = (
        select(
            LlmCallRow.provider,
            LlmCallRow.model,
            func.count().label("calls"),
            func.coalesce(func.sum(LlmCallRow.input_tokens), 0).label("input_tokens"),
            func.coalesce(func.sum(LlmCallRow.output_tokens), 0).label("output_tokens"),
            func.coalesce(func.sum(LlmCallRow.cost_usd), 0).label("cost_usd"),
        )
        .where(LlmCallRow.created_at >= since)
        .group_by(LlmCallRow.provider, LlmCallRow.model)
        .order_by(func.sum(LlmCallRow.cost_usd).desc())
    )
    rows = (await session.execute(stmt)).all()
    return [
        {
            "provider": r.provider,
            "model": r.model,
            "calls": int(r.calls),
            "input_tokens": int(r.input_tokens),
            "output_tokens": int(r.output_tokens),
            "cost_usd": Decimal(str(r.cost_usd or 0)),
        }
        for r in rows
    ]


# --------------------------------------------------------------------------------------
# Queue
# --------------------------------------------------------------------------------------


async def enqueue(session: AsyncSession, exception_id: uuid.UUID) -> uuid.UUID:
    """Create a job for this exception, or return the id of an already-active one.

    Safe to call repeatedly: the partial unique index ``uq_ingest_jobs_active_per_exception``
    allows at most one queued-or-running job per exception, so a client retrying a POST cannot
    enqueue a second triage and double the spend. The lookup below is an optimisation — the
    database is what actually guarantees it.
    """
    existing = await session.scalar(
        select(IngestJobRow.id)
        .where(
            IngestJobRow.exception_id == exception_id,
            IngestJobRow.status.in_(("queued", "running")),
        )
        .limit(1)
    )
    if existing is not None:
        return existing

    job = IngestJobRow(exception_id=exception_id, status="queued")
    session.add(job)
    await session.commit()
    return job.id


async def claim_next_job(session: AsyncSession, worker_id: str) -> IngestJobRow | None:
    """Claim exactly one due job, atomically.

    ``FOR UPDATE SKIP LOCKED`` is the correct Postgres queue primitive: two workers cannot
    claim the same job, and a slow job never blocks a fast one. ``available_at`` is what
    makes backoff possible — without it a failing job spins in a hot loop.

    ``attempts`` is incremented at claim time rather than on failure, so a worker killed
    mid-job still burns an attempt. Otherwise a job that reliably crashes its worker would
    retry forever.
    """
    subq = (
        select(IngestJobRow.id)
        .where(IngestJobRow.status == "queued", IngestJobRow.available_at <= func.now())
        .order_by(IngestJobRow.available_at)
        .with_for_update(skip_locked=True)
        .limit(1)
        .scalar_subquery()
    )
    stmt = select(IngestJobRow).where(IngestJobRow.id == subq)
    job = (await session.execute(stmt)).scalar_one_or_none()
    if job is None:
        return None
    job.status = "running"
    job.locked_by = worker_id
    job.locked_at = datetime.now(UTC)
    job.attempts += 1
    await session.commit()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> IngestJobRow | None:
    return await session.get(IngestJobRow, job_id)


async def requeue_job(
    session: AsyncSession,
    job_id: uuid.UUID,
    error: str,
    *,
    max_attempts: int = 5,
    retryable: bool = True,
) -> str:
    """Back the job off, or fail it for good. Returns the resulting status.

    ``retryable=False`` fails immediately regardless of the attempt count. That distinction
    matters: a 429 is worth retrying, a record the model could not produce after the repair
    loop is not — retrying costs money to reproduce the same failure.
    """
    job = await session.get(IngestJobRow, job_id)
    if job is None:
        return "missing"
    job.last_error = error[:2000]
    job.locked_by = None
    job.locked_at = None

    if not retryable or job.attempts >= max_attempts:
        job.status = "failed"
    else:
        job.status = "queued"
        # Exponential backoff, the same shape as the HTTP retry policy.
        job.available_at = datetime.now(UTC) + timedelta(seconds=2**job.attempts)

    await session.commit()
    return job.status


async def finish_job(session: AsyncSession, job_id: uuid.UUID) -> None:
    job = await session.get(IngestJobRow, job_id)
    if job is not None:
        job.status = "done"
        job.locked_by = None
        job.locked_at = None
        await session.commit()


async def reclaim_stale_jobs(
    session: AsyncSession, *, stale_after_s: int = 300
) -> list[uuid.UUID]:
    """Return jobs abandoned by a worker that died mid-run.

    A worker killed between claiming and finishing leaves its row in ``running`` forever, and
    the partial unique index means nothing can enqueue a replacement — the exception would be
    stuck with no way forward. This is the recovery path, and it is why ``locked_at`` exists.

    ``locked_at IS NULL`` is included so that rows written before this column existed (or by
    an older worker) are not stranded.
    """
    cutoff = datetime.now(UTC) - timedelta(seconds=max(stale_after_s, 1))
    stmt = (
        update(IngestJobRow)
        .where(
            IngestJobRow.status == "running",
            or_(IngestJobRow.locked_at.is_(None), IngestJobRow.locked_at < cutoff),
        )
        .values(
            status="queued",
            locked_by=None,
            locked_at=None,
            last_error="reclaimed: the worker holding this job did not finish in time",
        )
        .returning(IngestJobRow.id)
    )
    ids = list((await session.execute(stmt)).scalars().all())
    await session.commit()
    return ids
