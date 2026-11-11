"""The triage pipeline: gather evidence with tools, then extract a validated record.

Deliberately imports no FastAPI and no SQLAlchemy. ``evals/run.py`` calls :func:`triage`
directly rather than over HTTP, so the eval harness measures the pipeline and not the
transport — and it stays fast enough to run on every commit.

Sequence:

1. **Tool loop** — the model checks the claim in the message against the inventory data.
   Errors come back as results, so a wrong SKU is corrected rather than fatal.
2. **Extract** — one structured-output call constrained to :class:`InventoryException`.
3. **Repair** — if validation fails, re-ask with the validator's own error text appended.
   Bounded, because an unbounded repair loop is a cost incident.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal

from pydantic import ValidationError

from app.config import Settings, get_settings
from app.domain.inventory import TOOLS, ToolSpec
from app.domain.models import InventoryException
from app.domain.prompt_loader import render
from app.llm.base import BaseClient, LlmCallRecord, ToolCallRecord
from app.pipeline.cost import cost_usd


class TerminalTriageError(RuntimeError):
    """The pipeline could not produce a usable record, and running it again will not help.

    Distinct from a provider failure on purpose. A 429 or a dropped connection is worth
    retrying; a schema the model failed to satisfy *after* being handed the validator's own
    error text is not — a second attempt costs money to reproduce the same failure. The worker
    uses this distinction to decide between backoff and giving up.
    """


@dataclass
class TriageOutcome:
    """Everything one triage produced: the verdict, the evidence, and what it cost."""

    record: InventoryException
    evidence: list[ToolCallRecord] = field(default_factory=list)
    calls: list[LlmCallRecord] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    prompt_version: str = "v1"
    cost_usd: Decimal = Decimal("0")
    latency_ms: int = 0
    repair_attempts: int = 0
    stop_reason: str = ""

    @property
    def evidence_errors(self) -> int:
        return sum(1 for c in self.evidence if c.failed)


def _evidence_block(evidence: Sequence[ToolCallRecord]) -> str:
    """Render the tool results as text for the extraction prompt.

    The model needs the numbers it gathered, not a summary of them. Passing the raw JSON
    keeps the record and the evidence in agreement.
    """
    if not evidence:
        return "(no tool results were gathered)"
    lines = []
    for call in evidence:
        payload = json.dumps(call.result)
        marker = "ERROR" if call.failed else "ok"
        lines.append(f"- {call.name}({json.dumps(call.arguments)}) -> [{marker}] {payload}")
    return "\n".join(lines)


async def triage(
    text: str,
    *,
    client: BaseClient,
    settings: Settings | None = None,
    tools: Sequence[ToolSpec] | None = None,
) -> TriageOutcome:
    """Triage one inbound message.

    Async because both calls in it are network I/O — the textbook case. It also matters
    practically: the worker runs several jobs concurrently, and a synchronous pipeline would
    serialise them no matter how many coroutines it was wrapped in.
    """
    settings = settings or get_settings()
    version = settings.prompt_version
    started = time.perf_counter()

    system = render("triage_system", version)
    calls: list[LlmCallRecord] = []

    # ---- 1. gather evidence -----------------------------------------------------------
    loop = await client.atool_loop(
        text,
        tools=tools or TOOLS,
        system=system,
        max_rounds=settings.max_tool_rounds,
        max_tokens=settings.max_tokens_per_record,
        verbose=False,
    )
    calls.append(
        LlmCallRecord(
            provider=client.provider,
            model=client.model,
            prompt_version=version,
            input_tokens=loop.usage.input_tokens,
            output_tokens=loop.usage.output_tokens,
            cost_usd=cost_usd(
                client.provider, client.model, loop.usage.input_tokens, loop.usage.output_tokens
            ),
            latency_ms=int(loop.usage.latency_s * 1000),
            outcome="ok",
        )
    )

    # ---- 2. extract -------------------------------------------------------------------
    prompt = render(
        "triage_extract",
        version,
        message=text,
        evidence=_evidence_block(loop.tool_calls),
    )

    record: InventoryException | None = None
    repairs = 0
    for attempt in range(settings.repair_attempts + 1):
        try:
            result = await client.astructured(
                prompt,
                InventoryException,
                system=system,
                max_tokens=settings.max_tokens_per_record,
            )
        except Exception as exc:  # provider failure — recorded, then surfaced
            calls.append(
                LlmCallRecord(
                    provider=client.provider,
                    model=client.model,
                    prompt_version=version,
                    input_tokens=0,
                    output_tokens=0,
                    cost_usd=Decimal("0"),
                    latency_ms=0,
                    outcome="error",
                    error_class=type(exc).__name__,
                )
            )
            raise

        calls.append(
            LlmCallRecord(
                provider=client.provider,
                model=client.model,
                prompt_version=version,
                input_tokens=result.usage.input_tokens,
                output_tokens=result.usage.output_tokens,
                cost_usd=cost_usd(
                    client.provider,
                    client.model,
                    result.usage.input_tokens,
                    result.usage.output_tokens,
                ),
                latency_ms=int(result.usage.latency_s * 1000),
                retries=result.retries,
                outcome="ok",
            )
        )

        try:
            record = InventoryException.model_validate(result.parsed)
            break
        except ValidationError as exc:
            repairs += 1
            if attempt >= settings.repair_attempts:
                raise TerminalTriageError(
                    f"the model could not satisfy the schema after {repairs} repair attempt(s); "
                    f"last error: {exc.errors()[0]['msg']}"
                ) from exc
            # Feed the validator's own message back: it names the field and the allowed
            # values, which is far more useful to the model than a restated instruction.
            prompt = render("repair", version, validation_error=str(exc), message=text)

    if record is None:  # pragma: no cover - the loop either breaks or raises
        raise RuntimeError("triage produced no record")

    total_cost = sum((c.cost_usd for c in calls), Decimal("0"))
    return TriageOutcome(
        record=record,
        evidence=list(loop.tool_calls),
        calls=calls,
        provider=client.provider,
        model=client.model,
        prompt_version=version,
        cost_usd=total_cost,
        latency_ms=int((time.perf_counter() - started) * 1000),
        repair_attempts=repairs,
        stop_reason=loop.stop_reason,
    )


def triage_sync(
    text: str,
    *,
    client: BaseClient,
    settings: Settings | None = None,
    tools: Sequence[ToolSpec] | None = None,
) -> TriageOutcome:
    """Blocking wrapper for scripts, evals and one-off checks.

    Not usable from inside a running event loop — the API and the worker call ``triage``
    directly, which is the whole point of it being async.
    """
    return asyncio.run(triage(text, client=client, settings=settings, tools=tools))
