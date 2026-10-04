# Encerramento da ampliação Humanizador PT-BR

Execução encerrada: 912 posições percorridas, 848 respostas válidas de transporte, 64 saídas inválidas terminais. Isso não certifica correção factual ou cumprimento mecânico. Os 315 julgamentos em lote elegíveis terminaram; 39 grupos inelegíveis permaneceram sem submissão. São 308 pares julgados por cada juiz, 924 julgamentos de pares no total. Outros 102 pares completos não receberam notas por compartilhar grupos congelados com saídas inválidas; não serão reagrupados. Gasto conciliado: US$ 28.480551395 (incremento da retomada periódica: US$ 26.732851775). Avaliação humana e fidelidade semântica permanecem pendentes.

## Leitura dos resultados

| Juiz | Prefere skill | Prefere original | Empates | Impressão IA original | Impressão IA skill | Qualidade limitada original | Qualidade limitada skill |
|---|---:|---:|---:|---:|---:|---:|---:|
| Jev | 152 | 156 | 0 | 68.09 | 65.06 | 82.98 | 83.05 |
| Astra | 143 | 142 | 23 | 77.92 | 73.81 | 86.98 | 86.94 |
| Opus 5.5 | 161 | 130 | 17 | 60.76 | 56.13 | 76.86 | 78.42 |

Cada linha tem n=308 pares; peso igual por configuração observada. São opiniões dos mesmos textos, não 924 experimentos independentes. Impressão IA não comprova autoria. Qualidade e preferência não são a mesma métrica.

Não há vencedor geral: Jev prefere ligeiramente originais, Astra fica praticamente dividido, Opus prefere mais versões com skill. As médias de qualidade de Jev/Astra mudam pouco; a vantagem de Opus é descritiva. A menor impressão média de IA dos três juízes não prova superioridade ou evasão de detectores.

## Custos e tempo

Medições, sem teto monetário.

| Grupo | Chamadas observadas | Custo conhecido USD | Custos desconhecidos | Tempos conhecidos / chamadas |
|---|---:|---:|---:|---:|
| generation | 912 | 11.5044255928 | 0 | 17514.05 s; 912/912 |
| jev | 105 | 0.046255902 | 0 | 46.69 s; 105/105 |
| astra | 105 | 11.1417625 | 0 | 2802.14 s; 105/105 |
| opus | 105 | 5.784128 | 0 | 2247.69 s; 105/105 |
| probes\_extra | 20 | 0.003979418 | 0 | 34.74 s; 20/20 |

Custos de geração, Jev, Astra, Opus e sondagens/extras separados. Custo conhecido é parcial quando há chamadas de custo desconhecido; chamadas não iniciadas não são custo zero.


Ledger conciliado: US$ 28.480551395. Soma nativa com sondagens: US$ 28.4805514128. Diferença observada: US$ -1.78E-8; a soma de cada chamada truncada à resolução observada de 9 decimais coincide exatamente com o ledger. Isso não estabelece uma regra universal de faturamento.

Sondagens históricas: US$ 0.003979418, contadas uma única vez. Não houve nova sondagem paga nesta retomada periódica. O incremento é US$ 26.732851775; os resultados históricos de outros estudos não estão incluídos.

Primeira chamada preservada: 2026-10-02T13:08:09.405210+00:00; última resposta: 2026-10-04T09:42:21.401513+00:00. Janela total: 44.57 horas, incluindo pausas e recuperações, não apenas latência de inferência.

## Saídas inválidas e tokens

Os 64 desfechos inválidos incluem 30 respostas com `finish_reason=length` e 34 que informaram conclusão acima do limite de 4.096 tokens solicitado. Foram preservados, não corrigidos nem regenerados. O braço original teve 428 respostas válidas e 28 inválidas; o braço com skill, 420 válidas e 36 inválidas. Validade aqui é de resposta/telemetria, não aprovação editorial.

| Grupo | Chamadas | Entrada nativa | Saída nativa |
|---|---:|---:|---:|
| Original, chat | 456 | 174359 | 624329 |
| Com skill, chat | 456 | 2863439 | 675823 |
| Astra e Opus, chat | 210 | 818994 | 333174 |
| Jev, Decisions | 105 | 1101331 | 92407 |

Os totais incluem saídas inválidas cobradas. Entrada/saída usam `prompt_tokens`/`completion_tokens` no chat e `input_tokens`/`output_tokens` no Decisions, preservados por chamada. Tokens de raciocínio não são somados novamente à saída. O pacote editorial aumenta a entrada; não há alegação de economia de tokens. Sondagens têm contabilidade separada.

## Integridade e intervenções

- 912 posições únicas e 315 chamadas elegíveis verificadas contra os payloads/mapas congelados; nenhuma submissão ambígua.
- Textos, raciocínio público registrado, tokens, custos e notas da projeção comparados exatamente aos registros privados; skill e rotas não foram alteradas.
- 38 rejeições históricas arquivadas nesta recuperação, com novas tentativas somente após reconciliação e intervalo mínimo autorizado; demais resultados preservados byte a byte.
- Os 97 testes offline passaram; validam software, não qualidade editorial. Nenhum código de candidato foi executado.
- Publicados requests autoritativos, mapas, congelamento e relatórios. Logs, chaves, controles e cópias redundantes de fases permanecem privados. Metadados de autorização e caminhos do renderer foram normalizados apenas na publicação.
- Estados de apresentação foram marcados como encerrados; notas ausentes não foram inventadas. O renderer reconstitui tabelas/médias; os rótulos terminais são explicados nesta página.
- A primeira preparação offline da publicação omitiu `EXECUTION.md`, exigido pelo congelamento; falhou antes de renderizar relatórios. O arquivo foi incluído byte a byte e os hashes foram novamente verificados, sem chamadas pagas ou alteração de resultados.
- [Snapshot dos relatórios anteriores](history-before-completion/README.md); histórico dos dois contos e publicações anteriores intactos.

## Avaliação humana

Leia os [24 relatórios completos](../../README.md), comparando os textos originais e com skill. Diga onde há melhora de leitura, perda de precisão ou mudança de registro. A decisão de adoção permanece pendente.
