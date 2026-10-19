# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Humanizador PT-BR 0.8.0](skills/humanizador-pt-br/README.md): redação, revisão e diagnóstico com catálogo de 32 regras, 12 perfis e ferramentas locais em Python. A [revisão 0.8.0](skills/humanizador-pt-br/results/REVISAO-0.8.0.md) consolida três revisões independentes da 0.7.0: formas preferidas que só retiram o vício, exceções do catálogo no briefing, instruções por modo e verificação de literais e da origem de citações. [Teste funcional da 0.8.0](skills/humanizador-pt-br/results/reviews/0.8.0/SMOKE.md): 117 testes de software aprovados e cinco textos completos sem bloqueio mecânico, mas com problemas editoriais descritos no relatório; um sexto pedido foi recusado pelo provedor. Não houve comparação A/B nesta rodada.

Histórico: [revisão 0.7.0](skills/humanizador-pt-br/results/REVISAO-0.7.0.md) e [teste parcial](skills/humanizador-pt-br/results/runs/2026-10-19-max/README.md); [revisão 0.6.0](skills/humanizador-pt-br/results/REVISAO-2026-10-19.md) e [teste parcial](skills/humanizador-pt-br/results/runs/2026-10-19/README.md); [retomada 0.5.1](skills/humanizador-pt-br/results/runs/2026-10-13/README.md); [resultados de 10/10](skills/humanizador-pt-br/results/runs/2026-10-10/README.md). Nenhuma amostra demonstrou benefício geral. [Validação local](skills/humanizador-pt-br/results/README.md) e [24 prompts aprovados](skills/humanizador-pt-br/results/PROMPTS.md).

## Telegraphist

[Telegraphist](skills/telegraphist/SKILL.md): the supplied ultra-short reply prompt, with abbreviations and symbols. [English benchmark report](skills/telegraphist/tests/REPORT.md): seven current models, English/Portuguese prompts and Jev/Astra/Opus judges. The run stopped at an OpenRouter concurrent-request reservation limit: 67 of 336 planned candidate episodes started, nine valid judge votes, USD 1.860233450 reconciled spend. The current benchmark has no assistant-imposed monetary ceiling or quota; its dedicated key is enabled, and cost accounting is measurement only. OpenRouter's own reservation constraint is separate. The full comparison remains incomplete; no general token-saving or quality claim is justified. The skill root contains only `SKILL.md` and `tests/`; historical readable reports are translated into English and original evidence remains preserved.

## Estrutura

- **skills/**: Pasta raiz de skills.
  - **index.md**: Catálogo/Índice.
  - **[subpasta-skill]/**: Pasta individual de skill.
    - **SKILL.md**: Instruções e recursos.
    - **references/** (opcional): Material de consulta.
    - **assets/** (opcional): Mídias, imagens, ícones.
    - **scripts/** (opcional): Scripts utilitários.
