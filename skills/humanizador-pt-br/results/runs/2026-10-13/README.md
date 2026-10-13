# Resultado objetivo da retomada de 13/10/2026

A matriz continua incompleta. A retomada produziu 19 novas respostas de geração e nove novas chamadas de juízes antes da consolidação. O Qwen Flash recusou uma geração por limite temporário do provedor. Todos os resultados de 10/10 foram preservados; nenhuma resposta válida foi refeita nem a skill ajustada pelos votos.

## As três respostas

| Pergunta | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Humanização percebida, índice médio H de 0 a 100 | 40,03 | 38,52 | -1,52 pontos (-3,79%) |
| Tokens totais por geração, média | 601,47 | 19438,47 | +3131,84% |
| Tempo da chamada de redação, média em segundos | 10,92 | 9,47 | -13,28% |

Nesta amostra, não houve melhora média de humanização. H = 100 menos a impressão de IA atribuída pelo juiz, um índice descritivo não calibrado, não probabilidade de autoria. A média inclui as duas falhas de entrega descritas abaixo. A nota de naturalidade e os resultados separados de Jev, Astra e Opus estão no [relatório objetivo](OBJETIVO.md).

Humanização: 11 pares avaliados pelos três juízes, 33 julgamentos e 66 escores individuais. Tokens e tempo: 15 pares com respostas de API completas, somando entrada e saída sem adicionar reasoning. As duas falhas de entrega permanecem nesses resultados; não foram eliminadas para favorecer a skill.

## Limitações que mudam a interpretação

- Apenas o primeiro dos 24 pedidos, uma notícia sobre bibliotecas, foi executado parcialmente. Não há conclusão geral sobre todos os gêneros ou modelos.
- São 30 respostas de API validadas: 28 textos redigidos e duas saídas compostas apenas por comandos de ferramenta (MiMo Pro sem raciocínio e MiMo Flash com raciocínio, ambos com skill). Esses comandos não foram executados nem tratados como textos bem-sucedidos. A validação original de transporte não garante cumprimento editorial; os juízes viram as saídas reais, sem reparos.
- O tempo compara chamadas completas de geração. Não inclui juízes, tentativas rejeitadas, pausa entre dias nem preparação local da skill, cujo tempo original não foi registrado. Não é o tempo total de uma redação bem-sucedida nos dois casos que não entregaram texto.
- O consumo inclui a skill, os JSONs completos de catálogo/estilos e o plano local injetados em cada chamada, não apenas os tokens visíveis do texto final. Não mede um fluxo otimizado de consultas seletivas ou tool calling autônomo.
- As configurações têm peso igual na média observada. Três votos sobre um par não são três experimentos independentes. Não há repetição por condição nem calibração com leitores humanos.
- Quatro pares completos ficaram sem votos porque pertencem a grupos congelados que também contêm pares pendentes. Os grupos não foram rearranjados após ver os resultados.

## Cobertura e custo

| Etapa | Observado | Planejado |
|---|---:|---:|
| Respostas de geração validadas pela API | 30 | 912 |
| Pares com ambas as respostas completas | 15 | 456 |
| Chamadas de juízes válidas | 12 | 432 |
| Pares avaliados pelos três juízes | 11 | 456 |
| Julgamentos de pares | 33 | 1.368 |

Consumo acumulado da chave exclusiva, incluindo a execução de 10/10 e sondagens: USD 1.060676137 (aproximadamente USD 1.06). Geração: custo nativo conhecido USD 0.6864679240; juízes: USD 0.370330650; sondagens: USD 0.003877564.

O custo informado nas respostas soma USD 1.0606761380. A diferença de USD -1.0E-9 coincide com a precisão observada: a soma de cada chamada arredondada ou truncada a nove casas decimais é exatamente o consumo da chave. Custos nativos ausentes permanecem desconhecidos, não foram inventados como zero. [Contabilização](ACCOUNTING.json).

## Evidências

- [Relatório objetivo, três respostas e tabelas por modelo e juiz](OBJETIVO.md).
- [Dados estruturados e auditoria de origem](OBJETIVO.json).
- [Prompt literal, respostas completas e votos do primeiro pedido](experiments/01-noticia-bibliotecas/REPORT.md).
- [Resumo completo dos juízes](SUMMARY.md) e [telemetria](TELEMETRY.json).
- [Recuperação preservando o protocolo](RECOVERY.json) e [conclusão dos grupos de juízes elegíveis](JUDGING-AMENDMENT.json).
- [Auditoria da publicação](AUDIT.json), [manifesto de hashes](SHA256SUMS) e [resultados anteriores intactos](../2026-10-10/README.md).

## Reprodução local da agregação

Na pasta deste relatório, com Python 3 e sem nenhuma API:

```text
python3 analysis/agregar_objetivo.py --root evidence --scripts evidence/frozen/runner --output analysis/recalculo
```

O destino deve ser novo. O parâmetro `--scripts` aponta explicitamente para o executor congelado incluído no pacote, sem depender do caminho padrão da VPS. Uma reprodução local desta projeção foi executada e confirmou igualdade de percepção, tokens, tempo, cobertura e julgamentos com a origem privada.

Restam 881 gerações não iniciadas, uma rejeição sem resposta e 420 chamadas de juízes não iniciadas. O estudo não foi concluído. Os números acima são resultados parciais, não uma demonstração geral de benefício.
