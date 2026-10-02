# Ampliação por gênero: planejamento preparado

⏸️ Os 24 casos foram aprovados como recorte, mas a nova rodada ainda não começou. Falta definir o teto de gasto para geração, juízes e sondagens. O teto anterior de US$ 10 dizia respeito ao piloto; não foi ampliado automaticamente.

Este documento prepara a comparação, não apresenta resultados nem confirma disponibilidade de rotas. As tabelas com posições pendentes não são textos simulados, falhas observadas ou avaliações realizadas.

## Escopo

- 12 gêneros, dois pedidos distintos por gênero, descritos integralmente em [cases.json](cases.json).
- Referência de matriz: as 19 configurações de modelo/raciocínio do estudo histórico, em 14 modelos. Nenhum modelo novo foi acrescentado e nenhuma versão foi substituída.
- Mantida essa matriz, são 912 novas gerações, em 456 pares sem/com skill. Os dois contos anteriores permanecem separados, sem regeneração.
- Cada um dos três juízes avalia os mesmos 456 pares, totalizando 1.368 julgamentos de pares e 2.736 índices individuais de impressão de IA, além das dimensões de qualidade. São contagens previstas, não chamadas executadas ou experimentos estatisticamente independentes.
- Os dados de exercícios são fictícios e fornecidos no próprio pedido. Não representam notícias reais, medições de campo ou artigos publicados. Os textos não serão atribuídos a Ricardo.

## Comparação a executar

O mesmo prompt e a mesma base factual serão apresentados em gerações independentes nas duas condições. A condição com skill não verá o original. Modelo, rota, raciocínio e teto de saída serão iguais dentro de cada par. O tratamento usará o pacote textual da skill e as referências, preservados antes das chamadas. Sem SOUL.md, memórias, outras skills ou histórico do Hermes nas requisições cruas do OpenRouter.

A extensão será apropriada ao formato, conforme cada pedido. Não se aplica a regra histórica de 80 a 120 palavras aos novos gêneros. Contagem por espaços, incluindo títulos e blocos de código, salvo o roteiro de vídeo, que tem intervalo apenas para a fala. Os pedidos indicam as estruturas obrigatórias e quais dados não podem ser inventados.

A instrução de geração específica para contos em `scripts/contos.py` não deve ser reutilizada sem adaptação para os novos gêneros. O controle de geração e os contratos de julgamento precisam ser preparados e congelados antes da execução, depois da autorização financeira. Os relatórios preparados não significam que esse runner ampliado já está implementado.

## Avaliação prevista

As quatro dimensões serão registradas separadamente, por texto e por juiz:

| Dimensão | Peso na rubrica de 100 pontos | O que observar |
|---|---:|---|
| Naturalidade | 25 | Ritmo, formulações contextuais e voz adequada, sem premiar erros ou gírias gratuitas. |
| Clareza | 25 | Organização, compreensão e relações explícitas entre fatos e argumentos. |
| Adequação ao gênero | 25 | Registro, estrutura, propósito e formato exigidos pelo pedido. |
| Correção e fidelidade | 25 | Preservação dos fatos, ressalvas, números, unidades, citações e contratos. |

Cada dimensão terá índice próprio de 0 a 100. A soma ponderada, se apresentada, terá peso de 25% por dimensão e não substituirá as colunas separadas. Âncoras: 0 para requisito ausente ou contradito; 25 para problemas graves; 50 para cumprimento parcial; 75 para bom cumprimento com problemas localizados; 100 para pleno cumprimento observável. Valores intermediários precisam de justificativa breve.

Falha factual crítica inclui alterar um dado central, unidade, negação ou citação obrigatória; fabricar fonte ou medição; remover ressalva que muda a conclusão; contradizer o contrato de API ou fornecer código incorreto para o comportamento solicitado. Em caso crítico, correção fica limitada a 25/100 e a soma ponderada a 49/100. O texto permanece publicado como falha, sem conserto ou nova tentativa guiada por nota. Desvio mecânico de tamanho ou contagem é registrado separadamente, não automaticamente tratado como erro factual crítico.

Impressão de IA (0 a 100) e preferência A/B/empate continuarão separadas. Ambos os braços são de IA; nenhum índice comprova autoria. Menor impressão não equivale a maior correção ou qualidade. Jev, Astra e Opus 5.5 terão colunas próprias. Naturalidade e fidelidade semântica não são verificações mecânicas.

Cada caso traz verificações explícitas em `checks`. Os resultados de cálculo apresentados nesses critérios são referências de validação, não respostas de candidatos. Os verificadores ampliados de formato, cálculos e execução de código ainda precisam ser implementados e exercitados; não há alegação de validação automática já realizada dos textos novos. A revisão humana, especialmente dos técnicos, ficará marcada como pendente até ser feita.

## Anonimização e limites

Os juízes receberão prompt, base e textos com IDs opacos e pares A/B, sem nome do gerador nem indicação da condição. O mapa será preservado, não enviado aos juízes. Seed e regra de ordenação serão registradas antes das chamadas.

As médias terão peso igual por par/configuração, não por família de modelo. As escalas dos juízes não serão combinadas como probabilidades calibradas. Uma geração por condição e dois pedidos por gênero são exploração de diversidade, não prova de eficácia geral. Astra e Opus também são geradores, permitindo viés de autoavaliação mesmo com anonimização. A skill não será ajustada pelas notas.

## Pré-requisitos antes das chamadas pagas

1. Aprovar teto adicional para esta rodada, incluindo candidatos, juízes, sondagens e eventuais tentativas cobradas. Se o teto não bastar, parar antes de excedê-lo e informar o que ficou pendente.
2. Verificar saldo e limites, preparar uma chave exclusiva com controle de gasto e resolver rotas indisponíveis sem substituições silenciosas. A referência histórica não comprova disponibilidade atual ou possibilidade de desligar raciocínio.
3. Congelar pedido, base, skill, rubrica, payloads, configurações, preços máximos e código efetivo com versão e hashes antes da primeira chamada. Os hashes desta preparação não substituem esse congelamento de execução.
4. Exercitar um piloto de ponta a ponta com configuração real e contabilização, sem repetir saídas válidas ao retomar. Registrar recusas, vazios e truncamentos como desfechos, não oportunidades para selecionar uma resposta melhor.
5. Persistir pedidos e respostas; cobrança ambígua bloqueia repetição automática até reconciliação. Recuperação ou mudança de rota exige registro, preservação do plano original e manutenção da mesma rota nos dois braços afetados.
6. Publicar resultados e custos reais por caso nos respectivos `REPORT.md`, atualizar o índice e pedir avaliação humana. Nunca preencher ausências com conteúdo ou notas inventados.

## Organização

`tests/README.md` contém resumo, legenda visual e índice. Cada pedido tem `tests/experiments/<identificador>/REPORT.md`, com seu prompt, resumo e tabela completa. Os dois relatórios concluídos reutilizam as evidências anteriores, sem alterar os textos ou os juízes. `tests/REPORT.md`, `results/`, `frozen/`, `PROTOCOL.md` e o piloto anterior continuam disponíveis para preservar links e rastreabilidade.

As barras usam emojis coloridos e rótulos numéricos porque o GitHub não garante CSS ou texto colorido em Markdown. Verde/vermelho representa aprovação/reprovação apenas nas verificações objetivas; barras de preferência representam votos, não sucesso factual.

[Voltar ao índice](../README.md)
