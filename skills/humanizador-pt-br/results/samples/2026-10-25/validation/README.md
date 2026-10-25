# Verificação de software

A candidata foi validada antes das chamadas de comparação: 130 testes aprovados, sem falhas, erros ou testes pulados. A suíte original de 118 testes permaneceu byte a byte; os outros 12 testes cobrem os diagnósticos condicionais.

- [Resultado e hashes](software-validation.json).
- [Suíte original preservada](test_humanizar.py).
- [Testes novos](test_stop_slop.py).
- [Alterações implementadas](../report/IMPLEMENTACAO.md).

Os arquivos de testes são cópias para auditoria. A execução original usou a árvore completa da candidata, os READMEs e todas as fixtures históricas, em cópia conferida por hashes. Este diretório não é uma suíte autônoma de reprodução.

Também passaram 35 testes offline do runner, 11 regressões do preparo e 21 testes de geração e auditoria dos relatórios. Seus transportes de teste são sintéticos. As notas editoriais publicadas no relatório vêm da execução real, separada dessas verificações de software.
