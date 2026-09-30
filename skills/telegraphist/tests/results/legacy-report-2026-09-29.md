# Telegraphist evaluation

## Status and scope

The approved pilot completed **96/96 generation calls** (12 tasks × 2 model families × 2 repetitions × 2 arms) for **US$0.1293862**, below the **US$10 dedicated-key limit**. All 96 generation metadata audits succeeded. Exact-key ledger cost matches response costs; the dedicated key is disabled and verified. One blinded LLM reviewer assessed all 48 free-text responses. This is not human review.

The primary comparison is a neutral baseline versus the complete frozen `SKILL.md` (frontmatter and examples included). This is an output-style pilot, not a demonstration of universal savings, equivalence, or superiority over Caveman. Neither a one-line concision control nor Caveman is in this pilot.

## Frozen design

- Six English and six Portuguese tasks: six strictly scored JSON tasks and six free-text tasks assessed separately by a blinded LLM reviewer.
- Categories: exact extraction; retry/condition semantics; typed JSON round trip; logical evaluation of a supplied SQL query; missing evidence; operational summaries; temporal scope; requested explanation length; untrusted quoted instructions; deletion safety; uncertainty.
- The SQL task does **not** execute SQL. No generated code is executed or sandbox-tested. Broader code/SQL execution and agent tool-use remain untested.
- Models selected from the live catalog: `openai/gpt-4.1-mini` via `openai` (economical) and `anthropic/claude-sonnet-4.5` via `anthropic` (higher-capacity family).
- `provider.only` pins each route; `allow_fallbacks=false` and `require_parameters=true`. Actual model and provider must match. No alternate route after failure.
- Identical parameters within each model: temperature 0; output ceiling 2,048; no model seed (not jointly supported); no tools; Anthropic reasoning explicitly disabled, OpenAI reasoning unsupported/omitted. Temperature zero is not a determinism guarantee.
- Deterministically shuffled task/model/repetition blocks, randomized arm order inside each block; scheduling seed `20260929`. Each response is an independent request.
- Native usage includes full skill input overhead and message framing. Local tokenizer counts are separate illustrative measurements, not billing measurements.
- No explicit cache directives; record returned cache metadata. Do not assume cold cache from configuration alone.

## Isolation and evidence

`bench.py` uses only Python's standard library and direct HTTPS to OpenRouter. Requests contain a fixed neutral system message, the full skill only in the treatment arm, and the task. It does not load repository `AGENTS.md`, SOUL, memory, plugins, tools, previous answers, or any Hermes profile. Expected answers and rubrics never enter generation payloads.

The external evidence directory retains immutable skill, cases, runner, protocol, catalog/endpoint snapshots and SHA-256 manifest. `attempts.jsonl` is append-only and fsynced: durable start/payload records precede every request, result records retain raw API response, model/provider, generation ID, timestamps, local elapsed seconds, finish reason, usage/cost and deterministic score. Generation metadata is audited separately. Missing cost is unknown, not zero; reasoning tokens are not added twice to completion tokens.

A protocol-valid response is retained even when wrong, fenced instead of JSON, empty, refused or truncated. There is no answer selection or regeneration. `finish_reason=length` is failure, not savings.

### Budget and recovery

A dedicated, verified key has a non-resetting $10 cap, BYOK included and a one-day expiration. Management credentials stay in the local supervisor; the candidate subprocess receives only the child inference credential. Live account credits are checked separately; a $10 allowance does not imply a $10 account balance. No automatic recharge is initiated.

Sequential requests reserve $0.10 of remaining client budget each. Frozen price caps plus input UTF-8 bytes, a conservative framing allowance and the 2,048 output ceiling estimate less than this reservation per request. This is a conservative estimate, not a tokenizer guarantee; the vendor-side key cap is the hard backstop.

**Stricter than the research proposal:** this approved run allows at most 96 generation submissions and **zero automatic retries**, including transport errors. Any unknown charge, unmatched durable start, or routing/protocol error stops continuation. Resume skips all started slots; it cannot replay a completed response or silently resend an uncertain submission. Use one process per artifact directory. A partial malformed JSONL record fails closed and requires an audited manual recovery; never delete failed records to restart.

Disable the dedicated key on completion or unresolved stop; read the exact management record back and reconcile its usage with response costs. An immediate zero ledger value can lag and is not proof of free usage.

## Scoring and limits

`typed-json-v1` requires a whole JSON response with exact keys, list order, scalar types and values. Code fences are invalid, booleans are not integers, duplicate keys and nonfinite numbers are rejected. Key order and insignificant whitespace are allowed. This is a strict output contract, not a semantic quality rating.

