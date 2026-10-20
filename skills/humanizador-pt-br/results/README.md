# Resultados do Humanizador PT-BR

Teste A/B de percepção: cada pedido de [PROMPTS.md](PROMPTS.md) é escrito duas vezes pelo mesmo gerador, sem e com a skill, e os juízes Jev, Astra e Opus avaliam os textos sem saber a origem. H é 100 menos a impressão de IA dada pelo juiz, de 0 a 100; quanto maior, mais humano. Meta, protocolo, critérios de decisão e convenção de arquivos: [AGENTS.md](../AGENTS.md).

<!-- tabela:inicio -->
| Versão | Referência | Amostra julgada | H referência | H versão | Δ H | Votos versão / referência / empate | Situação | Textos e votos |
|---|---|---|---:|---:|---:|---|---|---|
| 0.2.0, 2 contos | sem skill | 38 de 38 pares; 2 contos; 19 configurações | 30,00 | 41,19 | +11,19 | 71 / 43 / 0 de 114 | Completa. Pedidos antigos, fora dos 24 aprovados. Sem decisão. Valores históricos fixos, conferidos em 20/10/2026. | [índice com textos e votos](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md) |
| 0.2.0, 02/10 | sem skill | 308 de 456 pares; 24 de 24 pedidos; 19 de 19 configurações | 31,08 | 35,00 | +3,93 | 456 / 428 / 40 de 924 | Encerrada com 64 saídas inválidas e 102 pares sem juízes. Pedidos com texto antigo. Sem decisão. Valores históricos fixos, conferidos em 20/10/2026. | [índice com textos e votos](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md) |
| 0.5.1, 10 e 13/10 | sem skill | 11 de 456 pares; pedido 01; 11 de 19 configurações | 40,03 | 38,52 | -1,52 | 14 / 17 / 2 de 33 | Parcial: parou no limite do Qwen Flash; 2 respostas com skill só trouxeram comandos. Sem decisão. | [textos e votos](runs/2026-10-13/experiments/01-noticia-bibliotecas/REPORT.md), [relatório](runs/2026-10-13/README.md), [início em 10/10](runs/2026-10-10/README.md) |
| 0.6.0, 19/10 | sem skill | 9 de 456 pares; pedido 01; 9 de 19 configurações | 42,04 | 49,19 | +7,15 | 11 / 13 / 3 de 27 | Parcial: parou no limite do Qwen Flash. Sem decisão. | [textos e votos](runs/2026-10-19/experiments/01-noticia-bibliotecas/REPORT.md), [relatório](runs/2026-10-19/README.md) |
| 0.7.0, 19/10 | sem skill | 22 de 456 pares; 22 de 24 pedidos; só claude-opus-5.5 | 26,74 | 40,27 | +13,53 | 35 / 31 / 0 de 66 | Parcial: parou sem capacidade do Grok. Sem decisão. | [textos e votos por pedido](README.md#textos-e-votos-por-pedido), [relatório](runs/2026-10-19-max/README.md) |
| 0.8.0 | não se aplica | Sem A/B: 5 textos do MiMo 2.6 Pro, sem juízes | não medido | não medido | n/d | n/d | Candidata do primeiro ciclo A/B, pendente. | [teste funcional](reviews/0.8.0/SMOKE.md), [revisão](reviews/0.8.0/REVISAO.md) |
<!-- tabela:fim -->

Cada linha compara a versão com a referência indicada, dentro da mesma rodada; até aqui a referência foi sempre o texto sem skill. Pedidos, geradores e amostras mudam entre linhas, então a diferença entre linhas não mede evolução da skill. Nenhuma versão foi aceita ou rejeitada pelo protocolo de [AGENTS.md](../AGENTS.md), que vale a partir do próximo ciclo.

<!-- detalhes:inicio -->
## Por juiz

Mesmos pares da tabela acima.

| Versão | Juiz | H referência | H versão | Δ H | Votos versão / referência / empate | Falhas críticas referência / versão |
|---|---|---:|---:|---:|---|---|
| 0.5.1 | Jev | 37,36 | 30,91 | -6,45 | 2 / 9 / 0 de 11 | 2 / 2 de 11 |
| 0.5.1 | Astra | 37,45 | 42,18 | +4,73 | 6 / 4 / 1 de 11 | 3 / 0 de 11 |
| 0.5.1 | Opus | 45,27 | 42,45 | -2,82 | 6 / 4 / 1 de 11 | 4 / 2 de 11 |
| 0.6.0 | Jev | 37,00 | 33,67 | -3,33 | 2 / 7 / 0 de 9 | 1 / 0 de 9 |
| 0.6.0 | Astra | 40,78 | 58,33 | +17,56 | 6 / 2 / 1 de 9 | 2 / 0 de 9 |
| 0.6.0 | Opus | 48,33 | 55,56 | +7,22 | 3 / 4 / 2 de 9 | 2 / 0 de 9 |
| 0.7.0 | Jev | 32,77 | 40,91 | +8,14 | 0 / 22 / 0 de 22 | 0 / 0 de 22 |
| 0.7.0 | Astra | 15,82 | 32,91 | +17,09 | 20 / 2 / 0 de 22 | 2 / 1 de 22 |
| 0.7.0 | Opus | 31,64 | 47,00 | +15,36 | 15 / 7 / 0 de 22 | 0 / 0 de 22 |

## Cobertura

Observado sobre planejado em cada rodada.

| Versão | Gerações enviadas | Respostas completas | Pares completos | Chamadas de juízes | Pares com três juízes |
|---|---:|---:|---:|---:|---:|
| 0.5.1 | 31 de 912 | 30 de 912 | 15 de 456 | 12 de 432 | 11 de 456 |
| 0.6.0 | 32 de 912 | 31 de 912 | 15 de 456 | 9 de 432 | 9 de 456 |
| 0.7.0 | 117 de 912 | 107 de 912 | 49 de 456 | 66 de 432 | 22 de 456 |

## Textos e votos por pedido

Cada link abre o pedido literal, os textos completos lado a lado, da referência e da versão, e as notas de Jev, Astra e Opus, com as justificativas de Astra e Opus. A 0.2.0 usou outra redação dos pedidos e está no [índice antigo](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md).

| Pedido | 0.5.1 | 0.6.0 | 0.7.0 |
|---|---|---|---|
| 01. Jornalístico: notícia sobre bibliotecas | [11 pares](runs/2026-10-13/experiments/01-noticia-bibliotecas/REPORT.md) | [9 pares](runs/2026-10-19/experiments/01-noticia-bibliotecas/REPORT.md) | [1 par](runs/2026-10-19-max/experiments/01-noticia-bibliotecas/REPORT.md) |
| 02. Jornalístico: reportagem sobre drenagem | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/02-reportagem-drenagem/REPORT.md) |
| 03. Desenvolvimento: documentação de API | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/03-documentacao-api/REPORT.md) |
| 04. Desenvolvimento: análise de bug | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/04-analise-bug/REPORT.md) |
| 05. Física: movimento e energia | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/05-energia-movimento/REPORT.md) |
| 06. Física: medidas de período | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/06-experimento-periodo/REPORT.md) |
| 07. Química: equilíbrio | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/07-equilibrio-quimico/REPORT.md) |
| 08. Química: titulação | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/08-titulacao/REPORT.md) |
| 09. Biologia e meio ambiente: decomposição | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/09-decomposicao/REPORT.md) |
| 10. Biologia e meio ambiente: estudo ambiental | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/10-estudo-ambiental/REPORT.md) |
| 11. Acadêmico: resumo | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/11-resumo-estudo/REPORT.md) |
| 12. Acadêmico: discussão | não rodou | não rodou | [textos sem juízes](runs/2026-10-19-max/experiments/12-discussao-estudo/REPORT.md) |
| 13. Didático: cache | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/13-cache-iniciantes/REPORT.md) |
| 14. Didático: probabilidade condicional | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/14-probabilidade-condicional/REPORT.md) |
| 15. Negócios: proposta comercial | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/15-proposta-comercial/REPORT.md) |
| 16. Negócios: comparação de infraestrutura | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/16-nota-investimento/REPORT.md) |
| 17. Comunicação profissional: negociação de prazo | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/17-email-prazo/REPORT.md) |
| 18. Comunicação profissional: indisponibilidade | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/18-comunicado-indisponibilidade/REPORT.md) |
| 19. Opinião e ensaio: IA na educação | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/19-ia-educacao/REPORT.md) |
| 20. Opinião e ensaio: concentração e disponibilidade | não rodou | não rodou | [textos sem juízes](runs/2026-10-19-max/experiments/20-ensaio-produtividade/REPORT.md) |
| 21. Redes sociais: aprendizado com deploys | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/21-linkedin-aprendizado/REPORT.md) |
| 22. Redes sociais: roteiro sobre senhas | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/22-roteiro-hash/REPORT.md) |
| 23. Literário: conto na oficina | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/23-conto-oficina/REPORT.md) |
| 24. Literário: crônica na lavanderia | não rodou | não rodou | [1 par](runs/2026-10-19-max/experiments/24-cronica-lavanderia/REPORT.md) |
<!-- detalhes:fim -->

