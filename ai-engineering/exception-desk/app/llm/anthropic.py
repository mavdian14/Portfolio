"""Anthropic Claude client.

The request payloads are built by pure module-level functions so the exact body sent to the
API is inspectable and printable without making a call. That is what makes the mock honest:
it reuses these builders and swaps only the transport.

Docs
  https://platform.claude.com/docs/en/build-with-claude/working-with-messages
  https://platform.claude.com/docs/en/build-with-claude/structured-outputs
  https://platform.claude.com/docs/en/build-with-claude/tool-use
  https://platform.claude.com/docs/en/build-with-claude/streaming
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable, Sequence
from typing import Any, Literal

from app.domain.inventory import TOOLS, ToolSpec, run_tool
from app.llm.base import (
    BaseClient,
    ModelT,
    StructuredResult,
    ToolCallRecord,
    ToolLoopResult,
    Usage,
    usage_from,
)
from app.llm.retry import awith_retries, with_retries

# --------------------------------------------------------------------------------------
# Pure payload builders
# --------------------------------------------------------------------------------------


def parse_kwargs(
    model: str,
    prompt: str,
    schema: type[Any],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """SDK-helper path: ``messages.parse(output_format=Model)``.

    Note the kwarg name: ``messages.parse`` takes ``output_format``, while
    ``messages.create`` takes ``output_config`` and does not accept ``output_format`` at
    all. Two names, two methods — the most common early mistake against this API.
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


def raw_schema_kwargs(
    model: str,
    prompt: str,
    json_schema: dict[str, Any],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Raw JSON-schema path: the schema travels in ``output_config.format``."""
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {"format": {"type": "json_schema", "schema": json_schema}},
    }
    if system:
        kwargs["system"] = system
    return kwargs


def tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Anthropic tool definitions: ``input_schema``, with ``strict`` alongside it."""
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.input_schema,
            "strict": t.strict,
        }
        for t in tools
    ]


def tool_kwargs(
    model: str,
    messages: list[dict[str, Any]],
    tools: Sequence[ToolSpec],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    parallel: bool = True,
) -> dict[str, Any]:
    """Tool request. Parallelism is disabled inside ``tool_choice``, not at the top level."""
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "tools": tool_schema(tools),
        "tool_choice": {"type": "auto", "disable_parallel_tool_use": not parallel},
    }
    if system:
        kwargs["system"] = system
    return kwargs


def first_text(resp: Any) -> str:
    """Concatenate the ``text`` content blocks of a Message."""
    parts: list[str] = []
    for block in getattr(resp, "content", []) or []:
        if getattr(block, "type", "") == "text":
            parts.append(getattr(block, "text", ""))
    return "".join(parts)


# --------------------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------------------


