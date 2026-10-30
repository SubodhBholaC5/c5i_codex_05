# Understand this repository

This lab is like a support agent's writing assistant: look up an order, prepare a suggested reply, check its supporting facts, and hand the draft back. The executable model is a fixed-rule simulator. It does not contact an AI provider. The endpoint adapter returns a status number and a Python dictionary; it does not start a web server. **Evidence: implementation; confirmed** — [`post_reply_draft`, api.py:1–14](../src/api.py#L1-L14), [`generate`, model.py:12–44](../src/model.py#L12-L44).

The intended user is a human support agent. Sending messages and issuing refunds are outside the feature's contract; the inspected execution path only reads order data and returns a draft. **Evidence: documentation and implementation; confirmed** — [feature contract:3–4,25–33](feature_contract.md#L25-L33), [`create`, service.py:9–23](../src/service.py#L9-L23), [lookup:7–14](../src/source_tool.py#L7-L14).

## Start here

1. [Process flow](process_flow.md): plain-language diagrams and worked examples. Start with this if you do not write code.
2. [Current behavior](current_behavior.md): exact rules, inputs, outputs, and boundary cases.
3. [Dependency map](dependency_mapping.md): which part calls which other part.
4. [Key findings](key_findings.md): proven gaps and suggested next steps.
5. [Exceptions and exemptions](exceptions_and_exemptions.md): alternative paths and special treatment.
6. [Verification and open questions](verification_and_open_questions.md): checks performed and remaining unknowns.

## Analysis baseline

| Item | Baseline |
|---|---|
| Date | 2026-10-30, Asia/Calcutta |
| Repository branch | `subodh/training/baseline_repo` |
| Commit | `fa73052a328525b67815d5654eb40819e245dbc5` |
| Application directory | `learner_day5/` |
| Inspected | All 11 Python files in `src/`, four test files, order JSON, repository README, AGENTS.md, and three pre-existing docs |
| Excluded | Git internals, `.DS_Store` metadata, external SDK/provider behavior, deployment outside this checkout |
| Changes | Seven new documentation files; application, configuration, fixtures, and existing docs preserved |

Baseline and inventory are **command-output evidence; confirmed**. See [verification record](verification_and_open_questions.md#commands-and-outcomes) for commands and results. Existing documents are treated as intent, not proof of execution.

## Useful files and their everyday roles

| File / symbol / range | Everyday role | Evidence type / confidence |
|---|---|---|
| [`api.post_reply_draft`:7–14](../src/api.py#L7-L14) | Reception desk: accepts a request and translates two error types into status codes | Implementation / confirmed |
| [`DraftService.create`:9–23](../src/service.py#L9-L23) | Coordinator: runs the steps in order | Implementation / confirmed |
| [`validate_request`, `validate_draft_shape`:3–29](../src/validation.py#L3-L29) | Checks the forms have acceptable fields and sizes | Implementation / confirmed |
| [`ReadOnlyOrderLookup`:4–14](../src/source_tool.py#L4-L14) | Looks up one order in the local address book | Implementation / confirmed |
| [`DeterministicModel.generate`:16–44](../src/model.py#L16-L44) | Chooses a reply template and estimates usage | Implementation / confirmed |
| [`validate_evidence`:3–15](../src/semantic_validation.py#L3-L15) | Compares listed facts with the order record | Implementation / confirmed |
| [`RequestCache`:3–12](../src/cache.py#L3-L12) | Temporary memory for earlier results | Implementation / confirmed |
| [`DraftRequest`, `DraftResponse`:3–19](../src/models.py#L3-L19) | Containers for request and response fields | Implementation / confirmed |
| [`benchmark.run`:8–23](../src/benchmark.py#L8-L23) | Repeats one request to measure the caching example | Implementation / confirmed |
| [Order fixtures:1–9](../data/source_records.json#L1-L9) | The factual source for the exercise | Configuration / confirmed |

## Local setup and execution

The repository README requires Python 3.10+ and says the core lab needs no third-party packages or API key ([README:5–8](../README.md#L5-L8), documentation). Inspected executable imports use the standard library and local modules ([dependency map](dependency_mapping.md#external-dependencies), implementation). No dependency installation was performed. Python 3.14.4 was available; the following commands were executed successfully from `learner_day5/`:

```powershell
cd learner_day5
python -B -m unittest discover -s tests -v
python -B -m src.benchmark
```

`-B` prevents bytecode files being written. To call the adapter directly, use this **illustrative command** from the same directory (the equivalent function call was exercised by the probes):

```powershell
python -B -c "from src.api import post_reply_draft; print(post_reply_draft({'case_id':'C1','customer_message':'Where is my order?','order_id':'ORD-1042'}))"
```

There is no verified HTTP launch command. `POST /v1/reply-drafts` is the documented interface; executable `api.py` supplies a framework-neutral function ([contract:6–14](feature_contract.md#L6-L14), [adapter:1–14](../src/api.py#L1-L14), documentation versus implementation; confirmed).

## Environment and configuration

| Name or setting | Purpose and actual status | Evidence / confidence |
|---|---|---|
| Core environment variables | None read in inspected `src/*.py`; search terms `environ|getenv` | Implementation search / confirmed within this scope |
| `OPENAI_API_KEY` | Credential named only for the optional live extension, not used by the core path | [Extension:3–6](live_api_extension.md#L3-L6), documentation / confirmed |
| `OPENAI_MODEL` | Suggested model selection for optional extension; skeleton uses `MODEL_FROM_ENV` without implementing loading | [Extension:6,32–39](live_api_extension.md#L32-L39), documentation / confirmed |
| Lookup path override | Constructor argument takes precedence over module-relative JSON path; file read on construction | [`__init__`:7–10](../src/source_tool.py#L7-L10), implementation / confirmed |
| Cache, model, lookup | Passed into service constructor; default cache created if supplied cache is falsey | [`__init__`:8](../src/service.py#L8-L8), implementation / confirmed |

## What is established and what is unknown

All 12 existing tests passed. Local probes confirmed order-status branches, missing-order review, English output for `fr`, a malformed-locale exception, unchecked draft prose, cache writes with `use_cache=False`, and zero-request benchmark failure. These observations and their source ranges are recorded in the [verification record](verification_and_open_questions.md). Authentication, hosting, live API execution, and production resilience remain unverified; they are not provided by the inspected adapter ([api.py:1–14](../src/api.py#L1-L14), [extension:45](live_api_extension.md#L45-L45), implementation and documented limitation).
