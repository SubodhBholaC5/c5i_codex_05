# Verification record and open questions

## Evidence rules and baseline

Analysis date: **2026-10-30 (Asia/Calcutta)**. Branch: `subodh/training/baseline_repo`. Commit: `fa73052a328525b67815d5654eb40819e245dbc5`. Application root: `learner_day5/`. Baseline commands returned these values; initial `git status --short` was empty. Documentation cites relative source paths with line ranges checked against this checkout. No application source/configuration was edited.

Labels throughout the guides mean:

- **Implementation/configuration:** directly inspected code or fixture; does not by itself mean execution was tested.
- **Test-backed:** an existing test executed and passed.
- **Probe-backed/command output:** a safe local check executed during this analysis.
- **Documentation:** a written claim or intent; conflicts with implementation are called out.
- **Inferred/unresolved:** conclusion needing additional evidence; not presented as established behavior.

## Commands and outcomes

Commands ran from the workspace root unless noted. Numbered reads used `Get-Content` with a line counter. The attachment was read as task instructions, not as repository evidence.

| Command / check | Outcome | Evidence type / confidence |
|---|---|---|
| `git status --short`, `git branch --show-current`, `git rev-parse HEAD`, `git rev-parse --show-toplevel` | Clean initial tree; branch/commit above; workspace is repository root | Command output / confirmed |
| `rg --files --hidden -g '!**/.git/**' -g '!**/.DS_Store' -g '!**/__pycache__/**'` | Application has 11 source Python files, four tests, three existing Markdown docs, README, AGENTS, JSON; no manifest/lockfile/notebook discovered | Command output / confirmed within inventory scope |
| `Get-Content learner_day5/AGENTS.md` and numbered reads of source/tests/docs/data | Read complete application and all existing narrative/fixture inputs | Static inspection / confirmed |
| `rg -n -i 'retry\|timeout\|environ\|getenv\|requests\|http\|import\|cache\|locale' learner_day5/src learner_day5/tests learner_day5/docs` (alternation using `|` in actual regex) | Retry/timeout expectations occur in docs; no executable retry/timeout control or environment-variable reads found in inspected source; import/call inspection distinguishes docs from code | Search plus static inspection / confirmed within specified paths |
| `python --version` | Python 3.14.4 | Command output / confirmed |
| `python -B -m unittest discover -s tests -v` from application root | **12 tests passed**, 0.005 seconds in captured run | Test/command output / confirmed |
| `python -B -m src.benchmark` from application root | Both 100-request modes completed; results below | Command output / confirmed |
| In-memory local Python probes via PowerShell here-string piped to `python -B -` | All expected observations below reproduced; exceptions intentionally caught by probe harness | Command output / confirmed |

The original README's command is `python3 -m unittest discover -s tests -v` ([README:14](../README.md#L14-L14)); this machine was checked using available `python`, with `-B` to prevent bytecode writes. This is not a framework migration. Existing tests use `unittest` ([contract tests:1–5](../tests/test_contract.py#L1-L5)); they were preserved despite the user's separate notebook-refactoring standards, because this task is inspection/documentation only.

## Existing tests and actual coverage

