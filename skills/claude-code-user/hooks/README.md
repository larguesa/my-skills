# Guard hook
`settings-guard.json` registers `guard.sh` as a PreToolUse hook on Bash. It assumes the skill lives at `~/.claude/skills/claude-code-user`; if you installed it elsewhere, edit the `command` path to point at your `guard.sh` (absolute path). Needs `jq`. Use with `claude -p ... --settings "$SKILL_DIR/hooks/settings-guard.json"`.
