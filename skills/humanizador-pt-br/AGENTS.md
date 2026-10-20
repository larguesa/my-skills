# AGENTS.md do Humanizador PT-BR

Regras para alterar, testar e aceitar versões desta skill. Valem junto com o [AGENTS.md da raiz](../../AGENTS.md).

## Meta

Aumentar a humanização percebida pelos modelos juízes nos textos escritos com a skill, sem perder fidelidade ao pedido. Todo ciclo de mudança termina num teste A/B, e o resultado do teste decide se a versão é aceita ou rejeitada.

## Métrica

- **Impressão de IA**: nota de 0 a 100 que cada juiz dá a cada texto. 0 é nenhum sinal de escrita por IA; 100 é certeza de IA.
- **H**: 100 menos a impressão de IA. Quanto maior, mais humano o texto pareceu ao juiz.
- **H do par**: média dos três juízes. **H do ciclo**: média dos pares julgados pelos três juízes.
- **ΔH**: H da candidata menos H da referência, em pontos.

## Juízes e rubrica

Sempre os mesmos três juízes: Jev 1.13 (`typesafe/jev-1.13`, Decisions nativo), Astra (`openai/gpt-6-astra`) e Opus 5.5 (`anthropic/claude-opus-5.5`). A rubrica é a de [eval_judges.py](results/scripts/eval_judges.py), sem mudança:

- por texto: impressão de IA de 0 a 100; naturalidade, clareza, adequação e correção de 0 a 100; falha factual crítica, sim ou não; justificativa (o Jev não escreve);
- por par: preferência A, B ou empate, pela qualidade e pelo atendimento ao pedido, nunca pela menor impressão de IA.

Falha factual crítica: alterar dado central, unidade, negação ou citação; inventar fonte ou medição; retirar ressalva que muda a conclusão; contradizer contrato de API ou entregar código errado.

## Tipos de teste

| Teste | O que mede | Papel na decisão |
|---|---|---|
| Software: `test_humanizar.py`, runner e análises | contratos do script, do catálogo e do runner | pré-requisito; não mede humanização |
| Funcional | se a versão entrega texto, sem comparação nem juízes | não decide |
| Percepção, A/B cego | ΔH entre candidata e referência | decide |
| Preferência, A/B cego | qual texto atende melhor ao pedido | trava contra perda de qualidade |

## Protocolo A/B

Versão 1, de 20/10/2026, congelada antes do próximo teste. Para mudar, escreva a versão 2 neste arquivo antes da primeira chamada de um ciclo; nunca durante o ciclo nem depois de ver resultados.

1. **Pedidos**: os 24 de [results/PROMPTS.md](results/PROMPTS.md), literais, sem acréscimos.
2. **Braços**: candidata contra referência. A referência é a última versão aceita. Enquanto nenhuma for aceita, a referência é o texto sem skill, gerado só com o pedido.
3. **Pareamento**: em cada par, os dois braços usam o mesmo pedido, modelo, provedor, modo de raciocínio e limite de saída, em chamadas novas e independentes. Só muda o pacote da skill. Nenhum braço recebe texto, nota ou crítica do outro.
4. **Plano**: o plano suportado hoje é a matriz do runner: 24 pedidos × 19 configurações, 912 gerações, 456 pares e 432 chamadas de juízes. Plano menor ou diferente, assim como referência com skill, exige antes adaptar runner, agregador e denominadores, com testes; só depois o plano pode ser congelado. O plano fica definido antes da primeira chamada e não muda depois.
5. **Congelamento**: o `prepare` do [runner](results/scripts/RUNNER.md) grava o manifest com SHA-256 da skill, catálogo, estilos, script, pedidos, payloads, mapa anônimo e runner. Registre na pasta do ciclo o commit e o SHA-256 deste arquivo.
6. **Cegueira**: os juízes recebem os textos com IDs anônimos, em grupos de até quatro pares congelados pelo runner, sem modelo nem braço.
7. **Textos brutos**: julgue e publique cada resposta exatamente como veio. Não edite, não escolha a melhor de várias tentativas, não refaça resposta recebida.
8. **Fidelidade**: a nota de correção e a falha crítica medem a preservação dos fatos do pedido. O `delivery` do runner registra bloqueios mecânicos, mas não substitui os juízes.
9. **Congelado até a decisão**: skill, protocolo, juízes e plano não mudam durante o ciclo. Não ajuste a skill pelos votos.

