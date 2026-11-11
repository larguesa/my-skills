# Execution contract

Apply before dispatch and on recovery. This is a procedure for the host agent, not an orchestration runtime.

## Four distinct observations

| Observation | Evidence | Does not establish |
|---|---|---|
| Launched | host handle, child identity, invocation | finished work |
| Terminal | real child exit or native final-turn event | correct artifacts |
| Accepted | current result, valid inputs, independent checks | publication or delivery |
| Delivered | every requested effect verified at its exact target | human reading |

A one-shot child must actually exit. A persistent RPC client may keep running after a completed turn; apply its native turn protocol. Never accept a launcher shell's exit as proof that its scoped child stopped.

## Before launch

Record ref (run/step/attempt), model, effort, auth/provider route, cwd, input revisions, output path, phase budget, global remainder, supervisor handle and result consumer. No credentials in the record. Keep stdout structured and stderr separate, in a directory unique to that attempt outside a checkout when logs are not project deliverables.

Tool availability, pre-approval, OS containment and user authorization are separate. Match the operations actually needed, including fixture generation and tests. Do not copy a read-only profile into implementation. No fallback when the user fixed the model/effort, unless substitution was separately authorized.

## Completion consumers

Use the live host schema. For Hermes as checked on 2026-11-11:

- External CLI: `terminal(background=true, notify=true)` creates a tracked process; `process_manage` reads/waits on that handle. Keep a finite child deadline. No nested `nohup`/detached shell.
- Native `delegate_task`: consume its completion message as the host specifies. Do not poll transcript/artifact files to await a native child. A file can appear before completion.
- A process-local child is not durable execution. For required restart survival, use an already authorized durable mechanism and verify its record. Do not invent a follow-up schedule.

The tool names and parameters above are a dated adapter example, not a portable interface guarantee. The five CLI skills remain host-neutral.

## Result acceptance

| CLI | Required protocol evidence in addition to current artifacts |
|---|---|
| Claude | final `result`, success subtype, `is_error=false`, terminal reason absent or completed, valid result/structured output; inspect necessary denials |
| Codex | last terminal turn is `turn.completed`, final answer/schema output, no unresolved required tool failure |
| pi | `agent_settled`, not aborted, final assistant `stopReason=stop`; `agent_end` alone is insufficient |
| OpenCode | real process completion and installed-version final-turn evidence; intermediate `step_finish` alone never suffices |
| Antigravity | final result SUCCESS plus valid response/structured output, tool failures and stderr auto-denials reconciled |

Also check exit code where applicable, expected exact session and effective model, schema/coverage and independent tests. A protocol predicate is necessary screening, not the complete acceptance decision. A recovered denial differs from a required operation still missing. Missing/truncated output is unknown, never green. Inspect new assistant events rather than mistaking unchanged cumulative auxiliary usage for a new fallback.

## Budgets and narrow recovery

Maintain separate controller capacity, child turns, phase wall time and global run/time/cost bounds. Allocate a closing reserve from the real remaining budget, not a universal percentage. Every launch and continuation consumes `max_agent_runs`; retain counters, fixed choices and absolute global deadline across sessions.

| Outcome | Next authorized action |
|---|---|
| Accepted phase | checkpoint, release ownership, advance |
| Local turn/time limit, real progress and global room | confirm old child stopped; reconcile artifacts; resume exact saved session with narrow remaining scope |
| Repeated continuation without new evidence | apply declared stagnation rule; checkpoint and report |
| Quota/rate window | preserve state; wait only within deadline/authorization, then retry after the observed condition changes |
| Auth/configuration failure | diagnose exact route; no credential copying, rotation or model substitution; retry only after a supported correction |
| Necessary operation denied | compare actual capability and approval pattern; correct only within existing worker authority, otherwise block |
| Global limit or no usable result | no new worker; persist handoff and deliver the truthful partial outcome |

A continuation brief includes exact session/cwd/model/effort/auth route, remaining scope, valid evidence, discarded approaches and remaining limits. Never use the latest-session selector. Do not reset counters or silently enlarge the global bound. Save phase outputs before beginning another long discovery.

## External effects and closing

Reuse authorization already covering the effect. Before acting, append `effect` with `status: started` and a stable key covering action, destination and content/revision. After execution, read the exact target and append `confirmed` with its receipt. `started` without confirmation is unknown: reconcile before repetition. This is duplicate avoidance, not a transport guarantee of exactly once.

Examples: compare remote branch SHA for push, installed file hashes for installation, and the exact stored message/response ID for delivery. An accepted send must not be repeated because later archival verification failed. Compensation needs its own existing authority; some explicitly authorized effects have `undo: none`.

Reserve separate acceptance items for technical work, publication, installation and requested final response. Preserve successful earlier phases if a later one fails. At interruption or exhaustion, close in the authorized conversation with the specific pending work, without internal lifecycle events, credentials or private execution paths.
