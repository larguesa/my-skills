---
name: codex-user
description: Drive the OpenAI Codex CLI headless as a user or agent - when to delegate (vs Claude Code, pi, OpenCode), standard `codex exec --json` invocation, -o/--output-schema, sandbox and approval modes, execpolicy rules guard, resume/fork, review mode, AGENTS.md, skills, MCP, ChatGPT-plan usage limits, verification, plus a cheat-sheet and the official Codex docs in markdown. Use when delegating coding work to Codex or looking up its commands, config, sandbox, rules, MCP or skills.
---


`$SKILL_DIR` = this skill's folder (e.g. `~/.agents/skills/codex-user`). Cheat-sheet: `reference.md`. Official docs (markdown, 2026-10-31) in `docs/` — see `docs/README.md`; refresh with `docs/update.sh`. Flags below were checked against `codex exec --help` of the installed version; items marked *(not tested live)* could not be run because the ChatGPT quota was exhausted when this was written.

## Recommended setup
Install: `npm i -g @openai/codex`, then `codex login` (ChatGPT account; on a headless machine use `codex login --device-auth` or log in through a desktop browser). Back up `~/.codex/config.toml`, then add:
```toml
sandbox_mode = "workspace-write"
[sandbox_workspace_write]
network_access = false
```
`mkdir -p ~/.codex/rules && ln -s "$SKILL_DIR/rules/guard.rules" ~/.codex/rules/guard.rules`. Check: `codex doctor --summary`, `codex sandbox -P :workspace -- bash -c 'touch x; curl -m5 https://example.com'`.

## When to delegate (and to whom)
- **Codex**: second opinion / independent implementation, `codex exec review` of a diff, tasks where an OpenAI model is wanted, well-scoped fixes with a test command. Runs on the user's ChatGPT plan.
- **Claude Code** (skill `claude-code-user`): biggest multi-file features, long fix-test loops; Anthropic subscription.
- **OpenCode / pi** (skills `opencode-user`, `pi-user`): pay-per-token on any provider (e.g. OpenRouter); cheap bulk work and parallel runs that must not touch subscription quota.
- **Yourself**: one-line edits, reading files, shell admin, anything needing the user's connectors or externally visible.
- Quota: ChatGPT plan limits (5-hour + weekly windows) are shared with the user's own Codex/ChatGPT use. Check https://chatgpt.com/settings/usage (URL from the CLI's own limit message) (the user checks it while signed in). A spent quota shows as `{"type":"error","message":"You've hit your usage limit... try again at <date>"}` then `turn.failed`. One well-specified run beats many small ones; use a smaller model (`-m`) for small jobs.

## Standard invocation
```bash
cd /workspace/<project> && git status --short          # baseline; Codex wants a git repo
codex exec --json \
  -C /workspace/<project> \
  -s workspace-write \
  -o /tmp/cx_<task>.last.md \
  "$PROMPT" </dev/null > /tmp/cx_<task>.jsonl 2>/tmp/cx_<task>.err
jq -c 'select(.type=="thread.started" or .type=="turn.completed" or .type=="turn.failed" or .type=="error")' /tmp/cx_<task>.jsonl
cat /tmp/cx_<task>.last.md
```
- Always `</dev/null`: with a prompt argument and piped stdin it appends stdin as a `<stdin>` block (prints "Reading additional input from stdin...").
- `--json` → JSONL on stdout: `thread.started{thread_id}`, `turn.started`, `item.started|updated|completed` (agent_message, reasoning, command_execution, file_change, mcp_tool_call, web_search, todo_list), `turn.completed{usage}`, `turn.failed`, `error` (docs/non-interactive-mode.md). Progress goes to stderr.
- `-o/--output-last-message FILE` writes the final message; `--output-schema schema.json` forces a JSON answer (docs/non-interactive-mode.md "Create structured outputs"). *(not tested live)*
- Outside git: `--skip-git-repo-check`. Other writable dirs: `--add-dir ../lib`. Isolation: `--worktree`.
- Model/config per run: `-m <model>`, `-c key=value` (TOML), `-c model_reasoning_effort="high"`, `-p <profile>` (layers `~/.codex/<name>.config.toml`). `--ephemeral` = no session files. `--search` enables live web search.

