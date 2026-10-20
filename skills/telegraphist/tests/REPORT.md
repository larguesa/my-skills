# Telegraphist test report

Purpose: economical communication with the agent, through telegraphic replies that keep the requested facts. Measured so far: shorter replies in an interrupted, unjudged sample; total tokens and cost were higher in that sample, and no test has checked that the current prompt keeps the needed information.

## Measurements

| Study | Prompt tested | Coverage | Result |
|---|---|---|---|
| Pilot, 2026-09-29 | [previous prompt](https://github.com/larguesa/my-skills/blob/5b958566d4b18905708bb18814182ee79ddcf6bb/skills/telegraphist/SKILL.md), not the current one | 96 of 96 generations; GPT-4.1 Mini and Claude Sonnet 4.5; 12 short tasks; one LLM reviewer | Output tokens -25.03% and -44.68%; total tokens +225.12% and +155.00%; billed cost +86.18% and +16.19% |
| Frontier, 2026-10-02 | current `SKILL.md` body | stopped after 67 of 336 episodes; 1 of 112 baseline/skill pairs judged | No correctness result: the only judged pair is empty in both arms (Qwen spent all 8,192 tokens on reasoning) |

The frontier run stopped when OpenRouter rejected one concurrent request for its in-flight budget reservation; the frozen no-retry rule halted the batch, so 269 episodes never started and judges finished 3 episodes (9 votes).

Unjudged token telemetry from that run. In 21 pairs both arms have a complete episode record (`valid_terminal`, first repetition only); a complete record is not a usable answer. In 3 of those pairs both arms stopped at the 8,192-token limit: Qwen on `long_deliverable_pt` returned an empty answer in each arm, and Gemini on `long_deliverable_en` and `long_deliverable_pt` returned truncated answers in each arm. The table uses the other 18 pairs, where both arms finished normally and passed the deterministic gates (format, word range, record reads); 7 models, 7 of 8 tasks:

| Measure | Baseline | Skill | Change |
|---|---:|---:|---:|
| Visible words in the answer | 4,607 | 2,727 | -40.8% |
| Output tokens, reasoning included | 29,813 | 21,662 | -27.3% (lower in 14 of 18 pairs) |
| Input tokens | 35,693 | 53,474 | +49.8% (higher in 18 of 18) |
| Total tokens, input plus output | 65,506 | 75,136 | +14.7% (lower in 3 of 18 pairs) |
| Billed cost, USD | 0.509252 | 0.517532 | +1.6% (lower in 8 of 18 pairs) |

No judge checked whether the shorter answers kept the required information.

## What follows

- In these 18 pairs the answers were shorter, and total tokens were higher in 15. The instruction adds 248 to 387 input tokens to every request, depending on the tokenizer, and agentic episodes resend it on every tool call.
- Not tested: information preservation of the current prompt, long multi-turn sessions, prompt caching, the second repetition.

## Reproduce

Offline runner and package checks, from the repository root (they test code, not model behavior):

```sh
python3 -B -m unittest discover -s skills/telegraphist/tests/scripts -v
```

Frontier telemetry table, from the evidence kept in history:

```sh
git show a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626:skills/telegraphist/tests/results/frontier-2026-10-02/events.jsonl | python3 -I -c '
import json, sys
ep = {r["slot"]: r for r in map(json.loads, sys.stdin)
      if r.get("event") == "episode_terminal" and r.get("phase") == "candidate" and r.get("valid_terminal") is True}
pairs = [(ep[s], ep[s.replace("|baseline", "|skill")]) for s in ep
         if s.endswith("|baseline") and s.replace("|baseline", "|skill") in ep]
done = [p for p in pairs if all(r["finish_reason"] == "stop" and (r["final"] or "").strip() for r in p)]
print("complete records", len(pairs), "normal non-empty answers in both arms", len(done))
for k in ("in", "out", "cost"):
    b, t = (sum(float(p[i]["totals"][k]) for p in done) for i in (0, 1))
    print(k, round(b, 6), round(t, 6), f"{t / b - 1:+.1%}")
'
```

`frontier_bench.py` is the runner of the stopped study, kept for a new one; its `freeze` command snapshots the current `SKILL.md`.

## History

Evidence removed from the tree on 2026-10-20 stays at commit `a01d780`:

- [Frontier evidence](https://github.com/larguesa/my-skills/tree/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/results/frontier-2026-10-02): protocol, every request and answer, votes, accounting (USD 1.860233450, reconciled with the dedicated key).
- [Full previous report](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/REPORT.md), with per-stratum tables.
- [Pilot report](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/results/legacy-report-2026-09-29.md) and [pilot evidence ZIP](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/results/legacy-pilot-2026-09-29.zip).
- [Restart report](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/results/restart-report-2026-09-30.md), model preflight, spending policy and offline test logs in the same [results folder](https://github.com/larguesa/my-skills/tree/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/results).
- The JSON minifier `legacy_pack.py`, unused by the current skill, is in the [scripts folder](https://github.com/larguesa/my-skills/tree/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/telegraphist/tests/scripts). `legacy_bench.py`, the pilot runner, stays in the tree because `frontier_bench.py` imports its helpers.
