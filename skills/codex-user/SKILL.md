---
name: codex-user
description: Use when delegating to Codex. Verify and resume work.
---

# Codex user

Drive `codex exec` without a PTY for unattended phases. `$SKILL_DIR` is this installed folder; `reference.md` and `docs/README.md` retain the command reference and official snapshots. Historical checks used 0.166.0; inspect the actual binary and `exec`/`resume` help before reuse.

## Prepare

- Record the task, owned files, baseline, required tests, requested model/effort and intended authentication/billing route. Do not infer standalone CLI login from Hermes login or a missing environment key.
- Prefer a Git checkout for edits. Authorized non-repository work can use `--skip-git-repo-check`; do not initialize an unrelated repository. Exec needs no PTY.
- Select sandbox and approval policy separately. Worktrees organize recovery, not OS containment. If sandbox startup fails, diagnose that environment; do not silently select full access.
- Keep guard rules in the actual `${CODEX_HOME:-$HOME/.codex}`. Follow `rules/README.md`; a private CODEX_HOME must not silently drop them. Do not edit global configuration as part of ordinary delegation.
- Allocate finite phase time inside global limits, including every continuation and a closing reserve. Save the supervisor handle and exact thread ID separately.

## Standard invocation

Set absolute `$PROJECT` and attempt-specific `$RUN` outside the checkout. Choose `$MODEL`, `$EFFORT` and `$SANDBOX` for the authorized phase. Run from the recorded cwd; retain structured stdout and stderr separately.

```bash
codex exec --json -C "$PROJECT" --model "$MODEL"   -c "model_reasoning_effort=\"$EFFORT\"" --sandbox "$SANDBOX"   --output-last-message "$RUN/last.md" -   < "$RUN/prompt.txt" > "$RUN/events.jsonl" 2> "$RUN/stderr.txt"
```

Capture the real child exit status. Protocol screening uses the last terminal turn, not any earlier success:

```bash
# protocol-check
jq -e -s 'map(select(.type=="turn.completed" or .type=="turn.failed")) | last | .type=="turn.completed"' "$RUN/events.jsonl"
```

Accept only with exit zero, expected current thread/model/effort, final answer or schema-valid structured output, required artifacts checked independently and no unresolved necessary operation. Inspect failed `command_execution` and tool items; a recovered warning is not the same as missing work. Empty/truncated JSONL, `turn.failed`, launch-only output and a handle are not success.

## Continue and supervise

Use the host's supervised background primitive and completion consumer, with a finite deadline. Do not detach again inside it. After timeout or interruption, confirm the old child exited and reconcile outputs before another writer starts.

From the same cwd and CODEX_HOME, resume the full saved ID, preserving provider configuration and sandbox:

```bash
codex exec resume "$THREAD_ID" --json --model "$MODEL"   -c "model_reasoning_effort=\"$EFFORT\""   -c "sandbox_mode=\"$SANDBOX\""   --output-last-message "$NEXT_RUN/last.md" -   < "$NEXT_RUN/prompt.txt" > "$NEXT_RUN/events.jsonl" 2> "$NEXT_RUN/stderr.txt"
```

Resume does not take the first invocation's `-C`/`-s` in the checked interface. Confirm live help. Include remaining scope, accepted evidence, failed approaches and remaining global limits. Do not recover with `--last`. Every continuation debits the original budget; stop at exhaustion and report the real partial state.

## Authentication, tools and review

- ChatGPT OAuth and a selected API provider are different routes. Preserve the chosen route; an API route must be authorized, use a narrowly scoped inference key in the environment and never receive a management credential. Retain isolated CODEX_HOME on resume when used.
- For an authorized custom Responses provider, set `model_provider`, its `base_url`, `env_key` and `wire_api` explicitly. Verify the exact model and supported effort first. Provider selection is not permission to switch model or billing on failure.
- `--full-auto` is removed in the checked versions. Never use it as a recovery recipe. `danger-full-access` and approval bypass require an explicitly authorized external containment boundary.
- `execpolicy` prefix rules are not a general filesystem sandbox. Read their limits and test the actual generated rules with the native checker. Existing read restrictions and network policy remain separate.
- A read-only review can use `codex exec review --uncommitted` or a named base, according to live help. Reviewers report findings; they do not push, deploy, publish or send.
- Use an output schema when required and validate the resulting artifact. Project instructions, skills and MCP have version-specific discovery and trust rules; inspect before executing an unfamiliar checkout.

## Finish

Read the diff and run the real tests independently. Preserve exit status, terminal events, thread ID, model/effort, usage and evidence; do not invent API costs from token counts. A technical result does not prove push, install or message delivery. The controller performs already authorized effects, reads their exact targets back, and closes through the requested channel without repeating ambiguous effects.
