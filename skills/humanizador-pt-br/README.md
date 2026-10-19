# Humanizador PT-BR 0.8.0

Redação, revisão e diagnóstico em português brasileiro. A orientação editorial positiva vem antes dos vetos: escrever para o leitor, reescrever o pedido em vez de copiá-lo, entregar o gênero completo, ser concreto e dar ritmo pelo sentido. Há regras explícitas contra travessão e traço substituto na prosa produzida, enchimentos, jargão decorativo e fórmulas de IA. Catálogo e estilo são aplicados antes de escrever, e a entrega é verificada antes de sair.

A versão 0.8.0 consolida três revisões independentes da 0.7.0. Cada forma preferida do catálogo só retira o vício, sem fato novo; o briefing em texto traz a orientação das regras de foco e a exceção de todas as regras; redação, revisão e diagnóstico têm instruções próprias; edição e entrega reconhecem código e citações do mesmo modo, e o travessão entre aspas só passa quando a citação está na fonte.

## Instalação e uso

Copie a pasta completa para o diretório de skills do agente e carregue [SKILL.md](SKILL.md). Para escrever do zero, forneça o briefing; para revisar, forneça o texto. O script requer Python 3 e usa apenas a biblioteca padrão, sem API ou serviço.

> Redija uma explicação de cache para iniciantes com humanizador-pt-br.
>
> Revise este artigo preservando fatos e voz: [...]. Use humanizador-pt-br.
>
> Diagnostique os vícios deste texto, sem reescrever: [...].

## Ferramentas no fluxo de redação

Execute na pasta da skill, pelo terminal do agente:

```text
python3 scripts/humanizar.py brief --profile jornalistico --genre noticia
```

`brief` devolve, nesta ordem: o ofício do gênero, o plano de funções do texto, o perfil, a regra de material (fatos, opinião ou ficção), os pontos de atenção do gênero (vício, forma preferida, termos, orientação e exceção), as demais regras do catálogo com termos e exceção, e o contrato de entrega, com uma instrução para cada modo. Cada gênero tem plano próprio: notícia com título e lide, reportagem com atribuição e limites, nota executiva com conclusão primeiro, ensaio, crônica e conto separados. Instruções que dependem de material (fala literal, nome do destinatário, conta, método empírico, pessoa narrativa) valem só quando o pedido o traz. `--format json` entrega o mesmo conteúdo para ferramentas, mais os invariantes de voz que a SKILL.md já declara. Para aprofundar:

```text
python3 scripts/humanizar.py catalog --query autoridade --genre noticia --limit 5
python3 scripts/humanizar.py styles --query jornalistico --genre noticia
python3 scripts/humanizar.py structure --profile jornalistico --genre noticia --breadth 2
```

Os blocos do plano são funções do texto, não seções obrigatórias. Para variar escolhas opcionais, acrescente `--randomness 0.4 --seed 17`; `--breadth` limita cobertura opcional, preservando os blocos obrigatórios. Seed reproduz o plano local, não o texto de um modelo. O script não inventa fatos nem gera prosa pronta.

Consultas `--query` ignoram acentos e maiúsculas; `--genre` exige o identificador exato, como `relatorio` ou `noticia`. Consulte todos os perfis com `styles --limit 20`; encontre uma regra por ID com `catalog --query PTBR-21`. Gêneros aceitos por perfil:

| Perfil | Gêneros |
|---|---|
| `neutro-claro` | artigo, relatorio |
| `tecnico-preciso` | tecnico, relatorio, email |
| `conversacional-contido` | email, post, roteiro |
| `argumentativo-sobrio` | artigo, post, ensaio (plano de opinião) |
| `jornalistico` | noticia, reportagem |
| `didatico` | didatico, artigo |
| `academico` | academico, relatorio |
| `executivo-direto` | proposta, negocios, relatorio |
| `literario` | conto, cronica |
| `coloquial` | conto, cronica, roteiro, post, email |
| `informal` | email, post, artigo, conto, cronica, roteiro |
| `caricato` | conto, cronica, roteiro, post |

