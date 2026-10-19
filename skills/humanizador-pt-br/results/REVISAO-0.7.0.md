# Revisão 0.7.0 (19/10/2026)

Pedido de Ricardo: nova revisão com Claude Code Opus 5.5, esforço max, e implementação de melhorias substanciais de escrita e naturalidade. Escopo: skill, catálogo, estilos, script, testes e documentação. Runner, prompts aprovados, modelos, modos, juízes, rubricas e histórico em `results/runs` não foram alterados.

Estado: implementação e validação offline concluídas. Após a revisão com Claude Code Opus 5.5 max, o teste parcial de 19/10 mostrou: H passou de 26,74 para 40,27 nos 22 pares do Opus avaliados pelos três juízes; preferência de 35 a 31 pela skill. Foram 117 gerações submetidas, com 107 respostas completas e 66 julgamentos. A indisponibilidade do Grok interrompeu a matriz. Os 121 testes de software passaram. [Resultado medido](runs/2026-10-19-max/README.md).

## Achados

Leitura somente das respostas e julgamentos preservados de 13/10 e 19/10 (pedido 01) e do tratamento 0.6.0. Nenhum texto dessas evidências entrou no material da skill.

1. **Texto que espelha o pedido.** Os juízes descreveram as respostas com skill como "quase repete o pedido", "reescrita mínima do enunciado", "seca", "protocolar" e "sem título nem estrutura de notícia". Numa leitura diagnóstica local, a fração de palavras em sequências de seis palavras idênticas ao pedido teve mediana de 0,85 com skill (14 de 15 respostas acima de 0,5) e cerca de 0,36 sem skill (5 de 16). Quatro das 15 respostas com skill saíram sem título. A naturalidade bruta média caiu de 83,60 para 81,42, e a preferência ficou em 13 a 11 para o baseline.
2. **Tratamento feito quase só de vetos.** Na 0.6.0, as 28 regras ocupavam cerca de 8.500 dos 11.000 caracteres do briefing, e a SKILL.md tinha uma única linha de orientação positiva. Os exemplos "Prefira" ensinavam a apagar ("É um aviso.", "O botão mudou.") e nove remetiam a dado vago ("na data informada", "na condição descrita", "indicado no briefing").
3. **Planos trocados entre gêneros.** Relatório em `tecnico-preciso` recebia o plano de documentação ("Mostre comandos ou etapas na ordem de execução"); nota de negócios recebia o de proposta ("responsável pelo aceite"); relatório executivo e texto acadêmico recebiam o de relatório de laboratório; `neutro-claro` com relatório recebia o de explicação. A notícia não tinha bloco de título; reportagem, ensaio e crônica reaproveitavam planos de outros gêneros.
4. **Ficção proibida no briefing.** Todo briefing mandava "preencha cada bloco só com fatos do pedido", proibia "fala ou vivência ausentes" e listava "Experiência pessoal inventada" em "Nunca", inclusive para conto e crônica. A SKILL.md permitia invenção na ficção, mas a instrução mais próxima do pedido a proibia.
5. **Fidelidade confundida com secura.** A proibição genérica de "orientação" impedia transformar um fato fornecido em instrução ao leitor, que é reescrita, não acréscimo.
6. **Redundância sem hierarquia.** O mesmo vício aparecia na SKILL.md, no perfil e no catálogo, e as 28 regras tinham o mesmo peso em todos os gêneros.

## Mudanças

| Arquivo | Mudança |
|---|---|
| `SKILL.md` | 0.7.0. Seção "Como escrever bem" antes dos vetos: leitor, pedido como matéria-prima, gênero completo, concretude, ritmo, sintaxe brasileira culta e fecho. Lista explícita de vícios mantida e ampliada (prosa de repartição, finalidade presumida, calcos do inglês, emoção pronta na ficção). Fidelidade por tipo de texto pedido (fato, opinião ou ficção), que prevalece sobre o padrão do gênero, com alcance de quantificadores. Ferramentas de revisão condensadas, com remissão ao README. Validação final literal. |
| `scripts/humanizar.py` | `VERSION` 0.7.0. `brief` em nova ordem: ofício do gênero, plano de funções (não seções), perfil, material, seis vícios típicos do gênero com exemplo de vício e forma preferida, demais regras por termos explícitos e contrato de entrega por último. O JSON ganha `genre_name`, `craft`, `material`, `material_label`, `material_policy`, `material_alternatives`, `focus` e `rules[].foco`. `check` e demais comandos inalterados. |
| `references/estilos.json` | 1.2. Quinze estruturas, cada uma com nome, ofício, vícios típicos e material padrão. Novas: `reportagem`, `nota-executiva`, `ensaio`, `academico` e `cronica`; `noticia` com título e serviço; `explicacao` começa por situação concreta; `procedimento` só para documentação técnica. Mapas `material` (regra do padrão) e `material_types` (regra condicional de cada tipo pedido). "Experiência pessoal inventada em não ficção". Ajustes mais concretos em nove perfis; textos de `coloquial`, `informal` e `caricato` preservados. |
| `references/catalogo.json` | 32 regras, todas com termos explícitos (`avoid`) e forma preferida concreta. Novas: PTBR-29 verbo-suporte, PTBR-30 finalidade-presumida, PTBR-31 cliche-narrativo e PTBR-32 calco-do-ingles. Variantes em PTBR-03, 04, 05, 07, 12 e 23. Quadro de serviço como exceção de PTBR-20. |
| `results/test_humanizar.py` | `Catalog070Tests`, `Structure070Tests`, `Brief070Tests`, `Material070Tests` e `Skill070Tests`, com 15 testes novos. Três testes de `BriefTests` passam a verificar o formato 0.7.0 em todos os pares perfil/gênero; o teste anti-cópia dos 24 prompts cobre os 36 briefings. |
| Documentação | README da skill e raiz, índice, `results/README.md`, `VALIDACAO.md` e esta revisão. |