## Falhas, empates e denominadores

- Resposta válida para o runner, mesmo ruim (só comandos, com preâmbulo), é julgada como veio e conta para o braço que a produziu.
- Resposta inválida para o runner (vazia, truncada, acima do limite) deixa o par incompleto e não é refeita, porque trouxe texto.
- Recusa válida de conteúdo pelo modelo é resposta do braço, não indisponibilidade: fica registrada e não é repetida.
- Chamada sem resposta não vira nota e nunca é repetida automaticamente. Timeout, erro HTTP ou de API e qualquer submissão ou cobrança ambígua bloqueiam novas chamadas, como no [RUNNER.md](results/scripts/RUNNER.md), até a evidência e o ledger da chave serem reconciliados. Só uma rejeição comprovadamente sem saída pode ter recuperação, expressamente autorizada, com o registro original preservado e a decisão congelada antes da repetição.
- Grupo de juízes com par incompleto não é julgado nem reagrupado.
- Empate de preferência não conta para nenhum braço, mas entra no total de votos. ΔH igual a zero não é ganho.
- Todo resultado mostra o denominador: pares julgados pelos três juízes sobre pares planejados, votos sobre o total de votos, falhas críticas sobre julgamentos.

## Decisão do ciclo

Pré-requisitos: testes de software passando e plano completo, com todos os pares planejados válidos nos dois braços e julgados pelos três juízes. Sem isso, o ciclo é **inconclusivo**, nunca aprovado.

Com o plano completo:

| Situação | Regra |
|---|---|
| **Aceita** | ΔH de pelo menos 5 pontos; ΔH positivo em pelo menos dois dos três juízes; votos da candidata em número maior ou igual aos da referência; falhas críticas da candidata em número menor ou igual às da referência |
| **Rejeitada** | ΔH menor ou igual a zero, ou mais votos para a referência, ou mais falhas críticas na candidata |
| **Inconclusiva** | qualquer outro caso, por exemplo ΔH entre 0 e 5 pontos |

Só a versão aceita vira referência. Rejeitada ou inconclusiva, a referência continua, e a candidata pode ser revista e testada num novo ciclo.

Compare candidata e referência só dentro do mesmo ciclo. Médias de rodadas diferentes, com outros geradores, pedidos ou datas, não medem evolução da skill.

Estas regras valem para os próximos ciclos. As tentativas anteriores continuam inconclusivas e não são reclassificadas.

## Ciclo de trabalho

1. Registre hipótese e mudanças em `results/reviews/X.Y.Z/README.md`.
2. Implemente e rode os [testes de software](results/README.md#testes-de-software). O agregador e o controlador usados até a 0.8.0 estão fora da árvore, no commit `a01d780`; restaure com o comando de [Pendências](results/README.md#pendências) e adapte ao plano, com testes, antes do passo 3.
3. Congele plano e pacote com `prepare`; registre commit e SHA-256 deste arquivo.
4. Execute o A/B sem mudar nada até o fim.
5. Decida pela tabela acima.
6. Ciclo aceito ou rejeitado: publique a rodada em `results/runs/AAAA-MM-DD-X.Y.Z/`, com `OBJETIVO.json`, `experiments/<pedido>/REPORT.md`, `README.md` e `SHA256SUMS`, e resuma o resultado em `results/README.md`. Ciclo inconclusivo: só uma linha na tabela de tentativas de `results/README.md`, com amostra, motivo da parada e local da evidência; nenhuma manchete de ganho.

O runner atual só usa o texto sem skill como referência. Depois da primeira versão aceita, adapte runner e agregador, com testes e antes de congelar o plano, para o braço de referência receber o pacote dessa versão.

## Arquivos

- Rodada publicada em `results/runs/` é evidência: não altere nem renomeie; o `SHA256SUMS` cobre cada arquivo.
- `results/scripts/fixtures/evidence-2026-10-13/` é a evidência bruta da tentativa de 13/10, mantida sem alteração como entrada dos testes do runner.
- Tentativas anteriores à 0.8.1 estão fora da árvore, no commit `a01d780`; veja [Histórico fora da árvore](results/README.md#histórico-fora-da-árvore).
