A revisão é estática: não executei o script, a suíte nem os textos de `results/runs`. Nada abaixo pede alteração de histórico, dos 24 prompts, de nota de juiz ou corte de regra para caber em token. Os 12 perfis, o catálogo efetivo, redação ou revisão, prosa sem travessão e a validação final literal devem permanecer.

## Achados prioritários

### P0. Os pares Evite/Prefira ensinam a inventar fato, e o briefing esconde a instrução que mandaria não inventar

Evidência, não hipótese. Em `brief()`, o exemplo detectado como vício vira “Evite” e o exemplo “bom” vira “Prefira”:

```377:380:skills/humanizador-pt-br/scripts/humanizar.py
compact = [{'id': r['id'], 'name': r.get('name', ''), 'foco': r['id'] in focus,
            'evite': r.get('positive_example'), 'prefira': r.get('negative_example'),
            'como': r.get('suggestion'), 'termos': r.get('avoid', []),
            'excecoes': r.get('exceptions', [])} for r in rules]
```

`brief_text()` imprime Evite/Prefira/termos e não usa `como` nem `excecoes` (`scripts/humanizar.py`, linhas 416 a 427). O formato padrão da CLI é texto (`linha 553`). O caminho recomendado pela skill é esse briefing. O JSON, que tem sugestão e exceção, só sai com `--format json`. As duas rotas não fazem “a mesma seleção” (`SKILL.md`, linhas 59 a 66).

A sugestão de PTBR-06 diz para não inventar fonte. O Prefira inventa fonte, magnitude e mês (`references/catalogo.json`, linha 7). O mesmo briefing de notícia também imprime o veto do perfil “Aspas inventadas” e “Autoridade vaga” (`references/estilos.json`, linhas 152 a 156) e, mais perto do pedido, o Prefira fabricado. O ofício acadêmico diz “Não invente referências” (`estilos.json`, linha 1034) e o foco acadêmico mostra o mesmo par.

Receita que falha, por regra. “Acrescenta” significa dado, fonte, data, número, causa ou objeto que não está no vício.

| Regra | Veredito |
|---|---|
| 01, 04, 14, 18, 20, 28, 30 | Preservam. 30 já foi o modelo certo. 32 troca “endereçar” por “corrigir”, substituição linguística aceitável, um pouco mais estreita. |
| 21, 26 | Descrevem o vício sem o símbolo. Não são par factual. |
| 03 | Acrescenta “às 18h”. |
| 06 | Acrescenta “equipe de suporte”, “pela metade”, “março”. |
| 10 | Acrescenta “cinco”, “dois minutos”. |
| 13 | Troca “poderia potencialmente” por “pode”. A própria sugestão manda conservar a incerteza (`catalogo.json`, linha 14). |
| 15 | Acrescenta “de instalação” e troca aparência por identidade, contra a exceção da mesma regra. |
| 23 | Acrescenta “de três para uma” tela. |
| 02, 05, 07, 08, 09, 11, 16, 17, 19, 22, 24, 25, 27, 29 | Substituem o vício por outro fato: site e balcão, tela única, login, servidor, planilha, versão em inglês, guia, vídeos, rascunho automático, refazer cadastro, CPF com pontos, PDF, boleto. |
| 12 | Conserva o botão no topo e acrescenta “sem rolagem”. |
| 31 | Troca a sala por uma chaleira. Ilustração de ficção, não edição do mesmo trecho. |

Focos em que isso é mais grave, porque esses pares saem com exemplo:

- Notícia: 30 preserva; 07, 06, 16 e 27 acrescentam; 12 acrescenta inferência.
- Nota executiva e proposta: os seis pares do foco acrescentam fato.
- Explicação/didático: os seis acrescentam fato.
- Acadêmico: só PTBR-14 preserva.

O teste `test_every_rule_lists_terms_and_a_concrete_preferred_form` (`results/test_humanizar.py`, linhas 1024 e 1046 a 1052) exige concretude e proíbe “informado”/“briefing” no Prefira, mas não proíbe fato novo. Só PTBR-30 tem teste de subconjunto de palavras (linhas 1092 a 1100). A revisão anterior registrou o resto como fora de escopo (`results/REVISAO-0.7.0.md`, linha 100). O mecanismo continua.

