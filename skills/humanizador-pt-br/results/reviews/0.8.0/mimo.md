# Revisão independente da skill humanizador-pt-br 0.7.0 (commit 4433074)

## Escopo e método

Leitura de `SKILL.md`, `README.md`, `scripts/humanizar.py`, `references/catalogo.json`, `references/estilos.json`, `results/test_humanizar.py` e `results/REVISAO-0.7.0.md`. Não executei testes nem rodei o script; cada afirmação de comportamento é derivada de leitura do código e marcada como **evidência** (leitura direta do arquivo) ou **hipótese editorial** (juízo sobre efeito no texto final). Não altero o histórico de resultados, os 24 prompts, os vetores de avaliação nem proponho otimização contra notas históricas.

---

# 1. Achados prioritários

## P1. `brief()` converte `positive_example` em "Evite" e `negative_example` em "Prefira" sem checar a polaridade real dos pares

**Evidência.** `scripts/humanizar.py:376-380`:

```python
# positive/negative_example seguem a polaridade do detector; aqui recebem o papel editorial.
compact = [{'id': r['id'], 'name': r.get('name', ''), 'foco': r['id'] in focus,
            'evite': r.get('positive_example'), 'prefira': r.get('negative_example'),
            ...
```

O comentário reconhece a inversão e a legitima como "papel editorial". Mas a polaridade do catálogo é **positivo = texto que o detector deve marcar** (ex.: PTBR-06 `positive_example` = "Especialistas afirmam que a mudança reduz erros no cadastro." = vício), e **negativo = exemplo limpo** (PTBR-06 `negative_example` = "Segundo a equipe de suporte, os erros de cadastro caíram pela metade em março."). O campo `avoid` da regra é literalmente o vício; a convenção está documentada por teste, não por contrato declarado no JSON.

**Bug editorial reproduzível (alta consequência para fidelidade).** Veja PTBR-06 (`catalogo.json:7`):

- `positive_example`: "Especialistas afirmam que a mudança reduz erros no cadastro."
- `negative_example`: "Segundo a equipe de suporte, os erros de cadastro caíram pela metade em março."

O briefing dirá: **`Evite: "Esterlistas afirmam que a mudança reduz erros no cadastro."` / `Prefira: "Segundo a equipe de suporte, os erros de cadastro caíram pela metade em março."`**. Isso manda o redator evitar uma frase que é **invenção de autoridade** (correto) e preferir uma frase que **inventa "equipe de suporte", "erros caíram pela metade" e "em março"** — fatos ausentes de qualquer briefing.

O teste `test_purpose_rule_example_keeps_exactly_the_facts` (`test_humanizar.py:1092-1100`) cobre **apenas PTBR-30**. As demais 31 regras com o mesmo formato de par não têm essa proteção. A REVISAO-0.7.0.md:100 admite explicitamente: *"Outros pares Evite/Prefira mostram concretude com detalhe ausente do exemplo de vício, entre eles PTBR-06 (autoridade vaga), que é regra de fidelidade. Por escopo, só PTBR-30 foi corrigido."*

**Impacto no uso real.** O brief entra no contexto do redator como "forma preferida". Um modelo tende a imitar o padrão `Segundo [fonte], [número] em [período]` como boilerplate de atribuição. É a **pior falha possível para um objetivo de fidelidade**: o briefing ensina, por exemplo, a fabricar atribuições e números.

**Pares em risco classificados por severidade (leitura dos 32 pares):**

| Regra | Risco factual do par "Prefira" | Severidade |
|---|---|---|
| PTBR-06 autoridade-vaga | "Segundo a equipe de suporte, os erros… caíram pela metade em março" | Crítica (fidelidade) |
| PTBR-08 promessa-total | "A atualização corrige a falha de login que travava o aplicativo" | Alta (inventa "atualização", "falha de login", "aplicativo") |
| PTBR-10 significancia | "O cadastro passou de cinco para dois minutos" | Alta (inventa números) |
| PTBR-30 finalidade-presumida | Corrigido em 0.7.0 | — |
| PTBR-12 gerúndio | "O botão mudou para o topo da página, onde aparece sem rolagem" | Média (inventa "sem rolagem") |
| PTBR-23 clichê-abstrato | "Precisamos reduzir de três para uma as telas do cadastro" | Média (inventa números) |
| PTBR-07 marco-histórico | "O novo botão abre o formulário na mesma tela" | Média (inventa "abre o formulário") |
| PTBR-13 incerteza | "A falha pode voltar" | Baixa (introduz "falha") |
| PTBR-16 fecho | "A versão em inglês do formulário entra no ar em março" | Média (inventa serviço, data) |

