---
name: antigravity-user
description: Drive the Google Antigravity CLI (`agy`) headless as a user or agent - when to delegate (vs Claude Code, Codex, pi, OpenCode), standard `agy -p --output-format stream-json` invocation, reading events and silent permission denials, permissions allow/deny rules guard, execution modes and terminal sandbox, resume, structured output, repo hooks risk, AGENTS.md, skills, MCP, Google plan quotas, verification, plus a cheat-sheet and the official Antigravity CLI docs in markdown. Use when delegating coding work to Antigravity or looking up its flags, settings, permissions, sandbox, hooks, rules, skills or MCP.
---

# Antigravity user: driving `agy` headless (tested on agy 1.4.2, Windows)

`$SKILL_DIR` = this skill's folder (e.g. `~/.gemini/config/skills/antigravity-user`). Cheat-sheet: `reference.md`. Official docs (markdown, 2026-11-08) in `docs/` — see `docs/README.md`; refresh with `docs/update.sh`. Items marked *(not tested live)* come from the docs only.

## Recommended setup
Install: `curl -fsSL https://antigravity.google/cli/install.sh | bash` (macOS/Linux) or `irm https://antigravity.google/cli/install.ps1 | iex` (Windows). Run `agy` once interactively to sign in with the Google account: headless reuses the cached login (kept in the OS keyring) and, with no terminal, exits with `authentication required` instead of prompting. API-key alternative for CI: `"modelProvider": "gemini"` in settings plus `GEMINI_API_KEY` in the environment (docs/install.md).
Back up `~/.gemini/antigravity-cli/settings.json`, then merge `$SKILL_DIR/rules/guard-permissions.json` (see `rules/README.md`) and add allow rules for the commands runs may execute unattended:
```json
{ "permissions": { "allow": ["command(git status)", "command(git diff)", "command(regex:(uv run |uvx )?pytest.*)", "command(regex:npm (test|run (build|lint|test)).*)"] } }
```
Settings are global only (no per-run settings flag); the CLI rewrites the file at startup and ignores rules it can't parse.

## When to delegate (and to whom)
- **Antigravity**: tasks where Gemini models are wanted, a second opinion beside Claude Code/Codex, or Claude/GPT-OSS models billed to the Google plan (`agy models` lists what the account has). Browser subagent (`/browser`), `/goal`, `/teamwork` exist but are interactive-first *(not tested live)*.
- **Claude Code / Codex** (skills `claude-code-user`, `codex-user`): their own subscriptions; Claude Code for the biggest multi-file features.
- **OpenCode / pi** (skills `opencode-user`, `pi-user`): pay-per-token on any provider; bulk and parallel work off subscription quota.
- **Yourself**: one-line edits, reading files, shell admin, anything needing the user's connectors or externally visible.
- Quota: model groups (Gemini Flash/Pro, Claude+GPT) share a weekly and a 5-hour limit, shared with the user's own Antigravity use; check with `/usage` in interactive `agy` (`agy -p /usage` did not work headless). Keep `useG1Credits` off: it spends paid AI credits after the quota runs out. One well-specified run beats many small ones; pick a `-low`/`flash` model for small jobs.

## Standard invocation
```bash
cd /workspace/<project> && git status --short          # baseline; the workspace is the cwd (no -C flag)
agy -p "$PROMPT" \
  --output-format stream-json \
  --mode accept-edits \
  --model gemini-3.8-flash-medium \
  --print-timeout 30m \
  </dev/null > /tmp/ag_<task>.jsonl 2>/tmp/ag_<task>.err
jq -c 'select(.event=="result") | .result | {status,conversation_id,num_turns,usage,error}' /tmp/ag_<task>.jsonl
jq -r 'select(.event=="step_update" and .step_update.state=="ERROR") | .step_update.tool_info.error.message' /tmp/ag_<task>.jsonl
cat /tmp/ag_<task>.err                                   # permission notices live here
```
- Events: one `init` (cwd, tools, `permission_mode`), `step_update` per step (`step_type` user_input|agent_response|tool|checkpoint; `state` ACTIVE|DONE, and ERROR when a tool fails or is denied — seen live, not in the docs), one `result` (same shape as `--output-format json`). Tool steps carry `tool_name` and `tool_info{name,parameters,output,error}`. Response text = `text_delta`s, or `.result.response`.
- `--output-format json` gives just the final envelope: `conversation_id`, `status` (SUCCESS|ERROR|CANCELED|INTERRUPTED|INVALID|WAITING|RUNNING), `response`, `error`, `duration_seconds`, `num_turns`, `usage{input,output,thinking,cache_read,total}_tokens`.
- **Silent denials**: a tool that needs approval is soft-denied in headless — the run goes on, exits 0 with `status: SUCCESS`, sometimes with an empty `response`, and stderr says `a tool required the "command" permission that headless mode cannot prompt for, so it was auto-denied`. Always read stderr. Seen live: in default mode workspace edits still applied and only commands were denied.
- Unknown `--model` → `status: ERROR`, exit 1 (no silent fallback). `--effort low|medium|high|xhigh|max` (model-dependent). `--agent <name>` (`agy agents`). `--add-dir DIR` widens the workspace.
- `--json-schema '<schema>|file.json|integer'` → `.structured_output` (adds a turn; `response` may hold extra text).
- Prompts starting with `/` run slash commands or skills; `--disable-slash-commands` sends them as text.

