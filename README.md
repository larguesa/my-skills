# my-skills

Gerenciador de skills pessoais de Ricardo Pupo Larguesa. Compartilhamento multi-projeto.

## Featured package

[**Animation Video Maker**](skills/animation-video-maker/README.md): an English-language creative-video workflow with 22 visual styles, original recipes, motion techniques, brand-neutral demos and 20 original T2S Tech service examples. Includes editable Canvas scenes, real MP4s, optional Jev selection and generative/hybrid planning guidance. See the [agent skill](skills/animation-video-maker/SKILL.md), [gallery source](skills/animation-video-maker/gallery.html) and [validation report](skills/animation-video-maker/references/validation.md). Download the package to run the HTML gallery locally.

Code/documentation licensing and brand/font exclusions are scoped to that package; see its [license and notices](skills/animation-video-maker/NOTICE.md).

## Humanizador PT-BR

[Humanizador PT-BR 0.6.0](skills/humanizador-pt-br/README.md): redação e revisão com catálogo, 12 perfis e ferramentas locais em Python. A [revisão 0.6.0](skills/humanizador-pt-br/results/REVISAO-2026-10-19.md) acrescenta briefing compacto, verificação de entrega e um [protocolo](skills/humanizador-pt-br/results/PROTOCOLO-0.6.0.md) com [execução parcial em 19/10](skills/humanizador-pt-br/results/runs/2026-10-19/README.md): 31 respostas completas, 27 julgamentos sobre 9 pares, H de 42,04 para 49,19 e nenhuma saída apenas com comandos no braço com skill. Os 84 testes de software passaram. O Qwen Flash voltou a interromper a matriz no primeiro pedido. Na versão 0.5.1, na [retomada de 13/10](skills/humanizador-pt-br/results/runs/2026-10-13/README.md), a humanização percebida média foi de 40,03 para 38,52/100 (queda relativa de 3,79%), os tokens aumentaram 3.131,84% e o tempo das chamadas caiu 13,28%. Amostra parcial de um pedido: 11 pares com três juízes e 15 pares com telemetria, incluindo duas respostas com comandos em vez de texto. O limite temporário do Qwen Flash impediu concluir a matriz dos [24 prompts aprovados](skills/humanizador-pt-br/results/PROMPTS.md). Não há benefício geral demonstrado. [Validação local](skills/humanizador-pt-br/results/README.md) e [resultados anteriores preservados](skills/humanizador-pt-br/results/runs/2026-10-10/README.md).

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