**Proposta concreta.** Duas alternativas, nesta ordem de preferência:

1. **Renomear os campos de saída** para refletir a polaridade real, e separar o par editorial do par de teste. No JSON, adicionar `editorial_pair: {avoid, prefer}` específico para o briefing, deixando `positive_example`/`negative_example` como exemplos de detecção. Risco: aumento de tamanho do catálogo.
2. **Corrigir os 8 pares acima** para que `negative_example` seja **estritamente uma sub-sequência factual do `positive_example`**, com o teste estendido de PTBR-30 para todas as regras.

Recomendo a alternativa **2** por impacto direto e menor superfície de mudança.

**Teste de regressão sugerido (unidade, `Catalog070Tests`):**

```python
def test_every_paired_example_preserves_only_facts_from_the_vice_example(self):
    import re
    rules = self.rules()
    for rule in rules:
        with self.subTest(rule=rule['id']):
            pos = set(re.findall(r'\w+', rule['positive_example'].casefold()))
            neg = set(re.findall(r'\w+', rule['negative_example'].casefold()))
            # A forma preferida não pode introduzir dado concreto novo
            # (nomes próprios, números, períodos, instrumentos ausentes do vício).
            new_concrete = {w for w in neg - pos
                            if re.match(r'^\d', w) or w in {'janeiro','fevereiro','março','abril','maio','junho',
                                'julho','agosto','setembro','outubro','novembro','dezembro'}
                            or (w.isupper() and len(w) > 2)}
            self.assertEqual(new_concrete, set(),
                f"{rule['id']}: forma preferida introduz dado concreto ausente do vício")
```

Adicional: teste de orientação (não de matcher) que garanta que "Evite" aparece antes de "Prefira" em todo par do briefing, já coberto por `test_brief_labels_examples_by_role_not_by_test_polarity` mas restrito a PTBR-25; estender para os 32 pares.

---

## P2. `suggest()` tem caminho que atribui `approved: True` antes de validar, e só revertido em `for edit in edits: edit['approved'] = False`

**Evidência.** `scripts/humanizar.py:55` e `:63-64`:

```python
edit.update(replacement=rng.choice(options), approved=True)   # linha 55
...
edits.append(edit)
if len(edits) >= 2: break
for edit in edits:
    edit['approved'] = False                                   # linha 63-64
```

O `approved=True` na linha 55 existe **apenas** porque `apply_edits()` exige `approved is True` para validar (`humanizar.py:117-118`). É uma porta dos fundos: se a função de validação for chamada diretamente com o plano intermediário de `suggest` durante o laço (ou se `apply_edits` passar a aceitar plano sem a checagem), a edição sai aprovada. **Não é um bug explorável hoje** (o retorno público sempre tem `approved: False`), mas é um contrato frágil e um sinal de que `apply_edits` não separa **validação estrutural** de **aprovação editorial**.

**Proposta concreta.** Separar em duas funções: `_validate_edits(text, edits, protected_terms)` (sem checar `approved`) e `apply_edits(text, plan, protected_terms)` que chama `_validate_edits` **depois** de exigir `approved is True`. O teste existente `test_apply_requires_hash_approval_and_exact_spans` continua válido.

**Teste de regressão sugerido:**

```python
def test_validate_edits_does_not_require_approval(self):
    h = module()
    text = 'vale destacar'
    edit = {'start': 0, 'end': 13, 'original': 'vale destacar', 'replacement': 'destaco'}
    # Não deve falhar por falta de approved
    self.assertIsInstance(h._validate_edits(text, [edit]), list)
    # apply_edits continua exigindo aprovação explícita
    with self.assertRaises(ValueError):
        h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [edit]})
```

---

## P3. `protected_spans` marca qualquer palavra com maiúscula como "possível nome", o que protege demais e destrói a usabilidade de `replace`/`apply` em texto normal

