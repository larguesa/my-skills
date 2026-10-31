# my-skills

Skills pessoais de Ricardo Pupo Larguesa para agentes de IA, reutilizadas em vários projetos. Cada skill funciona sozinha: copie a pasta da skill para o diretório de skills do agente e carregue o `SKILL.md`; as subpastas `results/` e `tests/` são da avaliação e podem ficar de fora. Catálogo: [skills/index.md](skills/index.md).

| Skill | Para que serve | O que foi medido |
|---|---|---|
| [Humanizador PT-BR](#humanizador-pt-br) | Texto em português, escrito ou reescrito pelo agente, que soa como de um bom redator humano | Comparação amostral 0.9.1 versus 0.8.1 interrompida, 68 de 95 pares de redação julgados |
| [Animation Video Maker](#animation-video-maker) | Vídeo curto explicativo a partir de um brief, com cena editável e MP4 gerado na sua máquina | 20 exemplos e 3 demonstrações renderizados e conferidos |
| [Telegraphist](#telegraphist) | Conversa econômica com o agente, para gastar menos tokens | Amostra interrompida, sem juízes: respostas mais curtas, tokens totais maiores |
| [Claude Code User](#claude-code-user) | Guia para o agente usar o Claude Code em modo headless (`claude -p`), com a documentação oficial em markdown | Testado no Claude Code 2.1.316: criar e retomar sessão, saída estruturada, modelo reserva e hook de proteção |
| [Pi User](#pi-user) | Guia para o agente usar o pi (pi.dev) em modo headless (`pi -p --mode json`), com a documentação oficial em markdown | Testado no pi 1.4.0: saída JSON, retomada de sessão, extensão de proteção e servidor MCP |
| [OpenCode User](#opencode-user) | Guia para o agente usar o OpenCode em modo headless (`opencode run --format json`), com a documentação oficial em markdown | Testado no OpenCode 1.19.5: saída JSON, retomada de sessão, regras de permissão de proteção e custo com e sem MCP |
| [Codex User](#codex-user) | Guia para o agente usar o OpenAI Codex CLI em modo headless (`codex exec --json`), com a documentação oficial em markdown | Conferido no codex-cli 0.166.0: opções pelo `--help`, sandbox e regras de proteção testados; execuções com modelo não testadas (cota esgotada) |

## Humanizador PT-BR

Para quando o agente vai escrever em português brasileiro, ou quando você tem um texto gerado por IA que soa como IA. O agente entrega o texto que um bom redator do gênero entregaria: natural, no registro certo, sem os clichês que denunciam a IA, com fatos e voz do autor preservados. Serve para notícia, e-mail, documentação, relatório, proposta, ensaio, post, conto ou crônica.

Peça, por exemplo: "Reescreva este texto gerado por IA para soar humano, sem mudar fatos nem números: [...]. Use humanizador-pt-br."

O propósito é humanizar textos produzidos ou revisados por IA. A melhora no julgamento de humanização é o critério de sucesso; economia de tempo e tokens não é objetivo desta skill. A avaliação compara textos anonimizados, preservando a fidelidade aos fatos e ao pedido. [Última comparação, com cobertura e textos completos](skills/humanizador-pt-br/results/samples/2026-10-25/README.md).

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

## Claude Code User

Ensina o agente a delegar trabalho de código ao Claude Code sem acompanhamento: quando vale delegar, a chamada padrão com `claude -p`, permissões, limites de turnos e de gasto, retomada de sessão, tarefas longas, um hook que bloqueia `git push` e comandos perigosos, e como conferir o resultado em vez de confiar no resumo. Traz um resumo de consulta rápida e cópias em markdown da documentação oficial (CLI, comandos, variáveis de ambiente, ferramentas, modo interativo, checkpoints, hooks, channels, glossário e headless), atualizáveis com `docs/update.sh`. Instrução em inglês.

Peça, por exemplo: "Use claude-code-user e delegue ao Claude Code a refatoração deste módulo, com testes."

[Claude Code User](skills/claude-code-user/SKILL.md) · [resumo de consulta](skills/claude-code-user/reference.md) · [documentação oficial](skills/claude-code-user/docs/README.md)

## Pi User

Ensina o agente a delegar trabalho de código ao pi sem acompanhamento: quando vale usar o pi em vez do Claude Code, a chamada padrão com `pi -p --mode json`, como ler os eventos JSON e o custo, retomada e bifurcação de sessão, modo RPC para agentes de longa duração, modelos via OpenRouter, MCP nativo (desde a versão 1.x), uma extensão que bloqueia `git push`, acesso a segredos e comandos perigosos, e como conferir o resultado. Traz um resumo de consulta rápida e cópias em markdown dos 43 arquivos da documentação oficial, atualizáveis com `docs/update.sh`. Instrução em inglês.

Peça, por exemplo: "Use pi-user e peça ao pi para criar um script com testes, usando o MiMo pela OpenRouter."

[Pi User](skills/pi-user/SKILL.md) · [resumo de consulta](skills/pi-user/reference.md) · [documentação oficial](skills/pi-user/docs/README.md)

## OpenCode User

Ensina o agente a delegar trabalho de código ao OpenCode sem acompanhamento: quando vale usar o OpenCode em vez do pi ou do Claude Code, a chamada padrão com `opencode run --format json`, como ler os eventos JSON e o custo, retomada e bifurcação de sessão, servidor persistente (`opencode serve` e `--attach`), agentes build e plan, modelos via OpenRouter, MCP, regras de permissão que bloqueiam `git push`, acesso a segredos e comandos perigosos, e como conferir o resultado. Traz um resumo de consulta rápida e cópias em markdown dos 33 arquivos da documentação oficial (convertidos de MDX), atualizáveis com `docs/update.sh`. Instrução em inglês.

Peça, por exemplo: "Use opencode-user e peça ao OpenCode para corrigir este bug e rodar os testes."

[OpenCode User](skills/opencode-user/SKILL.md) · [resumo de consulta](skills/opencode-user/reference.md) · [documentação oficial](skills/opencode-user/docs/README.md)

## Codex User

Ensina o agente a delegar trabalho de código ao OpenAI Codex CLI sem acompanhamento: quando vale usar o Codex em vez do Claude Code, do pi ou do OpenCode, a chamada padrão com `codex exec --json`, resposta final em arquivo (`-o`) ou em formato fixo (`--output-schema`), modos de sandbox e aprovação, regras de execução (`.rules`) que bloqueiam `git push`, publicação, deploy, `sudo` e acesso a segredos, retomada e bifurcação de sessão, revisão de código (`codex exec review`), AGENTS.md, skills, MCP, limites de uso do plano do ChatGPT e como conferir o resultado. Traz um resumo de consulta rápida e cópias em markdown de 20 páginas da documentação oficial, atualizáveis com `docs/update.sh`. As execuções com modelo ainda não foram testadas, porque a cota da conta estava esgotada. Instrução em inglês.

Peça, por exemplo: "Use codex-user e peça ao Codex para revisar as mudanças não commitadas deste repositório."

[Codex User](skills/codex-user/SKILL.md) · [resumo de consulta](skills/codex-user/reference.md) · [documentação oficial](skills/codex-user/docs/README.md)

## Estrutura

- **AGENTS.md**: propósito do repositório e regras para agentes.
- **skills/**: uma pasta por skill e o catálogo `index.md`.
  - **SKILL.md**: instruções que o agente carrega.
  - **README.md** (quando houver): uso, instalação e situação.
  - **AGENTS.md** (opcional): regras para alterar e testar a skill.
  - **references/**, **assets/**, **scripts/** (opcionais): material de consulta, mídias e scripts usados pela skill.
  - **results/** ou **tests/** (opcionais): avaliação e testes; não precisam ir para o diretório de skills do agente.
