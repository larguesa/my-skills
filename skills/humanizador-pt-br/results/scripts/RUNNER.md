# Runner da nova avaliação

Python 3 + stdlib/POSIX. Geração independente, não reescrita. Reuso do contrato de geração, rubrica e Jev Decisions do histórico `d14174698015e66f2c3814d0fe0110770509a242`, sem importar respostas históricas.

## CLI

Na raiz do repositório, substitua `<run-privado>` por um diretório novo fora de qualquer repositório Git. O pai deve concluir probes/reconciliação, revisar o código e só então preparar o freeze definitivo.

```sh
python3 skills/humanizador-pt-br/results/scripts/generation_eval.py prepare \
  --output <run-privado> \
  --history /home/hermes/entregas/humanizador-pt-br/expansao-20261002/private-raw/config-run.json \
  --catalog /home/hermes/entregas/humanizador-avaliacao-2026-10-10/catalog-live.json \
  --endpoints /home/hermes/entregas/humanizador-avaliacao-2026-10-10/endpoints-live.json \
  --amendments /home/hermes/entregas/humanizador-avaliacao-2026-10-10/route-amendments.json \
  --probe-dir /home/hermes/entregas/humanizador-avaliacao-2026-10-10/private/probes \
  --probes-accounting /home/hermes/entregas/humanizador-avaliacao-2026-10-10/probes-accounting.json

# Chamadas pagas: apenas após revisão/autorizações do controlador.
# A chave deve estar no ambiente do processo; não entra em arquivos/payloads.
python3 skills/humanizador-pt-br/results/scripts/generation_eval.py run \
  --root <run-privado> --execute-paid --pilot --max-new-calls 5

# Reutiliza os cinco slots do piloto, sem POST duplicado.
python3 skills/humanizador-pt-br/results/scripts/generation_eval.py run \
  --root <run-privado> --execute-paid

python3 skills/humanizador-pt-br/results/scripts/generation_eval.py render \
  --root <run-privado> --reports skills/humanizador-pt-br/results
```

`prepare`/`render` não fazem chamadas de rede. `run` é sequencial; `--pilot` executa somente as duas gerações do primeiro caso/configuração e seus três juízes, com IDs idênticos aos da matriz completa. `--max-new-calls` é limite de fronteira operacional, não monetário; uma interrupção por essa fronteira retorna código 2 e permite continuar apenas slots ainda não iniciados. Nenhum teto financeiro é implementado.

## Freeze e segurança de retomada

- Matriz corrigida: 24 casos, 19 configurações, **14 IDs de modelo**, 912 gerações, 432 chamadas de juízes, 1368 julgamentos de pares, 2736 escores de impressão. Não adiciona versões/modelos.
- Baseline: única mensagem `user`, conteúdo literal extraído de PROMPTS.md. Tratamento: mensagens `system` contendo exatamente SKILL.md 0.5.1 e JSONs integrais; mais retornos locais de catalog/styles/structure, calculados e congelados por caso. Mesma mensagem `user`. Nenhuma resposta de outro braço, memória ou feedback entra nos candidatos.
- Snapshot das fontes, seleção local, payload hashes, mapa anônimo e grupos fixos, histórico, catálogo/endpoints, amendments, probes e código. Hash divergente bloqueia execução. Prepare exige diretório novo; não sobrescreve freezes.
- Amendments explícitos podem trocar só provider do mesmo modelo/versão/modo. Os originais ficam preservados. Não há fallback. O Jev 1.13 nativo não aparece no catálogo `/models`; sua identidade usa o endpoint datado exato, sem substituir pelo Jev Router.
- Lock não bloqueante cobre execução inteira. Cada intent é publicado atomicamente e fsyncado **antes** do POST. Raw HTTP exato fica em base64 dentro de envelope imutável; cache derivado é comparado novamente ao raw.
- Intent sem raw, timeout, erro HTTP/API, uso/custo nativo ausente ou rota retornada divergente bloqueiam todas as novas chamadas. Não existe opção de retry nem recuperação automática desses intents. Reconciliação/decisão do controlador precisa ser externa e documentada; não apague intents para continuar.
- Se apenas o cache faltou mas raw/intent estão completos, ele é reconstruído sem POST. Respostas inválidas, vazias, truncadas ou recusadas ficam preservadas e não são reenviadas. Grupos inválidos não são reagrupados.
- Raw é privado e não sanitizado para preservar bytes: pode conter infraestrutura/segredo refletido pela API. Não publique o run inteiro. Renderer projeta textos/escores auditados, não bodies de erro. Revise a projeção antes de publicar.
- Probes precisam cobrir cada modelo/modo/provider efetivo, inclusive Jev. `run` bloqueia sem probes completos e recibo separado com ledger_reconciliation diferente de pending/unknown/ausente.

## Relatórios e limites

`SUMMARY.md`/`SUMMARY.json`: agregado por juiz/configuração, denominadores, deltas e preferências. `experiments/<caso>/REPORT.md`: prompt literal, textos completos lado a lado e colunas Jev/Astra/Opus. Cópias UTF-8 dos candidatos em `outputs/` preservam bytes. `TELEMETRY.json`: tokens, cache read/write, custos e tempos, separados de probes; desconhecidos ficam null, não zero. A contabilização não interrompe por gasto.

Impressão de IA não prova autoria nem é probabilidade calibrada. Menor impressão não equivale a maior qualidade. Votos dos três juízes sobre o mesmo texto não são experimentos independentes. Alias retornado não comprova a versão; zero reasoning tokens não comprova ausência/presença da computação solicitada. Jev usa o payload histórico Decisions sem max_tokens artificial; chat candidates usam 4096 e chat judges 16384.

## Testes offline portáteis

```sh
python3 -m unittest discover -s skills/humanizador-pt-br/results/scripts -p test_generation_eval.py -v
```

Fixtures em `fixtures/` são projeções de metadados históricos/live reais, com proveniência; não contêm respostas de API. O arquivo de probe de teste é explicitamente OFFLINE_FIXTURE_NOT_API_EVIDENCE e não satisfaz cobertura. FakeOfflineTransport só existe nos testes, marcado offline_only; uso de chave ou mistura de LIVE_API/OFFLINE_FAKE é rejeitado. A matriz fake testa persistência/coverage/renderização, nunca desempenho de escrita nem custos reais.

Integração opcional com metadados reais usa HUM​ANIZADOR_HISTORY, HUMANIZADOR_CATALOG, HUMANIZADOR_ENDPOINTS, HUMANIZADOR_AMENDMENTS e HUMANIZADOR_PROBES (nomes ASCII: HUMANIZADOR_HISTORY etc.). Os testes continuam offline. Nenhuma chave é necessária.
