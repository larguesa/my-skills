# Humanizador PT-BR

Revisão editorial de textos em português brasileiro, com preservação factual antes de estilo. [Instruções para o agente](SKILL.md).

## Uso textual

Peça: "Audite este texto para clareza e repetição; preserve a voz e não altere o arquivo." Para reescrita: "Proponha uma versão revisada, preservando fatos, ressalvas e termos técnicos." Uma amostra autoral pode orientar a voz. Ausência de amostra não autoriza inventar uma personalidade.

O resultado distingue achados, exceções legítimas, sugestões e alterações autorizadas. Não há palavras proibidas, score de autoria ou promessa de escapar de detectores. A presença de robusto, significativo ou além disso não é defeito por si só.

## Conteúdo

- [SKILL.md](SKILL.md): procedimento e salvaguardas.
- [Catálogo](references/catalogo.json): regras originais, regex Python, contexto, exceções, exemplos e fonte.
- [Estilos](references/estilos.json): variação discreta dentro da voz fornecida.
- [Fontes](references/fontes.md): referências, dados candidatos, vieses e direitos.
- [Protocolo](references/protocolo.md): autorização, preservação, três braços de avaliação e calibração.
- [Exploração limitada](references/exploracao-amostral.json): observações reais de uma amostra de conveniência, sem comparação equilibrada entre classes.

`positive_example` indica uma ocorrência candidata à inspeção. `negative_example` ilustra ausência do gatilho, não uma troca factual pronta. Não transferir detalhes entre exemplos. `source` referencia IDs de fontes.md; `evidence: heuristica_editorial` não é resultado estatístico.

## Utilitários locais

Python 3, biblioteca padrão. O editor é portátil; o benchmark usa bloqueio de arquivo POSIX e requer Linux/macOS. Em Windows, usar o editor local e executar o benchmark no WSL ou em Linux. Na raiz do repositório, usar a ferramenta `terminal` com:

```text
python3 skills/humanizador-pt-br/scripts/humanizar.py --help
python3 skills/humanizador-pt-br/scripts/humanizar.py audit entrada.txt
python3 skills/humanizador-pt-br/scripts/humanizar.py suggest entrada.txt --profile neutro-claro --seed 17
python3 skills/humanizador-pt-br/scripts/humanizar.py verify entrada.txt revisado.txt
python3 skills/humanizador-pt-br/scripts/humanizar.py apply entrada.txt --plan plano-aprovado.json --output revisado.txt
```

Auditoria e sugestões não alteram a entrada. `apply` exige plano ligado ao SHA256 da entrada, offsets Unicode de início e fim exclusivo, trecho original exato, substituição e `approved: true` por edição. Aprovação é decisão editorial, não mudança automática do campo. Destino deve ser novo. Mesmo passando verificações mecânicas, revisar sentido e condições.

As regras autorizam apenas `audit` e `suggest`; não oferecem substituições globais. O campo `suggestion` é uma instrução editorial, não texto de reposição. A CLI carrega os quatro perfis de estilos.json e retorna `style_focus`, uma ênfase opcional sorteada com seed, sem trocar a voz nem os fatos.

O catálogo padrão fornece recomendações contextuais, não pares de substituição aprovados. Por isso, `suggest` pode retornar recomendações e `edits: []`. Para aplicar uma proposta revisada pelo editor, preencher um plano como abaixo. Os offsets são índices de caracteres Unicode, não bytes. No exemplo, a substituição só vale para a entrada literal `vale destacar: ação.` e ainda exige avaliação de contexto.

```json
{"input_sha256":"HASH_DA_ENTRADA_OBTIDO_NA_AUDITORIA","edits":[{"start":0,"end":13,"original":"vale destacar","replacement":"destaco","approved":true}]}
```

O editor bloqueia mudanças em trechos protegidos e não sobrescreve arquivos. A proteção é heurística: nomes sem maiúsculas, termos técnicos não cadastrados e mudanças de sentido fora desses trechos exigem revisão editorial. Usar `--protect "termo técnico"` para invariantes adicionais. Regex e estilos são recursos locais confiáveis, não aceitar catálogos arbitrários da web como código seguro.

## Benchmark e página de comparação

O runner não recebe memórias, SOUL.md ou contexto do Hermes. Carrega somente o pedido do caso, o original e, nos braços previstos, esta skill com catálogo e estilos. Os dois braços com skill recebem o mesmo material editorial; o terceiro acrescenta apenas a auditoria local compacta. Não há reescrita automática pelo script nem uma segunda rodada de modelo corrigindo a primeira saída.

Em Linux/macOS, via `terminal`:

```text
python3 skills/humanizador-pt-br/scripts/benchmark.py plan --availability resultados/disponibilidade --budget 10 --max-tokens 4096 --out resultados/plano.json
python3 skills/humanizador-pt-br/scripts/benchmark.py run --plan resultados/plano.json --state resultados/estado.json --execute-paid
python3 skills/humanizador-pt-br/scripts/benchmark.py report --plan resultados/plano.json --state resultados/estado.json --out resultados/comparacao.html
python3 -m unittest discover -s tests -v
```

`OPENROUTER_API_KEY` deve estar no ambiente, nunca no comando ou no repositório. Usar chave exclusiva com limite no provedor, conferir saldo e reservar no teto total os custos dos testes de disponibilidade. `plan` e `report` não fazem inferência paga. `--availability` lê registros reais de sondagens por modelo e rota; sem evidência, o modo desligado não é presumido. `--probe` permite solicitar modos ainda não verificados, não os certifica. IDs e preços em modelos.json são um snapshot, não disponibilidade permanente.

O orçamento considera custos observados mais a reserva conservadora da próxima chamada. A soma de reservas de todas as combinações não é uma previsão de gasto nem autoriza ultrapassar o teto. O runner salva a intenção antes do envio e não repete registros incertos. Após erro ou cobrança desconhecida, reconciliar a chave e o registro antes de decidir qualquer recuperação; não apagar estado para forçar tentativas.

A página principal mostra pedido, original, revisão e telemetria. A página `comparacao-blind.html` permite avaliação manual e exportação JSON, sem enviar dados a um servidor. O arquivo `comparacao-key.json` associa rótulos e identidades: não entregar aos avaliadores. Quem já leu a comparação identificada não participa de uma avaliação genuinamente cega dos mesmos textos.

Os casos padrão são sintéticos e públicos; o runner permite coleta de dados pelo provedor. Não usar esse fluxo para material confidencial sem autorização e revisão explícita da política. Nenhuma nota humana ou conclusão de superioridade é criada automaticamente.

## Evidência disponível

A amostra registrada contém apenas material `real` de `c4_pt`. O registro preserva hashes e contagens, sem republicar o texto. O grupo sintético não foi obtido nessa exploração. As observações não demonstram sobre-representação, autoria, eficácia editorial ou generalização a outros gêneros. Direitos das fontes continuam por auditar; ODC-By não é licença indiscriminada de todo conteúdo web.

Catálogo e protocolo estão implementados como recursos editoriais. Calibração empírica permanece pendente. Resultados de testes de software, piloto, custos e rankings devem ser relatados separadamente, somente quando efetivamente executados.

## Limites

Não inventar fatos para tornar texto concreto. Não adicionar opinião, experiência, humor ou erros para parecer humano. Não retirar qualificações científicas ou jurídicas para reduzir contagens. Não enviar documentos confidenciais a serviços externos nem publicar versões sem autorização.

Instalar copiando a pasta completa para o local de skills documentado pelo agente escolhido. Os arquivos usam referências relativas. Nenhuma outra skill é pré-requisito e este pacote não altera configurações de comunicação globais.
