# exception-desk

An LLM-backed triage service for supply-chain exceptions. Inbound supplier emails and planner notes go
in; validated, evidence-backed records with a recommended action come out — and nothing gets committed
until a human approves it.

> **Status: week 1 of 4.** The build plan, data model, API contract and week-by-week done-criteria are
> in [PLAN.md](PLAN.md). This README grows into the full project story by week 4.

**All inventory data is synthetic.** SKU codes, suppliers and figures are invented sample data — no real
commercial data is included.

---

## What works today

| Endpoint | Status |
| --- | --- |
| `POST /triage` | ✅ sync one-shot triage — runs the tool loop, extracts, persists the record + evidence + cost |
| `GET /exceptions` | ✅ the queue, filterable by status / severity / SKU |
| `GET /exceptions/{id}` | ✅ the audit view: record + evidence + provenance |
| `GET /metrics/cost` | ✅ tokens and USD by model and day |
| `GET /healthz` · `GET /readyz` | ✅ liveness and database-reachable |
| `POST /exceptions` (202 + worker) | ⏳ week 2 |
| `POST /exceptions/{id}/decision` | ⏳ week 3 |
| `GET /exceptions/{id}/stream` (SSE) | ⏳ week 3 |
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
docker compose up --build          # api + db; migrations run on api startup
```

The worker is defined but behind a profile, because it lands in week 2:

```bash
docker compose --profile worker up
```

## Try it

No API key needed — `LLM_PROVIDER=mock` is the default and runs the real tool handlers offline.

```bash
curl -s localhost:8000/triage -H 'content-type: application/json' -d '{
  "source_kind": "supplier_email",
  "text": "Following up on PO-88411 for the M 4K25 RGB (CHR-M4K25-RGB) — our production line is fully committed through December, so we cannot confirm the Nov 14 date. We can offer Dec 2 at the earliest."
}' | python -m json.tool
```

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
- **Evals run against the mock provider in CI.** Live evals cost money on every push and fail on
  provider flakiness.

## Layout

```
app/
  domain/     synthetic inventory data, the 5 tools, pydantic schemas, versioned prompts
  llm/        provider clients (anthropic | openai | ollama | mock) behind one interface
  pipeline/   ingest → triage → cost accounting
  db/         SQLAlchemy tables, every query in repo.py, Alembic migrations
  api/        routers, dependency injection
evals/        golden dataset + scorer (week 4)
ui/           single static page, no build step (week 4)
```

Two rules hold the structure together: **all SQL lives in `db/repo.py`** — no queries in route handlers —
and **`pipeline/triage.py` imports without FastAPI**, because `evals/run.py` calls it directly rather
than over HTTP.

## Tests

```bash
.venv/bin/pytest -q
```

## Lineage

`app/domain/` and `app/llm/` are the productionised versions of the throwaway SDK study scripts in
[`practice/ai-foundations/`](../../practice/ai-foundations/). The scripts were the spike: hand-wired
primitives against two providers, no framework. This is the service built on them.
