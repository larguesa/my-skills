# Recuperação operacional da geração

A primeira execução foi interrompida em uma chamada Qwen Flash, modo desligado solicitado, com skill, no conto da chave. Foram preservadas 31 saídas completas e uma tentativa sem resposta disponível.

Antes da recuperação, a cobrança da chave foi conferida: soma de respostas conhecidas US$ 0,3350194708, ledger US$ 0,335019469. A diferença de US$ -0,0000000018 é compatível com precisão numérica; não há cobrança adicional visível para a tentativa falha. A categoria específica do erro HTTP não foi preservada pelo runner histórico, portanto não se atribui uma causa.

A recuperação preserva os bytes do estado original em `results/attempts/generation-attempt1.json`. O estado de continuação mantém as 31 saídas concluídas exatamente como estavam, sem repetir chamadas concluídas. Faz uma nova tentativa da posição sem resposta e depois executa somente as posições ainda ausentes. O teto acumulado de US$ 10 continua inalterado.

Houve uma segunda interrupção, no original MiMo Pro (modo desligado solicitado) do conto do bolo. A reconciliação apontou US$ 0,536923619 no ledger para US$ 0,5369236208 em respostas conhecidas, novamente diferença de US$ -0,0000000018. Foram preservadas 48 saídas completas, sem repetir as anteriores. O estado original dessa segunda tentativa está em `results/attempts/generation-attempt2.json`.

O script auxiliar `scripts/continuar.py` acrescenta apenas registro do status e corpo JSON sanitizado de futuras falhas HTTP. Usa exatamente os payloads e o controle de orçamento originais; não altera a skill, prompts, modelo, rota, raciocínio ou teto. Seu hash foi registrado antes da continuação em `results/attempts/recovery-runner-hash.json`.

A terceira tentativa parou na mesma posição MiMo Pro/bolo/original, com HTTP 429 (limite temporário do provedor). Não houve resposta de geração. A conferência posterior manteve o ledger em US$ 0,536923619, com diferença de US$ -0,0000000018 para as respostas conhecidas. As 48 saídas válidas são mantidas; somente a posição sem resposta será retomada, na mesma rota, após o intervalo. O estado e o erro desta tentativa ficam em `results/attempts/`.

A quarta tentativa recebeu novamente HTTP 429 na mesma posição, sem resposta e sem cobrança adicional visível. Para não abandonar os contos, foi fixada uma emenda antes de gerar as quatro posições MiMo Pro ainda ausentes do conto do bolo: usar GMICloud em lugar de DeepInfra. Duas sondagens confirmaram aceitação dos mesmos parâmetros ligado/desligado, com custo total de US$ 0,00002871. Ledger após sondagens: US$ 0,536952329; respostas conhecidas e sondagens: US$ 0,5369523308 (diferença US$ -0,0000000018).

Os quatro pedidos alterados conservam modelo, prompt, skill, raciocínio e teto. Só a rota e sua reserva de preço mudam. Os dois braços de cada par usam a mesma rota nova. As 48 respostas concluídas não são tocadas. O plano original e as quatro tentativas foram preservados. A emenda, os parâmetros e o hash do runner estão em `results/attempts/route-amendment.json`; o plano efetivo registra os payloads realmente executados. Os juízes ainda não haviam sido chamados. Esta rodada tem protocolo emendado, não execução ininterrupta do protocolo original.

A quinta execução parou em MiMo Flash/bolo/desligado/original, também com HTTP 429, sem resposta. Foram preservadas 60 respostas. Antes de continuar, o ledger US$ 0,615163551 foi comparado às respostas e sondagens conhecidas US$ 0,6151635528, com diferença US$ -0,0000000018. Duas sondagens GMICloud para Flash foram aceitas, somando US$ 0,00000896. As quatro posições Flash do bolo ainda ausentes passam também para GMICloud. O total de sondagens é US$ 0,00003767 e o total de posições com rota emendada é oito. A emenda anterior, seu plano e seu runner foram preservados antes dessa extensão. Nenhuma das 60 respostas válidas é repetida.

Nenhum conto foi corrigido, escolhido por nota ou regenerado após avaliação. A skill, os prompts e a configuração de geração continuam congelados. Os juízes ainda não tinham sido executados. Esta é uma intervenção operacional, não uma otimização editorial.

O estado definitivo registra os horários e resultados da continuação; a conclusão só pode ser declarada se todas as posições e avaliações estiverem presentes. Se uma nova chamada ficar incerta, a recuperação para novamente, sem repetição automática.