**Evidência.** `scripts/humanizar.py:93-95`:

```python
for match in re.finditer(r'\b\w+\b', text):
    if any(c.isupper() for c in match.group()):
        spans.append({'start': match.start(), 'end': match.end(), 'kind': 'possível nome'})
```

**Exemplo mínimo reproduzível (derivado de leitura):**

- Texto: `Envie o Formulário até sexta`
- `plan_replacements('Envie o Formulário até sexta', 'Formulário', 'Ficha')` não produzirá edição (o token `Formulário` tem maiúscula e cai em "possível nome").
- Idem para `HTTP`, `API`, `PDF`, `GET`, `POST`, `SQL`, `CPF`, `JSON`, `UTF`.

Não há `--protect` que relaxe isso; o README diz "A rotina pode recusar uma edição legítima; não contorne a proteção para forçá-la", o que empurra o trabalho de volta ao redator humando. É uma **decisão conservadora defensável**, mas é **muito ampla** para termos técnicos de alta frequência.

**Proposta concreta.** Duas camadas:
1. Criar lista de exceções por tipo (`sigla` quando `len <= 6 and word.isupper()`, `substantivo comum capitalizado` quando começa a frase). Reduzir "possível nome" para: token que contenha maiúscula **interna** (`McDonald`, `iPhone`) ou token que **não esteja no início de frase** e tenha maiúscula inicial.
2. Acrescentar flag `--relax-protected-nomes` (ou `--proper-nouns off`) para workflows de revisão em que o redator já verificou manualmente. Documentar no README.

**Teste de regressão sugerido:**

```python
def test_uppercase_acronym_is_not_automatically_a_protected_name(self):
    h = module()
    text = 'Use a API nova.'
    plan = h.plan_replacements(text, 'API', 'interface')
    self.assertEqual(len(plan['edits']), 1, 'Sigla comum não deve bloquear substituição')
    # Continua protegido: nome próprio com maiúscula interna
    text2 = 'O iPhone mudou.'
    self.assertEqual(h.plan_replacements(text2, 'iPhone', 'aparelho')['edits'], [])
```

(Se a decisão editorial for manter a proteção ampla, o teste acima deve ser invertido e documentado como invariante; o importante é **tornar explícito** o contrato, hoje só verbal.)

---

## P4. `check()` bloqueia travessão com `item(blocking, ...)` mesmo quando o pedido é "revisão de texto que já contém travessão"

**Evidência.** `scripts/humanizar.py:481-483`:

```python
for match in re.finditer('—', text):
    item(review if inside(match) else blocking,
         'travessao_protegido' if inside(match) else 'travessao', match)
```

O SKILL.md (`SKILL.md:35`) é explícito: "NÃO USE travessão U+2014 na prosa **produzida**". Em modo **Revisão**, o contrato diz (`SKILL.md:20`): "Preserve fatos, estrutura útil e voz", e o README (`README.md:66`) manda: "Preserve o símbolo quando pertence a uma citação literal ou código original". Mas `check` **não sabe o modo** (redação x revisão x diagnóstico). Rodar `check texto_revisado.txt` num texto do usuário que já tinha travessão em prosa comum bloqueia.

**Exemplo mínimo.** Usuário envia: `O prazo — que já venceu — foi mantido.` Revisor preserva a frase e entrega igual. `check` retorna código 1.

**Proposta concreta.** Acrescentar flag `--mode {redacao, revisao, diagnostico}` (padrão `redacao`). Em `revisao`, o travessão do original vira **alerta** (`review`), não bloqueio; a obrigação passa a ser "preservar o original, sinalizar". Idem para `saida_somente_comandos` (o modo revisão pode receber artefato com comando).

**Teste de regressão sugerido:**

```python
def test_check_revisao_mode_downgrades_existing_dash_to_review(self):
    h = module()
    rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
    text = 'O prazo — que já venceu — foi mantido.'
    self.assertFalse(h.check(text, rules)['deliverable'])
    self.assertTrue(h.check(text, rules, mode='revisao')['deliverable'])
    review_codes = {r['code'] for r in h.check(text, rules, mode='revisao')['review']}
    self.assertIn('travessao_preservado', review_codes)
```

