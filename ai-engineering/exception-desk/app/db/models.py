"""SQLAlchemy tables.

Five tables. ``exception_evidence`` is the one that makes a record auditable rather than
merely plausible: every extracted field should be traceable to a tool result, and without
storing them you cannot tell a grounded extraction from a confident invention.

``llm_calls`` is deliberately decoupled from ``exceptions`` — a triage attempt can fail
entirely and still cost money, and that has to be visible.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ExceptionRow(Base):
    """One inbound message and the triage verdict on it."""

    __tablename__ = "exceptions"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    # Idempotency key: sha256 of the *normalised* text. Hashing before normalising would
    # make the same supplier email with a trailing newline a second exception.
    source_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    status: Mapped[str] = mapped_column(
        Text, nullable=False, default="pending", server_default="pending"
    )

    # -- extraction result -------------------------------------------------------------
    sku: Mapped[str | None] = mapped_column(Text)
    severity: Mapped[str | None] = mapped_column(Text)
    root_cause: Mapped[str | None] = mapped_column(Text)
    weeks_of_cover: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    lead_time_impact_days: Mapped[int | None] = mapped_column(Integer)
    recommended_action: Mapped[str | None] = mapped_column(Text)
    requires_escalation: Mapped[bool | None] = mapped_column(Boolean)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rationale: Mapped[str | None] = mapped_column(Text)

    # -- provenance --------------------------------------------------------------------
    prompt_version: Mapped[str | None] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(Text)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    triaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)

    evidence: Mapped[list[EvidenceRow]] = relationship(
        back_populates="exception", cascade="all, delete-orphan", order_by="EvidenceRow.id"
    )
    decisions: Mapped[list[DecisionRow]] = relationship(
        back_populates="exception", cascade="all, delete-orphan", order_by="DecisionRow.id"
    )
    llm_calls: Mapped[list[LlmCallRow]] = relationship(back_populates="exception")


class EvidenceRow(Base):
    """One tool call the model made while triaging, and what it got back."""

    __tablename__ = "exception_evidence"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exception_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("exceptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    tool: Mapped[str] = mapped_column(Text, nullable=False)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_error: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    exception: Mapped[ExceptionRow] = relationship(back_populates="evidence")


class DecisionRow(Base):
    """A human's verdict on the recommendation. Only this commits anything."""

    __tablename__ = "decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exception_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("exceptions.id"), nullable=False, index=True
    )
    decided_by: Mapped[str] = mapped_column(Text, nullable=False)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)  # approved | edited | rejected
    final_action: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[str | None] = mapped_column(Text)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    exception: Mapped[ExceptionRow] = relationship(back_populates="decisions")


class LlmCallRow(Base):
    """Every model call, for cost accounting and for explaining a record's provenance."""

    __tablename__ = "llm_calls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exception_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("exceptions.id"), index=True
    )
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_version: Mapped[str] = mapped_column(Text, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(10, 6), nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    outcome: Mapped[str] = mapped_column(Text, nullable=False, default="ok")  # ok|error|refused
    error_class: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    exception: Mapped[ExceptionRow | None] = relationship(back_populates="llm_calls")


class IngestJobRow(Base):
    """The queue. ``available_at`` is what makes backoff possible."""

    __tablename__ = "ingest_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    exception_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("exceptions.id"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, default="queued", server_default="queued"
    )
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    locked_by: Mapped[str | None] = mapped_column(Text)
    last_error: Mapped[str | None] = mapped_column(Text)
