# Auditoria editorial do piloto — corte parcial

**Avaliação por assistente, não humana e não cega. Sem notas e sem detector de IA.**

- Corte UTC: `2026-09-29T13:49:32.876541+00:00`. Snapshot: 55 registros, 54 concluídos e 1 em andamento excluído.
- Triagem literal: **54 saídas**, 14 modelos; **1 falha** (ausência de `Aurora`). As outras 53 preservam os identificadores, o que não prova fidelidade semântica.
- Inspeção semântica: **12 saídas**, 12 modelos, 4 por braço (`simple`, `skill`, `skill_audit`), modos on/off: 8/4.
- **1 saída deve ser rejeitada**, a mesma da falha literal. Nas outras 11 inspecionadas não identifiquei alteração material; uma exige atenção editorial.
- Todos os concluídos eram `comunicado`. Não havia diversidade de casos disponível neste corte.
- Nos 54 registros, original = fonte congelada, edited = conteúdo da resposta, finish_reason = stop. Essas verificações não certificam significado.

## Fonte e método

O nome solicitado `cases.json` não existe. Li o arquivo real `../references/casos.json` com os quatro casos artificiais. Não alterei a fonte. SHA-256: `4a8c9986519656d7dde5608ccd2b2c68e2459e42c449c1da9de88e1b0f48b8eb`.

Snapshot integral em memória, SHA-256 `3e446701335d449494f086855907fd003f4630646caaa2e9abf175abc49af108`. O JSON desta auditoria preserva as 54 saídas usadas e seus checks, não inclui payloads ou raciocínio dos candidatos. A leitura paginada inicial foi seguida do corte integral; não houve atualização da amostra durante a revisão.

Teste literal: substring exata dos `literal_invariants`, sensível a maiúsculas. Ausência de menção a relatórios/dados e possível ampliação da indisponibilidade do portal foram procuradas por regex: nenhum sinal encontrado. **Sinais são triagem, não prova semântica**; não detectam toda mudança de sentido. A seleção priorizou falhas/sinais, modelos distintos e equilíbrio entre braços/modos, com desempate na ordem do snapshot. É intencional e não aleatória.

## Evidências das 12 inspeções

### 1. openai/gpt-6-luna | simple | on

ID: `9a0ae329f1e1cb7113c4346976fc0baf0e10aacac89175f45d163d6ee2bcc6a7`. Caso: `comunicado`. **rejeitar**.

- Fatos: Omite a equipe Aurora, presente no original e exigida literalmente. Mantém 14 de maio, 8h–9h30, relatórios, dados salvos e contato.
- Função: A lista facilita localizar data/horário/contato, mas elimina a identificação do responsável.
- Trecho: “**Dados salvos:** não serão alterados.”

### 2. xiaomi/mimo-v2.6-pro | skill | off

ID: `8199ebf40a2841dc287b43dd93ad94f8c33b4a2152e9643e8cf9ffe8ee01fd99`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Preserva Aurora, data, intervalo, indisponibilidade dos relatórios nesse período e a frase sobre dados salvos; não acrescenta objetivo técnico.
- Função: Título e parágrafos curtos preservam a função de aviso; remove promoção sem perda operacional.
- Trecho: “Nesse período, o acesso aos relatórios ficará indisponível.”

### 3. anthropic/claude-opus-5.5 | skill_audit | on

ID: `148cb83650159eb92670a64e1e02688307127792ba7d9a132128f75f390252b3`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Mantém responsável, data, intervalo, relatórios, dados salvos e contato. O fechamento promocional já existia na fonte; não é fato técnico novo.
- Função: Campos tornam o aviso consultável, mas a retórica sobre jornada digital permanece.
- Trecho: “**Responsável:** equipe Aurora”

### 4. xiaomi/mimo-v2.6-flash | simple | off

ID: `006f76857dd42d68e338a490ade24f481af0945b37103245cf4f9e7d596c98f4`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Mantém Aurora, data e horários; liga a indisponibilidade ao período e preserva os dados. A promessa vaga de jornada digital vem do original.
- Função: Aviso organizado; a frase promocional interrompe o caminho até o contato, sem mudar os fatos.
- Trecho: “Durante esse período, o acesso aos relatórios ficará indisponível.”

### 5. openai/gpt-6-astra | skill | on

ID: `622fd28e461fd7b337906a3aa6eb46495989210033c78eda16286af3bb691c32`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Preserva equipe, data, janela, acesso aos relatórios, dados e contato. Refraseia a avaliação promocional como “A atualização é um passo fundamental”, sem fornecer mecanismo técnico novo.
- Função: Lista permite consulta rápida; promoção permanece e a oposição “não apenas” desaparece, sem perda operacional material identificada.
- Trecho: “**Dados salvos:** não serão alterados.”

### 6. qwen/qwen3.8-flash | skill_audit | off

ID: `02e9425326fe2f8d55cfedd0a9979a0bd25d6dcaf4e67c43e9ee1d0333396f66`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Preserva Aurora, data, intervalo, relatórios do portal interno e contato. “A manutenção não altera os dados já salvos” conserva a ressalva, em presente.
- Função: Formato compacto depende da leitura conjunta dos campos para ligar horário e indisponibilidade; o vínculo continua compreensível.
- Trecho: “**Indisponibilidade:** Acesso aos relatórios do portal interno”

