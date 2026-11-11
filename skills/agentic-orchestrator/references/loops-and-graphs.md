# Loop engineering and graph engineering

Two complementary dimensions of the same flow. A **loop** repeats work until a verifiable condition or an exit; a **graph** says who acts, in what order, and what depends on what. A graph node can contain a loop; a loop can wrap a whole sub-graph. Neither excludes parallelism.

Contents: 1 Loops · 2 Stop conditions · 3 Feedback · 4 Loop types · 5 Graphs · 6 Decomposition · 7 Ownership and convergence · 8 Invalidation and resume · 9 Hierarchy

## 1. Loops

The basic cycle: **act → observe → verify → record → decide.** Every new attempt must answer what changed since the last one; repeating the same request is not iteration.

A loop is fully specified by:

| Part | Question it answers |
|---|---|
| Goal | What does "done" look like, in checkable terms? |
| Verifier | Who or what decides pass or fail? Deterministic checks first, then an independent agent, then a human. |
| Feedback | What goes back to the producer after a failure? |
| Memory | What carries across attempts: the attempt log, approaches already discarded, the best result so far. |
| Bounds | Maximum attempts, time, cost; local bounds inside the global budget. |
| Stagnation rule | How to tell that attempts stopped producing information. |
| Exits | Accept, limit, stagnation, block (next section). |
| Escalation | Who gets the problem when the loop exits without accepting. |

In a flow file this is the `loop` field of a step (`until`, `max`, `feedback`, `on_stagnation`) plus the step's `verify` and `accept` (see flow-spec.md).

Write the goal as something an outsider could check with one command or one look, plus its boundaries: what the agent must not do to get there (delete or weaken tests, lower coverage, narrow the question, drop hard cases). Without boundaries a loop learns to game its check. Settle ambiguities before the loop starts; agents rarely stop to ask mid-run.

A loop worth automating repeats often, has a verification that can run without a person, fits the budget, and lets the agent act and observe the result. If one of these fails, keep a human in the loop. Grow it in stages: run it once by hand, then as a flow with subagents, then on a schedule.

## 2. Stop conditions

Plan four exits for every loop:

- **Accept**: criteria met, evidence linked, coverage stated.
- **Limit**: attempts, time or cost exhausted. Never relabel this as success.
- **Stagnation**: attempts keep coming without new information or measurable progress.
- **Block**: an input, permission or capability is missing; more attempts cannot fix it.

Stagnation signals: the same failure signature twice in a row; a fix that undoes a previous fix (oscillation); an empty or cosmetic diff; a score that does not improve over the last two attempts; a "new" plan that restates an old one. A threshold like "two equivalent failures" is a local choice, not a law; write the one you use in `limits.stagnation`.

Keep an attempt ledger per step (in the state or the log): attempt number, action taken, outcome (success, failure, no-op), normalized error, cost. Countable breaker rules over it, checked from the most specific:

| Rule | Fires when (example thresholds) |
|---|---|
| Stagnation | the same normalized error 2-3 times in a row |
| Frustration | a similar action repeated 3 times, even with different errors |
| No progress | 5 consecutive failures of any kind |
| Budget | the step's or the flow's cost or run cap reached |
| Iteration cap | `loop.max` reached |

Normalize errors before comparing them (strip timestamps, paths, ids, line numbers), or every failure looks new. A rule that fires means escalate, not "try harder": never widen a threshold to keep going, never trim the ledger to hide repeats. A guard whose configuration is unclear should refuse to start rather than silently stop guarding.

Also stop on a plateau (after the third attempt, no gain over the last two) and on cost drift (each attempt costing more for the same result). To recover from a stuck loop: freeze it, audit what happened, shrink the problem to the failing unit, and replay with explicit acceptance criteria. Use fresh context for a genuinely independent phase. Resume an interrupted bounded phase by exact session when valid evidence and remaining budget support it; do not restart discovery merely because a local invocation ended.

Before every new attempt, give the producer a compact context block instead of the whole history: goal, progress so far, "already tried, do not repeat", failure patterns with counts, the last error (trimmed), and how many attempts remain.

Practitioner defaults (opinion, adjust per task): review or QA loops capped at 2 rounds before escalating; the same blocker type twice in a chain goes to a human; two unresolved handoffs in a row escalate; never send work back to a stage that already handled the same issue. Severity sets the move: blocking findings loop back, minor ones are logged and reported, critical ones (security, data loss, scope) stop and escalate.

For code, gate the loop on evidence that can fail: new tests must fail first for the right reason, then pass without any test having been edited to make them pass. For debugging: one written hypothesis, the smallest change, one variable at a time; a failed fix means a new hypothesis, not a stacked fix; after about three failed fixes, stop and question the approach with the user.

