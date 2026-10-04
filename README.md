# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Apresentação e uso](skills/humanizador-pt-br/README.md): escrita e revisão em PT-BR, com foco em ritmo, clareza e voz. A ampliação em 24 pedidos de 12 gêneros foi encerrada: 912 posições percorridas, 848 respostas válidas de transporte, 64 saídas inválidas terminais e 410 pares completos. Os três juízes avaliaram 308 pares cada, em 315 chamadas em lote; 102 pares completos ficaram sem notas por pertencerem a grupos congelados inelegíveis. Gasto conciliado: US$ 28.480551395. [Índice e textos completos](skills/humanizador-pt-br/tests/README.md) · [Resultados, custos e limitações](skills/humanizador-pt-br/tests/results/expansao-20261002-periodica/STATUS.md). Jev e Astra ficaram praticamente divididos; Opus preferiu mais versões com skill. A avaliação humana está pendente; validade de resposta não comprova correção factual e não há promessa de superioridade ou de escapar de detectores. Os dois contos históricos e as tentativas anteriores permanecem separados.

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
