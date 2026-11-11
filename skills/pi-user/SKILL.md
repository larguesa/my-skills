---
name: pi-user
description: Use when delegating to pi. Verify settled results.
---

# pi user

Drive pi headless in finite, resumable phases. `$SKILL_DIR` is this installed folder. Use `reference.md` for commands and `docs/README.md` for the preserved official snapshots; historical tests used pi 1.4.0. Resolve the actual executable and help before assuming a version or installation.

## Prepare and run

Record scope, owned outputs, baseline, exact tests, requested model/effort, provider and session policy. Workers do not inherit the controller's publication authority. Choose tools and MCP deliberately, and keep a finite phase deadline inside the global budget with room for verification and delivery.

Set an attempt-specific absolute `$RUN` outside the checkout. Use a supplied prompt argument with closed stdin, or deliberately use the documented piped-input protocol. Never append accidental stdin.

```bash
pi -p --mode json -e "$SKILL_DIR/hooks/guard.ts"   --model "$MODEL" --thinking "$EFFORT" --name "$TASK_NAME"   --no-mcp --tools read,bash,edit,write   "$PROMPT" </dev/null > "$RUN/events.jsonl" 2> "$RUN/stderr.txt"
```

The shown tool set is for implementation, not a read-only review. Restrict a review to the documented read/search tools; inspect MCP, extensions and codemode separately. Preserve the requested model/effort instead of substituting a cheaper default. A worktree or copy is recovery organization, not OS isolation.

## Accept only a settled result

Capture the child exit code and exact session header `.id`. `agent_end` alone is not final: retries or compaction can follow it. JSON-mode errors may not produce a nonzero exit. Screen the complete current-attempt stream:

```bash
# protocol-check
jq -e -s '([.[]|select(.type=="agent_settled")]|last|.aborted==false) and ([.[]|select(.type=="message_end" and .message.role=="assistant")]|last|.message.stopReason=="stop")' "$RUN/events.jsonl"
```

Also require the expected session/model, process termination, independently checked outputs and no unresolved required tool error. Inspect `tool_execution_end.isError` and final `stopReason`; `error`, `aborted`, `length`, an absent settled event or an empty/truncated stream do not pass. Verify structured deliverables against their contract, not merely the final text.

## Continue and long jobs

Save a supervisor handle as well as the full session ID. Use the host's supervised background/completion mechanism without a second detached shell. For persistent RPC, delimit and verify each turn separately; process lifetime is not turn completion.

After a bounded interruption, first confirm the old worker stopped and reconcile its outputs. Continue only within remaining limits:

```bash
pi -p --mode json -e "$SKILL_DIR/hooks/guard.ts"   --session "$SESSION_ID" --model "$MODEL" --thinking "$EFFORT"   --no-mcp --tools read,bash,edit,write   "$REMAINING_PROMPT" </dev/null > "$NEXT_RUN/events.jsonl" 2> "$NEXT_RUN/stderr.txt"
```

Require the resumed header to contain that full ID and the recorded cwd. `--session-id` can create a new session if absent; it is not recovery. Do not use partial IDs or the most recent session selector. Supply remaining scope, valid evidence, failed approaches and remaining budget; continuation does not reset counters or authorize a new provider.

## Guard, authentication and discovery

- Load `hooks/guard.ts` on every guarded phase, including resumes; follow `hooks/README.md` for actual coverage and blocked/clean probes at the installed path.
- Pi extensions are guardrails, not OS isolation. Tools or MCP execution outside a guard's coverage must be restricted separately. Never broaden powers merely to escape a denial.
- Preserve the authorized provider/login route. Pass inference keys only through the environment or a protected wrapper; never print authentication commands that expose a key.
- Project trust and execution authority differ. Inspect project configuration before trusting it; use the installed version's opt-out when appropriate. Add MCP only when needed and authorized.
- Native MCP, RPC, extensions and skills are documented in the snapshots; installation and global changes are separate actions, not prerequisites to perform automatically.

## Verify and deliver

Read the actual diff and rerun required checks yourself. Report model and observed usage. Sum only independent per-run cost events; do not describe subscription estimates as extra charges. Stop at global exhaustion with preserved artifacts and the real pending scope. Technical completion, external publication and final delivery remain distinct controller-owned outcomes.