Retries and waiting: retry only transient failures, a few times with growing pauses; items that still fail go to a human queue (dead letter) with their error, and only the failed items are retried later. Make steps idempotent so a retry cannot duplicate an effect. When waiting for something external, poll the real condition (a file, a status, a count) with a timeout, not a fixed sleep. Before external effects, record target, authorization and reconciliation; state compensation or explicitly authorized irreversibility. Compensation also needs authority. A later failure does not authorize new deletions or blind reversal.

Counters belong to the task, not to the agent: switching to another agent or model does not reset them. When a whole class of tasks keeps failing the same way (a broken environment, an expired credential), pause that class (a circuit breaker) instead of letting every task burn its retries. A stop must also suspend the steps that depend on the stopped one.

## 3. Feedback

"Rejected" is a verdict, not guidance. Feedback after a failed attempt carries:

1. The criterion that failed, as written in `accept`.
2. What was observed, with the location of the evidence (test name and output, file and line, source).
3. Why it matters (impact).
4. What was already tried and discarded, so the next attempt does not repeat it.

Give the producer the verifier's findings, not the verifier's whole transcript. Keep the acceptance criteria out of the producer's reach: a producer that can edit the test, the rubric or the threshold will eventually pass by editing them. If a criterion turns out wrong, change it as a separate, justified decision approved by the user, and re-evaluate what it already accepted.

## 4. Loop types

| Type | Shape | Typical exit |
|---|---|---|
| Retry | Same action after a transient failure (timeout, rate limit) | Bounded attempts after the relevant condition changes; resolve permission/auth mismatches only within existing authority |
| Refine (producer-verifier) | Produce, check, fix with feedback | Accept, or stagnation after equivalent failures |
| Search | Explore options until one passes or coverage is exhausted | Found, or "not found" with the coverage searched |
| Monitor | Check an external state until it changes (CI, a long job, a human reply) | Condition met, or timeout; check at the pace the state actually changes |
| Replan (adaptive) | The orchestrator revises the plan when evidence invalidates it | Plan converges, or `max_replans` |
| Improve the process | Change the flow or briefs, re-run held-out cases, compare | Better on held-out cases without regressions, or reject the change |

Nested loops are normal: a step's refine loop runs inside the flow's replan loop. Inner bounds must fit the outer budget.

Two kinds by termination: **goals** finish bounded work (they need a done definition, a verifier and a budget) and **cadence loops** run on a schedule to discover ongoing work (their state is a queue; each run should exit cheaply when there is nothing to do, without spawning agents). Classify failures before acting on them: a flaky check, a real regression, an environment problem and a configuration problem need different moves; environment problems are diagnosed and resolved inside existing authority (otherwise ask), and flaky checks are quarantined, not "fixed" with retries or longer timeouts. Persist the negatives too: human overrides and dismissed findings, so the loop does not propose them again.

**Autonomy grows with evidence.** For a newly proposed recurring automation, validate its decisions in report-only mode before enabling new external effects. An explicitly authorized bounded task may execute within that authorization; do not invent another approval ceremony for it. Raise autonomy (assisted, then unattended for low-risk actions) only after explicit graduation criteria are met, and lower it again after an incident or a cost spike. A kill switch returns everything to report-only.

**Budgets.** Track controller capacity, child turns, phase deadlines and global run/time/cost limits separately. Reserve closing capacity from the actual remaining budget, not a universal percentage. Every launch and exact-session continuation consumes the original global bounds. At a local phase cap, reconcile the stopped child and continue narrowly if room remains; at the global cap, start no worker, checkpoint and deliver the truthful partial result. An orchestrator may ask the user once for a bounded extension with a reason; it never raises its own limit. Cost multipliers to keep in mind: producer plus verifier is about 2× a single agent, N parallel candidates plus an arbiter is N+1, a two-sided debate of R rounds plus a judge is about 2R+1.

**After each run**, record what was missed, false positives, and one adjustment to try. Treat each lesson as a hypothesis to re-test on cases that were not used to find it; appending a new rule after every failure overfits the process and bloats the instructions.

## 5. Graphs

A graph is steps (nodes) and dependencies (edges). Keep two maps apart:

- **Work map**: tasks, dependencies, transitions (the flow file).
- **Knowledge map**: claims, sources and how they relate (supports, contradicts, depends on, replaces).

A relation between ideas does not set execution order, and an execution dependency does not prove a causal link between facts.

For every proposed edge ask: **"What would be wrong if this step started before that one finished?"** If nothing, there is no information dependency; the steps can run in parallel. Other real constraints still create edges: shared write access, a limited resource, an approval.