## Permissions, modes, sandbox (the real guard)
- Rules `action(target)` in `permissions.allow|ask|deny`; deny > ask > allow. Actions: `command(prefix|regex:...)`, `read_file(path)`, `write_file(path)` (write implies read; deny read implies deny write), `read_url(domain)`, `execute_url(domain)` (browser), `mcp(server/tool)`, `unsandboxed(...)` (business accounts). Paths are absolute or workspace-relative; `~` is not expanded. On Windows use `regex:` for commands (non-splittable ones need exact match otherwise) and `C:/...` paths (docs/permissions.md).
- Guard: `rules/guard-permissions.json` denies push, remotes/config, gh writes, publish, deploy CLIs, mutating curl, sudo, `rm -rf /`, `.secrets`, root `.env`. Verified on 1.4.2: blocked even with `command(git)` allowed, chained `echo hi && git push` included.
- Modes (`--mode` or `agentMode`): default (edits reviewed, commands Ask), `accept-edits` (edits auto-approved; commands by rules), `plan` (research and plan, no code), `auto` (sandboxed commands run, risky ones still ask; macOS/Linux 1.3.5+, Windows 1.4.4+, needs the sandbox, personal accounts only).
- Terminal sandbox: `--sandbox` or `"enableTerminalSandbox": true` + `"toolPermission": "proceed-in-sandbox"`; writes workspace/temp/caches, no network except `read_url`-allowed domains, blocks `~/.ssh` and `.env` (Linux namespaces, macOS seatbelt, Windows AppContainer on 11 24H2 + Aug 2026 update). Unavailable → flags have no effect *(not tested live)*.
- `--dangerously-skip-permissions` (`always-proceed`) approves everything except deny rules; only in a throwaway container or VM *(not tested live)*.

## Follow-ups
`agy -p "next step" --conversation <conversation_id> --output-format json ... </dev/null` (verified: same id, `num_turns` and `usage` cumulative). `-c/--continue` = most recent conversation in the cwd; avoid with parallel runs. Conversations are scoped to the working directory. `/fork` is interactive-only.
Multi-turn in one process: `--input-format stream-json --output-format stream-json`, one `{"event":"user","message":{"content":"..."}}` per stdin line, one `result` per turn, close stdin to end; no `-p`, no CLI slash commands like `/model` (docs/headless.md) *(not tested live)*.

## Long jobs
```bash
nohup agy -p "$PROMPT" --output-format stream-json --mode accept-edits --print-timeout 2h </dev/null > /workspace/<p>/.ag.jsonl 2> /workspace/<p>/.ag.err &
```
Background the Shell call and await; done when a line with `"event":"result"` appears. Subagents (`invoke_subagent`, optional git worktree) show as `subagent_info` on tool steps.

## Repo config runs without asking
Headless loads the workspace's `.agents/hooks.json` and ran its `SessionStart` hook even in a folder never trusted (verified 1.4.2). Workspace `.agents/mcp_config.json` servers and `.agents/plugins/` load per workspace too (docs/settings.md). Inspect an unknown repo's `.agents/` before running `agy` in it.

## AGENTS.md, skills, MCP
- Rules: `AGENTS.md` or `GEMINI.md` (also under `.agents/`) and `.agents/rules/*.md` (frontmatter `trigger` required) from the workspace up to the repo root; global `~/.gemini/AGENTS.md` or `~/.gemini/config/rules/*.md` (docs/rules.md).
- Skills: `.agents/skills/<name>/`, global `~/.gemini/config/skills/<name>/`; the CLI also reads `~/.gemini/antigravity-cli/skills/` and `~/.gemini/skills/` (docs/skills.md).
- MCP: `~/.gemini/config/mcp_config.json` or `.agents/mcp_config.json`, `{"mcpServers":{"name":{"command":...}|{"serverUrl":...}}}`; manage with `agy mcp add|remove|list|enable|disable`; headless tool calls need `mcp(server/*)` allow rules (docs/mcp.md).

## Writing the prompt
Goal (one sentence) · Context (files, stack, how to run) · Constraints (no new deps; do not commit or push) · Tests (exact command, matching an allow rule) · Done criteria · Output (summary of changed files + anything unverified).

## Verify, don't trust
1. `result.status` is SUCCESS and `response` is not empty; read stderr for auto-denied tools.
2. List tool steps with `state: "ERROR"` (denials, failures).
3. `git status --short && git diff --stat`, then read the diff.
4. Run the tests yourself; its summary is a claim, not proof.

## Safety
- Never let it push, deploy, publish, send messages or touch secrets without the user's explicit OK; keep the guard rules on and allow rules narrow.
- Never put keys in prompts. The login sits in the OS keyring; don't export `GEMINI_API_KEY` in runs that execute repo code unless needed.
- Report status, model and token usage (`usage`; on a Google plan it's quota, not money, unless AI credits are on).
