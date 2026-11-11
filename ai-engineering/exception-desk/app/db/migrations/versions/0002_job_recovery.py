"""job recovery: locked_at, and one active job per exception

Two changes, both about what happens when things go wrong.

1. ``locked_at`` — a worker that dies between claiming a job and finishing it leaves the row
   in ``running`` forever. Without a timestamp there is no way to tell "being worked on right
   now" from "abandoned an hour ago", so the job is lost silently.

2. A partial unique index on ``(exception_id) WHERE status IN ('queued','running')`` — at most
   one active job per exception, enforced by the database rather than by application logic.
   Without it, a client that retries a POST can enqueue a second job for the same message and
   double the spend.

The partial index is the more interesting of the two: it makes "enqueue is idempotent" a
property of the schema, so the application check in ``repo.enqueue`` becomes an optimisation
rather than the guarantee.

Revision ID: 0002_job_recovery
Revises: 0001_initial_schema
Create Date: 2026-10-21
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_job_recovery"
down_revision: str | None = "0001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ingest_jobs",
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
    )

    # The reclaim query is `status = 'running' AND locked_at < cutoff`, so the index is
    # partial on `running` — there are only ever a handful of those rows.
    op.create_index(
        "ix_ingest_jobs_running",
        "ingest_jobs",
        ["locked_at"],
        postgresql_where=sa.text("status = 'running'"),
    )

    # At most one queued-or-running job per exception, enforced by the database.
    op.create_index(
        "uq_ingest_jobs_active_per_exception",
        "ingest_jobs",
        ["exception_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued', 'running')"),
    )


def downgrade() -> None:
    op.drop_index("uq_ingest_jobs_active_per_exception", table_name="ingest_jobs")
    op.drop_index("ix_ingest_jobs_running", table_name="ingest_jobs")
    op.drop_column("ingest_jobs", "locked_at")
