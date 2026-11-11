# Verification, judging and consensus

A producer's confidence is not an acceptance criterion. This file covers how results are checked: verification layers, single verifiers, judge panels, consensus among independent agents, and debate.

Contents: 1 Layers · 2 Independent verifier · 3 Judge panels · 4 Consensus · 5 Debate · 6 Verdict formats · 7 Pitfalls

## 1. Layers

First establish the real terminal result for this attempt; a launch receipt is not completion (execution-contract.md). Then check in this order and stop at the first unresolved failure; cheap checks first.

1. **Integrity**: required fields, links, versions and coverage are complete; the output is where the contract says.
2. **Deterministic checks**: tests, builds, linters, schema validation, counts, diffs. Strong for what they define, silent about everything else: a valid format does not prove facts, a passing test does not prove safety.
3. **Content against criteria**: an independent agent (or panel) compares the result with the approved criteria.
4. **Contestation**: an agent tries to refute: contradictions, edge cases, alternative explanations.
5. **Human decision**: relevant ambiguity, or an action outside the current authorization.

Test the criteria too: can they reject a known-bad example? For a fix, show the defective case failing before and passing after. For research, state in advance which observations would contradict the hypothesis.

**Missing evidence means unknown, never pass.** Zero checks returned, a check that did not run, or a green status that is not a test result are "unknown"; the step is not accepted on them. The checker should measure something the producer cannot fake: it re-runs the tests itself, reads the sources itself, and ignores the producer's claims about them.

**A guard you never saw fire is not proven.** Before relying on a verifier or a guard rule, try it both ways: a seeded defect it must reject and a clean control it must pass. A verifier that rejects the clean control is broken too.

## 2. Independent verifier

- Give the verifier the spec, the artifact and the sources; not the producer's narrative of why it is right.
- Fresh context; ideally a different model family from the producer, to reduce shared blind spots. Separate context reduces anchoring but does not guarantee independent errors.
- Read-only: a verifier reports, it does not fix. Fixing turns it into a second producer nobody verifies.
- Review against the spec before reviewing quality: first missing work, extra work nobody asked for, and misread requirements; only then style, structure and maintainability. Polishing something that does the wrong thing wastes a round.
- "Requirements met" needs a line-by-line check against the requirements, not only passing tests. Before any claim of success: name the check that proves it, run it fresh and in full, read its output, then claim.
- Severity drives the next move: blocking findings send the step back with feedback; minor ones are logged and reported.
- Fail closed: a verifier that crashed, could not read the files, or whose gate was unavailable never yields "approved"; record the absence and retry once or ask a human. Its unparseable answer is not a reject either: a reject is a result, not an error, and a missing verdict is neither.
- Uncertainty never clears a blocker. For each unique blocking finding, a skeptic may try to refute it; only a confident, evidenced refutation removes it, an uncertain one keeps it blocking.
- Trust a verifier's approvals only after it has rejected something: a seeded defect, a known-bad sample, a real failure.

## 3. Judge panels

Use a panel when the quality judgment is subjective or high-stakes (writing, design, ranking options, A/B comparisons).