**Hipótese editorial.** O teste real (`DeliveryCheckTests.test_real_command_only_outputs_…`) fixa os vetores de 13/10 em que `travessao` deve bloquear; a mudança acima **não altera** o comportamento do modo `redacao`, então os testes históricos permanecem válidos.

---

## P5. Conflito de contrato: SKILL.md linha 44 autoriza exceção para "uso literal" de palavra evitada, mas a `check` marca qualquer ocorrência em prosa como `catalogo`

**Evidência.** `SKILL.md:44`:

> Preserve termos técnicos e usos literais (ecossistema biológico, estatística robusta, otimização com critério). Citação, código e dado original são intocáveis, mesmo com item evitado; **sinalize a exceção**.

Mas `check()` (`humanizar.py:485-492`) classifica **toda** ocorrência de regra do catálogo em `review` (código `catalogo`), sem campo `exception` ou `justification`. O redator não tem como sinalizar no texto que aquele uso é literal.

**Exemplo mínimo.** Texto: "A **estatística robusta** é definida por Andersen." A regra PTBR-09 (`robustez-sem-criterio`) não dispara porque o regex exige `solução|sistema|plataforma|processo + robusto`; mas PTBR-22 (`vocabulario-decorativo`, `fundamenta(?:l|is)`) dispara em "um resultado **fundamental** para a estatística robusta" mesmo que seja uso técnico legítimo.

**Proposta concreta.** Acrescentar no texto um marcador de exceção que o `check` reconhece:

```
<!-- excecao: PTBR-22 termo tecnico definido em nota -->
```

ou, mais simples e menos invasivo, campo `--accept-rule PTBR-22` na CLI de `check` para o revisor sinalizar exceções já aprovadas. Hoje a única saída é ignorar o alerta, mas o contrato da skill diz "sinalize a exceção" sem dar mecanismo.

**Teste de regressão sugerido:**

```python
def test_check_accepts_explicit_rule_exceptions(self):
    h = module()
    rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
    text = 'O resultado é fundamental para a estatística robusta.'
    self.assertIn('catalogo', {r['code'] for r in h.check(text, rules)['review']})
    clean = h.check(text, rules, accept_rules=['PTBR-22'])
    self.assertNotIn('catalogo', {r['code'] for r in clean['review']})
```

---

## P6. Contradição de nomenclatura entre `estilos.json.material_types` e `estilos.json.material`

**Evidência.** `estilos.json:28-45`:

```json
"material": {
  "fatos": "Use só fatos, números, fontes e falas do pedido; ...",
  "opiniao": "Posição, raciocínio ...",
  "ficcao": "Invente cena, gestos, ..."
},
"material_types": {
  "fatos": {"label": "fato", "when_requested": "Se o pedido for fato real: ..."},
  "opiniao": {"label": "opinião", ...},
  "ficcao": {"label": "ficção", ...}
}
```

Duas chaves **quase idênticas** com conteúdo **ligeiramente diferente**. `material_types.fatos.when_requested` diz "sem acrescentar dados, fontes **ou vivências**"; `material.fatos` diz "sem acrescentar dado, finalidade, previsão, dia da semana, data relativa, fonte, serviço **ou experiência**". A distinção não está documentada; o campo `when_requested` só é usado em `brief()` (`humanizar.py:375`) para os tipos **não** padrão.

**Risco.** Editorial, não de runtime. Duas fontes da verdade para a mesma regra, que serão atualizadas em momentos diferentes.

**Proposta concreta.** Unificar num único objeto `material_types` com dois campos: `default_policy` (o texto atual de `material`) e `when_requested` (o texto atual de `material_types.X.when_requested`). Manter `material` só como mapa `estrutura → tipo_default` (ex.: `"cena": "ficcao"`), separando **qual tipo é o padrão do gênero** de **qual é a política do tipo**.

**Teste de regressão sugerido:**

```python
def test_material_policy_is_not_duplicated_across_keys(self):
    data = json.loads((SKILL_DIR / 'references/estilos.json').read_text(encoding='utf-8'))
    self.assertEqual(set(data['material']), set(data['material_types']))
    for key in data['material']:
        # Nenhuma política de tipo aparece em duas chaves.
        self.assertNotIn('acrescentar', data['material_types'][key]['when_requested'])
```

---

