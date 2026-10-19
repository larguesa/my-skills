# Resultado objetivo

Execução: **LIVE_API**.

1. **Humanização percebida:** índice H médio baseline 26.74/100 e skill 40.27/100; diferença 13.53 pontos; variação relativa 50.59%. Não calibrado, não probabilidade de autoria. 22 pares com três juízes em 1 configurações observadas.
2. **Tokens:** variação 412.64% pela razão das somas. Baseline/skill 66753.00/342201.00 tokens; médias 1362.31/6983.69 por geração; n=49 pares completos. Entrada mais saída, sem somar reasoning.
3. **Tempo de redação via API:** variação 17.43%; somas baseline/skill 815.63/957.77 s; médias 16.65/19.55 s; n=49 pares completos. Sem juízes, retries ou pausas.

Consultas locais da skill: 0/24 casos relevantes medidos; 0.00 s conhecidos. Tempo incluindo preparo local compartilhado: indisponível, não tratado como zero.

Naturalidade bruta média baseline/skill: 83.36/86.67, escala 0 a 100. Pool descritivo de julgamentos: H 26.74/40.27; n=66.

## Modelos

| Modelo | Configurações | H baseline/skill | Diferença H em pontos | Tokens % | Tempo API % | Pares tokens/tempo |
|---|---:|---|---:|---:|---:|---|
| anthropic/claude-opus-5.5 | 1 | 26.74/40.27 | 13.53 | 335.71 | 3.15 | 22/22 |
| anthropic/claude-sonnet-5.5 | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| deepseek/deepseek-v4.1-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| google/gemini-3.8-flash | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| meta/muse-spark-1.3 | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| openai/gpt-6-astra | 1 | indisponível/indisponível | indisponível | 689.41 | 3.79 | 24/24 |
| openai/gpt-6-luna | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-max-prime | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| x-ai/grok-4.7 | 1 | indisponível/indisponível | indisponível | 339.79 | 256.68 | 3/3 |
| xiaomi/mimo-v2.6-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| xiaomi/mimo-v2.6-pro | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| z-ai/glm-5.3-flash | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| z-ai/glm-5.3-prime | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |

## Configurações

| Modelo / modo / provedor | H baseline/skill | Diferença em pontos | Pares 3 juízes | Tokens % | Tempo % | Pares válidos |
|---|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 / on / amazon-bedrock | 26.74/40.27 | 13.53 | 22/24 | 335.71 | 3.15 | 22/24 |
| openai/gpt-6-astra / on / openai | indisponível/indisponível | indisponível | 0/24 | 689.41 | 3.79 | 24/24 |
| x-ai/grok-4.7 / on / xai/zdr | indisponível/indisponível | indisponível | 0/24 | 339.79 | 256.68 | 3/24 |
| google/gemini-3.8-flash / on / google-ai-studio | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| meta/muse-spark-1.3 / on / meta | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| xiaomi/mimo-v2.6-pro / off / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| xiaomi/mimo-v2.6-pro / on / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| z-ai/glm-5.3-prime / on / alibaba | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| qwen/qwen3.8-max-prime / on / alibaba | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| openai/gpt-6-luna / off / openai | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| openai/gpt-6-luna / on / openai | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| xiaomi/mimo-v2.6-flash / off / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| xiaomi/mimo-v2.6-flash / on / xiaomi/fp8 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| z-ai/glm-5.3-flash / on / z-ai/fp8 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| anthropic/claude-sonnet-5.5 / on / google-vertex/global | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| qwen/qwen3.8-flash / off / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| qwen/qwen3.8-flash / on / alibaba/us-east-1 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / off / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| deepseek/deepseek-v4.1-flash / on / sail-research/fp4 | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |

## Juízes

| Juiz | H baseline/skill | Diferença em pontos | Naturalidade bruta baseline/skill | Julgamentos válidos |
|---|---|---:|---|---:|
| jev | 32.77/40.91 | 8.14 | 91.22/87.16 | 22/456 |
| astra | 15.82/32.91 | 17.09 | 84.82/92.14 | 22/456 |
| opus | 31.64/47.00 | 15.36 | 74.05/80.73 | 22/456 |

## Cobertura e decomposição

- geracoes_submetidas: 117/912 (12.83%).
- respostas_api_validadas: 107/912 (11.73%).
- textos_redigidos: 107/912 (11.73%).
- respostas_somente_comandos: 0/912 (0.00%).
- pedidos_com_resposta_api_validada: 24/24 (100.00%).
- pedidos_com_julgamento: 22/24 (91.67%).
- pares_geracao_validos: 49/456 (10.75%).
- chamadas_juizes_submetidas: 66/432 (15.28%).
- chamadas_juizes_validas: 66/432 (15.28%).
- julgamentos_pares: 66/1368 (4.82%).
- escores_individuais: 132/2736 (4.82%).
- pares_com_algum_juiz: 22/456 (4.82%).
- pares_tres_juizes: 22/456 (4.82%).
- configuracoes_com_tres_juizes: 1/19 (5.26%).
- pares_tokens: 49/456 (10.75%).
- pares_tempo: 49/456 (10.75%).
- Tokens de entrada, somas baseline/skill: 10574.00/277614.00; médias 215.80/5665.59; variação 2525.44%.
- Tokens de saida, somas baseline/skill: 56179.00/64587.00; médias 1146.51/1318.10; variação 14.97%.

## Erros e limites

Registros com erro ou alerta: 10. Grupos bloqueados por candidatos ausentes ou inválidos: 122. Detalhes e denominadores completos em OBJETIVO.json.

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
