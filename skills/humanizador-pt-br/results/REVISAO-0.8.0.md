# Revisão 0.8.0 (19/10/2026)

Pedido de Ricardo: consolidar e implementar as sugestões relevantes de três revisões independentes da versão 0.7.0 (commit-base `4433074e32085320c9cebc8ebace67833e321f92`): Codex CLI com `openai/gpt-6-astra` xhigh, `x-ai/grok-4.7` xhigh e `xiaomi/mimo-v2.6-pro` sem raciocínio. Cada achado foi lido como hipótese do revisor; os de comportamento foram reproduzidos no código antes de qualquer decisão. Escopo: `skills/humanizador-pt-br` (exceto `results/runs`, `results/PROMPTS.md` e `results/scripts`, congelados) e as menções à skill no README raiz e em `skills/index.md`. Durante a etapa de implementação, o Claude não fez chamadas externas adicionais, pesquisa, commit ou envio. Os relatórios completos e a proveniência das três revisões, arquivados pelo controlador, estão em [reviews/0.8.0](reviews/0.8.0/README.md).

Estado: implementação e validação offline concluídas. A verificação independente confirmou 117 testes aprovados e 11 reproduções corrigidas. O teste funcional de redação produziu cinco textos e uma recusa do provedor, conforme a seção abaixo.

## Decisões por achado

Legenda: **aceito**, **parcial**, **rejeitado** ou **adiado**. "Reproduzido" indica falha observada no commit-base com o caso citado.

### Codex