Common topologies: chain (each stage feeds the next), fan-out/fan-in (independent branches meet at a join), diamond (split, work, merge), tree (hierarchy of coordinators), bounded cycle (a back edge with a counter), conditional branch (route). The longest chain of dependent steps (the critical path) sets the minimum duration; parallel width is bounded by resources and by how much the verifiers can review.

Prefer wide, shallow graphs. If two steps seem to depend on each other, move the shared piece into its own upstream step. If one root step blocks everything, split the root. Independent branches that only meet at the end discover incompatibilities late: put a contract step before them.

## 6. Decomposition

A good task has one owner, one verifiable output, inputs that fit one context, one dominant risk, and a clear "done" (roughly what one agent finishes in one sitting). Two tasks are safe to run in parallel only if they share no files, neither needs the other's output, and neither edits something the other imports or reads. Destructive operations, migrations and writes to the same data never run in parallel without a gate. Split by **coverage** (different modules, sub-questions, hypotheses, perspectives) so agents do not repeat the same search. Too fine, and coordination costs exceed the work; too coarse, and nobody can verify it.

Before parallel implementation, fix the interfaces: agree on contracts (types, file formats, API shapes) in an early step, then let branches build against them. Changing a shared interface mid-flight invalidates every branch that uses it.

A delegated task never gains powers by being split: sub-delegation respects the global budget, the depth limit and the original scope.

Sizing (practitioner heuristics, not measured laws): 2-4 parallel workers is the usual sweet spot; from 5 up, coordination and review overhead grow fast. Use the smallest team that covers every distinct part; merge roles when there are more agents than real tasks. One task in progress per worker. Phases of 3-5 tasks are easy to review; a plan with more than ~25 tasks or 5 phases wants splitting into sub-flows. Multi-agent runs multiply token use; measure whether the split pays off on the task at hand.

## 7. Ownership and convergence

One owner per shared artifact. Many agents may read and propose; only the owner writes. Parallel steps get disjoint `owns`; contributions land in their own files and an integration step merges them. Record the version of the inputs each result was built on; if the base changed, reconcile before integrating ("last write wins" silently erases work).

Assigning ownership: list the files or outputs, cluster them (by folder, module, layer or topic), give each cluster one owner, and name the interface points (types, APIs, formats) that the orchestrator owns and workers only read. A file several workers need is split, or owned by one worker who takes change requests, or edited in sequence, never concurrently. Index or registry files that everyone touches are merged by the orchestrator at the end.

Integration: merge in dependency order; check build, types, tests and contracts after each merge; settle conflicts by the contract first, then the orchestrator's decision, then the tests, and only then by hand.

Join policies:

| Policy | Use when |
|---|---|
| `all` | Every branch is required (coverage). |
| `quorum` (`min: N`) | Redundant branches (judges, solvers); N valid answers suffice. |
| `any` / `first_valid` | Racing alternatives; cancel the rest once one passes. |

Declare which branches are required and what happens when one is missing. A branch that failed to access its source produced no evidence; that is not the same as "nothing found". Mark the synthesis incomplete instead.

When consolidating, deduplicate with provenance: keep every source behind a merged claim, never merge claims because they sound alike, and keep contradictions visible.

## 8. Invalidation and resume

An accepted result stays preserved. If one of its inputs changes, mark it and everything downstream `stale`; re-verify before reuse. Never carry an old verification over to a new version.

To resume after an interruption: read the state, rebuild it from the log if they disagree, check the state against the files (outputs it lists that are missing, files no step owns), find the last verified point, check which external effects really happened, keep accepted steps whose inputs are still valid, re-run only the affected steps and their dependents. Continue under existing authorization when the next action is covered. Ask only about a new decision or changed bounds; never require a fresh approval merely to resume the authorized task.

Checkpoints: after each verified phase, record a restore point (a commit, a copy, an id in the log) so a bad later step can be undone per unit of work without discarding everything. Keep a deviations log (date, step, what changed from the plan, why, resolution) next to the state. A recorded intention does not prove the action happened, and a missing confirmation does not prove it failed: check before repeating anything with external effects (idempotence). An action whose outcome is unknown is never retried automatically; reconcile with the real system first, or ask.

## 9. Hierarchy

A step can be a whole sub-flow with its own coordinator, state and log (`flow: subflow.yaml`). Use it when a branch is big enough to need its own decomposition. The parent sends a contract down (goal, inputs, limits, output) and receives a summary up (status, outputs, evidence, open issues); it does not micromanage the sub-flow's steps. Keep depth small (one or two levels): every level adds latency, cost and a place where meaning is lost.
