"""
Provider-agnostic LLM client layer used by the three study scripts.

Design notes
------------
* Request payloads are built by **pure functions** (`anthropic_parse_kwargs`, `openai_tool_kwargs`,
  ...) so the exact shape sent to each API is inspectable — and printable in `--dry-run` mode.
* `MockClient` implements the same surface with deterministic canned answers and no network calls,
  so the full control flow (tool loops, retries, stream resume, schema validation) is exercisable
  without keys. It still executes the real tool handlers.
* Retries: the SDKs retry twice by default. Here the clients are constructed with `max_retries=0`
  and `with_retries()` implements backoff + jitter explicitly, so the behaviour is visible.
  See https://platform.claude.com/docs/en/api/errors and
  https://platform.openai.com/docs/guides/error-codes

Doc anchors for the API surfaces used here:
* Anthropic Messages API      https://platform.claude.com/docs/en/build-with-claude/working-with-messages
* Anthropic structured outputs https://platform.claude.com/docs/en/build-with-claude/structured-outputs
* Anthropic tool use           https://platform.claude.com/docs/en/build-with-claude/tool-use
* Anthropic stop reasons       https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
* Anthropic streaming          https://platform.claude.com/docs/en/build-with-claude/streaming
* OpenAI function calling      https://developers.openai.com/api/docs/guides/function-calling
* OpenAI structured outputs    https://platform.openai.com/docs/guides/structured-outputs
"""

from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Iterator, Literal, Sequence, Type, TypeVar

from pydantic import BaseModel

from inventory import TOOLS, SYSTEM_PROMPT, ToolSpec, run_tool

ModelT = TypeVar("ModelT", bound=BaseModel)
Provider = Literal["anthropic", "openai"]

DEFAULT_MODELS: dict[str, str] = {
    "anthropic": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"),
    "openai": os.environ.get("OPENAI_MODEL", "gpt-5.6-terra"),
}

# --------------------------------------------------------------------------------------
# Environment loading (tiny .env reader so there is no python-dotenv dependency)
# --------------------------------------------------------------------------------------


def load_env(path: str | Path | None = None) -> None:
    """Load KEY=VALUE lines from a .env beside this file into os.environ (no overwrite)."""
    env_path = Path(path) if path else Path(__file__).with_name(".env")
    if not env_path.exists():
        return
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


def credential_status() -> dict[str, bool]:
    return {p: bool(os.environ.get(f"{p.upper()}_API_KEY")) for p in ("anthropic", "openai")}


# --------------------------------------------------------------------------------------
# Result types
# --------------------------------------------------------------------------------------


@dataclass
class Usage:
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    calls: int = 0
    latency_s: float = 0.0

    def add(self, other: "Usage") -> "Usage":
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
    name: str
    arguments: dict[str, Any]
    result: dict[str, Any]
    round: int
    call_id: str = ""

    @property
    def failed(self) -> bool:
        return "error" in self.result


@dataclass
class ToolLoopResult:
    final_text: str
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    rounds: int = 0
    stop_reason: str = ""
    usage: Usage | None = None
    transcript: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Retry helpers — backoff with jitter, honouring Retry-After
# --------------------------------------------------------------------------------------

RETRYABLE_NAMES = {
    "RateLimitError",
    "OverloadedError",
    "ServiceUnavailableError",
    "InternalServerError",
    "APIConnectionError",
    "APITimeoutError",
    "RetryableError",
    "ConflictError",
    "Timeout",
    "DeadlineExceededError",
}
RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504, 529}


def describe_error(exc: BaseException) -> str:
    """Human-readable error line that works for both SDKs and for the mock provider."""
    name = type(exc).__name__
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    msg = getattr(exc, "message", None) or str(exc)
    bits = [name]
    if status:
        bits.append(f"status={status}")
    return f"{' | '.join(bits)}: {msg}"


def is_retryable(exc: BaseException) -> bool:
    name = type(exc).__name__
    status = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
    if name in RETRYABLE_NAMES:
        return True
    return bool(status) and int(status) in RETRYABLE_STATUS


def retry_after_seconds(exc: BaseException) -> float | None:
    """Read Retry-After / retry-after-ms from the response headers, if present."""
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None
    for key in ("retry-after-ms", "Retry-After-Ms"):
        if key in headers:
            try:
                return float(headers[key]) / 1000.0
            except (TypeError, ValueError):
                pass
    for key in ("retry-after", "Retry-After"):
        if key in headers:
            try:
                return float(headers[key])
            except (TypeError, ValueError):
                pass
    return None


