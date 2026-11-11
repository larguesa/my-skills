---
name: opencode-user
description: Use when delegating to OpenCode. Verify final work.
---

# OpenCode user

Use `opencode run` for bounded unattended work. `$SKILL_DIR` is this installed folder; `reference.md` and `docs/README.md` preserve the command reference and official snapshots. Historical tests used 1.19.5, not a promise about the current host. Discover the executable, help, provider and effective permissions first.

## Prepare

Record task, owned files, baseline, exact test command, requested model/variant, authentication route and expected artifacts. Inspect repository configuration/plugins before trusting them. Apply `hooks/README.md` without replacing an existing deny/ask policy with a broad allow. A worktree is recovery organization, not OS containment.

Allocate a finite phase deadline and step count inside unchanged global bounds, including all continuations and closing work. Create an attempt-specific absolute `$RUN` outside the checkout. Disable only unused MCP servers deliberately, not a server name copied from another host.

## Invocation and observation

With reviewed permissions already in place and the actual phase step cap configured:

```bash
opencode run --format json --title "$TASK_NAME"   --model "$MODEL" --variant "$EFFORT"   "$PROMPT" </dev/null > "$RUN/events.jsonl" 2> "$RUN/stderr.txt"
```

Capture the real child exit status and full `sessionID`. Keep stderr separate. A launch receipt is not completion. Use the host's supervised background primitive and completion consumer, without a second detached shell. A persistent server is a separate owned process; it must not outlive the task accidentally or be exposed without authorization/authentication.

`step_finish` occurs at intermediate model/tool steps. The historical snapshot records `part.reason` but does not enumerate terminal values. Before treating a particular value as final, verify it against the installed version's session export or native API. Until then this is only protocol screening, not a complete acceptance predicate:

```bash
# protocol-check
jq -e -s 'length>0 and ([.[]|select(.type=="step_finish")]|length)>0 and ([.[]|select(.type=="text" and (.part.text|type)=="string" and (.part.text|length)>0)]|length)>0 and ([.[]|select(.type=="error")]|length)==0' "$RUN/events.jsonl"
```

Acceptance additionally requires process exit zero, the observed native final-turn shape, correct current session/model, independently verified artifacts and no unresolved required operation. A lone `step_finish`, partial text or incomplete export remains unverified. Inspect `tool_use.part.state.status`, denied permissions and stderr even when the process returned zero. If the final protocol cannot be established, preserve evidence and report that missing verification instead of assuming success.

## Continuation and recovery

After a phase limit or timeout, confirm the exact child exited and reconcile its files before another writer starts. Continue from the full saved ID with the same cwd, provider, permissions and requested model/variant:

```bash
opencode run --format json --session "$SESSION_ID"   --model "$MODEL" --variant "$EFFORT"   "$REMAINING_PROMPT" </dev/null > "$NEXT_RUN/events.jsonl" 2> "$NEXT_RUN/stderr.txt"
```

Do not use the most recent session selector in recovery. Supply remaining scope, accepted evidence, failed approaches and global budget left; a new invocation debits the same budget. Fix only operational mismatches within existing authorization. Missing permission or a quota/reset outside the remaining deadline is a blocker, not permission to switch billing/model or relax checks.

## Permissions and references

- `run` auto-rejects interactive asks in the documented versions. Distinguish missing pre-approval from lack of tool availability. Permit the actual tests and input-generation operations inside the worker's scope, not broad publication or credential access.
- Use the guard overlay and its lossless merge procedure in `hooks/README.md`. Guard patterns and configuration are not OS isolation. Inspect effective project/per-agent overrides.
- Use `--agent plan` for read-oriented planning only after checking its actual write exceptions. Build mode, MCP, external directories and plugins have independent authority implications.
- Provider keys remain in the environment/protected configuration, never prompts or logs. Preserve a fixed model and variant on every invocation; no silent fallback.
- `reference.md` covers serve/attach, models, MCP, skills and export. Do not install agents, expose servers, alter global configuration or refresh documentation automatically.

## Finish

Inspect the actual diff and rerun required tests. Report observed model, usage and unverified items, not host-specific historical price examples as forecasts. Technical acceptance is distinct from push, installation and message delivery; the controller reconciles each already authorized effect and replies through the requested channel without blind repetition.
