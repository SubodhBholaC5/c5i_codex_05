# Day 5 Lab: Support Reply Drafting Service

This standalone lab builds a small AI feature for drafting customer-support replies. The lab is staged so the instructor can teach the contract before inviting Codex to change code.

## Requirements
- Python 3.10 or newer
- No third-party packages or API key are required for the core lab
- Optional live Responses API extension: install the OpenAI Python SDK and set `OPENAI_API_KEY`; see `docs/live_api_extension.md`

## Start
1. Open this folder in Codex CLI or VS Code.
2. Ask Codex to map the repository without editing, using `learner/prompts.md` Prompt 1.
3. Read `docs/feature_contract.md`, `docs/source_records.json`, and `docs/failure_policy.md` before implementation.
4. Run the baseline checks: `python3 -m unittest discover -s tests -v`
5. Follow the 4-hour stages in `instructor/facilitation_guide.md`.

## Cost / latency activity
The core lab has a deterministic model simulator and a repeatable benchmark so every learner can calculate token-equivalent cost and measure local latency without API charges. It demonstrates application caching: repeated identical requests skip the model call. This is separate from provider-side prompt caching, which discounts repeated prompt prefixes but normally still runs inference. Optional live extension is for API mechanics only; do not compare raw local simulator latency with cloud latency.
