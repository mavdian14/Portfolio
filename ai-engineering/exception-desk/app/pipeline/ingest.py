"""Ingest: take an inbound message, store it, and put it in the queue.

The whole flow lives here rather than in the route handler, for the same reason the triage
pipeline lives outside the API: this is the part that has to be correct, and it should be
callable and testable without a web server.

Three steps, in order:

1. **Normalise and hash.** ``normalise`` collapses whitespace and canonicalises SKU casing
   *before* ``source_hash`` runs. Hashing the raw text would make the same supplier email with
   a trailing newline a second exception.
2. **Create or find.** ``ON CONFLICT DO NOTHING`` on the unique hash means the database, not
   application logic, decides whether this is a duplicate.
3. **Enqueue.** Unless the exception has already been triaged. Re-triaging a duplicate would
   double the cost and could produce a different verdict for identical input.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import repo
from app.domain.inventory import source_kind_for

#: Statuses that mean "there is nothing to do yet, or it is worth trying again".
#: Anything else is a finished record and must not be re-triaged.
PENDING_STATUSES = ("pending", "failed")


@dataclass
class IngestOutcome:
    exception_id: uuid.UUID
    status: str
    duplicate: bool
    job_id: uuid.UUID | None = None

    @property
    def queued(self) -> bool:
        return self.job_id is not None


async def ingest(
    session: AsyncSession,
    *,
    text: str,
    source_kind: str = "unknown",
) -> IngestOutcome:
    """Store an inbound message and queue it for triage. Idempotent."""
    kind = source_kind if source_kind != "unknown" else source_kind_for(text)

    row, duplicate = await repo.create_or_get_exception(session, text=text, source_kind=kind)

    # Already triaged: hand back what is stored rather than paying to redo it.
    if duplicate and row.status not in PENDING_STATUSES:
        return IngestOutcome(exception_id=row.id, status=row.status, duplicate=True)

    job_id = await repo.enqueue(session, row.id)
    return IngestOutcome(
        exception_id=row.id, status=row.status, duplicate=duplicate, job_id=job_id
    )
