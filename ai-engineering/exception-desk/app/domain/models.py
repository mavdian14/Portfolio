"""Pydantic schemas.

Two families live here:

* **Extraction targets** — the schemas the model is constrained to via structured
  outputs. Promoted from ``practice/ai-foundations/inventory.py``, with one addition:
  the triage extraction carries a ``rationale``, because a record that cannot explain
  itself is not auditable.
* **Transport shapes** — what the HTTP layer accepts and returns.

Keeping both in one module is deliberate: the record the model produces and the record
the API returns should be recognisably the same thing.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------------------
# Enumerations. These become JSON Schema enums, which is the difference between asking
# the model politely and constraining it structurally.
# --------------------------------------------------------------------------------------

Severity = Literal["critical", "high", "medium", "low"]
RootCause = Literal[
    "supplier_delay",
    "demand_spike",
    "data_quality",
    "allocation_error",
    "quality_hold",
    "forecast_error",
    "none",
]
Direction = Literal["up", "down", "flat"]
MessageCategory = Literal[
    "lead_time_change",
    "price_dispute",
    "logistics_update",
    "forecast_request",
    "general",
]
SourceKind = Literal["supplier_email", "planner_note", "po_ack", "unknown"]

# --------------------------------------------------------------------------------------
# Extraction targets
# --------------------------------------------------------------------------------------


class InventoryException(BaseModel):
    """One inbound message, triaged into typed fields. The primary extraction target."""

    sku: str = Field(description="The SKU code the note is about, e.g. CHR-M4K25-RGB")
    severity: Severity = Field(description="Business severity of the exception")
    root_cause: RootCause = Field(description="Primary driver behind the exception")
    weeks_of_cover: float = Field(
        description="Weeks of cover implied by the tool results; 0.0 if unknown"
    )
    lead_time_impact_days: int = Field(
        description="Days of lead-time slippage versus quoted; 0 if none"
    )
    recommended_action: str = Field(description="One concrete next action, imperative voice")
    requires_escalation: bool = Field(
        description="True if the message implies escalation beyond the planner"
    )
    confidence: float = Field(description="Model confidence in this extraction, 0.0-1.0")
    rationale: str = Field(
        description="Two sentences citing the specific tool results this decision rests on"
    )


class ExceptionTriage(BaseModel):
    """Classification target: one decision per inbound message."""

    sku: str = Field(description="SKU code, or 'UNKNOWN' if the message names none")
    category: MessageCategory = Field(description="What kind of message this is")
    priority: Severity = Field(description="How urgently a human should look at it")
    requires_human: bool = Field(description="True if the message needs a human decision")
    one_line_summary: str = Field(description="Summary in under 15 words")


class ExceptionTriageBatch(BaseModel):
    """Batch target: one decision per input, order preserved."""

    items: list[ExceptionTriage] = Field(
        description="One triage decision per input message, in the same order"
    )


class DemandSignal(BaseModel):
    """Extraction target for a demand-signal note."""

    sku: str = Field(description="SKU code")
    direction: Direction = Field(description="Direction of the demand change")
    pct_change: float = Field(description="Estimated percentage change versus prior period")
    driver: str = Field(description="What is driving the change, in a few words")
    confidence: float = Field(description="Confidence, 0.0-1.0")


class ReorderDecision(BaseModel):
    """The final structured answer when a caller asks for a reorder call."""

    sku: str = Field(description="SKU the decision is about")
    decision: Literal["reorder_now", "reorder_soon", "hold", "expedite_existing_po"] = Field(
        description="The recommended action"
    )
    order_quantity: int = Field(description="Units to order; 0 if the decision is hold")
    weeks_of_cover: float = Field(description="Weeks of cover at current demand")
    rationale: str = Field(description="Two sentences of justification citing the tool results")


# --------------------------------------------------------------------------------------
# Transport shapes
# --------------------------------------------------------------------------------------


class TriageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    source_kind: SourceKind = Field(
        default="unknown",
        description="Leave as 'unknown' to let the service infer it from the text.",
    )


class IngestResponse(BaseModel):
    exception_id: UUID
    status: str
    duplicate: bool


class EvidenceOut(BaseModel):
    round: int
    tool: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    is_error: bool


class ProvenanceOut(BaseModel):
    """Where a record came from. First-class, not debug output."""

    prompt_version: str
    provider: str
    model: str
    llm_calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    latency_ms: int
    retries: int


class TriageRecordOut(BaseModel):
    id: UUID
    status: str
    source_kind: str
    raw_text: str
    received_at: datetime
    triaged_at: datetime | None = None

    sku: str | None = None
    severity: str | None = None
    root_cause: str | None = None
    weeks_of_cover: float | None = None
    lead_time_impact_days: int | None = None
    recommended_action: str | None = None
    requires_escalation: bool | None = None
    confidence: float | None = None
    rationale: str | None = None

    evidence: list[EvidenceOut] = Field(default_factory=list)
    provenance: ProvenanceOut | None = None

    duplicate: bool = False
    error: str | None = None


class QueueItem(BaseModel):
    id: UUID
    status: str
    source_kind: str
    sku: str | None
    severity: str | None
    root_cause: str | None
    confidence: float | None
    received_at: datetime
    cost_usd: Decimal | None


class QueuePage(BaseModel):
    items: list[QueueItem]
    count: int


class CostRow(BaseModel):
    provider: str
    model: str
    calls: int
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal


class CostSummary(BaseModel):
    window_days: int
    total_calls: int
    total_cost_usd: Decimal
    rows: list[CostRow]
