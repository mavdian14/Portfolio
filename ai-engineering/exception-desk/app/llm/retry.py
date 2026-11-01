"""Retry policy: which failures to retry, how long to wait, and when to give up.

Promoted from ``practice/ai-foundations/llm_client.py``.

The SDKs retry twice by default, which is usually right in production and useless when the
retry behaviour is the thing you need to reason about. Every client here is constructed
with ``max_retries=0`` so this module owns the policy explicitly.

See https://platform.claude.com/docs/en/api/errors and
https://platform.openai.com/docs/guides/error-codes
"""

from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Callable
from typing import Any

# Matched on class name because the two SDKs use unrelated hierarchies, and on status
# code because that is what the HTTP layer actually told you. Belt and braces.
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

# Never retried: a retry burns budget and hides the bug.
FATAL_STATUS = {400, 401, 403, 404, 422}


def describe_error(exc: BaseException) -> str:
    """One-line human-readable form that works for both SDKs and for the mock."""
    name = type(exc).__name__
    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    msg = getattr(exc, "message", None) or str(exc)
    bits = [name]
    if status:
        bits.append(f"status={status}")
    return f"{' | '.join(bits)}: {msg}"


def is_retryable(exc: BaseException) -> bool:
    """True when retrying has a real chance of succeeding."""
    name = type(exc).__name__
    status = getattr(exc, "status_code", None) or getattr(
        getattr(exc, "response", None), "status_code", None
    )
    if name in RETRYABLE_NAMES:
        return True
    return bool(status) and int(status) in RETRYABLE_STATUS


def retry_after_seconds(exc: BaseException) -> float | None:
    """Read Retry-After / retry-after-ms from the response headers, if present.

    The server's number beats our exponential guess — always prefer it.
    """
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


def _delay_for(attempt: int, exc: BaseException, base_delay: float, max_delay: float) -> float:
    """Exponential backoff with full jitter, unless the server specified a delay.

    Full jitter (`uniform(0, delay)` rather than `delay`) matters more than it looks: a
    thousand clients that all failed at the same instant will otherwise all retry at the
    same instant and re-break the server.
    """
    server_delay = retry_after_seconds(exc)
    if server_delay is not None:
        return min(server_delay, max_delay)
    ceiling = min(max_delay, base_delay * (2 ** (attempt - 1)))
    return random.uniform(0, ceiling)


def with_retries(
    fn: Callable[[], Any],
    *,
    attempts: int = 4,
    base_delay: float = 0.8,
    max_delay: float = 8.0,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> tuple[Any, int]:
    """Call ``fn()``, retrying retryable failures. Returns ``(value, retries_used)``."""
    last: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn(), attempt - 1
        except BaseException as exc:  # noqa: BLE001 - re-raised below when not retryable
            last = exc
            if not is_retryable(exc) or attempt == attempts:
                raise
            delay = _delay_for(attempt, exc, base_delay, max_delay)
            if on_retry:
                on_retry(attempt, exc, delay)
            time.sleep(delay)
    # Unreachable: the loop returns on success or re-raises on the final attempt.
    if last is not None:  # pragma: no cover
        raise last
    raise RuntimeError("with_retries called with attempts < 1")  # pragma: no cover


async def awith_retries(
    fn: Callable[[], Any],
    *,
    attempts: int = 4,
    base_delay: float = 0.8,
    max_delay: float = 8.0,
    on_retry: Callable[[int, BaseException, float], None] | None = None,
) -> tuple[Any, int]:
    """Async twin of :func:`with_retries`. Identical policy, non-blocking sleep."""
    last: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await fn(), attempt - 1
        except BaseException as exc:  # noqa: BLE001
            last = exc
            if not is_retryable(exc) or attempt == attempts:
                raise
            delay = _delay_for(attempt, exc, base_delay, max_delay)
            if on_retry:
                on_retry(attempt, exc, delay)
            await asyncio.sleep(delay)
    if last is not None:  # pragma: no cover
        raise last
    raise RuntimeError("awith_retries called with attempts < 1")  # pragma: no cover
