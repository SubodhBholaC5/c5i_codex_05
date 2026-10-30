# Failure Policy

| Condition | Service behavior | Why |
|---|---|---|
| Invalid request shape or size | 400 response; do not call model | Prevent ambiguous work and control cost |
| Source record missing | Draft acknowledges missing record; human review true | No fabrication |
| Model timeout/transient provider error | One bounded retry for retryable errors, then safe unavailable response | Avoid retry storms and duplicate cost |
| Provider refusal | Preserve refusal state; do not parse as normal draft; request human review | Refusal is not a valid customer reply |
| Incomplete/truncated output | Reject; one bounded retry only if safe; then fail safely | Partial structure is not complete work |
| Invalid JSON/schema | Reject; one bounded repair/retry, then fail safely | Do not silently accept malformed output |
| Well-formed but source-inconsistent evidence | Reject claim, replace with uncertainty or ask for human review; never present unsupported value | Schema proves structure, not truth |
| Tool timeout/not found | Return unknown; do not guess | Tool is the factual source |
| Unknown tool name / invalid arguments | Stop tool execution and report safe error | Prevent unintended side effects |
| Cache unavailable | Continue uncached | Cache is an optimization, not source of truth |
| Cache record stale/version mismatch | Ignore entry and perform fresh retrieval/inference | Fresh source version matters |
