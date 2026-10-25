# Humanizador: retomada da comparação em 25/10/2026

A candidata 0.9.1 incorporou as correções e os três diagnósticos condicionais. A verificação de software aprovou 130 testes. A comparação com a referência 0.8.1 foi retomada nos mesmos cinco pedidos sorteados.

## Resultado

A comparação ficou incompleta: 68 dos 95 pares receberam os três julgamentos, totalizando 204 avaliações de pares. Nesses pares, a média de humanização percebida passou de 53,25 para 58,57, diferença de +5,32 pontos. A preferência global, que também considera qualidade e atendimento ao pedido, favoreceu a referência: 102 votos para 0.8.1, 86 para 0.9.1 e 16 empates.

A nota de correção/fidelidade passou de 84,43 para 87,66. Os julgamentos que identificaram falha crítica caíram de 22 para 11. São medidas diferentes de preferência e humanização.

A execução parou quando a rota Alibaba de `qwen/qwen3.8-flash`, sem raciocínio, recusou uma chamada por limite de concorrência do provedor compartilhado (`429`, `Throttling.Concurrency`). Não houve troca de rota nem repetição da chamada. Dos 27 pares sem comparação completa, sete tiveram respostas inválidas e vinte ficaram sem geração completa após a interrupção. A versão distribuída permanece 0.8.1.

## Evidências

- [Relatório completo](report/REPORT.md): agregados, 150 textos preservados, notas e observações dos três juízes, falhas, custos e tempos por modelo.
- [Alterações implementadas](report/IMPLEMENTACAO.md).
- [Verificação de software](validation/README.md).
- [Fontes congeladas e verificação local](sources/README.md): código e inputs experimentais preservados, manifesto público derivado e proveniência.
- [Cobrança observada](ACCOUNTING.md).

### Comparação por pedido

| Pedido | Pares com os três juízes | Relatório com textos integrais |
|---|---:|---|
| Notícia sobre bibliotecas | 15/19 | [Abrir](report/cases/01-noticia-bibliotecas.md) |
| Física: medidas de período | 13/19 | [Abrir](report/cases/06-experimento-periodo.md) |
| Discussão acadêmica | 13/19 | [Abrir](report/cases/12-discussao-estudo.md) |
| Probabilidade condicional | 13/19 | [Abrir](report/cases/14-probabilidade-condicional.md) |
| Comparação de infraestrutura | 14/19 | [Abrir](report/cases/16-nota-investimento.md) |

Os cinco pedidos correspondem à amostra de 20%, arredondada para cinco dos 24 pedidos aprovados. O sorteio e os critérios foram preservados. H é o índice de humanização percebida, calculado como 100 menos a nota de impressão de IA.
