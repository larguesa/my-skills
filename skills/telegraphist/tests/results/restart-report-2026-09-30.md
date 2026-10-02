> Historical report, English translation. The status and protocol below describe 2026-09-30, not the current benchmark. [Immutable Portuguese original](https://github.com/larguesa/my-skills/blob/777070e686d3b233d1e4d15ffc1917204849201e/skills/telegraphist/tests/results/restart-report-2026-09-30.md), SHA-256 `2378d1f93a130dae94d5ce28e55244d9a39e08328dcb2a7a07cf9ebb97afd5cd`. Original measurements, identifiers and historical conclusions are unchanged; only prose is translated and relocated evidence links are corrected.

# Telegraphist, evaluation restart

Updated on 2026-09-30. Status: skill and organization corrected; frontier evaluation suite not run. There are no new measurements of savings or correctness.

## Current deliverable

```text
skills/telegraphist/
  SKILL.md
  tests/
    REPORT.md
    scripts/
    results/
```

The skill body uses the prompt supplied by Ricardo, without additional rules, tools, explanations, or links. Only the punctuation between `language` and `no fluff` was changed to a comma. The example and the original-language prompt literal `PARE.` were retained. Minimal metadata remains in the frontmatter.

Old scripts and evidence were relocated, not treated as an evaluation of the new prompt. The `legacy_*` names identify the previous pilot. The legacy runner is limited to the original two-model design; it does not implement the new seven-model matrix or the three-judge panel.

## Model preflight

Source: official OpenRouter API, catalog and endpoints, queried on 2026-09-30 14:18 UTC. Evidence: [model-preflight-2026-09-30.json](model-preflight-2026-09-30.json).

| Requested name | Queried ID | Catalog / endpoints |
|---|---|---|
| Opus 5.5 | `anthropic/claude-opus-5.5` | Listed; endpoint responds |
| GPT-6-Astra | `openai/gpt-6-astra` | Listed; endpoint responds |
| GPT-6.1-Sol | `openai/gpt-6.1-sol` | Listed; endpoint responds |
| GPT-6.1-Luna | `openai/gpt-6.1-luna` | Absent; endpoint not found |
| GLM 4.3-Flash | `z-ai/glm-4.3-flash` | Absent; endpoint not found |
| Gemini 3.8 Flash | `google/gemini-3.8-flash` | Listed; endpoint responds |
| Qwen 3.8 Flash | `qwen/qwen3.8-flash` | Listed; endpoint responds |

Catalog availability does not amount to validated inference. No generation or judging call was submitted at this stage. The endpoint for `typesafe/jev-1.13`, the version used by the existing Jev client, also responded; the Decisions inference route has not yet been probed in this restart. Astra and Opus have their endpoints recorded in the same evidence. Informal names were not used as authorization to select other models.

There are separate entries for GPT-6 Luna, GLM 4.7 Flash, and GLM 5.3 Flash. They do not automatically replace the requested names. Implementation of the evaluation suite awaits confirmation of the two IDs and the cost ceiling, including candidates, judges, and paid probes. The previous pilot's limit was not reused as authorization for a new evaluation suite.

## Requested metrics

| Metric | With skill | Without skill | With / without ratio |
|---|---|---|---|
| Correct answers according to three judges | Pending | Pending | Not calculated |
| Tokens IN | Pending | Pending | Not calculated |
| Tokens OUT | Pending | Pending | Not calculated |
| Tokens CACHED | Pending | Pending | Not calculated |
| Latency | Pending | Pending | Not calculated |
| Cost | Pending | Pending | Not calculated |

Pending means unmeasured, never zero. Old results do not fill this table.

## Proposed contract for the new evaluation suite

This contract is neither frozen nor implemented. Task counts, repetitions, and limits depend on the confirmed budget.

- Direct HTTPS to OpenRouter, without SOUL, memories, AGENTS, plugins, or other skills. The same neutral system, tasks, tools, limits, and settings within each model; only the complete `SKILL.md` differs between arms.
- Include multistep agentic trajectories and long-answer tasks, in addition to short questions. Keep accumulated history, tools, and the final-delivery criterion equivalent. Do not confuse short answers with functional success.
- Freeze tasks, reference answers, criteria, runner, and prompt before the first generation; preserve hashes and randomize pair order. Do not generate new answers to replace failures, empty answers, or truncated answers.
- Requested judges: Jev, GPT-6 Astra, and Opus 5.5. Individual, blinded evaluation, with neither model nor arm revealed; a majority of three determines correctness when all votes are valid. Preserve disagreements. Unavailability of one judge leaves the evaluation incomplete; it does not authorize a two-judge majority.
- Jev uses the Decisions API, not chat. Define the binary question and threshold before execution. Validate route, version, and telemetry in a limited probe. For Astra/Opus, require a structured vote and a reason supported by the reference answer. Since they are also candidates, explicitly state the risk of self-evaluation bias. Deterministic format and execution checks complement, rather than replace, the requested three-judge panel.
- Correctness means fulfilling the task and constraints while preserving necessary content. Brevity earns no points by itself. Do not require an exact word count for every task, or consider a minimal answer correct merely because it is small.
- IN and OUT come from native telemetry; IN includes skill and history, OUT includes reasoning when the provider accounts for it that way. Reasoning is not added again. Publicly visible characters are a separate measure, never a substitute for native tokens.
- Separate cache-read and cache-write; an absent field remains unknown. A declared zero is an observed zero. A ratio with a zero denominator is undefined and accompanied by the absolute totals. Measure first-use and warm-cache conditions separately, without assuming a cold cache because no directive is present.
- End-to-end latency, from submission to the complete response, with median and p95 by arm. For agents, also report total trajectory duration and number of calls. Separate warm-up, errors, and availability attempts from the main matrix.
- Actual candidate and judge costs in separate groups, including probes and potentially billed failures; reconcile response costs with the dedicated key. A funded account and a capped key are separate checks.
- Aggregate ratio = sum(with skill) / sum(without skill), only for complete comparable pairs. Report coverage, differences in correctness rates, failures, and ratios greater than 1. Latency p50/p95 uses the ratio of the corresponding statistics, not a ratio of averages of percentiles. Do not extrapolate a pilot to universal savings or quality equivalence.

## Offline verification

The package tests validate the prompt and folder structure. The legacy tests validate old scripts, not the behavior of the new models.

```sh
python3 -B -m unittest discover -s skills/telegraphist/tests/scripts -v
```

32 offline tests passed: 3 verify the new prompt/layout and 29 cover legacy scripts. The previous baseline also passed the 29 tests. Four deliberate mutations (additional text, removal of the original-language literal `PARE.`, an unauthorized file in the root, and an unauthorized file in `tests/`) were rejected by the validators. Evidence: [full execution](offline-green.txt) and [verifiable summary](offline-validation.json). No offline result amounts to an LLM benchmark.

## Preserved history

- [Previous pilot, evidence](legacy-pilot-2026-09-29.zip), SHA-256 `7e3a0ad0c8c00ac5b6de6f501ae242a57b24cd825cddf10178863f864817ad01`.
- [Original report](legacy-report-2026-09-29.md), SHA-256 `cad46b1fc81d946fca09cdba924c273e3da6d156f2182b9b0b620ed546d00c6b`.

Both retain their original bytes. Paths, protocols, models, and claims in the historical report belong to the previous version. Its content does not demonstrate the result of the rewritten skill, and its commands are not the procedure for this new evaluation suite.
