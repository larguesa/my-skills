# Claude Code official docs (markdown copies)
Downloaded 2026-10-31 from https://code.claude.com/docs/en/<file>. Refresh: `./update.sh`.

| File | Source | Summary / when to consult |
|---|---|---|
| llms.txt | https://code.claude.com/docs/llms.txt | Index of every docs page with one-line descriptions. Use it to find a page not copied here (permissions, settings, sub-agents, model-config…) and fetch its `.md`. |
| headless.md | https://code.claude.com/docs/en/headless.md | Running `claude -p` programmatically: bare mode, output formats, json-schema, stream-json events, auto-approving tools, `--permission-prompts none`, resume. Primary reference for headless use. |
| cli-reference.md | https://code.claude.com/docs/en/cli-reference.md | Every subcommand and flag, plus system-prompt flags and how they snapshot on resume. Consult before using any flag. |
| commands.md | https://code.claude.com/docs/en/commands.md | Built-in slash commands (/rewind, /model, /compact, /review…). Consult when putting a slash command in a prompt or guiding an interactive session. |
| env-vars.md | https://code.claude.com/docs/en/env-vars.md | All environment variables (timeouts, models, effort, Bash limits, telemetry, auth tokens) and precedence vs flags. Consult when tuning behaviour without flags. |
| tools-reference.md | https://code.claude.com/docs/en/tools-reference.md | Built-in tools (Bash, Edit, Read, Glob, Grep, WebFetch, Agent, tasks…) and their behaviour. Consult when writing --tools/--allowedTools rules. |
| interactive-mode.md | https://code.claude.com/docs/en/interactive-mode.md | Keyboard shortcuts, input modes, vim mode, background bash, prompt suggestions. Consult only when a person drives the TUI. |
| checkpointing.md | https://code.claude.com/docs/en/checkpointing.md | Automatic snapshots and /rewind; limits (Bash/subagent/external edits not tracked). Consult before relying on undo; prefer git. |
| hooks.md | https://code.claude.com/docs/en/hooks.md | Hook events, matchers, input/output JSON, exit-code semantics, decision control. Consult when adding guards or automation (e.g. ../hooks/guard.sh). |
| channels-reference.md | https://code.claude.com/docs/en/channels-reference.md | Research-preview channels: MCP servers pushing chat/webhook events into a session, reply tools, permission relay. Consult when building a remote/gateway bridge. |
| glossary.md | https://code.claude.com/docs/en/glossary.md | Definitions of Claude Code terms (turn, compaction, system reminder, subagent…). Consult when a doc term is unclear. |
