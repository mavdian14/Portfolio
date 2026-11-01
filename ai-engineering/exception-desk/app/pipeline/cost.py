"""Cost accounting: tokens to USD, per call and per record.

This is the feature that separates an operated LLM system from a demo. Without it you
cannot answer "what did last month cost", and you cannot safely expose the service publicly.

Prices are stored per million tokens. An unpriced model returns zero *and logs a warning* —
silently reporting a fabricated cost is worse than reporting none.
"""

from __future__ import annotations

import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

MILLION = Decimal(1_000_000)

# (provider, model) -> (usd per 1M input tokens, usd per 1M output tokens)
PRICES: dict[tuple[str, str], tuple[Decimal, Decimal]] = {
    ("anthropic", "claude-sonnet-4-5"): (Decimal("3.00"), Decimal("15.00")),
    ("anthropic", "claude-haiku-4-5"): (Decimal("1.00"), Decimal("5.00")),
    ("anthropic", "claude-opus-5-5"): (Decimal("15.00"), Decimal("75.00")),
    ("openai", "gpt-5.6-terra"): (Decimal("2.50"), Decimal("10.00")),
    ("openai", "gpt-5.4"): (Decimal("1.25"), Decimal("5.00")),
    # A local model costs electricity, not tokens.
    ("ollama", "qwen3:8b"): (Decimal("0"), Decimal("0")),
    # The mock provider makes no network call at all.
    ("mock", "mock"): (Decimal("0"), Decimal("0")),
}

#: Six decimal places, matching the NUMERIC(10, 6) column.
QUANTUM = Decimal("0.000001")


def price_for(provider: str, model: str) -> tuple[Decimal, Decimal] | None:
    """The (input, output) per-million-token price, or None when unpriced."""
    return PRICES.get((provider, model))


def cost_usd(provider: str, model: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Cost of one call, quantised to what the database column can hold."""
    price = price_for(provider, model)
    if price is None:
        logger.warning(
            "no price for provider=%s model=%s; recording cost as 0. "
            "Add it to app.pipeline.cost.PRICES to make the cost report meaningful.",
            provider,
            model,
        )
        return Decimal("0").quantize(QUANTUM)
    per_in, per_out = price
    total = (Decimal(input_tokens) * per_in + Decimal(output_tokens) * per_out) / MILLION
    return total.quantize(QUANTUM)


def is_priced(provider: str, model: str) -> bool:
    """Used by /metrics/cost to state whether the totals are complete."""
    return price_for(provider, model) is not None
