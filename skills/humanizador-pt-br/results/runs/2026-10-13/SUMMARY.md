# Nova avaliação: geração independente

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Resumo agregado

Gerações válidas: 30/912. Chamadas de juízes válidas: 12/432. Julgamentos de pares: 33/1368; escores individuais de impressão: 66/2736.

Cada configuração tem o mesmo peso por par observado. Ausências não valem zero; médias e deltas usam somente pares completos de cada juiz. Valores B/S = baseline/skill. Δ = skill − baseline; menor impressão não demonstra maior qualidade.

| Configuração | Jev | Astra | Opus |
|---|---|---|---|
| anthropic/claude-opus-5.5 / on | Impressão B/S 61.00/62.00; Δ 1.00; qualidade Δ -2.06; n=1; votos {'baseline': 1} | Impressão B/S 60.00/45.00; Δ -15.00; qualidade Δ 5.25; n=1; votos {'skill': 1} | Impressão B/S 50.00/40.00; Δ -10.00; qualidade Δ 1.25; n=1; votos {'skill': 1} |
| openai/gpt-6-astra / on | Impressão B/S 73.00/71.00; Δ -2.00; qualidade Δ 0.19; n=1; votos {'baseline': 1} | Impressão B/S 55.00/55.00; Δ 0.00; qualidade Δ 0.00; n=1; votos {'empate': 1} | Impressão B/S 55.00/55.00; Δ 0.00; qualidade Δ 0.00; n=1; votos {'empate': 1} |
| x-ai/grok-4.7 / on | Impressão B/S 55.00/76.00; Δ 21.00; qualidade Δ -14.62; n=1; votos {'baseline': 1} | Impressão B/S 45.00/35.00; Δ -10.00; qualidade Δ -2.00; n=1; votos {'baseline': 1} | Impressão B/S 50.00/55.00; Δ 5.00; qualidade Δ -13.25; n=1; votos {'baseline': 1} |
| google/gemini-3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| meta/muse-spark-1.3 / on | Impressão B/S 66.00/69.00; Δ 3.00; qualidade Δ 1.12; n=1; votos {'baseline': 1} | Impressão B/S 50.00/50.00; Δ 0.00; qualidade Δ 3.25; n=1; votos {'skill': 1} | Impressão B/S 50.00/50.00; Δ 0.00; qualidade Δ 4.25; n=1; votos {'skill': 1} |
| xiaomi/mimo-v2.6-pro / off | Impressão B/S 73.00/79.00; Δ 6.00; qualidade Δ -76.19; n=1; votos {'skill': 1} | Impressão B/S 85.00/100.00; Δ 15.00; qualidade Δ -80.50; n=1; votos {'baseline': 1} | Impressão B/S 75.00/90.00; Δ 15.00; qualidade Δ -68.75; n=1; votos {'baseline': 1} |
| xiaomi/mimo-v2.6-pro / on | Impressão B/S 68.00/63.00; Δ -5.00; qualidade Δ 1.56; n=1; votos {'baseline': 1} | Impressão B/S 85.00/42.00; Δ -43.00; qualidade Δ 50.00; n=1; votos {'skill': 1} | Impressão B/S 62.00/45.00; Δ -17.00; qualidade Δ 33.25; n=1; votos {'skill': 1} |
| z-ai/glm-5.3-prime / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-max-prime / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| openai/gpt-6-luna / off | Impressão B/S 60.00/73.00; Δ 13.00; qualidade Δ -2.12; n=1; votos {'baseline': 1} | Impressão B/S 45.00/35.00; Δ -10.00; qualidade Δ -3.00; n=1; votos {'baseline': 1} | Impressão B/S 45.00/45.00; Δ 0.00; qualidade Δ -8.50; n=1; votos {'baseline': 1} |
| openai/gpt-6-luna / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-flash / off | Impressão B/S 54.00/73.00; Δ 19.00; qualidade Δ -6.50; n=1; votos {'baseline': 1} | Impressão B/S 65.00/80.00; Δ 15.00; qualidade Δ 0.50; n=1; votos {'skill': 1} | Impressão B/S 60.00/70.00; Δ 10.00; qualidade Δ 23.50; n=1; votos {'skill': 1} |
| xiaomi/mimo-v2.6-flash / on | Impressão B/S 63.00/82.00; Δ 19.00; qualidade Δ -41.88; n=1; votos {'baseline': 1} | Impressão B/S 65.00/99.00; Δ 34.00; qualidade Δ -47.75; n=1; votos {'baseline': 1} | Impressão B/S 45.00/90.00; Δ 45.00; qualidade Δ -46.25; n=1; votos {'baseline': 1} |
| z-ai/glm-5.3-flash / on | Impressão B/S 61.00/56.00; Δ -5.00; qualidade Δ 39.75; n=1; votos {'skill': 1} | Impressão B/S 65.00/50.00; Δ -15.00; qualidade Δ 43.00; n=1; votos {'skill': 1} | Impressão B/S 55.00/45.00; Δ -10.00; qualidade Δ 31.00; n=1; votos {'skill': 1} |
| anthropic/claude-sonnet-5.5 / on | Impressão B/S 55.00/56.00; Δ 1.00; qualidade Δ -3.25; n=1; votos {'baseline': 1} | Impressão B/S 68.00/45.00; Δ -23.00; qualidade Δ 8.00; n=1; votos {'skill': 1} | Impressão B/S 55.00/48.00; Δ -7.00; qualidade Δ 3.00; n=1; votos {'skill': 1} |
| qwen/qwen3.8-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |

## Custos e telemetria separados

Geração: conhecido USD 0.6864679240; custo completo None; 1 chamadas sem custo nativo.
Juízes: conhecido USD 0.370330650; custo completo 0.370330650; 0 chamadas sem custo nativo.
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