| Achado | Verificação | Decisão |
|---|---|---|
| 1. Literais divergentes entre edição e entrega | Reproduzido: em ` ``vale destacar`` ` e numa cerca de quatro crases com três no interior, `replace` propunha edição; `check` bloqueava travessão (U+2014) entre aspas curvas simples e entre aspas retas que atravessam linha, trechos que a edição protegia. | **Aceito.** `literal_spans` passa a ser o único reconhecedor: crases inline fecham com sequência do mesmo tamanho; cerca fecha com o mesmo caractere e comprimento igual ou maior; aspas retas, curvas, simples e angulares fecham no mesmo parágrafo (aspas retas simples na mesma linha, sem confundir apóstrofo). Trecho aberto é protegido na edição e não isenta nada na entrega. Código indentado: **adiado**, porque em Markdown se confunde com continuação de lista e nenhuma falha foi reproduzida. |
| 2. Aspas não provam origem | Reproduzido: uma fala nova entre aspas curvas, com U+2014, era entregável num pedido de diálogo novo. | **Aceito.** Travessão fora de código só passa se a citação estiver no pedido ou no original, se o nome que o contém (um código com U+2014 entre letras) estiver na fonte, ou, com `--original`, se a frase inteira for mantida do texto do usuário. Prosa do pedido copiada não prova nada. |
| 3. Pares Evite/Prefira acrescentam fatos | Confirmado por leitura: 22 formas preferidas traziam dado, alcance ou certeza ausentes do vício. | **Aceito.** 24 pares reescritos: o fato fica nos dois lados e a forma preferida só retira o vício (PTBR-03 com "às 18h" nos dois; PTBR-13 conserva "poderia"; PTBR-32 usa "tratar do problema", não "corrigir"). PTBR-31 continua ilustração de criação ficcional, com a chaleira já na cena e orientação "em relato real, fique no que aconteceu". `meaning_risk` de PTBR-29 e PTBR-32 passa a médio. |
| 4. Briefing em texto sem orientação e exceções | Reproduzido: 0 de 32 orientações e 0 exceções chegavam ao texto. | **Aceito.** Regras de foco trazem orientação (`Como`) e exceção (`Salvo`); as demais trazem termos e exceção. A condição de PTBR-04 ("ocorrência isolada") virou exceção explícita. |
| 5. Detector de saída só com comandos | Reproduzido: `ls`, `curl https://...` e JSON passavam; `Execute:` com `ls -la` em cerca era bloqueado. | **Parcial.** Comando sem argumento e mais executáveis contam; JSON puro bloqueia (`saida_somente_json`); comando dentro de cerca fechada é documentação e não conta, salvo chamada da própria skill (`humanizar.py`). Marcação de ferramenta continua contando mesmo em cerca, porque é o modo de falha documentado em 13/10; pedido que quer a marcação como artefato usa `--artifact codigo`. O limiar de oito palavras fica restrito a comandos fora de código. |
| 6. Preâmbulo | Reproduzido: `Seguem os documentos:` bloqueava; `Claro!` seguido de `Aqui está a notícia:` passava; preâmbulo em negrito não era detectado. | **Aceito.** Bloqueia o anúncio do próprio artefato ("aqui", linha sem complemento ou complemento como texto, versão, revisado, notícia), também depois de linha de cortesia e com marcação Markdown. Introdução de anexo ou lista gera alerta. |
| 7. Instruções de redação aplicadas à revisão e ao diagnóstico | Confirmado por leitura (fluxo e contrato de entrega). | **Aceito.** Linha de entrega com uma instrução por modo; SKILL.md com revisão no escopo pedido, frases que já funcionam preservadas e diagnóstico sem versão nova; exceção apontada no diagnóstico, não no texto entregue. `brief --mode`: **rejeitado**, porque uma linha fixa serve aos três usos sem nova opção de CLI. |
| 8. Política factual divergente | Confirmado: SKILL.md aceitava fato verificado e o briefing restringia ao pedido. | **Aceito.** Mesma regra nos dois: pedido, texto-base ou fonte verificada nesta tarefa, com atribuição; conceito geral pode ser explicado; exemplo numérico didático entra como hipótese; "não divulgado" só quando o material disser. |
| 9. Números e datas | Reproduzido: sinal e percentual perdidos; `domingo` casava dentro de `Domingos`. | **Aceito.** Números com sinal, percentual e ordinal, fora de blocos de código; datas comparadas por palavra inteira. Contagem de repetições: **rejeitada**, porque repetir número em título e lide é normal. |
| 10. NFD e abreviações | Reproduzido: `não aceito.` e `se o sr. pedir, aceite.` permitiam editar a oração. | **Aceito.** Negações e condições são buscadas numa forma sem acento com mapa de offsets; ponto de abreviação e pontuação dentro de literal não encerram a oração. |
| 11. Termos declarados não detectados | Reproduzido: "endereçar um problema", "otimizamos", "potencializamos". | **Aceito.** Regex de PTBR-11 e PTBR-32 ampliadas por flexões usuais; termos de PTBR-30 e PTBR-24 reescritos para serem detectáveis; teste exige detecção de cada termo declarado, exceto os esquemáticos. |
| Estruturas categóricas | Confirmado por leitura nos oito planos citados. | **Aceito.** Reportagem atribui sem exigir aspas; e-mail cumprimenta pelo nome só quando o pedido o traz; post cobre relato, opinião e anúncio; roteiro separa vídeo de fala sem tela; acadêmico segue a seção pedida e não exige método empírico em texto teórico; conto aceita narrador onisciente e prosa introspectiva; crônica usa a pessoa narrativa do pedido e humor só quando cabe; proposta não cria responsável pelo aceite. |
| `tecnico-preciso/email` recusado | Reproduzido. | **Aceito.** `email` entra no perfil com o plano `mensagem`; o padrão sem gênero continua `procedimento`. |
| `argumentativo-sobrio/post` usa `argumento` | Reproduzido. | **Parcial.** O plano de opinião continua (material de opinião é o adequado), agora chamado "Artigo ou post de opinião", com instrução de formato para post. Seleção explícita de estrutura por CLI: **adiada**, por ser arquitetura nova. |
| "Vícios mais comuns neste gênero" | Confirmado: não há frequência medida por gênero. | **Aceito.** "Pontos de atenção do gênero". |
| Estratégia de testes | Leitura. | Teste lexical da forma preferida sem vício: **mantido**, exceções legítimas têm testes próprios. Tetos de tamanho: **mantidos como guarda**, recalibrados e ancorados no limite congelado do runner. Contratos entre componentes, casos sintéticos fora dos 24 pedidos e controles antigos: **aceitos**. |

### Grok

