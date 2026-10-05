# Fontes, rastreabilidade e limites

Registro de consulta desta implementação. Fontes públicas acessadas em 29/09/2026; páginas e branches são mutáveis. IDs abaixo correspondem ao campo `source` do catálogo. A redação das regras, exceções e exemplos é própria. Não se importaram listas como verdade estatística nem se reproduziu um corpus.

## Aplicação na redação e na revisão

Estas referências explicam a origem das heurísticas de escrita. Não são fontes sobre o assunto de um artigo, notícia ou proposta, e não autorizam atribuir fatos aos seus autores. Na redação, use o catálogo para evitar fórmulas desde o rascunho; na revisão, inspecione ocorrências sem tratar palavras como proibidas.

A base factual é o contexto disponível da tarefa: briefing, documentos lidos e fontes já verificadas. Não invente estudos, entrevistas, links ou experiências para tornar o texto concreto. Exemplos linguísticos não fornecem dados reais reutilizáveis. Em ficção, a invenção se limita ao gênero autorizado.

O script opera sobre texto já escrito, inclusive um rascunho criado pela skill; não redige nem verifica fatos ou fontes.

## Referências editoriais

| ID | Fonte primária consultada | Aproveitamento | Limite |
|---|---|---|---|
| `blader` | [blader/humanizer](https://github.com/blader/humanizer), [README bruto](https://raw.githubusercontent.com/blader/humanizer/main/README.md) | Categorias de inflação, encenação, autoridade vaga e resíduos de conversa; preservação de fatos e voz. | Guia editorial baseado no contexto da Wikipedia e no inglês. Não importar frequências, ranking de sinais ou teste divulgado como validação PT-BR. |
| `aboudjem` | [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill), [README bruto](https://raw.githubusercontent.com/Aboudjem/humanizer-skill/main/README.md) | Separação entre auditoria, comparação factual e orientação de voz. | Não importar score 0 a 100, limiares ou interpretação de autoria. Retenção lexical não assegura equivalência semântica. |
| `mackswendhell` | [mackswendhell/humanizer-pt-br](https://github.com/mackswendhell/humanizer-pt-br), [README bruto](https://raw.githubusercontent.com/mackswendhell/humanizer-pt-br/main/README.md) | Candidatos em português: preenchimento, ganchos artificiais, tom promocional e fechos. | Adaptação editorial, não estudo controlado de frequência. Não autoriza criar uma personalidade fictícia. |
| `rpiochi` | [rpiochi/humanizer-pt-br](https://github.com/rpiochi/humanizer-pt-br), [README bruto](https://raw.githubusercontent.com/rpiochi/humanizer-pt-br/main/README.md) | Conectivos, qualificações, jargão e exemplos de registro brasileiro. | Exemplos da fonte não são fatos. Algumas reescritas exemplificadas acrescentam especificidade ausente no antes; essa prática não foi adotada. |
| `meta-unslop` | Meta RAM, [Towards RL for Superhuman Text: Unslopping AI](https://facebookresearch.github.io/RAM/blogs/unslop/) | Adequação à função da seção, seleção de informação e cuidado com juiz que premia cobertura e polimento. | Relato de RL-XAR dos próprios autores. Rubricas e resultados daquele experimento não calibram este catálogo, não demonstram ganho em PT-BR e não foram reproduzidos aqui. |

A versão local previamente disponível de Humanizer divergia do README público atual. Não se fixou um número universal de padrões nem se transplantaram comandos de instalação. Para reprodução histórica rigorosa, registrar commit e hash dos documentos usados na próxima calibração.

## Fontes comerciais: geradoras de hipóteses

| ID | Página consultada | Candidatos úteis | O que não adotar |
|---|---|---|---|
| `undetectable` | [Palavras comuns em IA](https://undetectable.ai/blog/br/palavras-comuns-em-ia/) | Vocabulário abstrato e frases intercambiáveis entre temas. | Identificação de autoria por palavra, promessa de indetectabilidade e afirmações promocionais de desempenho. |
| `justdone` | [Palavras e frases comuns de IA](https://justdone.com/pt/blog/ai/common-ai-words) | Aberturas genéricas, ressalvas vazias, robustez sem critério e jargão. | Generalizações regionais sobre brasileiros, troca mecânica de conectivos e redução de termos técnicos a sinônimos vagos. |
| `winston` | [Palavras mais comuns do ChatGPT](https://gowinston.ai/pt-br/most-common-chatgpt-words/) | Repetição estrutural e alerta de que palavras isoladas não provam autoria. | Precisão comercial anunciada, probabilidades de detector e recomendação de impor opiniões ou experiências. |

Esses fornecedores vendem produtos relacionados ao problema descrito. As páginas consultadas não sustentam uma estimativa reproduzível de prevalência no universo PT-BR, controlada por gênero, fonte e modelo. Concordância entre blogs não é replicação independente. Toda regra derivada permanece `heuristica_editorial`.

## Dados candidatos

### PTDetect

Fonte: [GSalimp/PTDetect](https://github.com/GSalimp/PTDetect), [README](https://raw.githubusercontent.com/GSalimp/PTDetect/main/README.md).

O projeto descreve artigos jornalísticos humanos, gerados e reescritos por IA, com classes 0, 1 e 2. A distinção de reescrita é útil: textos derivados do mesmo original não são observações independentes. Separar por artigo-fonte, manter humano e derivados na mesma partição e procurar duplicatas aproximadas antes de medir.

O README menciona `Articles/`, mas a consulta ao endpoint público desse diretório retornou 404; a árvore `main` consultada não apresentou arquivos CSV ou JSON. Portanto, não houve exploração de linhas de PTDetect nesta etapa. A existência descrita de dados não demonstra disponibilidade nem direitos de redistribuição. A licença MIT indicada pelo projeto não deve ser presumida para os artigos jornalísticos de terceiros.

Vieses esperados a investigar, não medir por suposição: veículo, tema, época, tamanho, prompts e modelos de geração, procedimentos de reescrita, seleção editorial e possível vazamento entre splits. Não extrapolar jornalismo para email, literatura ou documentação técnica.

### Corpus PT-BR v1

Fonte: [Madras1/corpus-ptbr-v1](https://huggingface.co/datasets/Madras1/corpus-ptbr-v1), [dataset card](https://huggingface.co/datasets/Madras1/corpus-ptbr-v1/raw/main/README.md).

A card apresenta `text`, `source`, `subset`, `word_count`, `char_count` e `language`, configuração `default` e split `train`. Descreve `real` proveniente de C4/FineWeb2 e `synthetic` de vários modelos e pipelines. Esses são rótulos de proveniência do fornecedor, não autenticação de autoria de cada documento. Web pode conter IA; dados sintéticos podem reproduzir trechos humanos.

A card relata filtragem SBERT orientada por rótulos de juiz LLM no material real, geração sintética por prompts e deduplicação exata por hash. Isso introduz seleção e assimetria entre subsets; não torna os grupos comparáveis. Hash exato não detecta paráfrases, espelhos, republicações ou derivados. O schema apresentado não basta para recuperar autor, URL, prompt e par original de toda linha; registrar ausências, não inventá-las.

Licença declarada: ODC-By 1.0. Trata-se de licença de base de dados, não de cessão indiscriminada dos direitos autorais de páginas web incorporadas. Conferir atribuição, termos upstream, finalidade, privacidade e direitos de redistribuição antes de publicar amostras. Acesso público não equivale a domínio público.

Não baixar o corpus inteiro como pré-requisito. Usar preview ou streaming estritamente limitado por linhas e bytes, registrando revisão, seleção e falhas. A consulta inicial ao endpoint `/rows` com cinco linhas retornou HTTP 500; isso não prova indisponibilidade permanente. A exploração limitada permanece no [histórico anterior à revisão](https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242/skills/humanizador-pt-br/tests/historico-20260929/exploracao-amostral.json): amostra de conveniência apenas de `real`/`c4_pt`, sem grupo sintético comparável. Não republica texto original. Seus valores são descritivos e não calibram o catálogo.

## Decisões de adaptação

- Não há blacklist. Termos técnicos, citações, procedimentos e vozes autorais têm exceções explícitas.
- Regras sinalizam ocorrências para inspeção, sem score de autoria, peso de suspeita ou remoção automática.
- Exemplos inventados demonstram formas linguísticas. Não reutilizar seus detalhes como informação verificada.
- Nenhum ganho de custo, qualidade ou ranking é inferido das fontes. Qualquer alegação futura exige execução registrada.
- Esta documentação é original e atribui suas referências. Licenças de projetos citados não licenciam automaticamente este pacote ou textos de terceiros.
