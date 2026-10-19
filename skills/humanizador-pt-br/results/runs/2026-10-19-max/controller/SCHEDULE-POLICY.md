# Política do controlador standalone

## Escopo

`schedule_run.py` muda apenas a ordem de execução. Usa `generation_eval.py`, `eval_store.py` e `eval_judges.py` de `ROOT/execution/frozen/runner`, com hashes iguais aos fontes vigentes e congelados em 19/10. Não importa o runner do repositório ativo nem modifica o freeze.

O conjunto permanece em 912 slots de geração, 456 pares e 432 chamadas de juízes. Payloads, prompts, modelos, reasoning, limites de saída, rubrica, IDs cegos e grupos são produzidos pelas funções originais. Não há reagrupamento.

## Ordem congelada

1. Para cada um dos 24 casos, executar o par r00, baseline e skill, seguido imediatamente pelos três juízes do singleton.
2. Executar as demais rotas por rota/caso: r01 a r14, r17, r18, r15 e r16.
3. Assim que todas as dependências de um grupo cego estiverem disponíveis, julgar o grupo pelos três juízes antes da próxima geração.
4. Se houver candidato terminal inválido, manter o grupo original sem julgamento. Não substituir nem reagrupar pares.

`execution/SCHEDULE.json` é publicado atomicamente, sem sobrescrita, antes de qualquer nova chamada. Contém hash do controlador, manifest, planos congelados, hashes dos payloads de geração, ordem completa de 1.344 eventos e dependências dos juízes. Payloads de juízes dependem das respostas futuras e são materializados em `judge-inputs/` antes de sua submissão. São rederivados e comparados na retomada.

Alterar controlador, manifest ou ordem após o congelamento bloqueia a execução. Não apagar o SCHEDULE para contornar o bloqueio.

## Entrada e comandos

`ROOT` contém `execution/` e `private/`. O controlador não prepara a matriz, não cria um execution ausente e não importa resultados antigos. A preparação da nova matriz é uma etapa separada.

Validar a preparação e congelar a ordem, sem chave ou API:

```sh
python3 -B /home/hermes/entregas/humanizador-avaliacao-0.7.0/schedule_run.py \
  --root /home/hermes/entregas/humanizador-avaliacao-0.7.0
```

Após preparação e autorização, executar apenas o piloto:

```sh
python3 -B /home/hermes/entregas/humanizador-avaliacao-0.7.0/schedule_run.py \
  --root /home/hermes/entregas/humanizador-avaliacao-0.7.0 --execute-paid --pilot
```

Retomar a matriz completa com `--execute-paid`, sem `--pilot`. Os slots terminais existentes são auditados e reaproveitados, inclusive um baseline produzido pelo piloto original. Não são reenviados ao Store.

`--max-new-calls N` estabelece uma fronteira opcional de novas chamadas por invocação. Não é teto monetário. `N=0` valida sem ler a chave e sem submeter chamadas. O controlador não impõe orçamento.

## Travas e evidência

- Mantém `.runner.lock` desde antes da validação até o fim da execução e dos relatórios, compatível com o lock do runner original.
- Valida inventário e hashes do manifest antes de importar código. Recalcula cobertura das probes, exige reconciliação separada e compara o mapa cego com o gerador original.
- Audita intent, raw, result, chamadas e payloads de candidatos e juízes. Rejeita artefatos desconhecidos no request store.
- Para imediatamente em qualquer status fora de `TERMINAL`, inclusive ao retomar. HTTP rejeitado, rota divergente e intent sem raw nunca são reenviados.
- `completed` e `invalid_response` são terminais no Store original. Respostas inválidas ficam preservadas, sem retry. Um raw terminal sem cache result pode ser rederivado sem nova chamada.
- Só a entrada explícita `--execute-paid` alcança `real_transport`. A chave de `private/inference-key.json` é lida em memória apenas diante da primeira nova chamada, após as auditorias. Não é colocada em argumentos, variável de ambiente, stdout ou relatórios.
- Não há fake na CLI. A injeção de transporte só é aceita com `offline=True` e marcador `offline_only=True`, usados pelos testes. `OFFLINE_FAKE` e `LIVE_API` não podem compartilhar registros.
- Cada nova chamada produz uma linha JSON de progresso com slot, fase, status e contagens, sem texto, payload ou segredo. `runtime-summary.json` é atualizado por chamada e ao terminar, mantendo os campos do runner original. Falhas da CLI expõem apenas a classe de erro, nunca seu conteúdo.

## Testes offline

```sh
cd /home/hermes/entregas/humanizador-avaliacao-0.7.0
python3 -B -m unittest -v test_schedule_run
```

A suíte copia somente o freeze e manifest preservados de 19/10 para `tempfile`, fora do Git. Bloqueia rede e leitura de `inference-key.json`. Exercita a matriz sintética completa, o renderer original, retomada sem duplicação, piloto original, igualdade de payloads e grupos, erros, intent incompleto, adulteração com hashes recalculados e separação de modos. Não representa execução de modelos.

A implementação foi conduzida em ciclos RED/GREEN para ordem, execução/retomada, auditoria de artefatos e CLI. Os testes adicionais cobrem os contratos do runner preservado.
