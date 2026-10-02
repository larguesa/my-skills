# Ampliação por gênero: execução autorizada

Ricardo autorizou em 2 de outubro de 2026: "Sem teto. Pode fazer. Está autorizado." A autorização abrange a matriz já preparada, incluindo geração, juízes e sondagens. Não há teto financeiro, quota na chave ou interrupção por gasto imposta pela assistente. Custos continuam sendo medidos. Limites de saldo, disponibilidade, reservas de requisições e rate limits do provedor são distintos dessa política.

## Escopo e preservação

- 24 pedidos, dois por gênero em 12 gêneros, sem alteração dos prompts de `cases.json`.
- 14 modelos e 19 configurações históricas de modelo/raciocínio, sem troca de versão ou fallback automático.
- 912 primeiras respostas independentes, formando 456 pares original/com skill. Os dois contos históricos não são repetidos e seus relatórios permanecem separados.
- Três juízes avaliam os mesmos pares: 1.368 julgamentos de pares e 2.736 índices individuais de impressão de IA previstos. Contagens previstas não equivalem a resultados executados.
- A mesma skill e referências textuais do teste anterior são congeladas. Nenhum texto é corrigido, selecionado ou regenerado com base em notas.

## Desenho

Cada par usa o mesmo pedido, base, modelo, rota, raciocínio e limite de saída. Apenas o braço com skill recebe o pacote editorial completo. Esse braço não vê a resposta original. As chamadas cruas do OpenRouter não recebem identidade, memória, outras skills ou histórico do Hermes.

Geração: limite experimental de 4.096 tokens de saída, incluindo raciocínio quando contado pelo provedor. Raciocínio segue os parâmetros das 19 configurações previamente observadas, não uma alegação de máximo. Julgamento de chat: limite de 16.384 tokens. Esses limites de saída não são tetos financeiros. As solicitações não incluem ferramentas, busca, imagens ou plugins.

Roteamento: somente a rota explicitamente congelada, `allow_fallbacks: false`, `require_parameters: true`. A aceitação das sondagens é observada por rota e modo; zero tokens de raciocínio informado não prova que um pedido de raciocínio foi cumprido ou que não houve computação oculta.

## Juízes e rubrica

Jev (`typesafe/jev-1.13`) usa exclusivamente a API nativa Decisions. Astra (`openai/gpt-6-astra`) e Opus 5.5 (`anthropic/claude-opus-5.5`) usam chat cru. Prompt, critérios e textos são enviados com IDs opacos; o mapa de modelo/condição não é enviado. Seed e ordem ficam registrados no congelamento. Os mesmos grupos de pares são usados pelos três juízes. Cada caso tem um par em grupo próprio, para reaproveitar o piloto, e os 18 pares restantes em cinco grupos de até quatro pares. São previstas 432 chamadas de julgamento, sem aumentar os 1.368 julgamentos de pares.

Naturalidade, clareza, adequação ao gênero e correção/fidelidade são julgadas separadamente. Cada dimensão tem peso de 25% na síntese. Âncoras: 0 para ausência ou contradição; 25 para problemas graves; 50 para cumprimento parcial; 75 para bom cumprimento com problemas localizados; 100 para pleno cumprimento observável.

Jev usa Score nativo com cinco níveis ordenados. Seu índice, entre 0 e 4, é a posição ponderada pelas probabilidades dos níveis, multiplicada por 25 para apresentação entre 0 e 100. Isso não é a confiança da resposta. A confiança e a distribuição, quando devolvidas, são preservadas separadamente. O serviço não produz uma justificativa textual para essas perguntas; ela será marcada indisponível, nunca inventada. Astra e Opus fornecem notas e justificativa breve.

Falha factual crítica: alterar dado central, unidade, negação ou citação obrigatória; fabricar fonte/medição; suprimir ressalva que altera a conclusão; contradizer o contrato de API ou fornecer código incorreto para o comportamento exigido. Notas brutas são preservadas. Na apresentação ajustada por criticidade, correção é limitada a 25 e a soma ponderada a 49. Desvio de extensão/contagem é mecânico e não automaticamente crítico.

Impressão de IA e preferência A/B/empate continuam separadas da rubrica e entre si. Ambos os braços são de IA. Esses índices não comprovam autoria nem são probabilidades calibradas. As escalas dos juízes não serão fundidas.

## Execução e recuperação

O runner persiste a intenção antes de enviar cada chamada, a resposta bruta, custo, tokens nativos, rota/modelo retornados, timestamps e duração. Uma chave exclusiva sem quota permite atribuir o gasto sem incluir outros projetos. A execução é sequencial, sem duplicar requisições em voo.

Um piloto de ponta a ponta usa os primeiros pares da própria matriz e seus juízes, não textos extras selecionados. Respostas válidas do piloto são reaproveitadas. Recusas, respostas vazias e truncamentos permanecem como desfechos, sem nova tentativa. Pares sem duas saídas válidas não recebem notas fabricadas. Falha de transporte ou cobrança incerta bloqueia reenvio automático e exige reconciliação antes de qualquer recuperação.

Não se muda a rota de um braço isoladamente. Qualquer recuperação posterior que altere rota ou limite precisa de emenda explícita, com plano original e custos preservados. A versão da skill não é ajustada em função dos resultados.

## Validação, publicação e limites

O verificador offline registra somente os critérios que implementa. Contagem de palavras, estrutura e presença de literais não demonstram fidelidade semântica. Os cálculos de referência são determinísticos. Código e comandos de candidatos são dados, não serão executados no host. Onde não houver verificação suficiente, o resultado fica pendente. A análise humana dos textos, sobretudo técnicos, continua necessária.

O índice em `tests/README.md` distingue dados históricos e novos. Cada `experiments/<caso>/REPORT.md` traz pedido exato, resumo visual, tabela completa com os dois textos, uma coluna por juiz, custos e tempos reais. Ausências e falhas ficam explícitas. Barras de preferência representam votos, não sucesso factual.

As médias usam peso igual por par/configuração, com denominadores por campo. Uma resposta por condição e dois pedidos por gênero são exploração de diversidade, não prova de superioridade geral. Astra e Opus também geram textos e podem apresentar viés de autoavaliação. Uma única ordem cega não elimina viés de posição. A avaliação humana permanece pendente.

## Referências do contrato Jev

Esquema atual: https://openrouter.ai/openapi.json (rota `/api/alpha/decisions`). Semântica do Score: https://docs.typesafe.ai/primitives/score.md . Exemplos da documentação são referências de API, não resultados desta rodada.

[Planejamento preservado](PLAN.md) · [Pedidos preparados](cases.json) · [Índice dos testes](../README.md)
