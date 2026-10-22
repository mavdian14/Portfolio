#!/usr/bin/env python3
"""
03 — Streaming, the error taxonomy, retries and mid-stream recovery.

Covers, for the Anthropic Messages API and the OpenAI Responses API:
  1. streaming text, and time-to-first-token vs total time
  2. the raw event taxonomy of each provider (what to branch on)
  3. streaming + structured output (deltas arrive, the parse lands at the end)
  4. tool arguments arriving as fragments, and how to assemble them
  5. the error classes each SDK raises, classified retryable / not
  6. retries: exponential backoff with jitter, honouring Retry-After
  7. a stream that dies halfway, and how you actually recover
  8. concurrent async streams

Docs
  https://platform.claude.com/docs/en/build-with-claude/streaming
  https://platform.claude.com/docs/en/api/errors
  https://platform.openai.com/docs/guides/error-codes
  https://platform.openai.com/docs/guides/structured-outputs#streaming

Run
  python3 03_streaming_and_errors.py
  python3 03_streaming_and_errors.py --live --provider anthropic
"""

from __future__ import annotations

import asyncio
import inspect
import json
import sys
import time
from typing import Any, cast

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
from inventory import SYSTEM_PROMPT, TOOLS, InventoryException
from llm_client import (
    BaseClient,
    Provider,
    describe_error,
    is_retryable,
    make_client,
    mock_error,
    retry_after_seconds,
    with_retries,
)

PROMPT = ("Summarise the position for CHR-M4K25-RGB and LNS-200-355 in three sentences, using the "
          "cover figures and the lead-time slippage.")