Free-text fixtures have frozen 100-point dimension weights (fidelity 50, completeness 30, clarity 20), critical constraints and task-specific requirements. One `gpt-6-astra` reviewer via `openai-codex` evaluated all 48 shuffled opaque-ID responses without model/arm mappings. Pass required all explicit requirements and no critical violation; a numeric score alone did not establish a pass. Style can reveal treatment, so blinding is imperfect. This is one subjective LLM review, not human adjudication or a multi-rater consensus. No separate OpenRouter judge calls were made; reviewer-harness costs are outside the measured generation spend.

Report strict JSON and semantic judgments separately. Combined pass counts and cost per combined pass are descriptive estimates using these two different evaluators, not independently established ground-truth accuracy. Structured-subset cost per pass uses only that subset's costs. Raw generation-time validator records retain `unscored` for free text; the completed judgments live separately in the evidence and are never retroactively substituted into API logs.

Paired aggregate token savings: `1 - sum(skill_tokens) / sum(baseline_tokens)`. Report output-only and total savings separately; retain negative savings. Restrict paired comparisons to complete matched usage and report coverage. Bootstrap task clusters, preserving model/repetition/arm pairs, for descriptive intervals; this small hand-authored suite does not establish a 2-percentage-point non-inferiority margin or population-level equivalence. The pilot cannot justify release claims requiring superiority over the one-line control or Caveman.

## Reproduce offline

From the repository root:

```sh
python3 -m unittest discover -s skills/telegraphist/tests -v
python3 -m py_compile skills/telegraphist/scripts/bench.py
```

The tests exercise blocked randomized scheduling, literal/type fidelity, strict JSON errors, matched payloads, explicit route/reasoning/price controls, budget rejection, resume without duplication, unknown-charge stops, safe network errors, frozen-file tampering and fixture balance. Network calls are replaced by deterministic test transports; synthetic unit-test responses are never benchmark results.

## Freeze and run (paid; explicit authorization required)

Prepare an external directory containing `SKILL.snapshot.md` (copied byte-for-byte from `SKILL.md`), `cases.jsonl`, live catalog/endpoint snapshots and a `config.json`. Config fields: `tasks` (12 fixture objects, exactly matching `cases.jsonl`), `routes` (two distinct model/provider objects), `budget` (`"10"`), `reserve_per_request` (`"0.10"`). Each route declares `model`, routing `provider`, `observed_provider`, optional `returned_models`, mandatory `max_price` (USD per million) and supported `reasoning` controls. The hardened runner verifies the 12-task/two-model design, typed fixture equality, 96 unique slots and a conservative reservation against full payload size, framing and output caps. Missing token accounting or malformed completion metadata fails closed. Observed reservation or cumulative-budget overruns are flagged even on the final request.

```sh
python3 skills/telegraphist/scripts/bench.py freeze --artifacts "$ARTIFACTS" --config "$ARTIFACTS/config.json"
python3 "$ARTIFACTS/bench.snapshot.py" verify --artifacts "$ARTIFACTS"
# Inject TELEGRAPHIST_API_KEY through a protected environment, never shell history.
# Run from the artifact directory; only the dedicated inference key is needed.
python3 "$ARTIFACTS/bench.snapshot.py" run --artifacts "$ARTIFACTS" --max-new 2
# Inspect actual first-pair telemetry before continuing; same command resumes.
python3 "$ARTIFACTS/bench.snapshot.py" run --artifacts "$ARTIFACTS"
```

Provisioning/teardown is intentionally outside the public runner. A user-supplied arbitrary API key is not an acceptable replacement for the approved dedicated capped key. Missing funds, unsupported routes, HTTP errors or unknown usage are blockers, not permission to substitute models or raise caps.

## Deterministic input compaction (separate from the pilot)

```sh
python3 skills/telegraphist/scripts/pack.py < source.json > packed.json
```

**Never use the same source/output path**: shell redirection truncates it before Python reads it. This helper removes insignificant JSON whitespace, preserves exact number lexemes and string bytes, rejects duplicate keys/nonstandard JSON, and caps input at 10 MiB. It appends no newline, including at the size boundary. Escape-heavy strings use a bounded-output byte scanner rather than a memory-amplifying regex; stdout write/flush errors are sanitized. The input cap is not a universal process-memory ceiling.

It does not project records, infer schemas, shorten prose, implement TOON, call a model or demonstrate semantic compression. Native JSON parse/serialize utilities may change number lexemes or large numeric values; do not label their output byte-literal-preserving. In a separate four-record local example, `tiktoken 0.14.0` / `o200k_base` counted **142 tokens before and 82 after** (42.25% reduction), with typed round-trip and idempotence verified. This is one deterministic preprocessing example, not an LLM benchmark or guaranteed reduction for arbitrary input.

