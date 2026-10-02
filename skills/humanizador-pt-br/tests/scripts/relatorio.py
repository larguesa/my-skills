#!/usr/bin/env python3
"""Renderiza somente evidências reais em Markdown, sem inferência ou correção."""
from collections import defaultdict
from decimal import Decimal
from html import escape
import json
from pathlib import Path
import re
import sys
import contos as c

TESTS = Path(__file__).resolve().parents[1]
ROOT = TESTS.parent


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def cell(value):
    return escape(str(value), quote=False).replace('|', '\\|').replace('\r\n', '\n').replace('\n', '<br>')


def results():
    config = c.checked_config(TESTS / 'frozen/config.json')
    state = load(TESTS / 'results/generation-state.json')
    plan = load(TESTS / 'results/generation-plan.json')
    import continuar
    expected = continuar.amended_calls(c.generation_calls(config, TESTS / 'frozen'), TESTS / 'results')
    if plan['calls'] != expected or c.b.digest({k: v for k, v in plan.items() if k != 'fingerprint'}) != plan['fingerprint'] or state['plan_fingerprint'] != plan['fingerprint']:
        raise ValueError('effective plan mismatch')
    records = state['records']
    expected_by_id = {call['id']: call for call in expected}
    if any(any(record.get(key) != value for key, value in expected_by_id.get(record['id'], {}).items()) for record in records):
        raise ValueError('generation request metadata differs from effective plan')
    if len({r['id'] for r in records}) != len(records) or {r['id'] for r in records} != {r['id'] for r in expected}:
        raise ValueError('missing or duplicate generation slots')
    if any(r['edited'] != r['response']['choices'][0]['message']['content'] or r['finish_reason'] != 'stop' for r in records):
        raise ValueError('published generation differs from raw response')
    if len(records) != len(config['cases']) * len(config['routes']) * 2 or any(r['status'] != 'completed' for r in records):
        raise ValueError('generation incomplete')
    tables = []
    for case in config['cases']:
        anon = load(TESTS / ('results/mapping-' + case['id'] + '.json'))
        expected_anon, expected_mapping = c.anonymous_case(config, state, case['id'])
        if anon != {'state': expected_anon, 'mapping': expected_mapping}:
            raise ValueError('anonymous mapping mismatch')
        mapping, paired = anon['mapping'], anon['state']['pares']
        jev = load(TESTS / ('results/jev-' + case['id'] + '.json'))
        if jev['status'] != 'completed' or jev['request'] != c.decisions_payload(expected_anon):
            raise ValueError('decision request mismatch')
        scores = {'Jev': c.validate_judge(jev['response'], expected_anon, True)}
        if scores['Jev'] != jev['judgment']:
            raise ValueError('decision scores differ from raw response')
        for name in ('astra', 'opus'):
            raw = load(TESTS / ('results/' + name + '-' + case['id'] + '-state.json'))['records'][0]
            if raw['status'] != 'completed' or raw['payload']['messages'][1]['content'] != json.dumps(expected_anon, ensure_ascii=False):
                raise ValueError('judge input mismatch')
            text = raw['response']['choices'][0]['message']['content'].strip()
            if text.startswith('```'):
                text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
            scores[name.title()] = c.validate_judge(json.loads(text), expected_anon)
            if scores[name.title()] != load(TESTS / ('results/judgment-' + name + '-' + case['id'] + '.json')):
                raise ValueError('judge scores differ from raw response')
        rows = []
        for route in config['routes']:
            keys = {v['arm']: tid for tid, v in mapping.items() if v['model'] == route['model'] and v['mode'] == route['mode']}
            tids = set(keys.values())
            pid, pair = next((pid, p) for pid, p in paired.items() if set(p.values()) == tids)
            detection = {}
            for name, judgment in scores.items():
                pref = judgment['preferencia'][pid]
                choice = 'empate' if pref == 'empate' else mapping[pair[pref]]['arm']
                detection[name] = {arm: judgment['deteccao'][keys[arm]] for arm in ('original', 'skill')}
                detection[name]['preference'] = choice
            original, skill = [next(r for r in records if r['model'] == route['model'] and r['mode'] == route['mode'] and r['case'] == case['id'] and r['arm'] == arm)['edited'] for arm in ('original', 'skill')]
            row = dict(model=route['model'], mode=route['mode'], original=original, skill=skill,
                       detection=detection)
            rows.append(row)
        tables.append((case, rows))
    return config, records, tables


