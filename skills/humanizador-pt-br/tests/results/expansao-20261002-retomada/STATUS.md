# Ampliação de 2 de outubro de 2026: retomada parcial

A retomada solicitada por Ricardo foi executada. As duas posições anteriormente rejeitadas de MiMo Flash concluíram, com os mesmos pedidos, modelo, rota e parâmetros. Depois, o provedor voltou a rejeitar uma nova posição de MiMo Flash no segundo caso (reportagem de drenagem), por sobrecarga temporária. A execução parou novamente, sem repetição automática, troca de provedor ou teto monetário.

## Resultado preservado e progresso

| Item | Estado observado |
|---|---|
| Pedidos alcançados | 2 de 24; os outros 22 não foram iniciados |
| Posições únicas de geração iniciadas | 61 de 912 |
| Textos com resposta válida | 51; validade da resposta não é correção factual |
| Saídas fora do protocolo | 9, preservadas sem nova geração |
| Nova rejeição sem texto | 1, no segundo pedido |
| Posições de geração não iniciadas | 851 |
| Pares com duas respostas válidas | 25 de 456 |
| Chamadas de julgamento | 12, com Jev, Astra e Opus 5.5 |
| Julgamentos de pares válidos | 39 de 1.368 (13 pares por juiz) |
| Avaliação humana | Pendente |

A retomada realizou 46 chamadas novas: 37 gerações, incluindo as duas novas tentativas explicitamente autorizadas, e nove chamadas de julgamento. Acrescentou 31 textos válidos e 36 julgamentos de pares aos resultados anteriores. As 27 respostas preservadas (20 textos válidos, quatro saídas inválidas e três chamadas de juízes) não foram repetidas nem alteradas.

No primeiro pedido, as 38 posições de geração foram tentadas: 32 textos válidos e seis saídas inválidas, formando 16 pares completos. Os três juízes avaliaram 13 desses pares. Três pares válidos não receberam notas porque pertenciam a grupos congelados que também continham saídas inválidas. No segundo pedido, 23 posições foram tentadas: 19 textos válidos, três saídas inválidas e uma rejeição; há nove pares completos, ainda sem juízes. A apresentação não transforma essas lacunas em votos ou notas.

As nove saídas fora do protocolo incluem excesso de tokens nativos ou término por limite de saída. Os textos retornados, os motivos, os custos e os tempos estão nas evidências. Essas falhas não foram substituídas por textos mais favoráveis.

## Custos conciliados

| Medição | USD |
|---|---:|
| Leitura da chave antes da retomada | 0.613509514 |
| Gasto adicional da retomada, segundo a chave | 1.134190106 |
| Gasto acumulado desta ampliação, segundo a chave | 1.747699620 |
| Soma dos custos conhecidos das respostas e sondagens | 1.7476996204 |
| Sondagens históricas incluídas, contadas uma vez | 0.003979418 |

A diferença de USD -0.0000000004 está abaixo da resolução de nove casas decimais observada no registro da chave. A segunda leitura confirmou o mesmo total. Não houve cobrança adicional observável para a nova rejeição nessa resolução; a API não devolveu custo nativo e o registro não inventa um custo zero. Os dois contos anteriores são outro estudo e não integram esse total.

A chave permaneceu sem limite ou quota monetária durante a execução. A parada foi causada pela rejeição do provedor, não pelo gasto. A chave exclusiva foi desativada depois da interrupção, sem alterar sua política de teto nulo.

[Contabilidade calculada](final-accounting.json) · [Resumo do renderer](report-summary.json) · [Emenda de retomada](RECOVERY.md) · [Tentativas anteriores rejeitadas](previous-rejected-attempts/) · [Estado da primeira execução, intacto](../expansao-20261002/STATUS.md).

## Leitura dos resultados

No primeiro pedido, Jev preferiu a skill em 7/13 pares, Astra em 8/13 e Opus em 9/13. Os mesmos textos foram avaliados pelos três juízes; esses votos não são experimentos independentes, sucesso factual ou prova de superioridade geral. Impressão de IA, qualidade e preferência permanecem campos separados.

Apenas dois pedidos foram alcançados, ambos jornalísticos. Os gêneros técnicos, acadêmicos e demais pedidos continuam sem resultados novos. A amostra parcial não autoriza concluir que a skill melhora textos em geral. As verificações determinísticas e os 97 testes de software passaram, mas não comprovam qualidade linguística ou fidelidade semântica.

## Preservação e publicação

O estudo é uma execução emendada, não uma replicação ininterrupta. O congelamento original, as duas rejeições históricas, os parâmetros e todas as respostas permanecem preservados. A cópia pública omite cookies e identificadores de infraestrutura, sem modificar textos, solicitações, notas ou uso de tokens. A igualdade das 27 respostas reaproveitadas e a integridade dos mapas e julgamentos foram verificadas.

[Resumo e índice](../../README.md) · [Notícia de bibliotecas](../../experiments/01-noticia-bibliotecas/REPORT.md) · [Reportagem de drenagem](../../experiments/02-reportagem-drenagem/REPORT.md).