Exemplo mínimo, par atual de PTBR-03: vício “o prazo termina amanhã”; forma ensinada “o prazo termina amanhã, às 18h”.

Proposta. Para cada par, o detalhe concreto fica nos dois lados. O Prefira só remove o vício. Não inventar um segundo mundo.

- PTBR-03: Evite “É importante notar que o prazo termina amanhã, às 18h.” Prefira “O prazo termina amanhã, às 18h.”
- PTBR-06: Prefira “A mudança reduz erros no cadastro.” Sem equipe, metade ou março. A sugestão, visível no briefing, diz: se a fonte estiver no material, nomeie-a; se não estiver, não invente e, na revisão, não apague a alegação em silêncio.
- PTBR-10: Evite “Houve uma melhoria significativa: o cadastro passou de cinco para dois minutos.” Prefira “O cadastro passou de cinco para dois minutos.”
- PTBR-13: Prefira “A falha poderia voltar.”
- PTBR-15: Prefira “O documento é um guia.” A sugestão avisa para não fazer isso se “se apresenta como” separar aparência de realidade.
- PTBR-16 e PTBR-27: o fato que hoje está só no Prefira entra também no Evite; o Prefira apaga o fecho ou o preâmbulo. PTBR-27 precisa continuar casando com a regex, que exige dois-pontos no fim da linha. Pode ser multiline no JSON. Em `brief_text()`, colapsar quebra de linha ao imprimir, senão a linha do briefing quebra e o exemplo deixa de ser detectável na forma exibida.
- Mesma operação nas regras 02, 05, 07, 08, 09, 11, 12, 17, 19, 22, 23, 24, 25 e 29. PTBR-32 pode manter “corrigir”. PTBR-31: reescrever dentro da sala, ou deixar fora do teste de vocabulário, com a sugestão de que o objeto tem de ser o da cena, não a chaleira do exemplo.

No texto do briefing, nas regras de foco, imprimir `como` e `excecoes`. Nas demais, imprimir a exceção quando existir. O cabeçalho “salvo termo técnico” não cobre quadro de serviço, conclusão pedida, contraste real nem “agência de fomento”.

Os tetos de 8500, 8800 e 17000 caracteres (`test_humanizar.py`, linhas 827, 1265 e 1274) não podem ser o motivo de omitir isso. Se estourar, subir o teto. Não apagar regra.

Teste de regressão. Novo teste, além do de PTBR-30:

- Nenhum Prefira introduz `\d+`, hora, mês, dia da semana ou palavra numérica (`dois`, `três`, `cinco`, `metade`) ausente do Evite. Sem exceção.
- Tokens novos do Prefira só podem estar numa lista explícita de substitutos linguísticos (`para`, `pagar`, `corrigir`, `também`, `é`). PTBR-21, PTBR-26 e, se não for reescrito, PTBR-31 ficam de fora desse segundo critério, não do primeiro.
- `brief_text` de `jornalistico/noticia` contém a sugestão de PTBR-06 com “sem invent” e não contém “equipe de suporte” só no Prefira.
- `brief_text` de `academico/academico` contém “estatística robusta” ou a exceção de PTBR-09, e “agência de fomento” aparece em algum briefing de relatório.
- O teste de concretude atual permanece: Prefira não dispara regra do catálogo.

### P0. `check` não pega a data relativa que a própria skill cita

Evidência. `SKILL.md`, linha 52, proíbe trocar data por “nesta quinta” ou “hoje”. `README.md`, linha 43, diz que o alerta cobre dia da semana e data relativa. A regex só aceita segunda a sexta com o sufixo `-feira` (`scripts/humanizar.py`, linhas 436 a 439). `(?i)` não remove acento.

Não casam: “nesta quinta”, “na terça”, “próxima sexta”, “esta semana”, “semana que vem”, “terca-feira”, “sabado”. Casam: “hoje”, “quinta-feira”, “sábado”. O teste existente usa “nesta quarta-feira” (`test_humanizar.py`, linhas 902 a 906), por isso não vê o buraco.