## P7. `brief_text` oculta `positive_example`/`negative_example` como nomes de campo, mas os mesmos valores são expostos rotulados "Evite"/"Prefira" para regras em foco, e só "termos" para as demais

**Evidência.** `humanizar.py:416-427`:

```python
for r in (by_id[rule_id] for rule_id in data['focus']):
    line = f"- {r['id']} {r['name']}. Evite: \"{r['evite']}\" Prefira: \"{r['prefira']}\""
    ...
for r in data['rules']:
    if not r['foco']:
        lines.append(f"- {r['id']} {r['name']}: " + '; '.join(r['termos'] or [r['evite']]) + '.')
```

**Bug de fallback silencioso.** Se uma regra tiver `avoid` vazio, o fallback é `r['evite']` = `positive_example` = **o vício**. O briefing passaria a listar o **vício** como se fosse a palavra a evitar, o que é redundante mas não errado. Porém, se o `positive_example` for uma frase longa (como PTBR-05: "O novo menu não é apenas uma mudança visual, mas uma nova forma de navegar."), a linha de "demais regras" vira uma frase inteira, encurtando artificialmente o espaço do briefing.

Não é bug hoje (todas as 32 regras têm `avoid` não vazio — verificado por `test_every_rule_lists_terms_and_a_concrete_preferred_form`), mas é um contrato implícito.

**Proposta concreta.** Se `avoid` for vazio, lançar `ValueError` em `load_catalog` em vez de fallback silencioso. Ou seja: `avoid` vazio é erro de configuração.

**Teste de regressão sugerido:**

```python
def test_rules_without_explicit_avoid_terms_are_rejected(self):
    h = module()
    with tempfile.TemporaryDirectory() as folder:
        catalog = Path(folder) / 'rules.json'
        catalog.write_text(json.dumps([{'id': 'x', 'pattern': 'a', 'positive_example': 'a', 'negative_example': 'b'}]), encoding='utf-8')
        with self.assertRaises(ValueError):
            h.load_catalog(catalog)
```

---

## P8. `check()` não marca como alerta a **omissão de conteúdo do pedido** (fatos presentes no briefing mas ausentes do texto)

**Evidência.** `humanizar.py:493-508`: compara números (`NUMBER` regex `\d+(?:[.,]\d+)*`) e datas relativas (`RELATIVE_DATE`), mas **não** nomes próprios, termos técnicos, condições ("se", "desde que") nem citações.

**Exemplo mínimo.** Briefing: "A Prefeitura de Vila Clara anunciou 1.200 vagas nas seis bibliotecas. Inscrições de 5 a 16 de outubro, para pessoas a partir de 12 anos." Texto: "A Prefeitura abriu 1.200 vagas em bibliotecas." — faltam "Vila Clara", "seis", "5 a 16 de outubro", "12 anos". `check` só acusaria `omissao_numerica` para "6", "5", "16" e "12" (mesmo que presentes por extenso no briefing, "seis" não é `\d+`).

**Limitação séria para o objetivo de fidelidade.** Hoje, `check` só cobre dígitos arábicos e uma lista fechada de expressões relativas de data.

**Proposta concreta.** Acrescentar ao `check` uma terceira categoria de alerta, `omissao_de_conteudo`, gerada por:
1. Extração de entidades nomeadas (heurística de maiúscula interna, como `protected_spans` já faz).
2. Extração de condições (`não`, `nunca`, `se`, `desde que`, `caso`, `a menos que`) — já protegidas por `protected_spans`, mas não comparadas com o briefing.
3. Extração de citações literais (aspas) do briefing, verificando se aparecem no texto.

Marcado como `review` (não `blocking`), porque é alerta de leitura, não prova.

**Teste de regressão sugerido:**

```python
def test_check_flags_missing_entities_from_briefing(self):
    h = module()
    rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
    briefing = 'A Prefeitura de Vila Clara anunciou 1.200 vagas nas seis bibliotecas.'
    text = 'A Prefeitura abriu 1.200 vagas.'
    report = h.check(text, rules, briefing)
    codes = {r['code'] for r in report['review']}
    self.assertIn('omissao_de_conteudo', codes)
    omitted = [r for r in report['review'] if r['code'] 'omissao_de_conteudo']
    self.assertIn('Vila Clara', ' '.join(r['original'] for r in omitted))
```

