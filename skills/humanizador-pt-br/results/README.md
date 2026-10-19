# Avaliação e validação

Os [24 prompts](PROMPTS.md) foram aprovados por Ricardo em 06/10/2026. Seus pedidos permanecem literais. H1 e H2 foram descartados.

A atualização 0.5.0 dos perfis coloquial, informal e caricato foi autorizada por Ricardo em 07/10/2026. Em 10/10/2026, Ricardo autorizou iniciar os novos testes e solicitou a remoção de duas referências textuais do pacote. A versão 0.5.1 remove esses arquivos e suas dependências de leitura, preservando catálogo, estilos, script e pedidos aprovados.

Estado: a [retomada de 13/10/2026](runs/2026-10-13/README.md) avançou para 30 respostas de geração completas (28 textos e duas saídas apenas com comandos) e 12 chamadas de juízes, com 33 julgamentos sobre 11 pares. O limite temporário do Qwen Flash impediu concluir a matriz. Na amostra parcial, a humanização média percebida caiu 3,79%, os tokens aumentaram 3.131,84% e o tempo das chamadas caiu 13,28%, incluindo as duas falhas de entrega. Consulte as três respostas e seus denominadores no [relatório objetivo](runs/2026-10-13/OBJETIVO.md). Os [resultados de 10/10](runs/2026-10-10/README.md) permanecem intactos; não há ganho geral demonstrado.

Versão 0.6.0, 19/10/2026: [revisão](REVISAO-2026-10-19.md) com briefing compacto, verificação de entrega e modo de empacotamento `v2-brief` no runner. O [teste de 19/10/2026](runs/2026-10-19/README.md) executou parcialmente o [protocolo 0.6.0](PROTOCOLO-0.6.0.md): 31 respostas completas, 15 pares de geração e 27 julgamentos sobre 9 pares. H passou de 42,04 para 49,19; os tokens médios passaram de 628,33 para 6.253,07, e o tempo de 6,91 para 7,37 segundos. As 15 respostas com skill passaram na verificação mecânica de entrega, sem saídas apenas com comandos. O limite temporário do Qwen Flash voltou a interromper a matriz no primeiro pedido. Os 84 testes de software passaram.

Versão 0.7.0, 19/10/2026: [revisão](REVISAO-0.7.0.md) com orientação editorial positiva antes dos vetos, plano e ofício próprios por gênero, material padrão por gênero, com o tipo pedido (fato, opinião ou ficção) prevalecendo, catálogo de 32 regras e tratamento cerca de 15% menor. Validação offline: 69 testes da skill, 15 do runner, 15 da análise e 22 do controlador, todos aprovados. Após a revisão com Claude Code Opus 5.5 max, o teste parcial de 19/10 mostrou: H passou de 26,74 para 40,27 nos 22 pares do Opus avaliados pelos três juízes; preferência de 35 a 31 pela skill. Foram 117 gerações submetidas, com 107 respostas completas e 66 julgamentos. A indisponibilidade do Grok interrompeu a matriz. Os 121 testes de software passaram. [Resultados completos da amostra](runs/2026-10-19-max/README.md), conforme o [protocolo 0.7.0](PROTOCOLO-0.7.0.md).

O [protocolo congelado](PROTOCOLO.md) de 0.5.1 descreve os 24 pedidos, 14 modelos e 19 configurações. A comparação usa chamadas independentes, variando apenas a presença da skill e de seu apoio local documentado. Nenhuma resposta é entregue à outra condição. O [runner](scripts/generation_eval.py) mantém respostas e custos separados das sondagens de disponibilidade, sem repetir chamadas automaticamente.

## Validação local do script

[test_humanizar.py](test_humanizar.py) contém testes funcionais offline, não avaliação de escrita por modelos. Execute na pasta da skill:

```text
python3 results/test_humanizar.py
python3 -m unittest discover -s results/scripts -p test_generation_eval.py
```

[VALIDACAO.md](VALIDACAO.md) registra a execução e os limites. Esta validação não mede naturalidade, preferência de leitores nem superioridade da skill.

A antiga pasta `tests/` não foi recriada. Evidências históricas continuam no [Git](https://github.com/larguesa/my-skills/tree/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests), sem serem apresentadas como resultados do novo desenho.
