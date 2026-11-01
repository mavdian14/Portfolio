"""Local provider via Ollama's OpenAI-compatible endpoint.

The fallback that keeps the service runnable with no API key and no spend: the same code
path, a model on localhost. It is the reason the provider abstraction earns its keep — this
module is the only file that had to be written to add a third vendor.

Ollama's ``/v1`` endpoint covers Chat Completions only. The Responses API calls that
:class:`~app.llm.openai.OpenAIClient` uses for structured output and tool calling are
overridden here to the Chat Completions equivalents.
"""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from typing import Any

from app.domain.inventory import TOOLS, ToolSpec
from app.llm.base import ModelT, StructuredResult, ToolLoopResult, usage_from
from app.llm.openai import OpenAIClient, chat_tool_schema
from app.llm.retry import with_retries


class OllamaClient(OpenAIClient):
    provider = "ollama"

    def __init__(
        self,
        model: str | None = None,
        *,
        base_url: str = "http://localhost:11434/v1",
        timeout: float = 120.0,
        max_retries: int = 0,
    ) -> None:
        self.base_url = base_url
        # Local models are slower than hosted ones; the default timeout is deliberately
        # longer than the hosted clients'.
        super().__init__(
            model or "qwen3:8b",
            api_key="not-needed",
            timeout=timeout,
            max_retries=max_retries,
        )

    def structured(
        self,
        prompt: str,
        schema: type[ModelT],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> StructuredResult:
        """Structured output via Chat Completions ``response_format``."""
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        json_schema = schema.model_json_schema()
        started = time.perf_counter()
        resp, retries = with_retries(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": schema.__name__, "schema": json_schema},
                },
                max_completion_tokens=max_tokens,
            )
        )
        text = resp.choices[0].message.content or ""
        return StructuredResult(
            parsed=schema.model_validate_json(text) if text else None,
            raw_text=text,
            usage=usage_from(resp, self.provider, self.model, time.perf_counter() - started),
            payload={"model": self.model, "response_format": "json_schema", "messages": messages},
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
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        started = time.perf_counter()
        resp, retries = with_retries(
            lambda: self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                response_format={
                    "type": "json_schema",
                    "json_schema": {"name": name, "schema": json_schema},
                },
                max_completion_tokens=max_tokens,
            )
        )
        text = resp.choices[0].message.content or ""
        return StructuredResult(
            parsed=json.loads(text) if text else None,
            raw_text=text,
            usage=usage_from(resp, self.provider, self.model, time.perf_counter() - started),
            payload={"model": self.model, "response_format": "json_schema"},
            retries=retries,
        )

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
        """Chat Completions is the only tool-calling surface Ollama exposes."""
        return self.tool_loop_chat_completions(
            prompt,
            tools=tools or TOOLS,
            system=system,
            max_rounds=max_rounds,
            max_tokens=max_tokens,
        )

    def list_models(self, limit: int = 40) -> list[str]:
        return sorted(m.id for m in self.client.models.list().data)[:limit]


__all__ = ["OllamaClient", "chat_tool_schema"]
