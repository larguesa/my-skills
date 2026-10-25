# Humanizador 0.9.1 versus 0.8.1



**Amostra interrompida.** H de 53,25 na 0.8.1 para 58,57 na 0.9.1; ΔH = +5,32 pontos nos 68 pares com os três juízes.

Cobertura: **68/95 pares completos**, **204/285 julgamentos válidos**.

Comparação descritiva de redação. A candidata não é promovida a release. Qualidade e fidelidade são avaliadas separadamente de H.

## Alterações e protocolo

As alterações efetivamente implementadas constam em [IMPLEMENTACAO.md](report/IMPLEMENTACAO.md). As emendas anteriores ao freeze constam em [PROTOCOL.md](report/PROTOCOL.md).

## Desenho e denominadores

Sorteio único de 5 dos 24 pedidos: 01, 06, 12, 14 e 16, equivalente a 20,83% após arredondamento. São 19 configurações de 14 modelos, 95 pares, 190 gerações e até 285 chamadas de julgamento. Cada chamada de juiz desta matriz julga um par e produz duas notas de impressão de IA: até 570 notas individuais.

Ambos os braços recebem sua própria skill, briefing e pedido literal em chamadas independentes. A comparação é 0.9.1 versus 0.8.1, não reescrita de uma resposta anterior.

H = 100 menos impressão de IA, de 0 a 100. H é percepção, não probabilidade calibrada de autoria. A média principal inclui somente pares com os três juízes válidos, com peso igual por par/configuração e por juiz. Configurações, não modelos distintos, são a unidade de ponderação. Por juiz, entram seus próprios pares válidos; esses denominadores podem diferir. Ausências não se tornam zeros nem votos.

Astra e Opus usam rationale v2, com características não-humanizadas e qualidade/fidelidade por texto. Jev mantém Decisions nativo, sem explicação textual. Preferência mede qualidade e atendimento ao pedido, não H.

## Resultado por juiz

| Juiz | Pares / 95 | H 0.8.1 | H 0.9.1 | ΔH | Votos 0.8.1 / 0.9.1 / empate |
|---|---:|---:|---:|---:|---|
| jev | 68/95 | 32,93 | 36,09 | +3,16 | 46 / 19 / 3 |
| astra | 68/95 | 80,81 | 87,53 | +6,72 | 22 / 37 / 9 |
| opus | 68/95 | 46,00 | 52,09 | +6,09 | 34 / 30 / 4 |

## Qualidade e fidelidade nos pares completos

| Medida | 0.8.1 | 0.9.1 | Denominador por versão |
|---|---:|---:|---:|
| Humanização percebida, média 0 a 100 | 53,25 | 58,57 | 204 avaliações |
| Naturalidade, média 0 a 100 | 81,61 | 84,32 | 204 avaliações |
| Clareza, média 0 a 100 | 87,04 | 87,77 | 204 avaliações |
| Adequação, média 0 a 100 | 84,22 | 85,92 | 204 avaliações |
| Correção/fidelidade, média 0 a 100 | 84,43 | 87,66 | 204 avaliações |
| Votos de preferência | 102 | 86 | 204 |
| Julgamentos com falha crítica | 22 | 11 | 204 |

Empates: 16/204. Três avaliações dos mesmos textos não são três experimentos independentes.

## Agregados por configuração

| Modelo / modo | Pares / 5 | H 0.8.1 | H 0.9.1 | ΔH | Avaliações / 15 |
|---|---:|---:|---:|---:|---:|
| anthropic/claude-opus-5.5 / on | 5/5 | 55,53 | 60,00 | +4,47 | 15/15 |
| openai/gpt-6-astra / on | 5/5 | 57,87 | 58,27 | +0,40 | 15/15 |
| x-ai/grok-4.7 / on | 1/5 | 61,67 | 68,00 | +6,33 | 3/15 |
| google/gemini-3.8-flash / on | 5/5 | 51,07 | 56,80 | +5,73 | 15/15 |
| meta/muse-spark-1.3 / on | 4/5 | 61,00 | 59,75 | -1,25 | 12/15 |
| xiaomi/mimo-v2.6-pro / off | 5/5 | 38,93 | 56,53 | +17,60 | 15/15 |
| xiaomi/mimo-v2.6-pro / on | 3/5 | 53,89 | 61,33 | +7,44 | 9/15 |
| z-ai/glm-5.3-prime / on | 5/5 | 55,00 | 62,47 | +7,47 | 15/15 |
| qwen/qwen3.8-max-prime / on | 5/5 | 42,47 | 57,07 | +14,60 | 15/15 |
| openai/gpt-6-luna / off | 5/5 | 62,20 | 62,53 | +0,33 | 15/15 |
| openai/gpt-6-luna / on | 5/5 | 62,27 | 65,40 | +3,13 | 15/15 |
| xiaomi/mimo-v2.6-flash / off | 5/5 | 50,47 | 47,13 | -3,33 | 15/15 |
| xiaomi/mimo-v2.6-flash / on | 5/5 | 46,07 | 55,80 | +9,73 | 15/15 |
| z-ai/glm-5.3-flash / on | 5/5 | 53,27 | 58,93 | +5,67 | 15/15 |
| anthropic/claude-sonnet-5.5 / on | 5/5 | 55,53 | 57,40 | +1,87 | 15/15 |
| qwen/qwen3.8-flash / off | 0/5 | não medido | não medido | não medido | 0/15 |
| qwen/qwen3.8-flash / on | 0/5 | não medido | não medido | não medido | 0/15 |
| deepseek/deepseek-v4.1-flash / off | 0/5 | não medido | não medido | não medido | 0/15 |
| deepseek/deepseek-v4.1-flash / on | 0/5 | não medido | não medido | não medido | 0/15 |

