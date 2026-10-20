# Resultado objetivo

Execução: **LIVE_API**.

1. **Humanização percebida:** índice H médio baseline 31.67/100 e skill 47.33/100; diferença 15.67 pontos; variação relativa 49.47%. Não calibrado, não probabilidade de autoria. 2 pares com três juízes em 1 configurações observadas.
2. **Tokens:** variação 481.23% pela razão das somas. Baseline/skill 3532.00/20529.00 tokens; médias 1766.00/10264.50 por geração; n=2 pares completos. Entrada mais saída, sem somar reasoning.
3. **Tempo de redação via API:** variação 13.62%; somas baseline/skill 33.33/37.87 s; médias 16.66/18.93 s; n=2 pares completos. Sem juízes, retries ou pausas.

Consultas locais da skill: 0/2 casos relevantes medidos; 0.00 s conhecidos. Tempo incluindo preparo local compartilhado: indisponível, não tratado como zero.

Naturalidade bruta média baseline/skill: 82.88/86.25, escala 0 a 100. Pool descritivo de julgamentos: H 31.67/47.33; n=6.

## Modelos

| Modelo | Configurações | H baseline/skill | Diferença H em pontos | Tokens % | Tempo API % | Pares tokens/tempo |
|---|---:|---|---:|---:|---:|---|
| anthropic/claude-opus-5.5 | 1 | 31.67/47.33 | 15.67 | 481.23 | 13.62 | 2/2 |
| anthropic/claude-sonnet-5.5 | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| deepseek/deepseek-v4.1-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| google/gemini-3.8-flash | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| meta/muse-spark-1.3 | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| openai/gpt-6-astra | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| openai/gpt-6-luna | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| qwen/qwen3.8-max-prime | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| x-ai/grok-4.7 | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| xiaomi/mimo-v2.6-flash | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| xiaomi/mimo-v2.6-pro | 2 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| z-ai/glm-5.3-flash | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |
| z-ai/glm-5.3-prime | 1 | indisponível/indisponível | indisponível | indisponível | indisponível | 0/0 |

## Configurações

| Modelo / modo / provedor | H baseline/skill | Diferença em pontos | Pares 3 juízes | Tokens % | Tempo % | Pares válidos |
|---|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 / on / amazon-bedrock | 31.67/47.33 | 15.67 | 2/24 | 481.23 | 13.62 | 2/24 |
| openai/gpt-6-astra / on / openai | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
| x-ai/grok-4.7 / on / xai/zdr | indisponível/indisponível | indisponível | 0/24 | indisponível | indisponível | 0/24 |
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
| jev | 36.50/42.00 | 5.50 | 91.12/85.75 | 2/456 |
| astra | 21.00/45.00 | 24.00 | 81.50/92.00 | 2/456 |
| opus | 37.50/55.00 | 17.50 | 76.00/81.00 | 2/456 |

## Cobertura e decomposição

- geracoes_submetidas: 6/912 (0.66%).
- respostas_api_validadas: 5/912 (0.55%).
- textos_redigidos: 5/912 (0.55%).
- respostas_somente_comandos: 0/912 (0.00%).
- pedidos_com_resposta_api_validada: 3/24 (12.50%).
- pedidos_com_julgamento: 2/24 (8.33%).
- pares_geracao_validos: 2/456 (0.44%).
- chamadas_juizes_submetidas: 6/432 (1.39%).
- chamadas_juizes_validas: 6/432 (1.39%).
- julgamentos_pares: 6/1368 (0.44%).
- escores_individuais: 12/2736 (0.44%).
- pares_com_algum_juiz: 2/456 (0.44%).
- pares_tres_juizes: 2/456 (0.44%).
- configuracoes_com_tres_juizes: 1/19 (5.26%).
- pares_tokens: 2/456 (0.44%).
- pares_tempo: 2/456 (0.44%).
- Tokens de entrada, somas baseline/skill: 444.00/17053.00; médias 222.00/8526.50; variação 3740.77%.
- Tokens de saida, somas baseline/skill: 3088.00/3476.00; médias 1544.00/1738.00; variação 12.56%.

## Erros e limites

Registros com erro ou alerta: 1. Grupos bloqueados por candidatos ausentes ou inválidos: 142. Detalhes e denominadores completos em OBJETIVO.json.

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
