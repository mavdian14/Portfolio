# exception-desk — build plan

> Supply-chain exceptions arrive as free text from five directions. `exception-desk` turns them into
> validated, evidence-backed records with a recommended action — and nothing gets committed until a
> human approves it.

Status: **week 1 of 4** · Location: `ai-engineering/exception-desk/` (promote to a standalone repo once
it has a green eval run, a Compose one-liner, and a live URL)

---

## 1. Why this project

The exception queue is where supply chains lose time. A supplier pushes a date, a planner spots a
coverage gap, a PO acknowledgement disagrees with the original order — and it all arrives as prose in
an inbox. Somebody has to read it, decide what it means, check it against the actual inventory
position, and act. That work is repetitive, it is judgement-heavy, and it leaves almost no audit trail.

This service does the reading and the checking, then stops and asks a human to decide.

It is deliberately built on the same synthetic inventory domain as `practice/ai-foundations/`, so the
study scripts act as the spike and this is the productionised version. The story is: *spiked the SDK
primitives in throwaway scripts, then built the service around them.*

## 2. What it does

1. **Ingest** — `POST /exceptions` takes raw text (supplier email, planner note, PO acknowledgement).
   Returns `202 Accepted` and a job id, because a tool-calling LLM request takes 5–30 seconds and an
   HTTP handler must not hold a connection open that long.
2. **Triage** — a background worker extracts a validated record, then uses **tools** against the
   inventory data to check the claim (is the lead time really slipping? is the SKU really below its
   reorder point?), then produces a recommended action with a confidence score.
3. **Queue** — `GET /exceptions` returns the triage queue, filterable by status, severity and SKU.
4. **Decide** — a human approves, edits or rejects. Only then does anything write.
5. **Audit** — every record carries the tool results that supported it, the prompt version that
   produced it, the model, the cost, and who approved it.

## 3. The decisions worth defending

| Decision | Alternative rejected | Why |
| --- | --- | --- |
| `202` + job id, worker does the triage | Blocking request handler | LLM latency in a request path times out behind any proxy; the queue also survives restarts |
| Model recommends, human commits | Model writes directly | Any component that can act unreviewed on supplier commitments will eventually act wrongly |
| Evidence stored per field | Store only the final record | Without evidence you cannot tell a grounded extraction from a plausible invention |
| Prompts are versioned files, recorded per record | Prompt strings inline in code | Lets you prove a prompt change helped, with data, instead of guessing |
| Evals in CI against the mock provider | Evals against the live API | Live evals cost money on every push and fail on provider flakiness |
| `FOR UPDATE SKIP LOCKED` for the queue | Application-level locking | Two workers cannot double-claim a job; a slow job never blocks a fast one |
| Idempotent ingest via a hash of the normalised text | Dedupe by exact string | The same supplier email with a trailing newline must not create two exceptions |

## 4. Architecture

```
                    POST /exceptions
                          │
                   normalise → sha256 → ON CONFLICT DO NOTHING
                          │
                    ingest_jobs (queued)
                          │
        ┌─────────────────┴─────────────────┐
        │   worker: claim 1 job atomically   │
        │   FOR UPDATE SKIP LOCKED           │
        └─────────────────┬─────────────────┘
                          │
              ┌───────────▼───────────┐
              │   triage pipeline     │
              │   round 1: tool loop  │──── 5 inventory tools (real handlers)
              │   round 2: extract    │──── structured output → InventoryException
              │   validate → repair   │──── bounded re-ask on ValidationError
              └───────────┬───────────┘
                          │
        exception_evidence + llm_calls  (provenance, cost)
                          │
                  status = needs_review
                          │
                 POST /exceptions/{id}/decision
                          │
                     decisions (audited)
```

## 5. Repository layout