## Agregados por pedido

| Pedido | Pares / 19 | ΔH | Votos referência / candidata / empate | Textos completos |
|---|---:|---:|---|---|
| Jornalístico: notícia sobre bibliotecas | 15/19 | +6,47 | 15 / 25 / 5 | [Abrir](report/cases/01-noticia-bibliotecas.md) |
| Física: medidas de período | 13/19 | +8,72 | 20 / 15 / 4 | [Abrir](report/cases/06-experimento-periodo.md) |
| Acadêmico: discussão | 13/19 | +0,90 | 24 / 14 / 1 | [Abrir](report/cases/12-discussao-estudo.md) |
| Didático: probabilidade condicional | 13/19 | +5,79 | 20 / 14 / 5 | [Abrir](report/cases/14-probabilidade-condicional.md) |
| Negócios: comparação de infraestrutura | 14/19 | +4,62 | 23 / 18 / 1 | [Abrir](report/cases/16-nota-investimento.md) |

## Cobertura ausente e interrupção

Estado terminal do supervisor: `blocked`. Estado reconstituído do runner: `blocked`. Intent sem raw é submissão ambígua, não falha comprovada do provedor. O relatório não retoma nem repete chamadas.

| Pedido / configuração | Causa da ausência do trio completo |
|---|---|
| 01-noticia-bibliotecas/r15 | baseline: billing_uncertain; skill: pending; jev: pending; astra: pending; opus: pending |
| 01-noticia-bibliotecas/r16 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 01-noticia-bibliotecas/r17 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 01-noticia-bibliotecas/r18 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r02 | baseline: invalid_response; skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r06 | baseline: invalid_response; skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r15 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r16 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r17 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 06-experimento-periodo/r18 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r02 | baseline: invalid_response; skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r04 | baseline: invalid_response; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r15 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r16 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r17 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 12-discussao-estudo/r18 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r02 | baseline: invalid_response; skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r06 | skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r15 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r16 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r17 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 14-probabilidade-condicional/r18 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 16-nota-investimento/r02 | baseline: invalid_response; skill: invalid_response; jev: pending; astra: pending; opus: pending |
| 16-nota-investimento/r15 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 16-nota-investimento/r16 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 16-nota-investimento/r17 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |
| 16-nota-investimento/r18 | baseline: pending; skill: pending; jev: pending; astra: pending; opus: pending |

## Telemetria secundária

Custo nativo conhecido não inclui chamadas sem custo informado. Tempo observado é a soma das latências registradas por chamada, não o tempo de trabalho de implementação. A janela por modelo vai do primeiro início ao último término observado e pode incluir espera entre pedidos. Tokens de raciocínio não se somam novamente aos de saída.

