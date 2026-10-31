---
name: pi-user
description: Drive pi (the `pi` coding agent CLI, pi.dev) headless as a user or agent - when to delegate, standard `pi -p --mode json` invocation, sessions and resume, RPC mode, models, native MCP, a guard extension, verification and cost, plus a cheat-sheet and the official pi docs in markdown. Use when delegating coding work to pi or looking up its flags, JSON events, RPC commands, settings, MCP, skills or extensions.
---

# pi user: driving pi headless (tested on v1.4.0, @earendil-works/pi-coding-agent)

`$SKILL_DIR` = this skill's folder (e.g. `~/.pi/agent/skills/pi-user`, `~/.claude/skills/pi-user` or wherever you copied it). Cheat-sheet: `reference.md`. Official docs (markdown, 2026-10-31) in `docs/` — see `docs/README.md`; refresh with `docs/update.sh`.
Install: `npm i -g @earendil-works/pi-coding-agent` (the old `@mariozechner/pi-coding-agent` package stops at 0.73.x, without native MCP). Give it a provider key via env (e.g. `OPENROUTER_API_KEY`) or `/login`; a small wrapper script that loads the key from a chmod-600 file keeps it out of your shell profile.

## When to use pi (vs Claude Code vs doing it yourself)
- pi: cheap, model-agnostic coding/scripting runs on any provider (e.g. OpenRouter, paid per token), quick generation tasks, design work via MCP servers, comparing models (`--model`), long-lived agents over RPC (gateways).
- Claude Code: hard multi-file work where quality matters most (subscription quota).
- Yourself: one-line edits, reading, shell admin, anything needing connectors or externally visible actions.

## Standard invocation
```bash
cd <project> && git status --short          # baseline; git repo preferred
pi -p --mode json \
  -e "$SKILL_DIR/hooks/guard.ts" \
  --thinking low --name "<task>" \
  "$PROMPT" </dev/null > /tmp/pi_<task>.jsonl 2>/tmp/pi_<task>.err
S=$(head -1 /tmp/pi_<task>.jsonl | jq -r .id)                             # session id
jq -r 'select(.type=="agent_end")|.messages[-1].content[]?|select(.type=="text").text' /tmp/pi_<task>.jsonl
jq -s '[.[]|select(.type=="message_end" and .message.role=="assistant")|.message.usage.cost.total]|add' /tmp/pi_<task>.jsonl   # USD
```
- Always `</dev/null` (it waits on stdin otherwise). `-p` = one-shot; `--mode json` = JSONL events (docs/json.md); first record is the session header with `.id`.
- Exit status: print mode exits nonzero on error/aborted/length; in JSON mode a failed reply does NOT set the exit code — check the last assistant `stopReason` and `agent_settled.aborted` (docs/cli-integration.md).
- Tools: default `read,bash,edit,write` (+ MCP via codemode). Read-only review: `--tools read,grep,find,ls`. `--tools` is an allowlist: keep `codemode` in it if you need MCP. `--exclude-tools bash` denies. `--no-mcp` disconnects MCP.
- Throwaway: `--no-session`. Fixed id: `--session-id <id>`. Untrusted repo: `-na` (ignore project `.pi/` files); `-a` trusts them.

## Follow-ups
`pi -p --mode json -e "$SKILL_DIR/hooks/guard.ts" --session "$S" "next step" </dev/null` (partial UUID works; runs in the session's original cwd). `--fork "$S"` branches into a new session in the current dir. `-c` = most recent session in cwd (avoid with parallel runs). Cost lines in the new run are for that run only. Sessions: `~/.pi/agent/sessions/`.

## Long jobs / persistent driver
Background the Shell call with `--mode json` and read the JSONL; `agent_settled` marks the real end (retries/compaction may follow `agent_end`). For a long-lived agent (gateway, IDE-like driver) use `pi --mode rpc` and send JSONL commands (`prompt`, `steer`, `abort`, `get_state`) — docs/rpc.md, rpc-commands.md. Embedding in Node: docs/sdk.md.

## Models (OpenRouter)
Default from `~/.pi/agent/settings.json` (e.g. `{"defaultProvider":"openrouter","defaultModel":"xiaomi/mimo-v2.6-pro"}`). Override per run: `--model openrouter/<vendor>/<id>` or `--model <id>:high`. `--thinking off|minimal|low|medium|high|xhigh|max`. List: `pi --list-models mimo`. Unlisted models / routing: docs/models-configuration.md, virtual-models.md. Check current models before changing the default.

## MCP (native since 1.x)
Register a server globally in `~/.pi/agent/mcp.json`, e.g. `pi mcp add open-design -- open-design-mcp`; `pi mcp list` shows state and tools (tested: connected, 34 tools, exposure `codemode` — the model calls `mcp__open_design__*` from a codemode script). Other servers: `pi mcp add <name> -- <cmd>` or `--url`. Project `.pi/mcp.json` loads only in trusted projects. docs/mcp.md, codemode.md.

## Skills
Global skills in `~/.pi/agent/skills/`. Add one-off: `--skill <dir>`; disable: `-ns`. docs/skills.md.

## Guard (always load it)
pi has no approval prompts: every tool call runs with your user's permissions (docs/security.md). `hooks/guard.ts` is an extension whose `tool_call` handler blocks bash `git push`, mutating `curl -X POST/PUT/DELETE/PATCH`, `.secrets`/`.env` access, `rm -rf /`, and read/write/edit of `.secrets`, `.env` or `auth.json`; the model gets "Blocked by guard…" as an error result. It's a tripwire, not a sandbox (a script could still do it indirectly) — for untrusted code use a container (docs/containerization.md).

## Writing the prompt
Goal · Context (files, stack, how to run) · Constraints (no new deps, no commit/push) · Tests (exact command; system pip is PEP-668 locked → `uvx pytest`/`uv run`) · Done criteria · Output (short summary of changed files + anything unverified). Stable project facts go in AGENTS.md (pi reads AGENTS.md and CLAUDE.md; `-nc` disables).

## Verify, don't trust
1. Last assistant message `stopReason` is `stop` (not `error`/`aborted`/`length`); no `isError` tool results you didn't expect (`jq 'select(.type=="tool_execution_end" and .isError)'`).
2. `git diff --stat`, read the diff. pi has no checkpoints/undo: rely on git.
3. Run the tests yourself.

## Safety & cost
- Never let it push, deploy, publish, send messages or touch secrets without the user's explicit OK; keep the guard on.
- Never put keys in prompts or print them; keep them in env vars or chmod-600 files outside the repo (`pi auth print-api-key` prints a secret — don't run it).
- Report cost (sum of `usage.cost.total`, USD) and model (`.message.model`). A tiny prompt costs ~$0.003 (≈6.5k input tokens of system prompt).
