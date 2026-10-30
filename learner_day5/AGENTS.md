# Lab working rules
- Read the feature contract and source records before proposing implementation changes.
- Do not invent customer facts, policy, refund eligibility, dates, or order status.
- Use only `data/source_records.json` as factual grounding for this exercise.
- Keep the public endpoint request and response contract stable unless the human approves a change.
- Treat model output as untrusted input. Validate its structure and separately verify factual claims against source records.
- Never execute a suggested action. The lab only drafts text; it does not send messages, issue refunds, or update orders.
- Keep the tool read-only and limited to the named order ID.
- Add or update tests for every behavior change. Do not make broad cleanup edits.
- Explain planned edits and affected files before modifying them; report checks run and limitations afterward.