| Fase / modelo / modo / braço | Chamadas válidas / submetidas | Custo nativo conhecido, USD | Com custo / submetidas | Tempo observado, s | Com tempo / submetidas | Janela observada, s |
|---|---:|---:|---:|---:|---:|---:|
| generation / anthropic/claude-opus-5.5 / on / baseline | 5/5 | 0.336632 | 5/5 | 85,37 | 5/5 | 306,45 |
| generation / anthropic/claude-opus-5.5 / on / skill | 5/5 | 0.317940 | 5/5 | 77,87 | 5/5 | 310,54 |
| generation / anthropic/claude-sonnet-5.5 / on / baseline | 5/5 | 0.136726 | 5/5 | 45,32 | 5/5 | 237,03 |
| generation / anthropic/claude-sonnet-5.5 / on / skill | 5/5 | 0.131620 | 5/5 | 41,09 | 5/5 | 240,04 |
| generation / google/gemini-3.8-flash / on / baseline | 5/5 | 0.04142400 | 5/5 | 53,82 | 5/5 | 233,32 |
| generation / google/gemini-3.8-flash / on / skill | 5/5 | 0.03894375 | 5/5 | 48,75 | 5/5 | 238,53 |
| generation / meta/muse-spark-1.3 / on / baseline | 4/5 | 0.08404400 | 5/5 | 72,16 | 5/5 | 223,32 |
| generation / meta/muse-spark-1.3 / on / skill | 5/5 | 0.08251650 | 5/5 | 71,10 | 5/5 | 235,24 |
| generation / openai/gpt-6-astra / on / baseline | 5/5 | 0.4015500 | 5/5 | 37,01 | 5/5 | 183,13 |
| generation / openai/gpt-6-astra / on / skill | 5/5 | 0.3979125 | 5/5 | 31,14 | 5/5 | 187,70 |
| generation / openai/gpt-6-luna / off / baseline | 5/5 | 0.003630500 | 5/5 | 13,03 | 5/5 | 154,21 |
| generation / openai/gpt-6-luna / off / skill | 5/5 | 0.003618125 | 5/5 | 13,48 | 5/5 | 154,52 |
| generation / openai/gpt-6-luna / on / baseline | 5/5 | 0.004277000 | 5/5 | 27,73 | 5/5 | 181,54 |
| generation / openai/gpt-6-luna / on / skill | 5/5 | 0.004312125 | 5/5 | 29,00 | 5/5 | 183,08 |
| generation / qwen/qwen3.8-flash / off / baseline | 0/1 | 0 | 0/1 | 7,19 | 1/1 | 7,19 |
| generation / qwen/qwen3.8-max-prime / on / baseline | 5/5 | 0.195488 | 5/5 | 113,05 | 5/5 | 356,67 |
| generation / qwen/qwen3.8-max-prime / on / skill | 5/5 | 0.161356 | 5/5 | 82,82 | 5/5 | 349,00 |
| generation / x-ai/grok-4.7 / on / baseline | 1/5 | 0.225810 | 5/5 | 435,67 | 5/5 | 785,29 |
| generation / x-ai/grok-4.7 / on / skill | 1/5 | 0.217374 | 5/5 | 388,20 | 5/5 | 803,96 |
| generation / xiaomi/mimo-v2.6-flash / off / baseline | 5/5 | 0.0042894488 | 5/5 | 83,29 | 5/5 | 285,73 |
| generation / xiaomi/mimo-v2.6-flash / off / skill | 5/5 | 0.0038722432 | 5/5 | 43,30 | 5/5 | 288,28 |
| generation / xiaomi/mimo-v2.6-flash / on / baseline | 5/5 | 0.0051380392 | 5/5 | 111,04 | 5/5 | 378,83 |
| generation / xiaomi/mimo-v2.6-flash / on / skill | 5/5 | 0.0046406192 | 5/5 | 101,73 | 5/5 | 374,66 |
| generation / xiaomi/mimo-v2.6-pro / off / baseline | 5/5 | 0.0124678554 | 5/5 | 98,87 | 5/5 | 337,23 |
| generation / xiaomi/mimo-v2.6-pro / off / skill | 5/5 | 0.0118592904 | 5/5 | 85,45 | 5/5 | 347,19 |
| generation / xiaomi/mimo-v2.6-pro / on / baseline | 4/5 | 0.0114263982 | 5/5 | 324,67 | 5/5 | 687,76 |
| generation / xiaomi/mimo-v2.6-pro / on / skill | 3/5 | 0.0113289840 | 5/5 | 307,68 | 5/5 | 705,19 |
| generation / z-ai/glm-5.3-flash / on / baseline | 5/5 | 0.00484207 | 5/5 | 58,42 | 5/5 | 260,66 |
| generation / z-ai/glm-5.3-flash / on / skill | 5/5 | 0.00478268 | 5/5 | 50,03 | 5/5 | 261,80 |
| generation / z-ai/glm-5.3-prime / on / baseline | 5/5 | 0.0859228 | 5/5 | 38,32 | 5/5 | 230,92 |
| generation / z-ai/glm-5.3-prime / on / skill | 5/5 | 0.0759864 | 5/5 | 28,44 | 5/5 | 233,35 |
| judge / anthropic/claude-opus-5.5 / on / opus | 68/68 | 3.083704 | 68/68 | 1164,02 | 68/68 | 5577,32 |
| judge / openai/gpt-6-astra / on / astra | 68/68 | 4.3888550 | 68/68 | 1166,30 | 68/68 | 5572,46 |
| judge / typesafe/jev-1.13 / native / jev | 68/68 | 0.011316942 | 68/68 | 27,60 | 68/68 | 5554,98 |

Contabilidade final fornecida pela controladora, campos públicos:

