"""The domain layer, with no LLM, no database and no web framework involved."""

from __future__ import annotations

import pytest

from app.domain.inventory import (
    INVENTORY,
    TOOLS,
    cover_weeks,
    first_sku,
    get_lead_time,
    get_sku_status,
    run_tool,
    skus_in_text,
)
from app.domain.prompt_loader import PromptNotFound, available_prompts, load_prompt, render


def test_cover_weeks_floors_at_zero() -> None:
    # CHR-M4K25-RGB: 3 on hand, 12 allocated, 0 in transit -> negative available.
    assert cover_weeks(INVENTORY["CHR-M4K25-RGB"]) == 0.0


def test_cover_weeks_counts_in_transit() -> None:
    # SPR-FILT-GS: (118 - 30 + 50) / 22.0 = 6.27
    assert cover_weeks(INVENTORY["SPR-FILT-GS"]) == 6.27


def test_get_lead_time_reports_slippage() -> None:
    assert get_lead_time("CHR-DHD1075")["slippage_days"] == 43  # 118 observed vs 75 quoted


def test_sku_lookup_raises_on_unknown() -> None:
    with pytest.raises(ValueError, match="unknown SKU"):
        get_sku_status("CHR-NOPE-000")


def test_skus_in_text_is_case_insensitive_and_ordered() -> None:
    text = "the long-throw lens (lns-200-355) and the M 4K25 RGB CHR-M4K25-RGB both slipped"
    assert skus_in_text(text) == ["CHR-M4K25-RGB", "LNS-200-355"]
    assert first_sku(text) == "CHR-M4K25-RGB"


def test_skus_in_text_finds_nothing_in_prose() -> None:
    assert skus_in_text("the supplier has not replied about the chip shortage") == []


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("get_sku_status", {"sku": "CHR-NOPE-000"}),        # domain error
        ("get_sku_status", {}),                              # missing argument
        ("delete_all_inventory", {}),                        # no such tool
        ("flag_exception", {"sku": "CHR-CRWU31", "reason": "x", "severity": "urgent"}),  # bad enum
    ],
)
def test_run_tool_never_raises(name: str, args: dict) -> None:
    """Every failure must come back as data, or the model cannot self-correct."""
    out = run_tool(name, args)
    assert "error" in out
    assert isinstance(out["error"], str) and out["error"]


def test_run_tool_returns_result_envelope_on_success() -> None:
    out = run_tool("get_sku_status", {"sku": "CHR-CRWU31"})
    assert "error" not in out
    assert out["result"]["sku"] == "CHR-CRWU31"


def test_every_tool_declares_a_strict_object_schema() -> None:
    for tool in TOOLS:
        assert tool.input_schema["type"] == "object"
        assert tool.input_schema["additionalProperties"] is False
        assert set(tool.input_schema["required"]) <= set(tool.input_schema["properties"])


def test_prompts_load_and_render() -> None:
    assert "triage_system.v1" in available_prompts()
    assert "inventory control analyst" in load_prompt("triage_system", "v1")
    rendered = render("triage_extract", "v1", message="hello", evidence="(none)")
    assert "hello" in rendered


def test_missing_prompt_names_what_exists() -> None:
    with pytest.raises(PromptNotFound, match="Available:"):
        load_prompt("does_not_exist", "v9")