def table_blocks(tables, selected=None):
    out = []
    for case, rows in tables:
        out.extend(['## ' + case['title'], '', '**Prompt original**', '', '> ' + case['prompt'], '',
                    '| Modelo | Resposta original | Resposta com skill | Detecção Jev | Detecção Astra | Detecção Opus 5.5 |', '|---|---|---|---|---|---|'])
        for row in rows:
            if selected is not None and (row['model'], row['mode']) not in selected:
                continue
            label = row['model'] + (' (raciocínio ligado)' if row['mode'] == 'on' else ' (raciocínio desligado solicitado)')
            detection = []
            for name in ('Jev', 'Astra', 'Opus'):
                data = row['detection'][name]
                choice = {'original': 'original', 'skill': 'com skill', 'empate': 'empate'}[data['preference']]
                detection.append(f"{data['original']:.1f} → {data['skill']:.1f}; prefere {choice}")
            out.append('| ' + ' | '.join(cell(x) for x in (label, row['original'], row['skill'], *detection)) + ' |')
        out.append('')
    return '\n'.join(out)


def aggregate_results(tables):
    rows = [row for _, entries in tables for row in entries]
    if not rows:
        raise ValueError('empty judgment sample')
    out = {}
    for name in ('Jev', 'Astra', 'Opus'):
        data = [row['detection'][name] for row in rows]
        n = len(data)
        out[name] = dict(
            pairs=n,
            original_mean=sum(d['original'] for d in data) / n,
            skill_mean=sum(d['skill'] for d in data) / n,
            delta_mean=sum(d['skill'] - d['original'] for d in data) / n,
            lower=sum(d['skill'] < d['original'] for d in data),
            equal=sum(d['skill'] == d['original'] for d in data),
            higher=sum(d['skill'] > d['original'] for d in data),
            **{choice: sum(d['preference'] == choice for d in data) for choice in ('skill', 'original', 'empate')})
    return out


