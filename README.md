# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Humanizador PT-BR 0.8.0](skills/humanizador-pt-br/README.md): redação, revisão e diagnóstico em português brasileiro, com catálogo de 32 regras, 12 perfis e ferramentas locais em Python. Meta: aumentar a humanização percebida pelos juízes Jev, Astra e Opus em testes A/B cegos com os [24 pedidos aprovados](skills/humanizador-pt-br/results/PROMPTS.md). Regras de avaliação e de aceitação de cada versão: [AGENTS.md da skill](skills/humanizador-pt-br/AGENTS.md).

<!-- tabela:inicio -->
| Versão | Referência | Amostra julgada | H referência | H versão | Δ H | Votos versão / referência / empate | Situação | Textos e votos |
|---|---|---|---:|---:|---:|---|---|---|
| 0.2.0, 2 contos | sem skill | 38 de 38 pares; 2 contos; 19 configurações | 30,00 | 41,19 | +11,19 | 71 / 43 / 0 de 114 | Completa. Pedidos antigos, fora dos 24 aprovados. Sem decisão. Valores históricos fixos, conferidos em 20/10/2026. | [índice com textos e votos](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md) |
| 0.2.0, 02/10 | sem skill | 308 de 456 pares; 24 de 24 pedidos; 19 de 19 configurações | 31,08 | 35,00 | +3,93 | 456 / 428 / 40 de 924 | Encerrada com 64 saídas inválidas e 102 pares sem juízes. Pedidos com texto antigo. Sem decisão. Valores históricos fixos, conferidos em 20/10/2026. | [índice com textos e votos](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md) |
| 0.5.1, 10 e 13/10 | sem skill | 11 de 456 pares; pedido 01; 11 de 19 configurações | 40,03 | 38,52 | -1,52 | 14 / 17 / 2 de 33 | Parcial: parou no limite do Qwen Flash; 2 respostas com skill só trouxeram comandos. Sem decisão. | [textos e votos](skills/humanizador-pt-br/results/runs/2026-10-13/experiments/01-noticia-bibliotecas/REPORT.md), [relatório](skills/humanizador-pt-br/results/runs/2026-10-13/README.md), [início em 10/10](skills/humanizador-pt-br/results/runs/2026-10-10/README.md) |
| 0.6.0, 19/10 | sem skill | 9 de 456 pares; pedido 01; 9 de 19 configurações | 42,04 | 49,19 | +7,15 | 11 / 13 / 3 de 27 | Parcial: parou no limite do Qwen Flash. Sem decisão. | [textos e votos](skills/humanizador-pt-br/results/runs/2026-10-19/experiments/01-noticia-bibliotecas/REPORT.md), [relatório](skills/humanizador-pt-br/results/runs/2026-10-19/README.md) |
| 0.7.0, 19/10 | sem skill | 22 de 456 pares; 22 de 24 pedidos; só claude-opus-5.5 | 26,74 | 40,27 | +13,53 | 35 / 31 / 0 de 66 | Parcial: parou sem capacidade do Grok. Sem decisão. | [textos e votos por pedido](skills/humanizador-pt-br/results/README.md#textos-e-votos-por-pedido), [relatório](skills/humanizador-pt-br/results/runs/2026-10-19-max/README.md) |
| 0.8.0 | não se aplica | Sem A/B: 5 textos do MiMo 2.6 Pro, sem juízes | não medido | não medido | n/d | n/d | Candidata do primeiro ciclo A/B, pendente. | [teste funcional](skills/humanizador-pt-br/results/reviews/0.8.0/SMOKE.md), [revisão](skills/humanizador-pt-br/results/reviews/0.8.0/REVISAO.md) |
<!-- tabela:fim -->

H é 100 menos a impressão de IA dada pelo juiz, de 0 a 100. Cada linha compara a versão com a referência indicada, dentro da mesma rodada; a diferença entre linhas não mede evolução da skill. Votos por juiz, cobertura e textos de cada pedido: [resultados](skills/humanizador-pt-br/results/README.md).

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
