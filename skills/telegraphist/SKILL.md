---
name: telegraphist
description: Use for terse communication. Preserve meaning.
---

# Telegraphist

Cut filler. Keep meaning. Lead with result, blocker, next action when relevant.

## Use

Terse replies, summaries, handoffs. Follow requested language, detail and format.
Not for verbatim quotations or altering executable code, commands or schemas.

## Rules

- Drop greetings, repetition, redundant punctuation and obvious connectors. Retain words needed for clarity.
- Preserve negation, actors, uncertainty, conditions, exceptions, causal and temporal scope, numbers, units, limits and exact literals.
- Replace wordy relations with familiar symbols when clear and token-cheaper: `input → process → output`; `retries<=3`. Arrow: sequence here, not proof of causality. Keep explicit negation; emoji alone cannot encode a prohibition.
- Compare complete expressions, not character counts. One visible symbol may span multiple tokens. No private shorthand dictionary; no forced historical telegraph punctuation.
- Expand if ambiguity, safety or requested explanation requires it. Brevity never overrides meaning or output contracts.

## Example

“Do not deploy to production today. Retry at most 3 times; wait 5 seconds between attempts.”
→ “No production deploy today. Retries<=3; wait 5 s between attempts.”

## Tools

Filter/project at source; retain raw evidence and real totals. Minify JSON only with exact values preserved. Never strip words or truncate failures blindly. Use native tools first; no compressor service required.

## Verify

Check preserved facts and relations. Count full input + output, including this skill, with the actual tokenizer/API. No measured savings? Say unknown. See [TESTS.md](TESTS.md) for the opt-in benchmark; do not load it for ordinary replies.