Exemplo mínimo: briefing “em 1º de outubro de 2026”; texto “A abertura foi nesta quinta.” `data_inferida` não entra em `review`.

Proposta. Não marcar “segunda” ou “quinta” soltas: “na segunda etapa” e “na quinta série” são falsos positivos. Marcar:

- `hoje`, `ontem`, `amanhã`, `anteontem`, com e sem acento;
- `nesta/neste/nessa/nesse/próxima/próximo/última/último` mais `segunda|terça|quarta|quinta|sexta`, com `-feira` opcional;
- `na/no` mais esses dias só com lookahead negativo para `etapa|versão|fase|linha|série|vez|parte|edição|chamada`;
- `nesta semana`, `esta semana`, `essa semana`, `semana que vem`, `nesta manhã/tarde/noite`.

Manter a comparação por `_search_text`, para “quinta-feira” já presente no pedido não alertar.

Teste. “nesta quinta”, “na terça” no fim da frase e “esta semana” alertam se ausentes do pedido. “hoje” continua alertando. “na segunda etapa” e “na quinta série” não alertam. “quinta-feira” presente no pedido não alerta. “terca-feira” sem acento alerta se o pedido não tiver “terça-feira”.

### P0. Citação e código não são o mesmo objeto em `check` e em `apply`

Evidência. A skill manda preservar citação, código e dado original, e sinalizar a exceção (`SKILL.md`, linha 44). Também manda preservar o travessão quando for citação ou código (`README.md`, linhas 66). `check` só isenta literais fechados nesta linha, aspas duplas retas ou curvas, bloco `>` de uma linha e cerca com newline antes do fechamento (`scripts/humanizar.py`, linhas 442 a 444 e 466 a 483). `protected_spans` é outro conjunto: aspas simples, aspas curvas simples, citação que atravessa linha e aspas não fechadas até o fim (`linhas 79 a 80`).

Exemplo mínimo. `check('A fonte disse \'prazo — curto\'.', [])` bloqueia `travessao`. `apply_edits` recusa editar esse trecho, porque a aspa simples é protegida. Os dois contratos se contradizem no mesmo input.

Também bloqueia, e o `apply` ou protege demais ou não protege:

- Citação multiline: `“O prazo\n— curto”`. `check` bloqueia. `protected_spans` protege a citação inteira.
- Segunda linha de blockquote sem `>`.
- «prazo — curto»: não é literal em nenhum dos dois. `check` bloqueia; `apply` deixa alterar o texto.
- Revisão de diálogo original com travessão, fora de aspas. A skill distingue diálogo novo de símbolo original (`SKILL.md`, linha 35). `check` não recebe o original e bloqueia qualquer U+2014 fora do literal estreito. Não há `--original`.

O teste de travessão protegido (`test_humanizar.py`, linhas 911 a 915) só cobre aspas curvas na mesma linha e crase. Trava o caso feliz, não os outros.

Proposta.

- Um único reconhecedor de literal fechado, usado por `check` e por `protected_spans`: aspas duplas retas e curvas, aspas simples retas e curvas, « », cerca fechada, crase, e cada linha `>`.
- Aspas não fechadas protegem só até o fim da linha, nos dois. Hoje, uma aspa aberta congela o resto do arquivo no `apply` e não isenta o travessão no `check`.
- Novo `--original` opcional, só revisão. Travessão cuja linha, normalizada, exista no original não bloqueia; travessão em linha nova bloqueia. Sem `--original`, o comportamento de redação permanece.
- Não regravar os textos de 13/10. O teste `test_real_command_only_outputs_are_blocked_and_real_texts_pass` fixa `r00.skill` como entregável e fixa os conjuntos de bloqueio. Qualquer bloqueio novo tem de continuar compatível com essas asserções.

Teste. Os quatro exemplos acima: aspas simples, citação multiline, « » e segunda linha de `>` com U+2014 ficam em `travessao_protegido`, com `deliverable` verdadeiro. O mesmo travessão fora disso bloqueia. Com `--original` igual ao texto, a linha antiga com travessão não bloqueia; uma linha acrescentada com travessão bloqueia. Edição dentro de «citação» continua recusada por `apply_edits`.

