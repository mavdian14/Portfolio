"""Provider-agnostic client interface and the result types every client returns.

Promoted from ``practice/ai-foundations/llm_client.py``. The one structural change: the
providers are now separate modules behind this interface, so adding Ollama did not touch
Anthropic or OpenAI.

Every method returns one of the dataclasses below. That is the entire mechanism by which
the rest of the service stays provider-agnostic — no route handler or pipeline step ever
sees an SDK response object.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Literal, TypeVar

from pydantic import BaseModel

from app.domain.inventory import ToolSpec

ModelT = TypeVar("ModelT", bound=BaseModel)

# OpenAI-only surfaces are declared on the base so call sites can branch with a
# try/except NotImplementedError instead of a hasattr() probe — which would always be
# true for a declared method and therefore tell you nothing.
StreamMode = Literal["text", "tools"]


@dataclass
class Usage:
    """Token accounting for one or more calls. Accumulated across tool-loop rounds."""

    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    latency_s: float = 0.0

    def add(self, other: Usage) -> Usage:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.calls += other.calls
        self.latency_s += other.latency_s
        return self

    def __str__(self) -> str:
        return (
            f"{self.provider}/{self.model} | calls={self.calls} "
            f"in={self.input_tokens} out={self.output_tokens} latency={self.latency_s:.2f}s"
        )


@dataclass
class StructuredResult:
    parsed: Any
    raw_text: str
    usage: Usage
    payload: dict[str, Any] = field(default_factory=dict)
    retries: int = 0


@dataclass
class ToolCallRecord:
    """One tool invocation the model asked for, and what it got back."""

    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    round: int
    call_id: str = ""

    @property
    def failed(self) -> bool:
        """Relies on the domain convention that run_tool returns an ``error`` key."""
        return "error" in self.result


@dataclass
class LlmCallRecord:
    """One model call, in the shape the ``llm_calls`` table wants.

    Carries the cost rather than looking it up later: the price table can change, and a
    historical record must keep the number it was actually billed.
    """

    provider: str
    model: str
    prompt_version: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    latency_ms: int
    retries: int = 0
    outcome: str = "ok"  # ok | error | refused
    error_class: str | None = None


@dataclass
class ToolLoopResult:
    final_text: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    rounds: int = 0
    stop_reason: str = ""
    # Never None in practice: every client seeds it before the first request so the
    # loop can accumulate across rounds. A sentinel keeps the type honest.
    usage: Usage = field(default_factory=lambda: Usage("unknown", ""))
    transcript: list[str] = field(default_factory=list)


class BaseClient:
    """The surface every provider implements, including the mock."""

    provider: str = "base"
    model: str = ""

    # -- structured output -------------------------------------------------------------
    def structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        raise NotImplementedError

    def structured_raw(
        self,
        prompt: str,
        json_schema: dict[str, Any],
        *,
        name: str = "payload",
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        raise NotImplementedError

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
        raise NotImplementedError

    # -- streaming ---------------------------------------------------------------------
    def stream_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 512,
        on_delta: Callable[[str], None] | None = None,
    ) -> str:
        raise NotImplementedError

    def stream_events(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 256,
        limit: int = 60,
        mode: StreamMode = "text",
    ) -> list[str]:
        raise NotImplementedError

    def stream_structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        raise NotImplementedError

    # -- OpenAI-only surfaces ----------------------------------------------------------
    def tool_loop_chat_completions(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        raise NotImplementedError

    def stream_chat_tool_arguments(
        self, prompt: str, **kwargs: Any
    ) -> dict[int, dict[str, str]]:
        raise NotImplementedError

    # -- async twins -------------------------------------------------------------------
    async def astructured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        raise NotImplementedError

    async def atool_loop(
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
        raise NotImplementedError

    async def astream_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 512,
        on_delta: Callable[[str], None] | None = None,
    ) -> str:
        raise NotImplementedError

    # -- introspection -----------------------------------------------------------------
    def list_models(self, limit: int = 40) -> list[str]:
        raise NotImplementedError


def usage_from(resp: Any, provider: str, model: str, latency: float) -> Usage:
    """Pull token counts out of either SDK's response object.

    ``getattr(..., 0) or 0`` covers both "attribute absent" and "attribute is None".
    """
    u = getattr(resp, "usage", None)
    return Usage(
        provider=provider,
        model=model,
        input_tokens=int(getattr(u, "input_tokens", 0) or 0),
        output_tokens=int(getattr(u, "output_tokens", 0) or 0),
        calls=1,
        latency_s=latency,
    )
