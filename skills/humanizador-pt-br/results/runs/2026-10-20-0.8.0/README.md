# Humanizador PT-BR 0.8.0: rodada de 20/10/2026

A execução foi interrompida após 15,75 minutos de espera sem resposta completa do Opus no terceiro pedido. Os dois primeiros pares foram avaliados por Jev, Astra e Opus. A matriz de 24 pedidos e 19 configurações ficou pendente.

A interrupção operacional está registrada em [SUPERVISION.json](SUPERVISION.json). A chamada sem conclusão foi preservada e não foi repetida; não recebeu nota.

**Situação: inconclusivo.** Pré-requisitos incompletos: software ou todos os pares válidos e julgados pelos três juízes.

Referência: sem skill. Critério: [AGENTS congelado](AGENTS-frozen.md), vinculado ao [protocolo](PROTOCOL.json).

## Resultado do ciclo

| Indicador | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| H do ciclo | 31,67 | 47,33 | 15,67 pontos |
| Tokens totais por geração, média | 1766,00 | 10264,50 | 481,23% |
| Tempo da geração API, média em segundos | 16,66 | 18,93 | 13,62% |

H = 100 menos impressão de IA. H do ciclo é a média dos pares com os três juízes, conforme AGENTS: 2/456 pares. Não é probabilidade de autoria. O agregado de configurações com peso igual permanece em OBJETIVO.md; numa matriz parcial ele pode diferir do H do ciclo.
Tokens: 2 pares, entrada completa mais saída, sem somar reasoning novamente. Tempo API: 2 pares, sem juízes nem preparação local. Ausência não vale zero.

## Preferência, falhas e decisão

Preferência: sem skill 2, com skill 4, empates 0; total 6 votos. Empates entram no total, não em um braço.
Falhas críticas: sem skill 1/6, com skill 0/6 julgamentos por braço.
Testes de software passando: sim. Plano completo: não. Aceitação requer ΔH ≥ 5, ganho em ao menos dois juízes, votos não inferiores e falhas críticas não superiores. Falta de pré-requisito torna a rodada inconclusiva.
Falhas/alertas API: 1; falhas mecânicas de entrega: 0; grupos bloqueados: 142. Nenhum texto ou escore foi corrigido ou excluído da fonte.
Chamadas ausentes: 1332/1344; registros não completos: 1. [Lista integral de ausências e falhas](FAILURES.json), com slots e categorias; saídas inválidas disponíveis permanecem nos 24 relatórios.
Motivo de parada registrado: ambiguous_intent_without_raw.

## Cobertura

| Etapa | Observado | Previsto |
|---|---:|---:|
| geracoes_submetidas | 6 | 912 |
| respostas_api_validadas | 5 | 912 |
| textos_redigidos | 5 | 912 |
| respostas_somente_comandos | 0 | 912 |
| pedidos_com_resposta_api_validada | 3 | 24 |
| pedidos_com_julgamento | 2 | 24 |
| pares_geracao_validos | 2 | 456 |
| chamadas_juizes_submetidas | 6 | 432 |
| chamadas_juizes_validas | 6 | 432 |
| julgamentos_pares | 6 | 1368 |
| escores_individuais | 12 | 2736 |
| pares_com_algum_juiz | 2 | 456 |
| pares_tres_juizes | 2 | 456 |
| configuracoes_com_tres_juizes | 1 | 19 |
| pares_tokens | 2 | 456 |
| pares_tempo | 2 | 456 |

## Modelos e modos

| Modelo | Modo | Provedor | USD nativo conhecido | Chamadas sem custo | Soma duração API (s) | Chamadas cronometradas |
|---|---|---|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 | on | amazon-bedrock | 0.231424 | 1 | 84,08 | 5 |
| openai/gpt-6-astra | on | openai | indisponível | 0 | indisponível | 0 |
| x-ai/grok-4.7 | on | xai/zdr | indisponível | 0 | indisponível | 0 |
| google/gemini-3.8-flash | on | google-ai-studio | indisponível | 0 | indisponível | 0 |
| meta/muse-spark-1.3 | on | meta | indisponível | 0 | indisponível | 0 |
| xiaomi/mimo-v2.6-pro | off | xiaomi/fp8 | indisponível | 0 | indisponível | 0 |
| xiaomi/mimo-v2.6-pro | on | xiaomi/fp8 | indisponível | 0 | indisponível | 0 |
| z-ai/glm-5.3-prime | on | alibaba | indisponível | 0 | indisponível | 0 |
| qwen/qwen3.8-max-prime | on | alibaba | indisponível | 0 | indisponível | 0 |
| openai/gpt-6-luna | off | openai | indisponível | 0 | indisponível | 0 |
| openai/gpt-6-luna | on | openai | indisponível | 0 | indisponível | 0 |
| xiaomi/mimo-v2.6-flash | off | xiaomi/fp8 | indisponível | 0 | indisponível | 0 |
| xiaomi/mimo-v2.6-flash | on | xiaomi/fp8 | indisponível | 0 | indisponível | 0 |
| z-ai/glm-5.3-flash | on | z-ai/fp8 | indisponível | 0 | indisponível | 0 |
| anthropic/claude-sonnet-5.5 | on | google-vertex/global | indisponível | 0 | indisponível | 0 |
| qwen/qwen3.8-flash | off | alibaba/us-east-1 | indisponível | 0 | indisponível | 0 |
| qwen/qwen3.8-flash | on | alibaba/us-east-1 | indisponível | 0 | indisponível | 0 |
| deepseek/deepseek-v4.1-flash | off | sail-research/fp4 | indisponível | 0 | indisponível | 0 |
| deepseek/deepseek-v4.1-flash | on | sail-research/fp4 | indisponível | 0 | indisponível | 0 |

