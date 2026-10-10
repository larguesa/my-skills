# Avaliação 0.5.1: execução interrompida

## Resultado prático

A limpeza solicitada foi concluída. A nova avaliação de geração independente começou com os 24 pedidos aprovados, mas parou durante uma chamada do MiMo Pro com a skill, que retornou falha de comunicação e nenhum texto. A origem dessa falha não foi diagnosticada. Não houve repetição da chamada nem alteração da skill pelos votos.

| Etapa | Resultado observado | Planejado |
|---|---:|---:|
| Chamadas de geração iniciadas | 12 | 912 |
| Textos válidos preservados | 11 | 912 |
| Pares com ambas as versões válidas | 5 | 456 |
| Chamadas de juízes válidas | 3 | 432 |
| Pares distintos julgados | 1 | 456 |
| Julgamentos de pares | 3 | 1.368 |
| Escores individuais de impressão | 6 | 2.736 |

Todos os textos produzidos pertencem ao primeiro pedido, uma notícia sobre bibliotecas. Os outros 23 pedidos não foram executados. Permanecem 900 chamadas de geração não iniciadas, uma chamada interrompida sem saída e 429 chamadas de juízes não iniciadas. Os relatórios dos casos não executados são apenas registros de pendência, não resultados.

No único par julgado, Astra e Opus preferiram a versão com skill; Jev preferiu o baseline. Isso é uma observação de um par, não evidência de superioridade geral. Os cinco pares completos e o baseline isolado do MiMo podem ser lidos na [comparação integral](experiments/01-noticia-bibliotecas/REPORT.md). Faça uma avaliação humana desses textos antes de concluir sobre qualidade.

## Custos registrados

Valores em USD. Tempo é a soma do tempo de cliente de cada chamada, incluindo a tentativa interrompida; não é TTFT nem tempo de computação isolado. Custos das sondagens não estão distribuídos na tabela de candidatos.

| Gerador / raciocínio | Chamadas | Textos válidos | Custo nativo conhecido | Custos nativos ausentes | Tempo de chamadas (s) |
|---|---:|---:|---:|---:|---:|
| Claude Opus 5.5 / on | 2 | 2 | 0.136868 | 0 | 19.684 |
| GPT-6 Astra / on | 2 | 2 | 0.2213625 | 0 | 5.484 |
| Grok 4.7 / on | 2 | 2 | 0.039584 | 0 | 10.168 |
| Gemini 3.8 Flash / on | 2 | 2 | 0.01966575 | 0 | 10.858 |
| Muse Spark 1.3 / on | 2 | 2 | 0.0331105 | 0 | 50.124 |
| MiMo 2.6 Pro / off | 2 | 1 | 0.000268395 | 1 | 365.335 |

| Juiz | Chamadas válidas | Custo nativo | Tempo de chamadas (s) |
|---|---:|---:|---:|
| Jev 1.13 | 1 | 0.000138558 | 0.413 |
| Astra | 1 | 0.0237 | 6.981 |
| Opus 5.5 | 1 | 0.021784 | 16.030 |

Gerações com custo informado: USD 0.450859145. Juízes: USD 0.045622558. Sondagens: USD 0.003877564. Soma conhecida e consumo da chave exclusiva: **USD 0.500359267**, reconciliados exatamente na leitura de 10/10/2026 às 20:03:34 UTC.

A tentativa interrompida não informou custo nativo; sua consulta de metadados retornou indisponível. O custo individual permanece desconhecido, não foi inventado como zero. A igualdade com o consumo da chave significa que não foi observada cobrança adicional inexplicada nessa leitura. [Contabilização](ACCOUNTING.json) e [telemetria](TELEMETRY.json) preservam essa distinção.

## Evidências e leitura

- [Resumo por configuração e juiz](SUMMARY.md), com denominadores e ausências.
- [Resumo estruturado](SUMMARY.json).
- [Comparação com prompt literal e textos completos](experiments/01-noticia-bibliotecas/REPORT.md).
- [Auditoria](AUDIT.json), com igualdade dos 11 textos, registros brutos e integridade do freeze.
- [Manifesto original](evidence/manifest.json) e [estado final do runner](evidence/runtime-summary.json).
- [Fontes, payloads, respostas e mapeamento anônimo](evidence/), sem credenciais ou arquivos privados da conta.

A resposta interrompida trouxe erro de API 502 dentro de uma resposta HTTP 200, sem texto ou usage. O recibo original está preservado em evidence/requests. O estado `billing_uncertain` foi mantido no registro original; a reconciliação posterior não reescreve a resposta nem transforma a tentativa em geração válida.

## Limites

Geração independente, não reescrita do baseline. O tratamento inclui skill, catálogo e estilos completos, mais consultas/plano locais congelados antes da redação. Não mede tool calling autônomo completo. Há uma geração por condição e configuração, apenas um pedido executado parcialmente e um par com três votos. Impressão de IA não comprova autoria, não é probabilidade calibrada e não substitui qualidade ou fidelidade. Não há conclusão geral nem ranking válido dos 14 modelos. Nenhum resultado histórico ou fixture offline foi apresentado como resultado novo.
