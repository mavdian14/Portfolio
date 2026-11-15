Triage the inbound message below into the required schema.

Base every field on the tool results you gathered in this conversation, not on the wording
of the message. Where the message and the tools disagree, the tools win.

- `sku` — the SKU the message is about. Use the exact code from the tool results.
- `severity` — derive it from `get_sku_status.weeks_of_cover` and `get_lead_time.slippage_days`
  alone, by this rule and no other:

    * `critical` — cover is at or below 0.5 weeks **and** slippage is 20 days or more.
      Both, not either. A part with no cover and a reliable supplier is next week's problem;
      a part with heavy slippage and comfortable cover is one you have time to fix. Only a
      part that is simultaneously out of runway and waiting on a late supplier is critical.
    * `high` — cover below 2.0 weeks, or slippage of 20 days or more.
    * `medium` — neither of the above, but the message raises something a planner should see.
    * `low` — nothing needs doing.

  Do not raise the severity because the message is alarmed, and do not lower it because the
  message is relaxed. If the numbers and the wording disagree, the numbers are right.
- `root_cause` — the primary driver, judged from the message and the tool results together.
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