def with_retries(
    fn: Callable[[], Any],
    *,
    attempts: int = 4,
    base_delay: float = 0.8,
    max_delay: float = 8.0,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> tuple[Any, int]:
    """Call fn(), retrying retryable failures with exponential backoff + full jitter."""
    last: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn(), attempt - 1
        except BaseException as exc:  # noqa: BLE001 - re-raised below when not retryable
            last = exc
            if not is_retryable(exc) or attempt == attempts:
                raise
            delay = retry_after_seconds(exc)
            if delay is None:
                delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                delay = random.uniform(0, delay)  # full jitter
            delay = min(delay, max_delay)
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
    raise last  # pragma: no cover - unreachable


async def awith_retries(
    fn: Callable[[], Any],
    *,
    attempts: int = 4,
    base_delay: float = 0.8,
    max_delay: float = 8.0,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> tuple[Any, int]:
    """Async twin of with_retries()."""
    last: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await fn(), attempt - 1
        except BaseException as exc:  # noqa: BLE001
            last = exc
            if not is_retryable(exc) or attempt == attempts:
                raise
            delay = retry_after_seconds(exc)
            if delay is None:
                delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                delay = random.uniform(0, delay)
            delay = min(delay, max_delay)
            if on_retry:
                on_retry(attempt, exc, delay)
            await asyncio.sleep(delay)
    raise last  # pragma: no cover


# --------------------------------------------------------------------------------------
# Pure payload builders — the exact request shapes, inspectable offline
# --------------------------------------------------------------------------------------


def anthropic_parse_kwargs(
    model: str,
    prompt: str,
    schema: Type[BaseModel],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """SDK-helper path: messages.parse(output_format=Model) sets output_config.format for you.

    https://platform.claude.com/docs/en/build-with-claude/structured-outputs#how-sdk-transformation-works
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "output_format": schema,
    }
    if system:
        kwargs["system"] = system
    return kwargs


def anthropic_raw_schema_kwargs(
    model: str,
    prompt: str,
    json_schema: dict[str, Any],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Raw JSON schema path: the schema travels in output_config.format.

    https://platform.claude.com/docs/en/build-with-claude/structured-outputs#using-a-raw-json-schema
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"format": {"type": "json_schema", "schema": json_schema}},
    }
    if system:
        kwargs["system"] = system
    return kwargs


def anthropic_tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Anthropic tool definitions. strict=True guarantees schema-valid tool inputs."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
            "strict": t.strict,
        }
        for t in tools
    ]


def anthropic_tool_kwargs(
    model: str,
    messages: list[dict[str, Any]],
    tools: Sequence[ToolSpec],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    parallel: bool = True,
) -> dict[str, Any]:
    """Anthropic tool-call request. tool_choice.disable_parallel_tool_use caps calls per turn.

    https://platform.claude.com/docs/en/build-with-claude/tool-use#how-tool-use-works
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "tools": anthropic_tool_schema(tools),
        "tool_choice": {"type": "auto", "disable_parallel_tool_use": not parallel},
    }
    if system:
        kwargs["system"] = system
    return kwargs


def openai_parse_kwargs(
    model: str,
    prompt: str,
    schema: Type[BaseModel],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """SDK-helper path: responses.parse(text_format=Model) builds the strict json_schema format.

    https://platform.openai.com/docs/guides/structured-outputs
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "text_format": schema,
        "max_output_tokens": max_tokens,
    }
    if system:
        kwargs["instructions"] = system
    return kwargs


def openai_raw_schema_kwargs(
    model: str,
    prompt: str,
    json_schema: dict[str, Any],
    *,
    name: str = "inventory_payload",
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Raw json_schema response format. Strict mode requires additionalProperties: false and
    every property listed in `required` (optionality is expressed with nullable types).

    https://platform.openai.com/docs/guides/structured-outputs
    """
    kwargs: dict[str, Any] = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "text": {"format": {"type": "json_schema", "name": name, "schema": json_schema, "strict": True}},
        "max_output_tokens": max_tokens,
    }
    if system:
        kwargs["instructions"] = system
    return kwargs


def openai_tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Responses API tool definitions are flat (no nested "function" object).

    https://developers.openai.com/api/docs/guides/function-calling
    """
    return [
        {
            "type": "function",
            "name": t.name,
            "description": t.description,
            "parameters": t.input_schema,
            "strict": t.strict,
        }
        for t in tools
    ]


def openai_chat_tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Chat Completions tool definitions are nested under "function" — the classic format trap."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
                "strict": t.strict,
            },
        }
        for t in tools
    ]


def openai_tool_kwargs(
    model: str,
    input_items: list[dict[str, Any]],
    tools: Sequence[ToolSpec],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    parallel: bool = True,
    previous_response_id: str | None = None,
) -> dict[str, Any]:
    """Responses API tool request. previous_response_id chains turns server-side."""
    kwargs: dict[str, Any] = {
        "model": model,
        "input": input_items,
        "tools": openai_tool_schema(tools),
        "max_output_tokens": max_tokens,
        "parallel_tool_calls": parallel,
    }
    if system:
        kwargs["instructions"] = system
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id
    return kwargs


# --------------------------------------------------------------------------------------
# Clients
# --------------------------------------------------------------------------------------


class BaseClient:
    """Common surface implemented by the real provider clients and by MockClient."""

    provider: str = "base"
    model: str = ""

    # --- structured output -----------------------------------------------------------------
    def structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                   max_tokens: int = 1024) -> StructuredResult:
        raise NotImplementedError

    def structured_raw(self, prompt: str, json_schema: dict[str, Any], *, name: str = "payload",
                       system: str | None = None, max_tokens: int = 1024) -> StructuredResult:
        raise NotImplementedError

    # --- tools -----------------------------------------------------------------------------
    def tool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                  system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                  parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        raise NotImplementedError

    # --- streaming -------------------------------------------------------------------------
    def stream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                    on_delta: Callable[[str], None] | None = None) -> str:
        raise NotImplementedError

    def stream_events(self, prompt: str, *, system: str | None = None, max_tokens: int = 256,
                      limit: int = 60, mode: Literal["text", "tools"] = "text") -> list[str]:
        raise NotImplementedError

    # OpenAI-only surfaces, declared here so callers can branch on hasattr() honestly.
    def tool_loop_chat_completions(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        raise NotImplementedError

    def stream_chat_tool_arguments(self, prompt: str, **kwargs: Any) -> dict[int, dict[str, str]]:
        raise NotImplementedError

    def stream_structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        raise NotImplementedError

    # --- async twins -----------------------------------------------------------------------
    async def astructured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        raise NotImplementedError

    async def atool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                         system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                         parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        raise NotImplementedError

    async def astream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                           on_delta: Callable[[str], None] | None = None) -> str:
        raise NotImplementedError

    # --- introspection ---------------------------------------------------------------------
    def list_models(self, limit: int = 40) -> list[str]:
        raise NotImplementedError


def _usage_from(resp: Any, provider: str, model: str, latency: float) -> Usage:
    u = getattr(resp, "usage", None)
    return Usage(
        provider=provider,
        model=model,
        input_tokens=int(getattr(u, "input_tokens", 0) or 0),
        output_tokens=int(getattr(u, "output_tokens", 0) or 0),
        calls=1,
        latency_s=latency,
    )


class AnthropicClient(BaseClient):
    """Anthropic Claude SDK. Sync + async, structured outputs, tool loop, streaming."""

    provider = "anthropic"

    def __init__(self, model: str | None = None, *, timeout: float = 60.0, max_retries: int = 0):
        import anthropic  # imported lazily so --dry-run works without the package installed

        self._anthropic = anthropic
        self.model = model or DEFAULT_MODELS["anthropic"]
        # max_retries=0: this file implements retries explicitly (see with_retries).
        self.client = anthropic.Anthropic(timeout=timeout, max_retries=max_retries)
        self.async_client = anthropic.AsyncAnthropic(timeout=timeout, max_retries=max_retries)

    # -- structured output ---------------------------------------------------------------
    def structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                   max_tokens: int = 1024) -> StructuredResult:
        kwargs = anthropic_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.messages.parse(**kwargs))
        usage = _usage_from(resp, self.provider, self.model, time.perf_counter() - started)
        return StructuredResult(
            parsed=resp.parsed_output,
            raw_text=_first_text(resp),
            usage=usage,
            payload=_redact(kwargs),
            retries=retries,
        )

    def structured_raw(self, prompt: str, json_schema: dict[str, Any], *, name: str = "payload",
                       system: str | None = None, max_tokens: int = 1024) -> StructuredResult:
        kwargs = anthropic_raw_schema_kwargs(self.model, prompt, json_schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.messages.create(**kwargs))
        usage = _usage_from(resp, self.provider, self.model, time.perf_counter() - started)
        text = _first_text(resp)
        return StructuredResult(parsed=json.loads(text), raw_text=text, usage=usage,
                                payload=_redact(kwargs), retries=retries)

    # -- tools ---------------------------------------------------------------------------
    def tool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                  system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                  parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = anthropic_tool_kwargs(self.model, messages, tools, system=system,
                                           max_tokens=budget, parallel=parallel)
            started = time.perf_counter()
            resp, _ = with_retries(lambda: self.client.messages.create(**kwargs))
            result.usage.add(_usage_from(resp, self.provider, self.model, time.perf_counter() - started))
            result.rounds = round_no

            # Stop reasons: https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
            if resp.stop_reason == "max_tokens":
                # Truncated (possibly mid tool_use block): retry the same request with more room.
                budget = min(budget * 2, 8192)
                result.transcript.append(f"round {round_no}: stop_reason=max_tokens -> retrying with max_tokens={budget}")
                continue

            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    out = run_tool(block.name, dict(block.input))
                    result.tool_calls.append(
                        ToolCallRecord(name=block.name, arguments=dict(block.input), result=out,
                                       round=round_no, call_id=block.id)
                    )
                    if verbose:
                        result.transcript.append(
                            f"round {round_no}: {block.name}({json.dumps(block.input)}) -> "
                            f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:220]}"
                        )
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(out),
                        # Errors are returned as results so the model can correct itself.
                        "is_error": "error" in out,
                    })
                # No extra text alongside tool_result blocks.
                messages.append({"role": "user", "content": tool_results})
                continue

            # end_turn / stop_sequence / refusal / pause_turn
            result.stop_reason = resp.stop_reason or ""
            result.final_text = _first_text(resp)
            break

        return result

    # -- streaming -----------------------------------------------------------------------
    def stream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                    on_delta: Callable[[str], None] | None = None) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:  # SDK-accumulated text deltas
                if on_delta:
                    on_delta(text)
            final = stream.get_final_message()  # no manual event assembly needed
        return _first_text(final)

    def stream_events(self, prompt: str, *, system: str | None = None, max_tokens: int = 256,
                      limit: int = 60, mode: Literal["text", "tools"] = "text") -> list[str]:
        """Raw event walk: message_start -> content_block_* -> message_delta -> message_stop.

        mode="tools" adds the tool definitions, so the stream carries a tool_use block whose
        arguments arrive as input_json_delta fragments.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if mode == "tools":
            kwargs["tools"] = anthropic_tool_schema(TOOLS)
        if system:
            kwargs["system"] = system
        seen: list[str] = []
        with self.client.messages.stream(**kwargs) as stream:
            for event in stream:
                etype = getattr(event, "type", "unknown")
                detail = ""
                if etype == "content_block_delta":
                    delta = event.delta
                    dtype = getattr(delta, "type", "")
                    detail = f" index={event.index} delta={dtype}"
                    if dtype == "text_delta":
                        detail += f" text={getattr(delta, 'text', '')!r}"
                    elif dtype == "input_json_delta":
                        detail += f" partial_json={getattr(delta, 'partial_json', '')!r}"
                elif etype == "message_delta":
                    detail = f" stop_reason={getattr(event.delta, 'stop_reason', None)}"
                elif etype == "error":
                    detail = f" error={getattr(getattr(event, 'error', None), 'type', '')}"
                seen.append(f"event={etype}{detail}")
                if len(seen) >= limit:
                    break
        return seen

    def stream_structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        """Structured output + streaming: text deltas arrive, the final message carries parsed_output."""
        kwargs = anthropic_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        deltas: list[str] = []
        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                deltas.append(text)
            final = stream.get_final_message()
        return StructuredResult(parsed=final.parsed_output, raw_text="".join(deltas),
                                usage=_usage_from(final, self.provider, self.model, 0.0),
                                payload=_redact(kwargs))

    # -- async ---------------------------------------------------------------------------
    async def astructured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        kwargs = anthropic_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = await awith_retries(lambda: self.async_client.messages.parse(**kwargs))
        return StructuredResult(parsed=resp.parsed_output, raw_text=_first_text(resp),
                                usage=_usage_from(resp, self.provider, self.model, time.perf_counter() - started),
                                payload=_redact(kwargs), retries=retries)

    async def atool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                         system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                         parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens
        for round_no in range(1, max_rounds + 1):
            kwargs = anthropic_tool_kwargs(self.model, messages, tools, system=system,
                                           max_tokens=budget, parallel=parallel)
            started = time.perf_counter()
            resp, _ = await awith_retries(lambda: self.async_client.messages.create(**kwargs))
            result.usage.add(_usage_from(resp, self.provider, self.model, time.perf_counter() - started))
            result.rounds = round_no
            if resp.stop_reason == "max_tokens":
                budget = min(budget * 2, 8192)
                continue
            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    out = run_tool(block.name, dict(block.input))
                    result.tool_calls.append(ToolCallRecord(block.name, dict(block.input), out, round_no, block.id))
                    tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                         "content": json.dumps(out), "is_error": "error" in out})
                messages.append({"role": "user", "content": tool_results})
                continue
            result.stop_reason = resp.stop_reason or ""
            result.final_text = _first_text(resp)
            break
        return result

    async def astream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                           on_delta: Callable[[str], None] | None = None) -> str:
        kwargs: dict[str, Any] = {"model": self.model, "max_tokens": max_tokens,
                                  "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        async with self.async_client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                if on_delta:
                    on_delta(text)
            final = await stream.get_final_message()
        return _first_text(final)

    def list_models(self, limit: int = 40) -> list[str]:
        return [m.id for m in self.client.models.list(limit=limit).data]


class OpenAIClient(BaseClient):
    """OpenAI SDK — Responses API primary (function calling + structured outputs), plus a
    Chat Completions variant for the format differences."""

    provider = "openai"

    def __init__(self, model: str | None = None, *, timeout: float = 60.0, max_retries: int = 0):
        import openai

        self._openai = openai
        self.model = model or DEFAULT_MODELS["openai"]
        self.client = openai.OpenAI(timeout=timeout, max_retries=max_retries)
        self.async_client = openai.AsyncOpenAI(timeout=timeout, max_retries=max_retries)

    # -- structured output ---------------------------------------------------------------
    def structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                   max_tokens: int = 1024) -> StructuredResult:
        kwargs = openai_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.responses.parse(**kwargs))
        return StructuredResult(parsed=resp.output_parsed, raw_text=resp.output_text or "",
                                usage=_usage_from(resp, self.provider, self.model, time.perf_counter() - started),
                                payload=_redact(kwargs), retries=retries)

    def structured_raw(self, prompt: str, json_schema: dict[str, Any], *, name: str = "payload",
                       system: str | None = None, max_tokens: int = 1024) -> StructuredResult:
        kwargs = openai_raw_schema_kwargs(self.model, prompt, json_schema, name=name,
                                          system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.responses.create(**kwargs))
        text = resp.output_text or ""
        return StructuredResult(parsed=json.loads(text) if text else None, raw_text=text,
                                usage=_usage_from(resp, self.provider, self.model, time.perf_counter() - started),
                                payload=_redact(kwargs), retries=retries)

    # -- tools ---------------------------------------------------------------------------
    def tool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                  system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                  parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        input_items: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        previous_response_id: str | None = None
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = openai_tool_kwargs(self.model, input_items, tools, system=system, max_tokens=budget,
                                        parallel=parallel, previous_response_id=previous_response_id)
            started = time.perf_counter()
            resp, _ = with_retries(lambda: self.client.responses.create(**kwargs))
            result.usage.add(_usage_from(resp, self.provider, self.model, time.perf_counter() - started))
            result.rounds = round_no

            incomplete = getattr(resp, "incomplete_details", None)
            if getattr(resp, "status", "") == "incomplete" and getattr(incomplete, "reason", "") == "max_output_tokens":
                budget = min(budget * 2, 8192)
                result.transcript.append(f"round {round_no}: incomplete (max_output_tokens) -> retry with {budget}")
                continue

            calls = [item for item in resp.output if getattr(item, "type", "") == "function_call"]
            if calls:
                outputs = []
                for call in calls:
                    try:
                        arguments = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                    out = run_tool(call.name, arguments)
                    result.tool_calls.append(
                        ToolCallRecord(name=call.name, arguments=arguments, result=out,
                                       round=round_no, call_id=call.call_id)
                    )
                    if verbose:
                        result.transcript.append(
                            f"round {round_no}: {call.name}({json.dumps(arguments)}) -> "
                            f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:220]}"
                        )
                    outputs.append({"type": "function_call_output", "call_id": call.call_id,
                                    "output": json.dumps(out)})
                input_items = outputs           # only the new items...
                previous_response_id = resp.id  # ...because the server keeps the prior turn
                continue

            result.final_text = resp.output_text or ""
            result.stop_reason = getattr(resp, "status", "") or ""
            break

        return result

    def tool_loop_chat_completions(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                                   system: str | None = None, max_rounds: int = 6,
                                   max_tokens: int = 1024) -> ToolLoopResult:
        """Same loop on Chat Completions — nested tool defs, message.tool_calls, role='tool'."""
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        for round_no in range(1, max_rounds + 1):
            started = time.perf_counter()
            resp, _ = with_retries(lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=openai_chat_tool_schema(tools),
                max_completion_tokens=max_tokens,
            ))
            result.usage.add(_usage_from(resp, self.provider, self.model, time.perf_counter() - started))
            result.rounds = round_no
            message = resp.choices[0].message
            if message.tool_calls:
                messages.append(message.model_dump(exclude_none=True))
                for call in message.tool_calls:
                    arguments = json.loads(call.function.arguments or "{}")
                    out = run_tool(call.function.name, arguments)
                    result.tool_calls.append(ToolCallRecord(call.function.name, arguments, out,
                                                            round_no, call.id or ""))
                    messages.append({"role": "tool", "tool_call_id": call.id,
                                     "content": json.dumps(out)})
                continue
            result.final_text = message.content or ""
            result.stop_reason = resp.choices[0].finish_reason or ""
            break
        return result

    # -- streaming -----------------------------------------------------------------------
    def stream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                    on_delta: Callable[[str], None] | None = None) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": [{"role": "user", "content": prompt}],
            "max_output_tokens": max_tokens,
        }
        if system:
            kwargs["instructions"] = system
        chunks: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    chunks.append(event.delta)
                    if on_delta:
                        on_delta(event.delta)
                elif event.type == "response.refusal.delta":
                    chunks.append(f"[refusal] {event.delta}")
                elif event.type == "response.error":
                    raise RuntimeError(f"stream error event: {event.error}")
            final = stream.get_final_response()
        return final.output_text or "".join(chunks)

    def stream_events(self, prompt: str, *, system: str | None = None, max_tokens: int = 256,
                      limit: int = 60, mode: Literal["text", "tools"] = "text") -> list[str]:
        kwargs: dict[str, Any] = {"model": self.model, "input": [{"role": "user", "content": prompt}],
                                  "max_output_tokens": max_tokens}
        if mode == "tools":
            kwargs["tools"] = openai_tool_schema(TOOLS)
        if system:
            kwargs["instructions"] = system
        seen: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                etype = getattr(event, "type", "unknown")
                detail = ""
                if etype == "response.output_text.delta":
                    detail = f" delta={event.delta!r}"
                elif etype == "response.function_call_arguments.delta":
                    detail = f" name={getattr(event, 'name', '')} delta={event.delta!r}"
                elif etype == "response.function_call_arguments.done":
                    detail = f" name={getattr(event, 'name', '')} arguments={event.arguments!r}"
                elif etype == "response.error":
                    detail = f" error={event.error}"
                seen.append(f"event={etype}{detail}")
                if len(seen) >= limit:
                    break
        return seen

    def stream_structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        kwargs = openai_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        chunks: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    chunks.append(event.delta)
                elif event.type == "response.refusal.delta":
                    chunks.append(f"[refusal] {event.delta}")
                elif event.type == "response.error":
                    raise RuntimeError(f"stream error event: {event.error}")
            final = stream.get_final_response()
        return StructuredResult(parsed=final.output_parsed, raw_text="".join(chunks),
                                usage=_usage_from(final, self.provider, self.model, 0.0),
                                payload=_redact(kwargs))

    def stream_chat_tool_arguments(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                                   system: str | None = None, max_tokens: int = 512) -> dict[int, dict[str, str]]:
        """Chat Completions streams tool arguments as fragments: accumulate per index, then json.loads.

        https://developers.openai.com/api/docs/guides/function-calling (streaming section)
        """
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        assembled: dict[int, dict[str, str]] = {}
        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, tools=openai_chat_tool_schema(tools),
            max_completion_tokens=max_tokens, stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            for tc in (delta.tool_calls or []):
                entry = assembled.setdefault(tc.index, {"name": "", "arguments": ""})
                if tc.function and tc.function.name:
                    entry["name"] = tc.function.name
                if tc.function and tc.function.arguments:
                    entry["arguments"] += tc.function.arguments
        return assembled

    # -- async ---------------------------------------------------------------------------
    async def astructured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        kwargs = openai_parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = await awith_retries(lambda: self.async_client.responses.parse(**kwargs))
        return StructuredResult(parsed=resp.output_parsed, raw_text=resp.output_text or "",
                                usage=_usage_from(resp, self.provider, self.model, time.perf_counter() - started),
                                payload=_redact(kwargs), retries=retries)

    async def atool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                         system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                         parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        input_items: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        previous_response_id: str | None = None
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens
        for round_no in range(1, max_rounds + 1):
            kwargs = openai_tool_kwargs(self.model, input_items, tools, system=system, max_tokens=budget,
                                        parallel=parallel, previous_response_id=previous_response_id)
            started = time.perf_counter()
            resp, _ = await awith_retries(lambda: self.async_client.responses.create(**kwargs))
            result.usage.add(_usage_from(resp, self.provider, self.model, time.perf_counter() - started))
            result.rounds = round_no
            calls = [item for item in resp.output if getattr(item, "type", "") == "function_call"]
            if calls:
                outputs = []
                for call in calls:
                    try:
                        arguments = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                    out = run_tool(call.name, arguments)
                    result.tool_calls.append(ToolCallRecord(call.name, arguments, out, round_no, call.call_id))
                    outputs.append({"type": "function_call_output", "call_id": call.call_id,
                                    "output": json.dumps(out)})
                input_items = outputs
                previous_response_id = resp.id
                continue
            result.final_text = resp.output_text or ""
            result.stop_reason = getattr(resp, "status", "") or ""
            break
        return result

    async def astream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                           on_delta: Callable[[str], None] | None = None) -> str:
        kwargs: dict[str, Any] = {"model": self.model, "input": [{"role": "user", "content": prompt}],
                                  "max_output_tokens": max_tokens}
        if system:
            kwargs["instructions"] = system
        chunks: list[str] = []
        async with self.async_client.responses.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    chunks.append(event.delta)
                    if on_delta:
                        on_delta(event.delta)
            final = await stream.get_final_response()
        return final.output_text or "".join(chunks)

    def list_models(self, limit: int = 60) -> list[str]:
        return sorted(m.id for m in self.client.models.list().data)[:limit]


