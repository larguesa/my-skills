# Ampliação de 2 de outubro de 2026: interrompida

A autorização sem teto financeiro foi aplicada. A interrupção não foi causada por um teto de gasto: o provedor de MiMo Flash rejeitou duas posições diferentes por indisponibilidade temporária de sua infraestrutura. Não foram trocados modelos, rotas ou parâmetros para contornar a falha.

## Resultado real preservado

- 26 das 912 posições de geração foram iniciadas, todas no primeiro pedido (notícia sobre bibliotecas).
- 20 textos cumpriram os requisitos de resposta da API e do protocolo, formando nove pares completos. Validade de resposta não significa correção factual ou cumprimento de todas as exigências do pedido.
- Quatro respostas ficaram fora do protocolo: duas de Grok excederam o limite nativo declarado de tokens; duas de Qwen Max terminaram por limite de saída. Seus retornos, custos e tempos foram mantidos.
- Duas posições de MiMo Flash foram rejeitadas sem texto, uma no modo desligado e outra no ligado.
- O par do piloto foi julgado por Jev, Astra e Opus, em três chamadas separadas. Os outros pares não receberam julgamentos antes da interrupção. Uma observação por juiz não sustenta conclusão de superioridade.
- Permanecem 886 posições de geração não iniciadas e a maior parte dos julgamentos. Os outros 23 pedidos não foram executados.

## Custos

A leitura final da chave exclusiva apresentou **US$ 0.613509514**, conciliados com as respostas conhecidas e as sondagens:

- Geração e três juízes: US$ 0.609530096.
- 19 sondagens de rota e uma verificação do contrato Score: US$ 0.003979418.
- Diferença não atribuída no fechamento: zero.

As rejeições não devolveram custo nativo. A ausência de gasto adicional observado é evidência do fechamento da chave, não um custo informado pela API. O primeiro registro recebeu atribuição contábil documentada; o segundo permanece sem custo nativo no registro. Isso explica a coluna de custo desconhecido no relatório derivado, mesmo com o total da rodada conciliado.

[Contabilidade final](final-accounting.json) · [Resumo calculado](report-summary.json) · [Protocolo congelado](frozen/EXECUTION.md) · [Intervenção de recuperação](RECOVERY.md).

## Preservação e limites

A primeira rejeição foi inspecionada e conciliada, sem nova tentativa daquela posição. A execução continuou apenas por posições ainda não iniciadas. Após a segunda rejeição, foi encerrada. Todas as respostas válidas foram preservadas, sem edição ou regeneração.

Os relatórios dos 24 pedidos mostram as 19 configurações e suas lacunas. Os dois contos históricos permanecem intactos. Notas, impressão de IA e preferência são campos separados por juiz; não há avaliação humana concluída nem evidência suficiente para adotar ou rejeitar a skill em geral.

As verificações determinísticas de software passaram (97 testes). Elas não demonstram qualidade textual. Apoio literal, formato e cálculos reconhecidos são observações limitadas; questões semânticas não verificadas continuam pendentes.

## Publicação segura

As cópias publicadas omitem cookies de infraestrutura e identificadores de conta devolvidos nos erros. Os textos, parâmetros, decisões, tokens e custos não foram alterados. O congelamento original do runner e o registro privado dos erros foram preservados. Nenhuma credencial integra a publicação.
