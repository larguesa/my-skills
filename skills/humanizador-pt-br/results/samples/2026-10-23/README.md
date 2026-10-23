# Humanização: 0.9.0 versus 0.8.1

**Amostra interrompida.** A humanização percebida aumentou: H passou de 33,02 na 0.8.1 para 39,00 na 0.9.0, diferença de +5,97 pontos nos 76 pares julgados pelos três avaliadores.

Cobertura: **76 de 95 pares** com os três juízes; **228 de 285 julgamentos** válidos.

## O que foi comparado

Foram sorteados 5 dos 24 pedidos de redação aprovados (20,83%, arredondamento para cima dos 20% solicitados). Os dois braços usam skill: versão anterior 0.8.1 e candidata 0.9.0. Cada par mantém pedido literal, modelo, provedor, raciocínio e limite de saída iguais, em contextos independentes. Foram planejadas todas as 19 configurações dos 14 modelos do estudo anterior.

H é o índice de humanização percebida, de 0 a 100: 100 menos a impressão de IA atribuída pelo juiz. ΔH positivo significa maior humanização percebida na candidata. Trata-se de julgamento do texto, não de probabilidade de autoria humana. A média principal usa apenas pares com os três juízes completos, com peso igual por par e juiz.

## Humanização percebida

| Avaliador | Pares julgados | H 0.8.1 | H 0.9.0 | ΔH (pontos) |
|---|---:|---:|---:|---:|
| jev | 76 de 95 | 36,71 | 39,17 | +2,46 |
| astra | 76 de 95 | 26,42 | 34,67 | +8,25 |
| opus | 76 de 95 | 35,93 | 43,14 | +7,21 |

**Média principal (76 pares completos):** 0.8.1 = 33,02, 0.9.0 = 39,00, ΔH = +5,97 pontos.

## Naturalidade, preferência e fidelidade

| Medida nos pares completos | 0.8.1 | 0.9.0 |
|---|---:|---:|
| Naturalidade média (0 a 100) | 80,69 | 84,59 |
| Correção/fidelidade média (0 a 100) | 82,61 | 87,20 |
| Votos de preferência | 142 | 77 |
| Julgamentos com falha factual crítica | 19 | 13 |

Houve 9 empates. Denominador: 228 votos e 228 avaliações de fidelidade por versão. Preferência avalia qualidade e atendimento ao pedido, separadamente da impressão de IA.

## Textos completos e notas por pedido

| Pedido sorteado | Pares com três juízes | ΔH médio nesses pares | Textos e notas |
|---|---:|---:|---|
| Jornalístico: reportagem sobre drenagem | 16 de 19 | +6,77 | [Abrir](cases/02-reportagem-drenagem.md) |
| Física: medidas de período | 15 de 19 | +4,93 | [Abrir](cases/06-experimento-periodo.md) |
| Química: equilíbrio | 16 de 19 | +5,67 | [Abrir](cases/07-equilibrio-quimico.md) |
| Negócios: proposta comercial | 16 de 19 | +8,29 | [Abrir](cases/15-proposta-comercial.md) |
| Opinião e ensaio: concentração e disponibilidade | 13 de 19 | +3,72 | [Abrir](cases/20-ensaio-produtividade.md) |

## Escopo e estado da execução

O sorteio foi único, com seed inteira `7355462371757875015`, antes das chamadas. Os casos foram 02, 06, 07, 15 e 20. A comparação usa novas gerações das duas versões, sem reaproveitar médias históricas. A candidata e os exemplos não foram modificados com base nas notas.

O corpus desta amostra é de redação. A reescrita e a leitura humana dos exemplos continuam pendentes. A versão distribuída permanece 0.8.1; o teste não publica a candidata como versão aceita.

A execução não concluiu todos os pares planejados. O resultado acima descreve apenas a cobertura indicada, sem atribuir notas aos pares ausentes.

A execução foi interrompida por limite de requisições do provedor Alibaba para o Qwen3.8 Flash. Foram avaliados 76 dos 95 pares planejados. Sete pares ficaram sem julgamento por saídas inválidas: sete respostas excederam a contagem máxima de saída e três foram truncadas. Outros 12 pares não foram concluídos após a interrupção. A chamada rejeitada não foi repetida; os textos e julgamentos já recebidos foram preservados.

## Telemetria secundária

Chamadas submetidas: 395. Custo nativo conhecido: USD 8.1543969932. Chamadas com custo nativo registrado: 394 de 395. Essas medidas não são critério de sucesso da humanização.

O uso registrado na chave dedicada foi USD 8.154396979, igual à soma dos custos nativos truncados individualmente a nove casas decimais. A chamada rejeitada não trouxe custo nativo; não foi atribuído um custo zero a ela.

## Evidências

- [Dados completos, textos e julgamentos](RESULTS.json).
- [Protocolo definido antes das chamadas](PROTOCOL.md).
- [Sorteio e sua reprodução](selection.json).
- [Hashes dos pacotes comparados](source-hashes.json).
- [Hashes da publicação](SHA256SUMS).
