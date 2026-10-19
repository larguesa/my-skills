# Protocolo da avaliação 0.7.0

Revisão solicitada por Ricardo: Claude Code, Opus 5.5, esforço max. Avaliação posterior à implementação, com skill congelada antes de gerar respostas. Os resultados de 0.6.0 permanecem intactos.

## Comparação

- Mesmos 24 prompts aprovados em `results/PROMPTS.md`, sem acréscimos ao pedido.
- Mesmos 14 modelos, 19 configurações, provedores, controles de raciocínio e limites de saída do estudo anterior. 912 gerações planejadas, 456 pares e 432 chamadas de juízes.
- Baseline: mensagem `user` com pedido literal, contexto novo.
- Tratamento: `SKILL.md` 0.7.0 e retorno literal do comando `brief`, empacotamento `v2-brief`, seguidos do mesmo pedido literal. Sem respostas de outro braço, memória, instruções pessoais ou críticas anteriores.
- Juízes: Jev 1.13 nativo, Astra e Opus 5.5. Mesmas rubricas e formação de grupos; nova semente automática `humanizador-0.7.0-independent-v2-brief`.
- Uma geração por braço/configuração/pedido. Nenhuma seleção do melhor texto, edição de resposta ou ajuste da skill após olhar notas.

## Ordem diversificada, definida antes da execução

A ordem antiga parava no Qwen Flash do primeiro pedido e deixava os demais gêneros sem teste. Nesta execução, o controlador começa por r00 (Opus), ambos os braços, nos 24 pedidos, com os três juízes sobre o singleton anônimo de cada pedido. Depois percorre as demais configurações por rota e pedido, deixando r15/r16 (Qwen Flash) por último. Julga cada grupo assim que todos os seus pares estiverem completos.

A mudança é apenas de ordem. Slots, conjunto de payloads, grupos anônimos, modelos, rubricas e tamanhos da matriz são preservados. `SCHEDULE.json` registra ordem e hash do controlador antes da primeira chamada. O piloto usa o primeiro par e os três juízes; a continuação reutiliza esses cinco registros.

Não há repetição automática, substituição de modelo nem avanço após uma chamada ambígua. Qualquer falha não terminal interrompe novas chamadas; preserva-se o registro, reconcilia-se a chave e descreve-se a cobertura real. Respostas inválidas terminais permanecem nos registros e não são refeitas. Grupos incompletos não são reagrupados.

## Congelamento e contabilidade

`prepare` congela skill, catálogo, estilos, script, prompts, briefings locais, payloads, mapa anônimo e runner com SHA-256. Sondagens históricas aceitas são reutilizadas, com consulta atual da identidade e disponibilidade das rotas. Não são novas chamadas de sondagem.

Nova chave exclusiva, sem teto monetário conforme autorização de Ricardo. A gestão da chave e o saldo são consultados antes da inferência. Custos nativos de geração e julgamento, tokens, cache e latência são preservados e conciliados com o consumo da chave. Claude Code usa a assinatura Max, contabilizado separadamente; preço de tabela não é cobrança adicional comprovada.

## Estado observado após a execução

Matriz parcial, interrompida por indisponibilidade do Grok. Foram submetidas 117 gerações e 66 chamadas de juízes; [resultados e pendências](runs/2026-10-19-max/README.md). O protocolo congelado antes das chamadas permanece preservado na evidência privada.

## Resultado a apresentar

1. Humanização percebida H = 100 menos a impressão de IA do juiz. Média por configuração em pares com os três juízes; índices de percepção, não probabilidade de autoria.
2. Naturalidade e preferência geral, separadas de H.
3. Tokens totais de entrada e saída em pares completos. Raciocínio não é somado novamente.
4. Tempo das chamadas de geração nos mesmos pares, separado dos juízes e da preparação local.
5. Cobertura por pedido/modelo/modo e falhas, incluindo respostas que não entreguem texto.
6. Textos completos lado a lado, três colunas de detecção e justificativas por juiz.

A comparação com 0.6.0 é descritiva: versão, momento, semente e ordem diferem. Não se excluem resultados desfavoráveis.
