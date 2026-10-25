# Alterações da candidata 0.9.1

Implementação concluída com Claude Code, Opus 5.5 e esforço máximo. A versão distribuída permanece 0.8.1. A candidata e a referência usadas na comparação estão preservadas nos [arquivos congelados](../sources/PACKAGE-INVENTORY.json).

## Objetivo

Melhorar a humanização percebida, preservando os fatos, a voz e o atendimento ao pedido. Tempo, tokens e custo são medidas de execução, não critérios de sucesso editorial. O resultado comparativo está no [relatório](REPORT.md).

## Mudanças

1. O exemplo do gênero ensina recursos de escrita, sem determinar os fatos, a extensão, a abertura, a estrutura ou os papéis do texto solicitado.
2. Antes de cortar, a redação confere se atendeu a cada verbo e conceito do pedido. Repetição funcional continua permitida.
3. Tranquilização automática: “E tudo bem” pede corte somente quando não tem função no artefato. Acolhimento solicitado e voz do autor ficam.
4. Fechos repetitivos: a frase de efeito reiterada pede revisão quando substitui o desenvolvimento. Frases curtas, fechos memoráveis e perguntas legítimas ficam.
5. Responsabilidade escondida: em “a decisão surgiu”, o responsável só é nomeado quando o material o identifica e isso importa. Não se inventa agente nem se troca um sujeito não humano legítimo, como “o servidor envia a resposta”.

Os três diagnósticos foram adaptados após a análise do [stop-slop no commit examinado](https://github.com/hardikpandya/stop-slop/tree/8da1f030185bdfe8471220585162991eaeb970e9), sem importar o pacote ou seus vetos universais. Advérbios, voz passiva, listas de três, perguntas e formalidade não ganharam proibição geral.

## Implementação funcional

O catálogo mantém 32 regras. Três delas receberam metadados com ação, exceções, exemplos e origem. `catalog` pesquisa esses metadados; `audit` retorna os sinais em `diagnosticos_condicionais`, separados de `findings` e `rule_counts`. Os sinais não bloqueiam `check` nem alteram o texto automaticamente.

A orientação editorial também está na SKILL.md. As heurísticas locais reconhecem formulações delimitadas e fechos finais repetidos; a decisão de editar continua dependente do contexto. Os briefings mantiveram seus contratos e limites de tamanho, e o modo revisão preservou suas impressões digitais.

## Validação de software

A verificação independente aprovou 130 testes, sem falhas, erros ou testes pulados: 118 da suíte original preservada e 12 novos testes dos diagnósticos. Foram exercitados o catálogo real, os comandos de linha de comando, exceções, casos positivos e negativos, documentação e contratos dos briefings.

Comando executado na pasta da candidata:

```text
python3 -B -W error -m unittest discover -s results -p 'test*.py' -v
```

A validação final também foi executada em cópia integral, conferida por hashes, com todas as fixtures originais. A suíte original não foi alterada: SHA-256 `17cdab4875e715c59cd95121499ba3f6d9283679b5c261514dca6863c1c0f9c9`.

Esses testes verificam o software. As notas de humanização, fidelidade e preferência vêm exclusivamente dos julgamentos registrados no relatório.

## Fontes preservadas

- [Candidata 0.9.1](../sources/frozen/skill/SKILL.md).
- [Referência 0.8.1](../sources/frozen/baseline/SKILL.md).
- [Runner efetivamente congelado](../sources/frozen/runner/sample_eval.py).
- [Protocolo e emenda](PROTOCOL.md).
- [Testes e verificação independente](../validation/README.md).

As outras propostas do plano não foram incorporadas nesta candidata. O estudo amostral não altera a versão distribuída.
