# Antigravity CLI cheat-sheet (agy 1.4.2, checked against `agy --help` + docs/reference.md, docs/headless.md, 2026-11-08)
Full docs: docs/README.md. `agy --help` of the installed version is authoritative.

## Current unattended contract
Follow SKILL.md for exact model/effort, finite phase deadline, attempt-specific stdout/stderr, guard and full --conversation ID on resume. Require real process exit, current final result, response or schema-valid structured_output, independently checked artifacts and no unresolved necessary operation. Inspect tool ERROR events and stderr auto-denied notices even with SUCCESS/exit zero.
Use the host's supervised completion consumer; keep the same auth/settings context and global counters across continuations. Do not activate paid-credit fallback to evade quota. Validate generated secret paths and effective rules following rules/README.md. Worktrees are not OS isolation. Historical Windows checks below do not establish native enforcement on another host; technical completion is not external delivery.

## agy [flags]
-p/--print/--prompt PROMPT (headless) · -i/--prompt-interactive PROMPT · --output-format text|json|stream-json · --input-format text|stream-json (needs stream-json out; prompts on stdin)
--json-schema STR|FILE|type → .structured_output · --print-timeout DUR (0s = none; e.g. 30m) · --disable-slash-commands
--model SLUG (`agy models`) · --effort low|medium|high|xhigh|max · --agent NAME (`agy agents`) · --mode accept-edits|auto|plan (default if omitted)
-c/--continue (latest in cwd) · --conversation ID · --add-dir DIR (repeatable) · --project ID|NAME · --new-project
--sandbox · --dangerously-skip-permissions (NO; deny rules still apply) · --remote-control · --log-file PATH
No -C/--cd: the workspace is the cwd. Always `</dev/null` with -p.

## Subcommands
models · agents (agent) · mcp add|remove|list|enable|disable · plugin(s) install|uninstall|list|enable|disable · changelog · update · install · remote-control start|status|stop · mic-serve · help

## Output (docs/headless.md)
json: {conversation_id, status, response, error?, duration_seconds, num_turns, structured_output?, json_schema?, usage{input_tokens,output_tokens,thinking_tokens,cache_read_tokens,total_tokens}}
status: SUCCESS · ERROR · CANCELED · INTERRUPTED · INVALID · WAITING · RUNNING. Exit 0 on success (also when tools were soft-denied), non-zero on failure (unknown model → 1).
stream-json: init{cwd,tools,permission_mode,model?,agent?} · step_update{step_index,state ACTIVE|DONE|ERROR,step_type user_input|agent_response|tool|checkpoint,tool_name,text_delta,usage,tool_info{name,parameters,output,error{type,message}},subagent_info} · result{same as json}
stderr: diagnostics + "...required the "<action>" permission that headless mode cannot prompt for, so it was auto-denied".
stdin stream: {"event":"user","message":{"content":"..."}} per line; one result per turn; usage/num_turns cumulative.

## settings.json (~/.gemini/antigravity-cli/settings.json; docs/reference.md, settings.md)
agentMode ""|accept-edits|auto|plan · toolPermission request-review|proceed-in-sandbox|always-proceed|strict · enableTerminalSandbox · allowNonWorkspaceAccess · artifactReviewPolicy
model · modelProvider "gemini" (+ GEMINI_API_KEY) · useG1Credits (paid credits after quota; keep false) · disableSlashCommands · trustedWorkspaces · sandboxProxy · customModelsConfig
permissions {allow,ask,deny}: command(prefix|regex:RE) · read_file(PATH) · write_file(PATH) · read_url(DOMAIN) · execute_url(DOMAIN) · mcp(server/tool|server/*) · unsandboxed(...) (business). deny > ask > allow; `*` = all.
Not here: hooks (~/.gemini/config/hooks.json, .agents/hooks.json) · MCP (~/.gemini/config/mcp_config.json, .agents/mcp_config.json) · plugins (~/.gemini/config/plugins/, .agents/plugins/) · keybindings.json.

## Hooks (docs/hooks.md)
{"name":{"enabled":true,"PreToolUse":[{"matcher":"run_command","hooks":[{"type":"command","command":"...","timeout":30}]}]}}
Events: SessionStart · PreToolUse · PostToolUse (matcher = tool regex) · PreInvocation · PostInvocation · Stop. stdin JSON (camelCase: toolCall{name,args}, conversationId, workspacePaths...); PreToolUse stdout {"decision":"allow|auto_approve|deny|ask|force_ask|deny_unless_prior_grant","reason":"..."}.
Tool names: run_command{CommandLine,Cwd} · read_file{Path} · edit_file · write_to_file · ask_permission · invoke_subagent · manage_task · schedule.

## Files
~/.gemini/antigravity-cli/: settings.json · keybindings.json · cli.log · brain/<conversation_id>/ (artifacts, .system_generated/logs/transcript.jsonl) · conversations/ · skills/
~/.gemini/config/: hooks.json · mcp_config.json · plugins/ · skills/ · rules/ · AGENTS.md · ~/.gemini/AGENTS.md|GEMINI.md
Repo: AGENTS.md|GEMINI.md · .agents/{rules/,skills/,hooks.json,mcp_config.json,plugins/}

## Tested setup
agy 1.4.2 on Windows 11, Google account login (keyring). Headless: json, stream-json, --json-schema, --conversation resume, unknown model error, default-mode soft denial; guard deny rules in a temporary HOME (USERPROFILE). Not tested: auto mode and sandbox (Windows needs 1.4.4+), --dangerously-skip-permissions, stdin streaming, MCP.
