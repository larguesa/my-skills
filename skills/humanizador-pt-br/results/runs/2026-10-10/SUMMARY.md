# Nova avaliação: geração independente

Execução: **LIVE_API, interrompida**. Falha de comunicação na chamada MiMo Pro com skill. Os resultados abaixo são parciais, não uma comparação concluída dos 14 modelos. [Estado, custos e limites](README.md).

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Resumo agregado

Gerações válidas: 11/912. Chamadas de juízes válidas: 3/432. Julgamentos de pares: 3/1368; escores individuais de impressão: 6/2736.

Cada configuração tem o mesmo peso por par observado. Ausências não valem zero; médias e deltas usam somente pares completos de cada juiz. Valores B/S = baseline/skill. Δ = skill − baseline; menor impressão não demonstra maior qualidade.

| Configuração | Jev | Astra | Opus |
|---|---|---|---|
| anthropic/claude-opus-5.5 / on | Impressão B/S 61.00/62.00; Δ 1.00; qualidade Δ -2.06; n=1; votos {'baseline': 1} | Impressão B/S 60.00/45.00; Δ -15.00; qualidade Δ 5.25; n=1; votos {'skill': 1} | Impressão B/S 50.00/40.00; Δ -10.00; qualidade Δ 1.25; n=1; votos {'skill': 1} |
| openai/gpt-6-astra / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| x-ai/grok-4.7 / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| google/gemini-3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| meta/muse-spark-1.3 / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-pro / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-pro / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| z-ai/glm-5.3-prime / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-max-prime / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| openai/gpt-6-luna / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| openai/gpt-6-luna / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| z-ai/glm-5.3-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| anthropic/claude-sonnet-5.5 / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |

## Custos e telemetria separados

Geração: conhecido USD 0.450859145; custo nativo completo não informado; uma chamada sem custo nativo. O consumo global foi reconciliado posteriormente em ACCOUNTING.json.
Juízes: conhecido USD 0.045622558; custo completo 0.045622558; 0 chamadas sem custo nativo.
Probes: conhecido USD 0.003877564; reconciliação no recibo separado.

Sem teto monetário. Cache read/write e tokens nativos em TELEMETRY.json; counters ausentes permanecem null. Reasoning não é somado à completion. Custos sintéticos OFFLINE_FAKE são fixtures, nunca gasto real.

## Casos

- [Jornalístico: notícia sobre bibliotecas](experiments/01-noticia-bibliotecas/REPORT.md)
- [Jornalístico: reportagem sobre drenagem](experiments/02-reportagem-drenagem/REPORT.md)
- [Desenvolvimento: documentação de API](experiments/03-documentacao-api/REPORT.md)
- [Desenvolvimento: análise de bug](experiments/04-analise-bug/REPORT.md)
- [Física: movimento e energia](experiments/05-energia-movimento/REPORT.md)
- [Física: medidas de período](experiments/06-experimento-periodo/REPORT.md)
- [Química: equilíbrio](experiments/07-equilibrio-quimico/REPORT.md)
- [Química: titulação](experiments/08-titulacao/REPORT.md)
- [Biologia e meio ambiente: decomposição](experiments/09-decomposicao/REPORT.md)
- [Biologia e meio ambiente: estudo ambiental](experiments/10-estudo-ambiental/REPORT.md)
- [Acadêmico: resumo](experiments/11-resumo-estudo/REPORT.md)
- [Acadêmico: discussão](experiments/12-discussao-estudo/REPORT.md)
- [Didático: cache](experiments/13-cache-iniciantes/REPORT.md)
- [Didático: probabilidade condicional](experiments/14-probabilidade-condicional/REPORT.md)
- [Negócios: proposta comercial](experiments/15-proposta-comercial/REPORT.md)
- [Negócios: comparação de infraestrutura](experiments/16-nota-investimento/REPORT.md)
- [Comunicação profissional: negociação de prazo](experiments/17-email-prazo/REPORT.md)
- [Comunicação profissional: indisponibilidade](experiments/18-comunicado-indisponibilidade/REPORT.md)
- [Opinião e ensaio: IA na educação](experiments/19-ia-educacao/REPORT.md)
- [Opinião e ensaio: concentração e disponibilidade](experiments/20-ensaio-produtividade/REPORT.md)
- [Redes sociais: aprendizado com deploys](experiments/21-linkedin-aprendizado/REPORT.md)
- [Redes sociais: roteiro sobre senhas](experiments/22-roteiro-hash/REPORT.md)
- [Literário: conto na oficina](experiments/23-conto-oficina/REPORT.md)
- [Literário: crônica na lavanderia](experiments/24-cronica-lavanderia/REPORT.md)