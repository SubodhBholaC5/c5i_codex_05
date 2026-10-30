# Optional Live Responses API Extension

This is an instructor-led extension. It requires an API account, an enabled model and a current official OpenAI Python SDK. Keep the secret in `OPENAI_API_KEY`; never store it in a source file, `.env` committed to Git, prompt, screenshot or notebook output. Current API behavior and model access can change; check official API documentation before class.

## Install / configure
Use a disposable virtual environment. Install the current `openai` package per the official SDK instructions and set `OPENAI_API_KEY` in the shell environment. Select `OPENAI_MODEL` to an account-enabled model; do not hard-code a stale model name in learner materials.

## Teaching sequence
1. Use `client.responses.parse(...)` with a Pydantic response model for `draft`, evidence, review flag and review reasons.
2. Inspect response status and refusal/incomplete cases; do not assume every response contains parsed content.
3. Define only `lookup_order` as a function tool, with strict JSON arguments. The model emits a proposed call; local application code validates the exact order ID and executes the read-only lookup.
4. Return tool output under its matching `call_id`, then request the final response.
5. Run local semantic evidence validation against the retrieved record before returning the draft.
6. Observe actual usage fields from the response, then calculate estimated cost using the current rate card outside the prompt.
7. Show typed streaming events only if there is time. Do not publish partial claims before final semantic validation.

## Skeleton (adapt to current SDK version)
```python
from pydantic import BaseModel
from openai import OpenAI

class Evidence(BaseModel):
    field: str
    value: str | bool | None

class ReplyDraft(BaseModel):
    draft: str
    evidence: list[Evidence]
    needs_human_review: bool
    review_reasons: list[str]

client = OpenAI()
response = client.responses.parse(
    model=MODEL_FROM_ENV,
    input=[
      {"role": "system", "content": "Draft a concise support reply. Use only supplied source facts. Never promise a refund."},
      {"role": "user", "content": "Customer asks where order ORD-1042 is. Source record: status shipped; delivery estimate 2026-11-02; refund_eligible false."}
    ],
    text_format=ReplyDraft,
)
# Production code must inspect status/refusal, validate parsed output,
# compare every evidence claim with source records, and handle API errors.
```

The snippet demonstrates typed structured output only. It intentionally does not implement a complete tool loop, authentication, retries, observability, or production error handling; use the official Responses API function-calling and Structured Outputs guides for current exact syntax.
