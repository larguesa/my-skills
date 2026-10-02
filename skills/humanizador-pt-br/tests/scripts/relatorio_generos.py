#!/usr/bin/env python3
"""Offline, evidence-only Markdown for the frozen 24-case expansion.

render(run_dir, destination_tests, accounting=None) never invokes a model.
Durable requests are authoritative; identical phase-state references are deduped.
All evidence is checked before any report is written. Historical reports are not
written. Reports reuse experiments/<case>/; summary lives in run_dir.
"""
import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
from html import escape
import json
import os
from pathlib import Path
import re
from urllib.parse import quote

import contos as c
import generos as g
import validar_generos as v

TESTS = Path(__file__).resolve().parents[1]
ARMS = ('original', 'skill')
JUDGES = ('jev', 'astra', 'opus')
LABELS = {'jev': 'Jev', 'astra': 'Astra', 'opus': 'Opus 5.5'}
DIMENSIONS = ('naturalidade', 'clareza', 'adequacao', 'correcao')
MARKER_START = '<!-- expansion-report:start -->'
MARKER_END = '<!-- expansion-report:end -->'


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def cell(value):
    text = escape(str(value), quote=False)
    text = re.sub(r'([\\`*_\[\]~|])', r'\\\1', text)
    return text.replace('\r\n', '\n').replace('\n', '<br>')


def fence(text):
    runs = [len(match) for match in re.findall(r'`+', text)]
    delimiter = '`' * max(3, max(runs, default=0) + 1)
    return delimiter + 'text\n' + text + ('\n' if not text.endswith('\n') else '') + delimiter


def link(path, target):
    return '[evidência](' + quote(os.path.relpath(path, Path(target).parent), safe='/.-') + ')'


def number(value):
    if value is None:
        return 'indisponível'
    return format(value, '.2f')


def fraction(n, total, good='🟩', rest='⬜'):
    if not total:
        return '⬜' * 10 + ' 0/0 (sem observações)'
    count = round(10 * n / total)
    return good * count + rest * (10 - count) + f' {n}/{total} ({100 * n / total:.1f}%)'


def checked_records(run, config):
    expected = g.generation_calls(config, run / 'frozen')
    by_id = {call['id']: call for call in expected}
    for plan in sorted(run.glob('generation*-plan.json')):
        calls = load(plan)['calls']
        case_id = plan.name[len('generation-'):-len('-plan.json')] if plan.name != 'generation-plan.json' else None
        planned = [call for call in expected if case_id is None or call['case'] == case_id]
        if not planned or calls != planned[:len(calls)]:
            raise ValueError('generation plan metadata mismatch')
    records, sources = {}, {}
    for state in sorted(run.glob('generation*-state.json')):
        entries = load(state)['records']
        if len({entry['id'] for entry in entries}) != len(entries):
            raise ValueError('duplicate generation record')
        for record in entries:
            if record['id'] in records:
                raise ValueError('duplicate generation phase record')
            records[record['id']] = record
            sources[record['id']] = state
    request_ids = set()
    for path in sorted((run / 'requests').glob('*.json')):
        record = load(path)
        if record.get('arm') not in ARMS:
            continue
        identifier = record['id']
        if identifier in request_ids:
            raise ValueError('duplicate durable request')
        request_ids.add(identifier)
        if path.stem != identifier:
            raise ValueError('request filename mismatch')
        if identifier in records and records[identifier] != record:
            raise ValueError('durable request/state mismatch')
        records[identifier], sources[identifier] = record, path
    for identifier, record in records.items():
        if identifier not in by_id or any(record.get(k) != value for k, value in by_id[identifier].items()):
            raise ValueError('generation request metadata mismatch')
        response = record.get('response')
        if response is not None:
            choices = response.get('choices', [])
            text = choices[0].get('message', {}).get('content') if choices else None
            if 'edited' in record and record['edited'] != text:
                raise ValueError('response/record edited mismatch')
            if 'usage' in record and record['usage'] != response.get('usage', {}):
                raise ValueError('response/record usage mismatch')
            if 'cost_usd' in record and 'cost' in response.get('usage', {}) and Decimal(str(record['cost_usd'])) != Decimal(str(response['usage']['cost'])):
                raise ValueError('response/record cost mismatch')
        if record['status'] == 'completed':
            if not response or not isinstance(text, str) or not text.strip() or choices[0].get('finish_reason') != 'stop':
                raise ValueError('completed generation has invalid response')
            if record.get('finish_reason') != choices[0].get('finish_reason'):
                raise ValueError('response/record finish_reason mismatch')
    slots = {(record['case'], record['model'], record['mode'], record['arm']): record for record in records.values()}
    if len(slots) != len(records):
        raise ValueError('duplicate generation slot')
    return records, slots, sources


