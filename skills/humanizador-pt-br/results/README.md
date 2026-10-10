# Avaliação e validação

Os [24 prompts](PROMPTS.md) foram aprovados por Ricardo em 06/10/2026. Seus pedidos permanecem literais. H1 e H2 foram descartados.

A atualização 0.5.0 dos perfis coloquial, informal e caricato foi autorizada por Ricardo em 07/10/2026. Em 10/10/2026, Ricardo autorizou iniciar os novos testes e solicitou a remoção de duas referências textuais do pacote. A versão 0.5.1 remove esses arquivos e suas dependências de leitura, preservando catálogo, estilos, script e pedidos aprovados.

Estado desta atualização: preparação da nova execução. Ainda não há geração nova ou voto de juiz publicado. Não há novo ganho de qualidade ou custo demonstrado.

A comparação futura usará o mesmo pedido em chamadas independentes do mesmo modelo e configuração, variando apenas a presença da skill aprovada. Nenhuma resposta será entregue à outra condição. O protocolo deve definir como as consultas ao catálogo, estilos e planos serão executadas ou injetadas, sem dar ferramentas ou contexto adicionais apenas a um braço por acidente.

## Validação local do script

[test_humanizar.py](test_humanizar.py) contém testes funcionais offline, não avaliação de escrita por modelos. Execute na pasta da skill:

```text
python3 results/test_humanizar.py
```

[VALIDACAO.md](VALIDACAO.md) registra a execução e os limites. Esta validação não mede naturalidade, preferência de leitores nem superioridade da skill.

A antiga pasta `tests/` não foi recriada. Evidências históricas continuam no [Git](https://github.com/larguesa/my-skills/tree/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests), sem serem apresentadas como resultados do novo desenho.
