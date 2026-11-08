# AGENTS.md

## Purpose

Repository of Ricardo Pupo Larguesa's personal skills, used across several projects. Each skill lives in `skills/<name>/`, with `SKILL.md`, its own resources and, when usage needs explaining, a `README.md`; the catalog is [skills/index.md](skills/index.md). A change to one skill does not alter the others.

Skills:

- [humanizador-pt-br](skills/humanizador-pt-br/README.md): PT-BR text that reads like a good human writer's.
- [animation-video-maker](skills/animation-video-maker/README.md): brief -> short video, editable scene + local MP4.
- [telegraphist](skills/telegraphist/SKILL.md): telegraphic answers, fewer tokens.
- [claude-code-user](skills/claude-code-user/SKILL.md): agent drives Claude Code headless (`claude -p`) + official docs.
- [pi-user](skills/pi-user/SKILL.md): agent drives pi headless (`pi -p --mode json`) + official docs.
- [opencode-user](skills/opencode-user/SKILL.md): agent drives OpenCode headless (`opencode run --format json`) + official docs.
- [codex-user](skills/codex-user/SKILL.md): agent drives OpenAI Codex CLI headless (`codex exec --json`) + official docs.
- [antigravity-user](skills/antigravity-user/SKILL.md): agent drives Google Antigravity CLI headless (`agy -p --output-format stream-json`) + official docs.
- [agentic-orchestrator](skills/agentic-orchestrator/SKILL.md): agent orchestrates other agents through natural language only; flow, state and events in YAML/JSON/Markdown; flow and communication patterns; no frameworks or scripts.

`*-user` skills: official docs in `docs/`, refresh via `docs/update.sh`. Guards (`hooks/`, `rules/`) block push, deploys, secrets; do not loosen them without Ricardo's OK.

Skill-specific rules live in `skills/<name>/AGENTS.md`. Read it before changing or testing the skill:

- [Humanizador PT-BR](skills/humanizador-pt-br/AGENTS.md): goal of raising the humanization perceived by judges, A/B protocol, and criteria for accepting or rejecting each version.

## Execution Rules

1. **Telegraphic language**: Telegraphic, syncretic, concise, elliptical style. Absolute brevity. No loss of understanding. Applies to reasoning and answers.
2. **Ready environment**: Assume software is installed. Investigate or install only if absence is detected.
3. **Familiarization**: Read [README.md](README.md) on first contact.
