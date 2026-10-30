# What the code currently does

Read [the illustrated walkthrough](process_flow.md) first for an everyday explanation. Here, **confirmed implementation** means directly visible in code; **test-backed** means an existing test passed; **probe-backed** means an additional local read-only check ran. Details of every executed check are in the [verification record](verification_and_open_questions.md).

## Behavior table

| Workflow | Trigger | Inputs | Decision/processing | Outputs/side effects | Evidence | Verification status |
|---|---|---|---|---|---|---|
| Draft request | Python call to `post_reply_draft` | Payload; optional user ID | Validate, retrieve, check cache, generate if needed, check output | `(200, response dictionary)` or mapped error | [`post_reply_draft`:9–14](../src/api.py#L9-L14), [`create`:9–23](../src/service.py#L9-L23) | Implementation confirmed; success probe-backed |
| Read order | Service has truthy order ID | One order identifier | Dictionary lookup against JSON loaded at construction | Record or `None`; no order write | [`ReadOnlyOrderLookup`:7–14](../src/source_tool.py#L7-L14) | Implementation and probes confirmed |
| Generate draft | No usable saved result | Validated request and record | Fixed templates by order status | Draft, evidence, review flags, estimated usage | [`generate`:16–44](../src/model.py#L16-L44) | Implementation and probes confirmed |
| Verify output | Fresh or cached result | Four output fields; retrieved record | Shape check then evidence comparison | Accepted output or `ContractError` | [shape:20–29](../src/validation.py#L20-L29), [facts:3–15](../src/semantic_validation.py#L3-L15) | Test-backed; prose gap probe-backed |
| Reuse result | Repeat request with cache reads enabled | User/request/source/prompt/model key | Recheck saved output against current in-memory source | Skips model; new request ID; original usage repeated | [key/get/set:6–12](../src/cache.py#L6-L12), [service:12–23](../src/service.py#L12-L23) | Test-backed; usage probe-backed |
| Benchmark | `python -m src.benchmark` | Default 100 requests per mode | Runs uncached then cached; calculates latency and illustrative cost | Console metrics; process-local cache mutation | [`run`, main guard:8–23](../src/benchmark.py#L8-L23) | Executed successfully |

## Request rules

All rows below are **implementation evidence; confirmed** from [`validate_request`:3–18](../src/validation.py#L3-L18). Python dataclass defaults agree with the request defaults ([`DraftRequest`:3–9](../src/models.py#L3-L9)).

| Input | Accepted / default | Boundary or exception |
|---|---|---|
| Body | Python `dict` only | Non-dictionary rejected; extra keys rejected |
| `case_id` | Required string, 1–40 characters | Whitespace-only ID passes because it is not stripped |
| `customer_message` | Required string, at most 2,000 characters | Empty or whitespace-only rejected; original text retained |
| `order_id` | Optional string or `None`, max 40 | Empty string accepted and skips lookup; whitespace string attempts lookup |
| `locale` | `en` or `fr`; absent defaults to `en` | Explicit `None` rejected; list/dict raises uncaught `TypeError` during set membership |
| `conversation_id` | Optional string or `None`, max 80 | Empty string accepted; used in cache identity, not to retrieve history |
| `user_id` | Separate argument, defaults to `demo-user` | No identity validation or authentication in adapter |

User ID handling is supported by [api:9–11](../src/api.py#L9-L11), [cache:6–8](../src/cache.py#L6-L8), and service history scope by the complete [create body:9–23](../src/service.py#L9-L23). Existing tests cover default locale, oversized text, and unknown keys ([contract tests:5–13](../tests/test_contract.py#L5-L13)); the full matrix is not covered by those tests.

## Reply selection: worked examples

These order fixtures are exercise facts, not current real orders. The following branches were exercised locally with `case_id=C1`, `customer_message=Help`, and `locale=fr`; output was English. **Implementation/configuration/probe evidence; confirmed** — [records:4–7](../data/source_records.json#L4-L7), [model:20–38](../src/model.py#L20-L38), [probe record](verification_and_open_questions.md#local-probes).

| Order input | Processing | Result in everyday language |
|---|---|---|
| `ORD-1042` | Status `shipped`, estimate `2026-11-02`, refund false | On its way, expected on the fixture date; review false |
| `ORD-1043` | Status `delivered`, estimate `2026-10-26`, refund true | Shows as delivered; agent can review return options; review false |
| `ORD-1044` | Status `processing`, missing estimate/refund value | Being prepared; review true, reason `delivery_estimate_unavailable` |
| `UNKNOWN` | No matching record | Cannot verify; review true, reason `order_record_missing` |
| Empty order ID | Service skips lookup | Same missing-record reply and review flag |

For existing records, the simulator always adds status evidence, adds delivery evidence when truthy, and adds refund evidence when not `None`. `refund_reason` is not included. The missing-record reply has no evidence. Any status other than shipped/delivered enters the preparation branch, including an unexpected status. **Implementation; confirmed** — [model:20–38](../src/model.py#L20-L38), [allowed evidence fields:7–12](../src/semantic_validation.py#L7-L12). Behavior for additional statuses is static analysis; no modified fixtures were used.

The customer message affects token estimates and cache identity, but its meaning does not select the reply. Locale and conversation ID do not affect the simulator's wording. **Implementation; confirmed** — [entire generation body:16–44](../src/model.py#L16-L44), [cache key:7](../src/cache.py#L7-L7).

## Two checks, with an important limit

The form check requires exactly `draft`, `evidence`, `needs_human_review`, and `review_reasons`; draft must be a string up to 600 characters, evidence a list of `{field, value}` dictionaries, review a boolean, reasons a list of strings. Empty draft/reasons and duplicate evidence items are not rejected. Evidence values have no independent type check. **Implementation; confirmed** — [`validate_draft_shape`:20–29](../src/validation.py#L20-L29).

The factual check accepts only status, estimated delivery, and refund eligibility evidence; each submitted value must compare equal to the source. A known source needs at least one evidence item. No source requires review true. It does not inspect the draft's sentences, demand all relevant fields, enforce reason codes, or require a reason for review. Python equality can also equate `0` and `False`. These are limits of this validator, not claims of full truth verification. **Implementation; confirmed** — [`validate_evidence`:3–15](../src/semantic_validation.py#L3-L15). A probe demonstrated false refund prose with matching status evidence being accepted; mismatch rejection is test-backed ([semantic tests:7–16](../tests/test_semantic_validation.py#L7-L16), [failure test:7–10](../tests/test_failures.py#L7-L10)).

## Cache, versions, and state

The cache key is a SHA-256 digest of sorted JSON containing user ID, case ID, stripped message, order ID, locale, conversation ID, source version, fixed `prompt-v1`, and model class name. Only message edges are normalized. Different users get different keys, but user authentication is the caller's responsibility. No cryptographic access-control guarantee follows from hashing a key. **Implementation/test evidence; confirmed** — [key:6–8](../src/cache.py#L6-L8), [service:12](../src/service.py#L12-L12), [user isolation test:11–12](../tests/test_service_cache.py#L11-L12).

The source file is loaded once per lookup object. Reading the same order on every request reads that in-memory dictionary, not the file again. A version change on disk alone does not refresh an existing object. The dictionary cache has no expiry or eviction in the inspected class; changing model options without changing its class is not represented in the key. `use_cache=False` bypasses reads but still writes successful generations. **Implementation; confirmed** — [source:7–14](../src/source_tool.py#L7-L14), [cache:3–12](../src/cache.py#L3-L12), [service:12–19](../src/service.py#L12-L19). Disabled-read/write behavior was probe-backed.

Importing `src.api` constructs a shared service and loads the JSON. Runtime changes are model call count, cache entries/counters, and a fresh 12-character UUID-derived request ID. No persistent conversation storage, outbound call, or order modification appears in the traced path. **Implementation; confirmed within the inspected path** — [api:7](../src/api.py#L7-L7), [source:7–14](../src/source_tool.py#L7-L14), [model:18](../src/model.py#L18-L18), [service:23](../src/service.py#L23-L23), [cache:5–12](../src/cache.py#L5-L12).

## Failure handling and documented intent

`ContractError` becomes 400, including model-output errors; `RuntimeError` becomes generic 503. A non-completed model status raises `RuntimeError` immediately. Other exceptions can escape, and file loading occurs before the adapter's try block. There is no retry loop or timeout control in inspected `src/*.py` (searched `retry|timeout`, then traced generation and adapter). **Implementation/search; confirmed within this scope** — [service:15–18](../src/service.py#L15-L18), [adapter:7–14](../src/api.py#L7-L14), [source:7–10](../src/source_tool.py#L7-L10).

The [failure policy:7–15](failure_policy.md#L7-L15) describes bounded retries, refusal preservation, uncertainty substitution, and uncached fallback. Those are documented intent: current code rejects incomplete output immediately, maps fact mismatch to 400, does not preserve separate refusal metadata, and has no cache-exception fallback. Both sides are detailed in [findings](key_findings.md) and [exceptions](exceptions_and_exemptions.md).

## Benchmark interpretation

`run` defaults to 100 requests and enabled cache. It measures total service-call latency with `perf_counter`, uses median for p50, and picks sorted index `min(n-1, int(.95*n))` for p95. It estimates input tokens by character count divided by four, assumes 30 output tokens, and uses teaching prices of $1/$4 per million input/output tokens. The simulator instead estimates actual chosen reply length divided by four. These are two different local estimates, not API usage or billing. **Implementation; confirmed** — [benchmark:9–21](../src/benchmark.py#L9-L21), [model:39–44](../src/model.py#L39-L44).

Executed result: 100 uncached model calls versus one cached call and 99 hits; estimated benchmark cost $0.016 versus $0.00016. The benchmark reports hit/miss counts, not a hit-rate field; 99% is derived for this run. Cached response usage repeats the original generation cost, so summing response usage overcounts repeat requests. `run(0)` fails with `IndexError`. **Command-output/implementation; confirmed** — [verification results](verification_and_open_questions.md#benchmark-results), [response usage:23](../src/service.py#L23-L23), [benchmark:15–21](../src/benchmark.py#L15-L21).