def parsed_chat(text):
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    return json.loads(text)


def checked_judges(run, config, records):
    """Match actual generos.judge_calls and durable native Decisions records."""
    chunks, mapping_paths, saved_chunks = {}, {}, {}
    state = dict(records=list(records.values()))
    for case in config['cases']:
        case_id = case['id']
        planned = g.anonymous_chunks(config, state, case_id)
        chunks[case_id] = {chunk['index']: chunk for chunk in planned}
        path = run / ('mapping-' + case_id + '.json')
        if path.exists():
            saved = load(path)
            # A resumed phase can stop before execute() refreshes its mapping.
            # Only prior not_generated slots may lag; existing texts/IDs must
            # still read back exactly and each judged chunk must be current.
            previous = saved.get('chunks', [])
            omitted = {(meta['model'], meta['mode'], meta['arm']) for item in previous
                       for meta in item.get('mapping', {}).values() if meta.get('invalid_status') == 'not_generated'}
            snapshot = dict(records=[record for record in state['records'] if record['case'] != case_id
                                     or (record['model'], record['mode'], record['arm']) not in omitted])
            if previous != g.anonymous_chunks(config, snapshot, case_id):
                raise ValueError('anonymous mapping correspondence mismatch')
            mapping_paths[case_id] = path
            saved_chunks[case_id] = {item['index']: item for item in previous}
    if any(path.name[len('mapping-'):-len('.json')] not in chunks for path in run.glob('mapping-*.json')):
        raise ValueError('unknown anonymous mapping case')
    durable, sources = {}, {}
    for judge in JUDGES:
        for path in sorted(run.glob(judge + '-*-state.json')):
            entries = load(path)['records']
            if len({record['id'] for record in entries}) != len(entries):
                raise ValueError('duplicate judge record')
            for record in entries:
                if record['id'] in durable:
                    raise ValueError('duplicate judge phase record')
                if record.get('judge') != judge:
                    raise ValueError('judge phase metadata mismatch')
                durable[record['id']], sources[record['id']] = record, path
    seen = set()
    for path in sorted((run / 'requests').glob('*.json')):
        record = load(path)
        if record.get('arm') != 'judge':
            continue
        identifier = record['id']
        if identifier in seen or path.stem != identifier:
            raise ValueError('duplicate judge request or filename mismatch')
        seen.add(identifier)
        if identifier in durable and durable[identifier] != record:
            raise ValueError('judge durable request/state mismatch')
        durable[identifier], sources[identifier] = record, path
    rows, calls = {name: {} for name in JUDGES}, {name: [] for name in JUDGES}
    claimed, copies = set(), set()
    for identifier, record in durable.items():
        judge, case_id, index = record.get('judge'), record.get('case'), record.get('chunk')
        chunk = chunks.get(case_id, {}).get(index)
        if judge not in JUDGES or chunk is None or not chunk['eligible'] or case_id not in mapping_paths:
            raise ValueError('judge input/mapping mismatch or missing saved mapping')
        if saved_chunks[case_id][index] != chunk:
            raise ValueError('judged chunk/saved mapping correspondence mismatch')
        expected = next(call for call in g.judge_calls(config, chunk['state'], case_id, index) if call['judge'] == judge)
        if any(record.get(key) != value for key, value in expected.items()):
            raise ValueError('judge request metadata mismatch')
        slot = (judge, case_id, index)
        if slot in claimed:
            raise ValueError('duplicate judge chunk slot')
        claimed.add(slot)
        source = sources[identifier]
        phase = judge + '-' + case_id + '-chunk-' + str(index).zfill(2)
        plan = run / (phase + '-plan.json')
        if plan.exists() and load(plan)['calls'] != [expected]:
            raise ValueError('judge plan metadata mismatch')
        calls[judge].append(record)
        response = record.get('response')
        if response is not None:
            if 'usage' in record and record['usage'] != response.get('usage', {}):
                raise ValueError('judge response/usage mismatch')
            if 'cost_usd' in record and 'cost' in response.get('usage', {}) and Decimal(str(record['cost_usd'])) != Decimal(str(response['usage']['cost'])):
                raise ValueError('judge response/cost mismatch')
            if judge != 'jev' and 'edited' in record:
                choice = (response.get('choices') or [{}])[0]
                if record['edited'] != (choice.get('message') or {}).get('content'):
                    raise ValueError('judge response/record edited mismatch')
        if record['status'] != 'completed':
            for pair in chunk['state']['pares'].values():
                meta = chunk['mapping'][pair['A']]
                rows[judge][(case_id, meta['model'], meta['mode'])] = dict(failure_status=record['status'], source=str(source))
            continue
        if judge == 'jev':
            judgment = g.validate_judge(response, chunk['state'], True)
        else:
            choice = response['choices'][0]
            if choice.get('finish_reason') != 'stop' or record.get('finish_reason') != 'stop':
                raise ValueError('judge finish_reason mismatch')
            judgment = g.validate_judge(parsed_chat(record['edited']), chunk['state'])
        capped = {tid: g.aggregate_quality(quality) for tid, quality in judgment['qualidade'].items()}
        if record.get('judgment') != judgment or record.get('quality_aggregate') != capped:
            raise ValueError('judge score/aggregate raw correspondence mismatch')
        copy = run / ('judgment-' + phase + '.json')
        if copy.exists():
            if load(copy) != judgment:
                raise ValueError('judge score copy/raw correspondence mismatch')
            copies.add(copy)
        mapping = chunk['mapping']
        for pid, pair in chunk['state']['pares'].items():
            chosen = judgment['preferencia'][pid]
            preference = 'empate' if chosen == 'empate' else mapping[pair[chosen]]['arm']
            data = dict(preference=preference, source=str(source), mapping_source=str(mapping_paths[case_id]), arms={})
            route_key = None
            for tid in pair.values():
                meta = mapping[tid]
                route_key = (case_id, meta['model'], meta['mode'])
                raw = judgment['qualidade'][tid]
                data['arms'][meta['arm']] = dict(raw=raw, capped=capped[tid], deteccao=judgment['deteccao'][tid],
                                                total_raw=sum(raw[dimension] for dimension in DIMENSIONS) / 4)
            if route_key in rows[judge]:
                raise ValueError('duplicate judge pair/configuration')
            rows[judge][route_key] = data
    if set(run.glob('judgment-*.json')) != copies:
        raise ValueError('unlinked or mismatched judge score copy')
    return rows, calls