| Achado | Verificação | Decisão |
|---|---|---|
| P0. Pares que ensinam a inventar e briefing sem orientação | Mesmo achado de Codex 3 e 4. | **Aceito** (ver acima). O teste novo segue a proposta: nenhum número, mês, dia, palavra numérica ou quantificador novo na forma preferida, e palavras novas só de uma lista explícita de substitutos linguísticos (há, também, além, da, do, para, é, pagar, tratar). |
| P0. Data relativa sem alerta | Reproduzido: "nesta quinta", "na terça", "próxima sexta", "esta semana", "semana que vem", "terca-feira" e "sabado" passavam. | **Aceito**, sem marcar "na segunda etapa" nem "na quinta série". |
| P0. Literais e `--original` | Reproduzido (aspas simples, multilinha, angulares). | **Aceito.** Segunda linha de citação sem `>`: **rejeitada**, porque em texto simples a linha seguinte nem sempre é citação; com `--original`, a frase mantida já é comprovada. Aspas abertas protegem até o fim do parágrafo, não do arquivo. |
| P0. Modos no contrato de entrega | Mesmo achado de Codex 7. | **Aceito.** |
| P1. Proteção excessiva em `apply` | `O caso foi arquivado` recusado: reproduzido. Substituição com maiúscula recusada: reproduzido. `1º` sem `º`: reproduzido. | Ordinal: **aceito** (`º`, `ª` e `°` fazem parte do número). Reduzir `se`, `caso`, `sem`, `salvo` e `nem` ao próprio token: **rejeitado**, porque enfraquece a proteção de condições reais; a recusa por homonímia é o comportamento conservador documentado. Retirar a verificação prévia da substituição: **rejeitado**, porque o inventário recusaria a mesma edição. |
| P1. Comando curto em cerca bloqueado | Reproduzido. | **Aceito** (ver Codex 5). |
| P1. Detectores largos ou cegos | Reproduzido em PTBR-20, 24, 29, 11 e 06. | **Aceito.** PTBR-20 só quando o rótulo se repete no item; PTBR-24 exige vírgula ou dois-pontos depois de "para concluir"; PTBR-29 sem "clara", "simples", "segura" e "prática"; PTBR-06 aceita "recentes", "científicos" e "internacionais" e quantificadores, sem marcar "Estudos do instituto mostram". "Robusto" isolado: **rejeitado**, porque exigiria exceções técnicas no detector; a lista explícita da SKILL.md continua e a exceção técnica agora chega ao briefing. "Jornada": mantida na lista, com "jornada de trabalho" entre os usos literais. |
| P1. Blocos que pedem material ausente | Confirmado por leitura. | **Aceito** (ver estruturas). |
| P2. Números em código, offsets, meia-risca, eco | Leitura e reprodução (404 em cerca alertava). | Números fora de código: **aceito**. Offsets da omissão: **aceito** na documentação (`source: briefing` já existia). Meia-risca sem glifo no briefing: **aceito** (PTBR-28 passa a exemplo descrito, como PTBR-21). Meia-risca como bloqueio: **não alterado**, como o próprio revisor recomendou. Alerta de eco do pedido: **adiado**, porque gera ruído em frases factuais que devem ser preservadas e dependeria de detectar o modo em `check`. |
| Melhorias editoriais | Leitura. | Título no presente sem mudar a data, ritmo de 130 a 150 palavras como referência de cálculo, pergunta ensaística como exceção de PTBR-25, cabeçalho com a contagem das demais regras e `suggest` documentado: **aceitos**. Mapa de perfis e gêneros: **parcial**, no README, porque a SKILL.md está no limite de tamanho do runner. "Em resumo do relatório": **rejeitado**, risco baixo e sem caso observado. Alerta de acentuação: **adiado**, sem falha observada. |

### MiMo

