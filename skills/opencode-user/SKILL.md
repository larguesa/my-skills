---
name: opencode-user
description: Drive OpenCode (the `opencode` CLI) headless as a user or agent - when to delegate, standard `opencode run --format json` invocation, JSON events and cost, sessions and resume, serve/attach, agents, models, MCP, permission-rule guard, verification, plus a cheat-sheet and the official OpenCode docs in markdown. Use when delegating coding work to OpenCode or looking up its commands, config, permissions, agents, tools, MCP, skills or server API.
---

# OpenCode user: driving OpenCode headless (tested on v1.19.5, opencode-ai)

`$SKILL_DIR` = this skill's folder (e.g. `~/.config/opencode/skills/opencode-user` or wherever you copied it). Cheat-sheet: `reference.md`. Official docs (markdown, 2026-10-31) in `docs/` — see `docs/README.md`; refresh with `docs/update.sh`.
Install: `npm i -g opencode-ai`. Give it a provider key via env (e.g. `OPENROUTER_API_KEY`, referenced in opencode.json as `{env:OPENROUTER_API_KEY}`) or `opencode providers login`; a small wrapper that loads the key from a chmod-600 file keeps it out of your shell profile. Config: `~/.config/opencode/opencode.json` (back it up before edits).

## When to use OpenCode (vs pi vs Claude Code vs doing it yourself)
- OpenCode: model-agnostic coding on OpenRouter (any provider, e.g. `openrouter/xiaomi/mimo-v2.6-pro`, paid per token) with real permission rules, built-in plan/build agents, subagents, LSP diagnostics, MCP servers, and an HTTP server (`serve`) for persistent/remote driving.
- pi: lighter/cheaper prompt (~6.5k tokens vs ~13k–36k here), RPC mode; no permission engine.
- Claude Code: hardest multi-file work (subscription quota). Yourself: trivial edits, connectors, anything externally visible.

## Standard invocation
```bash
cd <project> && git status --short          # baseline; git repo preferred
OPENCODE_CONFIG_CONTENT='{"mcp":{"open-design":{"enabled":false}}}' \
opencode run --format json --title "<task>" "$PROMPT" </dev/null > /tmp/oc_<task>.jsonl 2>/tmp/oc_<task>.err
S=$(head -1 /tmp/oc_<task>.jsonl | jq -r .sessionID)
jq -r 'select(.type=="text").part.text' /tmp/oc_<task>.jsonl                       # answer
jq -s '[.[]|select(.type=="step_finish").part.cost]|add' /tmp/oc_<task>.jsonl      # USD
jq -c 'select(.type=="tool_use")|{tool:.part.tool,status:.part.state.status}' /tmp/oc_<task>.jsonl
```
- Always `</dev/null`. `--format json` = JSONL events: `step_start`, `text`, `tool_use` (part.state.status completed|error), `step_finish` (part.cost, part.tokens), each with `sessionID`.
- The `OPENCODE_CONFIG_CONTENT` line disables an MCP server you don't need for this run (example: an `open-design` server). In tests, Open Design MCP + its skills cost ~23k extra input tokens per step ($0.015 vs $0.006 for a tiny prompt).
- Agents: default `build` (full tools). `--agent plan` = analysis only (edits denied except plan files). Subagents `general`/`explore` are used via the task tool.
- "ask" rules are auto-rejected in `run` (stderr: "permission requested: external_directory (/etc/*); auto-rejecting"; the tool_use gets status error). Paths outside the cwd hit `external_directory` (ask) — start in the project dir or add allow rules. `--auto` approves all non-denied asks (explicit `deny` still wins): only for wide unattended runs inside a throwaway project dir.
- Keep stderr separate (`2>file`): warnings are not JSON. If mixed, parse with `jq -R 'fromjson?'`.
- Cap agentic loops with an agent `steps` value (docs/agents.md "Max steps"), e.g. `OPENCODE_CONFIG_CONTENT='{"agent":{"build":{"steps":25}}}'`.

## Follow-ups
`opencode run --format json -s "$S" "next step" </dev/null` (same session, history kept). `--fork` with `-s`/`-c` branches first. `-c` = last session (avoid with parallel runs). `--command <name>` runs a custom command with the message as args. List: `opencode session list`; export JSON: `opencode export $S`.

## Persistent / remote
`opencode serve --port 4096` (localhost; set `OPENCODE_SERVER_PASSWORD` before exposing) then `opencode run --attach http://localhost:4096 ...` to skip MCP cold start each run, or drive it over HTTP (docs/server.md: POST /session, /session/:id/message, /event SSE, /session/:id/permissions/:id) or the JS SDK (docs/sdk.md). `opencode web` gives a browser UI. Background the Shell call; stop with SIGINT.

## Models (OpenRouter)
`-m openrouter/<vendor>/<id>`; `--variant high|max|minimal` for reasoning effort. List: `opencode models openrouter`. Usage history: `opencode stats`. Check current models before changing the default.

## MCP & skills
MCP servers live under `mcp` in opencode.json (e.g. `"open-design": {"type":"local","command":["open-design-mcp"],"enabled":true}`). `opencode mcp list` shows status. Skills load from `~/.config/opencode/skills`, and also `~/.claude/skills`, `~/.agents/skills`, project `.opencode/skills`, `.claude/skills` (docs/skills.md). Disable `.claude` loading: `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1`.

## Guard (global, always on)
`$SKILL_DIR/hooks/guard-permissions.json` is meant to be merged into opencode.json `permission`: bash `git push*`, `curl * -X POST/PUT/DELETE/PATCH*`, `*.secrets*`, `rm -rf /…` → deny; read/edit of `*.env`, `*/.secrets/*`, `*auth.json` → deny. Rules are wildcard, last match wins, bash matches each parsed command (docs/permissions.md). The model gets "The user has specified a rule which prevents you…" as a tool error. Re-apply after config edits: `jq -s '.[0] * .[1]' opencode.json "$SKILL_DIR/hooks/guard-permissions.json" > new.json` (review, then replace). A per-run variant: `OPENCODE_PERMISSION='<json>'`. Untrusted repo: its `opencode.json`/`.opencode/` are loaded automatically — inspect first, or run with `--pure` (no external plugins).

## Writing the prompt
Goal · Context · Constraints (no new deps, no commit/push) · Tests (exact command; `uvx pytest`/`uv run`, system pip is PEP-668 locked) · Done criteria · Output (changed files + anything unverified). Stable facts in AGENTS.md (`/init` creates it; CLAUDE.md is a fallback).

## Verify, don't trust
1. Last `step_finish` exists and no unexpected `tool_use` with status `error` (denials show up there).
2. `git diff --stat` and read the diff (OpenCode snapshots allow `/undo` in the TUI, but headless rely on git).
3. Run the tests yourself. Logs: `~/.local/share/opencode/log/`.

## Safety & cost
- Never let it push, deploy, publish, send messages or touch secrets without the user's explicit OK; never remove the guard rules.
- Never put keys in prompts or print them; keep them in env vars or chmod-600 files outside the repo (`opencode providers` / auth.json hold secrets).
- Report cost (sum of `step_finish.part.cost`, USD) and model. Tiny prompt: $0.006 without Open Design MCP, $0.015 with it.
