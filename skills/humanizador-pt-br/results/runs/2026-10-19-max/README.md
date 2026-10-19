# Humanizador PT-BR 0.7.0: novo teste de 19/10/2026

A skill foi revisada e implementada com Claude Code Opus 5.5, esforço max. Esta execução usa a versão 0.7.0 e o briefing compacto v2, com os mesmos 24 pedidos, 14 modelos e 19 configurações aprovados. Os históricos de 0.5.1 e 0.6.0 permanecem intactos. A ordem diversificada começa pelo Opus nos 24 pedidos e deixa Qwen Flash por último, sem alterar os payloads ou os grupos anônimos.

## Resultado objetivo

| Indicador | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Humanização percebida H, média de 0 a 100 | 26,74 | 40,27 | 13,53 pontos (50,59%) |
| Tokens totais por geração, média | 1362,31 | 6983,69 | 412,64% |
| Tempo da chamada de redação, média em segundos | 16,65 | 19,55 | 17,43% |

H = 100 menos a impressão de IA atribuída pelos juízes. Humanização: 22 pares com os três juízes; 66 julgamentos de pares. Tokens e tempo: 49 e 49 pares, respectivamente. A contagem de tokens inclui a entrada completa e a saída, sem somar raciocínio novamente. O tempo mede a chamada de geração, não juízes nem preparação local.

## Cobertura

| Etapa | Observado | Previsto |
|---|---:|---:|
| Gerações submetidas | 117 | 912 |
| Respostas completas de API | 107 | 912 |
| Pares completos | 49 | 456 |
| Chamadas de juízes válidas | 66 | 432 |
| Julgamentos de pares | 66 | 1.368 |
| Pedidos com respostas completas | 24 | 24 |

Estado: matriz parcial. Motivo de parada registrado: `billing_uncertain`. O consumo registrado coincide com as consultas de geração disponíveis; permanece a divergência de USD 0,029424 frente à soma nativa, documentada em ACCOUNTING.json. A [ordem registrada](SCHEDULE.json) preserva os grupos cegos; chamadas ambíguas não são repetidas. Falhas permanecem nos registros; nenhuma resposta foi refeita ou corrigida.

## Leitura do resultado e interrupção

A revisão foi feita com Claude Code Opus 5.5, esforço max. O teste de redação manteve os modelos e controles do protocolo anterior.

Nos 22 pares do Opus avaliados por todos os juízes, H subiu 13,53 pontos (26,74 para 40,27), e a naturalidade passou de 83,36 para 86,67. A preferência geral ficou em 35 votos com skill e 31 sem skill. A diferença entre juízes é relevante: Jev preferiu o baseline nos 22 pares; Astra preferiu a skill em 20; Opus, em 15. Há melhora de percepção nesta amostra, mas a preferência está dividida.

As médias de tokens (1.362,31 contra 6.983,69) e de tempo (16,65 contra 19,55 segundos) usam 49 pares completos, incluindo Opus, Astra e Grok. As métricas de percepção usam somente o Opus. Portanto, a avaliação não demonstra o resultado da skill nos 14 modelos planejados.

Foram submetidas 117 das 912 gerações: 107 respostas completas, nove respostas inválidas e uma rejeição. As nove inválidas são dois baselines do Opus truncados e sete respostas do Grok com skill cuja contagem de saída excedeu o teto de 4.096 tokens do contrato. Seus textos e custos foram preservados, sem nova tentativa. As 51 respostas completas com skill passaram na checagem mecânica de entrega, sem saídas apenas com comandos. Essa checagem não julga qualidade editorial.

A execução parou no baseline do Grok para o pedido 11: o provedor informou capacidade esgotada (HTTP 502). Restaram 795 gerações não submetidas. Dos 49 pares completos, 27 ficaram sem julgamento porque os grupos cegos preservados ainda não estavam completos; não foram reagrupados. A rodada contém textos dos 24 pedidos, mas só 22 pedidos tiveram julgamento, todos na configuração Opus.

A rodada anterior examinava nove pares de diferentes modelos no primeiro pedido; esta examinou 22 pedidos do Opus. A diferença dos índices agregados entre versões não mede, isoladamente, evolução da skill.

## Consumo observado

O registro da chave mostra USD 7,216459444, igual à soma das 181 consultas de geração disponíveis. As respostas originais somam USD 7,245883444. A diferença de USD 0,029424 corresponde ao custo nativo de uma resposta concluída cuja consulta posterior retornou 404. A rejeição final também não tem custo nativo nem registro recuperável. A diferença permanece documentada, sem atribuir custo zero a qualquer chamada. Consulte [ACCOUNTING.json](ACCOUNTING.json) e [as consultas de geração](GENERATION-COST-LOOKUPS.json).

## Projeção pública

Os textos, pedidos, votos e métricas foram preservados. Metadados de conta foram removidos somente da cópia pública, com hashes rederivados e registro em [SANITIZATION.json](SANITIZATION.json). O SCHEDULE.json guarda a identidade original do congelamento privado; não é um novo plano para executar a projeção sanitizada. As fontes privadas não foram alteradas.

## Consumo e rastreabilidade

Nova chave exclusiva: USD 7.216459444. Geração: custo nativo conhecido USD 5.4624790; juízes: USD 1.783404444. As sondagens de disponibilidade de 10/10 foram reutilizadas com verificação atual das mesmas rotas e não são cobradas novamente nesta soma. Claude Code foi usado pela assinatura Max; seus valores de tabela constam separadamente, não como cobrança adicional comprovada.

## Evidências

- [Métricas por modelo e juiz](OBJETIVO.md), [dados e denominadores](OBJETIVO.json).
- [Textos completos e votos por pedido](SUMMARY.md), [telemetria](TELEMETRY.json).
- [Verificação mecânica de entrega](DELIVERY.json), sem excluir respostas das métricas.
- [Contabilização](ACCOUNTING.json), [testes de software](SOFTWARE-TESTS.json), [revisão independente final](INDEPENDENT-REVIEW-FINAL.json), [achado anterior preservado](INDEPENDENT-REVIEW.json).
- [Execução Claude Code](CLAUDE-REVIEW.json), [protocolo 0.7.0](../../PROTOCOLO-0.7.0.md), [mudanças da skill](../../REVISAO-0.7.0.md).
- [Histórico 0.6.0](../2026-10-19/README.md), [histórico 0.5.1](../2026-10-13/README.md).

As médias se referem apenas aos pares observados. Três juízes avaliam os mesmos textos; H é um índice de percepção, não probabilidade de autoria. A comparação histórica também muda a data e o empacotamento, não apenas a versão da skill.
