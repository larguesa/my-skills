# Documentação de uma API de tarefas

⏸️ Caso preparado; nenhuma geração nem julgamento foi executado.

## Prompt previsto para as duas condições

Este é o pedido a usar sem e com skill, em chamadas independentes. Não foi utilizado para gerar um texto ainda.

```
Escreva em português brasileiro. Este é um exercício com dados e personagens fictícios, não um relato real. Use somente a base fornecida, sem inventar fontes, medições ou promessas. Entregue somente o texto no formato solicitado, sem análise sobre o processo de escrita. Não use travessão longo.

Escreva documentação técnica de 250 a 400 palavras para a API fictícia de tarefas. Seções obrigatórias nesta ordem: Autenticação, Criar tarefa, Erros, Limitações. Contrato: POST /v1/jobs; Authorization: Bearer <TOKEN>; Content-Type: application/json. Corpo {"name":"backup"}; name é obrigatório, string não vazia de até 80 caracteres. Sucesso HTTP 201 com {"id":"job_123","status":"queued"}; queued não significa execução concluída. O cabeçalho Idempotency-Key é opcional; a mesma chave e o mesmo corpo retornam a tarefa existente por 24 horas; a mesma chave com corpo diferente retorna 409. HTTP 400 para name inválido; 401 para token ausente ou inválido; 429 para limite de 60 requisições por minuto por token, com Retry-After em segundos. Inclua um exemplo curl com URL https://api.example.com/v1/jobs e um exemplo JSON de sucesso. Não invente endpoints de consulta, SDKs ou garantia de entrega.
```

## Resumo dos resultados

| Etapa | Estado |
|---|---|
| Geração sem e com skill | ⏸️ 0/38 textos |
| Trio de juízes | ⏸️ não executado |
| Avaliação humana | ⏸️ pendente |

## Critérios previstos

Naturalidade, clareza, adequação ao gênero e correção serão avaliadas separadamente. Impressão de IA e preferência não substituirão a verificação de fidelidade. Os critérios e o controle de execução serão congelados antes da primeira chamada paga.

- Quatro seções na ordem; 250 a 400 palavras, incluindo blocos de código.
- Preservar endpoint, nomes de campos, cabeçalhos, status HTTP e limites.
- JSON válido e curl coerente com o contrato; apenas token fictício &lt;TOKEN&gt;.
- Não apresentar queued como sucesso da execução nem inventar endpoints.

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