# --------------------------------------------------------------------------------------
# Mock provider — deterministic, offline, exercises the same control flow
# --------------------------------------------------------------------------------------


_MOCK_ERROR_TYPES: dict[str, type[Exception]] = {}


def mock_error(name: str, message: str, status_code: int | None = 500,
               retry_after: float | None = None) -> Exception:
    """Build an exception whose *class name* matches a real SDK error, so the same
    is_retryable() / describe_error() branches run in --dry-run and in live mode."""
    cls = _MOCK_ERROR_TYPES.get(name)
    if cls is None:
        cls = type(name, (Exception,), {})
        _MOCK_ERROR_TYPES[name] = cls
    exc = cls(message)
    exc.status_code = status_code
    if retry_after is not None:
        exc.response = type("MockResponse", (), {
            "status_code": status_code,
            "headers": {"retry-after": str(retry_after)},
        })()
    return exc


class MockClient(BaseClient):
    """Deterministic stand-in for a provider. Prints payloads, runs real tool handlers."""

    provider = "mock"
    fail_first_n_calls = 0  # set by the scripts to demo retry/backoff

    def __init__(self, model: str | None = None, *, label: str = "mock", real_provider: str = "anthropic",
                 interrupt_after: int | None = None):
        self.label = label
        self.model = model or DEFAULT_MODELS.get(real_provider, "mock-model")
        self.real_provider = real_provider
        self.interrupt_after = interrupt_after
        self._call_count = 0

    # -- helpers -------------------------------------------------------------------------
    def _maybe_fail(self) -> None:
        self._call_count += 1
        if self.fail_first_n_calls and self._call_count <= self.fail_first_n_calls:
            raise mock_error("RateLimitError", "simulated 429 from mock provider",
                             status_code=429, retry_after=0.2)

    def _mock_usage(self, text: str, calls: int = 1) -> Usage:
        return Usage(self.real_provider, self.model, input_tokens=len(text) // 4,
                     output_tokens=len(text) // 4, calls=calls, latency_s=0.0)

    # -- structured ----------------------------------------------------------------------
    def structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                   max_tokens: int = 1024) -> StructuredResult:
        self._maybe_fail()
        kwargs = (anthropic_parse_kwargs if self.real_provider == "anthropic" else openai_parse_kwargs)(
            self.model, prompt, schema, system=system, max_tokens=max_tokens)
        parsed = _mock_parse(schema, prompt)
        return StructuredResult(parsed=parsed, raw_text=parsed.model_dump_json(),
                                usage=self._mock_usage(prompt), payload=_redact(kwargs))

    def structured_raw(self, prompt: str, json_schema: dict[str, Any], *, name: str = "payload",
                       system: str | None = None, max_tokens: int = 1024) -> StructuredResult:
        self._maybe_fail()
        payload = {"sku": _first_sku(prompt) or "CHR-M4K25-RGB", "severity": "high",
                   "weeks_of_cover": 0.7, "root_cause": "supplier_delay"}
        return StructuredResult(parsed=payload, raw_text=json.dumps(payload),
                                usage=self._mock_usage(prompt), payload={"json_schema": json_schema, "name": name})

    # -- tools ---------------------------------------------------------------------------
    def tool_loop(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                  system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                  parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        result = self._tool_loop_impl(prompt, tools=tools, system=system, max_rounds=max_rounds,
                                      max_tokens=max_tokens, parallel=parallel, verbose=verbose)
        # Token counts estimated from the prompt plus every tool payload the loop carried.
        payload = prompt + "".join(json.dumps(c.result) for c in result.tool_calls)
        result.usage = self._mock_usage(payload, calls=max(result.rounds, 1))
        return result

    def _tool_loop_impl(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                        system: str | None = None, max_rounds: int = 6, max_tokens: int = 1024,
                        parallel: bool = True, verbose: bool = True) -> ToolLoopResult:
        tools = list(tools or TOOLS)
        result = ToolLoopResult(final_text="", usage=Usage(self.real_provider, self.model))
        skus = _skus_in(prompt) or ["CHR-M4K25-RGB"]
        result.rounds = 2
        if max_tokens < 128:
            # Emulate a truncated turn so the stop_reason=max_tokens recovery branch runs offline.
            result.transcript.append(
                f"round 1: stop_reason=max_tokens (budget={max_tokens}) -> retrying with "
                f"max_tokens={max_tokens * 2}"
            )
            result.rounds = 3

        # Round 1: a deliberate bad call (unknown SKU) then real calls — mirrors a real model
        # recovering from a tool error.
        bad = ToolCallRecord("get_sku_status", {"sku": "CHR-NOPE-000"},
                             run_tool("get_sku_status", {"sku": "CHR-NOPE-000"}), 1, "call_bad")
        result.tool_calls.append(bad)
        if verbose:
            result.transcript.append(f"round 1: get_sku_status({{'sku': 'CHR-NOPE-000'}}) -> ERROR "
                                     f"{json.dumps(bad.result)[:200]}")

        for sku in skus[:3]:
            for name, args in (("get_sku_status", {"sku": sku}),
                               ("get_lead_time", {"sku": sku}),
                               ("compute_reorder_point", {"sku": sku, "service_level": 0.95}),
                               ("query_open_positions", {"sku": sku})):
                out = run_tool(name, args)
                result.tool_calls.append(ToolCallRecord(name, args, out, 1, f"call_{name}_{sku}"))
                if verbose:
                    result.transcript.append(f"round 1: {name}({json.dumps(args)}) -> "
                                             f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:220]}")

        # Round 2: flag the worst SKU, then answer.
        worst = _worst_sku(skus)
        out = run_tool("flag_exception", {"sku": worst, "reason": "cover below reorder point after lead-time slippage",
                                          "severity": "high"})
        result.tool_calls.append(ToolCallRecord("flag_exception",
                                                {"sku": worst, "reason": "cover below reorder point", "severity": "high"},
                                                out, 2, "call_flag"))
        if verbose:
            result.transcript.append(f"round 2: flag_exception({{'sku': '{worst}', ...}}) -> {json.dumps(out)[:200]}")
        result.final_text = _mock_answer(skus, prompt)
        result.stop_reason = "end_turn" if self.real_provider == "anthropic" else "completed"
        result.usage.calls = 4 if result.rounds == 3 else 3
        return result

    def tool_loop_chat_completions(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        return self.tool_loop(prompt, **kwargs)

    # -- streaming -----------------------------------------------------------------------
    def stream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                    on_delta: Callable[[str], None] | None = None) -> str:
        text = _mock_answer(_skus_in(prompt) or ["CHR-M4K25-RGB"], prompt)
        for i, chunk in enumerate(_chunks(text, 12)):
            if self.interrupt_after is not None and i == self.interrupt_after:
                raise mock_error("APIConnectionError", "simulated mid-stream disconnect")
            if on_delta:
                on_delta(chunk)
        return text

    def stream_events(self, prompt: str, *, system: str | None = None, max_tokens: int = 256,
                      limit: int = 60, mode: Literal["text", "tools"] = "text") -> list[str]:
        sku = _first_sku(prompt) or "CHR-M4K25-RGB"
        if self.real_provider == "anthropic":
            if mode == "tools":
                base = [
                    "event=message_start",
                    "event=content_block_start index=0 block=tool_use name=get_sku_status",
                    "event=content_block_delta index=0 delta=input_json_delta partial_json='{\"sku\":'",
                    "event=content_block_delta index=0 delta=input_json_delta partial_json=' \"CHR-M4K'",
                    "event=content_block_delta index=0 delta=input_json_delta partial_json='25-RGB\"}'",
                    "event=content_block_stop index=0",
                    "event=message_delta stop_reason=tool_use",
                    "event=message_stop",
                ]
            else:
                base = ["event=message_start", "event=content_block_start index=0 block=text",
                        "event=ping",
                        "event=content_block_delta index=0 delta=text_delta text='Cover '",
                        "event=content_block_delta index=0 delta=text_delta text='is 0.7 weeks.'",
                        "event=content_block_stop index=0",
                        "event=message_delta stop_reason=end_turn",
                        "event=message_stop"]
        else:
            if mode == "tools":
                base = [
                    "event=response.created",
                    "event=response.output_item.added item=function_call name=get_sku_status",
                    "event=response.function_call_arguments.delta name=get_sku_status delta='{\"sku\":'",
                    "event=response.function_call_arguments.delta name=get_sku_status delta=' \"CHR-M4K25-RGB\"}'",
                    "event=response.function_call_arguments.done name=get_sku_status "
                    f"arguments='{{\"sku\": \"{sku}\"}}'",
                    "event=response.output_item.done",
                    "event=response.completed",
                ]
            else:
                base = ["event=response.created", "event=response.in_progress",
                        "event=response.output_item.added",
                        "event=response.output_text.delta delta='Cover '",
                        "event=response.output_text.delta delta='is 0.7 weeks.'",
                        "event=response.output_item.done", "event=response.completed"]
        return base[:limit]

    def stream_structured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        parsed = _mock_parse(schema, prompt)
        return StructuredResult(parsed=parsed, raw_text=parsed.model_dump_json(),
                                usage=self._mock_usage(prompt))

    def stream_chat_tool_arguments(self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
                                   system: str | None = None, max_tokens: int = 512) -> dict[int, dict[str, str]]:
        sku = _first_sku(prompt) or "CHR-M4K25-RGB"
        return {0: {"name": "get_sku_status", "arguments": json.dumps({"sku": sku})}}

    # -- async ---------------------------------------------------------------------------
    async def astructured(self, prompt: str, schema: Type[ModelT], *, system: str | None = None,
                          max_tokens: int = 1024) -> StructuredResult:
        await asyncio.sleep(0)
        return self.structured(prompt, schema, system=system, max_tokens=max_tokens)

    async def atool_loop(self, prompt: str, **kwargs: Any) -> ToolLoopResult:
        await asyncio.sleep(0)
        return self.tool_loop(prompt, **kwargs)

    async def astream_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 512,
                           on_delta: Callable[[str], None] | None = None) -> str:
        text = _mock_answer(_skus_in(prompt) or ["CHR-M4K25-RGB"], prompt)
        for i, chunk in enumerate(_chunks(text, 12)):
            await asyncio.sleep(0)
            if on_delta:
                on_delta(chunk)
        return text

    def list_models(self, limit: int = 40) -> list[str]:
        if self.real_provider == "anthropic":
            return ["claude-sonnet-4-5", "claude-opus-5-5", "claude-haiku-4-5"]
        return ["gpt-5.6-terra", "gpt-6-astra", "gpt-5.4"]


