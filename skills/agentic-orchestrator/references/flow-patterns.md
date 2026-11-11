# Flow patterns

Each pattern: when to use it, its shape as a flow-file fragment (fields in flow-spec.md), what goes wrong, and how it ends. Patterns compose: a hierarchical flow whose leaves are producer-verifier loops, a fan-out whose join feeds a judge panel. Start from the simplest one that covers the need; add a pattern only when you can name the problem it solves.

Fragments show only the fields that define each pattern. A real flow also gives every step an `accept` (or `verify`), outputs and limits, and passes the checklist in flow-spec.md §8.

Contents: 1 Single agent + check · 2 Sequential · 3 Router · 4 Fan-out / fan-in · 5 Producer-verifier loop · 6 Hierarchical · 7 Adaptive · 8 Competing hypotheses · 9 Consensus · 10 Judge panel · 11 Debate · 12 Council · 13 Best-of-N · 14 Escalation ladder · 15 Human gate · 16 Blackboard · 17 Handoff chain · 18 Cadence loop · 19 Saga · 20 Choosing

## 1. Single agent with a check (the baseline)
Use when the task is cohesive, fits one context and has few dependencies. Most tasks. Orchestration starts here: one worker, one deterministic check or one reviewer.
```yaml
steps:
  - { id: do, agent: worker, task: ..., verify: { by: check, run: npm test } }
```
Watch out: skipping the check because "it's simple". Exit: accept, or the step's loop limits.

## 2. Sequential pipeline
Use when each stage needs the previous stage's output (spec → implement → review → document). Each stage writes a file the next one reads, so context does not depend on memory.
```yaml
steps:
  - { id: spec,      agent: analyst,  output: out/01-spec.md }
  - { id: build,     agent: builder,  needs: [spec], output: out/02-build.md }
  - { id: review,    agent: reviewer, needs: [build], accept: [no blocking finding], on_fail: { goto: build } }
```
Variant, batches with checkpoints: run a few tasks (3-5), report, wait for the user, continue.
Watch out: a stage that silently fixes the previous one's mistakes (errors hide downstream); one slow stage stalls everything; a chain used where steps are actually independent (check the dependency test). Each stage summary should end with "critical issues for the next stage". Exit: last stage accepted.

## 3. Router
Use when inputs differ in kind and each kind needs a different specialist or path (bug vs feature; legal vs billing question; trivial vs complex).
```yaml
steps:
  - id: classify
    agent: triage
    task: Classify the request as bug, feature or question; one label, with the reason.
    route:
      - { when: label is bug, goto: debug }
      - { when: label is feature, goto: spec }
      - { default: answer }
```
Watch out: forced classification of unclear inputs (allow "unclear → ask the user"); categories that overlap; misroutes nobody detects (log the label and reason; let the specialist bounce a misrouted item back once). Exit: the chosen path's exit.

## 4. Parallel fan-out / fan-in
Use when the work splits into independent units: modules, sub-questions, review dimensions, documents, failing tests in unrelated areas.
```yaml
  - id: review
    agents: [security, performance, correctness]   # one dimension each, no overlap
    task: Review the diff for your dimension only; findings with severity, location, evidence.
    max_parallel: 3
    join: { policy: all, on_missing: mark the review incomplete }
  - { id: merge, agent: lead, needs: [review], task: Deduplicate findings with attribution; keep the higher severity on disagreement. }
```
Split by coverage, never by duplicating the same search; when branches must differ (several drafts, search angles), assign each its distinct direction instead of trusting them to diverge. Don't use it when units are related (one root cause behind several failures), when the work is exploratory, or when branches would edit the same files or a file another branch imports. At the join, wait for every branch, read every result, check for overlapping edits, run the full verification, spot-check (agents make systematic errors). A failed branch is noted and the others continue. The synthesis names agreements and tensions; it never averages conflicting positions; a concern raised independently by several branches is treated as blocking until checked.
Integrating parallel code: land non-overlapping units together and overlapping ones one at a time, re-running the integration checks after each landing; a unit that conflicts goes back to its owner with the conflict and test output.
Watch out: overlap between branches; a failed branch counted as "nothing found"; a join that waits forever (set a timeout and a missing-branch policy); cost is roughly N times one agent. Exit: join policy met, then the merge step.