---

## P9. `verify()` retorna `protected_content_preserved` calculado com o **mesmo** `protected_spans`, mas ignora a **ordem** das ocorrências

**Evidência.** `humanizar.py:26-27`:

```python
inventories = [Counter((s['kind'], text[s['start']:s['end']]) for s in protected_spans(text, protected_terms)) for text in (original, revised)]
return {..., 'protected_content_preserved': inventories[0] == inventories[1], ...}
```

`Counter` ignora ordem. Se o texto original tiver `"Maria"` no início e `"João"` no fim, e a revisão trocar as posições, o inventário continua igual.

**Exemplo mínimo.** Original: `Maria falou com João.` Revisado: `João falou com Maria.` `verify` diz `protected_content_preserved: True`, mas as posições de pessoas foram trocadas.

**Impacto.** Baixo para redação nova; **alto** para revisão, quando o objetivo é preservar vozes e atribuições.

**Proposta concreta.** Comparar também a **sequência ordenada por posição** dos tokens protegidos:

```python
sequence_original = [text[s['start']:s['end']] for s in protected_spans(original, protected_terms)]
sequence_revised = [revised[s['start']:s['end']] for s in protected_spans(revised, protected_terms)]
return {...., 'protected_sequence_preserved': sequence_original == sequence_revised, ...}
```

Manter `protected_content_preserved` (Counter) como está, e adicionar o campo novo. Documentar no README.

**Teste de regressão sugerido:**

```python
def test_verify_reports_when_protected_order_changes(self):
    h = module()
    result = h.verify('Maria falou com João.', 'João falou com Maria.')
    self.assertTrue(result['protected_content_preserved'])  # inventário igual
    self.assertFalse(result['protected_sequence_preserved'])  # ordem mudou
```

---

## P10. `rhythm()` conta aberturas com os dois primeiros tokens, mas não ignora artigos/preposições — gera falsos positivos de "abertura repetida"

**Evidência.** `humanizar.py:338-339`:

```python
openings = Counter(' '.join(words[:2]).casefold() for words in tokens)
```

**Exemplo mínimo.** Texto: "O formulário chegou. O prazo foi mantido. O site caiu." Três frases com abertura `"o formulario"`, `"o prazo"`, `"o site"` — nenhuma contagem repetida. Mas "A empresa anunciou. A empresa confirmou." → `"a empresa"` aparece duas vezes e é reportado como `repeated_openings`. É correto, mas `"o que"` / `"a que"` / `"em que"` também conta como repetição quando são só artigo+pronome.

**Impacto editorial.** Baixo. `repeated_openings` é só descritivo (sem score), então o redator pode ignorar. Mas pode induzir a quebrar frases que não precisam.

**Proposta concreta.** Acrescentar lista de palavras funcionais e, se a abertura for toda composta por elas, usar a próxima palavra significativa. Ou: relatar também `openings_significant` desconsiderando stopwords no início.

**Teste de regressão sugerido:**

```python
def test_rhythm_openings_ignore_function_words_at_the_start(self):
    h = module()
    text = 'O formulário chegou. O prazo venceu. O site caiu.'
    report = h.rhythm(text)
    self.assertEqual(report['repeated_openings'], [])
    text2 = 'O cadastro mudou ontem. O cadastro mudou hoje.'
    self.assertEqual(h.rhythm(text2)['repeated_openings'],
                     [{'opening': 'o cadastro', 'count': 2}])
```

---

# 2. Melhorias editoriais (não bloqueantes)

## E1. Inconsistência de vocabulário: "Revisão" x "Redação" x "Diagnóstico" na SKILL.md

A seção `## Modo` (`SKILL.md:17-21`) define três modos, mas o restante da skill alterna entre "redação" (implícito) e "revisão" sem etiquetar. Por exemplo, `SKILL.md:33` ("Evite explicitamente") vale para os três modos? Em modo Diagnóstico, "não use travessão" é incoerente (o diagnóstico descreve o texto, não produz).

**Proposta.** Abre-passo por modo no topo de cada seção-chave:
- "Como escrever bem" → redação e revisão.
- "Evite explicitamente" → somente prosa **produzida** (redação e revisão que reescreve).
- "Fidelidade" → todos os modos.
- "Verificação" → redação e revisão (o diagnóstico não precisa de `check`).