def judge_summary(rows, expected_pairs):
    result = dict(judge_pairs_observed=sum(sum('failure_status' not in entry for entry in data.values()) for data in rows.values()))
    fields = (*DIMENSIONS, 'correcao_raw', 'total', 'total_raw', 'deteccao')
    for judge, data in rows.items():
        entries = [entry for entry in data.values() if 'failure_status' not in entry]
        votes = Counter(entry['preference'] for entry in entries)
        metrics = {}
        for field in fields:
            metrics[field] = {}
            for arm in ARMS:
                values = []
                for entry in entries:
                    item = entry['arms'][arm]
                    value = item['raw']['correcao'] if field == 'correcao_raw' else item[field] if field in ('deteccao', 'total_raw') else item['capped'][field]
                    values.append(value)
                metrics[field][arm] = dict(mean=sum(values) / len(values) if values else None,
                                          n=len(values), missing=expected_pairs - len(values))
        result[judge] = dict(preference=dict(**{name: votes[name] for name in ('skill', 'original', 'empate')},
                                            n=len(entries), missing=expected_pairs - len(entries)), fields=metrics)
    return result


def judge_cell(judge, row, target):
    if row is None:
        return '⏸️ pendente: sem julgamento válido'
    if 'failure_status' in row:
        return cell('🟥 julgamento sem notas válidas: ' + row['failure_status']) + '<br>' + link(row['source'], target)
    text = []
    for arm in ARMS:
        data = row['arms'][arm]
        dimensions = '; '.join(dimension + ': bruto ' + number(data['raw'][dimension]) + ', limitado ' + number(data['capped'][dimension]) for dimension in DIMENSIONS)
        reason = 'justificativa indisponível (Score nativo Jev não retorna razões textuais)' if judge == 'jev' else 'justificativa: ' + data['raw']['justificativa']
        text.append(arm + ': ' + dimensions + '; total: bruto ' + number(data['total_raw']) + ', limitado ' + number(data['capped']['total'])
                    + '; crítico: ' + str(data['raw']['critico']).lower() + '; impressão IA: ' + number(data['deteccao']) + '; ' + reason)
    text += ['prefere ' + row['preference']]
    return cell('\n'.join(text)) + '<br>' + link(row['source'], target) + '; mapa: ' + link(row['mapping_source'], target)