```
exception-desk/
├── README.md                     ← the story (see §12)
├── PLAN.md                       ← this file
├── docker-compose.yml            ← api + worker + db, healthchecked
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── .env.example
├── app/
│   ├── main.py                   ← FastAPI app, routers, lifespan
│   ├── config.py                 ← pydantic-settings; every knob typed
│   ├── api/
│   │   ├── deps.py               ← dependency injection (db session, clients, settings)
│   │   ├── exceptions.py         ← ingest, queue, detail, stream, decision
│   │   ├── evals.py              ← eval run + latest results
│   │   └── ops.py                ← healthz, readyz, cost metrics
│   ├── domain/                   ← PROMOTED from practice/ai-foundations
│   │   ├── models.py             ← pydantic schemas
│   │   ├── inventory.py          ← synthetic master data + tools + registry
│   │   └── prompts/
│   │       ├── triage_system.v1.md
│   │       ├── triage_extract.v1.md
│   │       └── repair.v1.md
│   ├── llm/                      ← PROMOTED from practice/ai-foundations
│   │   ├── base.py               ← BaseClient + result types
│   │   ├── anthropic.py
│   │   ├── openai.py
│   │   ├── ollama.py             ← local fallback
│   │   ├── mock.py               ← deterministic; used by CI and tests
│   │   └── retry.py              ← with_retries, is_retryable
│   ├── pipeline/
│   │   ├── ingest.py             ← normalise → hash → dedupe → enqueue
│   │   ├── triage.py             ← tool loop + extract + repair, one importable function
│   │   ├── worker.py             ← job claim loop, backoff, graceful shutdown
│   │   └── cost.py               ← tokens → USD per model
│   ├── db/
│   │   ├── models.py             ← SQLAlchemy 2.0 tables
│   │   ├── repo.py               ← every query lives here, nowhere else
│   │   └── migrations/           ← alembic
│   └── observability/
│       └── tracing.py            ← request id, per-call logging
├── evals/
│   ├── golden/triage_cases.jsonl
│   ├── golden/edge_cases.jsonl
│   ├── run.py                    ← scores, writes results, --fail-under gate
│   └── results/
├── ui/index.html                 ← single static page, no build step
├── tests/
└── data/generate.py              ← ~300 synthetic exception messages
```

Two structural rules: **all SQL lives in `db/repo.py`** (no queries in route handlers), and
**`pipeline/triage.py` imports without FastAPI** — because `evals/run.py` calls it directly rather
than over HTTP. That constraint is what keeps the eval harness fast and honest.

## 6. Data model

Five tables. `exception_evidence` is what makes the record auditable rather than merely plausible.

```sql
CREATE TABLE exceptions (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_hash           TEXT UNIQUE NOT NULL,        -- idempotency key
    source_kind           TEXT NOT NULL,               -- supplier_email | planner_note | po_ack
    raw_text              TEXT NOT NULL,
    received_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    status                TEXT NOT NULL DEFAULT 'pending',
    -- pending | triaging | needs_review | decided | failed

    sku                   TEXT,
    severity              TEXT,
    root_cause            TEXT,
    weeks_of_cover        NUMERIC(8,2),
    lead_time_impact_days INT,
    recommended_action    TEXT,
    requires_escalation   BOOLEAN,
    confidence            NUMERIC(4,3),
    rationale             TEXT,

    prompt_version        TEXT,
    model                 TEXT,
    provider              TEXT,
    cost_usd              NUMERIC(10,6),
    triaged_at            TIMESTAMPTZ,
    error                 TEXT
);

CREATE TABLE exception_evidence (
    id            BIGSERIAL PRIMARY KEY,
    exception_id  UUID NOT NULL REFERENCES exceptions(id) ON DELETE CASCADE,
    round         INT  NOT NULL,
    tool          TEXT NOT NULL,
    arguments     JSONB NOT NULL,
    result        JSONB NOT NULL,
    is_error      BOOLEAN NOT NULL DEFAULT false
);

CREATE TABLE decisions (
    id            BIGSERIAL PRIMARY KEY,
    exception_id  UUID NOT NULL REFERENCES exceptions(id),
    decided_by    TEXT NOT NULL,
    outcome       TEXT NOT NULL,                       -- approved | edited | rejected
    final_action  TEXT NOT NULL,
    note          TEXT,
    decided_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE llm_calls (
    id             BIGSERIAL PRIMARY KEY,
    exception_id   UUID REFERENCES exceptions(id),
    provider       TEXT NOT NULL,
    model          TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    input_tokens   INT NOT NULL,
    output_tokens  INT NOT NULL,
    cost_usd       NUMERIC(10,6) NOT NULL,
    latency_ms     INT NOT NULL,
    retries        INT NOT NULL DEFAULT 0,
    outcome        TEXT NOT NULL,                      -- ok | error | refused
    error_class    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ingest_jobs (
    id           UUID PRIMARY KEY,
    exception_id UUID NOT NULL REFERENCES exceptions(id),
    status       TEXT NOT NULL DEFAULT 'queued',       -- queued | running | done | failed
    attempts     INT  NOT NULL DEFAULT 0,
    available_at TIMESTAMPTZ NOT NULL DEFAULT now(),   -- backoff lands here
    locked_by    TEXT,
    last_error   TEXT
);
```

