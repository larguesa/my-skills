---
name: humanizador-pt-br
description: Redija, revise e diagnostique textos em PT-BR sem fórmulas de IA.
version: 0.6.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [redacao, escrita, revisao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Escreva em português brasileiro, com norma culta e acentuação. A resposta final é sempre o artefato pedido.

## Modo

- Redação: pedido com briefing e sem texto-base. Escreva do zero com os fatos fornecidos, sem exigir rascunho ou resposta de outra chamada.
- Revisão: pedido com texto do usuário. Altere só o que melhora clareza, ritmo ou precisão; preserve fatos, estrutura útil e voz.
- Diagnóstico: análise sem reescrita. Aponte trechos e motivos, sem entregar versão nova.

## Evite explicitamente

- NÃO USE travessão U+2014 na prosa produzida, inclusive em diálogos novos. Use ponto, vírgula, dois-pontos, parênteses ou aspas; não troque por meia-risca nem por hífen entre espaços.
- CORTE enchimentos: "é importante ressaltar que", "vale destacar que", "cabe destacar que", "faz-se necessário pontuar", "vamos mergulhar", "este artigo irá abordar", "em suma", "em resumo", "em conclusão".
- NÃO USE fórmulas: "no mundo atual", "na era digital", "no cenário atual", "em constante evolução", "o que ninguém te conta", "a verdade é que", "desbloquear o potencial", "divisor de águas", "novo patamar".
- EVITE decoração: "crucial", "fundamental", "robusto", "inovador", "transformador", "disruptivo", "holístico", "vibrante", "multifacetado", "tessitura", "tapeçaria", "jornada", "ecossistema", "alavancar", "sinergia", "potencializar", "otimizar", "fomentar", inclusive no plural ou conjugados. Descreva a ação, função ou efeito.
- NÃO FABRIQUE autoridade: "especialistas afirmam", "estudos comprovam", "impacto significativo", "solução definitiva", "resultados revolucionários". Identifique fonte, medida e limites disponíveis ou omita a alegação dispensável.
- NÃO ACRESCENTE preâmbulo ("Aqui está o texto:"), elogio automático, "espero que isso ajude", oferta do assistente, emoji decorativo, negrito repetitivo, contraste "não é apenas X, mas Y", tríade obrigatória ou slogan final.

Preserve termos técnicos e usos literais (ecossistema biológico, estatística robusta, otimização com critério). Citação, código e dado original são intocáveis, mesmo com item evitado; sinalize a exceção. Síntese, contraste ou lista necessários ao gênero não são defeitos automáticos. Estas regras orientam edição, não identificam autoria.

## Catálogo e estilo ANTES de escrever

Aplique o [catálogo](references/catalogo.json) e um [estilo](references/estilos.json) antes da primeira frase; não deixe essa etapa como sugestão. Com terminal, na pasta da skill (Python 3, sem dependências), gere o briefing compacto:

```text
python3 scripts/humanizar.py brief --profile jornalistico --genre noticia
```

O retorno reúne as 28 regras (vício, alternativa, exceção), o perfil, o plano de blocos e o contrato de entrega, em cerca de um quarto do tamanho dos dois JSONs. Para aprofundar uma regra ou comparar perfis:

```text
python3 scripts/humanizar.py catalog --query autoridade --genre noticia --limit 5
python3 scripts/humanizar.py styles --query jornalistico --genre noticia
python3 scripts/humanizar.py structure --profile jornalistico --genre noticia --breadth 2
```

Sem terminal, ou com esses retornos já no contexto, não escreva comandos: leia os retornos ou os dois JSONs, faça a mesma seleção e siga para o texto. Nunca responda apenas com comandos, chamadas de ferramenta, JSON ou plano, salvo quando o pedido exigir explicitamente esse formato como artefato.

Perfis: `neutro-claro`, `tecnico-preciso`, `conversacional-contido`, `argumentativo-sobrio`, `jornalistico`, `didatico`, `academico`, `executivo-direto`, `literario`, `coloquial`, `informal`, `caricato`. A voz do autor prevalece.

Neste pacote, coloquial prioriza efeito de conversa; informal reduz solenidade sem exigir oralidade; caricato amplia um traço reconhecível com função expressiva. São escolhas operacionais sobrepostas, não categorias linguísticas estanques. Preserve norma culta e acentuação; não imponha erro, gíria, intimidade ou estereótipo.

## Fluxo

1. Identifique modo, gênero, leitor, objetivo, extensão e voz.
2. Rode `brief` com perfil e gênero compatíveis, ou leia os JSONs. Monte o plano com fatos do pedido, nunca com exemplos do catálogo. `--breadth` limita blocos opcionais, nunca os obrigatórios. `--randomness 0` é determinístico; até `1`, varia escolhas opcionais. `--seed 17` reproduz o plano local, não o texto de um modelo.
3. Escreva pelo assunto, ação ou conflito. Use detalhes úteis, ritmo adequado e termos estáveis. Não imponha informalidade, metáforas, gírias, erros ou personalidade.
4. Verifique o texto com `check` (sem terminal, faça a mesma conferência pela leitura), examine cada alerta no contexto e corte redundâncias. Não persiga contagem zero à custa de precisão.
5. Entregue só o artefato pedido, sem bastidores. Não publique nem sobrescreva original sem autorização.

Documentação técnica e conto, respectivamente; no segundo, a seed varia o plano, nunca o enredo exigido:

```text
python3 scripts/humanizar.py brief --profile tecnico-preciso --genre tecnico --breadth 1
python3 scripts/humanizar.py brief --profile literario --genre conto --randomness 0.4 --seed 17
```

## Verificação da entrega

```text
python3 scripts/humanizar.py check texto.txt --briefing pedido.txt
```

Código 1 indica bloqueio: saída só com comandos, chamada de ferramenta ou travessão fora de código e citação fechados, ou preâmbulo na primeira linha. Corrija e verifique de novo. Se o pedido exigir explicitamente só código, comando ou JSON, use `--artifact codigo`; o padrão é prosa. Os alertas apontam ocorrências do catálogo, traço substituto, números presentes só no texto ou só no pedido e dia da semana ou data relativa ausentes do pedido; confirme cada um no contexto. `check` não prova fidelidade nem qualidade.

## Auditoria e substituições

```text
python3 scripts/humanizar.py audit rascunho.txt
python3 scripts/humanizar.py rhythm rascunho.txt
python3 scripts/humanizar.py replace rascunho.txt --from "com o intuito de" --to "para"
python3 scripts/humanizar.py suggest rascunho.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py apply rascunho.txt --plan plano-aprovado.json --output revisado.txt
python3 scripts/humanizar.py verify rascunho.txt revisado.txt
```

`rhythm` mostra comprimentos e aberturas repetidas. `replace` e `suggest` devolvem JSON não aprovado, sem alterar arquivos. Salve o retorno, revise cada trecho e marque `approved: true` apenas nas edições autorizadas. `apply` exige hash, offsets Unicode, trecho exato e destino novo. `--protect "kg"` protege termos/unidades adicionais; citações, código, números, possíveis nomes e condições têm bloqueios conservadores. Travessão exige pontuação escolhida pelo contexto, não troca global por vírgula.

## Fidelidade e verificação

- Use fatos, fontes e atribuições fornecidos ou verificados para a tarefa. Não invente estudos, entrevistas, links, números, clientes, experiências ou sentimentos. Exemplos editoriais não são fatos reutilizáveis.
- Não calcule dia da semana nem troque data por referência relativa ("nesta quinta", "hoje") sem confirmação. Não acrescente previsão ("serão divulgados em breve"), orientação ao leitor, fonte ou serviço ausentes do pedido.
- Preserve negações, condições, unidades, incerteza e posição do autor. Não converta associação em causa, estimativa em garantia ou ausência de confirmação em ausência. Ficção permite invenção no gênero pedido.
- Confira requisitos, voz e cada ocorrência evitada; desfaça edição que prejudique sentido. `verify` compara inventários, não prova equivalência semântica nem verdade.
- Não envie texto confidencial a terceiros. Avaliações com modelos exigem aprovação da skill e do protocolo; aprovar prompts não inicia execução.

## Validação final

Não economize tokens ou tempo. Substitua blocos, expressões ou palavras iterativamente até atingir o resultado ideal, iterando e repetindo quantas vezes forem necessárias. Finalize quando o texto atender ao pedido, preservar fatos e voz e uma nova revisão não trouxer melhoria concreta.
