# Nova avaliação: geração independente

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Resumo agregado

Gerações válidas: 107/912. Chamadas de juízes válidas: 66/432. Julgamentos de pares: 66/1368; escores individuais de impressão: 132/2736.

Cada configuração tem o mesmo peso por par observado. Ausências não valem zero; médias e deltas usam somente pares completos de cada juiz. Valores B/S = baseline/skill. Δ = skill − baseline; menor impressão não demonstra maior qualidade.

| Configuração | Jev | Astra | Opus |
|---|---|---|---|
| anthropic/claude-opus-5.5 / on | Impressão B/S 67.23/59.09; Δ -8.14; qualidade Δ -3.89; n=22; votos {'baseline': 22} | Impressão B/S 84.18/67.09; Δ -17.09; qualidade Δ 7.53; n=22; votos {'skill': 20, 'baseline': 2} | Impressão B/S 68.36/53.00; Δ -15.36; qualidade Δ 3.56; n=22; votos {'skill': 15, 'baseline': 7} |
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

Geração: conhecido USD 5.4624790; custo completo None; 1 chamadas sem custo nativo.
Juízes: conhecido USD 1.783404444; custo completo 1.783404444; 0 chamadas sem custo nativo.
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