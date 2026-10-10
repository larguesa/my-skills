# Nova avaliação do Humanizador PT-BR 0.5.1

## Desenho congelado

Execução autorizada em 10/10/2026. Os 24 pedidos de [PROMPTS.md](PROMPTS.md) permanecem literais.

- 14 modelos, 19 configurações de modelo/raciocínio.
- 456 pares, com 912 gerações independentes previstas.
- Cada par usa o mesmo pedido, modelo, provedor e configuração. O baseline recebe somente o pedido; o tratamento recebe a skill 0.5.1, os JSONs completos de catálogo e estilos e consultas/plano locais congelados.
- Nenhuma condição recebe o texto da outra. Não há memória pessoal, resposta anterior ou orientação desta conversa nos candidatos.
- As consultas ao script são executadas antes da geração, com seletores fixos por caso. O teste mede esse pacote de instruções e apoio local, não uma execução autônoma completa de ferramentas pelo modelo.
- Uma geração por condição e configuração. Não há seleção de melhores tentativas nem ajuste da skill pelos resultados.
- Jev 1.13, Astra e Opus 5.5 recebem os mesmos textos anonimizados. Jev usa Decisions nativo, não chat.
- São previstas 432 chamadas de juízes, em grupos congelados de até quatro pares: 1.368 julgamentos de pares e 2.736 escores individuais de impressão de IA.
- Naturalidade, clareza, adequação e fidelidade são avaliadas separadamente. Falha factual crítica limita a nota agregada. Preferência não é o mesmo que impressão de IA.
- Um candidato inválido impede julgamento de seu grupo congelado. Ausências não viram nota zero e não há reagrupamento após os resultados.
- Não há teto monetário autorizado. Custos de sondagens, geração e juízes são medidos separadamente. Reasoning não é somado novamente aos tokens de conclusão.
- Não há repetição automática de chamadas rejeitadas, ambíguas ou já concluídas.

## Disponibilidade e alterações de rota

As 19 configurações tiveram sondagens reais aceitas. O contrato nativo de Jev também foi exercitado com Noul, Choice e Score. As sondagens totalizaram USD 0,003877564, reconciliados com o consumo da chave exclusiva da avaliação.

Antes de qualquer candidato, MiMo Pro e Flash passaram de DeepInfra FP8 para Xiaomi FP8, e Qwen Flash passou para a rota regional Alibaba us-east-1, após rejeições de disponibilidade. Os modelos e modos não mudaram. As tentativas anteriores foram preservadas; uma repetição acidental de sondagem na rota antiga do Qwen foi registrada. Não houve repetição de candidato.

## Execução verificada

O piloto real completou duas gerações independentes da primeira configuração e três chamadas de juízes, sem respostas inválidas. Seus registros pertencem à matriz completa e não serão gerados novamente. A execução completa foi iniciada em seguida.

Validação do software: 39 testes funcionais da skill e seis testes offline do runner passaram. Dados sintéticos desses testes não são resultados de modelos. O [runner](scripts/generation_eval.py) preserva intenções antes do envio, respostas brutas, hashes, custos e julgamentos, e permite retomar somente registros seguros, sem repetir chamadas.

## Limites

O piloto demonstra o funcionamento do fluxo, não ganho literário. Impressão de IA é uma avaliação não calibrada, não prova de autoria. Três votos sobre os mesmos textos não são três experimentos independentes. Modelos com dois modos aparecem em duas configurações. Caching não foi controlado como experimento separado. A conclusão depende da matriz observada e de avaliação humana.
