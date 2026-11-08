# Antigravity CLI official docs (markdown copies)
Downloaded 2026-11-08. Each page comes from https://antigravity.google/docs/<slug>.md (index: https://antigravity.google/llms.txt). The CLI pages are every `/docs/cli/*` link in llms.txt; the general pages hold all product tabs (App, CLI, IDE), so look for the "Antigravity CLI" section. Refresh: `./update.sh` (CLI pages are discovered automatically; general pages are a fixed list in the script).

| File | Source slug | Summary / when to consult |
|---|---|---|
| llms.txt | llms.txt | Index of every page with a .md twin. Use it to fetch a page not copied here (boost, goal, teamwork, remote-control, plans…). |
| headless.md | cli/headless | `agy -p`: text/json/stream-json output, event fields, `--json-schema`, resume, stdin streaming, headless permissions, exit codes and status values. Primary reference for our workflow. |
| reference.md | cli/reference | Every slash command, keybinding, startup flag and settings.json key. Consult before using any flag or key. |
| permissions.md | permissions | `action(target)` allow/ask/deny rules, matching, Windows quirks, defaults, modes vs `toolPermission`. Read before widening permissions. |
| sandbox.md | sandbox | Terminal sandbox per OS, settings and flags, what happens when it is unavailable, how rules shape its mounts and network. |
| modes.md | cli/modes | default, accept-edits, auto and plan modes; switching, persisting, limits of auto. |
| hooks.md | hooks | hooks.json locations, events, matchers, tool names and args, stdin/stdout contract, PreToolUse decisions. |
| settings.md | settings | settings.json location, how the CLI rewrites it, `/config`, object keys (permissions, statusLine, sandboxProxy, custom models), other config files. |
| install.md | install | Sign-in options, Gemini API key mode (`modelProvider` + `GEMINI_API_KEY`), enterprise auth. |
| getting-started.md | getting-started | Install commands (`install.sh`, `install.ps1`, `install.cmd`), first run, common commands and shortcuts. |
| conversations.md | cli/conversations | Conversations scoped to the cwd, `--continue`, `/fork`. |
| commands-resume.md | cli/commands/resume | Session picker and how resume finds conversations. |
| subagents.md | subagents | `invoke_subagent`, workspace modes (inherit, git worktree, share), custom subagents, monitoring. |
| commands-agents.md | cli/commands/agents | Agent Manager panel: custom agents and background subagents. |
| rules.md | rules | AGENTS.md / GEMINI.md and `.agents/rules/` discovery, frontmatter triggers, global rules, `@` file references. |
| skills.md | skills | Skill format and discovery paths (workspace, global, CLI-only dirs). |
| plugins.md | plugins | Plugins: install, enable, layout, what they can add (skills, hooks, MCP). |
| mcp.md | mcp | mcp_config.json (global and workspace), stdio vs Streamable HTTP, fields, `/mcp` manager. |
| features.md | features | Feature overview per surface (CLI tab). |
| enterprise.md | enterprise | Gemini Enterprise: models hosted in your organization's Google Cloud, supported products and setup. |
| using.md | cli/using | CLI settings and everyday tips. |
| prompting.md | cli/prompting | Prompt box, multiline input, interrupting a turn, pasting media. |
| best-practices.md | cli/best-practices | Workflows that keep the agent reliable, starting with local verification loops (tests, builds). |
| troubleshooting.md | cli/troubleshooting | PATH problems, self-update locks, keyring access, SSH clipboard. |
| acp.md | cli/acp | `agy acp` starts an Agent Client Protocol server so editors (Zed, JetBrains…) use agy as their agent. |
| artifacts.md | cli/artifacts | Reviewing generated code, plans and media with line comments before edits are applied. |
| gcli-migration.md | cli/gcli-migration | Moving from Gemini CLI: config conversion, extensions as plugins, skills paths, MCP config. |
| credits.md | cli/credits | AI credits and quota tracking, `useG1Credits`. |
| commands-credits.md | cli/commands/credits | `/credits` panel. |
| commands-usage.md | cli/commands/usage | `/usage`: model quota groups (weekly + 5-hour limits). |
| commands-effort.md | cli/commands/effort | Reasoning effort levels per model. |
| commands-permissions.md | cli/commands/permissions | `/permissions` manager: Project, Shared and Global scopes. |
| commands-context.md | cli/commands/context | Context usage panel. |
| commands-diff.md | cli/commands/diff | Diff viewer for changes, turns and commits. |
| commands-codesearch.md | cli/commands/codesearch | Code search panel. |
| commands-btw.md | cli/commands/btw | Side questions in the background. |
| commands-changelog.md | cli/commands/changelog | Release notes viewer (prints in headless mode). |
| commands-voice.md | cli/commands/voice | Voice mode and dictation. |
| commands-statusline.md, statusline.md | cli/commands/statusline, cli/statusline | Status line customization. |
| commands-title.md, title.md | cli/commands/title, cli/title | Terminal title customization. |
| vim-editor-mode.md | cli/vim-editor-mode | Vim keys in the prompt box. |