`llm_calls` is deliberately decoupled from `exceptions`: a triage attempt can fail entirely and still
cost money, and that has to be visible.

**pgvector is provisioned by the database container, not by Alembic.** Extension provisioning is an
infrastructure concern; migrations describe application schema. Keeping them separate means the app
migrates cleanly against any Postgres, and M2 gets the extension already present.

## 7. API contract

| Method | Path | Returns | Notes |
| --- | --- | --- | --- |
| `POST` | `/exceptions` | `202` `{exception_id, job_id, duplicate}` | Never blocks on the model |
| `GET` | `/exceptions` | paginated queue | `?status=&severity=&sku=&limit=&cursor=` |
| `GET` | `/exceptions/{id}` | record + evidence + decision | the audit view |
| `GET` | `/exceptions/{id}/stream` | `text/event-stream` | triage progress live |
| `POST` | `/exceptions/{id}/decision` | the committed decision | `409` if already decided |
| `POST` | `/triage` | `200` + full record | sync one-shot, for the UI demo |
| `GET` | `/evals/latest` | last run + per-field accuracy | what M3 builds on |
| `GET` | `/metrics/cost` | tokens + USD by model and day | |
| `GET` | `/healthz` · `/readyz` | | liveness vs database-reachable |

Ingest response:

```json
{ "exception_id": "b3f1…", "job_id": "0a92…", "duplicate": false, "status": "pending" }
```

A triaged record — `evidence` and `provenance` are first-class fields, not debug output:

```json
{
  "id": "b3f1…",
  "status": "needs_review",
  "sku": "CHR-M4K25-RGB",
  "severity": "critical",
  "root_cause": "supplier_delay",
  "weeks_of_cover": 0.71,
  "lead_time_impact_days": 23,
  "requires_escalation": true,
  "confidence": 0.86,
  "recommended_action": "Expedite PO-88411 and pull cover from the EMEA buffer",
  "rationale": "Observed lead time is 68 days against 45 quoted, and the PO-88411 line is already at risk.",
  "evidence": [
    {"round": 1, "tool": "get_sku_status",       "result": {"weeks_of_cover": 0.71},      "is_error": false},
    {"round": 1, "tool": "get_lead_time",        "result": {"slippage_days": 23},         "is_error": false},
    {"round": 1, "tool": "query_open_positions", "result": {"at_risk_pos": ["PO-88411"]}, "is_error": false}
  ],
  "provenance": {
    "prompt_version": "triage_extract.v1",
    "provider": "anthropic", "model": "claude-sonnet-4-5",
    "cost_usd": 0.00412, "llm_calls": 3
  }
}
```

## 8. The pipeline

