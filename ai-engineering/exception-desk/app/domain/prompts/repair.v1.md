Your previous response was rejected by schema validation.

{validation_error}

Return a corrected object that satisfies the schema exactly. Do not explain the error and
do not apologise — return only the corrected object.

Common causes and the fix:

- A value outside an allowed set (`severity`, `root_cause`): choose the closest allowed
  member. Severity and root cause are enums; there is no "urgent" and no "supplier delay".
- A number sent as a string (`"0.7"`): send it unquoted.
- A boolean sent as a string (`"yes"`): send `true` or `false`.
- A missing field: every field in the schema is required. If the message does not tell you,
  use the tool results; if the tool results do not either, use 0, false, or "unknown".
- `confidence` outside 0.0-1.0: clamp it.

Original message:

{message}