def aggregate_block(tables, records, judge_calls):
    # ponytail: interpretação desta rodada congelada; revisar a síntese antes de publicar outra rodada.
    stats = aggregate_results(tables)
    pairs = sum(len(rows) for _, rows in tables)
    judgments = pairs * len(stats)
    out = ['## Resultados consolidados', '',
           f'Esta consolidação considera somente a rodada de contos, sem misturar o histórico anterior: {len(tables)} pedidos, '
           f'{len({r["model"] for r in records})} modelos, {len({(r["model"], r["mode"]) for r in records})} configurações de modelo/raciocínio, '
           f'{len(records)} textos e {pairs} pares sem/com skill. Os três juízes avaliaram todos os pares: '
           f'**{judgments} julgamentos de pares e {judgments * 2} índices individuais**, obtidos em {judge_calls} chamadas de julgamento em lote.', '',
           '### Impressão de escrita por IA', '',
           f'Índice de 0 a 100, não uma probabilidade de autoria. Cada média usa os mesmos {pairs} pares do respectivo juiz. '
           'Variação = com skill menos original, em pontos do índice. A última coluna conta pares com índice menor, igual ou maior na versão com skill.', '',
           '| Juiz | Média original | Média com skill | Variação média (pontos) | Pares: menor / igual / maior |',
           '|---|---:|---:|---:|---:|']
    for name, data in stats.items():
        label = 'Opus 5.5' if name == 'Opus' else name
        out.append(f'| {label} | {data["original_mean"]:.2f} | {data["skill_mean"]:.2f} | {data["delta_mean"]:+.2f} | {data["lower"]} / {data["equal"]} / {data["higher"]} |')
    out.extend(['', '### Preferência de leitura', '',
                'A preferência foi julgada separadamente do índice de impressão de IA. Percentuais usam o total de julgamentos indicado em cada linha.', '',
                '| Juiz | Prefere com skill | Prefere original | Empate |', '|---|---:|---:|---:|'])
    total = dict(pairs=judgments, **{choice: sum(d[choice] for d in stats.values()) for choice in ('skill', 'original', 'empate')})
    for name, data in [*stats.items(), (f'Total ({judgments} julgamentos)', total)]:
        label = 'Opus 5.5' if name == 'Opus' else name
        out.append('| ' + ' | '.join([label, *(f'{data[choice]}/{data["pairs"]} ({data[choice] / data["pairs"] * 100:.1f}%)' for choice in ('skill', 'original', 'empate'))]) + ' |')
    out.extend(['', '| Conto | Pares | Prefere com skill | Prefere original | Empate |', '|---|---:|---:|---:|---:|'])
    for case, rows in tables:
        case_stats = aggregate_results([(case, rows)])
        n = len(rows) * len(case_stats)
        counts = {choice: sum(d[choice] for d in case_stats.values()) for choice in ('skill', 'original', 'empate')}
        out.append('| ' + ' | '.join([cell(case['title']), str(len(rows)), *(f'{counts[choice]}/{n} ({counts[choice] / n * 100:.1f}%)' for choice in ('skill', 'original', 'empate'))]) + ' |')
    out.extend(['', '### Verificações mecânicas', '',
                'Contagem por separação em espaços, incluindo títulos. Estes critérios não medem continuidade narrativa, voz ou fidelidade semântica ao pedido.', '',
                '| Critério | Original | Com skill |', '|---|---:|---:|'])
    for label, check in (
            ('Entre 80 e 120 palavras', lambda text: 80 <= len(text.split()) <= 120),
            ('Sem travessão longo', lambda text: '\u2014' not in text),
            ('Ambas as verificações', lambda text: 80 <= len(text.split()) <= 120 and '\u2014' not in text)):
        values = []
        for arm in ('original', 'skill'):
            texts = [r['edited'] for r in records if r['arm'] == arm]
            values.append(f'{sum(check(text) for text in texts)}/{len(texts)}')
        out.append('| ' + ' | '.join([label, *values]) + ' |')
    out.extend(['', '**Leitura do resultado:** os três juízes atribuíram menor impressão média de IA à versão com skill, mas a preferência literária divergiu: '
                'Jev preferiu mais originais; Astra e Opus 5.5 preferiram mais versões com skill. Menor impressão de IA não implica automaticamente um conto melhor.', '',
                'As médias têm peso igual por par, não por modelo; modelos testados em dois modos contribuem com mais pares. '
                'Não combinamos as médias dos juízes, cujas escalas não são calibradas. O total de preferências é uma contagem descritiva de opiniões sobre os mesmos textos, '
                f'não {judgments} experimentos independentes. Dois pedidos e uma geração por condição não permitem generalizar superioridade. '
                '**A avaliação humana permanece pendente.** Textos, julgamentos e skill foram preservados; esta consolidação não exigiu novas chamadas de modelos.', ''])
    return '\n'.join(out)


def accounting(records):
    groups = defaultdict(lambda: {'calls': 0, 'cost': Decimal(0), 'input': 0, 'output': 0, 'seconds': 0.0})
    for record in records:
        group = groups[record['model']]
        group['calls'] += 1
        group['cost'] += Decimal(record['cost_usd'])
        group['input'] += record['usage']['prompt_tokens']
        group['output'] += record['usage']['completion_tokens']
        group['seconds'] += record['elapsed_seconds']
    out = ['| Modelo | Chamadas | Custo USD | Tokens de entrada | Tokens de saída | Tempo somado (s) |', '|---|---:|---:|---:|---:|---:|']
    for mid, data in sorted(groups.items()):
        out.append(f"| {mid} | {data['calls']} | {data['cost']:.8f} | {data['input']} | {data['output']} | {data['seconds']:.1f} |")
    return '\n'.join(out)


