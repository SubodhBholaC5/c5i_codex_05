# Feature Contract: Support Reply Drafting

## Purpose
Draft a concise, empathetic support reply using an authenticated support case and a read-only order lookup. The result is a draft for a human support agent. It is never sent automatically.

## Request
`POST /v1/reply-drafts`

JSON fields:
- `case_id`: non-empty string, 1–40 characters.
- `customer_message`: non-empty string, maximum 2,000 characters.
- `order_id`: optional string, maximum 40 characters. If present, it is the only order identifier the tool may look up.
- `locale`: optional enum `en`, `fr`; defaults to `en`.
- `conversation_id`: optional opaque string. It is a correlation key, not permission to load arbitrary prior content.

## Response
- `case_id`: echoed from the validated request.
- `draft`: a string, maximum 600 characters.
- `evidence`: list of source-backed claims with `field` and `value`.
- `needs_human_review`: boolean.
- `review_reasons`: list of strings.
- `usage`: input token count, output token count and estimated cost in USD for the simulator.
- `request_id`: opaque correlation ID.

## Business constraints
1. Use the exact order record returned for the request's order ID; do not infer one customer/order from another.
2. State order status, delivery date and refund eligibility only when present in the source record.
3. If required evidence is missing, do not fabricate a specific answer. Say what is unknown and mark human review.
4. The model may recommend escalation, but refund issuance or message sending is outside the feature.
5. A response can pass JSON/schema validation and still be factually wrong. Validate every evidence claim against retrieved source data.
6. Keep conversation state scoped to the authenticated user and conversation. This lab's core endpoint is stateless and does not persist history.
7. Never put secrets or unrelated personal data in prompts, logs, cache keys or telemetry.
8. Cache only a normalized request plus versioned source data and prompt/model configuration. Do not cache across different users or mutable order versions. For this exercise, cache is process-local and keyed by exact request data plus source record version.

## Definition of done
- Request validation rejects malformed or oversized input with a useful 4xx error.
- Output schema is enforced and parsed into a typed model.
- Semantic evidence validation rejects an incorrect value even when the schema is valid.
- Tool calls validate arguments, allow-list the tool name, and only perform a read-only lookup.
- Failure cases return safe, predictable behavior without exposing stack traces or making up facts.
- Tests include normal, missing-data, malformed, adversarial, and wrong-but-well-formed output cases.
- Benchmark reports p50/p95 latency, model-call count, token estimates, estimated cost, and cache hit rate before/after application caching.
