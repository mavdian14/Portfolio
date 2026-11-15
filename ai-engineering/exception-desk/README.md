# exception-desk

An LLM-backed triage service for supply-chain exceptions. Inbound supplier emails and planner notes go
in; validated, evidence-backed records with a recommended action come out — and nothing gets committed
until a human approves it.

> **Status: week 3 of 4.** The build plan, data model, API contract and week-by-week done-criteria are
> in [PLAN.md](PLAN.md). This README grows into the full project story by week 4.

**All inventory data is synthetic.** SKU codes, suppliers and figures are invented sample data — no real
commercial data is included.

---

## What works today

| Endpoint | Status |
| --- | --- |
| `POST /exceptions` | ✅ `202` + job id — queue a message, triaged by a worker |
| `POST /triage` | ✅ sync one-shot triage — runs the tool loop, extracts, persists the record + evidence + cost |
| `GET /exceptions` | ✅ the queue, filterable by status / severity / SKU |
| `GET /exceptions/{id}` | ✅ the audit view: record + evidence + provenance |
| `GET /metrics/cost` | ✅ tokens and USD by model and day |
| `POST /exceptions/{id}/decision` | ✅ approve / edit / reject — the approved action executes through the tool layer |
| `GET /exceptions/{id}/stream` | ✅ server-sent events: status changes, then the finished record |
| `GET /prompts` | ✅ prompt versions on disk, and the one the worker renders |
| `GET /healthz` · `GET /readyz` | ✅ liveness and database-reachable |
| `python -m app.pipeline.worker` | ✅ the worker — claims jobs, retries, recovers orphans |
| `ui/index.html` | ✅ a clickable page for the whole loop |
| `GET /evals/latest` | ⏳ week 4 |

## Run it

### Local Postgres

```bash
createdb exception_desk          # or: CREATE ROLE exception_desk LOGIN PASSWORD 'exception_desk'; CREATE DATABASE exception_desk OWNER exception_desk;
cp .env.example .env
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload
```

### Docker Compose

```bash
cp .env.example .env
docker compose up --build                    # api + db; migrations run on api startup
docker compose --profile worker up --build   # adds the worker
```

## Run the worker

The worker is its own process. It polls the queue, triages what it finds, and records what
happened.

```bash
python -m app.pipeline.worker                  # loop until SIGINT/SIGTERM
python -m app.pipeline.worker --once           # one batch, then exit (CI, cron, demos)
python -m app.pipeline.worker --concurrency 8  # jobs held in flight
python -m app.pipeline.worker --prompt-version v2   # render a different prompt set
python -m app.pipeline.worker --help
```

Watch the retry path — the provider is told to fail once, the job backs off, and the next run
picks it up:

```bash
curl -s -X POST localhost:8000/exceptions -H 'content-type: application/json' \
  -d '{"text":"Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB)."}' >/dev/null

python -m app.pipeline.worker --once --fail-first-calls 1   # -> requeued, backoff 2s
python -m app.pipeline.worker --once                        # -> done
```

## Try it

No API key needed — `LLM_PROVIDER=mock` is the default and runs the real tool handlers offline.

```bash
curl -s localhost:8000/triage -H 'content-type: application/json' -d '{
  "source_kind": "supplier_email",
  "text": "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is fully committed through December, so we cannot confirm the Nov 14 date. We can offer Dec 2 at the earliest."
}' | python -m json.tool
```

Or open the UI at <http://localhost:8000/> and click through it. Queue a message, watch the
status frames arrive, read the verdict next to the tool results it rests on, then approve,
edit or reject. The page will sit on `pending` until you run a worker — which is the
architecture, not a bug.

Interactive API docs: <http://localhost:8000/docs>

## What offline mode cannot tell you

`LLM_PROVIDER=mock` is not a stub that returns canned text: it runs the real control flow —
the same payload builders, the same tool handlers against the same master data, the same
retry branches — and swaps only the network call. But two things are honestly worse offline:

1. **Token counts and latencies are estimates.** Roughly four characters per token, zero
   latency. Cost reports against the mock read `$0.000000`, which is correct — no call was
   made — but they are not a forecast of a live bill.
2. **Prose-described parts do not resolve to a SKU code.** The mock matches SKU *codes*
   (`CHR-M4K25-RGB`). A message that says "the GS Series high-security units" without the
   code resolves to `UNKNOWN`, where a live model would typically infer `CHR-GS25-HS` from
   the inventory descriptions. Anything about real model *behaviour* — how well extraction
   actually works, where the model chooses to call a tool — needs `LLM_PROVIDER=anthropic`
   or `openai`.

## The queue

`POST /exceptions` returns `202` and a job id; a worker does the triage. Four things make that a
queue rather than a table:

**`FOR UPDATE SKIP LOCKED`.** Two workers cannot claim the same job, because the row lock decides —
not application logic, and not a race-prone `SELECT` then `UPDATE`. A slow job never blocks a fast
one either: the second worker skips past a locked row instead of waiting on it.

**One active job per exception, enforced by the database.** A partial unique index on
`(exception_id) WHERE status IN ('queued','running')` means a client that retries a `POST` cannot
enqueue a second triage of the same message. The application check in `repo.enqueue` is an
optimisation; the index is the guarantee.

**`available_at` makes backoff possible.** On failure the job is requeued with
`available_at = now() + 2**attempts`. Without that column a failing job is immediately due again
and the worker spins, burning API budget in seconds.

**`locked_at` makes recovery possible.** A worker killed mid-job leaves its row in `running`
forever — and the partial index above means nothing can enqueue a replacement. The worker reclaims
any job still `running` past `WORKER_STALE_AFTER_S` before each batch, so an orphan comes back on
its own.

