---
name: claude-code-user
description: Drive Claude Code (the `claude` CLI) headless as a user or agent - when to delegate, standard `claude -p` invocation, permissions, budgets, resume, long jobs, a guard hook, verification, plus a cheat-sheet and the official Claude Code docs in markdown. Use when delegating coding work to Claude Code or looking up its flags, commands, env vars, tools, hooks or checkpointing.
---

# Claude Code user: driving it headless (tested on v2.1.316)


`$SKILL_DIR` = this skill's folder (e.g. `~/.claude/skills/claude-code-user` or wherever you copied it). Cheat-sheet: `reference.md`. Official docs (markdown, 2026-10-31) in `docs/` — see `docs/README.md`; refresh with `docs/update.sh`.

## When to delegate
- Delegate: multi-file features, refactors, cross-repo debugging, test suites, diff review, long fix-test loops.
- Do it yourself: one-line edits, reading files, shell admin, anything needing the user's accounts/connectors, anything externally visible.
- On a Claude subscription the quota (5-hour + weekly windows) is shared with the user's own use. One well-specified run beats many small ones; use `--model haiku`/`sonnet` for small jobs.

## Standard invocation
```bash
cd <project> && git status --short        # baseline; git repo preferred
claude -p "$PROMPT" \
  --output-format json \
  --permission-mode acceptEdits \
  --allowedTools "Bash(uvx pytest *),Bash(npm test *),Bash(git diff *),Bash(git status *)" \
  --settings "$SKILL_DIR/hooks/settings-guard.json" \
  --max-turns 30 --max-budget-usd 3 \
  --fallback-model sonnet \
  </dev/null > /tmp/cc_<task>.json
jq '{result,session_id,is_error,subtype,num_turns,total_cost_usd,permission_denials}' /tmp/cc_<task>.json
```
- Always `</dev/null` and `--output-format json`. Never `--bare`: it skips OAuth and needs ANTHROPIC_API_KEY (docs/headless.md).
- Since v2.1.302 `-p` starts in Manual mode: anything needing approval is denied and listed in `permission_denials` (docs/headless.md "Auto-approve tools").
- Wider unattended runs: `--permission-mode auto --permission-prompts none`. `--dangerously-skip-permissions` only in a throwaway sandbox.
- `--allowedTools` pre-approves; `--tools "Read,Edit,Bash"` restricts what exists; `--disallowedTools "Bash(rm *)"` denies.
- `--max-turns` exits with error_max_turns; `--max-budget-usd` is a client-side estimate and can overshoot, leave headroom.
- Python on PEP-668 systems: tell it to use `uvx pytest` / `uv run`.

## Shaping the run
- Extra rules without losing defaults: `--append-system-prompt "..."` / `--append-system-prompt-file f`. `--system-prompt` replaces everything (tool + safety guidance) — avoid.
- Machine-readable answer: `--json-schema '<schema>'` → `.structured_output` (adds a turn).
- Other dirs: `--add-dir ../lib` (file access only; their .claude config isn't loaded).
- Isolation: `-w <name>` runs in a git worktree at `.claude/worktrees/<name>`.
- Throwaway queries: `--no-session-persistence`. Name sessions with `-n`; `--session-id <uuid>` to fix the ID up front.
- Effort: `--effort low|medium|high|xhigh|max`.

## Follow-ups
`claude -p "next" --resume "$SESSION_ID" --output-format json ...same flags... </dev/null` (also accepts a name). `--fork-session` branches instead of reusing. `--continue` = most recent in cwd; avoid with parallel runs. `total_cost_usd` is cumulative on resume. System-prompt flags are snapshotted at the first request: changed text only applies after compaction or a new session (docs/cli-reference.md).

## Long jobs
```bash
nohup claude -p "$PROMPT" --output-format stream-json --verbose --permission-mode acceptEdits \
  --allowedTools "..." --max-turns 60 --max-budget-usd 8 </dev/null > <project>/.cc.log 2>&1 &
```
Background the Shell call and await; last line is the `result` object (`tail -1 .cc.log | jq`). `system/api_retry` events show throttling. Stop with SIGINT (SIGTERM → exit 143, turn lost). `-p` waits for its own background tasks (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`).

## Guard hook (always on)
`hooks/settings-guard.json` registers `hooks/guard.sh` as a PreToolUse hook on Bash: exit 2 blocks `git push`, mutating curl, `.secrets` access and `rm -rf /`, and Claude is told why. Exit 2 wins over any JSON "allow". Details: docs/hooks.md ("Exit code 2", "PreToolUse").
Warning: without `--bare`, `-p` runs the project's own `.claude/settings.json` hooks and `.mcp.json` servers with no trust prompt. Inspect an unknown repo first, or use `--setting-sources user` / `--strict-mcp-config`.

## Undo
Checkpoints (docs/checkpointing.md) snapshot only edits made by its Edit/Write tools, before each prompt; `/rewind` is interactive. Bash-made changes, subagent edits and external changes are NOT tracked. For headless work rely on git: commit or stash a baseline first; `git diff`/`git checkout` to undo.

## Remote driving
Channels (docs/channels-reference.md) are research preview: an MCP server pushes Telegram/Discord/webhook events into a running interactive session (`--channels plugin:...`); dev channels are ignored with `-p`. Not needed for -p workflows; consider for a remote/gateway bridge.

## Writing the prompt
Goal (one sentence) · Context (files, stack, how to run) · Constraints (no new deps, no commit/push unless asked) · Tests (exact command) · Done criteria · Output (short summary of changed files + anything unverified). Put stable project facts in CLAUDE.md.

## Verify, don't trust
1. `is_error` false and `subtype` "success" (else error_max_turns / error_during_execution / budget).
2. `git diff --stat` and read the diff.
3. Run the tests yourself; its summary is a claim, not proof.
4. Read `permission_denials`; widen allowances deliberately and resume.

## Safety
- Never let it push, deploy, publish, send messages or touch secrets without the user's explicit OK; keep those out of allowedTools and keep the guard hook on.
- Never pass API keys in prompts or print them; keep them in env vars or chmod-600 files outside the repo.
- Report cost (`total_cost_usd`, an estimate; on subscription it's quota) and model (`modelUsage` keys).
