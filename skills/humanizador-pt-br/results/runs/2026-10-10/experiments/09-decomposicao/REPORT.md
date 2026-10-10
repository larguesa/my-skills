# Biologia e meio ambiente: decomposição

Execução: **LIVE_API**.

Impressão de IA é julgamento não calibrado, não prova de autoria. Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos não são três experimentos independentes. Avaliação humana pendente.

## Prompt literal

```text
Escreva uma explicação para leigos sobre o que acontece com os restos de plantas em uma horta e qual é o papel dos fungos e das bactérias na decomposição. Relacione o processo ao retorno de nutrientes ao solo e ao destino do carbono. Use um exemplo cotidiano para ajudar na compreensão.
```

## Comparação completa

| Modelo / modo | Baseline | Skill 0.5.1 | Jev | Astra | Opus |
|---|---|---|---|---|---|
| anthropic/claude-opus-5.5 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-astra / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| x-ai/grok-4.7 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| google/gemini-3.8-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| meta/muse-spark-1.3 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-pro / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-pro / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| z-ai/glm-5.3-prime / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-max-prime / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-luna / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| openai/gpt-6-luna / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| xiaomi/mimo-v2.6-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| z-ai/glm-5.3-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| anthropic/claude-sonnet-5.5 / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| qwen/qwen3.8-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| deepseek/deepseek-v4.1-flash / off | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |
| deepseek/deepseek-v4.1-flash / on | PENDENTE | PENDENTE | PENDENTE | PENDENTE | PENDENTE |

## Protocolo e limitações

Chamadas novas e independentes. Baseline recebe só o prompt literal; tratamento recebe SKILL.md 0.5.1, JSONs completos de catálogo/estilos e consultas/plano locais congelados. Nenhum texto de outro braço, preferência pessoal ou feedback de juiz entra nos candidatos.
Mapeamento anônimo e grupos de até quatro pares são congelados; grupo com candidato inválido fica sem julgamento, sem reagrupamento oportunista.
Modelos, modos e providers efetivos são os congelados, incluindo amendments explícitos. Aliases na resposta não comprovam a versão efetiva nem o uso do reasoning solicitado.
Juízes chat: máximo 16384 tokens histórico. Jev Decisions: payload nativo histórico sem max_tokens artificial. Agregado de qualidade: média das quatro dimensões; erro crítico limita correção a 25 e total a 49, preservando notas brutas.

[Resumo agregado](../../SUMMARY.md)
