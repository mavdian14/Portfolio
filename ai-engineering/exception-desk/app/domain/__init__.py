"""The domain layer: synthetic inventory data, the tools, the schemas, the prompts.

Imports nothing from FastAPI, SQLAlchemy, or any LLM SDK. It is importable and testable on
its own, which is what keeps the pipeline honest — ``evals/run.py`` exercises the same code
the API serves, without going through HTTP.
"""

from app.domain.inventory import (
    INVENTORY,
    OPEN_POS,
    TOOLS,
    TOOLS_BY_NAME,
    ToolSpec,
    cover_weeks,
    first_sku,
    known_skus,
    run_tool,
    skus_in_text,
)
from app.domain.models import (
    DemandSignal,
    EvidenceOut,
    ExceptionTriage,
    ExceptionTriageBatch,
    InventoryException,
    ProvenanceOut,
    ReorderDecision,
    TriageRecordOut,
    TriageRequest,
)

__all__ = [
    "INVENTORY",
    "OPEN_POS",
    "TOOLS",
    "TOOLS_BY_NAME",
    "DemandSignal",
    "EvidenceOut",
    "ExceptionTriage",
    "ExceptionTriageBatch",
    "InventoryException",
    "ProvenanceOut",
    "ReorderDecision",
    "ToolSpec",
    "TriageRecordOut",
    "TriageRequest",
    "cover_weeks",
    "first_sku",
    "known_skus",
    "run_tool",
    "skus_in_text",
]
