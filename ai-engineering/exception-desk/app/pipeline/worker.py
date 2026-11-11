"""The worker: claim due jobs, triage them, record what happened.

Run as its own process, so the API stays responsive and the worker can be scaled, restarted
and debugged independently:

    python -m app.pipeline.worker            # loop forever
    python -m app.pipeline.worker --once     # one batch, then exit
    docker compose --profile worker up

Why a separate process rather than a background task inside the API: an LLM call takes 5-30
seconds. Inside the API process, a burst of work competes with request handling for the same
event loop, and a crash takes the API down with it. A queue exists precisely so the two can
fail and scale apart.

Concurrency: the worker claims up to ``WORKER_CONCURRENCY`` jobs and awaits them together.
While one job waits on the provider, the others make progress — which is the entire reason the
pipeline is async. Each job gets its own database session.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import signal
import socket
import sys
import uuid
from dataclasses import dataclass

from app.config import Settings, get_settings
from app.db import repo
from app.db.session import dispose_engine, get_sessionmaker
from app.llm import make_client
from app.llm.base import BaseClient
from app.llm.retry import describe_error, is_retryable
from app.pipeline.triage import TerminalTriageError, triage

logger = logging.getLogger("exception_desk.worker")


def is_retryable_failure(exc: BaseException) -> bool:
    """Whether running the same job again could plausibly succeed.

    Two distinct kinds of failure, and conflating them is expensive:

    * **Terminal** — the pipeline produced nothing usable and said so. The model already had
      the validator's own error text and still could not satisfy the schema, so a retry pays
      for the same failure.
    * **Transient** — classified by the shared retry policy. A 429 is worth backing off for; a
      401 will fail identically forever.
    """
    if isinstance(exc, TerminalTriageError):
        return False
    return is_retryable(exc)


@dataclass
class BatchResult:
    claimed: int = 0
    done: int = 0
    requeued: int = 0
    failed: int = 0

    @property
    def busy(self) -> bool:
        return self.claimed > 0

    def __str__(self) -> str:
        return (
            f"claimed={self.claimed} done={self.done} "
            f"requeued={self.requeued} failed={self.failed}"
        )


class Worker:
    def __init__(
        self,
        *,
        client: BaseClient,
        settings: Settings | None = None,
        worker_id: str | None = None,
    ) -> None:
        self.client = client
        self.settings = settings or get_settings()
        # Identifies this worker in `locked_by`, which is how a stale lock is traced back to
        # the process that abandoned it.
        self.worker_id = worker_id or f"{socket.gethostname()}:{os.getpid()}"
        self._stopping = False

    # -- shutdown ----------------------------------------------------------------------
    def request_stop(self, *_: object) -> None:
        """Ask the loop to finish the current batch and exit. Safe to call twice."""
        if not self._stopping:
            logger.info("stop requested — finishing the current batch")
        self._stopping = True

    # -- recovery ----------------------------------------------------------------------
    async def reclaim_stale(self) -> int:
        """Return jobs abandoned by a worker that died, so they can be picked up again."""
        async with get_sessionmaker()() as session:
            ids = await repo.reclaim_stale_jobs(
                session, stale_after_s=self.settings.worker_stale_after_s
            )
        if ids:
            logger.warning(
                "reclaimed %d job(s) abandoned by a dead worker (stale after %ds): %s",
                len(ids),
                self.settings.worker_stale_after_s,
                ", ".join(str(i) for i in ids),
            )
        return len(ids)

    # -- claiming ----------------------------------------------------------------------
    async def claim(self, limit: int) -> list[uuid.UUID]:
        """Claim up to ``limit`` due jobs.

        One short transaction per claim, and only ids are kept — holding the ORM objects open
        across the batch would pin a database session for the whole duration of an LLM call.
        """
        claimed: list[uuid.UUID] = []
        async with get_sessionmaker()() as session:
            for _ in range(limit):
                job = await repo.claim_next_job(session, self.worker_id)
                if job is None:
                    break
                claimed.append(job.id)
        return claimed

    # -- processing --------------------------------------------------------------------
    async def process(self, job_id: uuid.UUID) -> str:
        """Run one job to completion in its own session. Returns the terminal job status."""
        async with get_sessionmaker()() as session:
            job = await repo.get_job(session, job_id)
            if job is None:
                logger.error("job %s disappeared before it could be processed", job_id)
                return "missing"

            exception_id = job.exception_id
            row = await repo.get_exception(session, exception_id)
            if row is None:
                await repo.requeue_job(
                    session, job_id, "exception row is missing", retryable=False
                )
                return "failed"

            await repo.mark_triaging(session, exception_id)
            try:
                outcome = await triage(row.raw_text, client=self.client, settings=self.settings)
            except Exception as exc:  # noqa: BLE001 - classified below, never swallowed
                retryable = is_retryable_failure(exc)
                status = await repo.requeue_job(
                    session,
                    job_id,
                    f"{type(exc).__name__}: {exc}",
                    max_attempts=self.settings.job_max_attempts,
                    retryable=retryable,
                )
                if retryable:
                    # The job is going back on the queue, so the record must stop claiming it
                    # is being worked on. Otherwise `status=triaging` reports work in progress
                    # that is not happening.
                    await repo.mark_pending(session, exception_id)
                else:
                    # Nothing will change on a retry, so fail the record too — otherwise the
                    # exception sits in `triaging` forever with no way for a human to see why.
                    await repo.mark_failed(session, exception_id, f"{type(exc).__name__}: {exc}")
                logger.log(
                    logging.WARNING if retryable else logging.ERROR,
                    "job %s -> %s (%s)",
                    job_id,
                    status,
                    describe_error(exc),
                )
                return status

            await repo.save_triage(
                session,
                exception_id,
                record=outcome.record,
                evidence=outcome.evidence,
                calls=outcome.calls,
                provider=outcome.provider,
                model=outcome.model,
                prompt_version=outcome.prompt_version,
                cost_usd=outcome.cost_usd,
                latency_ms=outcome.latency_ms,
            )
            await repo.finish_job(session, job_id)
            logger.info(
                "job %s done: %s %s/%s cover=%.2f evidence=%d calls=%d cost=%s in %dms",
                job_id,
                outcome.record.sku,
                outcome.record.severity,
                outcome.record.root_cause,
                outcome.record.weeks_of_cover,
                len(outcome.evidence),
                len(outcome.calls),
                outcome.cost_usd,
                outcome.latency_ms,
            )
            return "done"

    # -- the loop ----------------------------------------------------------------------
    async def run_once(self, *, max_jobs: int | None = None) -> BatchResult:
        """Reclaim abandoned jobs, then claim a batch and process it concurrently.

        The reclaim runs on *every* batch, not just at startup, because a one-shot run
        (``--once``, CI, a cron trigger) may be the only run there ever is. Putting it in the
        loop instead would mean a worker driven by ``--once`` never recovers anything.
        """
        await self.reclaim_stale()

        limit = max_jobs if max_jobs is not None else self.settings.worker_concurrency
        job_ids = await self.claim(limit)
        result = BatchResult(claimed=len(job_ids))
        if not job_ids:
            return result

        # return_exceptions=True: one job raising out of the batch must not abandon the others.
        # Every job is already marked in the database, so a lost exception is recoverable —
        # the lock goes stale and reclaim picks it up.
        outcomes = await asyncio.gather(
            *(self.process(job_id) for job_id in job_ids), return_exceptions=True
        )

        for job_id, outcome in zip(job_ids, outcomes, strict=True):
            if isinstance(outcome, BaseException):
                logger.exception(
                    "job %s raised out of the batch", job_id, exc_info=outcome
                )
                result.failed += 1
            elif outcome == "done":
                result.done += 1
            elif outcome == "queued":
                result.requeued += 1
            else:
                result.failed += 1
        return result

    async def run_forever(self) -> None:
        logger.info(
            "worker %s starting | concurrency=%d poll=%.1fs stale_after=%ds "
            "max_attempts=%d provider=%s model=%s",
            self.worker_id,
            self.settings.worker_concurrency,
            self.settings.worker_poll_interval_s,
            self.settings.worker_stale_after_s,
            self.settings.job_max_attempts,
            self.client.provider,
            self.client.model,
        )

        while not self._stopping:
            # run_once reclaims stale locks itself, so recovery happens on the same cadence as
            # the work and there is only one code path to reason about.
            result = await self.run_once()
            if result.busy:
                logger.debug("batch: %s", result)
            else:
                await asyncio.sleep(self.settings.worker_poll_interval_s)

        logger.info("worker %s stopped", self.worker_id)


# --------------------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.pipeline.worker",
        description=(
            "Claim due triage jobs from the ingest queue and run them. "
            "Runs until stopped with SIGINT/SIGTERM."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="process a single batch and exit (useful in CI and for demos)",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=None,
        help="jobs to claim per batch (default: WORKER_CONCURRENCY)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="override WORKER_CONCURRENCY for this run",
    )
    parser.add_argument(
        "--provider",
        default=None,
        help="override LLM_PROVIDER for this run (mock|anthropic|openai|ollama)",
    )
    parser.add_argument(
        "--fail-first-calls",
        type=int,
        default=0,
        metavar="N",
        help=(
            "demo/testing affordance: make the first N provider calls fail transiently, so "
            "the backoff and retry path can be watched. Mock provider only."
        ),
    )
    parser.add_argument("--log-level", default=None, help="override LOG_LEVEL")
    return parser


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        stream=sys.stdout,
    )


def _build_client(args: argparse.Namespace, settings: Settings) -> BaseClient:
    client = make_client(args.provider, settings=settings)  # type: ignore[arg-type]
    if args.fail_first_calls > 0:
        if not hasattr(client, "fail_first_n_calls"):
            raise SystemExit(
                f"--fail-first-calls only works with the mock provider "
                f"(provider={client.provider!r} cannot be told to fail on demand)"
            )
        client.fail_first_n_calls = args.fail_first_calls  # type: ignore[attr-defined]
        logger.warning(
            "failure injection on: the first %d provider call(s) will fail transiently",
            args.fail_first_calls,
        )
    return client


async def _run(args: argparse.Namespace, settings: Settings) -> int:
    client = _build_client(args, settings)
    worker = Worker(client=client, settings=settings)

    # Graceful shutdown: finish the batch in flight rather than dropping jobs mid-triage.
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError, AttributeError):  # not on Windows
            loop.add_signal_handler(sig, worker.request_stop)

    try:
        if args.once:
            result = await worker.run_once(max_jobs=args.max_jobs)
            logger.info("single batch: %s", result)
            return 0
        await worker.run_forever()
        return 0
    finally:
        await dispose_engine()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = get_settings()
    if args.concurrency is not None:
        settings.worker_concurrency = max(args.concurrency, 1)
    _configure_logging(args.log_level or settings.log_level)

    if settings.llm_provider == "mock" and not args.once:
        logger.warning(
            "LLM_PROVIDER=mock — jobs will be triaged against deterministic stand-ins. "
            "Set LLM_PROVIDER=anthropic|openai|ollama for real calls."
        )
    return asyncio.run(_run(args, settings))


if __name__ == "__main__":
    raise SystemExit(main())
