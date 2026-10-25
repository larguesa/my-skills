---
name: humanizador-pt-br
description: "Faz texto em PT-BR soar escrito por um bom redator humano, ao redigir ou ao reescrever texto de IA: natural, no gênero certo, sem clichês de IA, com fatos e voz preservados."
version: 0.9.1
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [redacao, escrita, revisao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Escreva em português brasileiro, com norma culta e acentuação. Evitar vícios não basta: texto limpo que só repete o pedido continua fraco. Escreva como um bom redator brasileiro do gênero.

## Modo

- Redação: briefing sem texto-base. Escreva do zero com os fatos fornecidos, sem exigir rascunho ou resposta de outra chamada.
- Revisão: texto do usuário ou rascunho de IA. O pedido e o estado do texto definem a extensão da edição, não a origem presumida. Diagnostique antes de mexer: vícios do catálogo, ritmo e parágrafos uniformes, ressalvas que atenuam a posição, frases que só anunciam, abstração no lugar de exemplo, fecho que resume e desajuste ao gênero. Mude só o que o diagnóstico justifica, no escopo pedido: fatos, estrutura útil, voz e frases boas ficam, venham do autor ou de IA. Texto que já funciona pede poucas mudanças; devolvê-lo quase igual é resposta correta.
- Diagnóstico: análise sem reescrita. Aponte trechos, motivos e prioridades, sem versão nova.

## Como escrever bem

1. Escreva para o leitor: comece pelo que ele precisa saber ou fazer, na ordem que serve a ele, não a do pedido.
2. Na redação, o pedido é matéria-prima, não texto pronto. Conserve nomes, números, datas, termos e citações exatos, mas reescreva as frases com sintaxe própria, sujeito claro e verbo de ação.
3. Entregue o gênero completo, só com o material disponível e formatado como o meio publica. Curto não é telegráfico: frases inteiras, transições naturais, abertura e fecho do gênero.
4. Seja concreto: fato no lugar de adjetivo, exemplo no lugar de abstração, verbo no lugar de substantivo abstrato. O mesmo termo para a mesma coisa. Em "a decisão surgiu", nomeie quem decidiu só se o material disser e importar; nunca invente agente nem troque sujeito não humano legítimo ("o servidor envia a resposta").
5. Dê ritmo pelo sentido: alterne frases curtas e longas, varie aberturas e parágrafos, não force grupos de três. Ligue ideias pela relação real ("mas", "por isso"); sem relação, o ponto final basta. Lista para itens consultáveis; argumento e narrativa em parágrafos.
6. Soe brasileiro e culto: ordem direta, voz ativa, próclise natural com locuções ("pode se tornar"), sem calcos do inglês.
7. Termine quando o conteúdo acabar, sem resumo, moral ou slogan. Reescreva a frase de efeito reiterada que substitui desenvolvimento e corte "E tudo bem" sem função no artefato; frase curta, fecho memorável, pergunta legítima, acolhimento pedido e voz do autor ficam.

## Evite explicitamente

- NÃO USE travessão U+2014 na prosa produzida, inclusive em diálogos novos. Use ponto, vírgula, dois-pontos, parênteses ou aspas, sem meia-risca nem hífen entre espaços.
- CORTE enchimentos: "é importante ressaltar que", "vale destacar que", "cabe destacar que", "faz-se necessário pontuar", "vamos mergulhar", "este artigo irá abordar", "em suma", "em resumo", "em conclusão".
- NÃO USE fórmulas: "no mundo atual", "na era digital", "no cenário atual", "em constante evolução", "o que ninguém te conta", "a verdade é que", "desbloquear o potencial", "divisor de águas", "novo patamar", "não é apenas X, mas Y".
- EVITE decoração e jargão: "crucial", "fundamental", "robusto", "inovador", "transformador", "disruptivo", "holístico", "vibrante", "multifacetado", "tessitura", "tapeçaria", "jornada", "ecossistema", "alavancar", "sinergia", "potencializar", "otimizar", "fomentar", "endereçar um problema", "performar", inclusive no plural ou conjugados. Descreva a ação, função ou efeito.
- EVITE prosa de repartição: "realizar o pagamento", "efetuar a compra", "de forma eficiente", "com o intuito de".
- NÃO FABRIQUE autoridade nem finalidade: "especialistas afirmam", "estudos comprovam", "impacto significativo", "solução definitiva", "a iniciativa visa", "reforçando o compromisso". Atribua à fonte disponível ou omita.
- NA FICÇÃO, EVITE emoção pronta: "um silêncio pesado", "o tempo pareceu parar", "um nó na garganta", "e foi ali que eu entendi". Mostre gesto, objeto ou fala.
- NÃO ACRESCENTE preâmbulo ("Aqui está o texto:"), elogio automático, "espero que isso ajude", oferta do assistente, emoji decorativo ou negrito repetitivo.

Preserve termos técnicos e usos literais (ecossistema biológico, estatística robusta, jornada de trabalho, otimização com critério). Citação, código e dado original são intocáveis. Síntese, contraste, lista ou quadro necessários ao gênero não são defeitos. Estas regras orientam edição, não identificam autoria.

## Fidelidade

O pedido define se o texto é fato, opinião ou ficção e prevalece sobre o padrão do gênero (crônica pode ser relato real; roteiro, ficção).

- Fato: nomes, datas, números, resultados, falas e atribuições só do pedido, do texto-base ou de fonte verificada nesta tarefa. Reorganizar, explicar conceito geral, calcular o que o pedido manda e transformar fato em orientação ("o formulário aceita só PDF" vira "envie o arquivo em PDF") é escrever bem; acrescentar estudo, entrevista, link, número, cliente, finalidade, previsão, serviço, experiência ou sentimento não é.
- Não amplie nem restrinja o alcance ("todos", "apenas", "previsto", público). Preserve negações, condições, unidades, incerteza, tempo verbal, quem faz a ação e posição do autor; não converta associação em causa, provisório em confirmado nem ausência de confirmação em ausência.
- Não calcule dia da semana nem troque data por referência relativa ("nesta quinta", "hoje") sem conferência. Escreva "não divulgado" só quando o material disser; lacuna essencial aparece uma vez, sem previsão.
- Opinião: posição, raciocínio e exemplos hipotéticos, apresentados como hipótese, são seus; dados, estudos, citações e experiências reais só do pedido ou de fonte verificada.
- Ficção: invente cena, gestos, objetos e falas coerentes com a premissa; preserve o que o pedido fixa (narrador, frase literal, tipo de final) e não use pessoas reais.
- Exemplos editoriais não são fatos reutilizáveis. Não envie texto confidencial a terceiros. Avaliações com modelos exigem aprovação da skill e do protocolo.

## Catálogo e estilo

Aplique o [catálogo](references/catalogo.json), um [estilo](references/estilos.json) e o [exemplo do gênero](references/exemplos.json) antes da primeira frase. Com terminal, na pasta da skill, gere o briefing; na revisão, acrescente `--modo revisao`:

```text
python3 scripts/humanizar.py brief --profile jornalistico --genre noticia
```

Sem terminal, ou com esses retornos já no contexto, não escreva comandos: leia os retornos ou os JSONs e siga para o texto. Nunca responda apenas com comandos, chamadas de ferramenta, JSON ou plano, salvo quando o pedido exigir explicitamente esse formato como artefato.

Perfis: `neutro-claro`, `tecnico-preciso`, `conversacional-contido`, `argumentativo-sobrio`, `jornalistico`, `didatico`, `academico`, `executivo-direto`, `literario`, `coloquial`, `informal`, `caricato`. A voz do autor prevalece. Em todos, norma culta, sem erro, gíria ou estereótipo impostos.

## Fluxo

1. Identifique modo, gênero, leitor, objetivo, extensão e voz.
2. Rode `brief` com perfil e gênero compatíveis, ou leia os JSONs. Os blocos do plano são funções do texto, não seções obrigatórias; o exemplo do gênero ensina ofício, não molde.
3. Na redação, escreva o texto inteiro na voz do perfil, sem impor informalidade, metáfora decorativa ou personalidade; na revisão e no diagnóstico, siga o Modo.
4. Releia como leitor e como editor: complete o que falta, corte só repetição sem função e confira cada fato; na redação, antes de cortar, cumpra cada verbo do pedido e reescreva frases copiadas dele. Com terminal, rode `check`.
5. Entregue só o artefato pedido, sem bastidores. Não publique nem sobrescreva original sem autorização.

## Verificação e ferramentas

```text
python3 scripts/humanizar.py check texto.txt --briefing pedido.txt
```

Código 1 bloqueia comandos, chamada de ferramenta ou JSON no lugar do texto, preâmbulo e travessão na prosa; o travessão só passa em código, em citação, nome ou frase conferidos na fonte e, na revisão, na frase mantida (`--original`). Pedido de só código, comando ou JSON: `--artifact codigo`. Alertas pedem leitura; `check` não prova fidelidade nem qualidade.

Na revisão, `verify original.txt revisado.txt --campos caso.json` marca cada campo declarado como preservado, alterado ou ausente; o sentido continua a conferir. `audit`, `rhythm`, `replace`, `suggest` e `apply` estão no [README](README.md).

## Critério de parada

Releia o texto inteiro como editor: atende ao pedido, preserva fatos e voz? Na revisão, mudar sem motivo também é defeito. Pare quando uma nova revisão não trouxer melhoria concreta.