### P0. O contrato mais próximo do pedido empurra revisão e diagnóstico para reescrita

Evidência. Revisão pede preservar voz e estrutura útil (`SKILL.md`, linha 20). Diagnóstico pede não entregar versão nova (linha 21). O fluxo geral, sem distinguir modo, manda reescrever frases copiadas do pedido (linha 77). `DELIVERY` repete isso e não menciona modo (`scripts/humanizar.py`, linhas 352 a 358). `brief` não tem parâmetro de modo. Essa lista é o último bloco do briefing, o mais perto do pedido.

Exemplo mínimo. Pedido: “Revise, sem trocar a voz: Vale destacar que o prazo acaba amanhã.” O briefing ainda pergunta se as frases são do redator e não cópia do pedido. O modo revisão, lá em cima na skill, diz o contrário.

Proposta. Uma frase fixa no fim de `DELIVERY`, nos três usos: “Redação: reescreva a frase do pedido, conservando o fato. Revisão: altere só vício, clareza ou precisão; não troque a voz nem a estrutura que funciona. Diagnóstico: aponte trecho e motivo; não entregue versão nova.” Qualificar a linha 77 do mesmo jeito. Não criar CLI obrigatória. Se couber, `--mode` pode afinar o ofício; o padrão precisa ser seguro sem flag.

Teste. `brief_text` de qualquer par contém as três palavras “Redação”, “Revisão” e “Diagnóstico” nessa seção final, e a frase de revisão contém “não troque a voz”. A validação final literal de `SKILL.md` (linhas 91 a 92) permanece byte a byte. Vale a pena repetir essa frase inteira em `DELIVERY`, para o “não economize tokens” não ficar só longe do pedido.

### P1. `apply` recusa reescrita normal e ainda deixa mutilar “1º”

Evidência. `se`, `caso`, `sem`, `salvo` e `nem` disparam proteção da oração inteira (`scripts/humanizar.py`, linhas 81 a 91). “caso” é substantivo, “salvo” é particípio, “se” é pronome. A skill recomenda “pode se tornar” (`SKILL.md`, linha 30); essa frase trava a oração. Qualquer maiúscula vira “possível nome” (linhas 93 a 95). A substituição que contenha número, “não” ou maiúscula é recusada antes do inventário (linhas 129 a 130), mesmo quando só recopía o que já estava.

Exemplo mínimo.

- `O caso foi arquivado ontem.` Editar “arquivado” para “encerrado” levanta `ValueError`.
- `vale destacar o prazo.` Substituir por `O prazo acaba.` levanta `ValueError` por causa do “O”.
- `em 1º de outubro`. O span numérico é só `1`. Apagar `º` passa no `apply` e no inventário.

O README admite recusa de edição legítima. Isso vai além: trava oração por homonímia e recusa recopiar um número igual.

Proposta.

- Expandir à oração só `não`, `nunca`, `jamais` e condicionais de mais de uma palavra (`desde que`, `a menos que`, `somente se`, `salvo se`). `se`, `caso`, `sem`, `salvo` e `nem` protegem o token, não a frase.
- Nome: maiúscula interna ou sequência de dois tokens capitalizados, não a primeira palavra da substituição se for artigo ou pronome.
- Remover o pré-check da linha 129. O inventário já impede acrescentar número ou negação. Recopiar `20` dentro do span editado, sem mudar o multiset, deve passar. Trocar `20` por `21` deve falhar.
- Incluir `[ºª]` no span numérico.

Teste. Os três exemplos: os dois primeiros passam a ser aplicáveis; apagar `º` passa a falhar; `não pagar 1.500 reais hoje` continua protegido, como no teste da linha 50. `suggest` no catálogo real pode continuar sem variantes; não inventar substituição automática.

### P1. Resposta técnica curta com comando em cerca é bloqueada

Evidência. `had_commands` olha o texto bruto, inclusive cerca fechada. O limite de 8 palavras olha a prosa depois de apagar a cerca (`scripts/humanizar.py`, linhas 477 a 480). O teste que passa (`test_humanizar.py`, linha 918) usa uma frase longa. Uma frase curta cai abaixo de 8.