def cost_group(records):
    total = Decimal(0)
    known, unknown = 0, 0
    elapsed = []
    for record in records:
        cost = record.get('cost_usd')
        if cost is None:
            unknown += 1
        else:
            try:
                value = Decimal(str(cost))
            except InvalidOperation as exc:
                raise ValueError('invalid measured cost') from exc
            if not value.is_finite() or value < 0:
                raise ValueError('invalid measured cost')
            total += value
            known += 1
        if record.get('elapsed_seconds') is not None:
            value = float(record['elapsed_seconds'])
            if value < 0 or not value < float('inf'):
                raise ValueError('invalid elapsed_seconds')
            elapsed.append(value)
    return dict(calls=known + unknown, known_calls=known, unknown_calls=unknown,
                known_usd=str(total), elapsed_seconds=sum(elapsed), time_n=len(elapsed))


def extra_accounting(accounting, used_ids):
    """Optional path/dict {records:[raw probe/extra records]} or record list."""
    source = None
    if accounting is None:
        return dict(cost_group([]), available=False), source
    if isinstance(accounting, (str, Path)):
        source = str(Path(accounting).resolve())
        accounting = load(accounting)
    entries = accounting['records'] if isinstance(accounting, dict) else accounting
    if not isinstance(entries, list):
        raise ValueError('accounting requires a records list')
    seen, measured = set(), []
    for record in entries:
        identifier = record.get('id') or record.get('response', {}).get('id')
        if identifier is not None:
            if identifier in seen or identifier in used_ids:
                raise ValueError('duplicate/double-counted accounting record')
            seen.add(identifier)
        raw_cost = record.get('response', {}).get('usage', {}).get('cost')
        if raw_cost is not None and record.get('cost_usd') is not None and Decimal(str(raw_cost)) != Decimal(str(record['cost_usd'])):
            raise ValueError('accounting raw cost correspondence mismatch')
        measured.append(dict(record, cost_usd=record.get('cost_usd', raw_cost)))
    return dict(cost_group(measured), available=True), source


def observations(slots, config):
    result = {}
    for key, record in slots.items():
        if record['status'] == 'completed':
            result[key] = v.validate(next(case for case in config['cases'] if case['id'] == key[0]), record['edited'])
    return result


def mechanical_summary(observed, group='mechanical'):
    out = {}
    for arm in ARMS:
        counts = {}
        for key, data in observed.items():
            if key[-1] != arm:
                continue
            for check in data[group]:
                counter = counts.setdefault(check['name'], Counter())
                counter[check['status']] += 1
        out[arm] = {name: dict(pass_count=count['pass'], fail_count=count['fail'], pending=count['pending'],
                               n=count['pass'] + count['fail']) for name, count in sorted(counts.items())}
    return out


