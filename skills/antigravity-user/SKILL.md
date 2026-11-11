---
name: antigravity-user
description: Use when delegating to Antigravity. Verify results.
---

# Antigravity user

Drive `agy` in finite headless phases. `$SKILL_DIR` is this installed folder; `reference.md` and `docs/README.md` preserve commands and official snapshots. Historical tests used agy 1.4.2 on Windows. Resolve the actual binary, help, OS, model availability and authentication before applying those observations elsewhere.

## Prepare

Record objective, owned paths, baseline, exact tests, model/effort, intended billing route and expected outputs. Inspect workspace hooks, MCP and plugins: headless execution can load them without a trust prompt. Do not install/update the CLI or change global settings as an incidental prerequisite.

Apply the reviewed guard using `rules/README.md`. Confirm settings are valid and no example secret-path placeholder remains. Match the actual commands needed by the authorized phase. Workers do not inherit publication, messaging or root authority. Sandbox claims need an exercised OS boundary; a worktree only organizes recovery.

Allocate a finite phase timeout inside the remaining global limits, with capacity for verification and delivery. Create an absolute attempt-specific `$RUN` outside the checkout.

## Invocation

```bash
agy -p "$PROMPT" --output-format stream-json --mode accept-edits   --model "$MODEL" --effort "$EFFORT" --print-timeout "$PHASE_TIMEOUT"   </dev/null > "$RUN/events.jsonl" 2> "$RUN/stderr.txt"
```

Save the real child exit code and full `conversation_id`. Keep stderr separate and use the host's supervised background/completion primitive for long work, not a second detached shell. Activity, an init event and a launch receipt are not completion.

```bash
# protocol-check
jq -e -s 'map(select(.event=="result"))|last|.result|type=="object" and .status=="SUCCESS" and (((.response|type)=="string" and (.response|length)>0) or (has("structured_output") and .structured_output!=null))' "$RUN/events.jsonl"
```

Require exit zero, the expected current conversation/model, independently validated outputs and no unresolved necessary operation. Validate `structured_output` against its schema instead of requiring redundant prose. Screen tool `step_update.state=="ERROR"` and read stderr for `auto-denied` notices. Headless can return `SUCCESS` and exit zero after denying a required command; that phase is not accepted until the missing operation is resolved and checked. Empty/truncated JSONL and nonterminal statuses do not pass.

## Continue

After timeout or an interrupted phase, confirm the exact previous child stopped and reconcile artifacts. While budget remains, resume the full saved ID in the same cwd and authentication/settings context:

```bash
agy -p "$REMAINING_PROMPT" --conversation "$CONVERSATION_ID"   --output-format stream-json --mode accept-edits   --model "$MODEL" --effort "$EFFORT" --print-timeout "$REMAINING_TIMEOUT"   </dev/null > "$NEXT_RUN/events.jsonl" 2> "$NEXT_RUN/stderr.txt"
```

Require the returned conversation ID to match. Never recover with the most recent selector. Include valid evidence, failed approaches, exact remaining scope and remaining limits. Every continuation consumes the original budget. Cumulative `usage` and `num_turns` must not be summed as independent runs.

## Permissions and billing

- Preserve the user's exact model, effort and login/provider route. A rejected or unavailable model does not authorize substitution. Do not turn on paid-credit fallback to escape a subscription quota.
- Headless cannot answer interactive asks. Fix permission mismatches only inside the authorized worker scope; a silent denial is not an authentication failure.
- Follow `rules/README.md` for deny coverage, generated secret paths and verification. Malformed settings may be ignored by the CLI; valid JSON alone does not prove native enforcement. Exercise both blocked and clean controls on the installed version when available.
- Inspect effective sandbox support on that OS/version before relying on it. Guard regex, permission rules and prompts do not contain hostile code by themselves.
- Persistent input streaming, structured output, skills, MCP and interactive capabilities remain in the snapshots. Do not assume a TUI command is a valid headless protocol or create a schedule without authorization.
- Never put API keys in prompts, arguments or logs. Login metadata does not establish successful inference; verify the requested route with real work when that is the question.

## Deliver

Read the diff and rerun required tests independently. Preserve the final envelope, stderr findings, model and observed tokens. Stop on global exhaustion with session/artifacts and the actual pending work. Technical completion, external effects and final delivery are separate controller-owned outcomes; verify each exact target before reporting it and never blindly repeat an ambiguous effect.