## Pilot results

Completed 2026-09-29. Full-skill SHA-256: `9be5d126b5d8fb3d8188e49babcf66950df4baedd533c73ebcbfd88bc22a2f04`.

| Model | Arm | Responses | Strict JSON passes / scored | LLM semantic passes / reviewed | Input tokens | Output tokens | Total tokens | Cost USD | Latency p50 / p95 (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-4.1 Mini | Baseline | 24 | 2 / 12 | 9 / 12 | 2,200 | 1,570 | 3,770 | 0.0033920 | 1.349 / 2.214 |
| GPT-4.1 Mini | Telegraphist | 24 | 4 / 12 | 10 / 12 | 11,080 | 1,177 | 12,257 | 0.0063152 | 1.237 / 2.099 |
| Claude Sonnet 4.5 | Baseline | 24 | 0 / 12 | 9 / 12 | 2,418 | 3,207 | 5,625 | 0.055359 | 3.098 / 9.727 |
| Claude Sonnet 4.5 | Telegraphist | 24 | 0 / 12 | 10 / 12 | 12,570 | 1,774 | 14,344 | 0.064320 | 2.476 / 8.481 |

Both models shortened output but **increased total tokens and billed cost**:

| Model | Complete pairs | Output reduction | Total-token increase | Billed-cost increase | Native skill input overhead per request |
|---|---:|---:|---:|---:|---:|
| GPT-4.1 Mini | 24 / 24 | 25.03% | 225.12% | 86.18% | 370 tokens |
| Claude Sonnet 4.5 | 24 / 24 | 44.68% | 155.00% | 16.19% | 423 tokens |

Zero operational errors, truncations, unknown response costs or missing native usage fields. Reported cache-read, cache-write and reasoning tokens were zero across all responses; native metadata availability is recorded per group. This does not establish provider-internal cache behavior beyond returned accounting.

The strict JSON result is dominated by formatting violations: 42/48 responses failed the whole-response JSON contract. A labeled **post-hoc diagnostic, not a replacement score**, found 40 of those 42 contain a single JSON fence whose interior exactly matches expected typed data. The remaining two include extra prose plus a fenced query result. Do not portray these format failures as evidence that the factual contents were wrong; do not retroactively count fenced outputs as primary passes either.

The LLM reviewer accepted **38/48 free-text answers**, flagged ten requirement/fidelity failures and no violations of the predefined critical criteria. Flags included defining an attempt as only the first try, strengthening a risk warning, changing an untrusted instruction into an allegation, and confirming a restore-verification process rather than verified recoverability. Some judgments are debatable; exact answers, reasons and rubric scores remain auditable. No zero-risk or non-inferiority claim follows.

| Model | Baseline combined passes / 24 | Skill combined passes / 24 | Baseline cost / combined pass USD | Skill cost / combined pass USD |
|---|---:|---:|---:|---:|
| GPT-4.1 Mini | 11 | 14 | 0.00030836 | 0.00045109 |
| Claude Sonnet 4.5 | 9 | 10 | 0.006151 | 0.006432 |

The observed economic release gate fails for this short-task/full-skill regime, including cost per combined pass. Keep the package opt-in; do not advertise net savings or activate it globally based on this pilot. Longer tasks or amortized multi-turn use could differ, but were not tested. The larger study and one-line/Caveman comparisons were not run.

Download the [reviewed pilot evidence](results/pilot-2026-09-29.zip): frozen inputs and manifest, exact API request/response records, selected generation metadata, aggregate metrics, blinded reviews and mappings, accounting reconciliation, local compaction measurements and independent audit. Account-wide balances, credentials, account/session/workspace metadata and local supervisor files are excluded. API logs and historical snapshots remain unchanged; generation metadata is explicitly projected to an audited field allowlist.

### Operational interventions and historical runner

- The initial provisioning helper expected HTTP 200, while successful creation returned 201. Its unused orphan key was disabled and verified before replacement; zero inference calls used the orphan. This did not change model payloads or fixtures.
- Independent review after generation started identified gaps in the reusable runner's defensive validation. The pilot continued with the original frozen runner under the dedicated vendor cap, while a separate worker hardened repository code. `bench.snapshot.py` and the manifest remain unchanged. A post-run audit verified all 96 original request payloads, routes, required token/cost fields, per-request reservations, cumulative cost and matching generation metadata. The hardened repository runner is a separate post-pilot revision, not the software retroactively claimed to have produced these results.
- No response was rerun, repaired or replaced; no prompt/fixture/treatment change occurred after freezing. The current package passed 29 offline tests and an independent code review. Use the current `scripts/bench.py` for future experiments; the older snapshot is historical evidence, not the recommended runner.
