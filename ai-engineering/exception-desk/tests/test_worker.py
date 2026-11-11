"""The queue and the worker.

These tests are about behaviour under things going wrong, which is the only interesting
property a queue has: two workers racing, a job that fails, a worker that dies holding a lock.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.db import repo
from app.db.session import get_engine, get_sessionmaker
from app.llm import mock_error
from app.llm.mock import MockClient
from app.pipeline.ingest import ingest
from app.pipeline.triage import TerminalTriageError
from app.pipeline.worker import Worker, is_retryable_failure

NOTE_A = (
    "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is "
    "fully committed through December, so we cannot confirm the Nov 14 date."
)
NOTE_B = (
    "Control board PCB-CTRL-M4K is at zero on hand with 4 allocated to service jobs. "
    "Vektor has quoted 90 days and we are seeing 152 days actual."
)
NOTE_C = (
    "LNS-200-355 demand came in nearly double forecast for the quarter and we have 5 on hand "
    "against 11 allocated."
)
NOTE_D = "GS Series CHR-GS25-HS units look fine. No action needed, flagging for a status pass."


def _settings(**overrides: object) -> Settings:
    """A fresh Settings per test — never the cached singleton, which would leak between tests."""
    settings = Settings(llm_provider="mock")
    settings.worker_concurrency = 4
    settings.worker_poll_interval_s = 0.01
    settings.worker_stale_after_s = 300
    settings.job_max_attempts = 5
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


class RaisingClient(MockClient):
    """Fails the first tool-loop call, the way a provider outage would."""

    def __init__(self, exc: BaseException) -> None:
        super().__init__()
        self._exc = exc
        self.calls = 0

    async def atool_loop(self, prompt: str, **kwargs: object) -> object:  # type: ignore[override]
        self.calls += 1
        raise self._exc


async def _queue(session: AsyncSession, message: str) -> tuple[uuid.UUID, uuid.UUID]:
    outcome = await ingest(session, text=message, source_kind="supplier_email")
    assert outcome.job_id is not None, "ingest should have queued a job"
    return outcome.exception_id, outcome.job_id


async def _job_row(session: AsyncSession, job_id: uuid.UUID) -> dict:
    row = (
        await session.execute(
            text(
                "SELECT status, attempts, locked_by, locked_at, last_error, available_at "
                "FROM ingest_jobs WHERE id = :i"
            ),
            {"i": job_id},
        )
    ).mappings().one()
    return dict(row)


# --------------------------------------------------------------------------------------
# Enqueue
# --------------------------------------------------------------------------------------


async def test_enqueue_is_idempotent_while_a_job_is_active(session: AsyncSession) -> None:
    """A client retrying a POST must not double the spend."""
    exception_id, first = await _queue(session, NOTE_A)
    again = await repo.enqueue(session, exception_id)
    assert again == first


async def test_the_database_refuses_a_second_active_job(session: AsyncSession) -> None:
    """The guarantee is the partial unique index, not the application check above it."""
    exception_id, _ = await _queue(session, NOTE_A)
    with pytest.raises(IntegrityError):
        await session.execute(
            text("INSERT INTO ingest_jobs (exception_id, status) VALUES (:e, 'queued')"),
            {"e": exception_id},
        )
        await session.commit()
    await session.rollback()


async def test_a_finished_job_does_not_block_a_new_one(session: AsyncSession) -> None:
    """The index is partial on active statuses, so a done job frees the exception again."""
    exception_id, first = await _queue(session, NOTE_A)
    await repo.finish_job(session, first)
    second = await repo.enqueue(session, exception_id)
    assert second != first


# --------------------------------------------------------------------------------------
# Claiming
# --------------------------------------------------------------------------------------


async def test_claim_returns_none_when_nothing_is_due(session: AsyncSession) -> None:
    assert await repo.claim_next_job(session, "worker-a") is None


async def test_claim_marks_the_job_running_and_stamps_the_lock(session: AsyncSession) -> None:
    _, job_id = await _queue(session, NOTE_A)
    job = await repo.claim_next_job(session, "worker-a")

    assert job is not None and job.id == job_id
    row = await _job_row(session, job_id)
    assert row["status"] == "running"
    assert row["locked_by"] == "worker-a"
    assert row["locked_at"] is not None
    # attempts is incremented at claim time, so a worker killed mid-job still burns one.
    assert row["attempts"] == 1


async def test_a_job_in_the_future_is_not_claimed(session: AsyncSession) -> None:
    _, job_id = await _queue(session, NOTE_A)
    await session.execute(
        text("UPDATE ingest_jobs SET available_at = now() + interval '1 hour' WHERE id = :i"),
        {"i": job_id},
    )
    await session.commit()
    assert await repo.claim_next_job(session, "worker-a") is None


async def test_a_locked_job_is_skipped_not_waited_for(session: AsyncSession) -> None:
    """FOR UPDATE SKIP LOCKED.

    A second worker must take the *next* job rather than block on the one already claimed.
    Without SKIP LOCKED this test times out rather than failing an assertion — which is exactly
    what a blocked worker looks like in production.
    """
    first_exception, first_job = await _queue(session, NOTE_A)
    second_exception, second_job = await _queue(session, NOTE_B)
    assert first_exception != second_exception

    # Deterministic order: the first job is due earlier than the second.
    await session.execute(
        text("UPDATE ingest_jobs SET available_at = now() - interval '1 second' WHERE id = :i"),
        {"i": first_job},
    )
    await session.execute(
        text("UPDATE ingest_jobs SET available_at = now() WHERE id = :i"), {"i": second_job}
    )
    await session.commit()

    engine = get_engine()
    async with engine.connect() as blocker:
        trans = await blocker.begin()
        # Hold a row lock on the first job, as a worker would mid-claim.
        await blocker.execute(
            text("SELECT id FROM ingest_jobs WHERE id = :i FOR UPDATE"), {"i": first_job}
        )

        async with get_sessionmaker()() as claimer:
            claimed = await asyncio.wait_for(
                repo.claim_next_job(claimer, "worker-b"), timeout=5
            )

        await trans.rollback()

    assert claimed is not None, "the second worker should have taken the unlocked job"
    assert claimed.id == second_job, "the locked job should have been skipped, not claimed"


# --------------------------------------------------------------------------------------
# Processing
# --------------------------------------------------------------------------------------


async def test_worker_triages_a_batch_and_records_evidence(session: AsyncSession) -> None:
    exception_id, job_id = await _queue(session, NOTE_A)
    worker = Worker(client=MockClient(), settings=_settings())

    result = await worker.run_once()

    assert result.claimed == 1 and result.done == 1 and result.failed == 0
    row = await _job_row(session, job_id)
    assert row["status"] == "done" and row["locked_at"] is None

    record = await repo.get_exception(session, exception_id)
    assert record is not None
    assert record.status == "needs_review"
    assert record.sku == "CHR-M4K25-RGB"
    assert record.evidence, "a worker-triaged record must carry its evidence"
    assert record.llm_calls, "a worker-triaged record must carry its cost"


async def test_a_second_batch_claims_nothing(session: AsyncSession) -> None:
    await _queue(session, NOTE_A)
    worker = Worker(client=MockClient(), settings=_settings())
    assert (await worker.run_once()).claimed == 1
    assert (await worker.run_once()).claimed == 0


async def test_worker_processes_jobs_concurrently(session: AsyncSession) -> None:
    """The concurrency claim, measured rather than asserted.

    Four jobs, two provider calls each. Serialised that is 8 x delay; concurrent it is
    2 x delay. The threshold sits between the two.
    """
    for message in (NOTE_A, NOTE_B, NOTE_C, NOTE_D):
        await _queue(session, message)

    delay = 0.15
    worker = Worker(client=MockClient(async_delay_s=delay), settings=_settings())

    started = time.perf_counter()
    result = await worker.run_once()
    elapsed = time.perf_counter() - started

    serialised = delay * 2 * 4  # 4 jobs, 2 provider calls each
    assert result.done == 4
    assert elapsed < serialised * 0.6, (
        f"4 jobs took {elapsed:.2f}s against a serialised {serialised:.2f}s — "
        "that is serial, not concurrent"
    )


# --------------------------------------------------------------------------------------
# Failure
# --------------------------------------------------------------------------------------


async def test_a_transient_failure_requeues_with_backoff(session: AsyncSession) -> None:
    exception_id, job_id = await _queue(session, NOTE_A)
    client = RaisingClient(mock_error("RateLimitError", "slow down", 429, retry_after=0.01))
    worker = Worker(client=client, settings=_settings())

    result = await worker.run_once()

    assert result.requeued == 1 and result.failed == 0
    row = await _job_row(session, job_id)
    assert row["status"] == "queued"
    assert row["attempts"] == 1
    assert row["locked_at"] is None, "the lock must be released so another worker can take it"
    assert "RateLimitError" in row["last_error"]
    # Backoff: the job must not be due again immediately, or the worker spins on it.
    # attempts == 1, so the delay is 2 ** 1 = 2 seconds.
    due_in = (row["available_at"] - datetime.now(UTC)).total_seconds()
    assert 0 < due_in <= 2.5, f"expected roughly a 2s backoff, got {due_in:.1f}s"

    # The record must stop claiming it is being worked on, or `status=triaging` reports work
    # in progress that is not happening.
    record = await repo.get_exception(session, exception_id)
    assert record is not None and record.status == "pending"


async def test_a_transient_failure_then_succeeds_on_retry(session: AsyncSession) -> None:
    """The done-criterion: a forced provider failure retries, and then succeeds."""
    exception_id, job_id = await _queue(session, NOTE_A)

    # First batch: the provider is down.
    failing = Worker(
        client=RaisingClient(mock_error("APIConnectionError", "connection reset", None)),
        settings=_settings(),
    )
    assert (await failing.run_once()).requeued == 1

    # Make it due immediately rather than waiting out the backoff.
    await session.execute(
        text("UPDATE ingest_jobs SET available_at = now() WHERE id = :i"), {"i": job_id}
    )
    await session.commit()

    # Second batch: the provider is healthy.
    healthy = Worker(client=MockClient(), settings=_settings())
    assert (await healthy.run_once()).done == 1

    record = await repo.get_exception(session, exception_id)
    assert record is not None and record.status == "needs_review" and record.evidence


async def test_a_terminal_failure_fails_the_job_and_the_record(session: AsyncSession) -> None:
    """Retrying a schema the model could not satisfy pays to reproduce the same failure."""
    exception_id, job_id = await _queue(session, NOTE_A)
    worker = Worker(
        client=RaisingClient(TerminalTriageError("could not satisfy the schema")),
        settings=_settings(),
    )

    result = await worker.run_once()

    assert result.failed == 1 and result.requeued == 0
    assert (await _job_row(session, job_id))["status"] == "failed"
    record = await repo.get_exception(session, exception_id)
    assert record is not None
    assert record.status == "failed"
    # The record must say why, or a human has no way to act on it.
    assert record.error and "TerminalTriageError" in record.error


async def test_a_job_is_failed_after_max_attempts(session: AsyncSession) -> None:
    _, job_id = await _queue(session, NOTE_A)
    await session.execute(
        text("UPDATE ingest_jobs SET attempts = 5 WHERE id = :i"), {"i": job_id}
    )
    await session.commit()

    worker = Worker(
        client=RaisingClient(mock_error("RateLimitError", "slow down", 429)),
        settings=_settings(job_max_attempts=5),
    )
    assert (await worker.run_once()).failed == 1
    assert (await _job_row(session, job_id))["status"] == "failed"


@pytest.mark.parametrize(
    ("exc", "retryable"),
    [
        (TerminalTriageError("bad schema"), False),
        (mock_error("RateLimitError", "429", 429), True),
        (mock_error("APIConnectionError", "reset", None), True),
        (mock_error("InternalServerError", "500", 500), True),
        (mock_error("AuthenticationError", "bad key", 401), False),
        (mock_error("BadRequestError", "bad payload", 400), False),
    ],
)
def test_failure_classification(exc: BaseException, retryable: bool) -> None:
    assert is_retryable_failure(exc) is retryable


# --------------------------------------------------------------------------------------
# Recovery
# --------------------------------------------------------------------------------------


async def test_stale_locks_are_reclaimed(session: AsyncSession) -> None:
    """A worker killed mid-job leaves `running` behind, and nothing else can clear it."""
    _, job_id = await _queue(session, NOTE_A)
    await repo.claim_next_job(session, "worker-that-died")
    await session.execute(
        text("UPDATE ingest_jobs SET locked_at = now() - interval '2 hours' WHERE id = :i"),
        {"i": job_id},
    )
    await session.commit()

    reclaimed = await repo.reclaim_stale_jobs(session, stale_after_s=300)

    assert reclaimed == [job_id]
    row = await _job_row(session, job_id)
    assert row["status"] == "queued"
    assert row["locked_by"] is None and row["locked_at"] is None
    assert "reclaimed" in row["last_error"]


async def test_run_once_reclaims_a_stale_job_before_claiming(session: AsyncSession) -> None:
    """A one-shot run may be the only run there ever is, so it must recover orphans too.

    Regression: reclaim used to live only in `run_forever`, so `--once` — the CI and cron
    path — left an abandoned job stuck in `running` forever.
    """
    exception_id, job_id = await _queue(session, NOTE_A)
    await repo.claim_next_job(session, "worker-that-died")
    await session.execute(
        text("UPDATE ingest_jobs SET locked_at = now() - interval '2 hours' WHERE id = :i"),
        {"i": job_id},
    )
    await session.commit()

    result = await Worker(client=MockClient(), settings=_settings()).run_once()

    assert result.claimed == 1 and result.done == 1
    record = await repo.get_exception(session, exception_id)
    assert record is not None and record.status == "needs_review"
    assert (await _job_row(session, job_id))["status"] == "done"


async def test_a_fresh_lock_is_not_reclaimed(session: AsyncSession) -> None:
    """Reclaiming a job that is genuinely in flight would run it twice."""
    _, job_id = await _queue(session, NOTE_A)
    await repo.claim_next_job(session, "worker-still-working")

    assert await repo.reclaim_stale_jobs(session, stale_after_s=300) == []
    assert (await _job_row(session, job_id))["status"] == "running"


async def test_a_reclaimed_job_can_be_claimed_again(session: AsyncSession) -> None:
    _, job_id = await _queue(session, NOTE_A)
    await repo.claim_next_job(session, "worker-that-died")
    await session.execute(
        text("UPDATE ingest_jobs SET locked_at = now() - interval '2 hours' WHERE id = :i"),
        {"i": job_id},
    )
    await session.commit()
    await repo.reclaim_stale_jobs(session, stale_after_s=300)

    job = await repo.claim_next_job(session, "worker-alive")
    assert job is not None and job.id == job_id
    assert (await _job_row(session, job_id))["attempts"] == 2


async def test_reclaim_is_safe_to_run_when_nothing_is_stale(session: AsyncSession) -> None:
    await _queue(session, NOTE_A)
    assert await repo.reclaim_stale_jobs(session, stale_after_s=300) == []


# --------------------------------------------------------------------------------------
# Shutdown
# --------------------------------------------------------------------------------------


async def test_stop_request_ends_the_loop(session: AsyncSession) -> None:
    """Graceful shutdown: the loop exits after the batch in flight, not mid-job."""
    worker = Worker(client=MockClient(), settings=_settings())
    worker.request_stop()
    # No jobs queued, and the loop must notice the flag and return rather than spin.
    await asyncio.wait_for(worker.run_forever(), timeout=5)