def aggregate_block(summary):
    generation = summary['generation']
    expected = summary['expected']
    lines = ['## Ampliação 20261002: resultados observados', '',
             f"Somente esta rodada: {generation['completed']}/{expected['candidates']} candidatos válidos; {generation['complete_pairs']}/{expected['pairs']} pares completos; "
             f"{generation['failed']} falhas/saídas inválidas; {generation['missing']} posições não iniciadas.", '',
             'Médias com peso igual por par/configuração e denominadores próprios por campo. Não se combinam escalas de juízes nem dados antigos.', '',
             'Preferências são opiniões, não sucesso factual. Impressão de IA não é probabilidade de autoria. Revisão humana: pendente. Não há alegação de superioridade.', '',
             '| Juiz | Prefere com skill | Prefere original | Empate | Ausentes / previstos |', '|---|---|---|---|---:|']
    for judge in JUDGES:
        data = summary['judgments'][judge]['preference']
        lines.append('| ' + ' | '.join([LABELS[judge], fraction(data['skill'], data['n']), fraction(data['original'], data['n'], '🟦'), fraction(data['empate'], data['n'], '🟨'), f"{data['missing']}/{expected['pairs']}"]) + ' |')
    lines += ['', '| Juiz / dimensão (0–100) | Original: média; n; ausentes | Skill: média; n; ausentes |', '|---|---:|---:|']
    for judge in JUDGES:
        for field, data in summary['judgments'][judge]['fields'].items():
            values = [number(data[arm]['mean']) + f"; n={data[arm]['n']}; ausentes={data[arm]['missing']}" for arm in ARMS]
            lines.append('| ' + ' | '.join([LABELS[judge] + ' / ' + field, *values]) + ' |')
    lines += ['', 'Jev: dimensões por Score nativo, índice probabilístico contínuo 0–4 × 25 (não confiança ou noul); cinco âncoras ordenadas. Impressão de IA: noul × 100. Justificativa textual indisponível na API nativa. Correção crítica limitada a 25 e total a 49; notas brutas preservadas.', '']
    lines += ['', '| Verificação mecânica | Original | Com skill |', '|---|---|---|']
    names = sorted({name for data in summary['mechanical'].values() for name in data})
    for name in names:
        values = []
        for arm in ARMS:
            data = summary['mechanical'][arm].get(name, dict(pass_count=0, n=0, pending=0))
            values.append(fraction(data['pass_count'], data['n'], rest='🟥') + f"; pendentes: {data['pending']}")
        lines.append('| ' + ' | '.join([cell(name), *values]) + ' |')
    lines += ['', '| Observação de apoio literal / cálculo (não é verdade semântica) | Original | Com skill |', '|---|---|---|']
    names = sorted({name for data in summary['factual_support'].values() for name in data})
    for name in names:
        values = []
        for arm in ARMS:
            data = summary['factual_support'][arm].get(name, dict(pass_count=0, n=0, pending=0))
            values.append(fraction(data['pass_count'], data['n'], rest='🟥') + f"; pendentes: {data['pending']}")
        lines.append('| ' + ' | '.join([cell(name), *values]) + ' |')
    lines += ['', 'Verificações aprovadas só demonstram a observação nomeada; fidelidade factual e semântica continuam pendentes.', '',
              '### Contabilidade da ampliação (medições, sem teto monetário)', '',
              '| Grupo | Chamadas observadas | Custo conhecido USD | Custos desconhecidos | Tempos conhecidos / chamadas |', '|---|---:|---:|---:|---:|']
    for name, data in summary['accounting'].items():
        if data.get('available') is False:
            lines.append(f'| {cell(name)} | não fornecido | desconhecido | não fornecido | não fornecido |')
        else:
            lines.append(f"| {cell(name)} | {data['calls']} | {data['known_usd']} | {data['unknown_calls']} | {data['elapsed_seconds']:.2f} s; {data['time_n']}/{data['calls']} |")
    lines += ['', 'Custos de geração, Jev, Astra, Opus e sondagens/extras separados. Custo conhecido é parcial quando há chamadas de custo desconhecido; chamadas não iniciadas não são custo zero.', '']
    return '\n'.join(lines)


