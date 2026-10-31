# Claude Code cheat-sheet (v2.1.316, checked against docs/cli-reference.md + `claude --help`, 2026-10-31)
Note: `--help` doesn't list every flag (docs say so). Full docs: docs/README.md.

## Print-mode flags
-p/--print · --output-format text|json|stream-json (stream-json needs --verbose) · --input-format text|stream-json
--json-schema '<schema>' → .structured_output · --max-turns N (error_max_turns) · --max-budget-usd N (estimate, can overshoot)
--no-session-persistence · --permission-prompts host|none · --permission-prompt-tool mcp__srv__tool
--include-partial-messages · --include-hook-events · --forward-subagent-text · --replay-user-messages · --prompt-suggestions
--append-subagent-system-prompt[-file] · --exclude-dynamic-system-prompt-sections · --init / --maintenance (Setup hooks)

## Session
--resume/-r <id|name|path.jsonl> · --continue/-c · --fork-session · --session-id <uuid> · --name/-n · --worktree/-w <name>
--bg (background agent; not with -p) · claude agents --json · claude logs|attach|stop <id>

## Model
--model sonnet|opus|haiku|fable|<full id> · --fallback-model a,b (chain) · --effort low|medium|high|xhigh|max|ultracode · --advisor opus · --autocompact <auto|tokens>

## Permissions & tools
--permission-mode default(=manual)|acceptEdits|plan|auto|dontAsk|bypassPermissions (-p defaults to Manual since v2.1.302)
--allowedTools "Read" "Bash(git diff *)" (pre-approve) · --disallowedTools "Bash(rm *)" "mcp__*" (deny/remove) · --tools "Bash,Edit,Read" | "" | "default" (restrict set)
--dangerously-skip-permissions = bypassPermissions (sandbox only) · --restricted (no command tools, managed + --settings only)

## Context & config
--append-system-prompt[-file] (keep defaults) · --system-prompt[-file] (replace all) · --system-prompt-snapshot off
--add-dir <dirs> · --settings <file|json> · --setting-sources user,project,local · --mcp-config <files> · --strict-mcp-config
--agents '<json>'|file · --agent <name> · --plugin-dir · --disable-slash-commands · --safe-mode (no customizations, keeps auth) · --bare (NOT with our OAuth login)
--debug='mcp,startup' · --debug-file <path>

## Subcommands
claude auth status (exit 0 if logged in; authMethod) · claude doctor · claude update · claude mcp add|list|remove|login · claude plugin ... · claude purge <path> --dry-run · claude setup-token (long-lived OAuth for scripts; prints secret, don't log)

## JSON result fields (observed)
type, subtype (success|error_max_turns|error_during_execution|…), is_error, result, structured_output, session_id, num_turns, duration_ms, total_cost_usd (cumulative on resume), usage, modelUsage {model:…}, permission_denials [{tool_name,tool_input}], stop_reason. stream-json: first system/init, system/api_retry, last type=result.

## Env vars (docs/env-vars.md)
API_TIMEOUT_MS (default 600000) · ANTHROPIC_MODEL (flag overrides) · CLAUDE_CODE_EFFORT_LEVEL (overrides --effort) · CLAUDE_CODE_SUBAGENT_MODEL · CLAUDE_CODE_MAX_TURNS · BASH_DEFAULT_TIMEOUT_MS / BASH_MAX_TIMEOUT_MS / BASH_MAX_OUTPUT_LENGTH · MCP_TIMEOUT · CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS · CLAUDE_CODE_DISABLE_AUTO_MEMORY · CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC · CLAUDE_CODE_OAUTH_TOKEN (secret)

## Hooks (docs/hooks.md)
settings "hooks": {Event:[{matcher, hooks:[{type:"command",command}]}]}. Events: SessionStart, Setup, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, Stop, SubagentStop, PreCompact, SessionEnd, Notification…
Input JSON on stdin (.tool_name, .tool_input). Exit 0 = no decision · exit 2 = block (stderr shown to Claude, beats JSON allow) · other = non-blocking error. Guard: hooks/settings-guard.json.

## Checkpointing (docs/checkpointing.md)
Auto snapshot before each prompt, only Edit/Write-tool changes; /rewind (interactive), 100 checkpoints, ~30-day retention. Not Bash/subagent/external changes → use git.

## Config locations
~/.claude/settings.json · .claude/settings.json · .claude/settings.local.json · CLAUDE.md (project, ~/.claude/CLAUDE.md) · skills ~/.claude/skills or .claude/skills · agents .claude/agents · MCP .mcp.json.
Slash commands usable in a -p prompt: "/skill-name …" (docs/commands.md for the list).

## Setup notes
Optional: put other skills in ~/.claude/skills (or .claude/skills) so Claude Code can load them. Without system pytest use `uvx pytest`.

## Live tests
2026-10-31 base: create+resume run, 29 tests passed, opus. Flags test: --json-schema + --append-system-prompt + --tools Read + --max-budget-usd + --no-session-persistence → structured_output {"functions":["add","sub"]}, haiku, $0.11 est (num_turns 4 with --max-turns 3: schema adds a turn). --fallback-model haiku with bogus --model → answered on claude-haiku-5-5 (warning unrecognized_model on stderr). --settings guard hook → `git push` blocked, Claude reported it and didn't retry, $0.11 est.
