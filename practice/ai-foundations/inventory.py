"""
Domain layer for the AI Foundations scripts: synthetic inventory & supply-chain data,
the pydantic schemas used as structured-output targets, and the tool registry.

ALL DATA IS SYNTHETIC. SKU codes, suppliers and figures are invented for study purposes.

Framing: inventory control for a projector/display manufacturer — SKUs with on-hand,
allocated and in-transit quantities, supplier lead times that slip, safety stock, and
an exception queue that arrives as free text from planners and buyers.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------------------
# Synthetic master data
# --------------------------------------------------------------------------------------

# sku -> record. `demand_sigma` is the weekly demand standard deviation.
INVENTORY: dict[str, dict[str, Any]] = {
    "CHR-M4K25-RGB": {
        "description": "4K25 RGB pure-laser projector, 25,000 lumens",
        "on_hand": 3, "allocated": 12, "in_transit": 0, "safety_stock": 6,
        "avg_weekly_demand": 4.2, "demand_sigma": 2.1, "unit_cost": 41000.0,
        "supplier": "Nordlicht Optik GmbH", "quoted_lt_days": 45, "actual_lt_p90_days": 68,
        "region": "EMEA",
    },
    "CHR-CRWU31": {
        "description": "Crimson WU31 3-chip DLP projector",
        "on_hand": 14, "allocated": 9, "in_transit": 6, "safety_stock": 8,
        "avg_weekly_demand": 3.1, "demand_sigma": 1.4, "unit_cost": 28500.0,
        "supplier": "Nordlicht Optik GmbH", "quoted_lt_days": 60, "actual_lt_p90_days": 61,
        "region": "NA",
    },
    "CHR-GS25-HS": {
        "description": "GS Series 1DLP laser projector, high-security variant",
        "on_hand": 41, "allocated": 18, "in_transit": 20, "safety_stock": 12,
        "avg_weekly_demand": 9.5, "demand_sigma": 4.8, "unit_cost": 7400.0,
        "supplier": "Shenzhen Lumina Ltd", "quoted_lt_days": 30, "actual_lt_p90_days": 34,
        "region": "APAC",
    },
    "CHR-DHD1075": {
        "description": "DHD1075 1DLP projector, legacy",
        "on_hand": 2, "allocated": 1, "in_transit": 0, "safety_stock": 4,
        "avg_weekly_demand": 1.8, "demand_sigma": 0.9, "unit_cost": 12900.0,
        "supplier": "Shenzhen Lumina Ltd", "quoted_lt_days": 75, "actual_lt_p90_days": 118,
        "region": "NA",
    },
    "LNS-142-330": {
        "description": "1.42-2.03:1 zoom lens, 0.95\" DMD",
        "on_hand": 27, "allocated": 22, "in_transit": 15, "safety_stock": 10,
        "avg_weekly_demand": 6.4, "demand_sigma": 3.2, "unit_cost": 2150.0,
        "supplier": "Optikwerke Jena AG", "quoted_lt_days": 42, "actual_lt_p90_days": 44,
        "region": "EMEA",
    },
    "LNS-200-355": {
        "description": "2.00-3.55:1 long-throw zoom lens",
        "on_hand": 5, "allocated": 11, "in_transit": 0, "safety_stock": 8,
        "avg_weekly_demand": 5.9, "demand_sigma": 3.6, "unit_cost": 2680.0,
        "supplier": "Optikwerke Jena AG", "quoted_lt_days": 42, "actual_lt_p90_days": 79,
        "region": "EMEA",
    },
    "SPR-LAMP-CRW": {
        "description": "Crimson lamp module, spare",
        "on_hand": 63, "allocated": 12, "in_transit": 0, "safety_stock": 20,
        "avg_weekly_demand": 7.2, "demand_sigma": 5.1, "unit_cost": 980.0,
        "supplier": "Nordlicht Optik GmbH", "quoted_lt_days": 21, "actual_lt_p90_days": 23,
        "region": "NA",
    },
    "SPR-FILT-GS": {
        "description": "GS Series air filter kit",
        "on_hand": 118, "allocated": 30, "in_transit": 50, "safety_stock": 40,
        "avg_weekly_demand": 22.0, "demand_sigma": 9.4, "unit_cost": 145.0,
        "supplier": "Shenzhen Lumina Ltd", "quoted_lt_days": 18, "actual_lt_p90_days": 19,
        "region": "APAC",
    },
    "PRT-MOUNT-RIG": {
        "description": "Rigging frame mount, large format",
        "on_hand": 9, "allocated": 9, "in_transit": 4, "safety_stock": 5,
        "avg_weekly_demand": 2.4, "demand_sigma": 1.7, "unit_cost": 3300.0,
        "supplier": "Ferro Fabrication Inc", "quoted_lt_days": 28, "actual_lt_p90_days": 31,
        "region": "NA",
    },
    "PCB-CTRL-M4K": {
        "description": "M 4K25 control board, service part",
        "on_hand": 0, "allocated": 4, "in_transit": 12, "safety_stock": 5,
        "avg_weekly_demand": 1.6, "demand_sigma": 1.2, "unit_cost": 5600.0,
        "supplier": "Vektor Circuits Pte Ltd", "quoted_lt_days": 90, "actual_lt_p90_days": 152,
        "region": "APAC",
    },
    "CHR-CP4415": {
        "description": "CP4415-RGB 4K projector",
        "on_hand": 7, "allocated": 7, "in_transit": 3, "safety_stock": 4,
        "avg_weekly_demand": 1.9, "demand_sigma": 1.1, "unit_cost": 63000.0,
        "supplier": "Nordlicht Optik GmbH", "quoted_lt_days": 70, "actual_lt_p90_days": 96,
        "region": "EMEA",
    },
    "SPR-PSU-1KW": {
        "description": "1kW power supply unit, spare",
        "on_hand": 22, "allocated": 5, "in_transit": 0, "safety_stock": 15,
        "avg_weekly_demand": 4.4, "demand_sigma": 2.6, "unit_cost": 1240.0,
        "supplier": "Vektor Circuits Pte Ltd", "quoted_lt_days": 35, "actual_lt_p90_days": 37,
        "region": "APAC",
    },
}

OPEN_POS: list[dict[str, Any]] = [
    {"po": "PO-88410", "sku": "CHR-M4K25-RGB", "qty": 6, "unit_cost": 41000.0,
     "promised_date": "2026-11-14", "supplier": "Nordlicht Optik GmbH", "status": "confirmed"},
    {"po": "PO-88411", "sku": "CHR-M4K25-RGB", "qty": 4, "unit_cost": 41000.0,
     "promised_date": "2026-12-02", "supplier": "Nordlicht Optik GmbH", "status": "at_risk"},
    {"po": "PO-88455", "sku": "LNS-200-355", "qty": 8, "unit_cost": 2680.0,
     "promised_date": "2026-11-28", "supplier": "Optikwerke Jena AG", "status": "at_risk"},
    {"po": "PO-88460", "sku": "PCB-CTRL-M4K", "qty": 12, "unit_cost": 5600.0,
     "promised_date": "2026-12-19", "supplier": "Vektor Circuits Pte Ltd", "status": "confirmed"},
    {"po": "PO-88471", "sku": "CHR-GS25-HS", "qty": 20, "unit_cost": 7400.0,
     "promised_date": "2026-11-09", "supplier": "Shenzhen Lumina Ltd", "status": "in_transit"},
    {"po": "PO-88480", "sku": "SPR-FILT-GS", "qty": 50, "unit_cost": 145.0,
     "promised_date": "2026-11-05", "supplier": "Shenzhen Lumina Ltd", "status": "in_transit"},
]

# Free-text planner notes — the extraction demo turns these into typed records.
EXCEPTION_NOTES: list[str] = [
    "M 4K25 RGB — on hand 3, but 12 are already allocated to the Toronto showroom install "
    "landing Nov 12. Nordlicht has pushed the quoted 45-day lead time out to 68 days on the "
    "last two receipts and the PO-88411 line is flagged at risk. This is going to break the "
    "install date. I think we should escalate to the supplier and look at pulling from EMEA stock.",
    "The 2.00-3.55:1 long-throw lens is a mess this month. Demand came in nearly double forecast "
    "for the quarter and we have 5 on hand against 11 allocated. The PO that was supposed to cover "
    "it (PO-88455) is now showing at risk with a 79-day actual lead time versus 42 quoted. "
    "Medium urgency for now but it will go critical if the Q1 orders land early.",
    "Control board PCB-CTRL-M4K is at zero on hand with 4 allocated to service jobs. Vektor has "
    "quoted 90 days and we are seeing 152 days actual. Honestly the forecast for this part has been "
    "wrong for three quarters — the service demand is spiking because of the firmware recall. "
    "Needs a reorder decision and probably a second source.",
    "GS Series high-security units look fine — 41 on hand, 18 allocated, 20 in transit. Lead time "
    "is stable at 34 days against 30 quoted. No action needed, flagging only because the region "
    "planner asked for a status pass.",
]

# Longer log — used for the chaining / map-reduce prompt-engineering demo.
LONG_EXCEPTION_LOG: str = "\n".join(
    f"[2026-10-{day:02d}] {note}"
    for day, note in zip(
        [2, 5, 9, 12, 16, 19, 23],
        [
            "DHD1075 slipped again — 118 days actual against 75 quoted, now the worst lead time in the fleet.",
            "SPR-FILT-GS receipts on time, 19 vs 18 days. No concerns.",
            "LNS-142-330 demand up 40% week over week, driven by the two education tenders closing this month.",
            "CP4415-RGB promised date pushed from Nov 3 to Nov 21 by Nordlicht, no reason given.",
            "PRT-MOUNT-RIG allocated exactly to on-hand, zero cover — one cancelled order away from a shortage.",
            "SPR-PSU-1KW fine. Steady 37-day actual lead time, cover is comfortable.",
            "M 4K25 RGB escalated to category management; supplier committing to 55 days on the next PO only.",
        ],
    )
)

# Supplier messages — used for the classification demo.
SUPPLIER_MESSAGES: list[str] = [
    "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is fully "
    "committed through December, so we cannot confirm the Nov 14 date. We can offer Dec 2 at the "
    "earliest, or split the quantity.",
    "We are seeing a shortage of the 0.95\" DMD chip across the industry. Please expect lead times "
    "on the long-throw lens family (LNS-200-355) to extend by 3-4 weeks on orders placed after "
    "November.",
    "Invoice INV-20931 for the SPR-FILT-GS filter kits was issued at the wrong unit price. Please "
    "confirm the corrected amount and we will reissue before the end of the week.",
    "The PCB-CTRL-M4K control boards have cleared customs and are in transit to your DC. Tracking "
    "shows delivery on the promised date; no action required from your side.",
    "Requesting a forecast update for Q1 for the GS Series. We would like to reserve capacity now "
    "to protect the 30-day lead time you currently enjoy.",
]

# --------------------------------------------------------------------------------------
# Structured-output schemas (pydantic -> JSON schema for both providers)
# --------------------------------------------------------------------------------------

Severity = Literal["critical", "high", "medium", "low"]
RootCause = Literal[
    "supplier_delay", "demand_spike", "data_quality", "allocation_error",
    "quality_hold", "forecast_error", "none",
]
Direction = Literal["up", "down", "flat"]
MessageCategory = Literal[
    "lead_time_change", "price_dispute", "logistics_update", "forecast_request", "general",
]


class InventoryException(BaseModel):
    """One planner note, parsed into typed fields."""

    sku: str = Field(description="The SKU code the note is about, e.g. CHR-M4K25-RGB")
    severity: Severity = Field(description="Business severity of the exception")
    root_cause: RootCause = Field(description="Primary driver behind the exception")
    weeks_of_cover: float = Field(description="Approximate weeks of cover implied by the note; 0.0 if unknown")
    lead_time_impact_days: int = Field(description="Days of lead-time slippage versus quoted; 0 if none")
    recommended_action: str = Field(description="One concrete next action, imperative voice")
    requires_escalation: bool = Field(description="True if the note implies escalation beyond the planner")
    confidence: float = Field(description="Model confidence in this extraction, 0.0-1.0")


class ExceptionTriage(BaseModel):
    sku: str = Field(description="SKU code, or 'UNKNOWN' if the note names none")
    category: MessageCategory = Field(description="What kind of message this is")
    priority: Severity = Field(description="How urgently a human should look at it")
    requires_human: bool = Field(description="True if the message needs a human decision")
    one_line_summary: str = Field(description="Summary in under 15 words")


class ExceptionTriageBatch(BaseModel):
    """Classification target: one decision per note, returned as a batch."""

    items: list[ExceptionTriage] = Field(description="One triage decision per input note, in order")


class DemandSignal(BaseModel):
    """Extraction target for a demand-signal note."""

    sku: str = Field(description="SKU code")
    direction: Direction = Field(description="Direction of the demand change")
    pct_change: float = Field(description="Estimated percentage change versus prior period")
    driver: str = Field(description="What is driving the change, in a few words")
    confidence: float = Field(description="Confidence, 0.0-1.0")


class ReorderDecision(BaseModel):
    """The final structured answer for the tool-loop demo."""

    sku: str = Field(description="SKU the decision is about")
    decision: Literal["reorder_now", "reorder_soon", "hold", "expedite_existing_po"] = Field(
        description="The recommended action"
    )
    order_quantity: int = Field(description="Units to order; 0 if the decision is hold")
    weeks_of_cover: float = Field(description="Weeks of cover at current demand")
    rationale: str = Field(description="Two sentences of justification citing the tool results")


# --------------------------------------------------------------------------------------
# Tool registry (hand-rolled; no framework)
# --------------------------------------------------------------------------------------


@dataclass
class ToolSpec:
    """A tool the model may call: JSON schema for the model, python callable for us."""

    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]
    strict: bool = True

    def call(self, **kwargs: Any) -> Any:
        return self.handler(**kwargs)


def _cover_weeks(record: dict[str, Any]) -> float:
    demand = record["avg_weekly_demand"] or 1e-9
    available = record["on_hand"] - record["allocated"] + record["in_transit"]
    return round(max(available, 0) / demand, 2)


def get_sku_status(sku: str) -> dict[str, Any]:
    """Position snapshot for one SKU."""
    record = INVENTORY.get(sku)
    if record is None:
        raise ValueError(f"unknown SKU {sku!r}; known SKUs: {', '.join(sorted(INVENTORY))}")
    return {
        "sku": sku,
        "description": record["description"],
        "on_hand": record["on_hand"],
        "allocated": record["allocated"],
        "in_transit": record["in_transit"],
        "available": record["on_hand"] - record["allocated"],
        "safety_stock": record["safety_stock"],
        "weeks_of_cover": _cover_weeks(record),
        "avg_weekly_demand": record["avg_weekly_demand"],
        "region": record["region"],
    }


def get_lead_time(sku: str) -> dict[str, Any]:
    """Quoted vs observed (p90) supplier lead time, in days."""
    record = INVENTORY.get(sku)
    if record is None:
        raise ValueError(f"unknown SKU {sku!r}")
    return {
        "sku": sku,
        "supplier": record["supplier"],
        "quoted_lt_days": record["quoted_lt_days"],
        "actual_lt_p90_days": record["actual_lt_p90_days"],
        "slippage_days": record["actual_lt_p90_days"] - record["quoted_lt_days"],
    }


def compute_reorder_point(sku: str, service_level: float = 0.95) -> dict[str, Any]:
    """ROP = demand over lead time + safety factor * sigma over lead time (weekly demand model)."""
    record = INVENTORY.get(sku)
    if record is None:
        raise ValueError(f"unknown SKU {sku!r}")
    z_by_service = {0.90: 1.28, 0.95: 1.65, 0.98: 2.05, 0.99: 2.33}
    z = min(z_by_service.items(), key=lambda kv: abs(kv[0] - service_level))[1]
    lt_weeks = record["actual_lt_p90_days"] / 7.0
    demand_over_lt = record["avg_weekly_demand"] * lt_weeks
    sigma_over_lt = record["demand_sigma"] * math.sqrt(lt_weeks)
    rop = demand_over_lt + z * sigma_over_lt
    return {
        "sku": sku,
        "service_level": service_level,
        "z": z,
        "lead_time_weeks_used": round(lt_weeks, 2),
        "reorder_point_units": round(rop, 1),
        "on_hand": record["on_hand"],
        "below_reorder_point": record["on_hand"] < rop,
    }


def query_open_positions(sku: str) -> dict[str, Any]:
    """Open purchase orders for a SKU."""
    rows = [po for po in OPEN_POS if po["sku"] == sku]
    return {
        "sku": sku,
        "open_pos": rows,
        "open_qty": sum(r["qty"] for r in rows),
        "at_risk_pos": [r["po"] for r in rows if r["status"] == "at_risk"],
    }


_FLAGGED: list[dict[str, Any]] = []


VALID_SEVERITIES = ("critical", "high", "medium", "low")


def flag_exception(sku: str, reason: str, severity: str = "medium") -> dict[str, Any]:
    """Side-effecting tool: records an exception for follow-up."""
    if sku not in INVENTORY:
        raise ValueError(f"cannot flag unknown SKU {sku!r}")
    if severity not in VALID_SEVERITIES:
        raise ValueError(
            f"severity must be one of {', '.join(VALID_SEVERITIES)}; got {severity!r}"
        )
    entry = {"sku": sku, "reason": reason, "severity": severity}
    _FLAGGED.append(entry)
    return {"flagged": entry, "total_flagged_this_session": len(_FLAGGED)}


TOOLS: list[ToolSpec] = [
    ToolSpec(
        name="get_sku_status",
        description=(
            "Get the current inventory position for a SKU: on hand, allocated, in transit, "
            "available, safety stock and weeks of cover."
        ),
        input_schema={
            "type": "object",
            "properties": {"sku": {"type": "string", "description": "SKU code, e.g. CHR-M4K25-RGB"}},
            "required": ["sku"],
            "additionalProperties": False,
        },
        handler=get_sku_status,
    ),
    ToolSpec(
        name="get_lead_time",
        description=(
            "Get the supplier's quoted lead time versus the observed p90 lead time in days, "
            "and the slippage between them."
        ),
        input_schema={
            "type": "object",
            "properties": {"sku": {"type": "string", "description": "SKU code"}},
            "required": ["sku"],
            "additionalProperties": False,
        },
        handler=get_lead_time,
    ),
    ToolSpec(
        name="compute_reorder_point",
        description=(
            "Compute the statistical reorder point for a SKU at a target service level "
            "(demand over lead time plus a safety factor). Use the observed p90 lead time."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "SKU code"},
                "service_level": {
                    "type": "number",
                    "description": "Target service level, e.g. 0.95",
                    "enum": [0.9, 0.95, 0.98, 0.99],
                },
            },
            "required": ["sku", "service_level"],
            "additionalProperties": False,
        },
        handler=compute_reorder_point,
    ),
    ToolSpec(
        name="query_open_positions",
        description="List open purchase orders for a SKU, including quantity and which are at risk.",
        input_schema={
            "type": "object",
            "properties": {"sku": {"type": "string", "description": "SKU code"}},
            "required": ["sku"],
            "additionalProperties": False,
        },
        handler=query_open_positions,
    ),
    ToolSpec(
        name="flag_exception",
        description=(
            "Record an exception against a SKU for planner follow-up. Use only after you have "
            "checked the position and the lead time."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "SKU code"},
                "reason": {"type": "string", "description": "Why this needs follow-up"},
                "severity": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
            },
            "required": ["sku", "reason", "severity"],
            "additionalProperties": False,
        },
        handler=flag_exception,
    ),
]

TOOLS_BY_NAME: dict[str, ToolSpec] = {t.name: t for t in TOOLS}


def run_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool call by name, returning a result or an error envelope (never raising)."""
    spec = TOOLS_BY_NAME.get(name)
    if spec is None:
        return {"error": f"unknown tool {name!r}", "available": sorted(TOOLS_BY_NAME)}
    try:
        return {"result": spec.call(**arguments)}
    except TypeError as exc:  # wrong/missing arguments
        return {"error": f"invalid arguments for {name}: {exc}"}
    except Exception as exc:  # domain error (e.g. unknown SKU) — handed back to the model
        return {"error": str(exc)}


SYSTEM_PROMPT = (
    "You are an inventory control analyst supporting a projector and display manufacturer. "
    "You work only from the data returned by tools; never invent SKUs, quantities or lead times. "
    "When a tool returns an error, adapt: correct the argument and retry, or state plainly what "
    "you could not determine. Prefer concrete numbers over adjectives."
)
