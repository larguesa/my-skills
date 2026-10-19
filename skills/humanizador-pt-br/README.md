# Humanizador PT-BR 0.6.0

Redação, revisão e diagnóstico em português brasileiro. Regras explícitas contra travessão e traço substituto na prosa produzida, enchimentos, jargão decorativo e fórmulas de IA. Catálogo e estilo são aplicados antes de escrever, e a entrega é verificada antes de sair.

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

`brief` devolve em texto curto as 28 regras do catálogo (vício, alternativa, exceção), o perfil, o plano de blocos e o contrato de entrega. Ocupa cerca de um quarto dos dois JSONs e substitui a injeção integral deles. `--format json` entrega o mesmo conteúdo para ferramentas. Para aprofundar:

```text
python3 scripts/humanizar.py catalog --query autoridade --genre noticia --limit 5
python3 scripts/humanizar.py styles --query jornalistico --genre noticia
python3 scripts/humanizar.py structure --profile jornalistico --genre noticia --breadth 2
```

Organize os dados do pedido nos blocos do plano e só então escreva. Para variar escolhas opcionais, acrescente `--randomness 0.4 --seed 17`; `--breadth` limita cobertura opcional, preservando os blocos obrigatórios. Seed reproduz o plano local, não o texto de um modelo. O script não inventa fatos nem gera prosa pronta.

Consultas `--query` ignoram acentos e maiúsculas; `--genre` exige o identificador exato, como `relatorio` ou `noticia`. Consulte todos os perfis com `styles --limit 20`; encontre uma regra por ID com `catalog --query PTBR-21`.

Sem terminal, o agente lê os JSONs e segue direto para o texto. A resposta só é comando, chamada de ferramenta, JSON ou plano quando o pedido exige esse formato.

## Verificação da entrega

```text
python3 scripts/humanizar.py check texto.txt --briefing pedido.txt
```

Código 0: entregável. Código 1: bloqueio por saída só com comandos, chamada de ferramenta ou travessão fora de código e citação fechados, ou preâmbulo na primeira linha ("Aqui está a notícia:"). `--artifact codigo` é o contrato explícito para pedido de só código, comando ou JSON; o padrão é prosa. Código 2: erro de entrada. Alertas sem bloqueio listam ocorrências do catálogo, traço substituto, números presentes só no texto ou só no pedido e dia da semana ou data relativa ausentes do pedido. São pontos para leitura, não prova de defeito nem de fidelidade.

## Auditoria e edição

```text
python3 scripts/humanizar.py audit rascunho.txt
python3 scripts/humanizar.py rhythm rascunho.txt
python3 scripts/humanizar.py replace rascunho.txt --from "com o intuito de" --to "para"
python3 scripts/humanizar.py suggest rascunho.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py apply rascunho.txt --plan plano-aprovado.json --output revisado.txt
python3 scripts/humanizar.py verify rascunho.txt revisado.txt
```

`audit` localiza regras e repetições. `rhythm` descreve comprimentos e aberturas repetidas, sem nota de autoria. `replace` propõe substituição literal em trechos não protegidos; `suggest` usa variantes cadastradas, se houver. Ambos devolvem JSON com `approved: false`, sem alterar a entrada.

Salve o JSON retornado com a ferramenta de arquivos do agente. Leia cada trecho e seu contexto; marque `approved: true` somente nas edições aprovadas. `apply` exige hash da entrada, offsets Unicode (fim exclusivo), trecho exato e arquivo de destino novo. Exemplo de edição para a entrada literal `com o intuito de validar.`:

```json
{"input_sha256":"HASH_RETORNADO_PELO_SCRIPT","edits":[{"start":0,"end":16,"original":"com o intuito de","replacement":"para","approved":true}]}
```

`--protect "kg"` acrescenta proteção de termo ou unidade. Números, possíveis nomes, código, citações e condições recebem bloqueios heurísticos conservadores. A rotina pode recusar uma edição legítima; não contorne a proteção para forçá-la. A redação contextual pelo agente continua possível, seguida de leitura de fidelidade.

Travessão não tem substituição universal: escolha ponto, vírgula ou parênteses pela função da frase. Preserve o símbolo quando pertence a uma citação literal ou código original. `verify` verifica diferenças e inventários protegidos, não equivalência semântica nem veracidade.

## Recursos

- [Skill](SKILL.md): regras explícitas e procedimento.
- [Catálogo](references/catalogo.json): 28 padrões pesquisáveis, sugestões e exceções.
- [Estilos e estruturas](references/estilos.json): 12 perfis e planos de redação.
- [Script](scripts/humanizar.py): ferramentas locais e conservadoras.
- [24 prompts aprovados](results/PROMPTS.md): pedidos preservados, sem H1/H2.
- [Status e validação](results/README.md): testes locais separados da avaliação de escrita.
- [Revisão 0.6.0](results/REVISAO-2026-10-19.md) e [protocolo da avaliação](results/PROTOCOLO-0.6.0.md).

## Resultado prático mais recente

A [avaliação de 19/10/2026 da versão 0.6.0](results/runs/2026-10-19/README.md) produziu 31 respostas completas. Nos 9 pares avaliados pelos três juízes, H passou de 42,04 para 49,19. Nos 15 pares de geração, os tokens médios passaram de 628,33 para 6.253,07 e o tempo de API de 6,91 para 7,37 segundos. Nenhuma das 15 respostas com skill entregou apenas comandos. O Qwen Flash voltou a limitar a execução; a amostra cobre somente parte do primeiro dos 24 pedidos. Os 84 testes de software passaram.

### Histórico 0.5.1

Os números abaixo são da versão 0.5.1, preservados para consulta.

A [retomada de 13/10/2026](results/runs/2026-10-13/README.md) continua incompleta, devido ao limite temporário do Qwen Flash. Resultados parciais de uma notícia:

| Indicador | Sem skill | Com skill | Variação |
|---|---:|---:|---:|
| Humanização percebida, índice médio de 0 a 100 | 40,03 | 38,52 | −1,52 pontos (−3,79%) |
| Tokens totais por geração, média | 601,47 | 19.438,47 | +3.131,84% |
| Tempo da chamada de redação, média em segundos | 10,92 | 9,47 | −13,28% |

Humanização: 11 pares com Jev, Astra e Opus. Tokens e tempo: 15 pares de respostas completas, incluindo duas saídas que entregaram comandos de ferramenta em vez de texto. O índice é 100 menos a impressão de IA do juiz, não uma probabilidade de autoria humana. A preparação local da skill não foi cronometrada. Não houve melhora média nesta amostra; ela não sustenta uma conclusão geral.

Veja o [relatório objetivo](results/runs/2026-10-13/OBJETIVO.md), os [textos completos](results/runs/2026-10-13/experiments/01-noticia-bibliotecas/REPORT.md) e as limitações antes de adotar. A skill não foi ajustada para favorecer os votos. Os [resultados de 10/10](results/runs/2026-10-10/README.md) e as avaliações históricas no [Git](https://github.com/larguesa/my-skills/tree/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests) permanecem preservados. Faça também sua avaliação humana.