## Juízes

| Juiz | Modelo | Modo | ΔH | Votos observados | USD nativo conhecido | Duração API conhecida (s) |
|---|---|---|---:|---:|---:|---:|
| jev | typesafe/jev-1.13 | Decisions nativo | 5,50 | 2 | 0.000348306 | 0,73 |
| astra | openai/gpt-6-astra | {'effort': 'medium', 'enabled': True} | 24,00 | 2 | 0.0837725 | 22,08 |
| opus | anthropic/claude-opus-5.5 | {'effort': 'medium', 'enabled': True} | 17,50 | 2 | 0.059076 | 19,50 |

## Custo e duração mensurada

Ledger da chave dedicada: USD 0.374620806. Soma nativa conhecida: USD 0.374620806. Diferença ledger menos soma nativa: USD 0E-9.
Reconciliação na resolução observada: True. Chamadas sem custo nativo: 1. Valores ausentes não são custo zero; a publicação não reclassifica cobranças.
Novas sondagens: USD 0. Custo histórico excluído do ledger novo: True. Geração e juízes separados em [ACCOUNTING.json](ACCOUNTING.json).
Janela observada: 2026-10-20T17:20:26.047212+00:00 a 2026-10-20T17:23:01.632931+00:00; 155,59 s, incluindo pausas. Soma das chamadas cronometradas: 126,38 s em 11/12 chamadas. Não representa prazo para completar a matriz.
Preparação local: {"casos_relevantes": 2, "casos_com_medicao": 0, "segundos_conhecidos": 0, "soma_completa": null, "criterio": "consulta compartilhada de preparação por caso, rateada entre pares de tempo válidos; não repetida por configuração"}.

## Evidências

- [Métricas e denominadores](OBJETIVO.md), [dados objetivos](OBJETIVO.json), [decisão reproduzível](DECISION.json).
- [Resumo do renderer](SUMMARY.md), [telemetria](TELEMETRY.json), [contabilização](ACCOUNTING.json).
- [Auditoria local](AUDIT.json), [sanitização e hashes de origem](SANITIZATION.json), [inventário da fonte](SOURCE-SHA256.json), [SHA256SUMS](SHA256SUMS).
- [Manifesto público rederivado](evidence/manifest.json). SCHEDULE conserva a identidade histórica privada; a projeção não deve ser usada para retomar chamadas.
## Textos completos dos 24 casos

- [01-noticia-bibliotecas: Jornalístico: notícia sobre bibliotecas](experiments/01-noticia-bibliotecas/REPORT.md)
- [02-reportagem-drenagem: Jornalístico: reportagem sobre drenagem](experiments/02-reportagem-drenagem/REPORT.md)
- [03-documentacao-api: Desenvolvimento: documentação de API](experiments/03-documentacao-api/REPORT.md)
- [04-analise-bug: Desenvolvimento: análise de bug](experiments/04-analise-bug/REPORT.md)
- [05-energia-movimento: Física: movimento e energia](experiments/05-energia-movimento/REPORT.md)
- [06-experimento-periodo: Física: medidas de período](experiments/06-experimento-periodo/REPORT.md)
- [07-equilibrio-quimico: Química: equilíbrio](experiments/07-equilibrio-quimico/REPORT.md)
- [08-titulacao: Química: titulação](experiments/08-titulacao/REPORT.md)
- [09-decomposicao: Biologia e meio ambiente: decomposição](experiments/09-decomposicao/REPORT.md)
- [10-estudo-ambiental: Biologia e meio ambiente: estudo ambiental](experiments/10-estudo-ambiental/REPORT.md)
- [11-resumo-estudo: Acadêmico: resumo](experiments/11-resumo-estudo/REPORT.md)
- [12-discussao-estudo: Acadêmico: discussão](experiments/12-discussao-estudo/REPORT.md)
- [13-cache-iniciantes: Didático: cache](experiments/13-cache-iniciantes/REPORT.md)
- [14-probabilidade-condicional: Didático: probabilidade condicional](experiments/14-probabilidade-condicional/REPORT.md)
- [15-proposta-comercial: Negócios: proposta comercial](experiments/15-proposta-comercial/REPORT.md)
- [16-nota-investimento: Negócios: comparação de infraestrutura](experiments/16-nota-investimento/REPORT.md)
- [17-email-prazo: Comunicação profissional: negociação de prazo](experiments/17-email-prazo/REPORT.md)
- [18-comunicado-indisponibilidade: Comunicação profissional: indisponibilidade](experiments/18-comunicado-indisponibilidade/REPORT.md)
- [19-ia-educacao: Opinião e ensaio: IA na educação](experiments/19-ia-educacao/REPORT.md)
- [20-ensaio-produtividade: Opinião e ensaio: concentração e disponibilidade](experiments/20-ensaio-produtividade/REPORT.md)
- [21-linkedin-aprendizado: Redes sociais: aprendizado com deploys](experiments/21-linkedin-aprendizado/REPORT.md)
- [22-roteiro-hash: Redes sociais: roteiro sobre senhas](experiments/22-roteiro-hash/REPORT.md)
- [23-conto-oficina: Literário: conto na oficina](experiments/23-conto-oficina/REPORT.md)
- [24-cronica-lavanderia: Literário: crônica na lavanderia](experiments/24-cronica-lavanderia/REPORT.md)

Cada caso inclui pedido literal, respostas completas e escores disponíveis dos três juízes. Ausências e falhas permanecem explícitas. Não há reclassificação das rodadas anteriores.
