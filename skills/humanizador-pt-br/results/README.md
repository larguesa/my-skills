# Avaliação do Humanizador PT-BR

Pergunta: com o mesmo modelo e o mesmo pedido, o texto escrito com a skill parece mais humano aos juízes, sem perder qualidade nem fidelidade? Cada pedido de [PROMPTS.md](PROMPTS.md) é escrito sem e com a skill, e Jev, Astra e Opus avaliam os dois textos sem saber a origem. Regras de aceitação: [AGENTS.md](../AGENTS.md).

## Situação

Nenhuma versão foi aceita. Todas as tentativas abaixo pararam antes do plano de 456 pares ou usaram pedidos antigos, e por isso são inconclusivas. A versão atual, 0.8.1, só muda a descrição de ativação da 0.8.0 e nunca foi avaliada.

## Tentativas

H é a humanização percebida: 100 menos a impressão de IA que o juiz atribui ao texto, de 0 a 100. Δ H é a diferença entre os textos com e sem a skill, na média dos pares julgados pelos três juízes. Cada voto é a preferência de um juiz num par; por isso há três votos por par. Amostra, pedidos e geradores mudam de uma linha para outra, então os Δ H não se comparam entre linhas nem medem evolução entre versões.

| Versão e data | Pares julgados pelos 3 juízes | Pedidos e geradores julgados | Δ H | Votos com / sem skill / empate | Por que parou |
|---|---|---|---:|---|---|
| 0.2.0, contos | 38 de 38 | 2 contos com pedidos antigos; 19 configurações | +11,19 | 71 / 43 / 0 de 114 | Completa, mas fora dos 24 pedidos atuais |
| 0.2.0, 02/10 | 308 de 456 | 24 pedidos com redação antiga; 19 configurações | +3,93 | 456 / 428 / 40 de 924 | Encerrada com 64 saídas inválidas e 102 pares sem juízes |
| 0.5.1, 10 e 13/10 | 11 de 456 | pedido 01; 11 de 19 configurações | -1,52 | 14 / 17 / 2 de 33 | Qwen Flash recusou por limite do provedor ainda no pedido 01 |
| 0.6.0, 19/10 | 9 de 456 | pedido 01; 9 de 19 configurações | +7,15 | 11 / 13 / 3 de 27 | Qwen Flash recusou por limite do provedor ainda no pedido 01 |
| 0.7.0, 19/10 | 22 de 456 | 22 pedidos; só Opus 5.5 | +13,53 | 35 / 31 / 0 de 66 | Grok sem capacidade (HTTP 502) no pedido 11 |
| 0.8.0, 20/10 | 2 de 456 | pedidos 01 e 02; só Opus 5.5 | +15,67 | 4 / 2 / 0 de 6 | Operador interrompeu após 15 minutos sem resposta do Opus no pedido 03 |

Por que tão poucos pares: o plano exige 24 pedidos × 19 configurações de modelo, sem nova tentativa de chamada que falha. Uma falha de provedor ou chamada sem resposta para a rodada inteira, e um grupo de até quatro pares com um par incompleto não vai aos juízes. Na 0.5.1 e na 0.6.0 a ordem era pedido a pedido e a parada veio no primeiro; na 0.7.0 e na 0.8.0 a ordem começou pelo Opus em todos os pedidos, por isso só há pares do Opus julgados. A 0.8.0 enviou 6 das 912 gerações: dois pares completos, que dão os 6 votos (4 com skill, 2 sem), e o texto sem skill do pedido 03.

## O que os dados parciais mostram