---

## E2. Falta tipagem declarada para `positive_example`/`negative_example` no catálogo

`catalogo.json` não tem campo `example_polarity` ou comentário documentando a convenção. O comentário em `humanizar.py:376` é o único registro. Um editor futuro pode trocar a ordem sem perceber.

**Proposta.** Adicionar no JSON: `"example_convention": "positive_example = vício detectável; negative_example = forma preferida limpa"`. O teste `test_catalog_search_…` pode validar que esse campo existe em todas as regras.

---

## E3. Falta de cobertura de teste para os perfis `coloquial`, `informal`, `caricato` em relação a `catalogo`

`StyleTests.test_new_profiles_work_through_lookup_structure_and_suggestion_cli` (`test_humanizar.py:309-347`) cobre lookup, structure e suggest, mas **não** varre o catálogo para verificar se algum vício de PTBR-31 (clichê narrativo) é incompatível com `caricato`, que legitimamente usa hipérbole e repetição.

**Proposta editorial.** Marcar PTBR-31 e PTBR-22 com campo `"profile_exceptions": ["caricato", "literario"]` para que `audit` não sinalize como vício em produção de ficção hiperbólica.

**Teste sugerido:**

```python
def test_caricato_profile_relaxes_narrative_cliches(self):
    h = module()
    rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
    text = 'Um silêncio pesado tomou a sala, e foi ali que eu entendi tudo.'
    self.assertGreaterEqual(h.audit(text, rules)['rule_counts']['PTBR-31']['count'], 1)
    # Em ficção caricata, o clichê é escolha estilística, não vício
    filtered = [r for r in rules if r['id'] != 'PTBR-31']
    self.assertEqual(h.audit(text, filtered)['rule_counts'].get('PTBR-31', {}).get('count', 0), 0)
```

(É só um exemplo; a proposta real é o campo `profile_exceptions` processado por `audit`.)

---

## E4. README desatualizado quanto a "Variantes cadastradas" em `suggest`

`README.md:56` diz: "`suggest` usa variantes cadastradas, se houver." Mas o `catalogo.json` **não tem** campo `variants` em nenhuma regra (verificado por leitura das 32 entradas). O `suggest` sempre cai em `rule.get('replacement')` que **não existe** no catálogo real, então `options = [v for v in variants if isinstance(v, str) and v != finding['original']]` é `[]` e nenhuma edição é gerada para regras do catálogo real.

**Consequência prática.** O `suggest` do mundo real só funciona com catálogos customizados. Com o catálogo oficial, retorna sempre `edits: []`.

**Proposta.** Duas opções:
1. Acrescentar campo `variants` em cada regra do catálogo com uma ou duas substituições seguras (ex.: PTBR-14 → `{"neutro-claro": ["para", "a fim de"]}`).
2. Ou remover a promessa do README e reescrever: "`suggest` só propõe substituições quando o catálogo tiver `variants` ou `replacement`; caso contrário, retorna apenas `recommendations`."

A opção 2 é mais honesta e não força conteúdo editorial novo.

---

## E5. `structures[].material` tem valores `fatos`/`opiniao`/`ficcao`, mas o `noticia` é `fatos` mesmo sendo um gênero que **exige** material `fatos` — redundância

**Evidência.** `estilos.json:791`: `"material": "fatos"` para `noticia`. Toda a matriz atual usa `fatos` para todos os gêneros não literários. Só `cena`, `cronica` são `ficcao` e `argumento`, `ensaio` são `opiniao`. Não é bug, mas sugere que `material` poderia ser default herdado da estrutura em vez de explícito.

**Proposta editorial.** Se todos os `structures` de um `genre` herdam o mesmo `material`, movê-lo para `genre_defaults`. Se cada estrutura pode divergir (ex.: roteiro pode ser `fatos` ou `ficcao`), manter como está e documentar.

---

# 3. Testes sugeridos (consolidado)

Adicionar ao `results/test_humanizar.py` (não implementar agora):

