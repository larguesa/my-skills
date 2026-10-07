---
name: humanizador-pt-br
description: Humanize e redija textos em PT-BR sem fórmulas de IA.
version: 0.5.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [redacao, escrita, revisao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Escreva em português brasileiro.

## Evite explicitamente

- NÃO USE travessão U+2014 na prosa produzida, inclusive em diálogos novos. Use ponto, vírgula, parênteses ou aspas, não outro traço.
- CORTE enchimentos: "é importante ressaltar que", "vale destacar que", "cabe destacar que", "faz-se necessário pontuar", "vamos mergulhar", "este artigo irá abordar", "em suma", "em conclusão".
- NÃO USE fórmulas: "no mundo atual", "na era digital", "no cenário atual", "em constante evolução", "o que ninguém te conta", "a verdade é que", "desbloquear o potencial", "divisor de águas", "novo patamar".
- EVITE decoração: "crucial", "fundamental", "robusto", "inovador", "transformador", "disruptivo", "holístico", "vibrante", "multifacetado", "tessitura", "tapeçaria", "jornada", "ecossistema", "alavancar", "sinergia", "potencializar", "otimizar", "fomentar". Descreva a ação, função ou efeito.
- NÃO FABRIQUE autoridade: "especialistas afirmam", "estudos comprovam", "impacto significativo", "solução definitiva", "resultados revolucionários". Identifique fonte, medida e limites disponíveis ou omita a alegação dispensável.
- NÃO ACRESCENTE elogio automático, "espero que isso ajude", oferta do assistente, emoji decorativo, negrito repetitivo, contraste "não é apenas X, mas Y", tríade obrigatória ou slogan final.

Preserve termos técnicos e usos literais (ecossistema biológico, estatística robusta, otimização com critério). Citação, código e dado original são intocáveis, mesmo com item evitado; sinalize a exceção. Síntese, contraste ou lista necessários ao gênero não são defeitos automáticos. Estas regras orientam edição, não identificam autoria.

## Catálogo e estilo ANTES de escrever

CONSULTE o [catálogo](references/catalogo.json), SELECIONE um [estilo](references/estilos.json) e aplique as instruções e exceções retornadas. Não deixe essa etapa apenas como sugestão. Use `terminal` na pasta da skill (Python 3, sem dependências):

```text
python3 scripts/humanizar.py catalog --query autoridade --genre noticia --limit 5
python3 scripts/humanizar.py styles --query jornalistico --genre noticia
python3 scripts/humanizar.py structure --profile jornalistico --genre noticia --breadth 2
```

Leia os vícios de atribuição, o registro e os blocos retornados. Preencha o plano com fatos do briefing, não com exemplos do catálogo. Sem Python, leia os JSONs e faça a mesma seleção.

Perfis: `neutro-claro`, `tecnico-preciso`, `conversacional-contido`, `argumentativo-sobrio`, `jornalistico`, `didatico`, `academico`, `executivo-direto`, `literario`, `coloquial`, `informal`, `caricato`. A voz do autor prevalece.

Ao selecionar `coloquial`, `informal` ou `caricato`, leia as [práticas pesquisadas](references/praticas-estilos.md) antes de redigir. Neste pacote, coloquial prioriza efeito de conversa; informal reduz solenidade sem exigir oralidade; caricato amplia um traço reconhecível com função expressiva. São escolhas operacionais sobrepostas, não categorias linguísticas estanques. Preserve norma culta e acentuação; não imponha erro, gíria, intimidade ou estereótipo.

## Fluxo

1. Identifique gênero, leitor, objetivo, extensão e voz. Redação parte do briefing, sem exigir rascunho ou resposta de outra chamada.
2. Consulte catálogo e estilo. Na redação, gere um plano compatível. `--breadth` limita cobertura opcional, nunca blocos obrigatórios. `--randomness 0` é determinístico; até `1`, varia escolhas opcionais. `--seed 17` reproduz o plano local, não o texto de um modelo.
3. Escreva pelo assunto, ação ou conflito. Use detalhes úteis, ritmo adequado e termos estáveis. Não imponha informalidade, metáforas, gírias, erros ou personalidade.
4. Audite o texto, leia ocorrências no contexto e corte redundâncias. Não persiga contagem zero à custa de precisão. Entregue só o artefato pedido, sem bastidores; não publique nem sobrescreva original sem autorização.

Exemplo técnico, execute antes de redigir a documentação:

```text
python3 scripts/humanizar.py catalog --query robustez --genre tecnico
python3 scripts/humanizar.py styles --query tecnico-preciso
python3 scripts/humanizar.py structure --profile tecnico-preciso --genre tecnico --breadth 1
```

Preencha contrato, execução e verificação com a API fornecida. Para conto, use `--profile literario --genre conto`; acrescente `--randomness 0.4 --seed 17` se quiser variar o plano, nunca o enredo exigido.

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
- Preserve negações, condições, unidades, incerteza e posição do autor. Não converta associação em causa, estimativa em garantia ou ausência de confirmação em ausência. Ficção permite invenção no gênero pedido.
- Confira requisitos, voz e cada ocorrência evitada; desfaça edição que prejudique sentido. `verify` compara inventários, não prova equivalência semântica nem verdade. [fontes.md](references/fontes.md) traz instruções para aprofundar a revisão.
- Não envie texto confidencial a terceiros. Avaliações com modelos exigem aprovação da skill e do protocolo; aprovar prompts não inicia execução.

## Validação final

Não economize tokens ou tempo. Substitua blocos, expressões ou palavras iterativamente até atingir o resultado ideal, iterando e repetindo quantas vezes forem necessárias. Finalize quando o texto atender ao pedido, preservar fatos e voz e uma nova revisão não trouxer melhoria concreta.
