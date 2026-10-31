# Codex official docs (markdown copies)
Downloaded 2026-10-31. Site pages come from https://learn.chatgpt.com/docs/<slug>.md (developers.openai.com/codex redirects there; index: llms.txt). The openai/codex repo `docs/` folder is now mostly stubs pointing to the site, so only its two real files are kept. Refresh: `./update.sh`.

| File | Source slug | Summary / when to consult |
|---|---|---|
| llms.txt | developers.openai.com/codex/llms.txt | Index of every page with a .md twin. Use it to fetch a page not copied here (subagents, speed, app-server, permissions…). |
| non-interactive-mode.md | non-interactive-mode | `codex exec`: sandbox defaults, `--json` events, `--output-schema`, `-o`, resume, git check, CI auth. Primary reference for our workflow. |
| cli-reference.md | cli/reference | Every command and flag. Consult before using any flag. |
| cli-overview.md | codex/cli | CLI features overview (TUI, models, images, web search, review). |
| auth.md | auth | ChatGPT vs API-key login, device auth, headless login, credential storage. |
| approvals-security.md | agent-approvals-security | Sandbox modes, approval policies, protected paths (.git), network access, recommended combos. Read before widening permissions. |
| sandboxing.md | sandboxing | How the Linux/macOS/Windows sandboxes work and their limits. |
| rules.md | agent-configuration/rules | Execpolicy `.rules` (Starlark `prefix_rule`, forbidden/prompt/allow, `codex execpolicy check`). Used by ../rules/guard.rules. |
| agents-md.md | agent-configuration/agents-md | AGENTS.md discovery (global, repo root → cwd, override, fallbacks, size limit). |
| config-basic.md | config-file/config-basic | config.toml location, precedence, common keys, profiles. |
| config-advanced.md | config-file/config-advanced | Providers, profiles, history/sessions, telemetry, shell env policy, CODEX_HOME. |
| config-reference.md | config-file/config-reference | Every config key (approval_policy, sandbox_workspace_write.*, mcp_servers.*, skills.config…). |
| config-sample.md | config-file/config-sample | Fully commented sample config.toml. |
| environment-variables.md | config-file/environment-variables | CODEX_HOME, CODEX_SQLITE_HOME, install dirs, API keys. |
| mcp.md | extend/mcp | MCP servers in config.toml / `codex mcp add`, STDIO & HTTP, OAuth, required, tool allow/deny lists. |
| hooks.md | hooks | Lifecycle hooks, trust model, input/output. Consult before adding hooks (we use rules instead). |
| build-skills.md | build-skills | Skill format and discovery paths (~/.agents/skills, repo .agents/skills, /etc/codex/skills), symlinks allowed. |
| usage-limits.md | enterprise/usage-limits | Workspace usage limits and spend controls (enterprise-oriented; personal plan usage is at chatgpt.com/settings/usage). |
| repo-config-notes.md | github openai/codex docs/config.md | Pointer notes from the repo (links to config pages). |
| repo-install.md | github openai/codex docs/install.md | System requirements, install and build from source. |
