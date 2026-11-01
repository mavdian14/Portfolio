"""Operational endpoints.

Deliberately unauthenticated: a health check that needs a credential is a health check that
does not run when you need it most. None of these touch the model or expose record data.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Query, Request
from sqlalchemy import text

from app.api.deps import SessionDep, SettingsDep
from app.db import repo
from app.domain.models import CostRow, CostSummary
from app.domain.prompt_loader import available_prompts

router = APIRouter(tags=["ops"])


@router.get("/healthz", summary="Liveness — is the process up")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz", summary="Readiness — can it serve traffic")
async def readyz(request: Request, session: SessionDep, settings: SettingsDep) -> dict[str, object]:
    """Reports each dependency rather than a single boolean.

    A bare 503 tells you nothing at 3am; this tells you whether it is the database, the
    prompts or the provider configuration.
    """
    checks: dict[str, object] = {}

    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # noqa: BLE001 - the failure is the payload
        checks["database"] = f"error: {type(exc).__name__}"

    prompts = available_prompts()
    expected = f"triage_system.{settings.prompt_version}"
    checks["prompts"] = "ok" if expected in prompts else f"missing {expected}"
    checks["prompt_version"] = settings.prompt_version

    client = getattr(request.app.state, "llm", None)
    checks["provider"] = getattr(client, "provider", "unset")
    checks["model"] = getattr(client, "model", "unset")

    healthy = checks["database"] == "ok" and checks["prompts"] == "ok"
    return {"ready": healthy, "checks": checks}


@router.get("/metrics/cost", response_model=CostSummary, summary="Tokens and spend")
async def cost(
    session: SessionDep,
    days: Annotated[int, Query(ge=1, le=365)] = 7,
) -> CostSummary:
    """Cost per model over a rolling window, straight from ``llm_calls``.

    Read from the recorded cost rather than recomputed from prices: a historical record must
    keep the number it was actually billed, even after a price change.
    """
    rows = await repo.cost_summary(session, days=days)
    total = Decimal("0")
    for row in rows:
        total += row["cost_usd"]
    return CostSummary(
        window_days=days,
        total_calls=sum(row["calls"] for row in rows),
        total_cost_usd=total,
        rows=[CostRow(**row) for row in rows],
    )
