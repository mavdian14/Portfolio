# Eval harness

**Lands in week 4.** The design is fixed now so the pipeline is built to be measurable rather
than retrofitted with metrics later.

## Layout

```
evals/
  golden/triage_cases.jsonl    ~40 cases: raw_text -> expected {sku, severity, root_cause, requires_escalation}
  golden/edge_cases.jsonl      ~15 cases: unknown SKU, empty text, multi-SKU note, adversarial, refusal-bait
  run.py                       scores, writes results, --fail-under gate
  results/                     timestamped runs (gitignored)
```

## Scoring

- **Exact match** on `sku`, `severity`, `root_cause`, `requires_escalation`
- **±20% tolerance** on `weeks_of_cover` and `lead_time_impact_days`
- **Hard fail** on an invented SKU: any SKU in the output that is not in `INVENTORY` fails
  the case outright, whatever the other fields say

## Why it calls the pipeline directly

`run.py` imports `app.pipeline.triage` and calls it, rather than posting to the API. Two
reasons: it measures the pipeline instead of the transport, and it stays fast enough to run
on every commit.

## CI vs on demand

CI runs the golden set against the **mock** provider (`--fail-under 0.85`). Live runs are
opt-in and cost money — an eval suite that spends on every push gets disabled within a
fortnight, and then it is worth nothing.