Plano por seletor fixo do runner:

| Seletor | 0.6.0 | 0.7.0 |
|---|---|---|
| `jornalistico/noticia` | `noticia`, sem título | `noticia`, com título e serviço |
| `jornalistico/reportagem` | `noticia` | `reportagem` |
| `tecnico-preciso/tecnico` | `procedimento` | `procedimento` |
| `tecnico-preciso/relatorio` | `procedimento` | `relatorio` |
| `didatico/didatico` | `explicacao` | `explicacao`, a partir de situação concreta |
| `academico/academico` | `relatorio` | `academico` |
| `executivo-direto/proposta` | `proposta` | `proposta` |
| `executivo-direto/negocios` | `proposta` | `nota-executiva` |
| `executivo-direto/relatorio` | `relatorio` | `nota-executiva` |
| `conversacional-contido/email`, `post`, `roteiro` | `mensagem`, `post`, `roteiro` | iguais, com ofício e vícios típicos |
| `argumentativo-sobrio/artigo` | `argumento` | `argumento` |
| `argumentativo-sobrio/ensaio` | `argumento` | `ensaio` |
| `literario/conto` | `cena` | `cena` |
| `literario/cronica` | `cena` | `cronica` |

## Decisões

- Orientação positiva antes do veto; contrato de entrega por último, perto do pedido.
- Blocos como funções do texto, não seções, para não padronizar a forma.
- O catálogo inteiro continua no briefing, por termos, para manter a lista explícita; só os vícios típicos do gênero levam exemplo.
- Exemplos novos usam um micromundo neutro (cadastro, formulário, feira, chaleira), sem dados dos 24 prompts. O teste de sequências de cinco palavras cobre SKILL.md, os dois JSONs e os 36 briefings.
- Runner inalterado: o modo `v2-brief` lê SKILL.md e o retorno de `brief`, e só precisa de `--skill-version 0.7.0`.
- `check` inalterado. Alerta de eco do pedido e conferência de dia da semana foram considerados e não implementados, para não ampliar o escopo nem criar contagens novas no relatório de entrega.

## Correções da revisão independente

1. **Exemplo de PTBR-30 fiel aos fatos.** A forma preferida acrescentava "reúne produtores da região", ausente do exemplo de vício. Agora o par é "A feira abre no sábado com produtores da região. A iniciativa busca fortalecer o comércio local." e "A feira abre no sábado com produtores da região.": a edição retira só a finalidade presumida e preserva todos os fatos. O teste `test_purpose_rule_example_keeps_exactly_the_facts` exige que toda palavra da forma preferida exista no exemplo de vício e que a regra não a detecte; os invariantes anteriores do catálogo continuam valendo para as 32 regras.
2. **Material do gênero é padrão, não ordem.** O briefing passa a abrir a seção com "o tipo de texto pedido (fato, opinião ou ficção) prevalece", marca a regra do gênero como "Padrão do gênero" e traz a regra condicional dos outros dois tipos ("Se o pedido for ficção: invente dentro da premissa, sem usar pessoas reais."; "Se o pedido for fato real: use só o material dele, sem acrescentar dados, fontes ou vivências."). A SKILL.md abre a seção Fidelidade com "O pedido define se o texto é fato, opinião ou ficção e prevalece sobre o padrão do gênero (crônica pode ser relato real; roteiro, ficção)." Os padrões da matriz aprovada não mudaram: roteiro continua `fatos`, crônica continua `ficcao`. Sem CLI nova e sem mudança nos seletores. `Material070Tests` verifica, nos briefings de roteiro e crônica, o padrão preservado, a precedência do pedido, as regras condicionais e a ausência de ordem incondicional de inventar ou de restringir aos fatos, e verifica a mesma regra na SKILL.md.