Exemplo mínimo.

```text
Rode o comando.

```sh
python3 -m pip install pacote
```
```

`deliverable` fica falso, com `saida_somente_comandos`. O gênero técnico pede exatamente exemplo em bloco (`estilos.json`, linhas 486 a 488). `python3 scripts/humanizar.py brief` sozinho deve continuar bloqueado.

Proposta. Calcular `had_commands` só depois de remover literais fechados. Comando que existe apenas dentro de cerca ou citação não conta. Manter o bloqueio quando a resposta é só comando, chamada de ferramenta ou JSON sem `--artifact codigo`.

Teste. O exemplo curto acima é entregável. `python3 -m pip install pacote\n` sozinho não é. O exemplo longo da linha 918 continua entregável. Os slots `g.01-noticia-bibliotecas.r05.skill` e `r12.skill` continuam no conjunto `command_only`, sem eu ter reexecutado essa evidência: o implementador confirma ao rodar a suíte.

### P1. Detectores mais largos que a regra, ou cegos à regra

Evidência.

- PTBR-20 casa qualquer item com rótulo em negrito, não só rótulo repetido (`catalogo.json`, linha 21). `- **Prazo:** 5 a 16 de outubro.` dispara. O ofício da notícia pede quadro de serviço (`estilos.json`, linha 796). A exceção existe no JSON e o teste só verifica se a string “quadro de serviço” é buscável (`test_humanizar.py`, linhas 1088 a 1090). Não isenta o regex.
- PTBR-29 marca “de forma clara”, “simples”, “segura” e “prática” (`catalogo.json`, linha 30). A skill nomeia “de forma eficiente” (`SKILL.md`, linha 39). “De forma clara” é frase comum. O alerta empurra o modelo a inventar um modo concreto.
- PTBR-24 marca “Para concluir o pagamento, abra o aplicativo.” porque `para concluir` não exige vírgula (`catalogo.json`, linha 25).
- “robusto” solto está no veto da skill (linha 38) e não está no catálogo, salvo “solução/sistema/plataforma/processo robusto” (PTBR-09). “plano robusto” não alerta.
- PTBR-11 não casa “otimizados”, “alavancadas” nem “fomentado”, apesar de “inclusive no plural ou conjugados” (`SKILL.md`, linha 38).
- PTBR-06 não casa “Estudos recentes mostram”.

Não alargar “jornada” para a palavra solta. “Jornada de trabalho” é termo comum. O catálogo já limita a “jornada transformadora/rumo” (PTBR-23). A correção é na skill: tirar o verbete solto e escrever as colocações, com exceção explícita. O mesmo para “ecossistema”: não banir a palavra; a exceção biológica já está na linha 44.

Proposta de regex, sem remover regra.

- PTBR-20: só quando o texto do rótulo reaparece no item, com `(?i)` e retroreferência. `- **Prazo:** O prazo é amanhã.` continua. `- **Prazo:** 5 a 16 de outubro.` não.
- PTBR-24: `para concluir,` com vírgula.
- PTBR-29: retirar `clara|simples|segura|prática`. Manter `eficiente` e os adjetivos decorativos já listados em `avoid`.
- PTBR-11: incluir particípio plural e `fomentad[oa]s?`.
- PTBR-06: permitir até três palavras entre “estudos” e “mostram/comprovam”.
- “robusto”: só com lookahead/lookbehind que preserve “estatística robusta”, “controle robusto” e “teste de robustez”, e só se a exceção aparecer no briefing. Sem isso, não acrescentar o detector.

Teste. Um caso positivo e um negativo para cada item acima. “agência de fomento” e “otimização convexa” continuam com contagem 0, como já está no teste das linhas 792 a 795.

### P1. Blocos obrigatórios pedem material que o pedido pode não ter

Evidência, com mitigação parcial. O briefing diz que bloco não é seção obrigatória (`scripts/humanizar.py`, linhas 400 a 401). A instrução do bloco é mais específica e vem sem condição:

- Reportagem, `vozes`: “Dê voz às fontes com falas literais entre aspas” (`estilos.json`, linhas 893 a 895). Sem fala no material, isso pede aspas inventadas. A notícia, no bloco `atribuicao` (linha 829), já diz “preserve lacunas”. A reportagem não.
- E-mail: “Saudação pelo nome” (linha 538), sem “se estiver no pedido”.
- Explicação: “mostre contas com unidades” (linha 361), contra “calcule apenas o que ele manda calcular” (`estilos.json`, linha 29, e `SKILL.md`, linha 50).
- Acadêmico, `resultados`: “Apresente os resultados com números” (linha 1060), sem “se houver”.
- Crônica: “Primeira pessoa” incondicional (linhas 1137 a 1139). Se o pedido for relato real em terceira pessoa, o ofício briga com a regra de material.

Nota executiva já qualifica “se informados” (linha 1009). Esse é o modelo.

Proposta. Reescrever esses quatro blocos e o ofício da crônica com a condição. Reportagem: “Se houver fala literal, use aspas e atribua; se não houver, não invente aspas.” E-mail: “Saudação pelo nome só se o pedido trouxer o nome.” Explicação: “Conta só se o pedido pedir; com unidades.” Acadêmico: “Números só os do material.” Crônica factual: “A pessoa narrativa é a do pedido; não invente vivência.”

Teste. `brief_text('jornalistico','reportagem')` contém “não invente aspas”. `brief_text('conversacional-contido','email')` contém “se o pedido” junto de nome. `brief_text('didatico','didatico')` não contém “mostre contas” sem condição. Os `structure_id` de `GENRE_PLANS` não mudam.

### P2. O que `check` ainda não confere, e um alerta de eco só na redação

Evidência do que o código faz. Números são conjunto de strings de dígitos no texto inteiro, inclusive código (`linhas 493 a 504`). “seis” omitido não alerta. “-20” no lugar de “20” não alerta. “a partir de 12” virando “até 12” não alerta. “não” apagado não alerta. Offset de `omissao_numerica` é do briefing, não do texto, embora `source='briefing'` exista.

Meia-risca e hífen entre espaços são alerta de catálogo, não bloqueio. A skill os proíbe com o mesmo “não use” do travessão (`SKILL.md`, linha 35; `check`, linhas 481 a 483). O briefing de conto ainda imprime o glifo da meia-risca, porque o Evite de PTBR-28 entra no foco de `cena` e o teste exige o `positive_example` cru no texto. Isso contamina o prompt. O travessão U+2014 foi descrito sem glifo; a meia-risca, não.

A revisão 0.7.0 deixou de fora um alerta de eco (`REVISAO-0.7.0.md`, linhas 11 e 55). A skill já define o defeito: na redação, o pedido é matéria-prima (`SKILL.md`, linha 27). Isso não é otimização de nota.

Proposta.

- Comparar números só fora de literal fechado. `404` em cerca não alerta; `404` na prosa alerta.
- Documentar no JSON de omissão que `start`/`end` referem-se ao briefing.
- No texto do briefing, mostrar PTBR-28 como “meia-risca entre palavras”, sem o glifo. Ajustar o teste que exige o exemplo cru. O detector continua usando o JSON.
- Não promover meia-risca a bloqueio enquanto `r00.skill` não for conferido pelo implementador. Se for promovida, usar o mesmo `inside()` dos literais e não mexer nos arquivos históricos.
- Alerta `eco_do_pedido`, só redação, não bloqueio, não score: sequência de 6 palavras do pedido reaparecendo fora de literal. Revisão não alerta. Não copiar os 24 prompts para a skill; o teste usa frase sintética local.

Teste. Cerca com `404` não gera `acrescimo_numerico`; prosa com `404` gera. Briefing de `literario/conto` não contém U+2013. Texto de redação que repete seis palavras do pedido gera `eco_do_pedido`; o mesmo texto com modo revisão não gera.

## Melhorias editoriais

Hipótese, salvo onde indico evidência.