def case_report(case, config, slots, sources, observed, summary, target, run, judgments):
    lines = ['# ' + case['title'], '', '**Revisão humana: pendente.** Juízes dão opiniões; não há alegação de superioridade.', '',
             '**Prompt exato congelado**', '', fence(case['prompt']), '', '## Critérios fornecidos (não são respostas de candidatos)', '']
    lines += ['- ' + cell(check) for check in case.get('checks', [])]
    lines += ['', aggregate_block(summary), '## Tabela completa das 19 configurações', '',
              '| Modelo/configuração | Resposta original | Resposta com skill | Jev | Astra | Opus 5.5 | Custo original USD | Custo skill USD | Tempo original s | Tempo skill s | Verificações original | Verificações skill |',
              '|---|---|---|---|---|---|---:|---:|---:|---:|---|---|']
    for route in config['routes']:
        records = [slots.get((case['id'], route['model'], route['mode'], arm)) for arm in ARMS]
        texts, costs, times, checks = [], [], [], []
        for arm, record in zip(ARMS, records):
            if record is None:
                texts.append('⏸️ pendente: chamada não iniciada')
                costs.append('não iniciado')
                times.append('não iniciado')
                checks.append('pendente: sem saída válida')
                continue
            status = record['status']
            raw_text = record.get('edited')
            if not isinstance(raw_text, str):
                raw_text = 'sem texto retornado'
            notes = []
            for field in ('usage_issues', 'validation_error', 'error_type', 'http_status'):
                if record.get(field):
                    notes.append(field + ': ' + json.dumps(record[field], ensure_ascii=False))
            if record.get('usage_issues'):
                notes.append('completion_tokens nativos: ' + str(record.get('usage', {}).get('completion_tokens', 'indisponível'))
                             + '; max_tokens congelado: ' + str(record['payload']['max_tokens']))
            texts.append(cell(raw_text + '\n' + ('✅ saída válida' if status == 'completed' else '🟥 ' + status) + ('; ' + '; '.join(notes) if notes else ''))
                         + '<br>' + link(sources[record['id']], target))
            costs.append(record.get('cost_usd', 'desconhecido'))
            times.append(number(record.get('elapsed_seconds')))
            data = observed.get((case['id'], route['model'], route['mode'], arm))
            checks.append('; '.join(prefix + ': ' + {'pass': '🟩 aprovado', 'fail': '🟥 reprovado', 'pending': '⏸️ pendente'}[check['status']] + ': ' + check['name'] + ' (' + check['detail'] + ')'
                                    for group, prefix in [('mechanical', 'mecânica'), ('factual_support', 'apoio literal')]
                                    for check in data[group]) + '; semântica: pendente' if data else 'pendente: saída inválida/ausente')
        label = 'Configuração: ' + route['model'] + ' (' + route['mode'] + ')'
        judges = [judge_cell(judge, judgments[judge].get((case['id'], route['model'], route['mode'])), target) for judge in JUDGES]
        lines.append('| ' + ' | '.join([cell(label), *texts, *judges, *(cell(value) for value in [*costs, *times, *checks])]) + ' |')
    lines += ['', '## Evidências brutas', '', link(run / 'frozen/config.json', target), '']
    return '\n'.join(lines)


