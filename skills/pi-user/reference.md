# pi cheat-sheet (v1.4.0, checked against docs/cli.md + `pi --help`, 2026-10-31)
Full docs: docs/README.md. `--help` of the installed version is authoritative.

## Modes
-p/--print (one-shot, final text to stdout) · --mode text|json|rpc · piped stdin is prepended to the first prompt · `pi -p -- "- prompt starting with dash"` · @file args attach files/images
--export <session.jsonl> [out.html] · --list-models [search] · --offline (PI_OFFLINE=1) · --verbose

## Session
--continue/-c · --resume/-r (picker; TUI) · --session <path|partial-uuid> · --session-id <id> (exact, create if missing) · --fork <path|id> · --session-dir <dir> · --no-session · --name/-n <name>
Store: ~/.pi/agent/sessions/<cwd-slug>/*.jsonl (docs/session-format.md). TUI: /session /tree /fork /clone /compact /name /share.

## Model
--model <pattern|provider/id[:thinking]> · --provider <name> (with --model) · --models a,b (Ctrl+P cycle) · --thinking off|minimal|low|medium|high|xhigh|max · --api-key (avoid; env/wrapper instead)

## Tools & resources
--tools/-t a,b,'mcp__srv__*' (allowlist; +x/-x edit defaults; keep codemode for MCP) · --exclude-tools/-xt · --no-tools/-nt · --no-builtin-tools/-nbt
Built-in: read bash edit write (+ grep find ls off by default; powershell on Windows); codemode, tool_search (built-in extensions)
-e/--extension <file|builtin:name> · -ne (no extension discovery, also disables builtin:mcp) · --no-mcp · --skill <path> · -ns · --prompt-template · -np · -nc (no AGENTS.md/CLAUDE.md)
--system-prompt (replace) · --append-system-prompt <text|file> (repeatable) · -a/--approve (trust project .pi) · -na/--no-approve

## Subcommands
pi mcp add <n> [--env K=V --cwd d --exposure codemode|deferred|direct|hidden --description t] -- <cmd> | --url <u> [--header K=V --bearer-token-env-var N] · pi mcp list [--json] (exit 1 on failure) · pi mcp remove|login|logout <n> · -l = project .pi/mcp.json
pi install|remove|list|update [source|self] (packages: extensions/skills/prompts/themes) · pi config [-l] (TUI) · pi auth check|print-api-key|print-bearer-token (prints secrets!)

## JSON events (docs/json.md)
1st: {"type":"session","version":3,"id","timestamp","cwd"} · agent_start · turn_start · message_start/update/end · tool_execution_start/update/end {toolName,isError,result} · turn_end · agent_end {messages} · agent_settled {aborted}
Assistant message: content[] (thinking|text|toolCall), model, stopReason (stop|toolUse|error|aborted|length), usage {input,output,cacheRead,cacheWrite,reasoning,totalTokens,cost{total}}.
RPC (docs/rpc*.md): stdin JSONL commands {id,type:"prompt"|"steer"|"follow_up"|"abort"|"get_state"|"set_model"|"compact"…} → responses + same events, no session header.

## Config (docs/configuration.md, settings.md)
~/.pi/agent/: settings.json · mcp.json · models.json · auth.json (secret) · skills/ · extensions/ · prompts/ · AGENTS.md · SYSTEM.md/APPEND_SYSTEM.md
Project .pi/: same names, loaded only after project trust. settings: defaultProvider, defaultModel, defaultThinkingLevel, defaultTools, extensions (builtin:mcp|llama.cpp|codemode|tool-search, "-builtin:x" disables), compaction.*, retry.*, sessionDir, quietStartup.
Env: PI_CODING_AGENT_DIR · PI_CODING_AGENT_SESSION_DIR · PI_OFFLINE · PI_TELEMETRY · OPENROUTER_API_KEY (via wrapper).

## Extensions (docs/extensions.md)
TS module `export default function (pi: ExtensionAPI) { pi.on("tool_call", async (e) => ({ block: true, reason })) }` — events: session_start, before_agent_start, tool_call (block/mutate input), tool_result, turn_end, agent_end… Our guard: hooks/guard.ts.

## Setup notes
Install the `@earendil-works/pi-coding-agent` package (1.x). Optional: register MCP servers with `pi mcp add`, put skills in ~/.pi/agent/skills. Without system pytest use `uvx pytest`.

## Live tests (2026-10-31, OpenRouter xiaomi/mimo-v2.6-pro)
1. `-p --mode json -e guard.ts --thinking low "Reply with exactly: PONG"` → PONG, session header id, $0.0028 (6.5k input tokens).
2. `--session 01a19327 "What did you reply last time?"` → PONG, same session id (resume OK).
3. Guard: asked to run `git push origin main` → tool_execution_end isError "Blocked by guard…", model reported it and stopped, $0.0002.
4. MCP: count design systems via an Open Design MCP server → codemode → mcp__open_design__list_open_design_design_systems → 198, $0.0026.
Note: `-p --tools read` + an MCP request produced no output within 120 s (codemode not in allowlist) — include codemode.