## Sandbox and approvals (the real guard)
- `codex exec` defaults to read-only; the recommended config (below) sets `sandbox_mode = "workspace-write"` with network off. Verified on codex-cli 0.166.0 (Linux) with `codex sandbox -P :workspace`: writes cwd only, `$HOME` and `/etc` read-only, no network, and `.git/` is read-only (Codex cannot commit; the operator commits).
- `-s read-only` for analysis/review; `-s workspace-write` for edits; `danger-full-access` / `--dangerously-bypass-approvals-and-sandbox` only in a throwaway container or VM.
- Network for installs/tests: `-c sandbox_workspace_write.network_access=true` for that run only.
- exec is non-interactive: anything needing approval fails back to the model. `--approve-for-me` routes approvals to automatic review (docs). `--full-auto` and `approval_policy="untrusted"` are gone.
- Execpolicy rules: `$SKILL_DIR/rules/guard.rules` (symlink it into `~/.codex/rules/`) forbids git push/remote, gh writes, publish, deploy CLIs, `sudo`, `rm -rf /`, reading a secrets folder (edit the path to yours). Check: `codex execpolicy check --rules rules/guard.rules git push` → forbidden (verified). Rules govern commands Codex asks to run outside the sandbox; never pass `--ignore-rules`.
- Repo `.codex/` config, rules and hooks load only for trusted projects; never use `--dangerously-bypass-hook-trust`.

## Follow-ups
`codex exec resume <thread_id> "next step" --json -o ... </dev/null` (id from `thread.started`; a thread name also works). `--last` = newest session in cwd (add `--all` to ignore cwd); avoid with parallel runs. Note: `resume` has no `-s`/`-C` flags; run it from the same dir and pass sandbox via `-c sandbox_mode="workspace-write"`. Fork: `codex exec fork <id> "prompt"`. *(not tested live)*
Sessions: `~/.codex/sessions/YYYY/MM/DD/rollout-<ts>-<id>.jsonl`; manage with `codex archive|delete|unarchive <id>`.

## Long jobs
```bash
nohup codex exec --json -s workspace-write -C /workspace/<p> -o /workspace/<p>/.cx.last "$PROMPT" </dev/null > /workspace/<p>/.cx.jsonl 2>&1 &
```
Background the Shell call and await; done when a `turn.completed` or `turn.failed` line appears.

## Review mode
`codex exec review --uncommitted` | `--base main` | `--commit <sha>` ["focus on X"] — non-interactive review, read-only is enough (`-c sandbox_mode="read-only"`); good second reviewer of Claude Code / OpenCode output. *(not tested live)*

## AGENTS.md, skills, MCP
- AGENTS.md: global `~/.codex/AGENTS.md`, then repo root → cwd `AGENTS.md` (`AGENTS.override.md` wins) (docs/agents-md.md). Put stable project facts there.
- Skills: user skills in `~/.agents/skills` (symlinks allowed), repo `.agents/skills`, bundled `.system` (docs/build-skills.md). Mention `$skill-name` in the prompt to force one.
- MCP: `[mcp_servers.<name>]` in `~/.codex/config.toml` or `codex mcp add <name> -- <cmd>`; `required = true` makes exec fail if it won't start (docs/mcp.md). Disable a heavy server for one run with `-c mcp_servers.<name>.enabled=false`.

## Writing the prompt
Goal (one sentence) · Context (files, stack, how to run) · Constraints (no new deps; do not commit or push) · Tests (exact command, e.g. `uvx pytest -q`) · Done criteria · Output (summary of changed files + anything unverified).

## Verify, don't trust
1. Last event is `turn.completed` (not `turn.failed`/`error`); read usage.
2. `git status --short && git diff --stat`, then read the diff.
3. Run the tests yourself (`uvx pytest`, `npm test`); its summary is a claim.
4. Look for `command_execution` items with non-zero `exit_code` and sandbox denials.

## Safety
- Never let it push, deploy, publish, send messages or touch secrets without the user's explicit OK; keep network off by default and the guard rules on.
- Never put keys in prompts. ChatGPT auth lives in `~/.codex/auth.json` (secret; don't print). Don't set `CODEX_API_KEY`/`OPENAI_API_KEY` in runs that execute repo code.
