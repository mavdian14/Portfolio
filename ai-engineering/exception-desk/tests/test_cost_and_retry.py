"""Cost arithmetic and the retry policy."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.llm import mock_error
from app.llm.retry import (
    describe_error,
    is_retryable,
    retry_after_seconds,
    with_retries,
)
from app.pipeline.cost import cost_usd, is_priced


def test_cost_is_per_million_tokens() -> None:
    # claude-sonnet-4-5: $3 / 1M in, $15 / 1M out
    assert cost_usd("anthropic", "claude-sonnet-4-5", 1_000_000, 0) == Decimal("3.000000")
    assert cost_usd("anthropic", "claude-sonnet-4-5", 0, 1_000_000) == Decimal("15.000000")


def test_cost_quantises_to_the_column_width() -> None:
    value = cost_usd("anthropic", "claude-sonnet-4-5", 412, 88)
    assert value == Decimal("0.002556")  # 412*3 + 88*15 = 2556 / 1e6
    assert -value.as_tuple().exponent <= 6


def test_mock_and_local_calls_are_free() -> None:
    assert cost_usd("mock", "mock", 10_000, 10_000) == Decimal("0")
    assert cost_usd("ollama", "qwen3:8b", 10_000, 10_000) == Decimal("0")


def test_unpriced_model_reports_zero_and_says_so() -> None:
    assert not is_priced("anthropic", "claude-not-a-real-model")
    assert cost_usd("anthropic", "claude-not-a-real-model", 1_000_000, 1_000_000) == Decimal("0")


@pytest.mark.parametrize(
    ("name", "status", "expected"),
    [
        ("RateLimitError", 429, True),
        ("OverloadedError", 529, True),
        ("InternalServerError", 503, True),
        ("APIConnectionError", None, True),
        ("APITimeoutError", None, True),
        ("AuthenticationError", 401, False),
        ("NotFoundError", 404, False),
        ("BadRequestError", 400, False),
    ],
)
def test_retryable_classification(name: str, status: int | None, expected: bool) -> None:
    assert is_retryable(mock_error(name, "x", status)) is expected


def test_retry_after_is_read_from_headers() -> None:
    assert retry_after_seconds(mock_error("RateLimitError", "x", 429, retry_after=2.5)) == 2.5
    assert retry_after_seconds(mock_error("RateLimitError", "x", 429)) is None


def test_with_retries_retries_then_succeeds() -> None:
    attempts: list[tuple[int, str, float]] = []
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise mock_error("RateLimitError", "slow down", 429, retry_after=0.01)
        return "ok"

    value, retries = with_retries(
        flaky, attempts=4, base_delay=0.01,
        on_retry=lambda a, e, d: attempts.append((a, type(e).__name__, d)),
    )
    assert value == "ok"
    assert retries == 2
    assert [a for a, _, _ in attempts] == [1, 2]
    # Retry-After must win over the exponential curve.
    assert all(delay == pytest.approx(0.01, abs=1e-6) for _, _, delay in attempts)


def test_non_retryable_surfaces_immediately() -> None:
    calls = {"n": 0}

    def bad() -> None:
        calls["n"] += 1
        raise mock_error("BadRequestError", "max_tokens must be positive", 400)

    with pytest.raises(Exception) as exc:
        with_retries(bad, attempts=4, base_delay=0.01)
    assert calls["n"] == 1, "a 400 must not be retried"
    assert "status=400" in describe_error(exc.value)