```text
{
  "synthetic": false,
  "key_usage_usd": "10.505607254",
  "difference_usd": "-1.64E-8",
  "native_known_cost_usd": "10.5056072704",
  "observed_at": "2026-10-25T22:26:55.550075+00:00",
  "unknown_cost_slots": [
    {
      "slot": "g.01-noticia-bibliotecas.r15.baseline",
      "reason": "no_native_cost"
    }
  ],
  "native_cost_usd": null,
  "ledger_reconciliation": {
    "status": "unknown_native_costs",
    "unknown_costs_assigned": false,
    "note": "Uso da chave é cumulativo, não um delta isolado desta execução. A diferença informada não atribui cobranças a slots e não comprova custo zero para chamadas sem custo nativo. Reconciliação de escopo e cobranças não verificada aqui."
  }
}
```

Uso nativo agregado, incluindo denominadores de tokens e custo:

```text
{
  "all": {
    "submitted": 355,
    "cost_observed_calls": 354,
    "known_cost_usd": "10.5056072704",
    "cost_usd": null,
    "input_tokens": {
      "known": 1465980,
      "observed_calls": 354,
      "total": null
    },
    "output_tokens": {
      "known": 399819,
      "observed_calls": 354,
      "total": null
    }
  },
  "generation.baseline": {
    "submitted": 76,
    "cost_observed_calls": 75,
    "known_cost_usd": "1.5536681116",
    "cost_usd": null,
    "input_tokens": {
      "known": 444783,
      "observed_calls": 75,
      "total": null
    },
    "output_tokens": {
      "known": 108033,
      "observed_calls": 75,
      "total": null
    }
  },
  "generation.skill": {
    "submitted": 75,
    "cost_observed_calls": 75,
    "known_cost_usd": "1.4680632168",
    "cost_usd": "1.4680632168",
    "input_tokens": {
      "known": 445192,
      "observed_calls": 75,
      "total": 445192
    },
    "output_tokens": {
      "known": 96097,
      "observed_calls": 75,
      "total": 96097
    }
  },
  "judge.jev": {
    "submitted": 68,
    "cost_observed_calls": 68,
    "known_cost_usd": "0.011316942",
    "cost_usd": "0.011316942",
    "input_tokens": {
      "known": 269451,
      "observed_calls": 68,
      "total": 269451
    },
    "output_tokens": {
      "known": 20607,
      "observed_calls": 68,
      "total": 20607
    }
  },
  "judge.astra": {
    "submitted": 68,
    "cost_observed_calls": 68,
    "known_cost_usd": "4.3888550",
    "cost_usd": "4.3888550",
    "input_tokens": {
      "known": 113628,
      "observed_calls": 68,
      "total": 113628
    },
    "output_tokens": {
      "known": 59482,
      "observed_calls": 68,
      "total": 59482
    }
  },
  "judge.opus": {
    "submitted": 68,
    "cost_observed_calls": 68,
    "known_cost_usd": "3.083704",
    "cost_usd": "3.083704",
    "input_tokens": {
      "known": 192926,
      "observed_calls": 68,
      "total": 192926
    },
    "output_tokens": {
      "known": 115600,
      "observed_calls": 68,
      "total": 115600
    }
  }
}
```

## Limites da interpretação

A amostra mede redação em cinco pedidos, não reescrita nem leitura humana. Não autoriza aceitação da candidata. O pedido 06 já integrou diagnóstico anterior e os demais também pertenciam ao histórico. Médias de estudos com pedidos ou instruções de juiz diferentes não demonstram evolução sobre a 0.9.0.

## Evidências

Esta projeção parcial não é reprodução completa do store privado. O empacotamento opcional copia apenas a allowlist dos insumos congelados, sem HTTP raw, probes ou metadados de conta.

- [Textos e julgamentos estruturados](report/RESULTS.json).
- [Protocolo anterior às chamadas](report/PROTOCOL.md).
- [Seleção e seed](report/selection.json).
- [Hashes da preparação, não dos pacotes congelados](report/source-hashes.json).
- [Allowlist e hashes dos pacotes congelados](report/FREEZE-ALLOWLIST.json).
- [Implementação](report/IMPLEMENTACAO.md).
- [Contabilidade pública](report/accounting-public.json).
- [Hashes da projeção](report/SHA256SUMS).

## Textos completos

Cada pedido tem seu relatório com o texto original, os dois braços e os pareceres dos três juízes. Os links estão na tabela por pedido acima. O [arquivo integral em Markdown](https://raw.githubusercontent.com/larguesa/my-skills/3b27ad06598e2cc5270745e0a121bb77a0cd52cb/skills/humanizador-pt-br/results/samples/2026-10-25/report/REPORT.md) reúne todos os blocos em um único arquivo.
