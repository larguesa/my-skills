# Direct tool-call guard

Load `-e "$SKILL_DIR/hooks/guard.ts"` on initial and resumed phases. The extension validates input types and directly guards bash/powershell plus read/write/edit/grep/find/ls requested paths. It blocks direct publication, deployment/elevation, mutating HTTP/uploads, protected root/home removal and sensitive environment/credential paths, normalizing Windows separators. `.env.example`, ordinary temporary cleanup and `git stash push` are clean controls. Invalid known-tool input blocks; unknown tools are outside this guard's coverage.

The development suite imports the actual TypeScript handler with Node's native type stripping (Node 22.6 or newer) and a fake registration API. No Pi installation or model call is used for that test. Check blocked/clean fixtures against the installed handler too; a native Pi run remains a separate integration check.

Search tools default to the current directory when their documented path is omitted. A safe search root does not exclude sensitive descendants. codemode, MCP, external extensions, aliases, arbitrary scripts, symlinks and indirect execution require separate tool restrictions and OS containment. This direct-command/path tripwire is not a sandbox. Never grant the worker publication authority merely because the controller already has it.
