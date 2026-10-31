#!/bin/bash
# PreToolUse guard for Claude Code's Bash tool. Exit 2 = block (stderr is shown to Claude).
cmd=$(jq -r '.tool_input.command // ""')
if echo "$cmd" | grep -Eq 'git push|curl .*-X *(POST|PUT|DELETE)|\.secrets|rm -rf /'; then echo "Blocked by guard: needs the user's explicit OK" >&2; exit 2; fi
exit 0