Sem terminal, o agente lê os JSONs e segue direto para o texto. A resposta só é comando, chamada de ferramenta, JSON ou plano quando o pedido exige esse formato.

## Verificação da entrega

```text
python3 scripts/humanizar.py check texto.txt --briefing pedido.txt
```

Código 0: entregável. Código 1: bloqueio por comandos, chamada de ferramenta ou JSON no lugar do texto; por preâmbulo de entrega no início ("Aqui está a notícia:"), inclusive depois de uma cortesia como "Claro!" ou em negrito; ou por travessão na prosa. Comando dentro de bloco de código fechado é documentação e não bloqueia, salvo comando da própria skill. Linha que anuncia anexo ou lista da mensagem ("Seguem os documentos:") gera alerta, não bloqueio. O travessão passa em código fechado, em citação ou nome conferidos no pedido e, numa revisão com `--original texto-do-usuario.txt`, na frase mantida do autor; aspas, por si, não provam origem. `--artifact codigo` é o contrato explícito para pedido de só código, comando ou JSON; o padrão é prosa. Código 2: erro de entrada.

Alertas sem bloqueio listam ocorrências do catálogo, números presentes só no texto ou só no pedido (com sinal, percentual e ordinal, fora de blocos de código; `start` e `end` da omissão referem-se ao pedido) e dia da semana ou data relativa ausentes do pedido ("nesta quinta", "semana que vem", comparados por palavra inteira). São pontos para leitura, não prova de defeito nem de fidelidade.

## Auditoria e edição

```text
python3 scripts/humanizar.py audit rascunho.txt
python3 scripts/humanizar.py rhythm rascunho.txt
python3 scripts/humanizar.py replace rascunho.txt --from "com o intuito de" --to "para"
python3 scripts/humanizar.py suggest rascunho.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py apply rascunho.txt --plan plano-aprovado.json --output revisado.txt
python3 scripts/humanizar.py verify rascunho.txt revisado.txt
```

`audit` localiza regras e repetições. `rhythm` descreve comprimentos e aberturas repetidas, sem nota de autoria. `replace` propõe substituição literal em trechos não protegidos; `suggest` usa variantes cadastradas. O catálogo oficial não tem variantes: nele, `suggest` devolve só recomendações, sem edição, porque as formas preferidas dependem do contexto. Ambos devolvem JSON com `approved: false`, sem alterar a entrada.

Salve o JSON retornado com a ferramenta de arquivos do agente. Leia cada trecho e seu contexto; marque `approved: true` somente nas edições aprovadas. `apply` exige hash da entrada, offsets Unicode (fim exclusivo), trecho exato e arquivo de destino novo. Exemplo de edição para a entrada literal `com o intuito de validar.`:

```json
{"input_sha256":"HASH_RETORNADO_PELO_SCRIPT","edits":[{"start":0,"end":16,"original":"com o intuito de","replacement":"para","approved":true}]}
```

`--protect "kg"` acrescenta proteção de termo ou unidade. Recebem bloqueios heurísticos conservadores: números com sinal, percentual, ordinal ou grau; possíveis nomes; código com crases de qualquer tamanho e cercas de três ou mais caracteres; citações entre aspas retas, curvas, simples ou angulares, no mesmo parágrafo; orações com negação ou condição, inclusive em Unicode decomposto e com abreviações como "sr.". A rotina pode recusar uma edição legítima; não contorne a proteção para forçá-la. A redação contextual pelo agente continua possível, seguida de leitura de fidelidade.

Travessão não tem substituição universal: escolha ponto, vírgula ou parênteses pela função da frase. Preserve o símbolo quando pertence a uma citação literal ou código original. `verify` verifica diferenças e inventários protegidos, não equivalência semântica nem veracidade.

## Recursos

