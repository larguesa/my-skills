# Permission overlay without broad approval

`guard-permissions.json` adds direct publication, deployment/elevation, mutating HTTP/upload, protected removal and sensitive-file denials. It adds no wildcard allow. The only template exception is `.env.example`, and the merge preserves existing ask/deny policies rather than forcing that exception.

Prepare a separate candidate with the shipped helper, requiring Python 3:

```bash
python3 "$SKILL_DIR/hooks/merge-permissions.py" existing.json "$SKILL_DIR/hooks/guard-permissions.json" candidate.json
```

The helper preserves other configuration, converts scalar permission policies without widening them, repositions guard denials last and rejects duplicate JSON keys or invalid shapes. It never edits active configuration and refuses an existing output. Review the candidate and the actual effective project/per-agent rules before an authorized replacement. Do not use recursive object merging that inserts `"*":"allow"` or leaves a pre-existing guard pattern before a later allow. Test the real helper with ask/deny scalar and patterned fixtures.

Existing tool-name selectors must be literal names or the single global `"*"`; guard overlay tool names must be literal. Other tool-name patterns containing `*` or `?` (including `"b*":"deny"` and `"r*":"deny"`), as well as a global guard tool selector, are explicitly rejected before any candidate is written; they require manual review rather than an unsafe approximation of native precedence. Target/argument patterns inside supported tool policies retain their ordered last-match semantics, including inheritance from global tool rules.

The existing recursive absolute-removal wildcard remains conservative: it denies all matching absolute paths, including temporary paths. Use scoped relative cleanup for worker-owned artifacts or let the authorized controller handle it; this release does not add a new cleanup allow that could weaken user policy.

Wildcard rules use native last-match semantics. Direct command patterns are not a shell parser: the native client parses compound commands, while fixtures test the matching/merge layer only. Literal/case/quoting variants, indirect code, alternate tools/MCP, symlinks and project/per-agent overrides need separate review. These rules are not OS containment. The template exception is applied only when it demonstrably preserves an existing allow; conservative omission is preferable to widening an unknown policy.

Use a harmless seeded command such as `git push --help` plus `git status --short` to verify native blocked/clean behavior on an installed CLI. Synthetic matching tests do not establish native enforcement. Do not execute a real push, deploy or secret read as a probe.