def make_client(provider: Provider, *, model: str | None = None, dry_run: bool = False,
                interrupt_after: int | None = None, **kwargs: Any) -> BaseClient:
    """Factory: real client, or a MockClient labelled with the provider it stands in for."""
    if dry_run:
        return MockClient(model=model, real_provider=provider, interrupt_after=interrupt_after)
    if provider == "anthropic":
        return AnthropicClient(model=model, **kwargs)
    if provider == "openai":
        return OpenAIClient(model=model, **kwargs)
    raise ValueError(f"unknown provider {provider!r}")


# --------------------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------------------


def _first_text(resp: Any) -> str:
    """Concatenate text blocks from an Anthropic Message, or return OpenAI output_text."""
    if hasattr(resp, "output_text") and isinstance(getattr(resp, "output_text"), str):
        return resp.output_text
    parts: list[str] = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", "") == "text":
            parts.append(getattr(block, "text", ""))
    return "".join(parts)


def _redact(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Copy of a payload with the pydantic class replaced by its JSON schema (for printing)."""
    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        if isinstance(value, type) and issubclass(value, BaseModel):
            out[key] = f"<{value.__name__} -> json_schema>"
        else:
            out[key] = value
    return out


def _first_sku(text: str) -> str | None:
    skus = _skus_in(text)
    return skus[0] if skus else None


def _skus_in(text: str) -> list[str]:
    from inventory import INVENTORY

    found: list[str] = []
    upper = text.upper()
    for sku in INVENTORY:
        if sku in upper and sku not in found:
            found.append(sku)
    return found


def _worst_sku(skus: Sequence[str]) -> str:
    from inventory import INVENTORY, _cover_weeks

    def key(sku: str) -> float:
        rec = INVENTORY.get(sku)
        return _cover_weeks(rec) if rec else 99.0

    return min(skus, key=key)


def _chunks(text: str, size: int) -> Iterator[str]:
    for i in range(0, len(text), size):
        yield text[i:i + size]


def _mock_parse(schema: Type[ModelT], prompt: str) -> Any:
    """Deterministic, schema-valid answers so --dry-run exercises real validation paths."""
    from inventory import ExceptionTriage, ExceptionTriageBatch, InventoryException, DemandSignal, ReorderDecision

    sku = _first_sku(prompt) or "CHR-M4K25-RGB"
    if schema is InventoryException:
        low = prompt.lower()
        slip = 23 if "slipp" in low or "68" in prompt else 0
        if any(w in low for w in ("break the install", "at zero on hand", "shortage", "zero on hand")):
            severity, root = "critical", "supplier_delay"
        elif any(w in low for w in ("demand came in", "double forecast", "spiking", "spike")):
            severity, root = "high", "demand_spike"
        elif any(w in low for w in ("forecast", "planning input")):
            severity, root = "medium", "forecast_error"
        elif "no action" in low:
            severity, root = "low", "none"
        else:
            severity, root = "high", "supplier_delay"
        return InventoryException(
            sku=sku, severity=severity, root_cause=root,
            weeks_of_cover=0.7, lead_time_impact_days=slip,
            recommended_action=f"Expedite open PO for {sku} and pull cover from the EMEA buffer",
            requires_escalation=True, confidence=0.86,
        )
    if schema is ExceptionTriageBatch:
        notes = [n.strip() for n in re.split(r"\n{2,}", prompt) if n.strip()]
        notes = [re.sub(r"^\[\d+\]\s*", "", n) for n in notes
                 if not n.lower().startswith(("classify each", "you are"))]
        if not notes:
            notes = [prompt]
        return ExceptionTriageBatch(items=[_mock_triage(n) for n in notes[:8]])
    if schema is DemandSignal:
        return DemandSignal(sku=sku, direction="up", pct_change=40.0,
                            driver="education tender volume", confidence=0.72)
    if schema is ReorderDecision:
        return ReorderDecision(sku=sku, decision="expedite_existing_po", order_quantity=0,
                               weeks_of_cover=0.7,
                               rationale=("On-hand cover is 0.7 weeks against a 68-day observed lead time, "
                                          "and one of two open POs is already flagged at risk."))
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


def _mock_triage(note: str) -> Any:
    """Deterministic classification of one supplier message, so the batch demo has real content."""
    from inventory import ExceptionTriage

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

    if "cannot confirm" in low or "shortage" in low:
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
        sku=_first_sku(note) or "UNKNOWN",
        category=category,
        priority=priority,
        requires_human=category != "logistics_update",
        one_line_summary=summary[:80],
    )


def _mock_answer(skus: Sequence[str], prompt: str = "") -> str:
    from inventory import INVENTORY, _cover_weeks

    low = prompt.lower()
    if "worst" in low or "slippage" in low:
        ranked = sorted(
            INVENTORY.items(),
            key=lambda kv: kv[1]["actual_lt_p90_days"] - kv[1]["quoted_lt_days"],
            reverse=True,
        )[:2]
        rows = [
            f"{sku}: {rec['actual_lt_p90_days']}d observed vs {rec['quoted_lt_days']}d quoted "
            f"({rec['actual_lt_p90_days'] - rec['quoted_lt_days']:+d}d slippage)."
            for sku, rec in ranked
        ]
        return "Worst lead-time slippage:\n" + "\n".join(rows)
    if "stockout" in low or "closest" in low:
        sku, rec = min(INVENTORY.items(), key=lambda kv: _cover_weeks(kv[1]))
        return (f"Closest to stockout: {sku} — {_cover_weeks(rec):.1f} weeks of cover "
                f"({rec['on_hand']} on hand against {rec['allocated']} allocated, "
                f"{rec['in_transit']} in transit).")

    lines = []
    for sku in skus[:3]:
        rec = INVENTORY.get(sku)
        if not rec:
            continue
        lines.append(
            f"{sku}: {rec['on_hand']} on hand, {rec['allocated']} allocated, "
            f"{rec['in_transit']} in transit -> {_cover_weeks(rec):.1f} weeks of cover; "
            f"lead time {rec['quoted_lt_days']}d quoted vs {rec['actual_lt_p90_days']}d observed "
            f"({rec['actual_lt_p90_days'] - rec['quoted_lt_days']:+d}d slippage)."
        )
    return "Position review:\n" + "\n".join(lines) + "\nRecommendation: expedite the at-risk PO before reordering."