```
POST /exceptions
  → normalise   (collapse whitespace, strip quoting, uppercase SKU codes)
  → sha256(normalised)                        ← hash AFTER normalising
  → INSERT ... ON CONFLICT (source_hash) DO NOTHING
  → enqueue ingest_jobs row
  → 202

worker  (separate process, same image)
  → claim ONE job atomically:
      UPDATE ingest_jobs SET status='running', locked_by=$host
      WHERE id = (SELECT id FROM ingest_jobs
                  WHERE status='queued' AND available_at <= now()
                  ORDER BY available_at
                  FOR UPDATE SKIP LOCKED LIMIT 1)
      RETURNING *;
  → exceptions.status = 'triaging'
  → triage():
        round 1   tool loop  (5 inventory tools, real handlers)
        round 2   structured extract → InventoryException + recommended_action
        validate  on ValidationError → repair loop (max 2 re-asks)
  → write exception_evidence + llm_calls rows
  → exceptions.status = 'needs_review'
  → on failure: attempts++, available_at = now() + 2^attempts seconds, status='queued'
                (give up at 5 attempts → status='failed', error=…)
```

`available_at` is what makes backoff possible. Without it a failing job spins in a hot loop and burns
the API budget in seconds.

## 9. Prompt versioning

Prompts are files with the version in the name, loaded by `(name, version)`, and the version string is
written to `exceptions.prompt_version` and every `llm_calls` row. Editing a prompt means a new file,
never an edit in place. That is what lets the README say, with data: *"v2 raised severity accuracy
from 0.78 to 0.91 and cost 12% more per case."*

## 10. Eval harness

```
evals/golden/triage_cases.jsonl    ~40 cases: raw_text → expected {sku, severity, root_cause, requires_escalation}
evals/golden/edge_cases.jsonl      ~15 cases: unknown SKU, empty text, multi-SKU note, adversarial, refusal-bait
evals/run.py                       imports pipeline.triage directly (no HTTP), scores, writes results
```

Scoring: exact match on enums and SKU, ±20% tolerance on numerics, plus a hard **"no invented SKU"**
check — any SKU in the output that is not in `INVENTORY` fails the case outright.

Reported: accuracy per field, p50/p95 latency, cost per case, and a regression gate
(`--fail-under 0.85`) that CI runs against the **mock** provider. Live runs are on demand.

## 11. Four weeks, with done-criteria

| Week | Build | Done when |
| --- | --- | --- |
| 1 | Promote `domain/` + `llm/`; Postgres in Compose; Alembic; FastAPI skeleton; `POST /triage` against the mock | Compose comes up and a record comes back with evidence rows persisted |
| 2 | `POST /exceptions` + worker + `SKIP LOCKED` claim + idempotency + cost accounting | The same text posted twice returns `duplicate: true` and creates one row; a forced provider failure retries and then succeeds |
| 3 | SSE stream, decision endpoint, prompt versioning, degradation | You can watch a triage stream live, approve it, and the decision is audited |
| 4 | Eval harness + golden set, Compose polish, deploy + demo key, `ui/index.html`, README | A stranger opens the URL, watches a triage, approves one, and the README shows a pass rate |

## 12. The README a hiring manager reads

1. One-paragraph problem statement.
2. Architecture diagram.
3. Four decisions, each with the alternative rejected and why.
4. Results table — eval accuracy, p95 latency, cost per exception.
5. A 30-second GIF of the UI triaging something.
6. "What I'd do differently at 100× volume."

## 13. Pitfalls

1. **`create_all()` instead of migrations.** Alembic from commit one, or it never gets retrofitted.
2. **A blocking triage endpoint.** `202` + worker, always.
3. **Live evals in CI.** Costs money every push and fails on provider flakiness. Mock in CI, live on demand.
4. **An unrate-limited demo key.** The deploy is public; a stranger with a loop is the bill. Per-key rate
   limit and a hard daily token cap, enforced *before* the provider call.
5. **Over-engineering the SSE.** Polling the row every 500 ms is the honest week-3 version.
   `LISTEN/NOTIFY` is a week-6 improvement.
6. **Installing pgvector and building a vector table.** Extension only; M2 gets the table.
7. **Synthetic data that is too clean.** `data/generate.py` must produce multi-SKU notes, missing dates,
   and at least one supplier email with no SKU at all, or the queue and the edge cases go untested.
