# AI Foundations — SDK Pattern Scripts

Three throwaway CLI scripts for studying the **Anthropic Claude SDK** and the **OpenAI SDK** end-to-end,
built around a synthetic **inventory & supply-chain** domain (SKU exceptions, stock cover, supplier lead
times, open purchase orders) so every example stays close to real day-to-day data work.

Every section is annotated with the doc page it demonstrates. Nothing here uses an agent framework —
the point is to hand-wire the primitives so the abstractions stay legible. That is the whole exercise:
*architecture first, framework second.*

> **All inventory data is synthetic.** SKU codes, suppliers and supplier messages are invented sample
> data for study purposes — no real Christie Digital data is included.

## Files

| File | What it is |
| --- | --- |
| `inventory.py` | The domain layer: 12 synthetic SKUs, pydantic schemas, 5 tools, supplier messages, open POs |
| `llm_client.py` | Provider-agnostic client layer: Anthropic + OpenAI, sync + async, payload builders, retries, deterministic mock provider |
| `cli_common.py` | Shared plumbing: argparse, provider resolution, table formatting, strict-schema transform |
| `01_structured_outputs.py` | Structured outputs: extraction, classification, raw JSON schema, batch, repair, concurrency |
| `02_tool_calling_loop.py` | The hand-rolled tool-calling loop: tool surface, round trip, error results, Chat Completions variant, parallel calls, truncation |
| `03_streaming_and_errors.py` | Streaming, event taxonomies, streaming + structured output, tool-arg fragments, error taxonomy, retries, mid-stream recovery, concurrent streams |

## Setup

```bash
cd practice/ai-foundations
python3 -m pip install --user -r requirements.txt   # anthropic, openai, pydantic

# Credentials — only needed for --live (never commit these)
export ANTHROPIC_API_KEY=...      # https://platform.claude.com
export OPENAI_API_KEY=...         # https://platform.openai.com
# or: cp .env.example .env and fill it in — the scripts load .env if present

# Optional model overrides (defaults in llm_client.DEFAULT_MODELS)
export ANTHROPIC_MODEL=claude-sonnet-4-5
export OPENAI_MODEL=gpt-5.6-terra
```

## Run it

Offline is the default. With no key present the scripts run against a deterministic mock provider that
executes the **real** control flow — the same payload builders, the same tool handlers, the same retry
and error branches — and prints the exact request body that would have gone over the wire.

```bash
# offline, no keys, no network, no cost
python3 01_structured_outputs.py
python3 02_tool_calling_loop.py
python3 03_streaming_and_errors.py

# one provider only / machine-readable / model override
python3 01_structured_outputs.py --provider openai
python3 02_tool_calling_loop.py --provider anthropic --json
python3 03_streaming_and_errors.py --model claude-sonnet-4-5

# live against the real APIs (requires the matching key)
python3 01_structured_outputs.py --live
python3 02_tool_calling_loop.py --live --provider both
python3 03_streaming_and_errors.py --live --provider anthropic
```

Flags on all three: `--provider both|anthropic|openai` (default `both`), `--model MODEL`, `--live`,
`--json`. `--live` exits with a clear message if the key for the requested provider is missing.

## What each script covers

### `01_structured_outputs.py`

| # | Section | Pattern |
| --- | --- | --- |
| 1 | pydantic → JSON schema | what the model actually receives; nested models as `$defs`/`$ref` |
| 2 | SDK helper path | Anthropic `messages.parse()` vs OpenAI `responses.parse(text_format=...)` |
| 3 | raw JSON-schema path | Anthropic `output_config.format` vs OpenAI `text.format` — no SDK helper |
| 4 | batch extraction | one list-of-models over 5 supplier notes, not 5 calls |
| 5 | off-schema answers | validate → catch `ValidationError` → repair prompt with the error text |
| 6 | concurrency | `asyncio.gather` over the note backlog, sequential vs concurrent timings |
| 7 | comparison | where the two SDKs converge and where they diverge |

### `02_tool_calling_loop.py`