## Pendências

- A 0.8.0 não teve A/B. É a candidata do primeiro ciclo, contra o texto sem skill.
- Nenhuma rodada desde a 0.5.1 completou a matriz planejada. Só a 0.7.0 julgou vários pedidos, e com um único gerador; os pedidos 12 e 20 ficaram sem julgamento.
- Avaliação humana de percepção não registrada nestes resultados.
- O runner só usa o texto sem skill como referência. Depois da primeira versão aceita, ele precisa receber o pacote da referência.

## Testes de software

Na raiz do repositório:

```text
python3 -B -W error skills/humanizador-pt-br/results/test_humanizar.py
python3 -B -m unittest discover -s skills/humanizador-pt-br/results/scripts -p test_generation_eval.py
python3 -B -m unittest discover -s skills/humanizador-pt-br/results/runs/2026-10-19-max/analysis -p test_objetivo.py
python3 -B -m unittest discover -s skills/humanizador-pt-br/results/runs/2026-10-19-max/controller -p test_schedule_run.py
python3 -B skills/humanizador-pt-br/results/tabela.py
```

A última linha confere as tabelas destes READMEs contra os julgamentos gravados (as linhas da 0.2.0 são valores históricos fixos, sem recálculo), os links, os 24 pedidos e o `SHA256SUMS` de cada rodada. A opção `-B` evita gravar cache nas pastas seladas. Esses testes verificam software, não humanização.

