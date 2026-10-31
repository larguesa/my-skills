# AGENTS.md

## Propósito

Repositório de skills pessoais de Ricardo Pupo Larguesa, usadas em vários projetos. Cada skill fica em `skills/<nome>/`, com `SKILL.md`, recursos próprios e, quando o uso pede explicação, `README.md`; o catálogo é [skills/index.md](skills/index.md). Mudança numa skill não altera as outras.

Skills:

- [humanizador-pt-br](skills/humanizador-pt-br/README.md): texto PT-BR com cara de bom redator humano.
- [animation-video-maker](skills/animation-video-maker/README.md): brief -> vídeo curto, cena editável + MP4 local.
- [telegraphist](skills/telegraphist/SKILL.md): respostas telegráficas, menos tokens.
- [claude-code-user](skills/claude-code-user/SKILL.md): agente opera Claude Code headless (`claude -p`) + docs oficiais.
- [pi-user](skills/pi-user/SKILL.md): agente opera pi headless (`pi -p --mode json`) + docs oficiais.
- [opencode-user](skills/opencode-user/SKILL.md): agente opera OpenCode headless (`opencode run --format json`) + docs oficiais.
- [codex-user](skills/codex-user/SKILL.md): agente opera OpenAI Codex CLI headless (`codex exec --json`) + docs oficiais.

Skills `*-user`: docs oficiais em `docs/`, atualizar via `docs/update.sh`. Proteção (`hooks/`, `rules/`) bloqueia push, deploy, segredos; não afrouxar sem OK do Ricardo.

Regras próprias de uma skill ficam em `skills/<nome>/AGENTS.md`. Leia antes de alterar ou testar a skill:

- [Humanizador PT-BR](skills/humanizador-pt-br/AGENTS.md): meta de aumentar a humanização percebida pelos juízes, protocolo A/B e critérios para aceitar ou rejeitar cada versão.

## Regras de Execução

1. **Linguagem Telegráfica**: Estilo telegráfico, sincrético, conciso, elíptico. Brevidade absoluta. Sem perda de entendimento. Aplicável ao raciocínio e respostas.
2. **Ambiente Pronto**: Presumir software instalado. Investigar ou instalar apenas se ausência detectada.
3. **Familiarização**: Ler [README.md](README.md) no primeiro contato.
