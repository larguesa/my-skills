# Resultado objetivo

Execução: **LIVE_API**.

1. **Humanização percebida:** índice H médio baseline 42.04/100 e skill 49.19/100; diferença 7.15 pontos; variação relativa 17.00%. Não calibrado, não probabilidade de autoria. 9 pares com três juízes em 9 configurações observadas.
2. **Tokens:** variação 895.18% pela razão das somas. Baseline/skill 9425.00/93796.00 tokens; médias 628.33/6253.07 por geração; n=15 pares completos. Entrada mais saída, sem somar reasoning.
3. **Tempo de redação via API:** variação 6.68%; somas baseline/skill 103.63/110.56 s; médias 6.91/7.37 s; n=15 pares completos. Sem juízes, retries ou pausas.

Consultas locais da skill: 0/1 casos relevantes medidos; 0.00 s conhecidos. Tempo incluindo preparo local compartilhado: indisponível, não tratado como zero.

Naturalidade bruta média baseline/skill: 83.60/81.42, escala 0 a 100. Pool descritivo de julgamentos: H 42.04/49.19; n=27.

## Modelos

| Modelo | Configurações | H baseline/skill | Diferença H em pontos | Tokens % | Tempo API % | Pares tokens/tempo |
|---|---:|---|---:|---:|---:|---|
| anthropic/claude-opus-5.5 | 1 | 31.00/44.00 | 13.00 | 865.52 | -20.94 | 1/1 |
| anthropic/claude-sonnet-5.5 | 1 | 36.67/46.00 | 9.33 | 1188.57 | -35.10 | 1/1 |
| deepseek/deepseek-v4.1-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| google/gemini-3.8-flash | 1 | indisponível/indisponível | indisponível | 451.68 | -37.01 | 1/1 |
| meta/muse-spark-1.3 | 1 | indisponível/indisponível | indisponível | 463.36 | 15.42 | 1/1 |
| openai/gpt-6-astra | 1 | 46.33/47.00 | 0.67 | 2218.43 | 28.38 | 1/1 |
| openai/gpt-6-luna | 2 | 54.67/50.33 | -4.33 | 2090.60 | 25.31 | 2/2 |
| qwen/qwen3.8-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-max-prime | 1 | 24.67/52.67 | 28.00 | 988.91 | 100.64 | 1/1 |
| x-ai/grok-4.7 | 1 | 51.00/54.33 | 3.33 | 313.20 | 58.82 | 1/1 |
| xiaomi/mimo-v2.6-flash | 2 | 45.33/46.00 | 0.67 | 1125.37 | 42.08 | 2/2 |
| xiaomi/mimo-v2.6-pro | 2 | indisponível/indisponível | indisponível | 947.22 | -35.69 | 2/2 |
| z-ai/glm-5.3-flash | 1 | 34.00/52.00 | 18.00 | 1702.55 | -24.47 | 1/1 |
| z-ai/glm-5.3-prime | 1 | indisponível/indisponível | indisponível | 1753.59 | -18.86 | 1/1 |

## Configurações

| Modelo / modo / provedor | H baseline/skill | Diferença em pontos | Pares 3 juízes | Tokens % | Tempo % | Pares válidos |
|---|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 / on / amazon-bedrock | 31.00/44.00 | 13.00 | 1/24 | 865.52 | -20.94 | 1/24 |
| openai/gpt-6-astra / on / openai | 46.33/47.00 | 0.67 | 1/24 | 2218.43 | 28.38 | 1/24 |
| x-ai/grok-4.7 / on / xai/zdr | 51.00/54.33 | 3.33 | 1/24 | 313.20 | 58.82 | 1/24 |
| google/gemini-3.8-flash / on / google-ai-studio | indisponível/indisponível | indisponível | 0/24 | 451.68 | -37.01 | 1/24 |
| meta/muse-spark-1.3 / on / meta | indisponível/indisponível | indisponível | 0/24 | 463.36 | 15.42 | 1/24 |
| xiaomi/mimo-v2.6-pro / off / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | 1082.24 | -67.42 | 1/24 |
| xiaomi/mimo-v2.6-pro / on / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | 845.96 | -11.28 | 1/24 |
| z-ai/glm-5.3-prime / on / alibaba | indisponível/indisponível | indisponível | 0/24 | 1753.59 | -18.86 | 1/24 |
| qwen/qwen3.8-max-prime / on / alibaba | 24.67/52.67 | 28.00 | 1/24 | 988.91 | 100.64 | 1/24 |
| openai/gpt-6-luna / off / openai | 52.00/48.00 | -4.00 | 1/24 | 2274.41 | 40.20 | 1/24 |
| openai/gpt-6-luna / on / openai | 57.33/52.67 | -4.67 | 1/24 | 1939.69 | 17.52 | 1/24 |
| xiaomi/mimo-v2.6-flash / off / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | 800.91 | -36.89 | 1/24 |
| xiaomi/mimo-v2.6-flash / on / xiaomi/fp8 | 45.33/46.00 | 0.67 | 1/24 | 1717.50 | 232.16 | 1/24 |
| z-ai/glm-5.3-flash / on / z-ai/fp8 | 34.00/52.00 | 18.00 | 1/24 | 1702.55 | -24.47 | 1/24 |
| anthropic/claude-sonnet-5.5 / on / google-vertex/global | 36.67/46.00 | 9.33 | 1/24 | 1188.57 | -35.10 | 1/24 |
| qwen/qwen3.8-flash / off / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| qwen/qwen3.8-flash / on / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / off / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / on / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |

## Juízes

| Juiz | H baseline/skill | Diferença em pontos | Naturalidade bruta baseline/skill | Julgamentos válidos |
|---|---|---:|---|---:|
| jev | 37.00/33.67 | -3.33 | 86.92/81.25 | 9/456 |
| astra | 40.78/58.33 | 17.56 | 88.78/95.00 | 9/456 |
| opus | 48.33/55.56 | 7.22 | 75.11/68.00 | 9/456 |

## Cobertura e decomposição

- geracoes_submetidas: 32/912 (3.51%).
- respostas_api_validadas: 31/912 (3.40%).
- textos_redigidos: 31/912 (3.40%).
- respostas_somente_comandos: 0/912 (0.00%).
- pedidos_com_resposta_api_validada: 1/24 (4.17%).
- pedidos_com_julgamento: 1/24 (4.17%).
- pares_geracao_validos: 15/456 (3.29%).
- chamadas_juizes_submetidas: 9/432 (2.08%).
- chamadas_juizes_validas: 9/432 (2.08%).
- julgamentos_pares: 27/1368 (1.97%).
- escores_individuais: 54/2736 (1.97%).
- pares_com_algum_juiz: 9/456 (1.97%).
- pares_tres_juizes: 9/456 (1.97%).
- configuracoes_com_tres_juizes: 9/19 (47.37%).
- pares_tokens: 15/456 (3.29%).
- pares_tempo: 15/456 (3.29%).
- Tokens de entrada, somas baseline/skill: 3201.00/87008.00; médias 213.40/5800.53; variação 2618.15%.
- Tokens de saida, somas baseline/skill: 6224.00/6788.00; médias 414.93/452.53; variação 9.06%.

## Erros e limites

Registros com erro ou alerta: 1. Grupos bloqueados por candidatos ausentes ou inválidos: 141. Detalhes e denominadores completos em OBJETIVO.json.

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