### 7. x-ai/grok-4.7 | simple | on

ID: `11f96c378aa902e3dd35d5f4bcc8d31a71f5f56fee47fd97db07f151e386547f`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Preserva equipe, data, janela, acesso aos relatórios, integridade dos dados e contato, inclusive a retórica já presente.
- Função: Antecipar data e horário ajuda; o parágrafo único e a promoção conservada limitam a economia editorial.
- Trecho: “No dia 14 de maio, das 8h às 9h30, a equipe Aurora realizará uma manutenção no portal interno.”

### 8. deepseek/deepseek-v4.1-flash | skill | off

ID: `5f5b7efd12a5ef25b7d7505e9226500a9367f630690664883bb98cf3fd867efe`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Mantém Aurora, data, janela, indisponibilidade restrita ao acesso aos relatórios e dados inalterados; nenhum objetivo técnico adicionado.
- Função: Parágrafo direto cumpre a função do comunicado e remove a promoção.
- Trecho: “Durante esse período, o acesso aos relatórios ficará indisponível.”

### 9. google/gemini-3.8-flash | skill_audit | on

ID: `f09de525197f8cd66793163c8ad61ca5d1109a0d7527722f07243c3362e5955f`. Caso: `comunicado`. **ressalva_editorial_sem_rejeicao_material**.

- Fatos: Preserva fatos operacionais. “para otimizar nossa jornada digital” transforma a promoção original em finalidade explícita, mas usa conteúdo da própria fonte e não inventa objetivo técnico específico. “Garantia” reforça uma ressalva que já era categórica.
- Função: Campos facilitam consulta; abertura promocional e rótulo “Garantia” merecem revisão editorial, não demonstram por si invenção factual.
- Trecho: “A equipe Aurora realizará uma manutenção no portal interno para otimizar nossa jornada digital.”

### 10. meta/muse-spark-1.3 | simple | on

ID: `6f7b339080ac13069e3e1d2a4f0759399802151fbe7f4931150ab6a1301a050b`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Mantém responsável, data, janela, relatórios, integridade dos dados e contato. A frase promocional é conservada da fonte.
- Função: Aviso em campos cumpre a função; retórica desnecessária permanece antes do contato.
- Trecho: “Responsável: equipe Aurora”

### 11. z-ai/glm-5.3-prime | skill | on

ID: `22a9ea5eec0ee026c592f804e2c464cbeb43983f0b82b293942fc5bdf8345542`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Preserva Aurora, 14 de maio, 8h e 9h30, indisponibilidade dos relatórios durante o período, dados e contato.
- Função: Cabeçalho e campos destacam informações operacionais sem acrescentar finalidade técnica.
- Trecho: “Durante esse período, o acesso aos relatórios ficará indisponível. Os dados já salvos não serão alterados.”

### 12. qwen/qwen3.8-max-prime | skill_audit | on

ID: `2217687deea9cbddc40ddd87376e6fec734ca80fabb754d6b706dcbee99208b6`. Caso: `comunicado`. **sem_falha_material_identificada**.

- Fatos: Mantém equipe Aurora, data, intervalo, acesso aos relatórios durante a janela, dados inalterados e contato.
- Função: Campos elípticos preservam a função; não ampliam a indisponibilidade para todo o portal.
- Trecho: “Indisponibilidade: acesso aos relatórios durante a janela de manutenção”

## Rejeição e limites

Rejeitar `9a0ae329f1e1cb7113c4346976fc0baf0e10aacac89175f45d163d6ee2bcc6a7`: a saída não contém `Aurora` e elimina quem realizará a manutenção, apesar da exigência literal. Não é apenas uma preferência estilística.

- Avaliação automatizada por assistente, não humana e não cega; modelos e braços estavam visíveis. Não foram atribuídas notas.
- Snapshot inicial em memória; execução concorrente pode ter produzido novos resultados depois do corte. Não representa o piloto concluído.
- Todos os 54 resultados concluídos eram do caso comunicado. Não foi possível diversificar casos; nota-tecnica, ensaio e mensagem não tinham resultados concluídos nesse snapshot.
- Amostra semântica intencional, não aleatória: primeiro falhas literais/sinais, depois modelos novos, equilíbrio de braços e de modos; empate pela ordem do snapshot. Não permite ranking, efeito causal ou generalização.
- Invariantes literais por substring exata, sensível a maiúsculas; não verificam relações semânticas. Os sinais regex são triagem, não prova semântica; ausência de sinal não comprova fidelidade.
- Fidelidade significa correspondência à fonte fictícia congelada, não verificação de fatos do mundo. Sem detector de IA, inferência de autoria ou alegação de percepção humana.
- cases.json não existe na árvore frozen-source. Foi usado o arquivo real references/casos.json, que contém cases, literal_invariants e semantic_invariants; nome e hash registrados, sem renomear.
- Somente 12 saídas receberam inspeção semântica; os demais resultados têm apenas verificações mecânicas. Nenhuma nova chamada paga, acesso a chaves ou alteração do código/estado.

**Conclusão:** falha concreta de omissão em uma saída. Sem base para ordenar modelos, atribuir ganhos à skill ou aprovar automaticamente o restante do piloto.