| File / symbols / range | Passed tests | What execution establishes | What it does not establish |
|---|---|---|---|
| [`ContractTests`:5–13](../tests/test_contract.py#L5-L13) | 4 | Default `en`; reject 2,001-character message; reject extra key; shape accepts structurally valid false claim | Full type/size matrix, API status behavior |
| [`FailureTests`:6–14](../tests/test_failures.py#L6-L14) | 2 | Service rejects wrong refund evidence; incomplete model raises `RuntimeError` | Retries, provider refusal handling, mapped 503 at adapter |
| [`SemanticValidationTests`:6–16](../tests/test_semantic_validation.py#L6-L16) | 3 | Wrong refund evidence rejected; matching status accepted; missing record with review true accepted | Free-text truth, duplicate evidence, strict evidence types, no-review missing-source rejection |
| [`ServiceCacheTests`:6–14](../tests/test_service_cache.py#L6-L14) | 3 | Same-user repeat generates once; different users generate twice; disabled reads generate twice | Cache expiry, concurrency, stale source reload, per-request cost semantics |

Coverage statements are limited to the assertions actually present. The test named `test_missing_source_requires_review` exercises acceptance with review true, not rejection with review false ([test:14–16](../tests/test_semantic_validation.py#L14-L16)); the latter branch is only statically established by [validator:13–14](../src/semantic_validation.py#L13-L14).

## Benchmark results

The exact captured local sample follows; repeated timings vary. Code: [`benchmark.run`:9–21](../src/benchmark.py#L9-L21). Currency values are teaching estimates, not charges.

| Metric | Uncached reads | Cached reads |
|---|---:|---:|
| Requests | 100 | 100 |
| p50 milliseconds | 0.0292 | 0.0217 |
| p95 milliseconds | 0.0641 | 0.0314 |
| Total milliseconds | 4.6466 | 2.2424 |
| Model calls | 100 | 1 |
| Cache hits / misses | 0 / 0 | 99 / 1 |
| Estimated input tokens per generation | 40 | 40 |
| Assumed output tokens per generation | 30 | 30 |
| Estimated model cost USD | 0.016 | 0.00016 |

Zero uncached misses means cache reads were bypassed, not that every uncached request was a hit ([service:13](../src/service.py#L13-L13)). Enabled-mode hit rate is a **derived** 99/100 = 99%, not an emitted field. No live-network latency comparison is justified by these numbers.

## Local probes

Probe harness imports `post_reply_draft`, both validators, `DraftService`, `DeterministicModel`, `ReadOnlyOrderLookup`, and `benchmark.run`. It uses only supplied JSON fixtures and local objects. Probe P3's invented refund text is deliberately adversarial input, not a customer fact or an action performed.

| ID / reproducible input | Observed outcome | Code evidence / confidence |
|---|---|---|
| P1: adapter calls with `{'case_id':'C1','customer_message':'Help','locale':'fr','order_id':order}` for `ORD-1042`, `ORD-1043`, `ORD-1044`, `UNKNOWN`, `''` | All status 200 and English. First two review false; processing review true with `delivery_estimate_unavailable`; unknown/empty review true with `order_record_missing` | [model:20–38](../src/model.py#L20-L38), [service:11](../src/service.py#L11-L11), [records:4–6](../data/source_records.json#L4-L6); implementation and probe / confirmed |
| P2: adapter call with `{'case_id':'C1','customer_message':'Help','locale':[]}` | Uncaught `TypeError` from unhashable locale | [validation:15](../src/validation.py#L15-L15), [api:13–14](../src/api.py#L13-L14); implementation and probe / confirmed |
| P3: run shape then evidence validation on `{'draft':'Your refund was issued.','evidence':[{'field':'status','value':'shipped'}],'needs_human_review':False,'review_reasons':[]}` against `{'status':'shipped'}` | Both validators accept contradictory/unsupported prose | [shape:20–29](../src/validation.py#L20-L29), [semantic:3–15](../src/semantic_validation.py#L3-L15); implementation and probe / confirmed |
| P4: new service; payload `{'case_id':'C1','customer_message':'Help','order_id':'ORD-1042'}`; first `create(...,use_cache=False)`, then default `create(...)` | One model call, one cache hit, identical usage, different request IDs | [service:13–23](../src/service.py#L13-L23); implementation and probe / confirmed |
| P5: `run(0)` caught by probe harness | `IndexError: list index out of range` | [benchmark:12–16](../src/benchmark.py#L12-L16); implementation and probe / confirmed |

## Verification limits

- No external SDK execution, API access, credentials, provider billing, authentication, HTTP hosting, database, or queue checks. Those components are not implemented by the core adapter ([api:1–14](../src/api.py#L1-L14)); extension states its incompleteness ([extension:45](live_api_extension.md#L45-L45)).
- No dependency installation, static type checker, formatter, or new test suite was introduced. No test was skipped within the existing discovery run. No live integration test is supplied among the four inspected test files listed above.
- No fixture mutations, stale-file reload experiment, cache-failure injection, threading/load test, arbitrary source-schema corruption, or profiler run. Corresponding statements are static observations or explicitly inferred risks, not runtime guarantees.
- Mermaid diagrams were checked structurally for declared nodes/participants, balanced fences, labels, and call-path consistency. No Mermaid renderer was available through the inspected project; visual rendering is not claimed.
- Source line ranges and local Markdown targets are checked by the documentation validation command. Final results are recorded below after generation. Existing docs retain their original contents, including outdated pointers identified in [F10](key_findings.md).

## Open questions

| Question | Why it matters / evidence already available | Evidence needed to resolve |
|---|---|---|
| What hosts and authenticates this adapter? | [Contract:4,31](feature_contract.md#L31-L31) calls for authenticated scope; [adapter:9](../src/api.py#L9-L9) accepts a supplied/default user | Host/router code and identity middleware; deployment configuration |
| Which failure-policy behaviors belong to the core simulator? | [Policy:7–15](failure_policy.md#L7-L15) exceeds [service:13–22](../src/service.py#L13-L22) | Maintainer decision plus failure-case acceptance tests |
| Must `fr` translate output? | [Validator:14–15](../src/validation.py#L14-L15) accepts it, [templates:21–38](../src/model.py#L21-L38) do not use it | Product locale requirements and expected French fixtures |
| Does usage mean incremental work or original generation? | [Response usage:23](../src/service.py#L23-L23) repeats saved values | Consumer/accounting expectations and cache-hit contract |
| How should sources refresh and caches expire? | [Lookup:7–10](../src/source_tool.py#L7-L10) loads once; [cache:3–12](../src/cache.py#L3-L12) retains memory entries | Intended service lifetime, source update mechanism, retention requirements |
| How should free-text factual claims be verified? | [Evidence validator:3–15](../src/semantic_validation.py#L3-L15) does not inspect prose | Approved claim representation and adversarial acceptance cases |
| Who owns deployment and operational support? | Inventory provides lab files, not operational metadata | Owner/runbook/deployment records |

## Documentation validation

The seven new documents cross-reference each other and the unchanged source/data/test/doc files. Final validation checks local file targets, explicit source line ranges, Markdown fences, Mermaid block counts, and the Git diff to confirm documentation-only changes. This is mechanical link/range and structural validation; it does not prove a sentence is correct or a diagram renders. Manual call-path review supplies the semantic check.

Final executed results: a local Python validator checked **7 documents, 332 local links (including line-range and heading targets), and 6 Mermaid blocks**, with **zero errors** and balanced code fences. `git diff --check` returned no errors; because the new files are untracked, their whitespace was checked separately. Final `git status --short` listed only the seven requested new Markdown files. No source, test, configuration, fixture, or pre-existing documentation changes were reported. Mermaid visual rendering remains unverified.
