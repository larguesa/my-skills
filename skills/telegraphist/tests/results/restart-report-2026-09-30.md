# Telegraphist, reinício da avaliação

Atualizado em 2026-09-30. Status: skill e organização corrigidas; bateria de fronteira não executada. Não há novas medições de economia ou acertos.

## Entrega atual

```text
skills/telegraphist/
  SKILL.md
  tests/
    REPORT.md
    scripts/
    results/
```

O corpo da skill usa o prompt fornecido por Ricardo, sem regras adicionais, ferramentas, explicações ou links. Apenas a pontuação entre `language` e `no fluff` foi convertida para vírgula. O exemplo e o literal `PARE.` foram mantidos. Metadados mínimos permanecem no frontmatter.

Scripts e evidências antigos foram realocados, não tratados como avaliação do novo prompt. Os nomes `legacy_*` identificam o piloto anterior. O runner legado está limitado ao desenho original de dois modelos, não implementa a nova matriz de sete modelos nem o trio de juízes.

## Pré-verificação de modelos

Fonte: API oficial OpenRouter, catálogo e endpoints, consultados em 2026-09-30 14:18 UTC. Evidência: [model-preflight-2026-09-30.json](results/model-preflight-2026-09-30.json).

| Nome solicitado | ID consultado | Catálogo / endpoints |
|---|---|---|
| Opus 5.5 | `anthropic/claude-opus-5.5` | Listado; endpoint responde |
| GPT-6-Astra | `openai/gpt-6-astra` | Listado; endpoint responde |
| GPT-6.1-Sol | `openai/gpt-6.1-sol` | Listado; endpoint responde |
| GPT-6.1-Luna | `openai/gpt-6.1-luna` | Ausente; endpoint não encontrado |
| GLM 4.3-Flash | `z-ai/glm-4.3-flash` | Ausente; endpoint não encontrado |
| Gemini 3.8 Flash | `google/gemini-3.8-flash` | Listado; endpoint responde |
| Qwen 3.8 Flash | `qwen/qwen3.8-flash` | Listado; endpoint responde |

Disponibilidade de catálogo não equivale a inferência validada. Nenhuma chamada de geração ou julgamento foi submetida nesta etapa. O endpoint de `typesafe/jev-1.13`, versão usada pelo cliente Jev existente, também respondeu; a rota de inferência Decisions ainda não foi sondada neste reinício. Astra e Opus têm seus endpoints registrados na mesma evidência. Nomes informais não foram usados como autorização para escolher outros modelos.

Há entradas distintas para GPT-6 Luna, GLM 4.7 Flash e GLM 5.3 Flash. Não substituem automaticamente os nomes solicitados. A implementação da bateria aguarda confirmação dos dois IDs e do teto de custo, incluindo candidatos, juízes e sondagens pagas. O limite do piloto anterior não foi reutilizado como autorização para uma nova bateria.

## Métricas solicitadas

| Métrica | Com skill | Sem skill | Razão com / sem |
|---|---|---|---|
| Acertos por trio de juízes | Pendente | Pendente | Não calculada |
| Tokens IN | Pendente | Pendente | Não calculada |
| Tokens OUT | Pendente | Pendente | Não calculada |
| Tokens CACHED | Pendente | Pendente | Não calculada |
| Latência | Pendente | Pendente | Não calculada |
| Custo | Pendente | Pendente | Não calculada |

Pendente significa não medido, nunca zero. Resultados antigos não preenchem esta tabela.

## Contrato proposto para a nova bateria

Este contrato não está congelado nem implementado. Contagem de tarefas, repetições e limites depende do orçamento confirmado.