Para manter o limite de tamanho do tratamento, os termos das demais regras no briefing deixaram de vir entre aspas e duas frases foram encurtadas, sem retirar conteúdo.

## Validação offline

Comandos na raiz do repositório. Cada etapa teve os testes escritos e executados antes da implementação.

| Etapa | Antes da implementação | Depois |
|---|---|---|
| HEAD 0.6.0 | 54, 15 e 15 testes OK nas três suítes | |
| Catálogo | `Catalog070Tests`: 4 testes, 8 falhas e 27 erros de subteste (28 regras, termos ausentes, variantes não detectadas) | 58 testes; 1 falha no teste antigo de compactação (briefing de 15.173 caracteres), resolvida no redesenho do briefing |
| Estruturas | `Structure070Tests`: 2 testes, 10 falhas e 1 erro (planos trocados, notícia sem título, sem `material`) | 60 OK |
| Briefing | `BriefTests` e `Brief070Tests`: `KeyError: 'craft'` e `'focus'` em todos os pares | 63 OK |
| SKILL.md | `Skill070Tests`: 1 falha (versão) e 1 erro (sem "Como escrever bem"); a primeira redação, com 10.618 caracteres, falhou no limite de 8.800 | 66 OK |
| Correções da revisão | 3 testes, 4 falhas (forma preferida de PTBR-30 com palavras novas; briefings de roteiro e crônica sem precedência do pedido; SKILL.md sem a regra) | 69 testes, 1 falha de tamanho (17.003 caracteres no par mais longo, limite 17.000); depois do encurtamento, 69 OK |

Execução final:

| Comando | Resultado |
|---|---|
| `python3 -W error skills/humanizador-pt-br/results/test_humanizar.py` | 69 OK, após as correções |
| `python3 -m unittest discover -s skills/humanizador-pt-br/results/scripts -p test_generation_eval.py` | 15 OK, após as correções |
| `python3 -m unittest discover -s skills/humanizador-pt-br/results/runs/2026-10-13/analysis -p test_objetivo.py` | 15 OK antes das correções; a suíte não lê os arquivos corrigidos |

Compatibilidade: o modo v1 reproduz byte a byte o plano congelado de 13/10; no `v2-brief` com 0.7.0, as chamadas de baseline são idênticas às do v1 e o tratamento fica abaixo de 40% do v1; o `delivery` sobre a evidência de 13/10 mantém 11 e 12 respostas entregáveis.

Tamanho do tratamento sem o pedido, nos pares do runner, medido em caracteres pelo mesmo método nas duas versões: 0.6.0, de 19.143 a 19.308 (SKILL.md 8.312 e briefing de 10.831 a 10.996); 0.7.0, de 16.050 a 16.613 (SKILL.md 8.774 e briefing de 7.276 a 7.839). Entre os 36 pares perfil/gênero, o maior tratamento tem 16.985. Caracteres, não tokens.

## Teste de escrita

Executado parcialmente, conforme o [protocolo 0.7.0](PROTOCOLO-0.7.0.md) e o [relatório](runs/2026-10-19-max/README.md): `--packaging v2-brief --skill-version 0.7.0`, semente de anonimização `humanizador-0.7.0-independent-v2-brief`. Pedidos, baseline, modelos, juízes e métricas inalterados.

## Riscos que pedem decisão

1. Texto mais completo tende a ficar mais longo. Em 19/10, Astra considerou linha fina e quadro de serviço repetitivos numa notícia curta, e Opus os valorizou; o briefing deixa o serviço opcional, mas não resolve essa divergência.
2. Permitir transformar fato em orientação aumenta o risco de pequenas inferências de alcance, como "em qualquer unidade", que os juízes trataram como erro não crítico.
3. O tratamento caiu cerca de 15%, mas segue muito maior que o pedido. Reduzir mais exigiria tirar do briefing as regras fora do gênero, que hoje mantêm a lista explícita.
4. As quatro regras novas e as variantes ampliadas geram mais alertas de revisão em `check` e `delivery`. Os bloqueios não mudaram, mas as contagens de alertas de 0.7.0 não são comparáveis às de 0.6.0.
5. Sete seletores do runner trocam de plano e dois mudam de blocos; a comparação por pedido com 0.6.0 mistura efeito de plano e de orientação.
6. Outros pares "Evite/Prefira" mostram concretude com detalhe ausente do exemplo de vício, entre eles PTBR-06 (autoridade vaga), que é regra de fidelidade. Por escopo, só PTBR-30 foi corrigido.
