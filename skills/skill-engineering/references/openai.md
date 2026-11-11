# Modularidade e recursos, skill-creator OpenAI

Use ao decidir a estrutura e a necessidade de scripts, referências ou modelos.

## Práticas incorporadas

1. Comece com `SKILL.md`. Adicione recursos apenas quando eliminarem repetição, contiverem conhecimento específico ou integrarem o produto solicitado.
2. Separe três funções: instruções principais; referências lidas sob demanda; recursos utilizados para produzir a saída.
3. Use scripts para validação, transformação e operações determinísticas recorrentes. Declare entrada, saída, dependências e sinal de falha.
4. Mantenha referências diretamente alcançáveis a partir do núcleo. Evite uma cadeia de arquivos que exige ler quase tudo antes de agir.
5. Não acrescente README, changelog ou guias redundantes por hábito. Um guia humano pode ser entregue fora da skill quando solicitado.
6. Revise a correspondência entre nome de diretório, nome do frontmatter, capacidade e descrição. Preserve o identificador ao aprimorar uma skill existente.
7. Valide a estrutura antes do uso, mas teste também o produto gerado.

## Adaptação ao destino

O scaffold e os metadados de interface de Codex pertencem ao ecossistema Codex. Não exija `agents/openai.yaml` em uma skill Hermes nem execute um inicializador que crie recursos desnecessários.

O perfil `portable` do auxiliar valida um subconjunto básico de Agent Skills. O perfil `hermes` admite extensões próprias do Hermes. Nenhum dos dois é certificação de todas as versões de todos os agentes.

## Fonte fixada

OpenAI, skill-creator, revisão `49f948faa9258a0c61caceaf225e179651397431`:
https://github.com/openai/skills/blob/49f948faa9258a0c61caceaf225e179651397431/skills/.system/skill-creator/SKILL.md

Este arquivo é uma síntese operacional autoral.
