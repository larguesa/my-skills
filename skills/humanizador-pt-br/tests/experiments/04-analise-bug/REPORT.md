# Análise de um argumento padrão mutável

**Revisão humana: pendente.** Juízes dão opiniões; não há alegação de superioridade.

**Prompt exato congelado**

````text
Escreva em português brasileiro. Este é um exercício com dados e personagens fictícios, não um relato real. Use somente a base fornecida, sem inventar fontes, medições ou promessas. Entregue somente o texto no formato solicitado, sem análise sobre o processo de escrita. Não use travessão longo.

Escreva uma análise de bug de 220 a 320 palavras. Use as seções Reprodução, Causa, Correção e Limitações, nessa ordem. Código observado:
```python
def collect(item, bucket=[]):
    bucket.append(item)
    return bucket
```
Em um processo novo, collect("A") retorna ["A"] e a segunda chamada collect("B") retorna ["A", "B"]. Explique o compartilhamento do objeto padrão entre chamadas. Apresente código corrigido usando bucket=None e uma nova lista somente quando bucket is None. Se o chamador fornecer uma lista, preserve o contrato de acrescentar àquela própria lista e retorná-la. Inclua assert para duas chamadas independentes e assert para a identidade da lista fornecida. Não alegue segurança para uso concorrente.
````

## Critérios fornecidos (não são respostas de candidatos)

- Seções e código Python sintaticamente válidos; 220 a 320 palavras.
- Explicar argumento padrão criado uma vez, sem mudar comportamento da lista explícita.
- Correção com is None; duas chamadas independentes e identidade da lista fornecida testadas.
- Não usar bucket or \[\] nem prometer segurança concorrente.

## Ampliação 20261002: resultados observados

Somente esta rodada: 0/38 candidatos válidos; 0/19 pares completos; 0 falhas/saídas inválidas; 38 posições não iniciadas.

Médias com peso igual por par/configuração e denominadores próprios por campo. Não se combinam escalas de juízes nem dados antigos.

Preferências são opiniões, não sucesso factual. Impressão de IA não é probabilidade de autoria. Revisão humana: pendente. Não há alegação de superioridade.

| Juiz | Prefere com skill | Prefere original | Empate | Ausentes / previstos |
|---|---|---|---|---:|
| Jev | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | 19/19 |
| Astra | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | 19/19 |
| Opus 5.5 | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ 0/0 (sem observações) | 19/19 |

| Juiz / dimensão (0–100) | Original: média; n; ausentes | Skill: média; n; ausentes |
|---|---:|---:|
| Jev / naturalidade | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / clareza | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / adequacao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / correcao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / correcao_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / total | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / total_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Jev / deteccao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / naturalidade | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / clareza | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / adequacao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / correcao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / correcao_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / total | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / total_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Astra / deteccao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / naturalidade | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / clareza | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / adequacao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / correcao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / correcao_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / total | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / total_raw | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |
| Opus 5.5 / deteccao | indisponível; n=0; ausentes=19 | indisponível; n=0; ausentes=19 |

Jev: dimensões por Score nativo, índice probabilístico contínuo 0–4 × 25 (não confiança ou noul); cinco âncoras ordenadas. Impressão de IA: noul × 100. Justificativa textual indisponível na API nativa. Correção crítica limitada a 25 e total a 49; notas brutas preservadas.


| Verificação mecânica | Original | Com skill |
|---|---|---|

| Observação de apoio literal / cálculo (não é verdade semântica) | Original | Com skill |
|---|---|---|

Verificações aprovadas só demonstram a observação nomeada; fidelidade factual e semântica continuam pendentes.

### Contabilidade da ampliação (medições, sem teto monetário)

| Grupo | Chamadas observadas | Custo conhecido USD | Custos desconhecidos | Tempos conhecidos / chamadas |
|---|---:|---:|---:|---:|
| generation | 0 | 0 | 0 | 0.00 s; 0/0 |
| jev | 0 | 0 | 0 | 0.00 s; 0/0 |
| astra | 0 | 0 | 0 | 0.00 s; 0/0 |
| opus | 0 | 0 | 0 | 0.00 s; 0/0 |
| probes\_extra | 0 | 0 | 0 | 0.00 s; 0/0 |

Custos de geração, Jev, Astra, Opus e sondagens/extras separados. Custo conhecido é parcial quando há chamadas de custo desconhecido; chamadas não iniciadas não são custo zero.

## Tabela completa das 19 configurações

| Modelo/configuração | Resposta original | Resposta com skill | Jev | Astra | Opus 5.5 | Custo original USD | Custo skill USD | Tempo original s | Tempo skill s | Verificações original | Verificações skill |
|---|---|---|---|---|---|---:|---:|---:|---:|---|---|
| Configuração: anthropic/claude-opus-5.5 (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: openai/gpt-6-astra (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: x-ai/grok-4.7 (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: google/gemini-3.8-flash (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: meta/muse-spark-1.3 (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: xiaomi/mimo-v2.6-pro (off) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: xiaomi/mimo-v2.6-pro (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: z-ai/glm-5.3-prime (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: qwen/qwen3.8-max-prime (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: openai/gpt-6-luna (off) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: openai/gpt-6-luna (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: xiaomi/mimo-v2.6-flash (off) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: xiaomi/mimo-v2.6-flash (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: z-ai/glm-5.3-flash (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: anthropic/claude-sonnet-5.5 (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: qwen/qwen3.8-flash (off) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: qwen/qwen3.8-flash (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: deepseek/deepseek-v4.1-flash (off) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |
| Configuração: deepseek/deepseek-v4.1-flash (on) | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: chamada não iniciada | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | ⏸️ pendente: sem julgamento válido | não iniciado | não iniciado | não iniciado | não iniciado | pendente: sem saída válida | pendente: sem saída válida |

## Evidências brutas

[evidência](../../results/expansao-20261002/frozen/config.json)