| # | Section | Pattern |
| --- | --- | --- |
| 1 | the tool surface | the same 5 domain tools as Anthropic `input_schema` vs OpenAI `parameters` + `strict` |
| 2 | the loop | call → `tool_use`/`function_call` → execute → feed results back → final answer |
| 3 | message shapes | the exact role/content each provider requires fed back |
| 4 | tool errors | errors returned **as results** so the model self-corrects instead of crashing |
| 5 | Chat Completions | the same loop on the older surface: nested tool defs, `role="tool"`, `tool_call_id` |
| 6 | parallel vs sequential | `tool_use` blocks arriving together vs forced one-at-a-time |
| 7 | `stop_reason=max_tokens` | truncation is a stop reason, not an error — retry with more budget |
| 8 | side-effect check | the exception the model asked to flag is verified in the domain layer |

### `03_streaming_and_errors.py`

| # | Section | Pattern |
| --- | --- | --- |
| 1 | streaming text | time-to-first-token vs total time; deltas assembled into the final message |
| 2 | event taxonomy | the raw event types each SDK emits, and which ones you actually branch on |
| 3 | streaming + structured output | deltas stream, then one parse at the end |
| 4 | tool-arg fragments | arguments arrive as partial JSON strings — index and assemble them |
| 5 | error taxonomy | every error class per SDK, classified retryable vs not |
| 6 | retries | exponential backoff + jitter, honouring `Retry-After` |
| 7 | mid-stream failure | a stream that dies halfway, and the capture-and-resume recovery |
| 8 | concurrent streams | several async streams in flight; the shape a FastAPI handler will reuse |
| 9 | summary | timings and the retryable/not verdict per case |

## Doc → code map

### Anthropic — Claude Platform Docs

| Doc section | Where it's demonstrated |
| --- | --- |
| [Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages) | `01` §2, `02` §2–3, `llm_client.AnthropicClient` |
| [Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | `01` §1–5 (`messages.parse`, `output_config.format`) |
| [Tool use](https://platform.claude.com/docs/en/build-with-claude/tool-use) | `02` §1–4, 6–8 |
| [Stop reasons and fallback](https://platform.claude.com/docs/en/build-with-claude/handling-stop-reasons) | `02` §7, `03` §1 (final stop reason) |
| [Streaming](https://platform.claude.com/docs/en/build-with-claude/streaming) | `03` §1–4, 7–8 |
| [Errors and retries](https://platform.claude.com/docs/en/api/errors) | `03` §5–6, `llm_client.is_retryable` / `with_retries` |
| [Prompt engineering](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview) | `inventory.SYSTEM_PROMPT`, repair prompts in `01` §5 |

### OpenAI — API Docs

| Doc section | Where it's demonstrated |
| --- | --- |
| [Function calling](https://developers.openai.com/api/docs/guides/function-calling) | `02` §1–4, 6–8 (`function_call` → `function_call_output`) |
| ↳ Chat Completions vs Responses shapes | `02` §5 (`role="tool"`, `tool_call_id`) |
| [Structured outputs](https://platform.openai.com/docs/guides/structured-outputs) | `01` §1–5 (`text_format`, `text.format`, strict schemas) |
| ↳ [streaming structured outputs](https://platform.openai.com/docs/guides/structured-outputs#streaming) | `03` §3–4 |
| [Error codes and retries](https://platform.openai.com/docs/guides/error-codes) | `03` §5–6 |

### Deliberately not covered here

FastAPI (`async`, `Depends`, background tasks, SSE endpoints) — skipped by choice for these scripts.
The pieces that plug into a FastAPI service later are already here: `AsyncAnthropic` / `AsyncOpenAI`,
`async for` streaming, and the concurrent-stream section in `03`, which is exactly the shape an SSE
endpoint will wrap.

## Offline mode, honestly

The mock provider is not a stub that returns canned text. It runs the same code path as the live
clients — request payload builders, tool execution against `inventory.py`, retry loops, error
classification — and swaps only the network call. That means:

- token counts and latencies are **estimates**, not measured API values;
- model prose is generated from the domain data, so it is deterministic and always well-formed;
- the payloads printed in offline mode are the real request bodies, which is the useful part.

Anything about *model behaviour* (how well extraction actually works, where the model chooses to call a
tool) can only be judged with `--live`.

## Cost note

A full run of all three scripts against both providers is a handful of small calls — a few hundred
tokens each, a few cents total. Offline mode makes no network calls and costs nothing.
