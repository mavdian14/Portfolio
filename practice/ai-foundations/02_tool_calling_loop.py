#!/usr/bin/env python3
"""
02 — The tool-calling loop, hand-rolled for both providers.

Covers, for the Anthropic Messages API and the OpenAI Responses API:
  1. the tool surface the model sees (and how the two definitions differ)
  2. the loop: call -> tool_use / function_call -> execute -> feed results back -> final answer
  3. the exact message shapes each provider needs back
  4. tool errors as results (the model corrects itself instead of crashing)
  5. the Chat Completions variant of the same loop (nested tool defs, role="tool")
  6. parallel vs sequential tool calls
  7. stop_reason=max_tokens and the retry-with-more-budget branch
  8. verification: the side effect the model asked for actually landed in the domain layer

Docs
  https://platform.claude.com/docs/en/build-with-claude/tool-use
  https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons
  https://developers.openai.com/api/docs/guides/function-calling

Run
  python3 02_tool_calling_loop.py
  python3 02_tool_calling_loop.py --live --provider anthropic
"""

from __future__ import annotations

import json
from typing import Any

import inventory
from cli_common import (
    build_parser,
    emit_json,
    header,
    json_block,
    kv,
    note,
    resolve_clients,
    section,
    table,
)
from inventory import SYSTEM_PROMPT, TOOLS, run_tool
from llm_client import (
    BaseClient,
    ToolLoopResult,
    anthropic_tool_kwargs,
    anthropic_tool_schema,
    describe_error,
    openai_chat_tool_schema,
    openai_tool_kwargs,
    openai_tool_schema,
)

PROMPT = (
    "Cover check for two parts: the M 4K25 RGB projector (CHR-M4K25-RGB) and the 2.00-3.55:1 "
    "long-throw lens (LNS-200-355).\n"
    "For each: how many weeks of cover do we have, is the observed lead time running above the "
    "quoted one, and are we below the reorder point at a 95% service level?\n"
    "Flag whichever part is in worse shape for planner follow-up, then summarise in three bullets "
    "with the numbers you used."
)


def show_tool_surface() -> None:
    section("1", "the tool surface the model sees")
    table(["tool", "required args", "strict", "what it returns"],
          [[t.name, ", ".join(t.input_schema["required"]), t.strict, t.description[:52] + "..."]
           for t in TOOLS])
    print("\n  the same tool, as each provider wants it declared:")
    print("  Anthropic — input_schema, strict flag alongside it:")
    json_block(anthropic_tool_schema(TOOLS)[0], indent=4)
    print("\n  OpenAI Responses — flat, parameters instead of input_schema:")
    json_block(openai_tool_schema(TOOLS)[0], indent=4)
    print("\n  OpenAI Chat Completions — nested under 'function' (the classic format trap):")
    json_block(openai_chat_tool_schema(TOOLS)[0], indent=4)


def print_loop(provider: str, result: ToolLoopResult) -> None:
    print(f"\n  [{provider}] {result.usage}")
    if result.transcript:
        print("    transcript:")
        for line in result.transcript:
            print(f"      {line}")
    table(["round", "tool", "arguments", "status", "result"],
          [[c.round, c.name, json.dumps(c.arguments), "ERROR" if c.failed else "ok",
            json.dumps(c.result)[:64] + ("..." if len(json.dumps(c.result)) > 64 else "")]
           for c in result.tool_calls])
    kv([("rounds", result.rounds), ("stop reason", result.stop_reason)], indent=4)
    print("    final answer:")
    for line in (result.final_text or "(empty)").splitlines():
        print(f"      {line}")


def verify_side_effects(result: ToolLoopResult) -> dict[str, Any]:
    """The model asked for a flag_exception; check the domain layer actually recorded it."""
    reported = sorted({c.arguments.get("sku", "") for c in result.tool_calls if c.name == "flag_exception"})
    flagged = sorted({entry["sku"] for entry in inventory._FLAGGED})
    return {
        "flagged_by_model": reported,
        "recorded_in_domain_layer": flagged,
        "match": reported == flagged,
        "tool_errors_seen": sum(1 for c in result.tool_calls if c.failed),
    }