| Achado | Verificação | Decisão |
|---|---|---|
| P1. Polaridade invertida em `brief()` | Não reproduzido: `positive_example` é o vício detectado e vira "Evite"; o teste de 0.7.0 confirma a ordem. | **Rejeitado** como descrito. A preocupação de fundo, forma preferida com fato novo, foi **aceita** (Codex 3). |
| P2. `approved=True` interno em `suggest` | Leitura: toda edição volta com `approved: false` antes do retorno. | **Rejeitado.** Sem caminho que exponha aprovação; refatorar não muda comportamento. |
| P3. Siglas tratadas como possível nome | Reproduzido (`API` não editável). | **Rejeitado.** Trocar sigla técnica viola "Sinônimos aleatórios para termos técnicos"; opção para relaxar convidaria a contornar a proteção. |
| P4. Travessão do original bloqueado na revisão | Reproduzido. | **Aceito** com `--original`, que comprova a frase mantida, em vez de um modo que rebaixaria todo travessão. |
| P5. `--accept-rule` | Leitura. | **Rejeitado.** Alertas de catálogo não bloqueiam; suprimi-los esconderia leitura. O conflito entre "sinalize a exceção" e "sem bastidores" foi resolvido na SKILL.md. |
| P6. `material` e `material_types` | Leitura. | **Rejeitado** como reestruturação: os mapas têm papéis distintos (padrão e regra condicional) e testes dependem deles. Redação harmonizada com a política factual. |
| P7. Regra sem `avoid` | Leitura. | **Rejeitado.** Catálogos externos sem termos continuam válidos para `audit`; o catálogo oficial já é testado. |
| P8. Omissão de nomes e condições | Leitura. | **Adiado.** Heurística por maiúscula marcaria inícios de frase e verbos do pedido; números e datas já são comparados. A comparação de citações do pedido fica como ideia registrada. |
| P9. Ordem dos protegidos em `verify` | Reproduzido (inventário igual com nomes trocados). | **Rejeitado.** Reordenar é edição legítima comum; `verify` já devolve as diferenças e pede revisão semântica. |
| P10. Aberturas em `rhythm` | Não reproduzido: o próprio exemplo não gera repetição. | **Rejeitado.** |
| E1 a E5 | Leitura. | Modos (E1) e `suggest` no README (E2 e E4, sem campo novo no JSON): **aceitos**. Exceções por perfil (E3) e material herdado (E5): **rejeitados**, porque alertas não bloqueiam, PTBR-31 já excetua paródia e estruturas de opinião e ficção divergem do padrão. |

## Correções implementadas

| Arquivo | Mudança |
|---|---|
| `scripts/humanizar.py` | `VERSION` 0.8.0. `literal_spans` compartilhado por `protected_spans`, `verify`, `apply` e `check`. Negação e condição em forma sem acento com mapa de offsets; abreviações e literais não encerram a oração; ordinal e grau no número. `check`: origem do travessão (citação, nome ou frase do original), `--original`, `saida_somente_json`, comandos fora de código, preâmbulo após cortesia ou em Markdown, números com sinal, percentual e ordinal fora de código, datas relativas ampliadas e comparadas por palavra inteira, `original_sha256` e `motivo` em `travessao_protegido`. `brief_text`: pontos de atenção com orientação e exceção, exceção de todas as demais regras, exemplo em uma linha, sem a linha de invariantes (presentes no JSON e na SKILL.md). Contrato de entrega por modo. |
| `references/catalogo.json` | 24 pares reescritos, exceções condensadas e completas, orientações mais curtas, regex de PTBR-06, 11, 20, 24, 27, 29 e 32, termos detectáveis em PTBR-06, 24 e 30, PTBR-28 descrita sem glifo, risco médio em PTBR-29 e 32. |
| `references/estilos.json` | 1.3. E-mail em `tecnico-preciso`; plano de opinião para artigo e post; ofício e blocos condicionados ao material em explicação, mensagem, post, roteiro, reportagem, proposta, acadêmico, conto, crônica e notícia; política factual unificada. |
| `SKILL.md` | 0.8.0. Modos no fluxo, política factual unificada, lacuna só quando sustentada, exceção no diagnóstico, `--original` e bloqueios atualizados. Lista de vetos, 12 perfis e validação final literal preservados. |
| `results/test_humanizar.py` | 18 testes novos em sete classes; seis testes antigos ajustados ao contrato 0.8.0, um deles renomeado. |
| Documentação | README da skill, README raiz, `skills/index.md`, `results/README.md`, `VALIDACAO.md` e este relatório. Revisões e protocolos anteriores preservados. |

Testes antigos ajustados, com motivo: travessão entre aspas agora exige fonte (`test_em_dash_in_quotes_or_code_is_reported_without_blocking`); PTBR-28 entrou no conjunto de exemplos descritos; cabeçalho "Pontos de atenção do gênero"; versão 0.8.0 e tetos de 9.100 caracteres para a SKILL.md e 11.500 para o briefing; o teste "menor que 0.6.0" virou `test_treatment_fits_the_frozen_runner_budget`, com o limite do runner.

## Testes executados

Comandos equivalentes aos listados, executados com caminhos absolutos; saída completa conferida, sem filtros.

