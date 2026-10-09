# Projeto de aperfeiçoamento do Humanizador PT-BR

## Estado e escopo do projeto

**Estado:** relatório e sete melhorias propostas registrados; implementação pendente.

Este documento reúne a análise do post, das alternativas e do código, com as sugestões de aperfeiçoamento do `humanizador-pt-br` 0.5.0. A prioridade são os itens 1 a 3 da seção de melhorias. As demais propostas são complementares e dependem de validação de utilidade.

A criação deste arquivo não modifica `SKILL.md`, scripts, catálogo, perfis ou prompts aprovados, nem autoriza executar uma avaliação com modelos. O registro das propostas não significa que elas estejam implementadas.

Data da consulta: 09/10/2026. Escopo: análise, sem alterar a skill ou executar benchmarks com modelos.

## Conclusão

O `work-humanizer` acrescenta um fluxo útil para preservar compromissos e obter material do autor. Não justifica substituir nossa skill. O `humanizador-pt-br` 0.5.0 já contém preservação factual, voz do autor, exceções por gênero, edição aprovada, proteção de texto literal e aviso explícito de que seu verificador não prova equivalência semântica. Seu registro de fontes já inclui exatamente a revisão de `blader/humanizer` usada pelo autor do post.

As melhorias mais úteis são operacionalizar a fidelidade, proteger o significado das obrigações e criar testes de reescrita em português. A quantidade de padrões removidos e a classificação de um detector não devem ser os critérios de êxito.

## Fontes e revisões

- Post: https://x.com/PawelHuryn/status/2108511822445674638
- Imagem do placar: https://pbs.twimg.com/media/HULvRFGW8AEPBsz.png
- Imagem do exemplo comentado: https://pbs.twimg.com/media/HULv-nNWkAAa3t1.jpg
- `phuryn/work-humanizer`: `819ac9925fffc20f12931cdf7a447db69163cbb2`.
- `blader/humanizer`: `225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8`, versão 3.1.0.
- `larguesa/my-skills`: `9893dbc7f4c39d6e694c4482038e04bf95c216eb`, pacote `skills/humanizador-pt-br`, versão 0.5.0.
- Emulate: API, termos e privacidade oficiais, consultados em 09/10/2026. Não foi localizado código público oficial do modelo/backend.

As duas imagens foram inspecionadas visualmente. O texto integral do post foi recuperado do HTML público do X. Clones foram lidos em diretório descartável, sem instaladores, credenciais, publicação ou mudança de infraestrutura.

## 1. O que o post demonstra

A tese é pertinente: uma edição de estilo pode alterar uma promessa, admitir uma culpa, retirar um prazo ou trocar uma hipótese por certeza. O exemplo de atendimento preserva valores, mas algumas versões passam a pedir desculpas pela cobrança, impõem uma condição para a oferta ou atribuem o dano ao cliente.

Isso não estabelece, por si, uma consequência jurídica. O significado e os efeitos jurídicos dependem do contexto. O próprio método admite não ter testado contratos ou documentos jurídicos.

### Recontagem dos números

Reagreguei os arquivos de votos publicados, sem gerar respostas novas:

- 12 textos distintos, quatro modelos julgadores, duas ordens por texto: 96 escolhas de envio.
- `work-humanizer`: 46 escolhas, 47,92%, arredondados para 48%.
- `blader/humanizer`: 19 escolhas, 19,79%, arredondados para 20%.
- Prompt simples: uma escolha, 1,04%.
- Prompt com preservação: quatro escolhas, 4,17%.
- Emulate-1: nenhuma escolha.
- Um sexto braço experimental, não lançado: 24 escolhas, 25%.
- Nenhuma versão: duas escolhas, 2,08%.

São votos sobre os mesmos textos, não 96 casos independentes nem uma taxa de aprovação isolada. Os autores desenharam o experimento, os textos são sintéticos e em inglês, os julgadores são modelos e há apenas uma geração por ferramenta por texto. O experimento não inclui nossa skill.