- [Skill](SKILL.md): orientação editorial, regras explícitas e procedimento.
- [Catálogo](references/catalogo.json): 32 padrões pesquisáveis, com termos, sugestões e exceções. `positive_example` é o vício detectado; `negative_example` é a forma preferida, que só o retira.
- [Estilos e estruturas](references/estilos.json): 12 perfis, 15 planos por gênero com ofício e pontos de atenção, regras de material.
- [Script](scripts/humanizar.py): ferramentas locais e conservadoras.
- [24 prompts aprovados](results/PROMPTS.md): pedidos preservados, sem H1/H2.
- [Status e validação](results/README.md): testes locais separados da avaliação de escrita.
- [Revisão 0.8.0](results/REVISAO-0.8.0.md); [revisão 0.7.0](results/REVISAO-0.7.0.md) e [protocolo 0.7.0](results/PROTOCOLO-0.7.0.md); [revisão 0.6.0](results/REVISAO-2026-10-19.md) e [protocolo 0.6.0](results/PROTOCOLO-0.6.0.md).

## Avaliação

A versão 0.8.0 passou em 117 testes de software, mais 11 reproduções independentes. No [teste funcional de redação](results/reviews/0.8.0/SMOKE.md), o MiMo produziu cinco textos sem bloqueio mecânico e teve um pedido recusado por limite temporário. A leitura editorial encontrou imprecisões, acréscimos não fornecidos e problemas de continuidade. Não houve comparação A/B nesta rodada.

### Histórico 0.7.0

Após a revisão com Claude Code Opus 5.5 max, o teste parcial de 19/10 mostrou: H passou de 26,74 para 40,27 nos 22 pares do Opus avaliados pelos três juízes; preferência de 35 a 31 pela skill. Foram 117 gerações submetidas, com 107 respostas completas e 66 julgamentos. A indisponibilidade do Grok interrompeu a matriz. Os 121 testes de software passaram. Veja [resultados, textos e consumo](results/runs/2026-10-19-max/README.md).

### Histórico 0.6.0

A [avaliação de 19/10/2026 da versão 0.6.0](results/runs/2026-10-19/README.md) produziu 31 respostas completas. Nos 9 pares avaliados pelos três juízes, H passou de 42,04 para 49,19, mas a preferência geral ficou em 13 votos para o baseline, 11 para a skill e 3 empates. Nos 15 pares de geração, os tokens médios passaram de 628,33 para 6.253,07 e o tempo de API de 6,91 para 7,37 segundos. Nenhuma das 15 respostas com skill entregou apenas comandos. A amostra cobre somente parte do primeiro dos 24 pedidos.

### Histórico 0.5.1

A [retomada de 13/10/2026](results/runs/2026-10-13/README.md) continua incompleta, devido ao limite temporário do Qwen Flash. Resultados parciais de uma notícia:

| Indicador | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Humanização percebida, índice médio de 0 a 100 | 40,03 | 38,52 | −1,52 pontos (−3,79%) |
| Tokens totais por geração, média | 601,47 | 19.438,47 | +3.131,84% |
| Tempo da chamada de redação, média em segundos | 10,92 | 9,47 | −13,28% |

Humanização: 11 pares com Jev, Astra e Opus. Tokens e tempo: 15 pares de respostas completas, incluindo duas saídas que entregaram comandos de ferramenta em vez de texto. O índice é 100 menos a impressão de IA do juiz, não uma probabilidade de autoria humana. Não houve melhora média nesta amostra; ela não sustenta uma conclusão geral.

Veja o [relatório objetivo](results/runs/2026-10-13/OBJETIVO.md), os [textos completos](results/runs/2026-10-13/experiments/01-noticia-bibliotecas/REPORT.md) e as limitações antes de adotar. A skill não foi ajustada para favorecer os votos. Os [resultados de 10/10](results/runs/2026-10-10/README.md) e as avaliações históricas no [Git](https://github.com/larguesa/my-skills/tree/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests) permanecem preservados. Faça também sua avaliação humana.