- **Os dados não permitem estabelecer evolução da 0.7.0 para a 0.8.0.** Só dois pedidos, 01 e 02, têm pares das duas versões, com o mesmo gerador mas gerações diferentes. Descrição: Δ H de +5,33 e +24,00 na 0.7.0 e de +6,33 e +25,00 na 0.8.0; nos dois casos Jev votou no texto sem skill e Astra e Opus no texto com skill.
- **Os juízes discordam.** Na 0.7.0, Astra votou no texto com skill em 20 dos 22 pares e Opus em 15; Jev votou no texto sem skill nos 22, embora tenha dado H maior ao texto com skill (+8,14). Não foi uma escolha fixa de A ou B: o texto com skill ficou em A em 12 pares, e Jev escolheu A em 10.
- **Opus é gerador e juiz** nas duas tentativas mais recentes.
- **Só a redação foi testada.** Os 24 pedidos pedem texto novo a partir de um briefing. Reescrever texto gerado por IA, o uso principal da skill, nunca foi avaliado.
- **Custo.** Na 0.7.0, nos 49 pares completos de Opus, Astra e Grok, o texto com skill usou 5,1 vezes os tokens (entrada média de 216 para 5.666 tokens, pelas instruções da skill; saída 15% maior) e custou 2,05 vezes em USD. Na 0.8.0, a entrada média com skill subiu para cerca de 8.500 tokens, e o custo nos dois pares foi 2,17 vezes.
- **Falha com o Grok.** Na 0.7.0, 7 das 10 respostas do Grok com skill passaram do limite de 4.096 tokens de saída e foram inválidas, com 4.135 a 19.995 tokens de saída; sem skill, nenhuma das 10.

## Pendências

- Nova avaliação só depois de decidir um plano que consiga terminar. Com o runner atual, desde a 0.5.1, nenhuma tentativa passou de 117 das 912 gerações. Mudar o plano exige escrever a versão 2 do protocolo em [AGENTS.md](../AGENTS.md#protocolo-ab) e adaptar o runner.
- Na árvore está só o runner (`scripts/`: preparar, gerar, julgar e renderizar relatórios por pedido). O resto do pipeline da 0.8.0, que agenda a ordem das chamadas, agrega `OBJETIVO.json` e publica a rodada com `DECISION.json`, saiu da árvore e precisa ser restaurado e adaptado ao novo plano, com testes, antes do `prepare`. Na raiz do repositório:

  ```text
  git restore --source=a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626 --worktree -- skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0/analysis skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0/controller
  ```

  Ao restaurar o `publish.py`, corrija o motivo genérico "software ou todos os pares": a 0.8.0 tinha software passando e falhou só por plano incompleto. Os testes publicados do controlador da 0.8.0 (`test_publication.py`) falhavam em 2 de 10 dentro do repositório, porque carregam arquivos da pasta privada de execução.
- Incluir pedidos de reescrita de texto gerado por IA.
- Avaliação humana de percepção não registrada.

## Testes de software

Na raiz do repositório:

```text
python3 -B -W error skills/humanizador-pt-br/results/test_humanizar.py
python3 -B -m unittest discover -s skills/humanizador-pt-br/results/scripts -p test_generation_eval.py
```

O primeiro testa o script e o catálogo da skill; o segundo, o runner do A/B, com a evidência bruta da tentativa de 13/10 como entrada real (`scripts/fixtures/evidence-2026-10-13`). Testam software, não humanização.

## Histórico fora da árvore

As tentativas inconclusivas saíram da árvore em 20/10/2026 e continuam no commit `a01d780`, com textos completos, votos, justificativas, custos e `SHA256SUMS`:

- [0.5.1, início em 10/10](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/runs/2026-10-10/README.md) e [retomada em 13/10](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/runs/2026-10-13/README.md)
- [0.6.0, 19/10](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/runs/2026-10-19/README.md)
- [0.7.0, 19/10](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/runs/2026-10-19-max/README.md)
- [0.8.0, 20/10](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0/README.md)
- [Revisão e teste funcional da 0.8.0](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/reviews/0.8.0/README.md): mudanças da 0.8.0, pareceres de três revisores e cinco textos do MiMo 2.6 Pro, sem juízes.
- [Página de resultados anterior](https://github.com/larguesa/my-skills/blob/a01d78038bb48ff4afd6c92a3eeaf3d7f17cf626/skills/humanizador-pt-br/results/README.md), com notas por juiz e links por pedido.

Documentos mais antigos: análise da 0.5.0, protocolos e revisões da 0.5.1 à 0.7.0 e registro de validação no commit [`da74a16`](https://github.com/larguesa/my-skills/tree/da74a16cfead72a787b217675ab09d03548addc4/skills/humanizador-pt-br); testes da 0.2.0 no [índice com textos e votos por caso](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/README.md) do commit `d141746`.