- HTTPS direto ao OpenRouter, sem SOUL, memórias, AGENTS, plugins ou outras skills. Mesmo sistema neutro, tarefas, ferramentas, limites e configurações dentro de cada modelo; somente o `SKILL.md` completo difere entre braços.
- Incluir trajetórias agênticas de vários passos e tarefas de resposta longa, além de perguntas curtas. Manter histórico acumulado, ferramentas e critério de entrega final equivalentes. Não confundir respostas curtas com sucesso funcional.
- Congelar tarefas, respostas de referência, critérios, runner e prompt antes da primeira geração; preservar hashes e ordenar pares aleatoriamente. Não gerar novas respostas para substituir falhas, respostas vazias ou truncadas.
- Juízes solicitados: Jev, GPT-6 Astra e Opus 5.5. Avaliação individual e cega, sem modelo ou braço revelado; maioria de três determina o acerto quando todos os votos forem válidos. Preservar divergências. Indisponibilidade de um juiz deixa avaliação incompleta, não autoriza maioria de dois.
- Jev usa API Decisions, não chat. Definir pergunta binária e limiar antes da execução. Validar rota, versão e telemetria numa sondagem limitada. Para Astra/Opus, exigir voto estruturado e motivo apoiado no gabarito. Como também são candidatos, explicitar o risco de viés por autoavaliação. Validações determinísticas de formato e execução complementam, não substituem, o trio pedido.
- Acerto significa cumprir tarefa e restrições, preservando conteúdo necessário. Brevidade não rende pontos por si só. Não exigir quantidade exata de palavras em todas as tarefas, nem considerar uma resposta mínima correta apenas por ser pequena.
- IN e OUT vêm da telemetria nativa; IN inclui skill e histórico, OUT inclui raciocínio quando o provedor assim contabiliza. Raciocínio não é somado novamente. Caracteres públicos são medida separada, nunca substituto para tokens nativos.
- Cache-read e cache-write separados; campo ausente permanece desconhecido. Zero declarado é zero observado. Razão com denominador zero é indefinida, acompanhada dos totais absolutos. Medir condições de primeiro uso e cache aquecido separadamente, sem presumir cache frio por falta de diretiva.
- Latência de ponta a ponta, do envio ao retorno completo, com mediana e p95 por braço. Para agentes, informar também duração total da trajetória e número de chamadas. Separar aquecimento, erros e tentativas de disponibilidade da matriz principal.
- Custo real de candidatos e de juízes em grupos separados, incluindo sondagens e falhas potencialmente cobradas; reconciliar custos de resposta com a chave exclusiva. Conta financiada e chave limitada são verificações distintas.
- Razão agregada = soma(com skill) / soma(sem skill), apenas em pares completos comparáveis. Relatar cobertura, diferenças de taxa de acerto, falhas e razões maiores que 1. Latência p50/p95 usa razão das estatísticas correspondentes, não razão de médias de percentis. Não extrapolar um piloto para economia universal ou equivalência de qualidade.

## Verificação offline

Os testes do pacote validam o prompt e a estrutura de pastas. Os testes legados validam scripts antigos, não o comportamento dos modelos novos.

```sh
python3 -B -m unittest discover -s skills/telegraphist/tests/scripts -v
```

32 testes offline passaram: 3 verificam o novo prompt/layout e 29 cobrem scripts legados. O baseline anterior também passou nos 29 testes. Quatro mutações deliberadas (texto adicional, remoção de `PARE.`, arquivo indevido na raiz e arquivo indevido em `tests/`) foram rejeitadas pelos verificadores. Evidências: [execução completa](results/offline-green.txt) e [resumo verificável](results/offline-validation.json). Nenhum resultado offline equivale a benchmark de LLM.

## Histórico preservado

- [Piloto anterior, evidências](results/legacy-pilot-2026-09-29.zip), SHA-256 `7e3a0ad0c8c00ac5b6de6f501ae242a57b24cd825cddf10178863f864817ad01`.
- [Relatório original](results/legacy-report-2026-09-29.md), SHA-256 `cad46b1fc81d946fca09cdba924c273e3da6d156f2182b9b0b620ed546d00c6b`.

Ambos mantêm bytes originais. Caminhos, protocolos, modelos e afirmações no relatório histórico pertencem à versão anterior. Seu conteúdo não demonstra o resultado da skill reescrita e seus comandos não são o procedimento desta nova bateria.
