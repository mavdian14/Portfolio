Triage the inbound message below into the required schema.

Base every field on the tool results you gathered in this conversation, not on the wording
of the message. Where the message and the tools disagree, the tools win.

- `sku` — the SKU the message is about. Use the exact code from the tool results.
- `severity` — business impact: `critical` when a committed date is at risk or cover is at
  or near zero; `high` when cover is below the reorder point or slippage is material;
  `medium` when it is a forecast or process issue; `low` when no action is needed.
- `root_cause` — the primary driver, not every contributing factor.
- `weeks_of_cover` — take it from `get_sku_status`, do not estimate it from the message.
- `lead_time_impact_days` — the `slippage_days` figure from `get_lead_time`; 0 if none.
- `recommended_action` — one concrete next action, imperative voice. Name the PO or the
  quantity where the tool results give you one.
- `requires_escalation` — true only if the decision sits above a planner.
- `confidence` — 0.0-1.0. Lower it when the message names no SKU, names several, or the
  tool results are ambiguous.
- `rationale` — two sentences citing the specific tool results this decision rests on.

Message:

{message}
