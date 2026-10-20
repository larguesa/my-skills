# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Humanizador PT-BR 0.8.0](skills/humanizador-pt-br/README.md): redação, revisão e diagnóstico em português brasileiro, com 32 regras, 12 perfis e ferramentas locais em Python. Avaliação A/B cega por Jev, Astra e Opus conforme o [protocolo da skill](skills/humanizador-pt-br/AGENTS.md).

<!-- resumo:inicio -->
**0.8.0, 20/10: Parcial e inconclusiva: interrompida após mais de 15 minutos sem resposta completa do Opus no terceiro pedido.**

**H 47,33** com a skill, contra 31,67 na referência (sem skill). **ΔH +15,67 pontos**. H vai de 0 a 100: quanto maior, mais humano o texto pareceu aos juízes.

Cobertura: 2 de 456 pares; 2 de 24 pedidos; só claude-opus-5.5. Votos versão / referência / empate: 4 / 2 / 0 de 6.

Tokens totais, média por texto (referência → versão): 1766,00 → 10264,50 (+481,23%); 2 de 456 pares.

Tempo de geração na API, média por texto (referência → versão): 16,66 → 18,93 s (+13,62%); 2 de 456 pares.

[Relatório](skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0/README.md) · [Histórico](skills/humanizador-pt-br/results/README.md)
<!-- resumo:fim -->

## Telegraphist

[Telegraphist](skills/telegraphist/SKILL.md): the supplied ultra-short reply prompt, with abbreviations and symbols. [English benchmark report](skills/telegraphist/tests/REPORT.md): seven current models, English/Portuguese prompts and Jev/Astra/Opus judges. The run stopped at an OpenRouter concurrent-request reservation limit: 67 of 336 planned candidate episodes started, nine valid judge votes, USD 1.860233450 reconciled spend. The current benchmark has no assistant-imposed monetary ceiling or quota; its dedicated key is enabled, and cost accounting is measurement only. OpenRouter's own reservation constraint is separate. The full comparison remains incomplete; no general token-saving or quality claim is justified. The skill root contains only `SKILL.md` and `tests/`; historical readable reports are translated into English and original evidence remains preserved.

## Estrutura

- **AGENTS.md**: Propósito do repositório e regras para agentes.
- **skills/**: Pasta raiz de skills.
  - **index.md**: Catálogo/Índice.
  - **[subpasta-skill]/**: Pasta individual de skill.
    - **SKILL.md**: Instruções e recursos.
    - **README.md**: Uso e resultados.
    - **AGENTS.md** (opcional): Regras próprias da skill.
    - **references/** (opcional): Material de consulta.
    - **assets/** (opcional): Mídias, imagens, ícones.
    - **scripts/** (opcional): Scripts utilitários.