## 5. Producer-verifier loop
Use when output quality must be checked before moving on and the check can be stated: code with tests, text against a spec, data against a schema. Also called maker-checker or evaluator-optimizer.
```yaml
  - id: implement
    agent: coder
    verify: { by: check, run: npm test }
    loop: { until: tests pass and review has no blocking finding, max: 3, feedback: failing tests and blocking findings, on_stagnation: escalate }
  - id: review
    agent: reviewer          # read-only, fresh context, different model if possible
    needs: [implement]
    accept: [no blocking finding]
    on_fail: { goto: implement }
```
Two-stage review when it matters: spec compliance first (missing, extra, misread), then quality. The same producer fixes its own findings (it has the context) and touches only what was flagged; the verifier re-checks after every fix.
Dual independent verification for high stakes: two isolated reviewers with the same rubric (ideally different models), both must pass, findings merged; each round uses fresh reviewers; cap at about 3 rounds, then escalate. Deterministic checks run before either.
Watch out: a verifier that rubber-stamps (give it criteria and evidence, not the producer's narrative); a producer that edits the tests or the rubric; infinite polishing (cap rounds, usually 2-3). Exit: accept, iteration cap, stagnation.

## 6. Hierarchical (coordinator and specialists)
Use when distinct fronts need distribution, consolidation and coverage control, and one context cannot hold all of it. The coordinator keeps the global view and does not redo each specialist's work.
```yaml
  - { id: api-contract, agent: lead, task: Fix the API types both sides build against., output: out/contract.md }
  - { id: backend,  flow: flows/backend.yaml,  output: out/backend/SUMMARY.md, needs: [api-contract] }   # sub-flow with its own state
  - { id: frontend, flow: flows/frontend.yaml, output: out/frontend/SUMMARY.md, needs: [api-contract] }
  - { id: integrate, agent: lead, needs: [backend, frontend] }
```
Contract down (goal, inputs, limits, output), summary up (status, outputs, evidence, open issues). By default you run each sub-flow yourself, as a nested flow with its own state and log; handing it to a sub-coordinator agent needs `delegation_depth` of 2 or more and subagents that can start agents.
Watch out: depth (keep 1-2 levels; each level loses meaning and adds cost); sub-coordinators inventing scope; a synthesizer that receives names of results instead of the results. Exit: all sub-flows finished and integration accepted.

## 7. Adaptive (dynamic replanning)
Use when the decomposition cannot be known up front (open research, debugging, migrations with surprises). A planner creates or revises steps at run time based on evidence.
```yaml
limits: { max_agent_runs: 25 }
steps:
  - id: plan
    agent: planner
    task: From the evidence so far, propose the next 1-4 steps; never change the objective.
    output: out/plan/round-{attempt}.md
    loop: { max: 3 }                      # the first plan plus two replans
  - id: execute
    agent: lead
    needs: [plan]
    task: Run the steps of the latest plan, each with its own brief, and collect the evidence.
    route:
      - { when: the evidence invalidates the plan, goto: plan }   # back edge = replan
  - { id: report, agent: lead, needs: [execute], task: Answer the objective from the evidence or state what is missing. }
```
Triggers for a replan: a step's result invalidates the plan; low progress (add a specialist or a different approach); low quality (insert a review step). Every replan bumps `version` and logs why.
Watch out: the plan drifting into an easier objective; unbounded growth (cap replans and new steps); a replan that restates the old plan (stagnation). Exit: objective answered, replans exhausted (`plan.loop.max`), or budget.

## 8. Competing hypotheses
Use for diagnosis when several causes are plausible or earlier fixes failed. Counters confirmation bias.
```yaml
  - id: hypothesize
    agent: lead
    task: 2-4 falsifiable hypotheses across categories (logic, data, state, integration, resources, environment); for each, evidence that would confirm and evidence that would refute.
  - id: investigate
    agent: investigator
    for_each: items in out/hypotheses.yaml
    max_parallel: 3
    task: Test one hypothesis; try to refute it first; report confirmed, refuted or inconclusive with confidence and evidence (file:line, command output).
    join: { policy: all, on_missing: treat as inconclusive }
  - { id: arbitrate, agent: lead, needs: [investigate], task: Rank by evidence strength and causal chain; two confirmed related causes may be a compound cause. }
```
Investigators report other leads they notice but do not chase them. Negative results count as findings.
Watch out: hypotheses that cannot fail; ranking by eloquence. Exit: a confirmed cause with a reproduction, or all refuted (replan or report).

## 9. Consensus
Use when several independent attempts at the same question can be compared: a fact, an estimate, a classification, a root cause, a patch.
```yaml
  - id: solve
    agents: [solver_a, solver_b, solver_c]     # different models or framings; identical brief; no peeking
    output: out/solve/{agent}.md
    join: { policy: quorum, min: 2, on_missing: proceed with the valid answers }
  - { id: reconcile, agent: lead, needs: [solve], task: Compare item by item; settle disagreements by sources or tests; keep unsettled items as uncertain. }
```
Strict majority over identical outputs works for exactly comparable answers (failed attempts do not vote). For anything else, agreement is a signal to check, not evidence; several agents repeating one source are one source.
Watch out: correlated errors (same model, same prompt, same retrieved page); voting on facts. Exit: reconciled table with settled and uncertain items.

## 10. Judge panel (multi-agent judging)
Use for subjective or high-stakes quality decisions: comparing versions (A/B), ranking options, grading against a rubric.
```yaml
  - id: judge
    agents: [judge_1, judge_2, judge_3]        # odd number, different families, calibrated
    for_each: items in out/blind/pairs/
    task: Using rubric.md only, pass/fail per criterion and overall preference, with the quoted passage that decided it.
    output: out/judge/{agent}/{item}.json
    join: { policy: all, on_missing: "list as missing, never impute" }
  - id: aggregate
    agent: lead
    needs: [judge]
    task: Unblind; majority per item (no majority counts as split); report agreement, position bias, split items, and whether the margin passes a sign test.
```
Rubric frozen before judging; blind and randomized order; calibration items with known answers; aggregation rule stated in advance. Details: verification-and-judging.md.
Watch out: judges seeing each other's verdicts; producers judging themselves; differences inside the noise reported as wins. Exit: aggregated report.

## 11. Debate (adversarial)
Use to stress a plan, a design or an argument before committing, or to expose the weak points of a claim.
```yaml
  - id: positions
    agents: [advocate, critic]
    task: State your position on the proposal with evidence, without seeing the other side.
    output: out/positions/{agent}.md
  - id: rebuttal                          # 1-2 rounds
    agents: [advocate, critic]
    needs: [positions]
    inputs: [the other side's file in out/positions/]
    task: Answer the other side's strongest point with evidence; update your position where it holds.
    output: out/rebuttal/{agent}.md
  - id: decide
    agent: judge
    needs: [rebuttal]
    task: Decide point by point on the evidence; "unresolved" is allowed.
```
Watch out: persuasion over truth (the judge decides on evidence, important calls go to verification or a human); positions that never update between rounds; endless rounds. Exit: the judge's decision per point.

## 12. Council (advisors for a decision)
Use for a decision, not for checking work: an architecture choice, go/no-go, which option to pursue, a premise worth challenging.
```yaml
  - { id: own_view, agent: lead, task: Write your own position and reasoning before reading anyone else's. }
  - id: advise
    agents: [skeptic, pragmatist, critic]       # distinct lenses, fresh context, compact brief: the question and key facts only
    needs: [own_view]
    task: Answer in under 300 words with Position, Reasoning, Main risk, What would surprise you.
  - id: present
    agent: lead
    needs: [advise]
    task: Show the raw positions, the strongest dissent and any challenged premise; recommend; the user decides.
```
One round by default; no voting. Writing your own view first avoids anchoring on the first advisor you read.
Watch out: advisors given the lead's view (they echo it); a summary that hides the dissent; treating the council as verification. Exit: the user's decision.

## 13. Best-of-N (tournament)
Use when quality varies a lot between attempts and a reliable judge exists: names, designs, prompts, short texts.
```yaml
  - { id: candidates, agents: [gen_1, gen_2, gen_3, gen_4], task: Produce one candidate. }
  - { id: select, agent: judge, needs: [candidates], task: Rank pairwise against the rubric; randomize order; return the winner and why. }
```
Variant, race: first candidate that passes the check wins; stop the others (`join: first_valid`). Cost is N+1 agents. Watch out: a judge biased toward length or position; N too large to review. Exit: a winner, or none passes.

## 14. Escalation ladder (model tiering)
Use only when model selection/substitution is authorized. A user-fixed model and effort must not change through this ladder. When selection is open and most items are easy, try a cheap agent first, escalate on failure to a stronger model, then to a human. Also: a strong model plans, a cheaper one executes, a strong one reviews.
```yaml
  - id: solve
    agent: fast_worker
    verify: { by: check, run: the item's tests }
    on_fail: { escalate: [strong_worker, human] }   # the same step, re-run by the next role; counters kept
```
Watch out: the cheap agent "passing" because the check is weak; counters reset when escalating (they must not). Exit: an accepted result, or a human decision.

## 15. Human gate
Use before external effects (push, publish, send, deploy, pay), before scope or criteria changes, and where judgment is the user's (legal, product, taste).
```yaml
gates:
  - before: any external effect
steps:
  - id: approve
    human: Show the diff, test output and last review; ask to approve, request changes, or stop.
    needs: [review]
    route:                                   # route every option the question offers
      - { when: user requests changes, goto: implement }
      - { when: user says stop, end: cancelled }
      - { when: user explicitly approves, end: done }
```
Consult current authorization first: a design-only approval is not execution permission, but a request explicitly naming execution already covers it. A covered gate is recorded as decided; ask only about uncovered choices. Ask one question at a time, with the options and a recommendation, answerable without reading the logs. Watch out: notification floods; gates that approve by timeout. Exit: the human's recorded decision.

## 16. Blackboard
Use for open investigation where each finding can unlock another and the order cannot be planned: incident analysis, literature review, security audit.
```yaml
  - id: investigate
    agents: [logs_analyst, db_analyst, network_analyst]
    channel: { blackboard: out/board/ }   # one attributed file per contributor; controller owns the canonical board/log
    task: Read the board first; add new findings with evidence and build on others' without repeating them.
    loop: { until: a round adds no new finding, max: 4 }
    join: { policy: all, on_missing: note the silent analyst }
```
After each round the orchestrator reads the board and decides who looks at what next. See communication.md.
Watch out: overwrites (append-only or one file per contributor), guesses treated as facts, no stopping rule. Exit: a round with no new finding, the round limit, or the question answered.

## 17. Handoff chain
Use when control should move to whichever specialist fits the current state (support triage → billing → refunds), or across sessions and machines.
```yaml
  - id: support
    agent: triage
    channel: handoff                     # ends with a result, or a handoff packet naming the next owner
    task: Resolve the request, or hand it to billing or refunds with a packet (state, done, tried, next action).
    loop: { max: 4 }                     # bounds the chain of hops
```
Each hop is dispatched by the orchestrator to the named owner and logged; the receiver confirms. Watch out: ping-pong between agents (two unresolved handoffs in a row escalate); "see conversation above" instead of a packet; duplicate tasks from repeated handoffs. Exit: an agent completes instead of handing off.

## 18. Cadence loop
Use for ongoing work discovered on a schedule: triage of new issues, watching CI, daily summaries. It is a goal loop wrapped in a trigger.
```yaml
trigger: { schedule: every 1h }
limits: { max_agent_runs: 10, max_iterations: 3 }
steps:
  - id: triage
    agent: triager
    task: List new actionable items, skipping items another loop is acting on; check the budget first.
    output: out/runs/{run}/queue.md
    route:
      - { when: the queue is empty, end: done }     # cheap exit, no agents spawned
  - id: handle
    agent: worker
    needs: [triage]
    for_each: items in out/runs/{run}/queue.md
    max_parallel: 2
    task: Propose a fix for one item (report-only until autonomy is earned).
    join: { policy: all, on_missing: leave the item for the next run }
```
On each run: check the budget, triage cheaply, exit early when nothing is actionable, run a bounded goal flow per item, append one line to the run log. Start in report-only mode and earn autonomy with evidence (loops-and-graphs.md §4). Watch out: the loop reacting to its own changes; growing cost on idle runs; several loops acting on the same item (each loop marks what it is acting on; others skip). Exit per run: queue empty, budget, or kill switch.

## 19. Saga (compensations)
Use when a flow makes several external changes that must succeed together (create resources, then configure, then notify).
```yaml
  - id: create_bucket
    agent: ops
    effects: external
    gate: before
    undo: delete the bucket by the id recorded in out/create_bucket.md
    task: Create the storage bucket and record its id.
  - id: configure
    agent: ops
    needs: [create_bucket]
    effects: external
    gate: before
    undo: restore the configuration saved in out/config-before.json
```
Every external effect records target, current authorization, reconciliation and compensation before acting; explicitly authorized irreversible effects may use `undo: none`. On failure, apply only already-authorized compensations in reverse order. Record started/confirmed receipts and reconcile unknown outcomes before retrying; do not promise exactly-once transport. Watch out: effects with no undo (ask before them); retries that duplicate effects. Exit: all effects done, or all compensated and reported.

## 20. Choosing

Scale the flow to the task before choosing patterns. Rate it by what it touches (files, people, systems), whether it adds a dependency or changes a contract, and how ambiguous the design is; take the highest: trivial (do + check), standard (spec → do → review), large (research → plan → do → review → verify, with gates after the plan and before any external effect). Anything touching security, money, personal data or a public interface is at least standard.

| Need | Start with |
|---|---|
| One coherent task | 1 single agent + check |
| Output of one stage feeds the next | 2 sequential |
| Inputs of different kinds | 3 router |
| Independent units of work | 4 fan-out / fan-in |
| Quality must be checked and fixed | 5 producer-verifier |
| Several large fronts | 6 hierarchical |
| Plan cannot be known up front | 7 adaptive |
| Unknown cause, several suspects | 8 competing hypotheses |
| Establish a fact or answer reliably | 9 consensus (by evidence) |
| Subjective quality decision | 10 judge panel |
| Stress-test a proposal | 11 debate |
| Make a decision with several perspectives | 12 council |
| Quality varies by attempt | 13 best-of-N |
| Mostly easy items, some hard | 14 escalation ladder |
| External effects or user judgment | 15 human gate |
| Findings unlock findings | 16 blackboard |
| Control moves between specialists | 17 handoff chain |
| Recurring work on a schedule | 18 cadence loop |
| Several external changes that must hold together | 19 saga |
