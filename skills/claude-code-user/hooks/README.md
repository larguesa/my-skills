# Portable fail-closed guard

Requires Bash and Python 3. `settings-guard.json` guards Bash, Read, Edit and Write. Every invocation/parser/type/helper failure returns blocking code 2. No command in the input is executed by the guard.

Before each initial or resumed CLI phase, export `CLAUDE_CODE_USER_GUARD="$SKILL_DIR/hooks/guard.sh"` from the actual installed folder, check it is readable and load `--settings "$SKILL_DIR/hooks/settings-guard.json"`. The historical home-path fallback is checked, never silently ignored. Safe mode disables hooks and is not this guarded recipe.

Covered direct operations: Git push/config/remote including common global options, mutating HTTP requests/uploads, package publication, GitHub mutation, deployment/elevation commands, protected root/home recursive removal and credential file paths (including Windows separators and environment variants). `.env.example` is the documented template exception. Normal temporary cleanup and `git stash push` are not publication. Model workers still need narrow tool availability and pre-approval.

Test the actual installed path with synthetic JSON piped to `bash "$CLAUDE_CODE_USER_GUARD"`: Bash `git push --help` must return 2, Bash `git status --short` returns 0, Read of a fictitious `.env.local` returns 2, Read of `README.md` returns 0. Malformed input, missing helper and unavailable Python must return 2. The development suite also executes the command stored in settings with a skill path containing spaces. These are non-mutating controls; never execute a real push to test the hook.

This is a direct-command/path tripwire, not a shell interpreter or OS sandbox. It does not resolve aliases, variables, arbitrary subprocess code, symlink targets or unlisted tools/MCP. File-tool checks apply to the requested path, not everything a search or script could reach. Use separate OS containment and a reviewed tool set when those capabilities are exposed. A native CLI run is needed to establish that its hook actually fires; direct script tests establish only the shipped handler behavior.
