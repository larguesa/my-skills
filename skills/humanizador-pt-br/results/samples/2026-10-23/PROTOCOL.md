# Teste amostral de humanização, 23/10/2026

## Pergunta

A candidata 0.9.0 produz textos percebidos como mais humanos que a versão 0.8.1, sob os mesmos pedidos e configurações?

O resultado principal é o julgamento de humanização. Tempo, tokens e custo são apenas telemetria, não critérios de sucesso.

## Escopo solicitado

Ricardo pediu em 23/10/2026 um conjunto aleatório de 20% do corpo de testes. O corpo disponível contém 24 pedidos de redação aprovados. A seleção é de 5 pedidos, arredondamento para cima de 4,8 (20,83%). Os pedidos de reescrita ainda não possuem corpus final; este estudo mede redação e não cria evidência de reescrita.

O sorteio foi realizado uma única vez, antes de qualquer geração ou julgamento, com `random.Random(7355462371757875015).sample(range(1,25),5)`. A seed inteira foi obtida por `secrets.randbits(64)` e preservada. Ordinais selecionados, em ordem: 02, 06, 07, 15 e 20. Os arquivos `selection.json` e `sample.json` registram a mesma seleção; não são sorteios distintos.

## Comparação

- Referência: pacote 0.8.1 do commit `607fe0230d19633f07529bcd6dacdab0b3252504`.
- Candidata: pacote local 0.9.0 preservado antes das chamadas.
- Dois braços com skill. Não comparar a candidata contra texto sem skill nem contra médias de rodadas antigas.
- Mesmo pedido literal, modelo, provedor, configuração de raciocínio e limite de 4.096 tokens de saída em cada par.
- Cada braço recebe apenas a sua SKILL.md, o briefing local do mesmo gênero e o pedido. Contextos independentes, sem SOUL, memória ou orientações desta conversa, sem textos ou críticas do outro braço.
- Mantidas as 19 configurações anteriores, com as rotas efetivas da rodada 0.8.0. Catálogo e endpoints foram consultados novamente; as sondagens aceitas anteriores são preservadas como evidência histórica de compatibilidade, não como sondagens atuais.
- 5 pedidos × 19 configurações: 95 pares, 190 gerações e 285 julgamentos.
- Cada par é julgado por Jev 1.13 (Decisions nativo), GPT-6 Astra e Claude Opus 5.5. Rubrica inalterada de `eval_judges.py`, um par anônimo por chamada, sem identificação de braço ou gerador.
- A ordem percorre todos os pedidos sorteados de uma configuração, julgando cada par antes de avançar. Não há seleção de resultados favoráveis.

## Resultado

H = 100 menos a impressão de IA atribuída pelo juiz, na escala de 0 a 100. ΔH = H da 0.9.0 menos H da 0.8.1, em pontos. A média principal dá o mesmo peso a cada par com os três juízes completos. Também serão apresentados H e ΔH por juiz, naturalidade, preferência e falhas factuais críticas. H é um índice de percepção, não uma probabilidade de autoria humana.

ΔH positivo indica melhora percebida nos pares avaliados; zero indica ausência de mudança; negativo indica piora. Preferência e fidelidade são informadas separadamente para identificar eventual troca de qualidade por aparência. O relatório informa sempre o total planejado e o total efetivamente julgado. Não há aceitação de release nem conclusão sobre reescrita a partir deste estudo amostral.

## Integridade e execução

Este teste amostral foi solicitado após o plano integral. Não é execução nem aprovação do protocolo integral de duas modalidades. A leitura humana dos exemplos continua não realizada; não será simulada nem registrada como concluída.

Pacotes, seleção, payloads, mapa cego, rubrica e runner são congelados por SHA-256 antes das chamadas. Respostas brutas e notas são preservadas. Nenhuma saída é editada, substituída ou repetida. Saídas inválidas permanecem registradas; não recebem notas inventadas. Falha sem resposta ou cobrança ambígua interrompe novas chamadas para conferência, sem repetição automática.

A execução usa chave OpenRouter dedicada, sem teto monetário, com rastreamento de consumo. O supervisor dá a cada passo um prazo total de 600 segundos, além do timeout de socket do transporte. Se o prazo expirar, preserva a tentativa e interrompe o estudo, sem atribuir a causa ao provedor nem assumir cobrança zero. Os testes offline usam transporte explicitamente sintético e nunca contam como evidência de humanização.

## Publicação

O README deve mostrar o propósito da skill e o resultado observado da amostra em linguagem simples. O relatório apresenta os textos completos e os três julgamentos por par, mantendo a distinção entre estudo concluído e interrompido. Chaves, respostas HTTP privadas e dados de conta não são publicados. A candidata permanece distinta da versão distribuída enquanto não houver decisão de publicação.