def run_loop(provider: str, client: BaseClient, *, parallel: bool = True,
             max_tokens: int = 1024) -> ToolLoopResult:
    inventory._FLAGGED.clear()
    result = client.tool_loop(PROMPT, tools=TOOLS, system=SYSTEM_PROMPT, parallel=parallel,
                              max_tokens=max_tokens, verbose=True)
    print_loop(provider, result)
    check = verify_side_effects(result)
    kv([("side-effect check", "MATCH — the flag landed in the domain layer" if check["match"]
         else f"MISMATCH {check}"),
        ("tool errors the model worked around", check["tool_errors_seen"])], indent=4)
    return result


def show_message_shapes(result: ToolLoopResult) -> None:
    section("3", "the message shapes each provider needs fed back")
    note("reconstructed from the first tool call above — this is literally what the client appends "
         "to the conversation before the next request.")
    if not result.tool_calls:
        print("  no tool calls were made, nothing to show")
        return
    call = result.tool_calls[0]
    payload = json.dumps(call.result)
    print("\n  Anthropic: assistant turn carrying the tool_use block, then a user turn of tool_result blocks")
    json_block([
        {"role": "assistant", "content": [
            {"type": "tool_use", "id": call.call_id, "name": call.name, "input": call.arguments}]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": call.call_id, "content": payload,
             "is_error": call.failed}]},
    ], indent=4)
    note("no text alongside tool_result blocks, and every tool_use id must be answered or the next "
         "request is rejected.")
    print("\n  OpenAI Responses: typed items, chained by previous_response_id")
    json_block([
        {"type": "function_call", "call_id": call.call_id, "name": call.name,
         "arguments": json.dumps(call.arguments)},
        {"type": "function_call_output", "call_id": call.call_id, "output": payload},
    ], indent=4)
    print("\n  OpenAI Chat Completions: assistant message with tool_calls, then role='tool' messages")
    json_block([
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": call.call_id, "type": "function",
             "function": {"name": call.name, "arguments": json.dumps(call.arguments)}}]},
        {"role": "tool", "tool_call_id": call.call_id, "content": payload},
    ], indent=4)


def run_error_envelope_demo() -> None:
    section("4", "tool errors are results, not exceptions")
    cases = [
        ("unknown SKU", "get_sku_status", {"sku": "CHR-NOPE-000"}),
        ("missing required argument", "get_sku_status", {}),
        ("unknown tool name", "delete_all_inventory", {}),
        ("bad enum value", "flag_exception", {"sku": "CHR-CRWU31", "reason": "x", "severity": "urgent"}),
    ]
    for label, name, args in cases:
        out = run_tool(name, args)
        print(f"\n  {label}: {name}({json.dumps(args)})")
        json_block(out, indent=4, max_lines=6)
    note("every failure comes back as {'error': ...} so the model can read it and try again. "
         "Raising here would kill the loop and lose the model's chance to self-correct.")


def run_chat_completions_variant(clients: dict[str, BaseClient]) -> dict[str, Any] | None:
    section("5", "the same loop on Chat Completions (OpenAI only)")
    client = clients.get("openai")
    if client is None:
        print("  skipped — OpenAI not selected")
        return None
    note("older surface, still everywhere in production. Differences: nested tool definitions, "
         "message.tool_calls instead of typed output items, role='tool' messages, and the whole "
         "history resent every round (no server-side chaining).")
    inventory._FLAGGED.clear()
    result = client.tool_loop_chat_completions(PROMPT, tools=TOOLS, system=SYSTEM_PROMPT)
    print_loop("openai/chat-completions", result)
    check = verify_side_effects(result)
    return {"rounds": result.rounds, "calls": len(result.tool_calls), "match": check["match"]}


