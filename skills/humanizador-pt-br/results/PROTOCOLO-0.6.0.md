# Protocolo de avaliação do Humanizador PT-BR 0.6.0

Estado atualizado após a execução de 19/10/2026: **matriz parcial**, interrompida por limite temporário do Qwen Flash. Foram preservadas 31 respostas completas e 27 julgamentos sobre 9 pares. Consulte [resultados e evidências](runs/2026-10-19/README.md). Os parâmetros e payloads preparados antes das chamadas permanecem no snapshot congelado; esta atualização do documento altera somente a informação de estado. O congelamento é o `manifest.json` produzido por `prepare`, com SHA-256 de `SKILL.md`, catálogo, estilos, script, prompts, briefings por caso, plano de payloads, mapa anônimo e código do runner. Não é preciso commit antes do teste; o commit pode vir ao final, e os arquivos versionados devem coincidir com os hashes do manifest. A [revisão](REVISAO-2026-10-19.md) descreve o que mudou e por quê. O [protocolo de 10/10](PROTOCOLO.md) continua válido para os resultados de 0.5.1.

## O que muda e o que fica igual

- Pedidos: os mesmos 24 de [PROMPTS.md](PROMPTS.md), literais e sem orientação nova.
- Baseline: somente a mensagem `user` com o pedido literal. O teste `test_v2_brief_is_opt_in_compact_and_keeps_baseline_literal` confirma que as 456 chamadas de baseline são idênticas às do modo v1.
- Tratamento, modo `v2-brief`: uma mensagem `system` com `SKILL.md` 0.6.0, uma mensagem `system` com o retorno literal de `humanizar.py brief` para o perfil e o gênero fixos do caso, e a mesma mensagem `user`. Os JSONs integrais deixam de ser injetados. Os seletores de perfil e gênero são os mesmos de 13/10, definidos antes de qualquer geração.
- Nenhuma ferramenta é oferecida aos candidatos. A skill instrui que, sem terminal ou com os retornos já no contexto, o modelo não escreva comandos e entregue o texto.
- Matriz: 14 modelos, 19 configurações, 912 gerações, 432 chamadas de juízes (Jev 1.13 nativo, Astra e Opus 5.5), mesmos grupos de até quatro pares. A semente de anonimização muda para `humanizador-0.6.0-independent-v2-brief`.
- Sem teto monetário, sem repetição automática, sem reagrupamento. As exigências de sondagem e reconciliação do runner continuam: `run` recusa iniciar sem sondagens completas e contabilidade reconciliada.

Tamanho do tratamento sem o pedido, em caracteres: 62.958 a 63.307 no modo v1 de 13/10; 18.915 a 19.080 no modo v2 (média 69,9% menor). São caracteres medidos localmente, não tokens; a contagem de tokens virá das respostas da API.

## Comandos do controlador

Na raiz do repositório, com `<run-0.6.0>` novo e fora de qualquer repositório Git. Os argumentos de histórico, catálogo, endpoints, emendas e sondagens seguem o [RUNNER.md](scripts/RUNNER.md).

```sh
python3 skills/humanizador-pt-br/results/scripts/generation_eval.py prepare \
  --output <run-0.6.0> --packaging v2-brief --skill-version 0.6.0 \
  --history <history.json> --catalog <catalog.json> --endpoints <endpoints.json> \
  --amendments <route-amendments.json> --probe-dir <probes> --probes-accounting <probes-accounting.json>

python3 skills/humanizador-pt-br/results/scripts/generation_eval.py run \
  --root <run-0.6.0> --execute-paid --pilot --max-new-calls 5

python3 skills/humanizador-pt-br/results/scripts/generation_eval.py run \
  --root <run-0.6.0> --execute-paid

python3 skills/humanizador-pt-br/results/scripts/generation_eval.py render \
  --root <run-0.6.0> --reports <relatorio-novo>

python3 skills/humanizador-pt-br/results/scripts/generation_eval.py delivery \
  --root <run-0.6.0> --output <relatorio-novo>/DELIVERY.json \
  --checker <run-0.6.0>/frozen/skill/scripts/humanizar.py
```

Qualquer alteração posterior no runner ou nos arquivos congelados bloqueia `run` por divergência de hash. `delivery` usa o `humanizar.py` congelado no run, confere manifest, config, plano de payloads, mapa anônimo e intent/raw/result sem escrever na fonte, e recusa destino dentro da raiz do run, inclusive por symlink.

## Métricas

1. Humanização percebida H = 100 menos a impressão de IA, por par com três juízes, com as mesmas definições do [relatório de 13/10](runs/2026-10-13/OBJETIVO.md).
2. Tokens: prompt mais completion, razão das somas em pares completos; reasoning não é somado.
3. Tempo da chamada de geração em pares completos.
4. Entrega: `delivery` aplica `humanizar.py check` a cada texto completo, com o pedido literal como briefing. Conta, por braço, saídas só com comandos, chamadas de ferramenta, preâmbulo e travessão fora de código ou citação fechados. Os 24 pedidos são de prosa; o contrato `--artifact codigo` não é usado. Alertas de números e datas são descritivos.

Saídas bloqueadas permanecem em todas as métricas, sem reparo, exclusão ou reenvio. Comparação com 0.5.1 é apenas descritiva: data, semente de anonimização e pacote de tratamento diferem.

## Regras de interpretação

- A skill 0.6.0 fica congelada durante a execução. Não há ajuste por voto de juiz.
- Uma geração por braço e configuração; três juízes sobre o mesmo texto não são três experimentos.
- Matriz parcial vale só para os casos e configurações observados; ausências não valem zero.
- Avaliação humana continua pendente e não é substituída pelos juízes.
