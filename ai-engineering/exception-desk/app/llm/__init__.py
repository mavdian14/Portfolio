"""Provider clients behind one interface, plus the factory that picks one.

Adding a provider means adding a module and one branch in :func:`make_client`. Nothing else
in the service changes — which is the entire argument for this package existing.
"""

from __future__ import annotations

from app.config import Provider, Settings, get_settings
from app.llm.base import (
    BaseClient,
    StructuredResult,
    ToolCallRecord,
    ToolLoopResult,
    Usage,
)
from app.llm.mock import MockClient, mock_error
from app.llm.retry import (
    describe_error,
    is_retryable,
    retry_after_seconds,
    with_retries,
)

__all__ = [
    "BaseClient",
    "MockClient",
    "StructuredResult",
    "ToolCallRecord",
    "ToolLoopResult",
    "Usage",
    "describe_error",
    "is_retryable",
    "make_client",
    "mock_error",
    "retry_after_seconds",
    "with_retries",
]


def make_client(
    provider: Provider | None = None,
    *,
    model: str | None = None,
    settings: Settings | None = None,
) -> BaseClient:
    """Build the client for ``provider`` (defaulting to the configured one).

    Provider SDKs are imported lazily inside each client, so ``LLM_PROVIDER=mock`` works on
    a machine with neither ``anthropic`` nor ``openai`` installed.
    """
    settings = settings or get_settings()
    provider = provider or settings.llm_provider
    model = model or None

    if provider == "mock":
        return MockClient(model=model or "mock", real_provider="anthropic")

    if provider == "anthropic":
        from app.llm.anthropic import AnthropicClient

        if not settings.anthropic_api_key:
            raise RuntimeError(
                "LLM_PROVIDER=anthropic requires ANTHROPIC_API_KEY. "
                "Set it, or run with LLM_PROVIDER=mock."
            )
        return AnthropicClient(
            model=model or settings.anthropic_model,
            api_key=settings.anthropic_api_key,
            timeout=settings.request_timeout_s,
        )

    if provider == "openai":
        from app.llm.openai import OpenAIClient

        if not settings.openai_api_key:
            raise RuntimeError(
                "LLM_PROVIDER=openai requires OPENAI_API_KEY. "
                "Set it, or run with LLM_PROVIDER=mock."
            )
        return OpenAIClient(
            model=model or settings.openai_model,
            api_key=settings.openai_api_key,
            timeout=settings.request_timeout_s,
        )

    if provider == "ollama":
        from app.llm.ollama import OllamaClient

        return OllamaClient(
            model=model or settings.ollama_model,
            base_url=settings.ollama_base_url,
        )

    raise ValueError(f"unknown provider {provider!r}")
