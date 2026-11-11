# Skill Engineering

Turn a recurring workflow into a skill an agent can select, execute and verify. Use it to create a new skill, clarify an existing one or correct failures in activation, references, prerequisites and completion checks.

The instructions are in Brazilian Portuguese. They combine a concise operating core with targeted references, templates and local validation helpers.

## Use

Ask the agent, for example:

> Use a skill-engineering para criar uma skill de conferência de propostas a partir deste fluxo. A saída deve identificar campos, divergências e suas localizações nos documentos originais.

Or improve an existing skill:

> Use a skill-engineering para melhorar a skill [nome], preservando a versão anterior e corrigindo [falha observada].

The workflow defines acceptance before drafting, separates skill discovery from execution quality, and uses observed failures to guide revisions. Drafting, installation, publication and paid evaluations have separate authorization scopes.

## Install

Copy this complete folder into your agent's skills directory and load [SKILL.md](SKILL.md). Keep `references/`, `templates/` and `scripts/` together. The `tests/` folder is publication evidence and is optional for installation; `scripts/test_skill_checks.py` remains with the reusable helpers.

The shipped frontmatter includes Hermes extensions. For another agent, adapt its metadata, tool names and loading conventions to that agent's documented format. The `hermes` helper profile follows the short-description convention documented in this package, not a universal description limit.

## Package

- [SKILL.md](SKILL.md): scope, decisions, examples and completion checks.
- [Sources and synthesis decisions](references/fontes.md): attribution and links to the five source guides.
- [Evaluation protocol](references/avaliacao.md): paired comparisons, separate discovery tests, critical failures and observed metrics.
- [Skill template](templates/skill.md) and [evaluation plan](templates/avaliacao.json): editable starting points.
- [Local helpers](scripts/skill_checks.py): structure validation and paired-result aggregation.
- [Helper tests](scripts/test_skill_checks.py): artificial fixtures for the software contracts.

## Run the local checks

The helpers require Python 3.10 or newer; YAML validation also requires PyYAML. They do not call models, access the network or install dependencies.

From the repository root, with those dependencies already available:

```bash
python3 skills/skill-engineering/scripts/skill_checks.py validate skills/skill-engineering --profile hermes
python3 skills/skill-engineering/scripts/test_skill_checks.py
```

To aggregate real results recorded in the [documented JSON format](references/avaliacao.md):

```bash
python3 skills/skill-engineering/scripts/skill_checks.py aggregate path/to/results.json
```

The `portable` profile checks a basic Agent Skills field set. Apply it after adapting the shipped Hermes-specific frontmatter; the unchanged package intentionally uses the `hermes` profile.

The `validate` command checks metadata and local links in `SKILL.md` and top-level `references/*.md`. It does not traverse the package README, templates or nested reference directories; the publication checks cover additional files as recorded in the test report.

## Verification

Publication checks passed: 22 helper tests, YAML parsing, local-reference checks and the package's Hermes structure validation. See the [test report](tests/REPORT.md) and [machine-readable results](tests/results/checks.json).

These checks establish the helper and package contracts. Execution quality and spontaneous discovery have their own evaluation protocol; no comparative performance gain is claimed for this publication.
