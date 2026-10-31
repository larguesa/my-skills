# Codex CLI cheat-sheet (codex-cli 0.166.0, checked against `--help` + docs/cli-reference.md, 2026-10-31)
Full docs: docs/README.md. `--help` of the installed version is authoritative.

## codex exec [OPTIONS] [PROMPT|-]   (alias `codex e`)
--json (JSONL events) · -o/--output-last-message FILE · --output-schema FILE · --color always|never|auto
-C/--cd DIR · --add-dir DIR (extra writable) · --worktree · --skip-git-repo-check · --ephemeral (no session files)
-m/--model M · -c key=TOML (repeatable) · -p/--profile NAME ($CODEX_HOME/NAME.config.toml) · --enable/--disable FEATURE
-s/--sandbox read-only|workspace-write|danger-full-access · --approve-for-me (auto-review approvals) · --dangerously-bypass-approvals-and-sandbox (NO)
--ignore-user-config · --ignore-rules (NO) · --strict-config · -i/--image FILE · --oss/--local-provider lmstudio|ollama
Prompt: arg, or `-`/omitted = stdin; arg + piped stdin = stdin appended as <stdin> block. Always `</dev/null`.
Gone: --full-auto, approval_policy "untrusted". `-a/--ask-for-approval on-request|never` and `--search` are top-level (TUI) flags.

## Subcommands of exec
resume [ID|name] [PROMPT] --last --all -m -c --json -o --output-schema --ephemeral --skip-git-repo-check --worktree (no -s/-C)
fork <ID> PROMPT · review [PROMPT] --uncommitted | --base BR | --commit SHA [--title]

## JSON events (docs/non-interactive-mode.md)
thread.started{thread_id} · turn.started · item.started/updated/completed{item:{id,type,...}} · turn.completed{usage:{input_tokens,cached_input_tokens,output_tokens,reasoning_output_tokens}} · turn.failed{error} · error{message}
item types: agent_message{text} · reasoning · command_execution{command,exit_code,status} · file_change · mcp_tool_call · web_search · todo_list
Quota exhausted → error + turn.failed "You've hit your usage limit ... try again at <date>".

## Other commands
codex login [status] · logout · doctor [--summary|--json] · features list|enable|disable · mcp list|get|add|remove|login|logout
codex mcp add NAME [--env K=V] -- CMD ARGS | --url URL · sandbox [-P :read-only|:workspace|:danger-full-access] -- CMD (test the sandbox)
execpolicy check --rules FILE [--pretty] CMD... · apply (git apply last diff) · resume/fork (TUI) · archive|delete|unarchive ID · update · cloud (exp.) · app-server (exp.)

## Config (~/.codex/config.toml; docs/config-reference.md, config-sample.md)
model · model_reasoning_effort · sandbox_mode · approval_policy (on-request|never|{granular}) · [sandbox_workspace_write] writable_roots, network_access · default_permissions (":workspace"...; don't mix with sandbox_mode)
[mcp_servers.NAME] command, args, env, url, required, startup_timeout_sec, enabled_tools, disabled_tools · [features] · [profiles] · skills.config[] {path, enabled}
Env: CODEX_HOME (~/.codex) · CODEX_SQLITE_HOME · CODEX_API_KEY (API-key runs; avoid with repo code)

## Files
~/.codex/: config.toml · auth.json (secret) · sessions/YYYY/MM/DD/rollout-*.jsonl · rules/*.rules · AGENTS.md · skills/.system (bundled) · log/
User skills: ~/.agents/skills · Repo: AGENTS.md, .agents/skills, .codex/ (trusted projects only)

## Tested setup
npm global codex-cli 0.166.0, ChatGPT login. config.toml: sandbox_mode=workspace-write, network off. Rules: ~/.codex/rules/guard.rules → $SKILL_DIR/rules/guard.rules. User skills symlinked into ~/.agents/skills. No MCP servers.
