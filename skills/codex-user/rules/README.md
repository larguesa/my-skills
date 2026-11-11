# Instance guard and prefix limits

Keep the canonical `guard.rules` unchanged. After an authorized setup decision, use `install-guard.py` to generate a reviewed copy for the actual CODEX_HOME and absolute secrets directory:

```bash
python3 "$SKILL_DIR/rules/install-guard.py" --secrets-dir "$SECRETS_DIR" --output "$CANDIDATE_RULES"
codex execpolicy check --rules "$CANDIDATE_RULES" git push --help
```

The generator replaces the original `/home/USER` home placeholder and its `.secrets` path with explicit resolved values, writes a new candidate with restrictive permissions and refuses overwrite. Inspect it and install only into `${CODEX_HOME:-$HOME/.codex}/rules/` under the setup authorization. A private CODEX_HOME does not inherit the historical home rules. Copying this skill does not alter global Codex settings or authentication.

`execpolicy check` must report forbidden for seeded publication and allow/no matched restriction for a clean `git status`; never execute the dangerous text. Every rule includes native match/not_match examples.

These are exact command-prefix tokens. The secret directory token does not automatically match a file beneath it, a file read through a builtin tool, an absolute executable name or Git global-option prefixes. The native development tests record those nonmatches, not false protection. Use actual filesystem/OS confinement, narrow read/tool scope and network policy to protect secrets and publication; a workspace path or regex is not that boundary. Do not silently disable sandboxing when service namespaces fail.
