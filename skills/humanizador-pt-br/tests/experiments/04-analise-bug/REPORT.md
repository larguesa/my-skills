# Análise de um argumento padrão mutável

⏸️ Caso preparado; nenhuma geração nem julgamento foi executado.

## Prompt previsto para as duas condições

Este é o pedido a usar sem e com skill, em chamadas independentes. Não foi utilizado para gerar um texto ainda.

````
Escreva em português brasileiro. Este é um exercício com dados e personagens fictícios, não um relato real. Use somente a base fornecida, sem inventar fontes, medições ou promessas. Entregue somente o texto no formato solicitado, sem análise sobre o processo de escrita. Não use travessão longo.

Escreva uma análise de bug de 220 a 320 palavras. Use as seções Reprodução, Causa, Correção e Limitações, nessa ordem. Código observado:
```python
def collect(item, bucket=[]):
    bucket.append(item)
    return bucket
```
Em um processo novo, collect("A") retorna ["A"] e a segunda chamada collect("B") retorna ["A", "B"]. Explique o compartilhamento do objeto padrão entre chamadas. Apresente código corrigido usando bucket=None e uma nova lista somente quando bucket is None. Se o chamador fornecer uma lista, preserve o contrato de acrescentar àquela própria lista e retorná-la. Inclua assert para duas chamadas independentes e assert para a identidade da lista fornecida. Não alegue segurança para uso concorrente.
````

## Resumo dos resultados

| Etapa | Estado |
|---|---|
| Geração sem e com skill | ⏸️ 0/38 textos |
| Trio de juízes | ⏸️ não executado |
| Avaliação humana | ⏸️ pendente |

## Critérios previstos

Naturalidade, clareza, adequação ao gênero e correção serão avaliadas separadamente. Impressão de IA e preferência não substituirão a verificação de fidelidade. Os critérios e o controle de execução serão congelados antes da primeira chamada paga.

- Seções e código Python sintaticamente válidos; 220 a 320 palavras.
- Explicar argumento padrão criado uma vez, sem mudar comportamento da lista explícita.
- Correção com is None; duas chamadas independentes e identidade da lista fornecida testadas.
- Não usar bucket or [] nem prometer segurança concorrente.

## Tabela completa da matriz prevista

Todas as posições abaixo estão pendentes. Não são falhas observadas nem resultados simulados.

| Modelo/configuração histórica | Original | Com skill | Jev | Astra | Opus 5.5 |
|---|---|---|---|---|---|
| anthropic/claude-opus-5.5 (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| anthropic/claude-sonnet-5.5 (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| deepseek/deepseek-v4.1-flash (raciocínio desligado solicitado) | pendente | pendente | pendente | pendente | pendente |
| deepseek/deepseek-v4.1-flash (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| google/gemini-3.8-flash (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| meta/muse-spark-1.3 (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| openai/gpt-6-astra (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| openai/gpt-6-luna (raciocínio desligado solicitado) | pendente | pendente | pendente | pendente | pendente |
| openai/gpt-6-luna (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| qwen/qwen3.8-flash (raciocínio desligado solicitado) | pendente | pendente | pendente | pendente | pendente |
| qwen/qwen3.8-flash (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| qwen/qwen3.8-max-prime (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| x-ai/grok-4.7 (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| xiaomi/mimo-v2.6-flash (raciocínio desligado solicitado) | pendente | pendente | pendente | pendente | pendente |
| xiaomi/mimo-v2.6-flash (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| xiaomi/mimo-v2.6-pro (raciocínio desligado solicitado) | pendente | pendente | pendente | pendente | pendente |
| xiaomi/mimo-v2.6-pro (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| z-ai/glm-5.3-flash (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |
| z-ai/glm-5.3-prime (raciocínio ligado) | pendente | pendente | pendente | pendente | pendente |

As 19 configurações históricas são uma referência, não uma confirmação atual de disponibilidade. Rotas efetivas e aceitação dos modos de raciocínio devem ser verificadas antes da execução. Nenhum modelo será substituído silenciosamente.

[Planejamento e critérios comuns](../PLAN.md) · [Voltar ao índice](../../README.md)
