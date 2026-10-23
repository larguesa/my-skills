# my-skills

Skills pessoais de Ricardo Pupo Larguesa para agentes de IA, reutilizadas em vários projetos. Cada skill funciona sozinha: copie a pasta da skill para o diretório de skills do agente e carregue o `SKILL.md`; as subpastas `results/` e `tests/` são da avaliação e podem ficar de fora. Catálogo: [skills/index.md](skills/index.md).

| Skill | Para que serve | O que foi medido |
|---|---|---|
| [Humanizador PT-BR](#humanizador-pt-br) | Texto em português, escrito ou reescrito pelo agente, que soa como de um bom redator humano | Comparação amostral 0.9.0 versus 0.8.1 interrompida, 76 de 95 pares de redação julgados |
| [Animation Video Maker](#animation-video-maker) | Vídeo curto explicativo a partir de um brief, com cena editável e MP4 gerado na sua máquina | 20 exemplos e 3 demonstrações renderizados e conferidos |
| [Telegraphist](#telegraphist) | Conversa econômica com o agente, para gastar menos tokens | Amostra interrompida, sem juízes: respostas mais curtas, tokens totais maiores |

## Humanizador PT-BR

Para quando o agente vai escrever em português brasileiro, ou quando você tem um texto gerado por IA que soa como IA. O agente entrega o texto que um bom redator do gênero entregaria: natural, no registro certo, sem os clichês que denunciam a IA, com fatos e voz do autor preservados. Serve para notícia, e-mail, documentação, relatório, proposta, ensaio, post, conto ou crônica.

Peça, por exemplo: "Reescreva este texto gerado por IA para soar humano, sem mudar fatos nem números: [...]. Use humanizador-pt-br."

O propósito é humanizar textos produzidos ou revisados por IA. A melhora no julgamento de humanização é o critério de sucesso; economia de tempo e tokens não é objetivo desta skill. A avaliação compara textos anonimizados, preservando a fidelidade aos fatos e ao pedido. [Resultados e cobertura dos testes](skills/humanizador-pt-br/results/README.md).

[Humanizador PT-BR 0.8.1: instalação e exemplos](skills/humanizador-pt-br/README.md) · [avaliação](skills/humanizador-pt-br/results/README.md)

## Animation Video Maker

Transforma um brief em vídeo curto explicativo, de produto ou tipográfico. O agente escreve a cena em código, com texto e logos exatos, e a exporta para MP4 na sua máquina, sem API de geração de vídeo; a cena-fonte continua editável. Exportar exige Python, Playwright com Chromium e FFmpeg. Para imagens orgânicas, o pacote orienta rotas generativa e híbrida com um provedor configurado à parte, sem adaptador pronto.

Inclui 22 estilos visuais, receitas criativas originais e técnicas de movimento, para vídeos explicativos, demonstrações de produto, tipografia animada e narrativa com dados. Peça, por exemplo: "Crie uma animação de 20 segundos explicando nossa abordagem de migração para gestores não técnicos. Use o fluxo do Animation Video Maker, sugira um estilo e entregue a cena editável e um MP4 validado."

Para ver antes de usar: 20 exemplos originais, cada um com MP4, cena-fonte editável e guia do estilo, conferidos no [relatório de validação](skills/animation-video-maker/references/validation.md), e três demonstrações sem marca na [validação da 0.2.0](skills/animation-video-maker/references/validation-0.2.md). Os 20 exemplos usam a marca T2S Tech, excluída da licença MIT; troque marca e conteúdo ao reaproveitar.

[Animation Video Maker](skills/animation-video-maker/README.md) (em inglês) · [skill do agente](skills/animation-video-maker/SKILL.md) · [galeria](skills/animation-video-maker/gallery.html), que roda localmente depois de baixar o pacote · [licença e avisos](skills/animation-video-maker/NOTICE.md)

## Telegraphist

Serve para economizar tokens na conversa com o agente: ele responde como um telegrafista, em frases curtas, com abreviações e símbolos como `->`, `=` e `+`, sem repetir a pergunta e entregando só o dado ou o próximo passo pedido. Você também lê menos. A instrução é em inglês.

Peça, por exemplo: "Use telegraphist: qual a diferença entre TCP e UDP?"

Medido até agora, sem juízes: respostas mais curtas, não economia total. A única execução com a instrução atual foi interrompida em 67 de 336 episódios. Em 18 pares com resposta completa nos dois braços (outros 3 pares terminaram vazios ou truncados nos dois braços e ficaram fora), a versão com skill teve 40,8% menos palavras e 27,3% menos tokens de saída, mas 49,8% mais tokens de entrada, porque a instrução vai em cada requisição; o total subiu 14,7% e o custo, 1,6%. Nenhum juiz verificou se as respostas curtas preservaram a informação necessária.

[Telegraphist](skills/telegraphist/SKILL.md) · [relatório de testes](skills/telegraphist/tests/REPORT.md) (em inglês)

## Estrutura

- **AGENTS.md**: propósito do repositório e regras para agentes.
- **skills/**: uma pasta por skill e o catálogo `index.md`.
  - **SKILL.md**: instruções que o agente carrega.
  - **README.md** (quando houver): uso, instalação e situação.
  - **AGENTS.md** (opcional): regras para alterar e testar a skill.
  - **references/**, **assets/**, **scripts/** (opcionais): material de consulta, mídias e scripts usados pela skill.
  - **results/** ou **tests/** (opcionais): avaliação e testes; não precisam ir para o diretório de skills do agente.
