"""decision execution: what approving actually did

The ``decisions`` table recorded *that* a human decided and *what* they decided. It did not
record what followed. For an audit trail whose whole premise is "the model recommends, a human
commits", that is the important half missing.

Two columns:

* ``executed_tool`` — the domain tool the approval invoked, e.g. ``flag_exception``. Null when
  the human rejected, because a rejection executes nothing.
* ``executed_result`` — the tool's return value, **including its error envelope**. The tool
  layer returns errors as data rather than raising, so a refused execution is stored as
  ``{"error": ...}`` rather than being lost or crashing the request. A decision whose
  consequence failed is still a decision, and both halves belong in the record.

Revision ID: 0003_decision_execution
Revises: 0002_job_recovery
Create Date: 2026-10-21
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_decision_execution"
down_revision: str | None = "0002_job_recovery"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("decisions", sa.Column("executed_tool", sa.Text(), nullable=True))
    op.add_column(
        "decisions", sa.Column("executed_result", postgresql.JSONB(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("decisions", "executed_result")
    op.drop_column("decisions", "executed_tool")
