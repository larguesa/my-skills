---
name: humanizador-pt-br
description: Revise textos em PT-BR preservando fatos e voz.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [escrita, edicao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Revisão editorial contextual de clareza, ritmo e adequação ao leitor. Não detecta autoria, não promete escapar de detectores e não transforma frequências em probabilidade de IA.

## Quando usar

- Revisar prosa em português brasileiro percebida como genérica, repetitiva ou distante da voz do autor.
- Auditar um rascunho antes de propor alterações ou comparar versões autorizadas.
- Variar discretamente a forma de uma série, dentro da mesma voz.
- Não usar para julgar autoria acadêmica, remover atribuições ou fabricar experiência pessoal.

## Pré-requisitos

Texto original, finalidade e público. Amostra de voz é opcional. Se ausente, conservar registro e escolhas reconhecíveis do original, sem impor uma personalidade.

O procedimento textual funciona com leitura e revisão. Utilitários locais são auxiliares: consultar o README e o `--help` da versão presente antes de executá-los. Não pressupor APIs, dependências ou flags não documentadas. Não enviar material confidencial a serviços externos sem autorização.

## Procedimento

1. **Delimitar a autorização.** Auditoria é o padrão. Pedido explícito de reescrita autoriza uma proposta revisada, não publicação ou sobrescrita do arquivo de origem. Registrar público, gênero e restrições.
2. **Fixar invariantes.** Inventariar fatos, nomes, números, datas, unidades, URLs, citações, comandos, negações, condições, grau de certeza, agente e causalidade. Preservar códigos, tabelas de dados e trechos literais. Resolver ambiguidades relevantes antes de alterar sentido.
3. **Ler a voz.** Anotar formalidade, distância do leitor, ritmo e vocabulário técnico a partir do original ou de amostras autorizadas. Não inferir biografia, região, sentimentos ou opinião.
4. **Auditar contexto.** Ler [catálogo](references/catalogo.json). Cada regex localiza candidatos; não decide se há defeito. Conferir gênero, entorno, exceções e risco. Aceitar como legítima uma ocorrência que cumpre função.
5. **Propor por trecho.** Informar problema observável, alternativa e possível perda. Nunca fazer substituição global de palavras. Fontes comerciais e skills inspiram candidatos, não autorizam alterações.
6. **Reescrever apenas no escopo aprovado.** Usar fatos já disponíveis. Se faltar detalhe, preservar a formulação sustentada ou marcar uma pergunta fora do texto final. Não preencher lacunas com números, depoimentos ou exemplos apresentados como reais.
7. **Variar com discrição, se solicitado.** Consultar [estilos](references/estilos.json), manter a voz fixa e registrar perfil e seed. Seed organiza escolhas editoriais; não garante reprodução literal de saída de modelo.
8. **Revisar semântica antes de fluência.** Comparar cada afirmação com o original. Conferir especialmente negações, obrigação versus possibilidade, correlação versus causa, intervalo e denominador. Uma checagem lexical não prova equivalência.
9. **Entregar resultado verificável.** Mostrar auditoria ou versão revisada, mudanças relevantes, preservações deliberadas e dúvidas. Se houver autorização de gravação, usar destino separado ou diff aprovado. Não publicar.

## Ferramentas locais

Usar `terminal` na raiz do pacote: `python3 scripts/humanizar.py audit entrada.txt` para achados; `python3 scripts/humanizar.py suggest entrada.txt --profile neutro-claro --seed 17` para recomendações e ênfase de estilo. O catálogo padrão não fornece trocas automáticas; `edits: []` pode ser o resultado correto.

Aplicar apenas um plano aprovado: `python3 scripts/humanizar.py apply entrada.txt --plan plano.json --output revisado.txt`. Comparar com `python3 scripts/humanizar.py verify entrada.txt revisado.txt`. Acrescentar `--protect "termo"` para termos invariantes. Ver [formato do plano](README.md) antes de preenchê-lo.

O segundo utilitário, [benchmark.py](scripts/benchmark.py), executa comparação externa somente com autorização e teto explícito. Verificar `--help` e o protocolo antes de chamadas pagas. Não instalar classificador, serviço permanente ou biblioteca linguística pesada.

## Contrato do catálogo

- Raiz JSON: lista de regras. `pattern`: regex Python com flags explícitas; `source`: IDs do [registro](references/fontes.md).
- `positive_example`: exemplo inventado de ocorrência candidata; não significa texto ruim nem autoria de IA.
- `negative_example`: exemplo inventado sem o gatilho. Não é reescrita factual automaticamente autorizada do positivo.
- `context`, `exceptions`, `genres` e `meaning_risk` exigem avaliação humana ou editorial; regex não os interpreta.
- `allowed_action` restringe as regras a `audit` e `suggest`. Aplicar edição exige autorização explícita fora do catálogo.
- `evidence: heuristica_editorial` significa hipótese editorial sem calibração estatística demonstrada.

## Salvaguardas

- Não há palavras proibidas. Manter robusto, significativo, além disso e termos semelhantes quando precisos. Significância estatística não é sinônimo de importância prática.
- Preservar qualificadores científicos, legais e de segurança. Clareza não justifica aumentar certeza.
- Não inserir erros, gírias aleatórias, regionalismos presumidos, falsa intimidade ou depoimentos inventados.
- Não remover listas úteis, conectivos lógicos ou terminologia para reduzir uma contagem.
- Não introduzir travessão longo na nova prosa. Em citação literal ou dado protegido, preservar o original e sinalizar conflito de formato.
- Ritmo variado é uma escolha de leitura, não um sinal obrigatório de humanidade.
- Frequência normalizada descreve apenas a amostra, tokenização e regra usadas. Zero ocorrências não comprova qualidade ou autoria.

## Verificação

- Todos os fatos e qualificações mantidos; nenhuma experiência ou fonte adicionada sem base.
- Cada alteração tem motivo contextual e está dentro da autorização.
- Voz e gênero preservados; nenhuma aplicação cega de regex.
- Relatórios distinguem achados, sugestões, edições aprovadas e pendências.
- Resultados empíricos, custos e rankings só aparecem acompanhados de execução e evidência real.

Para avaliação e limites dos dados, ler [protocolo](references/protocolo.md) e [fontes](references/fontes.md). Exploração de amostra não equivale a validação do catálogo.