def run_parallel_demo(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("6", "parallel vs sequential tool calls")
    print("  the payload flag that controls it:")
    print("    Anthropic tool_choice:", json.dumps(
        anthropic_tool_kwargs("model", [], TOOLS, parallel=False)["tool_choice"]))
    print("    OpenAI parallel_tool_calls:", json.dumps(
        openai_tool_kwargs("model", [], TOOLS, parallel=False)["parallel_tool_calls"]))
    note("parallel is the default on both. Turn it off when the tools have order-dependent side "
         "effects, or when you want a predictable one-call-per-round audit trail.")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        for parallel in (True, False):
            inventory._FLAGGED.clear()
            result = client.tool_loop(PROMPT, tools=TOOLS, system=SYSTEM_PROMPT,
                                      parallel=parallel, verbose=False)
            round1 = sum(1 for c in result.tool_calls if c.round == 1)
            kv([(f"{provider} parallel={parallel}",
                 f"rounds={result.rounds} calls={len(result.tool_calls)} in_round_1={round1} "
                 f"stop={result.stop_reason}")], indent=4)
            out[f"{provider}_parallel_{parallel}"] = {"rounds": result.rounds,
                                                      "calls": len(result.tool_calls)}
    note("in dry-run the mock returns a fixed call set regardless of the flag — what changes here "
         "is the request, which is what you can verify offline.")
    return out


def run_truncation_demo(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("7", "stop_reason=max_tokens: truncation is a stop reason, not an error")
    note("a truncated turn can end mid-tool-call, so the tool_use block is incomplete and "
         "unparseable. Both loops here retry the same request with double the budget instead of "
         "guessing at the partial block.")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        inventory._FLAGGED.clear()
        result = client.tool_loop(PROMPT, tools=TOOLS, system=SYSTEM_PROMPT, max_tokens=64,
                                  verbose=True)
        print(f"\n  [{provider}] budget started at 64 -> rounds={result.rounds} "
              f"stop={result.stop_reason}")
        for line in result.transcript:
            if "max_tokens" in line:
                print(f"    {line}")
        out[provider] = {"rounds": result.rounds, "final_stop_reason": result.stop_reason}
    return out


def main() -> None:
    parser = build_parser(__doc__ or "")
    args = parser.parse_args()
    clients, dry_run, status = resolve_clients(args)
    header("02 — Tool calling: the hand-rolled loop", clients, dry_run)
    kv([(f"{p} key present", status[p]) for p in clients])

    show_tool_surface()

    section("2", "the loop: call -> execute -> feed back -> answer")
    results: dict[str, Any] = {}
    first: ToolLoopResult | None = None
    for provider, client in clients.items():
        result = run_loop(provider, client)
        first = first or result
        results[provider] = {
            "rounds": result.rounds, "calls": len(result.tool_calls),
            "stop_reason": result.stop_reason,
            "tools_used": sorted({c.name for c in result.tool_calls}),
            "usage": str(result.usage),
            **verify_side_effects(result),
        }

    if first is not None:
        show_message_shapes(first)
    run_error_envelope_demo()
    chat = run_chat_completions_variant(clients)
    parallel = run_parallel_demo(clients)
    truncation = run_truncation_demo(clients)

    section("8", "summary")
    table(["provider", "rounds", "tool calls", "stop reason", "tools used"],
          [[p, r["rounds"], r["calls"], r["stop_reason"], ", ".join(r["tools_used"])]
           for p, r in results.items()])
    print("\n  the loop is about 40 lines per provider and has no framework in it. Everything a "
          "framework adds on top — retries, tracing, state, parallelism — you can now read, "
          "because you wrote the version underneath it.")
    note("Anthropic needs the tool_result blocks in a *user* turn with no extra text; OpenAI's "
         "Responses API chains turns server-side via previous_response_id, so you only send the "
         "new function_call_output items; Chat Completions resends everything.")
    note("Errors go back as results with is_error / an 'error' key, never as raised exceptions — "
         "that is what makes the self-correction in section 4 possible.")

    emit_json(args, {"dry_run": dry_run, "loops": results, "chat_completions": chat,
                     "parallel": parallel, "truncation": truncation})


if __name__ == "__main__":
    main()
