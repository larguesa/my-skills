---
name: claude-code-user
description: Use when delegating to Claude Code. Verify completion.
---

# Claude Code user

Run bounded, resumable Claude Code phases. `$SKILL_DIR` is this installed folder; `reference.md` is the cheat-sheet and `docs/README.md` indexes the preserved official documentation. Historical tests used 2.1.316; discover the actual binary and help before reusing version-sensitive flags.

## Execution contract

1. Read the request and project instructions; record baseline, owned files, expected artifacts and the exact test command. Reuse authorization already given, without passing publication or messaging authority to the worker.
2. Record the exact model, effort, authentication route and session policy. Reconcile `CLAUDE_CODE_EFFORT_LEVEL` with the requested effort. No silent fallback, cheaper-model substitution, credential copying or change of billing route.
3. Allocate finite child turns and wall time inside the remaining flow budget, leaving capacity for verification and delivery. A phase limit is not the global limit. Check tool availability and pre-approval separately.
4. Create an attempt-specific `$RUN` outside the checkout. Save the prompt, invocation, exit status, structured stdout, stderr and session ID. One active writer per output.
5. Validate the protocol, then independently inspect artifacts, diff and tests. A launch receipt, activity or `subtype=success` alone is not completion.

## Standard invocation

Choose `$MODEL`, `$EFFORT`, `$TURN_LIMIT`, `$AVAILABLE_TOOLS` and `$PREAPPROVED_TOOLS` from the authorized phase, not from this example. A review may expose only Read/Glob/Grep; implementation also needs Write/Edit and the actual test operations. Set `$RUN` and `$SKILL_DIR` to absolute paths. Inspect repository hooks/MCP before unattended use.

```bash
export CLAUDE_CODE_USER_GUARD="$SKILL_DIR/hooks/guard.sh"
test -r "$CLAUDE_CODE_USER_GUARD" || exit 2
claude -p --model "$MODEL" --effort "$EFFORT"   --tools "$AVAILABLE_TOOLS" --allowedTools "$PREAPPROVED_TOOLS"   --permission-mode dontAsk --settings "$SKILL_DIR/hooks/settings-guard.json"   --max-turns "$TURN_LIMIT" --output-format stream-json --verbose   < "$RUN/prompt.txt" > "$RUN/events.jsonl" 2> "$RUN/stderr.txt"
```

The host must capture the child exit code without masking it with a pipeline. The following is a protocol check, not artifact or permission-denial verification:

```bash
# protocol-check
jq -e -s 'map(select(.type=="result")) | last | type=="object" and .subtype=="success" and .is_error==false and ((.terminal_reason==null) or (.terminal_reason=="completed")) and (((.result | type)=="string" and (.result | length)>0) or (has("structured_output") and .structured_output!=null))' "$RUN/events.jsonl"
```

Also require exit zero, expected session/model, a complete current-attempt result, no unresolved necessary operation and independently verified outputs. Validate `structured_output` against the requested schema. Inspect `permission_denials` even on success; a denial later recovered is different from work still missing.

## Continuation and long jobs

Use the host's supervised background primitive with a completion consumer, finite deadline and a saved handle. Keep this same guard and stdout/stderr separation in long runs; do not add a second detached shell. Print mode needs no PTY; a multi-round task does not require the TUI.

After a phase turn limit or timeout, verify that the exact previous child exited, reconcile its outputs and resume only while global budget remains:

```bash
claude -p --resume "$SESSION_ID" --model "$MODEL" --effort "$EFFORT"   --tools "$AVAILABLE_TOOLS" --allowedTools "$PREAPPROVED_TOOLS"   --permission-mode dontAsk --settings "$SKILL_DIR/hooks/settings-guard.json"   --max-turns "$REMAINING_TURNS" --output-format stream-json --verbose   < "$NEXT_RUN/prompt.txt" > "$NEXT_RUN/events.jsonl" 2> "$NEXT_RUN/stderr.txt"
```

Keep the exported guard path, exact session ID, cwd and authentication route. Supply remaining scope, valid evidence, failed approaches and remaining limits. Never recover with the most recent session selector. Cota/rate limits require the observed reset or a changed condition; auth errors do not authorize token rotation. Stop at the global bound and deliver a truthful partial result.

## Permissions, authentication and recovery

- `--tools` selects capabilities; `--allowedTools` pre-approves operations. A test allow rule does not authorize unrelated input-generation commands. Fix a mismatch only inside the worker's authorized scope.
- Preserve subscription OAuth. `--bare` skips it; use that mode only for an explicitly intended API/helper route. `--safe-mode` disables customizations, including the guard, so it is not a substitute for the guarded recipe.
- `--settings` loads the portable guard; follow `hooks/README.md` and exercise blocked and clean inputs at the installed path. Missing guard/parser must block. Regex and permissions are guardrails, not OS isolation.
- A worktree or copy organizes recovery, not containment. Inspect untrusted project hooks/configuration before launch; expose only needed tools/MCP servers.
- Keep exact-session persistence for resumable work. Use `--no-session-persistence` only for disposable phases. Use stdin for long prompts, especially beside variadic options.
- Review actual assistant-model events in continuations. Unchanged cumulative auxiliary-model counters do not prove new fallback. Report subscription list-price estimates separately from API charges; do not sum cumulative resume totals.
- Checkpoints do not cover every Bash, subagent or external edit. Preserve the user's changes; never stash/reset an unrelated worktree to obtain a baseline.

## Delivery

A completed Claude phase is not a published, installed or delivered task. The controller performs only the external effects already authorized, reads each target back, and replies through the requested channel. On interruption, preserve session and artifacts and report the actual pending work. Never log credentials or internal lifecycle messages as user deliverables.
