# Humanizador PT-BR 0.8.1

Humanizador PT-BR orienta agentes de IA a escrever e revisar textos em português brasileiro para que soem mais humanos: naturais, adequados ao gênero e fiéis aos fatos e à voz do autor.

## Propósito e critério de sucesso

**O propósito desta skill é humanizar textos. Seu sucesso é medido pela melhora no julgamento de humanização dos textos que ela produz ou revisa.**

A comparação é cega: os juízes avaliam os textos sem saber qual versão da skill os produziu. O indicador principal é a humanização percebida, com preservação dos fatos e do sentido. Menos tempo, tokens ou custo não significa sucesso da skill; essas medidas servem apenas para acompanhar a execução e não compensam um texto menos humano.

## Exemplos de uso

> Reescreva este texto gerado por IA para soar humano, sem mudar fatos nem números: [...]. Use humanizador-pt-br.
>
> Redija uma notícia curta com estes dados: [...]. Use humanizador-pt-br.
>
> Aponte os vícios de IA deste texto, sem reescrever: [...]. Use humanizador-pt-br.

**Versão distribuída: 0.8.1.** A candidata 0.9.1 foi comparada diretamente com a 0.8.1 nos mesmos cinco pedidos de redação sorteados. A execução foi interrompida por limite de concorrência do provedor, com 68 de 95 pares julgados. [Resultado de humanização, cobertura e textos completos](results/samples/2026-10-25/README.md). A reescrita ainda não foi avaliada.

## O que a skill faz pelo seu texto

- **Entrega o gênero completo.** Há 15 planos por gênero: notícia com título e lide, reportagem com atribuição e limites, nota executiva com a conclusão primeiro, além de planos próprios para ensaio, crônica, conto, proposta, e-mail, roteiro e texto acadêmico.
- **Corta os clichês de IA.** São 32 regras pesquisáveis contra enchimento ("é importante ressaltar que"), fórmulas ("no mundo atual"), jargão decorativo ("robusto", "alavancar"), autoridade fabricada ("estudos comprovam") e travessão na prosa. Os usos legítimos ficam: "ecossistema biológico" e "estatística robusta" continuam valendo.
- **Acerta o registro.** Os 12 perfis de estilo vão do técnico preciso ao literário, do executivo direto ao coloquial, cada um ligado aos gêneros em que funciona.
- **Preserva fatos e voz.** Nomes, números, datas, citações e ressalvas vêm só do pedido ou do texto-base. Na revisão, a skill muda apenas o que melhora clareza, ritmo ou precisão e mantém as frases que já funcionam.
- **Confere antes de entregar.** Um script local barra preâmbulo ("Aqui está a notícia:"), travessão e comando no lugar do texto, e aponta números e datas relativas que não estão no pedido.

## Como conferir o resultado

O [relatório da amostra 0.9.0 versus 0.8.1](results/samples/2026-10-23/README.md) reúne as notas de humanização, naturalidade e fidelidade, os votos e os textos completos lado a lado. O [histórico de avaliações](results/README.md) mantém as tentativas anteriores separadas desta comparação entre versões.

## Instalação e uso

Copie a pasta para o diretório de skills do agente e carregue [SKILL.md](SKILL.md). A subpasta `results/` é só da avaliação e pode ficar de fora. O script requer Python 3 e usa apenas a biblioteca padrão, sem API ou serviço.

São três modos. Redação: briefing sem texto-base, escrito do zero com os fatos fornecidos. Revisão: texto do usuário ou gerado por IA, reescrito só no escopo pedido, com fatos preservados. Diagnóstico: trechos, motivos e prioridades, sem versão nova.

## Recursos

- [Skill](SKILL.md): orientação editorial, regras explícitas e procedimento.
- [Catálogo](references/catalogo.json): 32 padrões pesquisáveis, com termos, sugestões e exceções. `positive_example` é o vício detectado; `negative_example` é a forma preferida, que só o retira.
- [Estilos e estruturas](references/estilos.json): 12 perfis, 15 planos por gênero com ofício e pontos de atenção, regras de material.
- [Script](scripts/humanizar.py): ferramentas locais e conservadoras.
- [24 pedidos da avaliação](results/PROMPTS.md): pedidos de redação usados no A/B.
- [Regras de avaliação](AGENTS.md): meta, protocolo A/B e critérios para aceitar ou rejeitar cada versão.
- [Avaliação](results/README.md): situação, tentativas, limites, pendências e testes de software.

## Detalhes técnicos

Referência das ferramentas locais. Clique para abrir cada parte.

<details>
<summary><strong>Como a skill orienta a escrita</strong></summary>

A orientação editorial positiva vem antes dos vetos: escrever para o leitor, reescrever o pedido em vez de copiá-lo, entregar o gênero completo, ser concreto e dar ritmo pelo sentido. Há regras explícitas contra travessão e traço substituto na prosa produzida, enchimentos, jargão decorativo e fórmulas de IA. Catálogo e estilo são aplicados antes de escrever, e a entrega é verificada antes de sair.

Cada forma preferida do catálogo só retira o vício, sem fato novo; o briefing em texto traz a orientação das regras de foco e a exceção de todas as regras; redação, revisão e diagnóstico têm instruções próprias; edição e entrega reconhecem código e citações do mesmo modo, e o travessão entre aspas só passa quando a citação está na fonte.

</details>

<details>
<summary><strong>Ferramentas no fluxo de redação</strong></summary>

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

</details>

<details>
<summary><strong>Verificação da entrega</strong></summary>

```text
python3 scripts/humanizar.py check texto.txt --briefing pedido.txt
```

Código 0: entregável. Código 1: bloqueio por comandos, chamada de ferramenta ou JSON no lugar do texto; por preâmbulo de entrega no início ("Aqui está a notícia:"), inclusive depois de uma cortesia como "Claro!" ou em negrito; ou por travessão na prosa. Comando dentro de bloco de código fechado é documentação e não bloqueia, salvo comando da própria skill. Linha que anuncia anexo ou lista da mensagem ("Seguem os documentos:") gera alerta, não bloqueio. O travessão passa em código fechado, em citação ou nome conferidos no pedido e, numa revisão com `--original texto-do-usuario.txt`, na frase mantida do autor; aspas, por si, não provam origem. `--artifact codigo` é o contrato explícito para pedido de só código, comando ou JSON; o padrão é prosa. Código 2: erro de entrada.

Alertas sem bloqueio listam ocorrências do catálogo, números presentes só no texto ou só no pedido (com sinal, percentual e ordinal, fora de blocos de código; `start` e `end` da omissão referem-se ao pedido) e dia da semana ou data relativa ausentes do pedido ("nesta quinta", "semana que vem", comparados por palavra inteira). São pontos para leitura, não prova de defeito nem de fidelidade.

</details>

<details>
<summary><strong>Auditoria e edição</strong></summary>

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

</details>
