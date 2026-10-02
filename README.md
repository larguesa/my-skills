# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Apresentação e uso](skills/humanizador-pt-br/README.md): escrita e revisão em PT-BR, com foco em ritmo, clareza e voz. O [índice dos testes](skills/humanizador-pt-br/tests/README.md) reúne os dois contos históricos e a ampliação em 24 pedidos de 12 gêneros. A retomada avançou para 51 textos válidos de resposta, 25 pares completos e 39 julgamentos de pares (13 por juiz), mas outra rejeição do provedor no segundo pedido interrompeu a execução. Gasto acumulado desta ampliação: US$ 1.747699620, segundo a chave exclusiva. A matriz completa permanece pendente. Jev, Astra e Opus 5.5 aparecem em colunas próprias. [Estado e limitações da retomada](skills/humanizador-pt-br/tests/results/expansao-20261002-retomada/STATUS.md). A avaliação humana está pendente; não há promessa de superioridade ou de escapar de detectores.

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
