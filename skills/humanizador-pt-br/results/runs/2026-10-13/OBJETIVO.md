# Resultado objetivo

Execução: **LIVE_API**.

**Nota essencial:** 2 respostas retornam somente comandos tool_call, sem entregar prosa: g.01-noticia-bibliotecas.r05.skill, g.01-noticia-bibliotecas.r12.skill. Nenhum comando foi executado. As falhas permanecem nas métricas principais, inclusive H, tokens e tempo. Há 30 respostas API validadas, mas 28 textos redigidos.

1. **Humanização percebida:** índice H médio baseline 40.03/100 e skill 38.52/100; diferença -1.52 pontos; variação relativa -3.79%. Não calibrado, não probabilidade de autoria. 11 pares com três juízes em 11 configurações observadas.
2. **Tokens:** variação 3131.84% pela razão das somas. Baseline/skill 9022.00/291577.00 tokens; médias 601.47/19438.47 por geração; n=15 pares completos. Entrada mais saída, sem somar reasoning.
3. **Tempo de redação via API:** variação -13.28%; somas baseline/skill 163.73/141.98 s; médias 10.92/9.47 s; n=15 pares completos. Sem juízes, retries ou pausas.

Consultas locais da skill: 0/1 casos relevantes medidos; 0.00 s conhecidos. Tempo incluindo preparo local compartilhado: indisponível, não tratado como zero.

Naturalidade bruta média baseline/skill: 82.57/69.41, escala 0 a 100. Pool descritivo de julgamentos: H 40.03/38.52; n=33.

## Modelos

| Modelo | Configurações | H baseline/skill | Diferença H em pontos | Tokens % | Tempo API % | Pares tokens/tempo |
|---|---:|---|---:|---:|---:|---|
| anthropic/claude-opus-5.5 | 1 | 43.00/51.00 | 8.00 | 4292.42 | 103.29 | 1/1 |
| anthropic/claude-sonnet-5.5 | 1 | 40.67/50.33 | 9.67 | 5287.85 | 4.74 | 1/1 |
| deepseek/deepseek-v4.1-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| google/gemini-3.8-flash | 1 | indisponível/indisponível | indisponível | 1457.85 | -27.61 | 1/1 |
| meta/muse-spark-1.3 | 1 | 44.67/43.67 | -1.00 | 1283.46 | 17.27 | 1/1 |
| openai/gpt-6-astra | 1 | 39.00/39.67 | 0.67 | 7659.45 | -13.49 | 1/1 |
| openai/gpt-6-luna | 2 | 50.00/49.00 | -1.00 | 6736.23 | 39.92 | 2/2 |
| qwen/qwen3.8-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-max-prime | 1 | indisponível/indisponível | indisponível | 2967.54 | 286.43 | 1/1 |
| x-ai/grok-4.7 | 1 | 50.00/44.67 | -5.33 | 1067.20 | 90.34 | 1/1 |
| xiaomi/mimo-v2.6-flash | 2 | 41.33/17.67 | -23.67 | 4585.08 | -7.38 | 2/2 |
| xiaomi/mimo-v2.6-pro | 2 | 25.33/30.17 | 4.83 | 3769.73 | -66.09 | 2/2 |
| z-ai/glm-5.3-flash | 1 | 39.67/49.67 | 10.00 | 5607.91 | -19.00 | 1/1 |
| z-ai/glm-5.3-prime | 1 | indisponível/indisponível | indisponível | 5378.18 | -10.06 | 1/1 |

## Configurações

| Modelo / modo / provedor | H baseline/skill | Diferença em pontos | Pares 3 juízes | Tokens % | Tempo % | Pares válidos |
|---|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 / on / amazon-bedrock | 43.00/51.00 | 8.00 | 1/24 | 4292.42 | 103.29 | 1/24 |
| openai/gpt-6-astra / on / openai | 39.00/39.67 | 0.67 | 1/24 | 7659.45 | -13.49 | 1/24 |
| x-ai/grok-4.7 / on / xai/zdr | 50.00/44.67 | -5.33 | 1/24 | 1067.20 | 90.34 | 1/24 |
| google/gemini-3.8-flash / on / google-ai-studio | indisponível/indisponível | indisponível | 0/24 | 1457.85 | -27.61 | 1/24 |
| meta/muse-spark-1.3 / on / meta | 44.67/43.67 | -1.00 | 1/24 | 1283.46 | 17.27 | 1/24 |
| xiaomi/mimo-v2.6-pro / off / xiaomi/fp8 | 22.33/10.33 | -12.00 | 1/24 | 4770.45 | -92.48 | 1/24 |
| xiaomi/mimo-v2.6-pro / on / xiaomi/fp8 | 28.33/50.00 | 21.67 | 1/24 | 3125.81 | 47.49 | 1/24 |
| z-ai/glm-5.3-prime / on / alibaba | indisponível/indisponível | indisponível | 0/24 | 5378.18 | -10.06 | 1/24 |
| qwen/qwen3.8-max-prime / on / alibaba | indisponível/indisponível | indisponível | 0/24 | 2967.54 | 286.43 | 1/24 |
| openai/gpt-6-luna / off / openai | 50.00/49.00 | -1.00 | 1/24 | 7910.00 | 18.01 | 1/24 |
| openai/gpt-6-luna / on / openai | indisponível/indisponível | indisponível | 0/24 | 5868.31 | 56.26 | 1/24 |
| xiaomi/mimo-v2.6-flash / off / xiaomi/fp8 | 40.33/25.67 | -14.67 | 1/24 | 5470.57 | 20.12 | 1/24 |
| xiaomi/mimo-v2.6-flash / on / xiaomi/fp8 | 42.33/9.67 | -32.67 | 1/24 | 3941.27 | -21.89 | 1/24 |
| z-ai/glm-5.3-flash / on / z-ai/fp8 | 39.67/49.67 | 10.00 | 1/24 | 5607.91 | -19.00 | 1/24 |
| anthropic/claude-sonnet-5.5 / on / google-vertex/global | 40.67/50.33 | 9.67 | 1/24 | 5287.85 | 4.74 | 1/24 |
| qwen/qwen3.8-flash / off / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| qwen/qwen3.8-flash / on / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / off / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / on / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |

