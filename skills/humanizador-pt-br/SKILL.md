---
name: humanizador-pt-br
description: Redija e revise em PT-BR com clareza e voz coerente.
version: 0.3.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [redacao, escrita, revisao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Redija do zero ou revise em português brasileiro. Trabalhe clareza, ritmo, precisão e voz desde a escolha das ideias até a leitura final. Não é preciso fornecer um texto pronto, e reduzir marcas de escrita genérica não substitui escrever bem.

## Quando usar

- Redigir artigos, notícias, conteúdo técnico, textos didáticos, propostas, mensagens, posts, roteiros e literatura a partir de um pedido ou briefing.
- Revisar ou reescrever um texto existente, no nível de intervenção solicitado.
- Avaliar um texto sem alterá-lo quando o pedido for somente diagnóstico.

Não usar para fabricar depoimentos, esconder atribuições ou comprovar autoria. Esta skill não é um detector de IA.

## Defina a tarefa

Leia o pedido e o contexto disponível. Identifique gênero, leitor, finalidade, voz, extensão e restrições que realmente foram solicitadas. Uma amostra do autor orienta a voz; sem amostra, use o registro adequado ao pedido, sem inventar uma personalidade. Pergunte somente se faltar informação indispensável.

- **Redação:** planeje e produza o texto diretamente do pedido, dos dados e das fontes disponíveis. Não exija um rascunho nem crie uma versão genérica para depois humanizá-la.
- **Revisão:** preserve fatos, acontecimentos, nomes, números, citações, negações, condições, grau de certeza e posição do autor. Um trecho bom pode permanecer intacto. Reescrita ampla só quando o pedido permitir.
- **Diagnóstico:** indique trechos concretos, o problema contextual e sugestões. Não entregue uma reescrita completa por iniciativa própria.

## Fatos, citações e limites de invenção

Estas regras valem tanto para redação quanto para revisão, sem o usuário precisar repeti-las:

1. Baseie alegações factuais específicas, dados empíricos, citações e atribuições apenas no contexto existente: informações fornecidas, documentos lidos e fontes já verificadas para a tarefa. Os exemplos desta skill e do catálogo não são evidência sobre o assunto.
2. Não invente fontes, autores, estudos, especialistas, entrevistas, links, números, resultados, clientes ou credenciais. Não use expressões como “estudos mostram” para emprestar autoridade a uma opinião sem referência disponível.
3. Preserve citações literais e suas atribuições. Uma paráfrase deve manter o sentido e não aparecer como fala literal. Não transforme dado fornecido pelo solicitante em informação independentemente confirmada.
4. Se faltar uma fonte ou um fato essencial, peça-o ou indique a lacuna. Se for dispensável, escreva sem a alegação. Não pesquise nem amplie o escopo por conta própria apenas para ornamentar o texto.
5. Separe observação, cálculo, hipótese e opinião. Não converta associação em causalidade, estimativa em garantia ou ausência de confirmação em prova de ausência. Preserve ressalvas técnicas, científicas, jurídicas e de segurança.
6. Não atribua ao autor experiências, sentimentos ou opiniões pessoais ausentes do contexto. Primeira pessoa depende do papel e da posição autorizados pelo pedido.
7. Em ficção, desenvolva personagens, cenas, ações e sensações compatíveis com o gênero. Não apresente invenção como biografia, depoimento ou notícia real. Ao revisar ficção, preserve enredo e ponto de vista salvo autorização para mudá-los. Não acrescente avisos de ficção a cada conto quando o gênero já estiver claro.

## Redação e leitura final

1. **Escolha o que importa ao leitor.** Organize as informações ou a cena para cumprir a intenção. Comece pelo assunto, ação ou conflito, sem abertura que apenas anuncie o texto.
2. **Dê função aos detalhes.** Em não ficção, prefira detalhes sustentados pelo contexto. Em literatura, use detalhes que participem da cena. Não compense falta de conteúdo com abstrações, adjetivos ou decoração.
3. **Ajuste o ritmo ao gênero.** Varie frases e parágrafos quando isso ajudar a leitura. Evite fragmentos dramáticos em sequência, contrastes encenados, listas de três itens obrigatórias e parágrafos com cadência idêntica.
4. **Mantenha precisão lexical.** Repetição pode sustentar voz, clareza ou efeito literário. Não substitua termos técnicos por sinônimos vagos nem troque palavras só para parecer variado.
5. **Use estrutura e pontuação com propósito.** Títulos, listas, ênfase e apartes devem ajudar o leitor, não repetir um molde em todo texto. Evite excesso de pontuação enfática; nenhuma marca isolada identifica autoria.
6. **Não fabrique espontaneidade.** Humor, coloquialidade e primeira pessoa dependem do pedido. Gírias aleatórias, erros deliberados, falsa intimidade e opinião obrigatória não melhoram o texto.
7. **Corte o que não acrescenta.** Retire anúncios de percurso, importância inflada, fechos genéricos e explicações que a cena ou o argumento já resolvem. Mantenha a explicação necessária ao público.
8. **Leia o conjunto.** Confira progressão, continuidade, precisão e voz. Desfaça qualquer ajuste que piore a leitura. Na redação, faça essa revisão sobre o próprio rascunho, sem precisar de um texto de outra chamada.

O [catálogo](references/catalogo.json) ajuda a evitar fórmulas na redação e localizar candidatos na revisão. Regex não decide defeitos: considere contexto, gênero, exceções e risco de sentido. Não há blacklist de palavras. Os [estilos](references/estilos.json) orientam a forma tanto na redação quanto na revisão, sem sortear fatos ou personalidade.

## Entrega

Entregue o texto pronto no formato pedido. Mostre diagnóstico, versões intermediárias ou lista de mudanças somente quando solicitados, ou uma observação curta quando uma lacuna impedir a entrega fiel. Não inclua comentários sobre o processo no artefato.

Não publique nem sobrescreva o original sem autorização. Não altere trechos literais protegidos para atender uma preferência de estilo.

## Scripts opcionais

A redação e a revisão textual não dependem de Python. O script local auxilia a inspeção de um rascunho recém-escrito ou de um original fornecido, sem gerar prosa nem verificar fontes. Use `terminal` na pasta da skill:

```text
python3 scripts/humanizar.py audit rascunho.txt
python3 scripts/humanizar.py suggest rascunho.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py apply rascunho.txt --plan plano-aprovado.json --output revisado.txt
python3 scripts/humanizar.py verify rascunho.txt revisado.txt
```

`suggest` retorna recomendações não aprovadas e uma ênfase de estilo; `edits: []` é válido. `apply` exige SHA256 da entrada, offsets Unicode, trecho exato e aprovação explícita por edição; o destino deve ser novo. `--protect "termo"` acrescenta invariantes. Veja [uso e exemplo de plano](README.md).

Não envie material confidencial a terceiros sem autorização. Experimentos com modelos só podem começar após aprovação explícita da skill, dos prompts e do protocolo de execução.

## Verificação

- Cumpre a intenção e o gênero, sem impor informalidade, ornamentação ou estruturas não pedidas.
- Na redação, sustenta fatos e atribuições no contexto e respeita os limites de invenção.
- Na revisão, preserva sentido, condições, certeza e voz.
- Cada ajuste melhora leitura ou precisão, não apenas uma contagem de palavras.
- Não trata notas de juízes ou detectores como prova de autoria ou de qualidade.

[Fontes e limites das heurísticas](references/fontes.md). Não há garantia de superioridade nem de “passar em detector”.