def render(run_dir, destination_tests, accounting=None):
    run, destination = Path(run_dir).resolve(), Path(destination_tests).resolve()
    if not re.fullmatch(r'(?:run|expansao)-[a-z0-9]+(?:-[a-z0-9]+)*', run.name):
        raise ValueError('invalid run directory name')
    config = c.checked_config(run / 'frozen/config.json')
    if (run / 'config-run.json').exists() and load(run / 'config-run.json') != config:
        raise ValueError('frozen run config metadata mismatch')
    if config.get('budget_usd', 'missing') is not None or config['max_tokens'] != 4096 or config['judge_max_tokens'] != 16384:
        raise ValueError('frozen expansion metadata mismatch')
    ids = [case['id'] for case in config['cases']]
    routes = [(route['model'], route['mode']) for route in config['routes']]
    if len(ids) != 24 or len(set(ids)) != 24 or len(routes) != 19 or len(set(routes)) != 19:
        raise ValueError('expected 24 unique cases and 19 unique configurations')
    for case in config['cases']:
        if case['id'] not in v.CASES or case != v.CASES[case['id']]:
            raise ValueError('frozen approved case metadata mismatch')
    records, slots, sources = checked_records(run, config)
    judgments, judge_calls = checked_judges(run, config, records)
    used_ids = set(records) | {record['id'] for data in judge_calls.values() for record in data}
    extra, extra_source = extra_accounting(accounting, used_ids)
    chunk_counts = [len(g.anonymous_chunks(config, dict(records=[]), case['id'])) for case in config['cases']]
    observed = observations(slots, config)
    complete_pairs = sum(all(slots.get((case['id'], *route, arm), {}).get('status') == 'completed' for arm in ARMS) for case in config['cases'] for route in routes)
    summary = dict(schema=1, run=run.name, human_review='pending', budget_usd=None,
                   expected=dict(cases=24, configurations=19, candidates=912, pairs=456, judge_pairs=1368),
                   generation=dict(completed=sum(record['status'] == 'completed' for record in records.values()),
                                   failed=sum(record['status'] != 'completed' for record in records.values()),
                                   missing=912 - len(records), complete_pairs=complete_pairs),
                   mechanical=mechanical_summary(observed),
                   factual_support=mechanical_summary(observed, 'factual_support'),
                   methodology=dict(chunks_per_case=chunk_counts, planned_judge_calls=sum(chunk_counts) * len(JUDGES),
                                    quality_score='native_score_index_0_4_times_25', jev_justification='unavailable'),
                   judgments=judge_summary(judgments, 456),
                   accounting={'generation': cost_group(records.values()), **{name: cost_group(judge_calls[name]) for name in JUDGES}, 'probes_extra': extra},
                   accounting_evidence=extra_source)
    out = destination / 'experiments'
    documents = {}
    for case in config['cases']:
        target = out / case['id'] / 'REPORT.md'
        case_slots = {key: value for key, value in slots.items() if key[0] == case['id']}
        case_summary = dict(summary, expected=dict(cases=1, configurations=19, candidates=38, pairs=19, judge_pairs=57),
                            accounting={'generation': cost_group(case_slots.values()), **{name: cost_group(record for record in judge_calls[name] if record['case'] == case['id']) for name in JUDGES}, 'probes_extra': cost_group([])},
                            judgments=judge_summary({judge: {key: value for key, value in data.items() if key[0] == case['id']} for judge, data in judgments.items()}, 19),
                            generation=dict(completed=sum(record['status'] == 'completed' for record in case_slots.values()),
                              failed=sum(record['status'] != 'completed' for record in case_slots.values()),
                              missing=38 - len(case_slots), complete_pairs=sum(all(case_slots.get((case['id'], *route, arm), {}).get('status') == 'completed' for arm in ARMS) for route in routes)),
                            mechanical=mechanical_summary({key:value for key,value in observed.items() if key[0] == case['id']}))
        case_summary['factual_support'] = mechanical_summary({key:value for key,value in observed.items() if key[0] == case['id']}, 'factual_support')
        documents[target] = case_report(case, config, slots, sources, observed, case_summary, target, run, judgments)
    readme_path = destination / 'README.md'
    readme = (readme_path if readme_path.exists() else TESTS / 'README.md').read_text(encoding='utf-8')
    readme = re.sub(re.escape(MARKER_START) + r'.*?' + re.escape(MARKER_END) + r'\n*', '', readme, flags=re.S)
    readme = readme.replace('A rodada nova depende de um teto de gasto específico; o teto de US$ 10 era do piloto anterior.', 'A ampliação tem orçamento monetário null; valores financeiros são medições, não tetos. O teto histórico de US$ 10 não se aplica à ampliação.')
    readme = re.sub(r'✅ 2 casos concluídos:[^\n]*', '✅ Histórico separado: 2 casos, 76 textos, 38 pares e 114 julgamentos. Ampliação: dados observados na seção própria.', readme, count=1)
    readme = readme.replace('## Resumo dos resultados\n', '## Resumo dos resultados (histórico: dois contos)\n', 1)
    readme = readme.replace('Os novos gêneros ainda não foram avaliados.', 'Os resultados da ampliação estão separados abaixo.')
    for case in config['cases']:
        old_link = 'experiments/' + case['id'] + '/REPORT.md'
        new_link = old_link
        readme = readme.replace(old_link, new_link)
        case_records = [record for record in records.values() if record['case'] == case['id']]
        completed = sum(record['status'] == 'completed' for record in case_records)
        pairs = sum(all(slots.get((case['id'], *route, arm), {}).get('status') == 'completed' for arm in ARMS) for route in routes)
        costs = cost_group(case_records)
        judge_pairs = sum(sum(key[0] == case['id'] and 'failure_status' not in row for key, row in data.items()) for data in judgments.values())
        status = '✅ concluído' if completed == 38 and judge_pairs == 57 else '⏸️ pendente' if not case_records else '⏸️ parcial'
        cost = costs['known_usd'] + (' + desconhecido' if costs['unknown_calls'] else '') if case_records else 'não iniciado'
        seconds = f"{costs['elapsed_seconds']:.1f}" if case_records else 'não iniciado'
        row = '| ' + ' | '.join([cell(case['genre']), '[' + cell(case['title']) + '](' + new_link + ')', status, str(completed), str(pairs), cost, seconds]) + ' |'
        readme = re.sub(r'^\|[^\n]*' + re.escape(new_link) + r'[^\n]*$', lambda match: row, readme, flags=re.M)
    block = MARKER_START + '\n' + aggregate_block(summary) + '\n' + MARKER_END + '\n\n'
    readme = readme.replace('## Índice dos experimentos', block + '## Índice dos experimentos', 1)
    documents[readme_path] = readme
    documents[run / 'report-summary.json'] = json.dumps(summary, ensure_ascii=False, indent=2) + '\n'
    for path, text in documents.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('destination_tests', type=Path)
    parser.add_argument('--accounting', type=Path)
    args = parser.parse_args()
    print(json.dumps(render(args.run_dir, args.destination_tests, args.accounting), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
