# OpenCode cheat-sheet (v1.19.5, checked against docs/cli.md + `opencode --help` / `run --help`, 2026-10-31)
Full docs: docs/README.md.

## run (non-interactive)
opencode run [message..] · --format default|json · -m/--model provider/model · --variant high|max|minimal · --agent build|plan|<custom> · -f/--file <files> · --title [t]
-c/--continue · -s/--session <id> · --fork (with -c/-s) · --command <name> (message = args) · --dir <path> · --port <n> · --attach <url> [-u user -p password] · --thinking (show) · --auto (approve non-denied asks; dangerous) · -i/--interactive (split-footer)
Global: --pure (no external plugins) · --print-logs · --log-level DEBUG|INFO|WARN|ERROR

## Other commands
serve [--port 4096 --hostname 127.0.0.1 --cors <origin> --mdns] · web · attach <url> · acp · tui: opencode [project]
session list | delete <id> · export [id] (JSON) · import <file> · stats · models [provider] · providers (alias auth) login|list|logout
mcp add|list|auth|logout|debug · agent create|list · plugin <module> · github install|run · pr <number> · upgrade [target] · uninstall · debug … · db

## JSON events (run --format json, observed)
Each line {type, timestamp, sessionID, part}: step_start · text (part.text) · tool_use (part.tool, part.state.{status: completed|error, input, output, error}) · step_finish (part.cost USD, part.tokens{input,output,reasoning,cache{read,write}}, part.reason)

## Config (docs/config.md) — merge order, later wins
remote .well-known → ~/.config/opencode/opencode.json → OPENCODE_CONFIG file → project opencode.json → .opencode/ dirs → OPENCODE_CONFIG_CONTENT (inline JSON)
Keys: model, small_model, provider{openrouter:{options:{apiKey:"{env:OPENROUTER_API_KEY}"}}}, agent{name:{model,prompt,steps,permission,mode,disable}}, permission, mcp{name:{type:local|remote,command[],url,enabled,environment}}, instructions[], command{}, formatter, lsp, snapshot, autoupdate, plugin[]
Substitution: {env:VAR} · {file:path}

## Permissions (docs/permissions.md)
"permission": "allow" | {"*":"ask", "bash":{"*":"allow","git push *":"deny"}, "edit":"deny", "read":{"*.env":"deny"}, "external_directory":{"~/x/**":"allow"}}
Actions allow|ask|deny · wildcards * ? · last matching rule wins · keys: read edit(=edit/write/patch) glob grep bash task todowrite skill lsp question webfetch websearch external_directory doom_loop
Defaults: mostly allow; external_directory + doom_loop ask; *.env read ask. Per agent: agent.<name>.permission. Env: OPENCODE_PERMISSION (inline JSON).

## Agents (docs/agents.md)
Primary: build (all tools), plan (no edits except plan files). Subagents: general, explore (read-only). Hidden: compaction, title, summary. Custom: opencode.json "agent" or .opencode/agents/*.md / ~/.config/opencode/agents/*.md. Option steps = max agentic iterations.

## Tools (docs/tools.md)
bash · edit · write · read · grep · glob · list · patch · todowrite/todoread · webfetch · websearch · question · skill · task · lsp (experimental) — restrict via permission.

## Env vars (docs/cli.md)
OPENCODE_CONFIG · OPENCODE_CONFIG_DIR · OPENCODE_CONFIG_CONTENT · OPENCODE_PERMISSION · OPENCODE_DISABLE_AUTOUPDATE · OPENCODE_DISABLE_AUTOCOMPACT · OPENCODE_DISABLE_CLAUDE_CODE(_PROMPT|_SKILLS) · OPENCODE_DISABLE_LSP_DOWNLOAD · OPENCODE_DISABLE_MODELS_FETCH · OPENCODE_SERVER_PASSWORD / _USERNAME · OPENCODE_EXPERIMENTAL_PLAN_MODE

## Paths
Config ~/.config/opencode/ (opencode.json, skills/, agents/, commands/, AGENTS.md) · data ~/.local/share/opencode/ (auth.json secret, mcp-auth.json, log/, storage) · project: opencode.json, .opencode/{skills,agents,commands,tools,plugins}, AGENTS.md

## Setup notes
Install `opencode-ai` (npm). Merge hooks/guard-permissions.json into your global opencode.json `permission`. Without system pytest use `uvx pytest`.

## Live tests (2026-10-31, OpenRouter xiaomi/mimo-v2.6-pro)
1. `run --format json "Reply with exactly: PONG"` → PONG, sessionID ses_e6cd…, $0.0149 (34k input tokens, Open Design MCP + skills loaded).
2. `run -s ses_e6cd… "What did you reply last time?"` → PONG in the same session, $0.0002 (cache).
3. Guard: "git push origin main + cat a secrets file" → model refused on its own ($0.031). Explicit `git push --help` → tool_use status error "The user has specified a rule which prevents you…", $0.0152.
4. external_directory ask in run: read /etc/hostname → "auto-rejecting", tool_use error "The user rejected permission…", $0.006.
5. Same PONG with OPENCODE_CONFIG_CONTENT disabling open-design → 13.3k input, $0.0058.