### Retryable or terminal

Not every failure deserves a retry, and conflating the two is expensive:

| Failure | Classified | Why |
| --- | --- | --- |
| `429`, `5xx`, connection drop, timeout | **retryable** — backoff and try again | The server, not the request |
| `401`, `404`, `400` | **terminal** — fail immediately | A retry sends the same wrong request |
| Schema unsatisfied after the repair loop | **terminal** — fail immediately | The model already had the validator's own error text; a retry pays to reproduce the same failure |

A terminal failure marks both the job and the record `failed`, with the error stored, because a
record stuck in `triaging` with no explanation is worse than one that admits it failed.

## The human decision

The service recommends; it never commits. `POST /exceptions/{id}/decision` takes
`approved`, `edited` or `rejected`.

**Approving executes.** It is not a status flag: the approved action runs through the domain
tool layer, and the tool's result — including a refusal — is written into the decision row.
The tool layer returns errors as data rather than raising, so a decision whose consequence
failed is still recorded as a decision. A record that says "approved" with no trace of what
followed is the least useful row in the database.

**A rejection executes nothing**, and says so: `executed` comes back `null`. That is the
point of a rejection.

**One decision per record.** A second `POST` is a `409`, not an overwrite. Silently replacing
an audit record would defeat the point of having one.

**One transaction.** The decision row and the record's move to `decided` commit together, so
no reader ever sees a decided record with no decision on it.

## Watching it happen

`GET /exceptions/{id}/stream` is server-sent events. It emits `status` on every change, then
`record` with the full audit view once the record is terminal, then `done`. A record that is
already terminal emits everything immediately and closes, so connecting late is not a special
case.

It polls. That is deliberate: triage runs in a **different process**, so the API has nothing
to subscribe to — the worker commits to a table and the stream reads it. Making that push
instead would mean `LISTEN/NOTIFY`, Redis or a broker: real infrastructure for a latency
improvement measured in milliseconds against a job that takes seconds.

Two details that are easy to get wrong:

- **A session per poll, not the request's.** The generator outlives the request dependency's
  scope, and one pooled connection held for the life of a browser tab exhausts the pool after
  a handful of viewers.
- **The blank line after each frame is the terminator.** Omit it and the client buffers
  everything until the connection closes, which looks exactly like a broken stream.

## Prompt versioning

Prompts are files: `app/domain/prompts/{triage_system,triage_extract,repair}.vN.md`. Adding a
file is the whole mechanism. `PROMPT_VERSION` selects one, `--prompt-version` overrides it per
run, and `GET /prompts` reports what exists and what is active.

A versioning scheme that cannot demonstrate a difference is documentation, not engineering, so
v2 changes something real: **v1 treats alarming phrasing as a severity signal; v2 calibrates
severity from the tool results alone.**

```
"PCB-CTRL-M4K is at zero on hand ... quoted 90 days and we are seeing 152 days actual."
  cover 5.0 weeks · slippage 62 days
  v1 -> critical   (the message says "zero on hand")
  v2 -> high       (5 weeks of cover is not critical, whatever the sender thinks)
```

Same message, same tools, same data. The record and every `llm_call` store the prompt version
that produced them, so "which prompt was this?" is answerable from the API and not just from a
psql shell.

The offline provider has to be told which version it is standing in for — a live model reads
the rule out of the prompt, the mock cannot. `make_client` passes `settings.prompt_version`
through for exactly that reason; without it a v2 run would still be graded by v1's rules and
the comparison would be a lie.

## Design notes

The decisions worth defending, and the alternatives rejected, are in [PLAN.md §3](PLAN.md). The short
version:

- **`202` + worker instead of a blocking handler** — a tool-calling request takes 5–30 s; no proxy will
  wait that long, and a queue survives restarts.
- **The model recommends, a human commits.** Anything that can act unreviewed on supplier commitments
  will eventually act wrongly.
- **Evidence is stored per field.** Without it you cannot tell a grounded extraction from a plausible
  invention.
- **Prompts are versioned files, recorded per record** — so a prompt change can be shown to help, with
  data.
- **Approving goes through the domain tool layer, not around it** — the same code path the model's
  read-only tools use, so there is one place where side effects happen and one place to audit.
- **Evals run against the mock provider in CI.** Live evals cost money on every push and fail on
  provider flakiness.

## Layout

```
app/
  domain/     synthetic inventory data, the 5 tools, pydantic schemas, versioned prompts
  llm/        provider clients (anthropic | openai | ollama | mock) behind one interface
  pipeline/   ingest → triage → cost accounting, and the worker that drives them
  db/         SQLAlchemy tables, every query in repo.py, Alembic migrations
  api/        routers, dependency injection
evals/        golden dataset + scorer (week 4)
ui/           single static page, no build step — the clickable front end
```

Three rules hold the structure together: **all SQL lives in `db/repo.py`** — no queries in route
handlers; **`pipeline/triage.py` imports without FastAPI**, because `evals/run.py` calls it directly
rather than over HTTP; and **`pipeline/worker.py` is the only module that loops**, so the API process
never holds a long-running task.

`triage()` is async. That is not decoration: the worker runs several jobs concurrently, and a
synchronous pipeline would serialise them no matter how many coroutines wrapped it.

## Tests

```bash
.venv/bin/pytest -q
```

## Lineage

`app/domain/` and `app/llm/` are the productionised versions of the throwaway SDK study scripts in
[`practice/ai-foundations/`](../../practice/ai-foundations/). The scripts were the spike: hand-wired
primitives against two providers, no framework. This is the service built on them.
