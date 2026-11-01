"""Mock provider fidelity.

A mock that quietly disagrees with reality is worse than no mock: it manufactures false
confidence. These tests pin the properties the service relies on.
"""

from __future__ import annotations

import pytest

from app.domain.inventory import INVENTORY, cover_weeks
from app.domain.models import InventoryException
from app.domain.prompt_loader import render
from app.llm import make_client, mock_error
from app.llm.mock import MockClient, message_from_prompt, mock_parse
from app.llm.retry import describe_error, is_retryable


@pytest.fixture
def mock() -> MockClient:
    return MockClient()


def test_usage_is_not_zero(mock: MockClient) -> None:
    """`calls=3, tokens=0` is worse than no usage table at all."""
    loop = mock.tool_loop("Position check for CHR-M4K25-RGB")
    assert loop.usage.calls >= 1
    assert loop.usage.input_tokens > 0
    assert loop.usage.output_tokens > 0


def test_tool_loop_executes_the_real_handlers(mock: MockClient) -> None:
    loop = mock.tool_loop("Check CHR-M4K25-RGB")
    tools_called = {c.name for c in loop.tool_calls}
    assert {"get_sku_status", "get_lead_time", "query_open_positions"} <= tools_called
    # The result is the real domain output, not a canned string.
    status = next(c for c in loop.tool_calls if c.name == "get_sku_status")
    assert status.result["result"]["on_hand"] == INVENTORY["CHR-M4K25-RGB"]["on_hand"]


def test_extraction_agrees_with_the_inventory_record(mock: MockClient) -> None:
    """The record the mock produces must match the evidence it gathered."""
    result = mock.structured("Triage CHR-DHD1075", InventoryException)
    parsed: InventoryException = result.parsed
    rec = INVENTORY["CHR-DHD1075"]
    assert parsed.sku == "CHR-DHD1075"
    assert parsed.lead_time_impact_days == rec["actual_lt_p90_days"] - rec["quoted_lt_days"]
    assert parsed.weeks_of_cover == cover_weeks(rec)


def test_no_sku_in_text_produces_an_error_evidence_row(mock: MockClient) -> None:
    """A message naming no SKU must show a failed lookup, not a silent invention."""
    loop = mock.tool_loop("the supplier has not replied about anything")
    assert loop.tool_calls and loop.tool_calls[0].failed


def test_no_sku_extraction_is_low_confidence(mock: MockClient) -> None:
    parsed = mock.structured("no part numbers here at all", InventoryException).parsed
    assert parsed.sku == "UNKNOWN"
    assert parsed.confidence < 0.5


def test_extraction_is_deterministic(mock: MockClient) -> None:
    a = mock.structured("Check LNS-200-355", InventoryException).parsed
    b = mock.structured("Check LNS-200-355", InventoryException).parsed
    assert a == b


def test_mock_error_carries_the_real_class_name() -> None:
    exc = mock_error("RateLimitError", "slow down", 429, retry_after=1.5)
    assert type(exc).__name__ == "RateLimitError"
    assert is_retryable(exc)
    assert "status=429" in describe_error(exc)


def test_fail_first_n_calls_is_a_real_retry_surface() -> None:
    client = MockClient(fail_first_n_calls=1)
    with pytest.raises(Exception) as first:
        client.structured("x", InventoryException)
    assert is_retryable(first.value)
    # The budget is spent, so the second call succeeds.
    assert client.structured("x", InventoryException).parsed is not None


def test_make_client_returns_the_mock_offline() -> None:
    assert isinstance(make_client("mock"), MockClient)


def test_transport_errors_have_no_http_status() -> None:
    exc = mock_error("APIConnectionError", "reset by peer", None)
    assert exc.status_code is None
    assert is_retryable(exc)  # retryable by class name, not by status


def test_message_is_sliced_out_of_the_prompt_scaffolding() -> None:
    prompt = render("triage_extract", "v1", message="CHR-M4K25-RGB slipped", evidence="(none)")
    assert message_from_prompt(prompt).strip() == "CHR-M4K25-RGB slipped"


def test_intent_is_read_from_the_message_not_the_scaffolding() -> None:
    """Regression: the extract template contains "low when no action is needed".

    Matching intent keywords against the whole prompt let the *instructions* masquerade as
    the message, so every record classified as root_cause='none'.
    """
    prompt = render(
        "triage_extract", "v1", message="CHR-M4K25-RGB slipped 23 days", evidence="(none)"
    )
    assert "no action" in prompt.lower(), "the trap this test guards against has moved"
    assert mock_parse(InventoryException, prompt).root_cause == "supplier_delay"


def test_a_genuinely_quiet_message_still_classifies_as_no_action() -> None:
    """The fix must not break the case the keyword was there for.

    The message names its SKU, so the verdict comes from the message rather than from the
    "unknown SKU" fallback.
    """
    note = "CHR-GS25-HS units look fine. No action needed, flagging only for a status pass."
    prompt = render("triage_extract", "v1", message=note, evidence="(none)")
    parsed = mock_parse(InventoryException, prompt)
    assert parsed.root_cause == "none"
    assert parsed.severity == "low"


def test_no_sku_message_that_needs_nothing_reports_no_action() -> None:
    """Regression: a status-pass message with no SKU code came back as severity=medium,
    root_cause=data_quality — reporting a data problem that was not one."""
    note = (
        "GS Series high-security units look fine — 41 on hand, 18 allocated, 20 in transit. "
        "No action needed, flagging only because the region planner asked for a status pass."
    )
    prompt = render("triage_extract", "v1", message=note, evidence="(none)")
    parsed = mock_parse(InventoryException, prompt)
    assert parsed.sku == "UNKNOWN"
    assert parsed.root_cause == "none"
    assert parsed.severity == "low"


def test_no_sku_message_that_needs_something_still_reports_a_data_problem() -> None:
    note = "Requesting a forecast update for Q1 to reserve capacity."
    prompt = render("triage_extract", "v1", message=note, evidence="(none)")
    parsed = mock_parse(InventoryException, prompt)
    assert parsed.root_cause == "data_quality"
    assert parsed.confidence < 0.5


def test_multi_segment_sku_codes_normalise_fully() -> None:
    """Regression: a generic `(chr|lns)-([a-z0-9]+)` rule only reaches the first segment."""
    from app.domain.inventory import normalise

    assert normalise("check chr-m4k25-rgb now") == "check CHR-M4K25-RGB now"
    assert normalise("the spr-lamp-crw module") == "the SPR-LAMP-CRW module"
    assert normalise("lns-200-355 slipped") == "LNS-200-355 slipped"