## Juízes

| Juiz | H baseline/skill | Diferença em pontos | Naturalidade bruta baseline/skill | Julgamentos válidos |
|---|---|---:|---|---:|
| jev | 37.36/30.91 | -6.45 | 85.07/68.86 | 11/456 |
| astra | 37.45/42.18 | 4.73 | 87.36/77.09 | 11/456 |
| opus | 45.27/42.45 | -2.82 | 75.27/62.27 | 11/456 |

## Cobertura e decomposição

- geracoes_submetidas: 31/912 (3.40%).
- respostas_api_validadas: 30/912 (3.29%).
- textos_redigidos: 28/912 (3.07%).
- respostas_somente_comandos: 2/912 (0.22%).
- pedidos_com_resposta_api_validada: 1/24 (4.17%).
- pedidos_com_julgamento: 1/24 (4.17%).
- pares_geracao_validos: 15/456 (3.29%).
- chamadas_juizes_submetidas: 12/432 (2.78%).
- chamadas_juizes_validas: 12/432 (2.78%).
- julgamentos_pares: 33/1368 (2.41%).
- escores_individuais: 66/2736 (2.41%).
- pares_com_algum_juiz: 11/456 (2.41%).
- pares_tres_juizes: 11/456 (2.41%).
- configuracoes_com_tres_juizes: 11/19 (57.89%).
- pares_tokens: 15/456 (3.29%).
- pares_tempo: 15/456 (3.29%).
- Tokens de entrada, somas baseline/skill: 3200.00/283932.00; médias 213.33/18928.80; variação 8772.88%.
- Tokens de saída, somas baseline/skill: 5822.00/7645.00; médias 388.13/509.67; variação 31.31%.

## Erros e limites

Registros com erro ou alerta: 1. Grupos bloqueados por candidatos ausentes ou inválidos: 140. Detalhes e denominadores completos em OBJETIVO.json.

- H = 100 menos detecção. Índice descritivo não calibrado, não probabilidade de autoria humana.
- Completed valida a resposta API, não a entrega editorial. Saídas compostas somente por tool_call são comandos, não textos redigidos; ficam nas métricas principais sem execução e sem exclusão silenciosa.
- Humanização percebida não comprova autoria nem qualidade. Naturalidade é a dimensão bruta 0 a 100.
- Principal: mesmo par avaliado pelos três juízes, média dos juízes e casos em cada configuração; média com peso igual entre configurações observadas.
- Configurações e casos ausentes não valem zero; cobertura parcial não permite concluir sobre toda a matriz.
- Pool: peso igual por caso, configuração e juiz observado. Juízes repetidos sobre os mesmos textos não são observações independentes.
- Tokens = prompt_tokens + completion_tokens. Reasoning não é somado, nem subtraído; cache permanece no contador nativo de entrada.
- Tokens e tempo usam pares completos equivalentes por caso e configuração, não exigem julgamento. Percentual principal é a razão das somas menos 1, vezes 100.
- Razão das médias equivale à razão das somas no mesmo conjunto. Média dos percentuais pareados é auxiliar e usa somente baseline positivo.
- Tempo API é elapsed_seconds das gerações, inclui eventual fila da requisição, exclui juízes, retries e pausas entre requisições. Não é tempo humano de redação.
- Consultas locais compartilhadas na preparação não foram cronometradas pelo runner original; indisponibilidade não equivale a zero. Medição posterior não substitui a original.
- Sem inferência estatística, causalidade geral ou calibração humana; uma geração por braço e configuração. Avaliação humana não medida.

Textos e respostas brutas permanecem intactos na fonte. Nenhuma normalização, nova consulta de modelo ou publicação.
