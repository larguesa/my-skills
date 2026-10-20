# my-skills

Skills pessoais de Ricardo Pupo Larguesa para agentes de IA, reutilizadas em vários projetos. Cada skill funciona sozinha: copie a pasta para o diretório de skills do agente e carregue o `SKILL.md`. Catálogo completo: [skills/index.md](skills/index.md).

| Skill | Para que serve | Idioma do pacote |
|---|---|---|
| [Humanizador PT-BR](#humanizador-pt-br) | Redigir, revisar e diagnosticar textos em português brasileiro, sem fórmulas de IA | Português |
| [Animation Video Maker](#animation-video-maker) | Produzir vídeos animados com o agente, do brief ao MP4 | Inglês |
| [Telegraphist](#telegraphist) | Obter respostas ultracurtas, com abreviações e símbolos | Inglês |

## Humanizador PT-BR

Escreve, revisa e diagnostica textos em português brasileiro com ofício de redator: corta os clichês que denunciam a IA, acerta o registro do gênero e preserva fatos e voz do autor. Traz 32 regras, 12 perfis de estilo, 15 planos por gênero e um verificador local em Python.

Serve para notícia, documentação, e-mail, proposta, ensaio, conto ou crônica que precisa sair pronta para publicar. Peça, por exemplo: "Revise este artigo preservando fatos e voz: [...]. Use humanizador-pt-br."

[Humanizador PT-BR 0.8.0: instalação e exemplos](skills/humanizador-pt-br/README.md) · [protocolo da skill](skills/humanizador-pt-br/AGENTS.md)

<!-- resumo:inicio -->
**Na amostra avaliada, os textos escritos com a skill pareceram mais humanos aos juízes e receberam mais votos de preferência.**

Avaliação parcial de 20/10: 2 de 456 pares, gerados com Opus 5.5 e avaliados por Jev, Astra e Opus; ciclo ainda inconclusivo.

| Indicador | Sem skill | Com a skill 0.8.0 | Variação |
|---|---:|---:|---:|
| Humanização percebida, 0 a 100 | 31,67 | 47,33 | +15,67 pontos |
| Preferência dos juízes, votos | 2 de 6 | 4 de 6 | +2 |
| Falhas factuais críticas, julgamentos | 1 de 6 | 0 de 6 | -1 |
| Tokens por texto, média | 1766,00 | 10264,50 | +481,23% |
| Segundos de geração por texto, média | 16,66 | 18,93 | +13,62% |

Humanização percebida é a nota de 0 a 100 que três modelos juízes dão a cada texto, sem saber qual usou a skill; maior é mais humano. Nos votos, cada juiz escolhe o texto que atende melhor ao pedido.

[Relatório legível](skills/humanizador-pt-br/results/README.md#avaliação-mais-recente) · [Evidência original da rodada](skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0/README.md) · [Histórico](skills/humanizador-pt-br/results/README.md#histórico-das-avaliações)
<!-- resumo:fim -->

## Animation Video Maker

Transforma uma explicação, um diagrama ou um fluxo de interface em vídeo curto. O agente escreve a cena em código, com texto e logos exatos, e a exporta para MP4 na sua máquina, sem API de geração de vídeo; a cena-fonte continua editável. Para imagens orgânicas, o pacote orienta rotas generativa e híbrida com um provedor configurado à parte.

Inclui 22 estilos visuais, receitas criativas originais e técnicas de movimento, para vídeos explicativos, demonstrações de produto, tipografia animada e narrativa com dados. Peça, por exemplo: "Crie uma animação de 20 segundos explicando nossa abordagem de migração para gestores não técnicos. Use o fluxo do Animation Video Maker, sugira um estilo e entregue a cena editável e um MP4 validado."

Para ver antes de usar: 20 exemplos originais, cada um com MP4, cena-fonte editável e guia do estilo, conferidos no [relatório de validação](skills/animation-video-maker/references/validation.md), e três demonstrações sem marca na [validação da 0.2.0](skills/animation-video-maker/references/validation-0.2.md).

[Animation Video Maker](skills/animation-video-maker/README.md) (em inglês) · [skill do agente](skills/animation-video-maker/SKILL.md) · [galeria](skills/animation-video-maker/gallery.html), que roda localmente depois de baixar o pacote · [licença e avisos](skills/animation-video-maker/NOTICE.md)

## Telegraphist

Faz o agente responder como um telegrafista: direto ao ponto, sem repetir a pergunta, em frases curtas, com abreviações e símbolos como `->`, `=` e `+`. Útil em consultas rápidas, quando você quer só o dado ou o próximo passo. A instrução é em inglês.

Peça, por exemplo: "Use telegraphist: qual a diferença entre TCP e UDP?"

Avaliação parcial: 67 de 336 episódios iniciados e 9 votos válidos de juízes, ainda insuficientes para comprovar economia de tokens. [Telegraphist](skills/telegraphist/SKILL.md) · [relatório do benchmark](skills/telegraphist/tests/REPORT.md) (em inglês)

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