class AnthropicClient(BaseClient):
    provider = "anthropic"

    def __init__(
        self,
        model: str | None = None,
        *,
        api_key: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 0,
    ) -> None:
        import anthropic  # imported lazily so the mock path needs no SDK installed

        self.model = model or "claude-sonnet-4-5"
        # max_retries=0: app.llm.retry owns the retry policy, so it is visible and testable.
        self.client = anthropic.Anthropic(
            api_key=api_key or None, timeout=timeout, max_retries=max_retries
        )
        self.async_client = anthropic.AsyncAnthropic(
            api_key=api_key or None, timeout=timeout, max_retries=max_retries
        )

    # -- structured output -------------------------------------------------------------
    def structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        kwargs = parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.messages.parse(**kwargs))
        return StructuredResult(
            parsed=resp.parsed_output,
            raw_text=first_text(resp),
            usage=usage_from(resp, self.provider, self.model, time.perf_counter() - started),
            payload=_printable(kwargs),
            retries=retries,
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
        kwargs = raw_schema_kwargs(
            self.model, prompt, json_schema, system=system, max_tokens=max_tokens
        )
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.messages.create(**kwargs))
        text = first_text(resp)
        return StructuredResult(
            parsed=json.loads(text) if text else None,
            raw_text=text,
            usage=usage_from(resp, self.provider, self.model, time.perf_counter() - started),
            payload=_printable(kwargs),
            retries=retries,
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
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = tool_kwargs(
                self.model, messages, tools, system=system, max_tokens=budget, parallel=parallel
            )
            started = time.perf_counter()
            resp, _ = with_retries(lambda kw=kwargs: self.client.messages.create(**kw))
            result.usage.add(
                usage_from(resp, self.provider, self.model, time.perf_counter() - started)
            )
            result.rounds = round_no

            if resp.stop_reason == "max_tokens":
                # A truncated turn can end mid-tool-call, leaving an unparseable block.
                # Re-issue the same request with more room rather than guessing at it.
                budget = min(budget * 2, 8192)
                result.transcript.append(
                    f"round {round_no}: stop_reason=max_tokens -> retrying with max_tokens={budget}"
                )
                continue

            if resp.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": resp.content})
                tool_results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    out = run_tool(block.name, dict(block.input))
                    result.tool_calls.append(
                        ToolCallRecord(
                            name=block.name,
                            arguments=dict(block.input),
                            result=out,
                            round=round_no,
                            call_id=block.id,
                        )
                    )
                    if verbose:
                        result.transcript.append(
                            f"round {round_no}: {block.name}({json.dumps(block.input)}) -> "
                            f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:200]}"
                        )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(out),
                            # Errors go back as results so the model can correct itself.
                            "is_error": "error" in out,
                        }
                    )
                # Tool results travel in a USER turn, with no text alongside them.
                messages.append({"role": "user", "content": tool_results})
                continue

            result.stop_reason = resp.stop_reason or ""
            result.final_text = first_text(resp)
            break

        return result

    # -- streaming ---------------------------------------------------------------------
    def stream_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 512,
        on_delta: Callable[[str], None] | None = None,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:  # SDK-accumulated deltas
                if on_delta:
                    on_delta(text)
            final = stream.get_final_message()
        return first_text(final)

    def stream_events(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 256,
        limit: int = 60,
        mode: Literal["text", "tools"] = "text",
    ) -> list[str]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if mode == "tools":
            kwargs["tools"] = tool_schema(TOOLS)
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

    def stream_structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        kwargs = parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        deltas: list[str] = []
        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                deltas.append(text)
            final = stream.get_final_message()
        return StructuredResult(
            parsed=final.parsed_output,
            raw_text="".join(deltas),
            usage=usage_from(final, self.provider, self.model, 0.0),
            payload=_printable(kwargs),
        )

    # -- async -------------------------------------------------------------------------
    async def astructured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        kwargs = parse_kwargs(self.model, prompt, schema, system=system, max_tokens=max_tokens)
        started = time.perf_counter()
        resp, retries = await awith_retries(lambda: self.async_client.messages.parse(**kwargs))
        return StructuredResult(
            parsed=resp.parsed_output,
            raw_text=first_text(resp),
            usage=usage_from(resp, self.provider, self.model, time.perf_counter() - started),
            payload=_printable(kwargs),
            retries=retries,
        )

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
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = tool_kwargs(
                self.model, messages, tools, system=system, max_tokens=budget, parallel=parallel
            )
            started = time.perf_counter()
            resp, _ = await awith_retries(
                lambda kw=kwargs: self.async_client.messages.create(**kw)
            )
            result.usage.add(
                usage_from(resp, self.provider, self.model, time.perf_counter() - started)
            )
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
                    result.tool_calls.append(
                        ToolCallRecord(block.name, dict(block.input), out, round_no, block.id)
                    )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(out),
                            "is_error": "error" in out,
                        }
                    )
                messages.append({"role": "user", "content": tool_results})
                continue

            result.stop_reason = resp.stop_reason or ""
            result.final_text = first_text(resp)
            break

        return result

    async def astream_text(
        self,
        prompt: str,
        *,
        system: str | None = None,
        max_tokens: int = 512,
        on_delta: Callable[[str], None] | None = None,
    ) -> str:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        async with self.async_client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                if on_delta:
                    on_delta(text)
            final = await stream.get_final_message()
        return first_text(final)

    def list_models(self, limit: int = 40) -> list[str]:
        return [m.id for m in self.client.models.list(limit=limit).data]


def _printable(kwargs: dict[str, Any]) -> dict[str, Any]:
    """A copy of a payload with any pydantic *class* replaced by a placeholder.

    Without this, printing the request body fails: a class cannot be JSON-serialised.
    """
    from pydantic import BaseModel

    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        if isinstance(value, type) and issubclass(value, BaseModel):
            out[key] = f"<{value.__name__} -> json_schema>"
        else:
            out[key] = value
    return out