| Teste | Classe | Propósito |
|---|---|---|
| `test_every_paired_example_preserves_only_facts_from_the_vice_example` | `Catalog070Tests` | P1 (fidelidade dos pares Evite/Prefira) |
| `test_validate_edits_does_not_require_approval` | `EditorTests` | P2 (contrato `apply_edits`) |
| `test_uppercase_acronym_is_not_automatically_a_protected_name` | `EditorTests` | P3 (proteção de siglas) |
| `test_check_revisao_mode_downgrades_existing_dash_to_review` | `DeliveryCheckTests` | P4 (modo revisão) |
| `test_check_accepts_explicit_rule_exceptions` | `DeliveryCheckTests` | P5 (exceções declaradas) |
| `test_material_policy_is_not_duplicated_across_keys` | `Material070Tests` | P6 (unificação de material) |
| `test_rules_without_explicit_avoid_terms_are_rejected` | `Catalog070Tests` | P7 (contrato `avoid`) |
| `test_check_flags_missing_entities_from_briefing` | `DeliveryCheckTests` | P8 (omissão de conteúdo) |
| `test_verify_reports_when_protected_order_changes` | `EditorTests` | P9 (ordem de protegidos) |
| `test_rhythm_openings_ignore_function_words_at_the_start` | `RhythmTests` | P10 (aberturas) |
| `test_caricato_profile_relaxes_narrative_cliches` | `StyleTests` | E3 (perfis de ficção) |

---

# 4. Verificação de requisitos preservados

| Requisito | Estado na 0.7.0 | Observação |
|---|---|---|
| Prosa nova sem travessão | ✅ `SKILL.md:35` explícito; `check` bloqueia | P4 propõe relaxamento só em modo revisão |
| Norma culta / acentuação | ✅ `SKILL.md:15, 30, 70` reitera | — |
| 12 perfis | ✅ 12 em `estilos.json:47-348`; lista única em `SKILL.md:68`; teste `test_documented_profiles_match_registered_profiles` garante | — |
| Catálogo efetivo | ✅ 32 regras, `load_catalog` valida unicidade, regex, tamanho | P5: falta mecanismo de exceção declarada |
| Redação independente ou revisão | ✅ Três modos em `SKILL.md:17-21`; `brief` para redação, `audit/replace/suggest/apply/verify` para revisão | P4: `check` não distingue modo |
| Iteração final | ✅ `SKILL.md:90-92` literal, com teste `FINAL_VALIDATION` | — |
| 24 prompts aprovados preservados | ✅ `test_skill_material_does_not_copy_approved_prompts` cobre | — |
| Histórico de resultados preservado | ✅ README mantém 0.5.1, 0.6.0, 0.7.0 | — |
| Não otimizar contra notas históricas | ✅ Esta revisão propõe melhorias de contrato, não ajuste de vieses | — |
| Não remover regras por tokens | ✅ Nenhuma remoção proposta | — |

---

# 5. Resumo executivo

A 0.7.0 tem arquitetura sólida: separação clara entre **orientação positiva** (SKILL.md "Como escrever bem"), **vetos explícitos** (lista de vícios) e **ferramentas locais** (script conservador). Os 12 perfis e as 15 estruturas estão coerentes, e os testes cobrem bem a superfície de runtime.

**O achado mais sério é P1**: o briefing converte `positive_example`/`negative_example` em "Evite/Prefira" sem inverter a polaridade quando necessário. Para 8 das 32 regras, isso **ensina o redator a fabricar fatos** (nomes, números, datas, fontes) — exatamente o que a seção "Fidelidade" proíbe. É o único achado que eu trataria como **bloqueador de release** antes de próxima avaliação.

Os demais achados (P2 a P10) são melhorias de contrato, cobertura e clareza; nenhum invalida a arquitetura. As melhorias editoriais E1 a E5 aumentam a manutenibilidade sem mudar comportamento.

Recomendo, nesta ordem:
1. **P1** (corrigir pares Evite/Prefira para preservar apenas fatos do exemplo de vício).
2. **P4 + P5** (modo revisão em `check` e exceções declaradas) — resolvem contradições entre contrato editorial e ferramenta.
3. **P2 + P3 + P9** (contratos internos do script) — reduzem superfície de erro futuro.
4. **P6, P7, P8, P10** e melhorias editoriais — polimento.

Sem execução de testes nesta revisão; cada proposta acima deve ser validada pelas suítes `test_humanizar.py`, `test_generation_eval.py` e `test_objetivo.py` antes de commit.