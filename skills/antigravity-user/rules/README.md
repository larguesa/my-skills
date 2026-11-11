# Deny overlay and explicit secret paths

`guard-permissions.json` retains worker publication/configuration, GitHub, package, deployment/elevation, mutating HTTP, protected removal and secret-path denials. Git command patterns cover common global options. Native deny rules take precedence over ask/allow in the documented version.

After an authorized settings change, generate a separate candidate using the shipped Python 3 helper:

```bash
python3 "$SKILL_DIR/rules/merge-permissions.py" existing.json "$SKILL_DIR/rules/guard-permissions.json" "$SECRETS_DIR" candidate.json
```

The helper preserves existing denials, replaces the canonical `/home/USER/.secrets` placeholder with the supplied absolute path, validates shapes and regex syntax, rejects duplicate JSON keys and writes only a new restrictive-permission candidate. Review it, ensure no placeholder remains and confirm the actual effective settings before replacement. Settings are global in the historically tested client; copying the skill does not configure them.

The development suite fullmatches synthetic commands against the actual JSON regexes; it does not run agy or prove native enforcement. The historical Windows 1.4.2 checks remain in reference.md. On an available CLI, exercise `git push --help` (blocked) and `git status --short` (clean), never an actual publication. Malformed rules can be ignored by the client, so valid JSON alone is insufficient.

The file rules shown protect the workspace-root `.env` and configured secrets path. Nested environment files and other sensitive paths need separately reviewed native rules/containment; the direct regex layer is not an OS sandbox or a general shell interpreter. Variables, aliases, indirect scripts, tool/MCP alternatives and path/symlink resolution are outside these synthetic matching checks. Preserve model/effort and billing route when a required operation is denied.