No vencedor, o avaliador registrou 10 omissões, seis alterações e duas adições: 18 apontamentos distribuídos por 10 dos 12 textos. Foram classificados como menores pelo avaliador. Isso não significa necessariamente que cada apontamento inviabilize o texto, mas refuta a leitura de preservação perfeita. No exemplo divulgado, fotos para entender a base da dedução viram fotos para ver o dano, perdendo parte da finalidade justificativa.

Há ainda um problema de unidade no gráfico: para alguns concorrentes, soma itens alterados e número de textos com invenção. Por isso o prompt aparece com 42, embora tenha 41 itens de omissão/alteração/adição; Emulate aparece com 120, embora tenha 117 desses itens. Não é uma contagem uniforme e deduplicada de erros.

A versão atual também contém regras acrescentadas depois da versão pontuada. E o `check.py` não participou das gerações do benchmark, pois ferramentas estavam desativadas. Testes do checker não demonstram que ele causou o ganho.

Fontes: [método](https://github.com/phuryn/work-humanizer/blob/819ac9925fffc20f12931cdf7a447db69163cbb2/evidence/README.md#L59-L85), [fórmula do gráfico](https://github.com/phuryn/work-humanizer/blob/819ac9925fffc20f12931cdf7a447db69163cbb2/evidence/charts/results.html#L6-L9), [configuração](https://github.com/phuryn/work-humanizer/blob/819ac9925fffc20f12931cdf7a447db69163cbb2/evidence/scripts/common.py#L41-L58).

## 2. Os cinco métodos da imagem

### work-humanizer

É uma skill em Markdown, acompanhada de lista de padrões e um linter Python. O linter sinaliza vocabulário, formatação e ritmo; não compara o sentido da entrada e da saída. Usa somente a biblioteca padrão.

O principal aproveitamento é listar alegações com seu grau de certeza, conferir nos dois sentidos e recorrer a perguntas ou notas quando faltam informações do autor. O texto instrucional não é infalível: um exemplo transforma contribuição em condição necessária e introduz dez anos ausentes da frase original. Não copiar exemplos automaticamente.

### blader/humanizer

É outra skill em Markdown, com código de validação do pacote, não um modelo de reescrita ou verificador semântico. Nossa referência já cobre seu commit atual.

O exemplo completo de Lisboa introduz maioria onde havia muitos viajantes, transforma possibilidade de filas longas em uma fila longa e acrescenta preferência pessoal e um absoluto sobre as pessoas não terem pressa. A skill permite acrescentar reação quando a voz a comporta. Nossa regra de não inventar opinião ou sentimento do autor deve prevalecer.

Fontes: [instruções](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/SKILL.md#L34-L45), [exemplo](https://github.com/blader/humanizer/blob/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8/README.md#L169-L191).

### “Rewrite this to sound human”

É um controle experimental de uma frase, não um repositório. No teste do autor, soa mais humano que o rascunho com frequência, mas também muda significado e pode inventar informações. Fluência não é fidelidade.

### “Rewrite this to sound human, without changing the meaning”

É o outro controle, também sem repositório. Acrescentar a ressalva reduz alguns desvios naquele conjunto, mas não especifica o que preservar nem demonstra equivalência. O método com duas chamadas e auditoria, chamado v6, é um braço distinto.

Fonte dos dois prompts: [montagem efetiva](https://github.com/phuryn/work-humanizer/blob/819ac9925fffc20f12931cdf7a447db69163cbb2/evidence/scripts/common.py#L141-L165).

### Emulate-1

É um serviço hospedado acessado por API. O repositório do teste contém o cliente HTTP, não o código do modelo. Não localizei implementação, pesos ou model card oficiais públicos. Logo, não foi possível auditar a implementação interna.

A documentação apresenta `/humanize` e `/write`, e informa que o campo `reads_human` atualmente é sempre `null`. Os termos reconhecem alterações involuntárias de significado e não garantem aprovação em detectores. A política permite ler textos e usá-los para testar e treinar modelos. Não é uma boa dependência para material confidencial.

Fontes: [API](https://www.tryemulate.ai/docs/api), [termos](https://www.tryemulate.ai/terms), [privacidade](https://www.tryemulate.ai/privacy).

### Pangram (detector, não humanizador)

Pangram é o detector usado na comparação, não uma alternativa de reescrita. Sua classificação não comprova autoria nem fidelidade. O resultado favorável obtido com material do próprio autor é uma observação do experimento, não uma garantia aplicável a outros textos ou ao português brasileiro.

## 3. Nossa skill: o que já está resolvido

- 26 regras editoriais, 12 perfis e 10 estruturas, conforme os JSONs atuais.
- Preservação de fatos, negações, condições, unidades, incerteza, atribuição e posição do autor.
- Proteção de código, citações, números, possíveis nomes, condições e termos adicionais.
- Aprovação por edição, hash e offsets, sem sobrescrever silenciosamente.
- Exceções técnicas e de gênero, norma culta, acentuação e proibição de travessão em prosa nova.
- Voz do autor acima de perfil genérico; proibição de vivência, emoção e opinião inventadas.
- Ritmo como observação editorial, não detector de autoria.
- Avaliação com modelos pendente de aprovação do protocolo. Os 24 prompts já aprovados não autorizam execução automática nem modificação silenciosa.

Rodei a suíte existente com avisos como erro: **39 testes passaram**. Isso valida os contratos testados, não a qualidade da escrita.

### Limite demonstrado do verificador

Construí sete pares mínimos adversariais, manualmente, para testar `verify`. Não são textos produzidos pela skill ou por um modelo:

1. `vamos reembolsar 45 reais` → `reembolsamos 45 reais`.
2. `podemos entregar na sexta` → `vamos entregar na sexta`.
3. `Maria pagou 45 reais a João` → `João pagou 45 reais a Maria`.
4. `cancele até 10/11 para evitar a renovação` → `cancele após 10/11 para evitar a renovação`.
5. `o custo é 45 reais` → `o custo é 45 euros`.
6. `consideramos justa a cobrança` → `pedimos desculpas pela cobrança`.
7. `acho a ferramenta pouco útil` → `acho a ferramenta inútil`.

Nos sete pares, `protected_content_preserved` foi verdadeiro e `semantic_review_needed` também foi verdadeiro. Isso está coerente com o contrato atual: o script compara inventários, não relações ou equivalência. Não é uma falsa garantia da documentação. O achado mostra por que preservar tokens protegidos não basta.

Fonte: [verify e proteção](https://github.com/larguesa/my-skills/blob/9893dbc7f4c39d6e694c4482038e04bf95c216eb/skills/humanizador-pt-br/scripts/humanizar.py#L19-L98).

## 4. Melhorias recomendadas, em ordem de prioridade

### 1. Tornar a fidelidade um contrato por afirmação

Acrescentar um registro, simples e revisável, com: quem faz, o quê, para quem, valor e unidade, prazo, estado da ação, certeza, condições, motivo, fonte e intenção da frase. Conferir entrada → saída para perdas e saída → entrada para acréscimos. Qualquer diferença material impede finalizar antes de corrigir ou obter autorização.

É uma operacionalização do princípio existente, não uma nova promessa de equivalência automática. No trecho contratual ou científico, manter a formulação quando não houver alternativa seguramente equivalente.

### 2. Explicitar compromissos e atos de fala

Criar exemplos PT-BR para: reconhecer insatisfação versus pedir desculpas pela cobrança; poder versus prometer; propor versus aprovar; planejar versus concluir; oferecer versus impor condição; explicar um dano versus atribuir culpa ao destinatário. Proteger também destinatário, elegibilidade, intensidade da opinião e alcance de quantificadores, como muitos versus maioria.

Critério: nenhuma mudança material desses elementos pode ser aceita apenas porque ficou mais natural.

### 3. Melhorar a saída e os alertas do verificador

Deixar explícito no JSON que o inventário foi preservado, mas a equivalência semântica não foi avaliada. Considerar um campo como `semantic_status: not_evaluated`, sem quebrar consumidores existentes.

Ampliar alertas para quantia vinculada à moeda/unidade, expressões de prazo, modalizadores e estado da ação. Isso ajuda a localizar risco; não substitui revisão de significado nem prova quem fez o quê. Incluir os sete pares adversariais como regressões de limite do mecanismo e como casos da futura avaliação semântica.

### 4. Criar um modo de entrevista pontual

Quando faltarem opinião, episódio, número ou resultado que só o autor conhece, perguntar sobre a lacuna concreta. Não perguntar por ritual quando o briefing já basta, não repetir informações recuperáveis e permitir pular. Resposta ausente produz texto menos específico, nunca invenção.

Para Ricardo no chat, manter uma pergunta por vez. A entrevista pode ser opcional; não copiar a rodada obrigatória de cinco perguntas de outro fluxo.

### 5. Tratar notas e transcrições como material principal

Conservar sequência do raciocínio, ligações de causa e contraste, vocabulário característico e frases boas do autor. Usar um rascunho de IA apenas como lista secundária de pontos, não como estrutura obrigatória. Resolver contradição factual relevante com o autor, sem escolher silenciosamente a versão mais conveniente.

Esse fluxo detalha “a voz do autor prevalece” sem impor informalidade ou erros. Avaliar autoria editorial e clareza, não aprovação em detector.

### 6. Aprimorar a revisão de estrutura sem impor fórmulas

Além de palavras e ritmo, conferir redundância entre parágrafos, progressão do argumento, explicação que apenas repete o exemplo e repetição de abertura no fechamento. Não acrescentar causalidade só para ligar frases.

Preservar listas, conectores e explicações quando servirem ao gênero, sobretudo em ensino e documentação. Manter edição conservadora por padrão; recomposição maior e versão curta são opções, não obrigações. Não acrescentar um rodapé “Shorter option” a todo texto.

### 7. Medir melhora real em PT-BR

Propor um complemento de reescrita ao protocolo existente, sem alterar os 24 prompts aprovados. Incluir textos já bons e casos críticos de atendimento, proposta, negociação, ciência e opinião.

Comparar baseline atual, versão proposta, work-humanizer e os dois prompts de controle. Usar o mesmo modelo, contexto, configuração e acesso às ferramentas. Se houver entrevistas, fornecer as mesmas informações aos demais braços ou reportar essa vantagem separadamente.

Fidelidade material é critério eliminatório. Naturalidade, voz, clareza, tempo de revisão, latência e custo são métricas separadas. Contar desvios deduplicados por gravidade e por texto; usar mais de uma geração e revisão humana dos compromissos críticos. Não somar itens e textos numa única taxa. Executar somente após aprovação do protocolo.

## 5. O que não importar

- Listas inglesas ou limites numéricos de ritmo como regra universal de PT-BR.
- Promessa de texto indetectável ou de preservação perfeita.
- Opinião, sentimento, anedota, erro ou gíria adicionados para simular personalidade.
- Reescrita integral e entrevista obrigatórias.
- Exclusão de informação verdadeira apenas porque parece clichê.
- Instalação de um serviço externo que recebe textos confidenciais.

## Evidências locais

Os resultados de teste, os sete pares construídos, a recontagem e os pareceres técnicos foram preservados no arquivo de entregas da análise original; esses artefatos não estão incluídos neste documento. A recontagem apenas lê os dados publicados. Na análise, nenhuma inferência nova, avaliação de detector ou benchmark pago foi executada.

**Recomendação:** aperfeiçoar nossa skill, mantendo sua base PT-BR e controles existentes. Priorizar os itens 1 a 3; os demais dependem de validação de utilidade, não de importação integral do pacote.
