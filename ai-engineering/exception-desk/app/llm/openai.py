"""OpenAI client — Responses API primary, with the Chat Completions variant kept for the
format differences.

Docs
  https://developers.openai.com/api/docs/guides/function-calling
  https://platform.openai.com/docs/guides/structured-outputs
  https://platform.openai.com/docs/guides/error-codes
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
    """SDK-helper path: ``responses.parse(text_format=Model)``.

    The helper kwarg is ``text_format`` here, where Anthropic's is ``output_format``.
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


def raw_schema_kwargs(
    model: str,
    prompt: str,
    json_schema: dict[str, Any],
    *,
    name: str = "payload",
    system: str | None = None,
    max_tokens: int = 1024,
) -> dict[str, Any]:
    """Raw json_schema response format, nested under ``text.format`` with ``strict``."""
    kwargs: dict[str, Any] = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": name,
                "schema": json_schema,
                "strict": True,
            }
        },
        "max_output_tokens": max_tokens,
    }
    if system:
        kwargs["instructions"] = system
    return kwargs


def tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Responses API tool definitions are flat — no nested ``function`` object."""
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


def chat_tool_schema(tools: Sequence[ToolSpec]) -> list[dict[str, Any]]:
    """Chat Completions tool definitions are nested under ``function`` — the classic trap."""
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


def tool_kwargs(
    model: str,
    input_items: list[dict[str, Any]],
    tools: Sequence[ToolSpec],
    *,
    system: str | None = None,
    max_tokens: int = 1024,
    parallel: bool = True,
    previous_response_id: str | None = None,
) -> dict[str, Any]:
    """Responses API tool request. Parallelism is a top-level flag here, not nested."""
    kwargs: dict[str, Any] = {
        "model": model,
        "input": input_items,
        "tools": tool_schema(tools),
        "max_output_tokens": max_tokens,
        "parallel_tool_calls": parallel,
    }
    if system:
        kwargs["instructions"] = system
    if previous_response_id:
        kwargs["previous_response_id"] = previous_response_id
    return kwargs


# --------------------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------------------


class OpenAIClient(BaseClient):
    provider = "openai"

    #: Overridden by :class:`app.llm.ollama.OllamaClient` to point at a local server.
    base_url: str | None = None

    def __init__(
        self,
        model: str | None = None,
        *,
        api_key: str | None = None,
        timeout: float = 60.0,
        max_retries: int = 0,
    ) -> None:
        import openai

        self.model = model or "gpt-5.6-terra"
        client_kwargs: dict[str, Any] = {
            "timeout": timeout,
            "max_retries": max_retries,
        }
        if api_key:
            client_kwargs["api_key"] = api_key
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
            # A local server needs no credential, but the SDK insists on a non-empty one.
            client_kwargs.setdefault("api_key", "not-needed")
        self.client = openai.OpenAI(**client_kwargs)
        self.async_client = openai.AsyncOpenAI(**client_kwargs)

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
        resp, retries = with_retries(lambda: self.client.responses.parse(**kwargs))
        return StructuredResult(
            parsed=resp.output_parsed,
            raw_text=resp.output_text or "",
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
            self.model, prompt, json_schema, name=name, system=system, max_tokens=max_tokens
        )
        started = time.perf_counter()
        resp, retries = with_retries(lambda: self.client.responses.create(**kwargs))
        text = resp.output_text or ""
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
        input_items: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        previous_response_id: str | None = None
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = tool_kwargs(
                self.model,
                input_items,
                tools,
                system=system,
                max_tokens=budget,
                parallel=parallel,
                previous_response_id=previous_response_id,
            )
            started = time.perf_counter()
            resp, _ = with_retries(lambda kw=kwargs: self.client.responses.create(**kw))
            result.usage.add(
                usage_from(resp, self.provider, self.model, time.perf_counter() - started)
            )
            result.rounds = round_no

            # OpenAI signals truncation through status + incomplete_details, not stop_reason.
            incomplete = getattr(resp, "incomplete_details", None)
            if (
                getattr(resp, "status", "") == "incomplete"
                and getattr(incomplete, "reason", "") == "max_output_tokens"
            ):
                budget = min(budget * 2, 8192)
                result.transcript.append(
                    f"round {round_no}: incomplete (max_output_tokens) -> retry with {budget}"
                )
                continue

            calls = [item for item in resp.output if getattr(item, "type", "") == "function_call"]
            if calls:
                outputs = []
                for call in calls:
                    # Tool arguments arrive as a JSON *string*, unlike Anthropic's parsed dict.
                    try:
                        arguments = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                    out = run_tool(call.name, arguments)
                    result.tool_calls.append(
                        ToolCallRecord(
                            name=call.name,
                            arguments=arguments,
                            result=out,
                            round=round_no,
                            call_id=call.call_id,
                        )
                    )
                    if verbose:
                        result.transcript.append(
                            f"round {round_no}: {call.name}({json.dumps(arguments)}) -> "
                            f"{'ERROR ' if 'error' in out else ''}{json.dumps(out)[:200]}"
                        )
                    outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": json.dumps(out),
                        }
                    )
                # Only the new items — the server keeps the prior turn via the id below.
                input_items = outputs
                previous_response_id = resp.id
                continue

            result.final_text = resp.output_text or ""
            result.stop_reason = getattr(resp, "status", "") or ""
            break

        return result

    def tool_loop_chat_completions(
        self,
        prompt: str,
        *,
        tools: Sequence[ToolSpec] | None = None,
        system: str | None = None,
        max_rounds: int = 6,
        max_tokens: int = 1024,
    ) -> ToolLoopResult:
        """The same loop on Chat Completions: nested tool defs, ``role='tool'``, full history."""
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))

        for round_no in range(1, max_rounds + 1):
            started = time.perf_counter()
            resp, _ = with_retries(
                # The SDK's param unions are stricter than these plain dicts; the shapes
                # are exactly what the API expects (verified against the docs).
                lambda: self.client.chat.completions.create(  # type: ignore[arg-type]
                    model=self.model,
                    messages=messages,
                    tools=chat_tool_schema(tools),
                    max_completion_tokens=max_tokens,
                )
            )
            result.usage.add(
                usage_from(resp, self.provider, self.model, time.perf_counter() - started)
            )
            result.rounds = round_no
            message = resp.choices[0].message
            if message.tool_calls:
                messages.append(message.model_dump(exclude_none=True))
                for call in message.tool_calls:
                    try:
                        arguments = json.loads(call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        arguments = {}
                    out = run_tool(call.function.name, arguments)
                    result.tool_calls.append(
                        ToolCallRecord(
                            call.function.name, arguments, out, round_no, call.id or ""
                        )
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(out),
                        }
                    )
                continue
            result.final_text = message.content or ""
            result.stop_reason = resp.choices[0].finish_reason or ""
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
            "input": [{"role": "user", "content": prompt}],
            "max_output_tokens": max_tokens,
        }
        if system:
            kwargs["instructions"] = system
        chunks: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    chunks.append(delta)
                    if on_delta:
                        on_delta(delta)
                elif event.type == "response.refusal.delta":
                    # A refusal is a legitimate outcome, not an error.
                    chunks.append(f"[refusal] {getattr(event, 'delta', '')}")
                elif event.type == "response.error":
                    raise RuntimeError(f"stream error event: {getattr(event, 'error', None)}")
            final = stream.get_final_response()
        return final.output_text or "".join(chunks)

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
            "input": [{"role": "user", "content": prompt}],
            "max_output_tokens": max_tokens,
        }
        if mode == "tools":
            kwargs["tools"] = tool_schema(TOOLS)
        if system:
            kwargs["instructions"] = system
        seen: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                etype = getattr(event, "type", "unknown")
                detail = ""
                if etype == "response.output_text.delta":
                    detail = f" delta={getattr(event, 'delta', '')!r}"
                elif etype == "response.function_call_arguments.delta":
                    detail = (
                        f" name={getattr(event, 'name', '')} "
                        f"delta={getattr(event, 'delta', '')!r}"
                    )
                elif etype == "response.function_call_arguments.done":
                    detail = (
                        f" name={getattr(event, 'name', '')} "
                        f"arguments={getattr(event, 'arguments', '')!r}"
                    )
                elif etype == "response.error":
                    detail = f" error={getattr(event, 'error', None)}"
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
        chunks: list[str] = []
        with self.client.responses.stream(**kwargs) as stream:
            for event in stream:
                if event.type == "response.output_text.delta":
                    chunks.append(getattr(event, "delta", ""))
                elif event.type == "response.refusal.delta":
                    chunks.append(f"[refusal] {getattr(event, 'delta', '')}")
                elif event.type == "response.error":
                    raise RuntimeError(f"stream error event: {getattr(event, 'error', None)}")
            final = stream.get_final_response()
        return StructuredResult(
            parsed=final.output_parsed,
            raw_text="".join(chunks),
            usage=usage_from(final, self.provider, self.model, 0.0),
            payload=_printable(kwargs),
        )

    def stream_chat_tool_arguments(
        self, prompt: str, *, tools: Sequence[ToolSpec] | None = None,
        system: str | None = None, max_tokens: int = 512,
    ) -> dict[int, dict[str, str]]:
        """Chat Completions streams tool arguments as fragments — accumulate per index.

        Fragments for several parallel calls are interleaved, so ``tc.index`` is the
        discriminator. Never ``json.loads`` a fragment; parse on the done event.
        """
        tools = list(tools or TOOLS)
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        assembled: dict[int, dict[str, str]] = {}
        stream = self.client.chat.completions.create(  # type: ignore[arg-type]
            model=self.model,
            messages=messages,
            tools=chat_tool_schema(tools),
            max_completion_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            for tc in delta.tool_calls or []:
                entry = assembled.setdefault(tc.index, {"name": "", "arguments": ""})
                if tc.function and tc.function.name:
                    entry["name"] = tc.function.name
                if tc.function and tc.function.arguments:
                    entry["arguments"] += tc.function.arguments
        return assembled

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
        resp, retries = await awith_retries(lambda: self.async_client.responses.parse(**kwargs))
        return StructuredResult(
            parsed=resp.output_parsed,
            raw_text=resp.output_text or "",
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
        input_items: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
        previous_response_id: str | None = None
        result = ToolLoopResult(final_text="", usage=Usage(self.provider, self.model))
        budget = max_tokens

        for round_no in range(1, max_rounds + 1):
            kwargs = tool_kwargs(
                self.model,
                input_items,
                tools,
                system=system,
                max_tokens=budget,
                parallel=parallel,
                previous_response_id=previous_response_id,
            )
            started = time.perf_counter()
            resp, _ = await awith_retries(
                lambda kw=kwargs: self.async_client.responses.create(**kw)
            )
            result.usage.add(
                usage_from(resp, self.provider, self.model, time.perf_counter() - started)
            )
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
                    result.tool_calls.append(
                        ToolCallRecord(call.name, arguments, out, round_no, call.call_id)
                    )
                    outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": json.dumps(out),
                        }
                    )
                input_items = outputs
                previous_response_id = resp.id
                continue
            result.final_text = resp.output_text or ""
            result.stop_reason = getattr(resp, "status", "") or ""
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
            "input": [{"role": "user", "content": prompt}],
            "max_output_tokens": max_tokens,
        }
        if system:
            kwargs["instructions"] = system
        chunks: list[str] = []
        async with self.async_client.responses.stream(**kwargs) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    delta = getattr(event, "delta", "")
                    chunks.append(delta)
                    if on_delta:
                        on_delta(delta)
            final = await stream.get_final_response()
        return final.output_text or "".join(chunks)

    def list_models(self, limit: int = 60) -> list[str]:
        return sorted(m.id for m in self.client.models.list().data)[:limit]


def _printable(kwargs: dict[str, Any]) -> dict[str, Any]:
    """A copy of a payload with any pydantic class replaced by a placeholder."""
    from pydantic import BaseModel

    out: dict[str, Any] = {}
    for key, value in kwargs.items():
        if isinstance(value, type) and issubclass(value, BaseModel):
            out[key] = f"<{value.__name__} -> json_schema>"
        else:
            out[key] = value
    return out