## Histórico fora da árvore

Documentos antigos saíram da árvore e continuam no commit `da74a16`:

- [Project.MD](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/Project.MD): análise de 09/10/2026 sobre a 0.5.0, com propostas de melhoria.
- Protocolos da [0.5.1](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/PROTOCOLO.md), da [0.6.0](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/PROTOCOLO-0.6.0.md) e da [0.7.0](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/PROTOCOLO-0.7.0.md).
- Revisões da [0.6.0](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/REVISAO-2026-10-19.md) e da [0.7.0](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/REVISAO-0.7.0.md).
- [Registro de validação](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/VALIDACAO.md) da 0.4.0 à 0.8.0 e registros da pesquisa de estilos da 0.5.0: [fontes](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/fontes-estilos.json) e [validação](https://github.com/larguesa/my-skills/blob/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br/results/validacao-estilos.json).

Os quatro caminhos citados pelas rodadas seladas de 19/10 (`PROTOCOLO-0.6.0.md`, `PROTOCOLO-0.7.0.md`, `REVISAO-2026-10-19.md` e `REVISAO-0.7.0.md`) continuam nesta pasta como apontadores curtos para esses textos integrais. Os testes da 0.2.0 e o piloto de revisão de 29/09/2026, sem juízes, estão na pasta `tests/` do commit `d141746`: [índice com textos e votos por caso](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md).