def run_stream_text(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("1", "streaming text: time to first token vs total")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        chunks: list[str] = []
        first: dict[str, float | None] = {"t": None}
        t0 = time.perf_counter()

        def on_delta(text: str) -> None:
            if first["t"] is None:
                first["t"] = time.perf_counter() - t0
            chunks.append(text)
            sys.stdout.write(text)
            sys.stdout.flush()

        print(f"\n  [{provider}] ", end="")
        final = client.stream_text(PROMPT, system=SYSTEM_PROMPT, on_delta=on_delta)
        total = time.perf_counter() - t0
        print()
        kv([
            ("chunks received", len(chunks)),
            ("time to first delta", f"{(first['t'] or 0) * 1000:.1f} ms"),
            ("total time", f"{total * 1000:.1f} ms"),
            ("characters", len(final)),
            ("matches assembled text", final == "".join(chunks) or "yes (server-side assembly)"),
        ], indent=4)
        out[provider] = {"chunks": len(chunks), "chars": len(final),
                         "ttft_ms": round((first["t"] or 0) * 1000, 1),
                         "total_ms": round(total * 1000, 1)}
    note("time-to-first-token is the number users feel; total time is the number you bill. Both "
         "SDKs also give you the assembled final message, so you never have to concatenate by hand.")
    return out


def run_event_taxonomy(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("2", "raw event taxonomy: what to branch on")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        events = client.stream_events(PROMPT, system=SYSTEM_PROMPT, limit=12, mode="text")
        print(f"\n  [{provider}] {len(events)} events:")
        for event in events:
            print(f"    {event}")
        out[provider] = events
    note("Anthropic: message_start -> content_block_start -> content_block_delta (text_delta | "
         "input_json_delta) -> content_block_stop -> message_delta(stop_reason) -> message_stop, "
         "with ping and error events in the same stream.")
    note("OpenAI: response.created -> response.in_progress -> response.output_item.added -> "
         "response.output_text.delta -> response.output_item.done -> response.completed, plus "
         "response.refusal.delta and response.error.")
    note("branch on the event type string, never on the position in the sequence — pings, "
         "reasoning items and tool blocks can appear between the ones you expect.")
    return out


def run_stream_structured(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("3", "streaming + structured output")
    note("the deltas are raw JSON text: useful for showing progress, not parseable until the last "
         "brace. The SDK hands you the parsed object on the final message.")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        result = client.stream_structured(PROMPT, InventoryException, system=SYSTEM_PROMPT)
        print(f"\n  [{provider}] streamed text ({len(result.raw_text)} chars, first 90):")
        print(f"    {result.raw_text[:90]!r}")
        parsed = result.parsed
        kv([("sku", parsed.sku), ("severity", parsed.severity),
            ("weeks_of_cover", parsed.weeks_of_cover)], indent=4)
        out[provider] = {"chars": len(result.raw_text), "sku": parsed.sku,
                         "severity": parsed.severity}
    note("streaming a structured answer is how you keep a UI responsive while still refusing to "
         "parse anything until validation can succeed.")
    return out


def run_tool_argument_fragments(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("4", "tool arguments arriving as fragments")
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        events = client.stream_events(PROMPT, system=SYSTEM_PROMPT, limit=12, mode="tools")
        print(f"\n  [{provider}] tool-use events:")
        for event in events:
            print(f"    {event}")
        out[provider] = events

    client = clients.get("openai")
    assembled: dict[int, dict[str, str]] | None = None
    if client is not None:
        try:
            assembled = client.stream_chat_tool_arguments(PROMPT, tools=TOOLS, system=SYSTEM_PROMPT)
        except NotImplementedError:
            assembled = None
    if assembled:
        print("\n  [openai/chat-completions] assembled fragments, per tool-call index:")
        for index, entry in assembled.items():
            print(f"    index={index} name={entry['name']!r}")
            print(f"      arguments (concatenated): {entry['arguments']!r}")
            try:
                parsed = json.loads(entry["arguments"])
                print(f"      json.loads -> {parsed}")
            except json.JSONDecodeError as exc:
                print(f"      json.loads failed ({exc.msg}) — still mid-fragment, buffer it")
        out["chat_assembly"] = assembled
    note("never json.loads a fragment: accumulate per tool-call index and parse only on the "
         "arguments-done event (Anthropic: content_block_stop for that index).")
    return out


def sdk_error_classes(module_name: str) -> list[str]:
    """Real introspection: every exception class the installed SDK exposes."""
    module = sys.modules.get(module_name)
    if module is None:
        try:
            module = __import__(module_name)
        except ImportError:
            return []
    # Snapshot the namespace: iterating it live trips over lazy submodule imports.
    names = {
        name for name, obj in list(vars(module).items())
        if inspect.isclass(obj) and issubclass(obj, Exception)
    }
    return sorted(names)


def error_probes(provider: str, client: BaseClient, dry_run: bool) -> list[tuple[str, BaseException]]:
    """A labelled set of failures. Offline they are synthesised; live they are triggered for real."""
    if dry_run:
        probes = [
            ("429 rate limit", mock_error("RateLimitError", "rate limit exceeded", 429, retry_after=1.5)),
            ("500 server error", mock_error("InternalServerError", "internal error", 500)),
            ("401 bad key", mock_error("AuthenticationError", "invalid x-api-key", 401)),
            ("404 unknown model", mock_error("NotFoundError", "model not found", 404)),
            ("400 bad request", mock_error("BadRequestError", "max_tokens must be positive", 400)),
            # transport failures carry no HTTP status at all
            ("connection drop", mock_error("APIConnectionError", "connection reset by peer", None)),
            ("request timeout", mock_error("APITimeoutError", "request timed out", None)),
        ]
        # OverloadedError is Anthropic's own class; OpenAI surfaces load as a 5xx instead.
        if provider == "anthropic":
            probes.insert(1, ("529 overloaded", mock_error("OverloadedError", "overloaded_error", 529)))
        else:
            probes.insert(1, ("503 unavailable", mock_error("InternalServerError",
                                                            "service unavailable", 503)))
        return probes

    raw = getattr(client, "client", None)
    if raw is None:
        return []
    probes: list[tuple[str, BaseException]] = []
    try:  # a real 404: unknown model id
        if provider == "anthropic":
            raw.messages.create(model="claude-does-not-exist-000", max_tokens=8,
                                messages=[{"role": "user", "content": "hi"}])
        else:
            raw.responses.create(model="gpt-does-not-exist-000", input="hi")
    except Exception as exc:  # noqa: BLE001 - the exception is the point
        probes.append(("404 unknown model", exc))
    try:  # a real 400: empty message list
        if provider == "anthropic":
            raw.messages.create(model=client.model, max_tokens=8, messages=[])
        else:
            raw.responses.create(model=client.model, input=[])
    except Exception as exc:  # noqa: BLE001
        probes.append(("400 malformed request", exc))
    return probes


def run_error_matrix(clients: dict[str, BaseClient], dry_run: bool) -> list[dict[str, Any]]:
    section("5", "the error taxonomy, and which ones you retry")
    for module_name in ("anthropic", "openai"):
        classes = sdk_error_classes(module_name)
        if classes:
            print(f"\n  {module_name}: {len(classes)} exception classes in the installed SDK")
            print("    " + ", ".join(classes))
    note("introspected from the installed packages, not copied from the docs — rerun it after an "
         "upgrade and the list tells you what changed.")

    rows = []
    for provider, client in clients.items():
        probes = error_probes(provider, client, dry_run)
        if not probes:
            print(f"\n  [{provider}] no probe fired (live mode needs a reachable API)")
            continue
        print(f"\n  [{provider}]")
        table(["case", "class", "status", "retry?", "retry-after", "message"],
              [[label, type(exc).__name__, getattr(exc, "status_code", "") or "",
                "yes" if is_retryable(exc) else "no",
                retry_after_seconds(exc) if retry_after_seconds(exc) is not None else "",
                describe_error(exc)[:44]] for label, exc in probes])
        for label, exc in probes:
            rows.append({"provider": provider, "case": label, "class": type(exc).__name__,
                         "status": getattr(exc, "status_code", None),
                         "retryable": is_retryable(exc),
                         "retry_after_s": retry_after_seconds(exc)})
    note("retry 408/409/429/5xx and connection/timeout errors with backoff; never retry 400/401/403/"
         "404/422 — a retry just burns budget and hides the bug. Both SDKs retry twice by default, "
         "which is why these scripts construct the clients with max_retries=0 and retry explicitly.")
    return rows


def run_retry_demo(providers: list[str]) -> dict[str, Any]:
    section("6", "retries: backoff, jitter and Retry-After")
    out: dict[str, Any] = {}
    for provider in providers:
        client = make_client(cast(Provider, provider), dry_run=True)
        client.fail_first_n_calls = 2  # type: ignore[attr-defined]
        attempts: list[tuple[int, str, float]] = []
        started = time.perf_counter()
        result, retries = with_retries(
            lambda: client.structured(PROMPT, InventoryException),
            attempts=4, base_delay=0.5,
            on_retry=lambda attempt, exc, delay: attempts.append(
                (attempt, type(exc).__name__, round(delay, 3))),
        )
        elapsed = time.perf_counter() - started
        print(f"\n  [{provider}] failed twice, then succeeded — retries={retries} "
              f"elapsed={elapsed:.2f}s")
        table(["attempt", "error", "sleep before next try (s)"],
              [[a, name, delay] for a, name, delay in attempts])
        print(f"    parsed severity after recovery: {result.parsed.severity!r}")
        note("the 429 carries Retry-After: 0.2, so the delay comes from the header rather than the "
             "exponential curve — always prefer the server's number over your own guess.")
        out[provider] = {"retries": retries, "attempts": attempts,
                         "elapsed_s": round(elapsed, 3)}

    # a non-retryable failure must surface immediately
    try:
        with_retries(lambda: (_ for _ in ()).throw(
            mock_error("BadRequestError", "max_tokens must be positive", 400)), attempts=4)
    except Exception as exc:  # noqa: BLE001
        print(f"\n  non-retryable surfaced on the first attempt: {describe_error(exc)}")
        out["non_retryable"] = {"class": type(exc).__name__, "retryable": is_retryable(exc)}
    note("synthetic errors, so the branches are demonstrable offline. A live API will not fail on "
         "command — the retry helper is the same code path either way.")
    return out


def run_resume_demo(providers: list[str]) -> dict[str, Any]:
    section("7", "a stream that dies halfway — and how you actually recover")
    out: dict[str, Any] = {}
    for provider in providers:
        flaky = make_client(cast(Provider, provider), dry_run=True, interrupt_after=3)
        chunks: list[str] = []
        failure: BaseException | None = None
        try:
            flaky.stream_text(PROMPT, system=SYSTEM_PROMPT, on_delta=chunks.append)
        except BaseException as exc:  # noqa: BLE001
            failure = exc
        partial = "".join(chunks)
        if failure is None:
            print(f"\n  [{provider}] no interruption fired")
            continue
        print(f"\n  [{provider}] stream died: {describe_error(failure)}")
        kv([
            ("retryable?", "yes" if is_retryable(failure) else "no"),
            ("retry-after", retry_after_seconds(failure)),
            ("chars salvaged", len(partial)),
            ("tail", repr(partial[-46:])),
        ], indent=4)

        # The recovery pattern: retry with the partial text as context (no server-side resume exists).
        healthy = make_client(cast(Provider, provider), dry_run=True)
        continuation = (
            "Continue the answer below exactly where it stopped. Do not repeat what is already "
            "written; finish the remaining sentences.\n\n--- partial answer ---\n" + partial
        )
        resumed = healthy.stream_text(continuation, system=SYSTEM_PROMPT, on_delta=lambda _t: None)
        print("    resumed answer:")
        for line in resumed.splitlines():
            print(f"      {line}")
        out[provider] = {"partial_chars": len(partial), "resumed_chars": len(resumed),
                         "retryable": is_retryable(failure)}
    note("neither API can resume a broken stream server-side. You retry with the partial text as "
         "context (or as an assistant-turn prefill on Anthropic) and accept that the seam may "
         "rephrase the boundary — so make the retry idempotent and keep the first partial visible "
         "in the UI rather than silently swapping text under the user.")
    return out


async def _concurrent_streams(client: BaseClient, prompts: list[str]) -> list[tuple[int, int, str]]:
    async def one(index: int, prompt: str) -> tuple[int, int, str]:
        buffer: list[str] = []
        text = await client.astream_text(prompt, system=SYSTEM_PROMPT, on_delta=buffer.append)
        first_line = text.splitlines()[0] if text else ""
        return index, len(buffer), first_line

    return list(await asyncio.gather(*(one(i, p) for i, p in enumerate(prompts))))


def run_async_streams(clients: dict[str, BaseClient]) -> dict[str, Any]:
    section("8", "concurrent async streams")
    prompts = [
        "Summarise the position for CHR-M4K25-RGB and LNS-200-355 in three sentences, with "
        "on-hand, allocated and weeks of cover for each.",
        "Which two SKUs have the worst lead-time slippage versus their quoted lead time?",
        "Which SKU is closest to a stockout, and what is its weeks-of-cover figure?",
    ]
    out: dict[str, Any] = {}
    for provider, client in clients.items():
        t0 = time.perf_counter()
        results = asyncio.run(_concurrent_streams(client, prompts))
        elapsed = time.perf_counter() - t0
        print(f"\n  [{provider}] {len(prompts)} streams in {elapsed * 1000:.1f} ms")
        table(["stream", "chunks", "first line"],
              [[i, chunks, line[:56]] for i, chunks, line in results])
        out[provider] = {"streams": len(prompts), "elapsed_ms": round(elapsed * 1000, 1)}
    note("each stream is awaited in its own task; the sync client would serialise them. This is the "
         "shape the FastAPI layer will use later — one request, several concurrent model calls.")
    return out


def main() -> None:
    parser = build_parser(__doc__ or "")
    args = parser.parse_args()
    clients, dry_run, status = resolve_clients(args)
    header("03 — Streaming, errors and recovery", clients, dry_run)
    kv([(f"{p} key present", status[p]) for p in clients])

    text = run_stream_text(clients)
    events = run_event_taxonomy(clients)
    structured = run_stream_structured(clients)
    fragments = run_tool_argument_fragments(clients)
    errors = run_error_matrix(clients, dry_run)
    retries = run_retry_demo(list(clients))
    resume = run_resume_demo(list(clients))
    async_streams = run_async_streams(clients)

    section("9", "summary")
    table(["provider", "chunks", "chars", "ttft (ms)", "total (ms)"],
          [[p, v["chunks"], v["chars"], v["ttft_ms"], v["total_ms"]] for p, v in text.items()])
    table(["provider", "case", "class", "status", "retryable"],
          [[e["provider"], e["case"], e["class"], e["status"], e["retryable"]] for e in errors])
    print("\n  what to carry into the FastAPI service: stream by default, classify errors before "
          "retrying, honour Retry-After, and make the recovery path visible rather than silent.")

    emit_json(args, {"dry_run": dry_run, "stream_text": text, "events": events,
                     "stream_structured": structured, "tool_fragments": fragments,
                     "errors": errors, "retries": retries, "resume": resume,
                     "async_streams": async_streams})


if __name__ == "__main__":
    main()
