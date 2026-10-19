# Humanizador PT-BR 0.6.0: novo teste de 19/10/2026

A skill foi revisada e implementada com Claude Code Opus 5.5, esforço high. Esta execução usa a versão 0.6.0 e o briefing compacto v2, com os mesmos 24 pedidos, 14 modelos e 19 configurações aprovados. O histórico de 0.5.1 permanece intacto.

## Resultado objetivo

| Indicador | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Humanização percebida H, média de 0 a 100 | 42,04 | 49,19 | 7,15 pontos (17,00%) |
| Tokens totais por geração, média | 628,33 | 6253,07 | 895,18% |
| Tempo da chamada de redação, média em segundos | 6,91 | 7,37 | 6,68% |

H = 100 menos a impressão de IA atribuída pelos juízes. Humanização: 9 pares com os três juízes; 27 julgamentos de pares. Tokens e tempo: 15 e 15 pares, respectivamente. A contagem de tokens inclui a entrada completa e a saída, sem somar raciocínio novamente. O tempo mede a chamada de geração, não juízes nem preparação local.

A naturalidade bruta média foi de 83,60 sem skill e 81,42 com skill. Na preferência geral, foram 13 votos para o baseline, 11 para a skill e 3 empates. A melhora do índice H não correspondeu a uma preferência majoritária pela skill.

## Cobertura

| Etapa | Observado | Previsto |
|---|---:|---:|
| Gerações submetidas | 32 | 912 |
| Respostas completas de API | 31 | 912 |
| Pares completos | 15 | 456 |
| Chamadas de juízes válidas | 9 | 432 |
| Julgamentos de pares | 27 | 1.368 |
| Pedidos com respostas completas | 1 | 24 |

Estado: matriz parcial. Seis dos 15 pares completos ficaram sem julgamento porque seus grupos congelados também continham pares ausentes; os grupos não foram reorganizados após as respostas. O provedor Alibaba recusou a chamada com skill do Qwen 3.8 Flash por limite temporário de sua capacidade compartilhada (HTTP 429). A contabilização foi reconciliada; a chamada rejeitada não foi repetida. Os grupos completos de juízes foram concluídos conforme [emenda registrada](JUDGING-AMENDMENT.json), sem reagrupar pares. Falhas permanecem nos registros; nenhuma resposta foi refeita ou corrigida.

## Consumo e rastreabilidade

Nova chave exclusiva: USD 0.547210106. Geração: custo nativo conhecido USD 0.2685751024; juízes: USD 0.278635004. As sondagens de disponibilidade de 10/10 foram reutilizadas com verificação atual das mesmas rotas e não são cobradas novamente nesta soma. Claude Code foi usado pela assinatura Max; seus valores de tabela constam separadamente, não como cobrança adicional comprovada.

## Evidências

A pasta `evidence` é uma projeção pública sanitizada. Identificadores de conta foram retirados de cinco respostas de erro; os originais privados foram preservados. [SANITIZATION.json](SANITIZATION.json) registra os hashes originais e públicos, incluindo o manifest público derivado. Textos, julgamentos, payloads, status e telemetria permanecem iguais aos originais.

- [Métricas por modelo e juiz](OBJETIVO.md), [dados e denominadores](OBJETIVO.json).
- [Textos completos e votos por pedido](SUMMARY.md), [telemetria](TELEMETRY.json).
- [Verificação mecânica de entrega](DELIVERY.json), sem excluir respostas das métricas.
- [Contabilização](ACCOUNTING.json), [testes de software](SOFTWARE-TESTS.json), [revisão independente final](INDEPENDENT-REVIEW-FINAL.json), [achado anterior preservado](INDEPENDENT-REVIEW.json).
- [Execução Claude Code](CLAUDE-REVIEW.json), [protocolo 0.6.0](../../PROTOCOLO-0.6.0.md), [mudanças da skill](../../REVISAO-2026-10-19.md).
- [Histórico 0.5.1](../2026-10-13/README.md).

As médias se referem apenas aos pares observados. Três juízes avaliam os mesmos textos; H é um índice de percepção, não probabilidade de autoria. A comparação histórica também muda a data e o empacotamento, não apenas a versão da skill.
