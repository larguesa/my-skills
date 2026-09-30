---
name: humanizador-pt-br
description: Melhore naturalidade em PT-BR sem perder a voz.
version: 0.2.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [escrita, edicao, pt-br]
    related_skills: []
---

# Humanizador PT-BR

Melhore o texto para quem vai ler: clareza, ritmo, precisão e voz. Cortar sinais de escrita genérica é um meio, não o objetivo. Um texto sem palavras sinalizadas ainda pode ser ruim.

## Quando usar

- Reescrever textos genéricos, repetitivos ou com formalidade deslocada.
- Revisar artigos, mensagens, conteúdo técnico e pequenos contos.
- Escrever do zero quando o pedido autorizar criação, inclusive ficção.
- Auditar sem reescrever quando o usuário pedir apenas diagnóstico.

Não usar para esconder atribuições, fabricar depoimentos ou comprovar autoria. Esta skill não é um detector de IA.

## Antes de escrever

Leia o pedido e o material disponível. Identifique gênero, leitor, intenção, registro e restrições. Use a amostra de voz quando houver; sem amostra, preserve o registro do original ou o indicado no pedido. Pergunte só se faltar informação que altere o resultado.

Distinga as duas tarefas:

- **Revisão:** conserve os acontecimentos, fatos, nomes, números, citações, negações, condições e grau de certeza. Não acrescente experiências, fontes ou detalhes apresentados como reais.
- **Criação:** desenvolva o conteúdo dentro do que o pedido permite. Em ficção, pode inventar personagens, cenas, ações e sensações; não apresente isso como biografia, depoimento ou fato real. Ao revisar uma ficção existente, preserve seu enredo e ponto de vista, salvo autorização para mudá-los.

## Como melhorar a leitura

1. **Comece pelo que acontece ou pelo que importa.** Remova aberturas que apenas anunciam o assunto. Em um conto, a cena pode começar com uma ação, um objeto ou uma fala, se isso servir à história.
2. **Troque abstração vazia por informação sustentada.** Em não ficção, use somente detalhes disponíveis. Na criação ficcional, escolha detalhes concretos que participem da cena, sem preencher cada frase com decoração.
3. **Ajuste o ritmo ao trecho.** Combine comprimentos e construções quando a leitura pedir. Não transforme todos os parágrafos em frases curtas, fragmentos dramáticos ou uma sequência de frases igualmente polidas.
4. **Conserve palavras que têm função.** Repetição pode sustentar uma ideia, uma voz ou um efeito literário. Não alterne sinônimos só para evitar repetir um nome ou termo técnico.
5. **Reduza explicações que o texto já resolve.** Corte moral da história, resumo final e interpretação de emoções quando ações e contexto já comunicarem isso. Mantenha explicações necessárias ao leitor.
6. **Prefira uma voz coerente a uma personalidade fabricada.** Humor, coloquialidade, opinião e primeira pessoa dependem do pedido e da voz. Gírias, erros deliberados e falsa intimidade não tornam o texto melhor.
7. **Leia o resultado como texto, não como checklist.** Retire a alteração que piora precisão, continuidade, ritmo ou intenção. Não editar um trecho bom também é uma decisão válida.

Consulte o [catálogo](references/catalogo.json) para localizar candidatos à revisão. Uma regex não decide se há defeito: considere contexto, gênero, exceções e risco de sentido. As palavras “robusto”, “significativo” e “além disso” não são proibidas. Consulte os [estilos](references/estilos.json) quando precisar variar discretamente a forma, sem sortear fatos ou personalidade.

## Entrega

Em pedido de criação ou reescrita, entregue o texto pronto. Acrescente observações ou mudanças somente quando forem solicitadas ou quando uma dúvida relevante impedir a revisão fiel. Em auditoria, mostre problemas concretos, trechos e sugestões, sem reescrever por conta própria.

Não publique nem sobrescreva o original sem autorização. Não introduza travessão longo na prosa nova; preserve um trecho literal protegido e sinalize conflito se houver. Não remova ressalvas técnicas, científicas, jurídicas ou de segurança para deixar o texto mais leve.

## Scripts opcionais

O procedimento textual não depende de Python. Para uma auditoria local, use `terminal` na pasta da skill:

```text
python3 scripts/humanizar.py audit entrada.txt
python3 scripts/humanizar.py suggest entrada.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py apply entrada.txt --plan plano-aprovado.json --output revisado.txt
python3 scripts/humanizar.py verify entrada.txt revisado.txt
```

O script não redige. `suggest` oferece recomendações e uma ênfase de estilo; `edits: []` é válido. `apply` exige SHA256 da entrada, offsets Unicode, trecho exato e aprovação explícita por edição; o destino deve ser novo. Use `--protect "termo"` para invariantes adicionais. Ver [uso e exemplo de plano](README.me).

Scripts de experimento e resultados ficam em [tests/](tests/README.md). Chamadas externas exigem autorização e teto financeiro. Não envie material confidencial a terceiros sem autorização.

## Verificação

- O resultado cumpre o pedido e funciona no gênero, sem impor informalidade ou ornamentação.
- Na revisão, preserva sentido, fatos, condições e voz; na criação, respeita os limites de invenção.
- Cada mudança melhora a leitura ou a precisão, não apenas uma contagem de palavras.
- Não usa notas de juízes ou detectores para otimizar o texto. Resultados de percepção precisam de leitura humana.

[Fontes e limites das heurísticas](references/fontes.md). Nenhuma taxa de autoria ou garantia de “passar em detector” é oferecida.
