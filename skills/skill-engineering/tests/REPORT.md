# Publication checks

Checked on 11 November 2026 with Python 3.14.9 and PyYAML 6.0.3.

## Result

- 22 helper tests passed, with no failures, errors or skipped tests.
- The shipped package passed the `hermes` structural profile, without warnings.
- Both SKILL.md frontmatter blocks parsed as YAML; the evaluation plan parsed as JSON.
- 22 local links were checked in the main instructions, package README and references.
- The 12 runtime files match the delivered skill byte for byte.
- Review of the publication allowlist and a targeted scan found no private host paths, mailbox identities, thread identifiers, API credentials or private keys in the new runtime files and README.

The fixtures cover valid and invalid metadata, missing and escaping links, symlinks, profile-specific constraints, paired-result coverage, missing metrics, critical failures, technical errors, duplicate records, invalid numeric values and CLI status codes.

## Reproduce

From the repository root, with Python 3.10+ and PyYAML available:

```bash
python3 skills/skill-engineering/scripts/test_skill_checks.py
python3 skills/skill-engineering/scripts/skill_checks.py validate skills/skill-engineering --profile hermes
```

The scripts make no model or network calls. [checks.json](results/checks.json) records the actual check results and runtime-file hashes.

## Scope

This publication verifies the software helpers and package structure. No model-quality comparison or spontaneous-discovery benchmark was run as part of the repository publication. The [evaluation protocol](../references/avaliacao.md) defines those separate experiments.
