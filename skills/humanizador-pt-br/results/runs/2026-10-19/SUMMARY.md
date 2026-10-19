# Nova avaliação: geração independente

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Resumo agregado

Gerações válidas: 31/912. Chamadas de juízes válidas: 9/432. Julgamentos de pares: 27/1368; escores individuais de impressão: 54/2736.

Cada configuração tem o mesmo peso por par observado. Ausências não valem zero; médias e deltas usam somente pares completos de cada juiz. Valores B/S = baseline/skill. Δ = skill − baseline; menor impressão não demonstra maior qualidade.

| Configuração | Jev | Astra | Opus |
|---|---|---|---|
| anthropic/claude-opus-5.5 / on | Impressão B/S 69.00/68.00; Δ -1.00; qualidade Δ 0.06; n=1; votos {'baseline': 1} | Impressão B/S 78.00/55.00; Δ -23.00; qualidade Δ 10.50; n=1; votos {'skill': 1} | Impressão B/S 60.00/45.00; Δ -15.00; qualidade Δ -4.75; n=1; votos {'baseline': 1} |
| openai/gpt-6-astra / on | Impressão B/S 66.00/64.00; Δ -2.00; qualidade Δ -1.19; n=1; votos {'skill': 1} | Impressão B/S 45.00/45.00; Δ 0.00; qualidade Δ 0.00; n=1; votos {'empate': 1} | Impressão B/S 50.00/50.00; Δ 0.00; qualidade Δ 0.50; n=1; votos {'empate': 1} |
| x-ai/grok-4.7 / on | Impressão B/S 62.00/72.00; Δ 10.00; qualidade Δ -7.38; n=1; votos {'baseline': 1} | Impressão B/S 40.00/30.00; Δ -10.00; qualidade Δ -2.00; n=1; votos {'baseline': 1} | Impressão B/S 45.00/35.00; Δ -10.00; qualidade Δ -15.75; n=1; votos {'baseline': 1} |
| google/gemini-3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| meta/muse-spark-1.3 / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-pro / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-pro / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| z-ai/glm-5.3-prime / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-max-prime / on | Impressão B/S 71.00/67.00; Δ -4.00; qualidade Δ -2.69; n=1; votos {'baseline': 1} | Impressão B/S 85.00/35.00; Δ -50.00; qualidade Δ 49.75; n=1; votos {'skill': 1} | Impressão B/S 70.00/40.00; Δ -30.00; qualidade Δ 26.00; n=1; votos {'skill': 1} |
| openai/gpt-6-luna / off | Impressão B/S 59.00/71.00; Δ 12.00; qualidade Δ -13.44; n=1; votos {'baseline': 1} | Impressão B/S 40.00/40.00; Δ 0.00; qualidade Δ -2.00; n=1; votos {'baseline': 1} | Impressão B/S 45.00/45.00; Δ 0.00; qualidade Δ -9.50; n=1; votos {'baseline': 1} |
| openai/gpt-6-luna / on | Impressão B/S 53.00/57.00; Δ 4.00; qualidade Δ 2.25; n=1; votos {'baseline': 1} | Impressão B/S 35.00/40.00; Δ 5.00; qualidade Δ 2.25; n=1; votos {'skill': 1} | Impressão B/S 40.00/45.00; Δ 5.00; qualidade Δ -1.00; n=1; votos {'empate': 1} |
| xiaomi/mimo-v2.6-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| xiaomi/mimo-v2.6-flash / on | Impressão B/S 54.00/67.00; Δ 13.00; qualidade Δ -5.94; n=1; votos {'baseline': 1} | Impressão B/S 65.00/45.00; Δ -20.00; qualidade Δ 11.50; n=1; votos {'skill': 1} | Impressão B/S 45.00/50.00; Δ 5.00; qualidade Δ 9.00; n=1; votos {'skill': 1} |
| z-ai/glm-5.3-flash / on | Impressão B/S 68.00/64.00; Δ -4.00; qualidade Δ 39.62; n=1; votos {'skill': 1} | Impressão B/S 75.00/40.00; Δ -35.00; qualidade Δ 45.50; n=1; votos {'skill': 1} | Impressão B/S 55.00/40.00; Δ -15.00; qualidade Δ 29.75; n=1; votos {'skill': 1} |
| anthropic/claude-sonnet-5.5 / on | Impressão B/S 65.00/67.00; Δ 2.00; qualidade Δ 5.31; n=1; votos {'baseline': 1} | Impressão B/S 70.00/45.00; Δ -25.00; qualidade Δ 12.75; n=1; votos {'skill': 1} | Impressão B/S 55.00/50.00; Δ -5.00; qualidade Δ -2.25; n=1; votos {'baseline': 1} |
| qwen/qwen3.8-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| qwen/qwen3.8-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / off | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |
| deepseek/deepseek-v4.1-flash / on | PENDENTE (n=0) | PENDENTE (n=0) | PENDENTE (n=0) |

## Custos e telemetria separados

Geração: conhecido USD 0.2685751024; custo completo None; 1 chamadas sem custo nativo.
Juízes: conhecido USD 0.278635004; custo completo 0.278635004; 0 chamadas sem custo nativo.
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