- **Rubric first, frozen before judging.** Prefer pass/fail per criterion over 1-10 scales; scales drift and invite middle scores. One criterion per failure mode that matters, each with a PASS and a FAIL example in the judge's brief.
- **Blind and randomized.** Hide which version is which and who produced it; randomize position per item; keep the key where judges cannot read it.
- **Independent.** Identical brief to every judge; judges never see each other's verdicts. Use different model families when possible; never let a producer judge its own output.
- **Calibrate.** Before the real run, give each judge a few items with a known answer (clearly better, clearly worse, equal). A judge that fails them is advisory only or replaced (with the user's approval); never lower the bar to keep it.
- **Aggregate with a stated rule**: majority for pass/fail or preference, median for scores. Report agreement (how often judges coincide), per-judge position bias (how often the first item won), and the split items with each judge's reason.
- **Odd panel sizes** (3 or 5) avoid ties in two-way verdicts (pass/fail, X/Y). When "tie" is also an option, an item can have no majority: count it as split. More judges reduce noise, not shared bias.
- **Is the difference real?** For A/B preferences, run a two-sided sign test on the items with a winner and report a preference only if it passes (with 12 items, 10-2 or better at 5%); otherwise report "no detectable difference".
- **Noise.** A difference inside the observed disagreement between judges or reruns is not a result. Re-run with variation, or report "no detectable difference". "Rerun" is not a verdict.
- For decisions that gate a release or a merge, if two independent evaluations disagree, treat it as not passed and escalate, instead of explaining the disagreement away.

## 4. Consensus

Consensus is for questions where several independent attempts can be compared: facts to establish, answers to a problem, estimates, root causes.

1. Broadcast the identical brief to N independent solvers (different models, prompts or sources raise independence). They do not see each other.
2. Compare the answers item by item. Where they agree on verifiable items, still check the evidence: several agents repeating one source are one source.
3. Where they disagree, settle by material that can be checked (sources, tests, reproductions), in a targeted step: "claim X: A says p citing s1, B says q citing s2; decide by the sources".
4. If no source is decisive, keep the item as uncertain, with both positions. Do not vote it into a fact.

Majority over identical outputs works when answers can be compared exactly (a number, a label, a patch): run N isolated attempts, failed attempts do not vote, a strict majority wins, and "no change needed" is a valid winner. Without a strict majority, fall back to evidence or escalate.

**Agreement is not evidence.** Voting is fine for preferences and for picking among valid options; it is not a way to establish truth. Correlated errors (same training data, same retrieved page, same prompt) produce confident, wrong consensus.

Weighing conflicting evidence: quality over quantity; primary sources over secondary; independent corroboration over repetition; sources closer in time to the fact over later ones. Outcomes: resolved, probable, unresolved, or both partly right. Evidence that should exist but does not is itself evidence. A search is exhaustive enough when further searching would only confirm what is known, and the report says what was covered.

## 5. Debate

Two or more agents argue opposing positions for a bounded number of rounds; a separate judge decides by the evidence presented. Useful to expose weak points of a plan or an argument before committing. Rules: one or two rounds; each claim needs evidence, not rhetoric; the judge sees the arguments and the sources, decides per point, and may declare "unresolved". Risk: persuasion beats truth; a fluent wrong argument can win, which is why the judge decides on evidence and the final call on important matters stays with a verification step or a human.

## 6. Verdict formats

Ask for verdicts in a fixed shape so they can be aggregated:

```yaml
item: pair-07
verdict: X            # X | Y | tie, or pass | fail, or supported | refuted | inconclusive
criteria:
  - { name: factual accuracy, verdict: pass, evidence: "quote or file:line" }
  - { name: concision, verdict: fail, evidence: "paragraph 3 repeats paragraph 1" }
confidence: medium    # high | medium | low, with what would change it
top_fix: Remove the repeated paragraph.   # exactly one, when the verdict is negative
```

Findings from several reviewers, merged (key them on the evidence: location plus the quoted snippet): same location and same issue → one finding, credit all; same location, different issue → keep both, tag co-located; same issue in several places → cross-reference; severities disagree → keep the higher and note it; fixes disagree → keep both with attribution.

## 7. Pitfalls

| Pitfall | Correction |
|---|---|
| Reviewer endorses the producer | Own criteria, separate context, evidence required, read-only |
| Producer edits tests or rubric to pass | Criteria owned by the orchestrator; changes need user approval |
| Panel of the same model with the same prompt | Vary models or framing; measure agreement |
| Position or length bias | Randomize order; criteria about content, not length |
| "Nothing found" from a failed search | Separate access failure from absence of findings |
| Unparseable verdict counted as fail | Retry once or escalate; never impute |
| Majority vote on a factual dispute | Settle by sources or keep as uncertain |