- Roteamento. Sem perfil, `brief` cai em `neutro-claro` e no primeiro plano compatível, em geral explicação. A skill não diz o mapa. Incluir na skill, curto: notícia e reportagem, `jornalistico`; e-mail, `conversacional-contido` ou `informal`; conto e crônica, `literario`, `coloquial` ou `caricato`; proposta e nota, `executivo-direto`; opinião, `argumentativo-sobrio`. Não inferir gênero no script.
- `argumentativo-sobrio` + `post` usa `argumento`, não `post`, porque o primeiro `structure_id` compatível ganha (`scripts/humanizar.py`, linhas 263 a 268). O teste do primeiro match trava isso. Se o post argumentativo deve ter abertura de rede, o plano `post` precisa vir antes, ou o gênero `post` precisa de estrutura própria nesse perfil. Não mudar os seletores já documentados na revisão 0.7.0 sem decisão.
- Título de notícia “verbo no presente” (`estilos.json`, linha 793) pode transformar “anunciou em 1º de outubro” em “anuncia”. Convenção jornalística, não bug. Qualificar: presente no título se o fato ainda vale; não mudar o tempo do lide nem a data.
- Roteiro pede 130 a 150 palavras por minuto (linha 642). É ofício, não fato do assunto. Dizer que esse número não entra no texto entregue.
- Ensaio: o ofício pede fechar com pergunta (`estilos.json`, linha 778) e o foco PTBR-25 ensina a apagar a pergunta e pôr uma causa de CPF. Depois de corrigir o par, a sugestão deve dizer que pergunta concreta de ensaio não é gancho retórico.
- “em resumo do relatório” no início da frase casa PTBR-24. Exigir que o conector feche a locução (`em resumo,`) reduz o falso positivo. Hipótese de frequência; o caso “para concluir” sem vírgula é o defeito claro.
- Não acrescentar corretor ortográfico. Acento obrigatório está na skill e não há verificação. Se houver alerta, que seja lista curta e revisão, fora de literal: `nao`, `voce`, `tambem`, dias sem acento. Não bloquear.
- `suggest` no catálogo real não propõe edição, porque não há `variants`. Está documentado. Não cadastrar substituição automática a partir dos Prefira: com os pares atuais, isso aplicaria fato inventado. Depois da correção dos pares, `suggest` pode devolver a sugestão como texto, com `approved: false`, nunca como edição.
- O cabeçalho “32 no total” na seção que não lista as 32 (`brief_text`, linhas 423 a 424) confunde. Dizer “as outras N regras”.
- Perfis `coloquial`, `informal` e `caricato` estão distinguíveis e compatíveis com norma culta. Não enxugar.

## O que não desfazer

- Doze perfis, ids iguais na skill e em `estilos.json`.
- Quinze planos; `relatorio` não volta a `procedimento`; notícia tem título; crônica e ensaio têm plano próprio.
- Material do gênero é padrão; o pedido prevalece. Roteiro continua `fatos`, crônica continua `ficcao`. As linhas condicionais “Se o pedido for” ficam.
- PTBR-30 como está.
- Bloqueio de U+2014 na prosa, de preâmbulo na primeira linha, de saída só com comando e de artefato `codigo` opt-in.
- `apply` com hash, `approved: true`, offsets Unicode, arquivo novo e recusa de sobreposição.
- A frase inteira de validação final em `SKILL.md`, linhas 91 a 92.
- Ausência de U+2014 em `SKILL.md` e `README.md`.
- Os 24 prompts e `results/runs`. Teste novo usa frase local, não trecho desses prompts.

## Ordem para implementar

1. Reescrever os pares e imprimir sugestão e exceção no briefing. Subir teto de teste se precisar.
2. Corrigir `RELATIVE_DATE` sem marcar “segunda etapa”.
3. Unificar literais e acrescentar `--original` para travessão de revisão.
4. Qualificar modo no fim do briefing e na linha 77 da skill.
5. Estreitar proteção do `apply`, incluir `º`, e corrigir os regex de PTBR-20, 24, 29, 11 e 06.
6. Corrigir `saida_somente_comandos` para ignorar comando dentro de literal fechado.
7. Qualificar os blocos que pedem aspas, nome, conta ou número.
8. Alertas de número fora de código e de eco na redação. Meia-risca sem glifo no briefing.

Não há, nesta leitura, motivo para mudar versão de catálogo sem subir o patch da skill se esses contratos mudarem. Isso fica para quem implementar.