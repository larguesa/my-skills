# Avaliação e iteração, skill-creator Anthropic

Use ao comparar versões, planejar ensaios e avaliar os artefatos entregues.

## Práticas incorporadas

1. Capture a intenção a partir do pedido e dos materiais existentes antes de perguntar novamente.
2. Use casos realistas. Defina expectativas observáveis, não uma rubrica que premie apenas nomes de arquivos ou frases decorativas.
3. Para skill nova, compare com execução sem a nova skill. Para revisão, preserve uma cópia da versão anterior como baseline.
4. Execute cada condição em contexto limpo, com o mesmo modelo, ferramentas, entradas e orçamento. A única diferença intencional é a skill.
5. Observe o uso de referências e ferramentas além da resposta final. Um artefato com nome correto e conteúdo errado falha.
6. Separe critérios objetivos da avaliação humana de texto, design e utilidade. Use comparação cega quando ela ajudar a reduzir preferência pela versão nova.
7. Corrija regras gerais a partir de padrões, não de detalhes de um único caso. Retenha regressões e confirme em casos novos.

## Ajustes desta síntese

A revisão estudada no relatório de origem contém contratos inconsistentes entre diretórios prescritos e consumidos pelo agregador, conversão de caracteres em tokens e exceções tratadas como não acionamento. O método é reaproveitado; os scripts não foram copiados.

Use um arquivo de resultados explícito, estados distintos de falha, unidades reais e pareamento por caso/repetição. Campos sem observação ficam `null`. Se o runtime não expuser tokens ou custo, não os invente.

Selecione versões em desenvolvimento e validação. Reavaliar um conjunto durante a otimização impede tratá-lo como teste final intocado.

O pacote oferece validação e agregação local. Ele não promete um executor automático de Claude CLI ou de outro provedor. Escolha e autorize a execução de modelos no ambiente real.

## Fonte fixada

Anthropic, skill-creator, revisão `ca45fc496a3436251f191354091d557da31c15b5`:
https://github.com/anthropics/skills/blob/ca45fc496a3436251f191354091d557da31c15b5/skills/skill-creator/SKILL.md

As observações de instrumentação dizem respeito a essa revisão inspecionada, não a todas as versões futuras. Este arquivo contém síntese autoral.
