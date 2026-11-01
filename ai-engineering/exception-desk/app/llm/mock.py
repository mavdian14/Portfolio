"""Deterministic offline provider.

This is not a stub that returns canned text. It runs the same control flow as the real
clients — real tool handlers against the real domain data, the same retry branches, the
same error classes — and swaps only the network call. That is what lets the test suite and
CI exercise the whole pipeline with no keys and no spend.

The mock's extraction is derived from the inventory records, so the record it produces
agrees with the evidence it gathered. A mock that contradicts itself teaches you nothing.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator, Sequence
from typing import Any

from app.domain.inventory import (
    INVENTORY,
    TOOLS,
    ToolSpec,
    cover_weeks,
    first_sku,
    run_tool,
    skus_in_text,
)
from app.domain.models import (
    DemandSignal,
    ExceptionTriage,
    ExceptionTriageBatch,
    InventoryException,
    ReorderDecision,
    RootCause,
    Severity,
)
from app.llm.base import (
    BaseClient,
    ModelT,
    StructuredResult,
    ToolCallRecord,
    ToolLoopResult,
    Usage,
)

_MOCK_ERROR_TYPES: dict[str, type[Exception]] = {}


def mock_error(
    name: str,
    message: str,
    status_code: int | None = 500,
    retry_after: float | None = None,
) -> Exception:
    """Build an exception whose *class name* matches a real SDK error.

    ``type(name, (Exception,), {})`` creates a class at runtime, so ``__name__`` is
    literally ``"RateLimitError"`` and the same ``is_retryable`` / ``describe_error``
    branches run offline and live. Assigning ``self.__class__.__name__`` instead would
    mutate the class for every instance ever created — a real bug, fixed by doing this.
    """
    cls: Any = _MOCK_ERROR_TYPES.get(name)
    if cls is None:
        cls = type(name, (Exception,), {})
        _MOCK_ERROR_TYPES[name] = cls
    exc: Any = cls(message)
    exc.status_code = status_code
    if retry_after is not None:
        exc.response = type(
            "MockResponse",
            (),
            {"status_code": status_code, "headers": {"retry-after": str(retry_after)}},
        )()
    return exc


class MockClient(BaseClient):
    """Deterministic stand-in for a provider. Runs the real tool handlers."""

    provider = "mock"

    def __init__(
        self,
        model: str | None = None,
        *,
        real_provider: str = "anthropic",
        interrupt_after: int | None = None,
        fail_first_n_calls: int = 0,
    ) -> None:
        self.model = model or "mock"
        self.real_provider = real_provider
        self.interrupt_after = interrupt_after
        self.fail_first_n_calls = fail_first_n_calls
        self._call_count = 0

    # -- helpers -----------------------------------------------------------------------
    def _maybe_fail(self) -> None:
        """Raise a synthetic 429 while the failure budget lasts. Used to demo retries."""
        self._call_count += 1
        if self.fail_first_n_calls and self._call_count <= self.fail_first_n_calls:
            raise mock_error(
                "RateLimitError",
                "simulated 429 from mock provider",
                status_code=429,
                retry_after=0.2,
            )

    def _mock_usage(self, text: str, calls: int = 1) -> Usage:
        """Estimate tokens at the standard ~4 characters per token ratio."""
        return Usage(
            self.provider,
            self.model,
            input_tokens=len(text) // 4,
            output_tokens=len(text) // 4,
            calls=calls,
            latency_s=0.0,
        )

    # -- structured --------------------------------------------------------------------
    def structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        self._maybe_fail()
        parsed = mock_parse(schema, prompt)
        return StructuredResult(
            parsed=parsed,
            raw_text=parsed.model_dump_json(),
            usage=self._mock_usage(prompt),
            payload={"model": self.model, "schema": schema.__name__},
        )

    def structured_raw(
        self,
        prompt: str,
        json_schema: dict[str, Any],
        *,
        name: str = "payload",
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        self._maybe_fail()
        sku = first_sku(prompt) or "CHR-M4K25-RGB"
        payload = {"sku": sku, "severity": "high", "weeks_of_cover": 0.7}
        return StructuredResult(
            parsed=payload,
            raw_text=json.dumps(payload),
            usage=self._mock_usage(prompt),
            payload={"json_schema": json_schema, "name": name},
        )

    # -- tools -------------------------------------------------------------------------
    def tool_loop(
        self,
        prompt: str,
        *,
        tools: Sequence[ToolSpec] | None = None,
        system: str | None = None,
        max_rounds: int = 6,
        max_tokens: int = 1024,
        parallel: bool = True,
        verbose: bool = True,
    ) -> ToolLoopResult:
        self._maybe_fail()
        result = self._tool_loop_impl(
            prompt,
            tools=tools,
            system=system,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
            parallel=parallel,
            verbose=verbose,
        )
        # Token counts estimated from the prompt plus every tool payload the loop carried,
        # so the usage table is not a fiction.
        payload = prompt + "".join(json.dumps(c.result) for c in result.tool_calls)
        result.usage = self._mock_usage(payload, calls=max(result.rounds, 1))
        return result

    def _tool_loop_impl(
        self,
        prompt: str,
        *,
        tools: Sequence[ToolSpec] | None = None,
        system: str | None = None,
        max_rounds: int = 6,
        max_tokens: int = 1024,
        parallel: bool = True,
        verbose: bool = True,
    ) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        skus = skus_in_text(prompt)
        result.rounds = 1

        if not skus:
            # The message names no SKU. A real model would try something plausible, get an
            # error, and fall back — so the mock does exactly that, and the error lands in
            # the evidence table as it should.
            bad_args = {"sku": "UNKNOWN"}
            out = run_tool("get_sku_status", bad_args)
            result.tool_calls.append(
                ToolCallRecord("get_sku_status", bad_args, out, 1, "call_no_sku")
            )
            if verbose:
                result.transcript.append(
                    f"round 1: get_sku_status({json.dumps(bad_args)}) -> ERROR "
                    f"{json.dumps(out)[:180]}"
                )
            result.final_text = "No SKU identifiable in the message; nothing to look up."
            result.stop_reason = "end_turn" if self.real_provider == "anthropic" else "completed"
            result.usage = self._mock_usage(prompt, calls=2)
            return result

        for sku in skus[:2]:
            for name, args in (
                ("get_sku_status", {"sku": sku}),
                ("get_lead_time", {"sku": sku}),
                ("compute_reorder_point", {"sku": sku, "service_level": 0.95}),
                ("query_open_positions", {"sku": sku}),
            ):
                out = run_tool(name, args)
                result.tool_calls.append(
                    ToolCallRecord(name, args, out, 1, f"call_{name}_{sku}")
                )
                if verbose:
                    result.transcript.append(
                        f"round 1: {name}({json.dumps(args)}) -> "
                        f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:200]}"
                    )

        result.final_text = _mock_summary(skus)
        result.stop_reason = "end_turn" if self.real_provider == "anthropic" else "completed"
        return result

    def tool_loop_chat_completions(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        return self.tool_loop(prompt, **kwargs)

    # -- streaming ---------------------------------------------------------------------
    def stream_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 512,
        on_delta: Callable[[str], None] | None = None,
    ) -> str:
        text = _mock_summary(skus_in_text(prompt) or ["CHR-M4K25-RGB"])
        for i, chunk in enumerate(_chunks(text, 12)):
            if self.interrupt_after is not None and i == self.interrupt_after:
                raise mock_error("APIConnectionError", "simulated mid-stream disconnect", None)
            if on_delta:
                on_delta(chunk)
        return text

    def stream_events(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 256,
        limit: int = 60,
        mode: str = "text",
    ) -> list[str]:
        if self.real_provider == "anthropic":
            base = [
                "event=message_start",
                "event=content_block_start index=0 block=text",
                "event=ping",
                "event=content_block_delta index=0 delta=text_delta text='Cover '",
                "event=content_block_delta index=0 delta=text_delta text='is 0.7 weeks.'",
                "event=content_block_stop index=0",
                "event=message_delta stop_reason=end_turn",
                "event=message_stop",
            ]
        else:
            base = [
                "event=response.created",
                "event=response.in_progress",
                "event=response.output_item.added",
                "event=response.output_text.delta delta='Cover '",
                "event=response.output_text.delta delta='is 0.7 weeks.'",
                "event=response.output_item.done",
                "event=response.completed",
            ]
        return base[:limit]

    def stream_structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        parsed = mock_parse(schema, prompt)
        return StructuredResult(
            parsed=parsed,
            raw_text=parsed.model_dump_json(),
            usage=self._mock_usage(prompt),
        )

    def stream_chat_tool_arguments(
        self, prompt: str, **kwargs: Any
    ) -> dict[int, dict[str, str]]:
        sku = first_sku(prompt) or "CHR-M4K25-RGB"
        return {0: {"name": "get_sku_status", "arguments": json.dumps({"sku": sku})}}

    # -- async -------------------------------------------------------------------------
    async def astructured(self, prompt: str, schema: type[ModelT], **kw: Any) -> StructuredResult:
        return self.structured(prompt, schema, **kw)

    async def atool_loop(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        return self.tool_loop(prompt, **kwargs)

    async def astream_text(self, prompt: str, **kw: Any) -> str:
        return self.stream_text(prompt, **kw)

    def list_models(self, limit: int = 40) -> list[str]:
        return ["mock"]


# --------------------------------------------------------------------------------------
# Deterministic generation
# --------------------------------------------------------------------------------------


def _chunks(text: str, size: int) -> Iterator[str]:
    for i in range(0, len(text), size):
        yield text[i : i + size]


def _mock_summary(skus: Sequence[str]) -> str:
    lines = []
    for sku in skus[:3]:
        rec = INVENTORY.get(sku)
        if not rec:
            continue
        slip = rec["actual_lt_p90_days"] - rec["quoted_lt_days"]
        lines.append(
            f"{sku}: {rec['on_hand']} on hand, {rec['allocated']} allocated, "
            f"{rec['in_transit']} in transit -> {cover_weeks(rec):.1f} weeks of cover; "
            f"lead time {rec['quoted_lt_days']}d quoted vs {rec['actual_lt_p90_days']}d observed "
            f"({slip:+d}d slippage)."
        )
    return "Position review:\n" + "\n".join(lines) if lines else "No SKU identified."


#: The extract template ends with the inbound message under this marker.
_MESSAGE_MARKER = "Message:"


def message_from_prompt(prompt: str) -> str:
    """The inbound message alone, without the instruction scaffolding around it.

    Necessary because the template itself contains phrases like "low when no action is
    needed". Matching intent against the whole prompt lets the *instructions* masquerade as
    the message, and the mock then classifies every record as "no action" — which is exactly
    the class of quiet disagreement with reality that makes a mock worse than useless.
    """
    idx = prompt.rfind(_MESSAGE_MARKER)
    return prompt[idx + len(_MESSAGE_MARKER) :] if idx != -1 else prompt


def _says_no_action(text: str) -> bool:
    """True when the message itself asserts that nothing needs doing."""
    low = text.lower()
    return "no action" in low or "no concerns" in low or "look fine" in low


def _severity_for(sku: str, text: str) -> Severity:
    """Business impact, derived from the inventory record rather than the wording."""
    rec = INVENTORY.get(sku)
    if not rec:
        # Nothing to read impact from. Use the one signal the message does carry.
        return "low" if _says_no_action(text) else "medium"
    cover = cover_weeks(rec)
    slip = rec["actual_lt_p90_days"] - rec["quoted_lt_days"]
    low = text.lower()
    if cover <= 0.5 or "break the install" in low or "zero on hand" in low:
        return "critical"
    if cover < 2.0 or slip >= 20:
        return "high"
    if "no action" in low or "no concerns" in low:
        return "low"
    return "medium"


def _root_cause_for(sku: str, text: str) -> RootCause:
    rec = INVENTORY.get(sku)
    slip = (rec["actual_lt_p90_days"] - rec["quoted_lt_days"]) if rec else 0
    low = text.lower()
    if "forecast" in low and "wrong" in low:
        return "forecast_error"
    if "double forecast" in low or "spiking" in low or "spike" in low or "demand came in" in low:
        return "demand_spike"
    if "no action" in low:
        return "none"
    return "supplier_delay" if slip > 0 else "none"


def mock_parse(schema: type[ModelT], prompt: str) -> Any:
    """Deterministic, schema-valid answers so offline runs exercise real validation.

    Values are read from the domain records, so the extraction agrees with the tool
    results gathered in the same run.
    """
    sku = first_sku(prompt)
    known = sku is not None
    sku = sku or "UNKNOWN"
    # Classify on the message, never on the prompt that carries it.
    message = message_from_prompt(prompt)

    if schema is InventoryException:
        rec = INVENTORY.get(sku, {})
        slip = (rec.get("actual_lt_p90_days", 0) - rec.get("quoted_lt_days", 0)) if rec else 0
        cover = cover_weeks(rec) if rec else 0.0
        severity = _severity_for(sku, message)
        if known:
            root = _root_cause_for(sku, message)
        else:
            # No SKU resolved. That the message cannot be acted on as-is is itself the
            # finding — unless it explicitly needs nothing, in which case say so rather
            # than reporting a data problem that is not one.
            root = "none" if _says_no_action(message) else "data_quality"
        return InventoryException(
            sku=sku,
            severity=severity,
            root_cause=root,
            weeks_of_cover=cover,
            lead_time_impact_days=max(slip, 0),
            recommended_action=(
                f"Expedite the at-risk open PO for {sku} and review cover against the "
                f"{rec.get('actual_lt_p90_days', 0)}-day observed lead time"
                if known
                else "Ask the sender which SKU the message concerns before acting"
            ),
            requires_escalation=severity in ("critical", "high") and known,
            confidence=0.86 if known else (0.5 if _says_no_action(message) else 0.35),
            rationale=(
                f"Observed lead time is {rec.get('actual_lt_p90_days', 0)} days against "
                f"{rec.get('quoted_lt_days', 0)} quoted ({slip:+d} days slippage) and cover is "
                f"{cover:.2f} weeks at current demand."
                if known
                else "The message names no SKU that exists in the inventory master, so no "
                "position could be checked."
            ),
        )

    if schema is ExceptionTriageBatch:
        notes = [n.strip() for n in prompt.split("\n\n") if n.strip()]
        notes = [n for n in notes if not n.lower().startswith(("triage the", "message:"))]
        items = [_mock_triage(n) for n in notes[:10]] or [_mock_triage(prompt)]
        return ExceptionTriageBatch(items=items)

    if schema is ExceptionTriage:
        return _mock_triage(prompt)

    if schema is DemandSignal:
        return DemandSignal(
            sku=sku,
            direction="up",
            pct_change=40.0,
            driver="education tender volume",
            confidence=0.72,
        )

    if schema is ReorderDecision:
        rec = INVENTORY.get(sku, {})
        cover = cover_weeks(rec) if rec else 0.0
        return ReorderDecision(
            sku=sku,
            decision="expedite_existing_po" if rec else "hold",
            order_quantity=0,
            weeks_of_cover=cover,
            rationale="Cover is below the reorder point after lead-time slippage and an open "
            "PO is already flagged at risk.",
        )

    # Generic fallback: fill every field with a type-appropriate placeholder.
    values: dict[str, Any] = {}
    for name, field_info in schema.model_fields.items():
        ann = str(field_info.annotation)
        if "str" in ann:
            values[name] = f"<mock {name}>"
        elif "bool" in ann:
            values[name] = True
        elif "float" in ann:
            values[name] = 0.5
        elif "int" in ann:
            values[name] = 1
        else:
            values[name] = None
    return schema(**values)


def _mock_triage(note: str) -> ExceptionTriage:
    """Deterministic classification of one inbound message."""
    low = note.lower()
    if "invoice" in low or "unit price" in low:
        category = "price_dispute"
    elif "forecast" in low:
        category = "forecast_request"
    elif "customs" in low or "in transit" in low or "tracking" in low:
        category = "logistics_update"
    elif "lead time" in low or "cannot confirm" in low or "date" in low:
        category = "lead_time_change"
    else:
        category = "general"

    if "cannot confirm" in low or "shortage" in low or "zero on hand" in low:
        priority = "critical"
    elif "extend" in low or "expect" in low or "wrong" in low:
        priority = "high"
    elif "no action required" in low or "no concerns" in low:
        priority = "low"
    else:
        priority = "medium"

    words = note.split()
    summary = " ".join(words[:11]) + ("..." if len(words) > 11 else "")
    return ExceptionTriage(
        sku=first_sku(note) or "UNKNOWN",
        category=category,
        priority=priority,
        requires_human=category != "logistics_update",
        one_line_summary=summary[:80],
    )
