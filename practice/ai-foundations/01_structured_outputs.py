#!/usr/bin/env python3
"""
01 — Structured outputs: one pydantic model, two providers.

Covers, for the Anthropic Messages API and the OpenAI Responses API:
  1. pydantic -> JSON schema, and the strict-mode transform the SDKs apply for you
  2. SDK helper path            (messages.parse(output_format=Model) / responses.parse(text_format=Model))
  3. raw JSON-schema path       (output_config.format            / text.format)
  4. batch extraction into a list-of-models
  5. validation + repair when an answer arrives off-schema
  6. async fan-out with asyncio.gather
  7. side-by-side comparison table

Docs
  https://platform.claude.com/docs/en/build-with-claude/structured-outputs
  https://platform.openai.com/docs/guides/structured-outputs

Run
  python3 01_structured_outputs.py                 # offline dry-run
  python3 01_structured_outputs.py --live          # real API calls (keys required)
  python3 01_structured_outputs.py --provider openai --json
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from cli_common import (
    build_parser,
    emit_json,
    header,
    json_block,
    kv,
    note,
    resolve_clients,
    schema_field_rows,
    section,
    table,
    to_strict_schema,
)
from inventory import EXCEPTION_NOTES, SUPPLIER_MESSAGES, ExceptionTriageBatch, InventoryException
from llm_client import BaseClient, StructuredResult


class PlanLine(BaseModel):
    """One purchase-order line inside a reorder plan (nested -> travels as $defs/$ref)."""

    po_number: str = Field(description="Purchase order the line belongs to, e.g. PO-88411")
    quantity: int = Field(description="Units to order on this line")
    supplier_note: str | None = Field(default=None, description="Free-text note for the buyer")


class ReorderPlan(BaseModel):
    """A schema with optional and nested fields, to show what strict mode does to them."""

    sku: str = Field(description="SKU the plan covers")
    expedite: bool = Field(default=False, description="Pay for expedited freight")
    eta_days: int | None = Field(default=None, description="Expected days to receipt, if known")
    lines: list[PlanLine] = Field(default_factory=list, description="Order lines to raise")

NOTE = EXCEPTION_NOTES[0]          # the M 4K25 RGB note: shortage + lead-time slippage + escalation
DEMAND_NOTE = EXCEPTION_NOTES[1]   # the long-throw lens note: demand spike

# A deliberately off-schema answer, used to exercise the repair loop in dry-run mode.
OFF_SCHEMA_SAMPLE: dict[str, Any] = {
    "sku": "chr-m4k25-rgb",           # wrong case
    "severity": "urgent",             # not in the Literal set
    "root_cause": "supplier delay",   # not in the Literal set
    "weeks_of_cover": "0.7",          # string instead of float
    "lead_time_impact_days": 23,
    "recommended_action": "Expedite PO-88411",
    "requires_escalation": "yes",     # string instead of bool
    "confidence": 1.4,                # outside the documented 0.0-1.0 range
    "extra_field": "invented by the model",
}


def show_schema_path() -> dict[str, Any]:
    section("1", "pydantic -> JSON schema: what the model actually receives")
    raw = InventoryException.model_json_schema()
    strict = to_strict_schema(raw)

    print("  fields (from the raw pydantic schema):")
    table(["field", "type", "required", "constraint"], schema_field_rows(raw))

    raw_required = len(raw.get("required", []))
    strict_required = len(strict.get("required", []))
    kv([
        ("raw required fields", f"{raw_required} of {len(raw.get('properties', {}))}"),
        ("strict required fields", f"{strict_required} of {len(strict.get('properties', {}))}"),
        ("raw additionalProperties", raw.get("additionalProperties", "<unset>")),
        ("strict additionalProperties", strict.get("additionalProperties")),
    ])
    note("every field here is required in both views, so this schema alone cannot show what the "
         "transform does. A schema with optional and nested fields can:")

    nested_raw = ReorderPlan.model_json_schema()
    nested_strict = to_strict_schema(nested_raw)
    print("\n  ReorderPlan — raw (what pydantic emits):")
    table(["field", "type", "required", "constraint"], schema_field_rows(nested_raw), indent=4)
    print("\n  ReorderPlan — strict (what the model is actually constrained to):")
    table(["field", "type", "required", "constraint"], schema_field_rows(nested_strict), indent=4)
    kv([
        ("raw required", nested_raw.get("required")),
        ("strict required", nested_strict.get("required")),
        ("$defs (nested models)", list(nested_raw.get("$defs", {})) or "none"),
        ("$refs used by the schema",
         [v.get("$ref") for v in nested_strict.get("properties", {}).values() if "$ref" in v]
         or "none"),
    ], indent=4)
    note("three things changed: additionalProperties became false, `required` grew to every "
         "property, and the two optional fields (expedite, eta_days) turned into nullable types "
         "instead of disappearing from `required`. Their `default` keys were dropped too — a "
         "required field with a default contradicts itself.")
    note("nested models do not get inlined: they stay in $defs and are referenced by $ref, so an "
         "unresolved $ref is the usual reason a hand-written schema is rejected.")
    return {"raw": raw, "strict": strict, "nested_raw": nested_raw, "nested_strict": nested_strict}


def run_helper_path(clients: dict[str, BaseClient]) -> list[dict[str, Any]]:
    section("2", "SDK helper path: messages.parse() / responses.parse()")
    rows = []
    for provider, client in clients.items():
        result: StructuredResult = client.structured(NOTE, InventoryException)
        parsed = result.parsed
        print(f"\n  [{provider}] {result.usage}")
        kv([
            ("sku", parsed.sku),
            ("severity", parsed.severity),
            ("root_cause", parsed.root_cause),
            ("weeks_of_cover", parsed.weeks_of_cover),
            ("lead_time_impact_days", parsed.lead_time_impact_days),
            ("requires_escalation", parsed.requires_escalation),
            ("confidence", parsed.confidence),
            ("action", parsed.recommended_action),
        ], indent=4)
        print("    payload sent:")
        json_block({k: v for k, v in result.payload.items()}, indent=6, max_lines=14)
        rows.append({"provider": provider, "path": "helper (parse)", "model": result.usage.model,
                     "calls": result.usage.calls, "in": result.usage.input_tokens,
                     "out": result.usage.output_tokens, "retries": result.retries})
    return rows


def run_raw_path(clients: dict[str, BaseClient], schemas: dict[str, Any]) -> list[dict[str, Any]]:
    section("3", "raw JSON-schema path: output_config.format / text.format")
    note("same schema, no SDK convenience wrapper: you own the schema, the strict flags and the "
         "json.loads on the way back. This is the path that works when your schema comes from a "
         "contract, a database or another service rather than a pydantic class.")
    rows = []
    for provider, client in clients.items():
        result = client.structured_raw(DEMAND_NOTE, schemas["strict"], name="demand_signal")
        print(f"\n  [{provider}] {result.usage}")
        kv([(k, v) for k, v in (result.parsed or {}).items()], indent=4)
        print("    payload keys sent:", ", ".join(sorted(result.payload)))
        rows.append({"provider": provider, "path": "raw json_schema", "model": result.usage.model,
                     "calls": result.usage.calls, "in": result.usage.input_tokens,
                     "out": result.usage.output_tokens, "retries": result.retries})
    return rows


def run_batch_path(clients: dict[str, BaseClient]) -> list[dict[str, Any]]:
    section("4", "batch extraction: many notes, one list-of-models")
    note("the supplier inbox is the realistic case — one call, one decision per message, order "
         "preserved. Watch for the model returning fewer items than inputs; that is why the "
         "prompt states the count explicitly.")
    prompt = (
        f"Classify each of the {len(SUPPLIER_MESSAGES)} supplier messages below. "
        "Return exactly one triage item per message, in the same order.\n\n"
        + "\n\n".join(f"[{i + 1}] {msg}" for i, msg in enumerate(SUPPLIER_MESSAGES))
    )
    rows = []
    for provider, client in clients.items():
        result = client.structured(prompt, ExceptionTriageBatch)
        items = result.parsed.items
        print(f"\n  [{provider}] {result.usage} — returned {len(items)} of {len(SUPPLIER_MESSAGES)}")
        table(["#", "sku", "category", "priority", "human?", "summary"],
              [[i + 1, it.sku, it.category, it.priority, it.requires_human, it.one_line_summary]
               for i, it in enumerate(items)])
        rows.append({"provider": provider, "path": "helper (batch)", "model": result.usage.model,
                     "calls": result.usage.calls, "in": result.usage.input_tokens,
                     "out": result.usage.output_tokens, "retries": result.retries,
                     "items_returned": len(items), "items_expected": len(SUPPLIER_MESSAGES)})
    return rows


def structured_with_repair(client: BaseClient, prompt: str, schema: type, *,
                           inject: dict[str, Any] | None = None, max_attempts: int = 3):
    """Validate, and on failure re-ask with the validation error appended to the prompt."""
    log: list[str] = []
    current = prompt
    for attempt in range(1, max_attempts + 1):
        if attempt == 1 and inject is not None:
            candidate = inject
            log.append(f"attempt {attempt}: (simulated) model answered off-schema")
        else:
            result = client.structured(current, schema)
            candidate = result.parsed
            log.append(f"attempt {attempt}: model answered, validating")
        try:
            return schema.model_validate(candidate), attempt, log
        except ValidationError as exc:
            first = exc.errors()[0]
            log.append(f"attempt {attempt}: REJECTED — {'.'.join(str(p) for p in first['loc'])}: {first['msg']}")
            current = (
                f"{prompt}\n\nYour previous response was rejected by schema validation:\n{exc}\n"
                "Return a corrected object that satisfies the schema exactly."
            )
    raise RuntimeError("repair loop exhausted")


def run_repair_path(clients: dict[str, BaseClient], dry_run: bool) -> dict[str, Any]:
    section("5", "when an answer arrives off-schema: validate, then repair")
    print("  an off-schema payload, validated directly:")
    try:
        InventoryException.model_validate(OFF_SCHEMA_SAMPLE)
        print("    unexpectedly valid")
    except ValidationError as exc:
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            print(f"    - {loc}: {err['msg']} (got {err.get('input')!r})")
    note("pydantic coerces \"0.7\" -> 0.7 and \"yes\" -> True, but it will not invent an enum "
         "member: 'urgent' and 'supplier delay' are hard failures. That is the difference "
         "between a type system and a suggestion.")

    summary: dict[str, Any] = {}
    for provider, client in clients.items():
        parsed, attempts, log = structured_with_repair(
            client, NOTE, InventoryException, inject=OFF_SCHEMA_SAMPLE if dry_run else None
        )
        print(f"\n  [{provider}] repair loop:")
        for line in log:
            print(f"    {line}")
        print(f"    -> severity={parsed.severity!r} root_cause={parsed.root_cause!r} "
              f"attempts={attempts}")
        summary[provider] = {"attempts": attempts, "final_severity": parsed.severity}
    note("with strict structured outputs the first answer is normally valid, so this loop is "
         "cheap insurance rather than the main path — keep it for raw-schema and non-strict calls.")
    return summary


async def _fan_out(clients: dict[str, BaseClient], notes: list[str]) -> dict[str, list[Any]]:
    tasks: dict[str, list[Any]] = {}
    for provider, client in clients.items():
        tasks[provider] = [asyncio.create_task(client.astructured(n, InventoryException)) for n in notes]
    out: dict[str, list[Any]] = {}
    for provider, provider_tasks in tasks.items():
        out[provider] = [await task for task in provider_tasks]
    return out


def run_async_path(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("6", "concurrency: asyncio.gather over the note backlog")
    notes = EXCEPTION_NOTES
    timings: dict[str, Any] = {}

    for provider, client in clients.items():
        t0 = time.perf_counter()
        seq = [client.structured(n, InventoryException) for n in notes]
        seq_elapsed = time.perf_counter() - t0

        t0 = time.perf_counter()
        results = asyncio.run(_fan_out({provider: client}, notes))[provider]
        par_elapsed = time.perf_counter() - t0

        print(f"\n  [{provider}] {len(notes)} notes")
        kv([
            ("sequential", f"{seq_elapsed * 1000:.1f} ms"),
            ("concurrent", f"{par_elapsed * 1000:.1f} ms"),
            ("severities", ", ".join(r.parsed.severity for r in results)),
            ("tokens", f"in={sum(r.usage.input_tokens for r in results)} "
                       f"out={sum(r.usage.output_tokens for r in results)}"),
        ], indent=4)
        timings[provider] = {"sequential_ms": round(seq_elapsed * 1000, 1),
                             "concurrent_ms": round(par_elapsed * 1000, 1),
                             "severities": [r.parsed.severity for r in results]}
        _ = seq  # sequential results kept only for the timing comparison
    note("in dry-run the mock has no network latency so the two columns look similar; against the "
         "real APIs the concurrent column is roughly max(call) instead of sum(call).")
    return timings


def main() -> None:
    parser = build_parser(__doc__ or "")
    args = parser.parse_args()
    clients, dry_run, status = resolve_clients(args)
    header("01 — Structured outputs across two providers", clients, dry_run)
    kv([(f"{p} key present", status[p]) for p in clients])

    schemas = show_schema_path()
    rows = []
    rows += run_helper_path(clients)
    rows += run_raw_path(clients, schemas)
    rows += run_batch_path(clients)
    repair = run_repair_path(clients, dry_run)
    timings = run_async_path(clients)

    section("7", "comparison")
    table(["provider", "path", "model", "calls", "in", "out", "retries"], [
        [r["provider"], r["path"], r["model"], r["calls"], r["in"], r["out"], r["retries"]]
        for r in rows
    ])
    print("\n  differences worth remembering:")
    note("Anthropic: the helper is messages.parse(output_format=Model) and the raw schema goes in "
         "output_config.format; the response object exposes .parsed_output.")
    note("OpenAI: the helper is responses.parse(text_format=Model) and the raw schema goes in "
         "text.format with strict:true; the response exposes .output_parsed and .output_text.")
    note("Both accept a pydantic class in the helper path — the class never crosses the wire, only "
         "the JSON schema derived from it does.")
    note("Refusals are not errors: a structured-output call can come back with a refusal reason "
         "and no parsed object, so check for a null parse before you index into it.")

    emit_json(args, {"dry_run": dry_run, "schema": schemas["strict"],
                     "reorder_plan_strict": schemas["nested_strict"], "calls": rows,
                     "repair": repair, "timings": timings})


if __name__ == "__main__":
    main()