| Etapa | Antes da implementação | Depois |
|---|---|---|
| Commit-base | 69, 15 e 15 testes OK nas três suítes | |
| Regressões novas | 18 testes, todos falhando: 81 falhas de subteste e 1 erro (`Gênero incompatível` em `tecnico-preciso/email`) | |
| Literais e proteções na edição | 3 testes novos falhando | 24 OK (`Literal080`, `Protection080`, `EditorTests`, `ReplacementTests`) |
| `check` | 8 testes novos falhando | 38 testes, 2 falhas: preâmbulo em negrito (dependia da regex de PTBR-27) e o teste antigo de travessão entre aspas sem fonte, ajustado ao contrato novo |
| Catálogo | 2 testes novos falhando | 24 testes, 1 falha no teste antigo que exigia o glifo de PTBR-28; ajustado |
| Briefing, estilos e SKILL.md | 5 testes novos falhando | suíte completa com 87 testes: 76 falhas e 37 erros de subteste em quatro testes antigos presos à 0.7.0 e 1 falha de versão do README; depois dos ajustes e da documentação, 87 OK |

Execução final, depois de todas as alterações de código, dados, testes e documentação:

| Comando | Resultado |
|---|---|
| `python3 -W error skills/humanizador-pt-br/results/test_humanizar.py` | 87 OK |
| `python3 -m unittest discover -s skills/humanizador-pt-br/results/scripts -p test_generation_eval.py` | 15 OK |
| `python3 -m unittest discover -s skills/humanizador-pt-br/results/runs/2026-10-13/analysis -p test_objetivo.py` | 15 OK |
| `git diff --check` | sem apontamentos |

Compatibilidade: assinatura `check(text, rules, briefing)` mantida para o runner; `delivery` sobre a evidência de 13/10 continua com 11 e 12 respostas entregáveis e os mesmos conjuntos de bloqueio (comandos, preâmbulo e travessão). Nos textos de 13/10, nenhum travessão estava em código ou entre aspas pelo reconhecedor anterior, e os conjuntos de bloqueio fixados pelos testes continuam idênticos com o novo. Mudança deliberada: travessão entre aspas sem pedido ou original informados agora bloqueia. Alertas de 0.8.0 não são comparáveis aos de 0.7.0.

Tamanho do tratamento sem o pedido, em caracteres: 0.7.0, de 16.050 a 16.613 nos pares do runner; 0.8.0, de 18.971 a 19.421 (SKILL.md com 9.007 e briefing de 9.964 a 10.414), abaixo do limite congelado de 19.540 (40% de 48.850). Entre os 37 pares perfil/gênero, o maior tem 20.108 (`caricato/roteiro`). O acréscimo vem das exceções e orientações do catálogo; para caber, foram condensadas frases que repetiam a ressalva geral e retirada a linha de invariantes do texto. Caracteres, não tokens.

## Teste de redação

Após a consolidação, o controlador executou seis pedidos já aprovados com MiMo 2.6 Pro, sem raciocínio. Cinco produziram texto completo e passaram no verificador mecânico; a documentação de API foi recusada por limite temporário. A leitura editorial encontrou imprecisão temporal, analogia inadequada, acréscimos não fornecidos e problemas de linguagem e continuidade. Textos preservados, observações, tempos e custos no [relatório funcional](reviews/0.8.0/SMOKE.md). Não houve reescrita dos resultados nem comparação A/B. A matriz anterior permaneceu inalterada.

## Hipóteses editoriais a medir

1. Formas preferidas sem fato novo reduzem acréscimos de dado, fonte e alcance.
2. Exceções no briefing reduzem aplicação excessiva (conector isolado, quadro de serviço, termo técnico, pergunta ensaística).
3. A instrução por modo reduz reescrita desnecessária em revisões.
4. Blocos condicionados ao material reduzem aspas, nomes e números inventados.
5. O tratamento de 17% a 18% maior que o da 0.7.0 pode aumentar custo e diluir atenção.

## Riscos que pedem decisão

1. O tratamento ocupa 99,4% do limite do runner no par mais longo; nova instrução exigirá corte equivalente.
2. Com `--original`, mexer numa frase com travessão exige retirar o travessão dela; citação abreviada ou parafraseada com travessão bloqueia.
3. Comando dentro de cerca fechada deixa de contar como saída de comandos; o modo de falha observado (chamadas de ferramenta cruas e comandos da skill) continua bloqueado.