def render():
    config, records, tables = results()
    summary = load(TESTS / 'results/summary.json')
    reconciliation = load(TESTS / 'results/reconciliation.json')
    all_blocks = table_blocks(tables)
    intro = f'''# Humanizador PT-BR: primeiro teste de percepção

Leia os contos lado a lado e decida se a skill melhora a leitura. **A avaliação humana de Ricardo está pendente.** O resultado do juiz não foi usado para ajustar a skill ou os textos.

Foram gerados {len(records)} contos em {len(set(r['model'] for r in records))} modelos: dois pedidos, {len(config['routes'])} configurações de modelo/raciocínio e duas condições. Isso produz {summary['pairs']} pares. Cada par mostra a primeira resposta sem skill e a primeira resposta com a skill.

{aggregate_block(tables, records, summary['judge_calls'])}

## Como ler as colunas de detecção

Cada juiz dá um índice de **impressão de escrita por IA**, de 0 a 100. A seta mostra **original → com skill**. Menor índice significa que o juiz percebeu menos marcas de escrita padronizada. A preferência ao lado indica qual conto ele considerou melhor de ler.

**Os dois textos são de IA.** Esses índices não descobrem autoria, não são probabilidades calibradas e não medem sozinhos qualidade. Juízes podem discordar. Não há vencedor declarado.

Jev (`typesafe/jev-1.13`) usa Decisions com respostas tipadas; Astra (`openai/gpt-6-astra`) e Opus 5.5 (`anthropic/claude-opus-5.5`) usam chamadas cruas de chat. Receberam textos e pares anonimizados, com ordem A/B alternada de maneira reproduzível, sem nomes dos geradores nem indicação de uso da skill.

'''
    instructions = '''## Sua avaliação humana

Em cada par, responda: qual conto funciona melhor, por quê e o que soa artificial? Pode preferir o original, a versão com skill, nenhuma delas ou considerar empate. Observe cena, continuidade, ritmo, voz e cumprimento do pedido. Leia os textos antes de olhar a coluna dos juízes.

Esta página identifica os modelos; sua leitura não será uma avaliação cega. Isso não impede uma avaliação prática e crítica dos textos.
'''
    (TESTS / 'README.md').write_text(intro + all_blocks + '\n' + instructions + '\n[Relatório final e custos](REPORT.md). [Como repetir o experimento](PROTOCOL.md).\n', encoding='utf-8')
    judge_records = []
    for file in sorted((TESTS / 'results').glob('*-state.json')):
        if file.name != 'generation-state.json':
            judge_records.extend(load(file)['records'])
    judge_cost = sum((Decimal(r['cost_usd']) for r in judge_records), Decimal(0))
    jev_cost = sum((Decimal(load(f)['cost_usd']) for f in (TESTS / 'results').glob('jev-*.json')), Decimal(0))
    generation_cost = sum((Decimal(r['cost_usd']) for r in records), Decimal(0))
    violations = []
    for r in records:
        words = len(r['edited'].split())
        if not 80 <= words <= 120 or '\u2014' in r['edited']:
            violations.append(f"- {r['case']} / {r['model']} / {r['mode']} / {r['arm']}: {words} palavras; travessão longo {'presente' if chr(8212) in r['edited'] else 'ausente'}.")
    report = intro + all_blocks + f'''
## O que este teste permite concluir

A skill está pronta para uma avaliação prática de leitura. A revisão passou a orientar criação ficcional, cenas concretas, ritmo contextual e entrega do texto pronto, sem burocracia de auditoria obrigatória. Na revisão de não ficção, as salvaguardas de fatos e voz continuam.

Este primeiro relatório apresenta as saídas sem edição manual, seleção por nota ou nova geração após o julgamento. Houve recuperações operacionais de tentativas sem resposta, após reconciliação de cobrança, antes dos juízes; as saídas já concluídas não foram repetidas. Oito posições MiMo Pro e Flash do conto do bolo usaram GMICloud após falhas na rota DeepInfra, com os dois braços de cada par na mesma rota. O protocolo foi emendado e os pedidos efetivos foram preservados. Ver [RECOVERY.md](RECOVERY.md). **Não permite afirmar que a skill é superior, que elimina marcas de IA ou que funciona melhor em todos os gêneros.** A adoção depende da avaliação humana.

## Consumo desta rodada

- Geração: US$ {generation_cost:.8f}.
- Astra e Opus como juízes: US$ {judge_cost:.8f}.
- Jev como juiz: US$ {jev_cost:.8f}.
- Sondagens das rotas alternativas MiMo Pro e Flash: US$ {Decimal(load(TESTS / 'results/attempts/route-amendment.json')['probe_cost_usd']):.8f}.
- Soma dos custos informados nas respostas, incluindo sondagens: US$ {Decimal(summary['cost_usd']):.8f}.
- Consumo da chave exclusiva, confirmado depois da execução: US$ {Decimal(str(reconciliation['usage_usd'])):.8f}.
- Consumo histórico anterior: US$ {Decimal(config['prior_usage_usd']):.8f}, separado deste teste.
- Consumo acumulado dos dois pilotos: US$ {Decimal(str(reconciliation['usage_usd'])) + Decimal(config['prior_usage_usd']):.8f}, dentro do teto global de US$ 10 aprovado para o piloto.

### Geração por modelo

{accounting(records)}

### Julgamento por modelo

{accounting(judge_records)}

Jev: duas chamadas Decisions. Seus tokens de entrada e saída e tempos estão nos registros próprios. Tokens de raciocínio não são somados novamente aos tokens de saída; ausência de contadores de cache não significa zero. Tempo somado é duração observada das chamadas, não tempo exclusivo de geração.

## Limites e verificações

- Dois contos e uma primeira resposta por condição. Não há repetições estatísticas nem referência humana de autoria verificada.
- As duas condições foram geradas independentemente com o mesmo prompt, modelo, rota, modo e teto de saída. A versão com skill **não recebeu a resposta original para reescrever**.
- As chamadas não receberam SOUL.md, memórias, outras skills ou contexto desta conversa. O tratamento recebeu somente esta skill e suas referências editoriais publicadas.
- Modos ligados e desligados refletem os parâmetros enviados. O modo desligado só foi incluído em rotas com aceitação previamente registrada; isso não prova ausência de computação oculta.
- Cinco modelos foram testados nos dois modos. Os demais ficaram apenas no modo ligado. Moonlight/Kimi permanecem fora por identificação ainda não resolvida no escopo anterior; não houve substituição silenciosa.
- Astra e Opus também são geradores, o que permite viés de autoavaliação apesar da anonimização. A ordem foi embaralhada; uma única ordem por par não elimina viés de posição.
- O uso da skill foi congelado antes da primeira geração. Não houve alterações na skill ou nos contos após ver resultados dos juízes.
- O script local não redigiu, não aplicou substituições e não foi medido como uma condição separada nesta rodada. A prova prática é do uso textual da skill na criação de contos.
- A suite offline valida software e integridade, não naturalidade literária. Seu resultado está em [results/software-tests.txt](results/software-tests.txt).

### Cumprimento mecânico do pedido

Contagem por separação em espaços, incluindo eventuais títulos não solicitados. Estes desvios permanecem publicados, sem conserto ou regeneração:

{chr(10).join(violations) if violations else 'Todas as respostas têm de 80 a 120 palavras e não contêm travessão longo.'}

## Evidências e reprodução

[Protocolo](PROTOCOL.md), [configuração e hashes congelados](frozen/config.json), [prompt completo da skill](frozen/skill-bundle.txt), [planos e respostas reais](results/), [script de execução](scripts/contos.py), [script de relatório](scripts/relatorio.py). O histórico anterior foi preservado em [historico-20260929/](historico-20260929/REPORT.md), sem misturar seus resultados com os contos.

''' + instructions
    (TESTS / 'REPORT.md').write_text(report, encoding='utf-8')
    # ponytail: exemplos fixos de três famílias; o conjunto completo está nos testes, sem seleção por nota.
    selected = {('anthropic/claude-opus-5.5', 'on'), ('openai/gpt-6-luna', 'off'), ('xiaomi/mimo-v2.6-flash', 'off')}
    root_readme = '''# Humanizador PT-BR

Escreva ou revise em português brasileiro sem ficar preso à cara de um texto genérico. A skill orienta ritmo, detalhes úteis e uma voz coerente, preservando fatos na revisão e permitindo invenção quando o pedido é ficcional.

**Veja o resultado, não apenas a promessa.** O primeiro teste apresenta dois pequenos contos, 14 modelos e 38 pares sem/com skill. Abaixo há exemplos fixos de três famílias; o conjunto completo está no [README dos testes](tests/README.md) e no [relatório final](tests/REPORT.md).

A avaliação humana está pendente. Não anunciamos ganho garantido, vencedor ou proteção contra detectores. Nas colunas de detecção, cada número é uma impressão do juiz, de 0 a 100, na ordem original → com skill; não é uma probabilidade de autoria. Ambos os textos foram gerados por IA.

## Usar a skill

Copie a pasta completa para o diretório de skills do seu agente e carregue [SKILL.md](SKILL.md). Peça, por exemplo:

> Reescreva este texto com a skill humanizador-pt-br. Preserve os fatos e o registro. Entregue somente a versão final.

> Escreva um pequeno conto usando humanizador-pt-br, com uma cena cotidiana e final aberto.

A skill não exige Python para escrever. O script opcional só audita, sugere e aplica edições explicitamente aprovadas. Não há serviço permanente ou biblioteca linguística pesada.

''' + table_blocks(tables, selected) + f'''
## O que foi testado

- {len(records)} primeiras gerações, sem correção manual ou repetição guiada por notas.
- Jev, Astra e Opus 5.5 julgando versões anonimizadas.
- US$ {Decimal(summary['cost_usd']):.8f} nesta rodada, incluindo os juízes.
- Testes de software e resultados reunidos em `tests/`. Relatórios em Markdown.

Leia os contos e diga se a skill melhora a leitura de verdade. Esse é o critério de adoção.

## Script opcional

```text
python3 scripts/humanizar.py audit entrada.txt
python3 scripts/humanizar.py suggest entrada.txt --profile neutro-claro --seed 17
python3 scripts/humanizar.py verify entrada.txt revisado.txt
python3 scripts/humanizar.py apply entrada.txt --plan plano.json --output revisado.txt
```

`apply` exige o SHA256 da entrada, índices de caracteres Unicode (fim exclusivo), trecho exato e aprovação explícita. O destino deve ser novo. Exemplo de formato, válido apenas para a entrada literal `vale destacar: ação.` após revisão contextual:

```json
{{"input_sha256":"HASH_DA_ENTRADA_OBTIDO_NA_AUDITORIA","edits":[{{"start":0,"end":13,"original":"vale destacar","replacement":"destaco","approved":true}}]}}
```

Use `--protect "termo"` para proteção adicional. A comparação mecânica não comprova equivalência de sentido. Não publique ou sobrescreva sem autorização.

## Organização

`README.me`, `SKILL.md`, `references/`, `scripts/` e `tests/`, sem resultados soltos na pasta da skill. O nome `README.me` foi mantido literalmente conforme o pedido; a apresentação renderizável no GitHub está em `tests/README.md`.

[Catálogo editorial](references/catalogo.json), [estilos](references/estilos.json), [fontes e limites](references/fontes.md). Não há palavras proibidas nem score de autoria no editor local. Não usar catálogos arbitrários como código confiável.
'''
    (ROOT / 'README.me').write_text(root_readme, encoding='utf-8')
    print(json.dumps({'pairs': summary['pairs'], 'rows_in_each_full_document': sum(len(rows) for _, rows in tables), 'root_example_rows': sum((r['model'], r['mode']) in selected for _, rows in tables for r in rows)}))


if __name__ == '__main__':
    render()
