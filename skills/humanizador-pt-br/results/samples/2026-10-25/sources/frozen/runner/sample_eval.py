#!/usr/bin/env python3
"""A/B exploratório de redação 0.8.1/0.9.1. Não aceita/rejeita releases.

API: prepare(...), load_frozen(root), step(root, dry_run=True), run(...), report(root).
A seleção vem de JSON externo: method=python-random-sample-v1, seed:string ou inteiro,
population_sha256:SHA256 dos bytes de PROMPTS.md, ordinals:cinco inteiros ordenados
iguais a sorted(random.Random(seed).sample(range(1, 25), 5)). Nunca usa resultados.

Somente imports normais do checkout confiável. O freeze nunca é carregado como
código. prepare executa apenas os dois scripts humanizar.py explicitamente
aprovados com trust_snapshot_code, em subprocessos isolados (-I -B), sem chave.
O snapshot git é fixo. Estado privado fora do Git; sem retry, fallback ou repair.
"""
import argparse
from decimal import Decimal
import json
import os
from pathlib import Path
import random
import re
import subprocess
import sys

import generation_eval as g
import eval_judges as judges
import eval_store as store_module

HERE = Path(__file__).resolve().parent
BASELINE_COMMIT = '607fe0230d19633f07529bcd6dacdab0b3252504'
SKILL_PATH = 'skills/humanizador-pt-br'
ARMS = g.ARMS  # baseline=0.8.1, skill=0.9.1. Both carry their skill package.
RUNNER_FILES = ('sample_eval.py', 'generation_eval.py', 'eval_judges.py', 'eval_store.py',
                'eval_delivery.py', 'eval_render.py', 'fixtures/history.json')
SOURCES = ('SKILL.md', 'references/catalogo.json', 'references/estilos.json', 'scripts/humanizar.py')
EXPECTED = g.expected_counts(5, 19, 'pair')
JEV = dict(model='typesafe/jev-1.13', mode='native', endpoint=dict(
    name='TypeSafe | typesafe/jev-1.13-20260917', model_id='typesafe/jev-1.13',
    tag='typesafe', provider_name='TypeSafe'))


def git_bytes(repo, name):
    return subprocess.run(['git', '-C', str(repo), 'show', BASELINE_COMMIT + ':' +
                           SKILL_PATH + '/' + name], check=True, capture_output=True).stdout


def selected_cases(prompts, history, sample):
    cases = g.parse_prompts(prompts.decode('utf-8'))
    if (sample.get('method') != 'python-random-sample-v1' or
            type(sample.get('seed')) not in (str, int) or sample['seed'] == '' or
            sample.get('population_sha256') != g.digest(prompts)):
        raise ValueError('external sample method/seed/population hash mismatch')
    expected = sorted(random.Random(sample['seed']).sample(range(1, 25), 5))
    if (sample.get('ordinals') != expected or
            any(type(i) is not int for i in sample['ordinals'])):
        raise ValueError('external sample must reproduce five seeded ordinals')
    if len(history['cases']) != 24 or len({c['id'] for c in history['cases']}) != 24:
        raise ValueError('expected original 24 case identifiers')
    for case, old in zip(cases, history['cases']):
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]+', old['id']):
            raise ValueError('unsafe case ID')
        case.update(id=old['id'], genre=case['title'].split(':')[0])
    return [c for c in cases if c['ordinal'] in expected]


def route_settings(history, effective):
    if history != g.read_json(HERE / 'fixtures/history.json'):
        raise ValueError('history differs from the approved 24-case/19-configuration fixture')
    routes = effective['routes']
    if (len(routes) != 19 or len({(r['model'], r['mode']) for r in routes}) != 19 or
            len({r['model'] for r in routes}) != 14):
        raise ValueError('expected all 19 original configurations / 14 models')
    for old, route in zip(history['routes'], routes):
        if any(route[k] != old[k] for k in ('model', 'mode', 'reasoning')):
            raise ValueError('effective routes must preserve original model/mode/reasoning order')
        if (route['endpoint']['model_id'] != route['model'] or
                route['endpoint']['name'].split(' | ')[-1] != old['endpoint']['name'].split(' | ')[-1]):
            raise ValueError('effective route must preserve exact model version')
    endpoint_keys = ('name', 'model_id', 'tag', 'provider_name')
    chat_judges = effective['judges']
    if (len(chat_judges) != 2 or any(
            any(old[k] != judge.get(k) for k in ('name', 'model', 'mode', 'reasoning')) or
            any(old['endpoint'][k] != judge['endpoint'].get(k) for k in endpoint_keys)
            for old, judge in zip(history['judges'], chat_judges)) or effective.get('jev', JEV) != JEV):
        raise ValueError('unchanged Astra/Opus and native Jev required')
    if effective['max_tokens'] != 4096 or effective['judge_max_tokens'] != history['judge_max_tokens']:
        raise ValueError('frozen output ceilings changed')
    return dict(routes=routes, judges=effective['judges'], jev=effective.get('jev', JEV),
                max_tokens=4096, judge_max_tokens=effective['judge_max_tokens'])


def brief(snapshot, ordinal):
    profile, genre = g.SELECTORS[ordinal - 1]
    args = ['scripts/humanizar.py', 'brief', '--profile', profile, '--genre', genre,
            '--breadth', '2', '--randomness', '0', '--seed', '17']
    # Local scripts are trusted explicitly, not a sandbox. Never pass ambient API secrets.
    env = {k: os.environ[k] for k in ('PATH', 'LANG', 'LC_ALL', 'SYSTEMROOT') if k in os.environ}
    result = subprocess.run([sys.executable, '-I', '-B', *args], cwd=snapshot,
                            capture_output=True, timeout=30, check=True, env=env)
    if not result.stdout.strip():
        raise ValueError('empty brief from snapshot')
    return dict(argv=['python3', '-I', '-B', *args], stdout_utf8=result.stdout.decode('utf-8'))


def generation_calls(root, config):
    frozen = Path(root) / 'frozen'
    for case in config['cases']:
        for index, route in enumerate(config['routes']):
            for arm in ARMS:
                messages = [dict(role='system', content=(frozen / arm / 'SKILL.md').read_bytes().decode('utf-8')),
                            dict(role='system', content=g.read_json(frozen / 'local' / arm /
                                 (case['id'] + '.json'))['stdout_utf8']),
                            dict(role='user', content=case['prompt'])]
                yield dict(slot=f'g.{case["id"]}.r{index:02}.{arm}', phase='generation',
                           case=case['id'], ordinal=case['ordinal'], route=index, arm=arm,
                           model=route['model'], mode=route['mode'], endpoint=route['endpoint'],
                           api='chat', payload=g.chat_payload(route, messages, config['max_tokens']))


def schedule(config, blinds):
    """Each route visits every selected prompt; each pair is judged before the next."""
    result = []
    by_case = {b['case']: b for b in blinds}
    for route in range(19):
        for case in config['cases']:
            blind = by_case[case['id']]
            deps = [f'g.{case["id"]}.r{route:02}.{arm}' for arm in ARMS]
            group = next(i for i, pids in enumerate(blind['groups'])
                         if {blind['mapping'][t] for t in blind['pairs'][pids[0]].values()} == set(deps))
            for slot in deps:
                result.append(dict(slot=slot, phase='generation'))
            for judge in g.JUDGES:
                result.append(dict(slot=f'j.{case["id"]}.c{group:02}.{judge}', phase='judge',
                                   case=case['id'], chunk=group, judge=judge, dependencies=deps))
    if len(result) != 475 or len({e['slot'] for e in result}) != 475:
        raise ValueError('schedule coverage mismatch')
    return result


def prepare(output, *, baseline_repo, candidate, history, prompts, sample,
            route_config=None, trust_snapshot_code=False, catalog=None, endpoints=None,
            probe_dir=None, probes_accounting=None, protocol=None):
    """Offline freeze. Existing output never overwritten; manifest is published last."""
    if not trust_snapshot_code:
        raise ValueError('explicit trust_snapshot_code required to execute local brief scripts')
    root, candidate = Path(output), Path(candidate)
    historical = g.read_json(history)
    effective_bytes = Path(route_config or history).read_bytes()
    settings = route_settings(historical, json.loads(effective_bytes))
    prompt_bytes, sample_bytes = Path(prompts).read_bytes(), Path(sample).read_bytes()
    if prompt_bytes != git_bytes(baseline_repo, 'results/PROMPTS.md'):
        raise ValueError('approved prompts differ from baseline snapshot')
    selection = json.loads(sample_bytes)
    cases = selected_cases(prompt_bytes, historical, selection)
    snapshots = {'baseline': {name: git_bytes(baseline_repo, name) for name in SOURCES},
                 'skill': {name: (candidate / name).read_bytes() for name in
                           (*SOURCES, 'references/exemplos.json')}}
    for arm, version in (('baseline', '0.8.1'), ('skill', '0.9.1')):
        if not re.search(r'^version: ' + re.escape(version) + '$', snapshots[arm]['SKILL.md'].decode(), re.M):
            raise ValueError('snapshot version mismatch: ' + arm)
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    with g.locked(root):
        frozen = root / 'frozen'
        for arm, files in snapshots.items():
            for name, data in files.items():
                g.immutable(frozen / arm / name, data)
            for case in cases:
                g.immutable(frozen / 'local' / arm / (case['id'] + '.json'),
                            brief(frozen / arm, case['ordinal']))
        for name, data in [('history.json', Path(history).read_bytes()), ('route-config.json', effective_bytes),
                           ('PROMPTS.md', prompt_bytes), ('sample.json', sample_bytes)]:
            g.immutable(frozen / name, data)
        for name, path in [('catalog.json', catalog), ('endpoints.json', endpoints),
                           ('probes-accounting.json', probes_accounting), ('protocol.md', protocol)]:
            if path:
                g.immutable(frozen / name, Path(path).read_bytes())
        if probe_dir:
            for path in sorted(Path(probe_dir).glob('*.json')):
                g.immutable(frozen / 'probe-evidence' / path.name, path.read_bytes())
        config = dict(schema='sample-ab-v1', exploratory_only=True, study='redacao',
                      versions=dict(baseline='0.8.1', skill='0.9.1'), baseline_commit=BASELINE_COMMIT,
                      cases=cases, **settings, judge_unit='pair', judge_rationale_version='2',
                      blind_seed='sample-ab-v1:' + str(selection['seed']), monetary_ceiling=None,
                      automatic_retry=False, treatment_packaging='both-skills-v2-brief',
                      primary_metric='H=100-deteccao; full-three-judge pairs',
                      order='route-case-pair-then-three-judges', rubric_provenance=g.HISTORY_COMMIT)
        g.immutable(frozen / 'config.json', config)
        g.immutable(frozen / 'generation-plan.json', list(generation_calls(root, config)))
        blinds = [g.blind_case(config, case) for case in cases]
        g.immutable(frozen / 'blind-plan.json', blinds)
        g.immutable(frozen / 'schedule.json', schedule(config, blinds))
        for name in RUNNER_FILES:
            g.immutable(frozen / 'runner' / name, (HERE / name).read_bytes())
        coverage = g.probe_coverage(settings['routes'] + settings['judges'] + [settings['jev']],
                                   sorted((frozen / 'probe-evidence').glob('*.json')))
        g.immutable(frozen / 'probe-coverage.json', coverage)
        manifest = dict(schema='sample-ab-v1', frozen_at=g.now(), expected=EXPECTED,
                        exploratory_only=True, release_decision='not_applicable',
                        baseline_commit=BASELINE_COMMIT, paid_calls=0,
                        sha256={p.relative_to(root).as_posix(): g.digest(p.read_bytes())
                                for p in sorted(frozen.rglob('*')) if p.is_file()})
        g.immutable(root / 'manifest.json', manifest)
    return manifest


def load_frozen(root):
    """Verify inputs as data, never import/execute a frozen runner or brief."""
    root = Path(root).resolve()
    if any(p.is_symlink() for p in root.rglob('*')):
        raise ValueError('symlink forbidden in frozen inputs or execution state')
    manifest = g.read_json(root / 'manifest.json')
    inventory = manifest['sha256']
    actual = {p.relative_to(root).as_posix() for p in (root / 'frozen').rglob('*') if p.is_file()}
    if actual != set(inventory):
        raise ValueError('frozen inventory mismatch')
    for name, sha in inventory.items():
        path = root / name
        if not name.startswith('frozen/') or path.is_symlink() or not path.resolve().is_relative_to(root / 'frozen'):
            raise ValueError('unsafe frozen path')
        if g.digest(path.read_bytes()) != sha:
            raise ValueError('frozen hash mismatch: ' + name)
    for name in RUNNER_FILES:
        if (root / 'frozen/runner' / name).read_bytes() != (HERE / name).read_bytes():
            raise ValueError('runner differs from trusted checkout: ' + name)
    config = g.read_json(root / 'frozen/config.json')
    settings = route_settings(g.read_json(root / 'frozen/history.json'), g.read_json(root / 'frozen/route-config.json'))
    cases = selected_cases((root / 'frozen/PROMPTS.md').read_bytes(), g.read_json(root / 'frozen/history.json'),
                           g.read_json(root / 'frozen/sample.json'))
    if (config['cases'] != cases or any(config[k] != v for k, v in settings.items()) or
            config['versions'] != dict(baseline='0.8.1', skill='0.9.1') or
            config['baseline_commit'] != BASELINE_COMMIT or config['judge_unit'] != 'pair' or
            config.get('judge_rationale_version') != '2' or
            config['automatic_retry'] is not False or config['exploratory_only'] is not True or
            manifest['expected'] != EXPECTED):
        raise ValueError('sample plan contract mismatch')
    if list(generation_calls(root, config)) != g.read_json(root / 'frozen/generation-plan.json'):
        raise ValueError('generation payload mismatch')
    blinds = [g.blind_case(config, case) for case in cases]
    if blinds != g.read_json(root / 'frozen/blind-plan.json') or schedule(config, blinds) != g.read_json(root / 'frozen/schedule.json'):
        raise ValueError('blind map/schedule mismatch')
    return config


def judge_plan(config, case, blind, chunk, records):
    calls, missing = g.judge_calls(config, case, blind, chunk, records)
    if missing:
        return None
    deps = {blind['mapping'][tid] for tid in calls[0]['judge_state']['textos']}
    return dict(calls=calls, raw_sha256={slot: records[slot][1]['raw_sha256'] for slot in sorted(deps)})


def audit(root, config):
    """Read-only recomputation from intent/raw; reject extra slots and any retry."""
    root = Path(root)
    marker = root / 'execution-mode.json'
    mode = g.read_json(marker)['mode'] if marker.exists() else None
    if mode not in (None, 'OFFLINE_FAKE', 'LIVE_API'):
        raise ValueError('unknown execution mode')
    store = store_module.Store(root, mode, readonly=True)
    records = store.audit()
    if records and mode is None:
        raise ValueError('records without execution mode')
    for path in (root / 'requests').glob('*/*'):
        if path.name not in ('intent.json', 'raw.json', 'result.json', 'transport-error.json'):
            raise ValueError('sample study prohibits retries/unknown request artifacts')
    expected = {c['slot']: c for c in generation_calls(root, config)}
    plans = {}
    for case in config['cases']:
        blind = g.blind_case(config, case)
        for chunk in range(len(blind['groups'])):
            plan = judge_plan(config, case, blind, chunk, records)
            if plan:
                name = f'{case["id"]}.c{chunk:02}.json'
                plans[name] = plan
                expected.update({c['slot']: c for c in plan['calls']})
    for slot, (call, result) in records.items():
        if expected.get(slot) != call:
            raise ValueError('stored call outside frozen matrix/blind inputs')
        if call['phase'] == 'judge' and not (root / 'judge-inputs' / f'{call["case"]}.c{call["chunk"]:02}.json').exists():
            raise ValueError('judge submitted without frozen input')
    for path in (root / 'judge-inputs').glob('*'):
        if not path.is_file() or g.read_json(path) != plans.get(path.name):
            raise ValueError('frozen judge input/raw binding mismatch')
    return mode, records, plans


def next_call(root, config, records, plans):
    blocked = [dict(slot=slot, status=r['status']) for slot, (_, r) in records.items()
               if r['status'] not in store_module.TERMINAL]
    if blocked:
        return None, dict(status='blocked', blocked=blocked, skipped=[])
    generated = {c['slot']: c for c in generation_calls(root, config)}
    skipped = []
    for event in g.read_json(Path(root) / 'frozen/schedule.json'):
        if event['slot'] in records:
            continue
        if event['phase'] == 'generation':
            return generated[event['slot']], dict(status='ready', skipped=skipped)
        name = f'{event["case"]}.c{event["chunk"]:02}.json'
        plan = plans.get(name)
        if plan is None:
            if any(slot not in records for slot in event['dependencies']):
                raise ValueError('schedule dependency missing before judge')
            skipped.append(dict(slot=event['slot'], reason='incomplete_or_invalid_pair'))
            continue
        return next(c for c in plan['calls'] if c['slot'] == event['slot']), dict(status='ready', skipped=skipped)
    return None, dict(status='finished', skipped=skipped)


def live_preflight(root, config, expected_manifest_sha256):
    if g.digest((root / 'manifest.json').read_bytes()) != expected_manifest_sha256:
        raise ValueError('explicit reviewed manifest SHA256 required for live execution')
    if any((p / '.git').exists() for p in (root, *root.parents)):
        raise ValueError('live raw store must be private outside Git')
    if root.stat().st_mode & 0o077:
        raise ValueError('live raw root must have private permissions (0700)')
    frozen = root / 'frozen'
    catalog = {m['id']: m for m in g.read_json(frozen / 'catalog.json')['data']}
    endpoints = g.read_json(frozen / 'endpoints.json')
    routes = config['routes'] + config['judges'] + [config['jev']]
    for route in routes:
        g.route_evidence(route, catalog, endpoints)
    coverage = g.probe_coverage(routes, sorted((frozen / 'probe-evidence').glob('*.json')))
    if coverage != g.read_json(frozen / 'probe-coverage.json') or not all(c['accepted_evidence'] for c in coverage):
        raise ValueError('complete exact-route accepted probes required')
    receipt = g.read_json(frozen / 'probes-accounting.json')
    if receipt.get('ledger_reconciliation') in (None, False, 'pending', 'unknown'):
        raise ValueError('reconciled separate probe accounting required')


def run(root, *, max_new_calls=1, dry_run=True, offline=False, transport=None,
        key='', execute_paid=False, expected_manifest_sha256=None):
    """Bounded execution. No resubmission path, even for billed invalid text.

    dry_run is read-only. Only offline=True accepts an explicit offline_only fake.
    Paid execution requires explicit approval, reviewed manifest hash and preflight.
    """
    if type(max_new_calls) is not int or max_new_calls < 1:
        raise ValueError('max_new_calls must be a positive integer')
    root = Path(root).resolve()
    config = load_frozen(root)
    if dry_run:
        if key or execute_paid or transport is not None:
            raise ValueError('dry-run never accepts credentials or transport')
        _, records, plans = audit(root, config)
        call, state = next_call(root, config, records, plans)
        return dict(state, new_calls=0, next_slot=call['slot'] if call else None,
                    expected=EXPECTED, submitted=len(records), dry_run=True)
    with g.locked(root):
        # Revalidate under the shared lock before reading or submitting mutable state.
        config = load_frozen(root)
        mode, records, plans = audit(root, config)
        target_mode = 'OFFLINE_FAKE' if offline else 'LIVE_API'
        if mode is not None and mode != target_mode:
            raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
        if offline:
            if key or execute_paid or not getattr(transport, 'offline_only', False):
                raise ValueError('offline execution requires explicit fake and no API key')
        else:
            if not execute_paid or transport is not None:
                raise ValueError('live calls require execute_paid; transport injection is offline only')
            live_preflight(root, config, expected_manifest_sha256)
            transport = store_module.real_transport(key)
        new_calls = 0
        while True:
            call, state = next_call(root, config, records, plans)
            if call is None or new_calls >= max_new_calls:
                break
            if mode is None:
                g.immutable(root / 'execution-mode.json', dict(mode=target_mode, synthetic=offline))
                mode = target_mode
            if call['phase'] == 'judge':
                name = f'{call["case"]}.c{call["chunk"]:02}.json'
                path = root / 'judge-inputs' / name
                if not path.exists():
                    g.immutable(path, plans[name])
                elif g.read_json(path) != plans[name]:
                    raise ValueError('judge input changed')
            store = store_module.Store(root, mode)
            result = store.submit(call, transport)
            records[call['slot']] = (call, result)
            new_calls += 1
            if call['phase'] == 'generation':
                case = next(c for c in config['cases'] if c['id'] == call['case'])
                blind = g.blind_case(config, case)
                for chunk in range(len(blind['groups'])):
                    plan = judge_plan(config, case, blind, chunk, records)
                    if plan:
                        plans[f'{case["id"]}.c{chunk:02}.json'] = plan
        summary = dict(state, new_calls=new_calls, next_slot=call['slot'] if call else None,
                       expected=EXPECTED, submitted=len(records), execution_mode=mode,
                       completed=sum(r['status'] == 'completed' for _, r in records.values()),
                       invalid=sum(r['status'] == 'invalid_response' for _, r in records.values()))
        g.derived_write(root / 'runtime-summary.json', summary)
        return summary


def step(root, **kwargs):
    """Exactly zero (dry-run/blocked/finished) or one new submission."""
    return run(root, max_new_calls=1, **kwargs)


def mean(values):
    return sum(values) / len(values) if values else None


def metrics(rows, expected):
    """All means are paired; missing judgments never become zeros or votes."""
    result = dict(n=len(rows), expected=expected,
                  preferencia={arm: sum(r['preferencia'] == arm for r in rows) for arm in (*ARMS, 'empate')},
                  critico={arm: sum(r['critico'][arm] for r in rows) for arm in ARMS})
    for field in ('H', *judges.DIMENSIONS):
        result[field] = {arm: mean([r[field][arm] for r in rows]) for arm in ARMS}
    result['delta_H'] = mean([r['H']['skill'] - r['H']['baseline'] for r in rows])
    result['critical_denominator_per_arm'] = len(rows)
    return result


def accounting(records):
    """Secondary observed subtotals, never invented zero cost for unknown calls."""
    output = {}
    groups = {'all': list(records.values())}
    for arm in ARMS:
        groups['generation.' + arm] = [(c, r) for c, r in records.values()
                                       if c['phase'] == 'generation' and c['arm'] == arm]
    for name in g.JUDGES:
        groups['judge.' + name] = [(c, r) for c, r in records.values()
                                  if c['phase'] == 'judge' and c['judge'] == name]
    for name, rows in groups.items():
        costs = [Decimal(r['telemetry']['cost_usd']) for _, r in rows
                 if r.get('telemetry', {}).get('cost_usd') is not None]
        known = str(sum(costs, Decimal(0)))
        data = dict(submitted=len(rows), cost_observed_calls=len(costs), known_cost_usd=known,
                    cost_usd=known if len(costs) == len(rows) else None)
        for label, fields in [('input_tokens', ('prompt_tokens', 'input_tokens')),
                              ('output_tokens', ('completion_tokens', 'output_tokens'))]:
            values = [r.get('telemetry', {}).get('usage', {}).get(fields[c['api'] == 'decisions']) for c, r in rows]
            valid = [v for v in values if type(v) is int and v >= 0]
            data[label] = dict(known=sum(valid), observed_calls=len(valid),
                               total=sum(valid) if len(valid) == len(rows) else None)
        output[name] = data
    return output


def report(root):
    """Audited JSON with complete texts and scores. Does not write into the run."""
    root = Path(root)
    config = load_frozen(root)
    mode, records, plans = audit(root, config)
    _, runtime = next_call(root, config, records, plans)
    pairs = []
    per_judge = {name: [] for name in g.JUDGES}
    complete_rows = []
    for case in config['cases']:
        blind = g.blind_case(config, case)
        for route, spec in enumerate(config['routes']):
            slots = {arm: f'g.{case["id"]}.r{route:02}.{arm}' for arm in ARMS}
            chunk = next(i for i, group in enumerate(blind['groups'])
                         if {blind['mapping'][t] for t in blind['pairs'][group[0]].values()} == set(slots.values()))
            pid = blind['groups'][chunk][0]
            ab_arms = {ab: records[blind['mapping'][tid]][0]['arm'] if blind['mapping'][tid] in records
                       else next(arm for arm, slot in slots.items() if slot == blind['mapping'][tid])
                       for ab, tid in blind['pairs'][pid].items()}
            tid_arm = {tid: ab_arms[ab] for ab, tid in blind['pairs'][pid].items()}
            pair = dict(case=case['id'], title=case['title'], prompt=case['prompt'],
                        route=route, configuration=spec, texts={}, judgments={}, H=None, delta_H=None)
            for arm, slot in slots.items():
                r = records[slot][1] if slot in records else {}
                pair['texts'][arm] = dict(slot=slot, status=r.get('status', 'pending'), text=r.get('text'),
                    telemetry=r.get('telemetry'), validation_issues=r.get('validation_issues', []),
                    raw_sha256=r.get('raw_sha256'), raw_file=f'requests/{slot}/raw.json' if r.get('raw_sha256') else None)
            for name in g.JUDGES:
                slot = f'j.{case["id"]}.c{chunk:02}.{name}'
                r = records[slot][1] if slot in records else {}
                row = dict(slot=slot, status=r.get('status', 'pending'))
                if r.get('status') == 'completed':
                    judgment = r['judgment']
                    choice = judgment['preferencia'][pid]
                    row.update(H={arm: 100 - judgment['deteccao'][tid] for tid, arm in tid_arm.items()},
                               preferencia='empate' if choice == 'empate' else ab_arms[choice],
                               raw_judgment=judgment, raw_sha256=r['raw_sha256'])
                    for field in (*judges.DIMENSIONS, 'critico', 'justificativa'):
                        row[field] = {arm: judgment['qualidade'][tid][field] for tid, arm in tid_arm.items()}
                    row['delta_H'] = row['H']['skill'] - row['H']['baseline']
                    per_judge[name].append(row)
                pair['judgments'][name] = row
            if all(r['status'] == 'completed' for r in pair['judgments'].values()):
                complete_rows.extend(pair['judgments'].values())
                pair['H'] = {arm: mean([r['H'][arm] for r in pair['judgments'].values()]) for arm in ARMS}
                pair['delta_H'] = pair['H']['skill'] - pair['H']['baseline']
            pairs.append(pair)
    summary = dict(exploratory_only=True, release_decision='not_applicable',
                   model_writing_evidence=mode == 'LIVE_API', execution_mode=mode,
                   expected=EXPECTED, complete_pairs=sum(p['H'] is not None for p in pairs),
                   valid_judgments=sum(len(rows) for rows in per_judge.values()),
                   aggregate=metrics(complete_rows, 285),
                   by_judge={name: metrics(rows, 95) for name, rows in per_judge.items()},
                   all_valid_judgments=metrics([r for rows in per_judge.values() for r in rows], 285),
                   runtime=runtime, secondary_telemetry=accounting(records),
                   aggregation='primary: mean of equal-weight complete three-judge pairs; per-judge includes own valid pairs',
                   limitations=['Exploratory five-prompt writing sample, not release acceptance or rewriting.',
                                'H=100-deteccao is not a calibrated authorship probability.',
                                'Naturalidade and fidelity (raw correcao/critico) are separate from H and preference.',
                                'Pooled judgments on the same texts are not independent experiments.',
                                'Missing/invalid outputs are retained, not repeated; no imputed scores.',
                                'Native Jev supplies no textual justification.'])
    return dict(schema='sample-ab-report-v1', manifest_sha256=g.digest((root / 'manifest.json').read_bytes()),
                versions=config['versions'], sample=g.read_json(root / 'frozen/sample.json'),
                summary=summary, pairs=pairs)


def fence(text):
    marker = '`' * max(3, 1 + max((len(m) for m in re.findall(r'`+', text)), default=0))
    return marker + 'text\n' + text + '\n' + marker


def write_report(root, output):
    """New directory only. JSON is authoritative; Markdown retains literal texts."""
    data = report(root)
    output = Path(output)
    if output.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError('reports must be outside the private run')
    summary = data['summary']
    lines = ['# A/B amostral: 0.8.1 versus 0.9.1', '',
             'Exploratório, só redação. Não decide aceitação da versão. H = 100 menos impressão de IA.',
             'H não é probabilidade calibrada de autoria. Custo/tokens são telemetria secundária.', '',
             f'Modo: {summary["execution_mode"] or "não executado"}.',
             f'Pares completos: {summary["complete_pairs"]}/95. Julgamentos válidos: {summary["valid_judgments"]}/285.', '',
             '| Juiz | n / planejado | H 0.8.1 | H 0.9.1 | ΔH | Naturalidade 0.8.1 / 0.9.1 | Preferência ref. / cand. / empate | Correção ref. / cand. | Críticas ref. / cand. |',
             '|---|---:|---:|---:|---:|---|---|---|---|']
    for name, row in [*summary['by_judge'].items(), ('Agregado, só trios completos', summary['aggregate'])]:
        lines.append(f'| {name} | {row["n"]}/{row["expected"]} | {row["H"]["baseline"]} | {row["H"]["skill"]} | {row["delta_H"]} | '
                     f'{row["naturalidade"]["baseline"]} / {row["naturalidade"]["skill"]} | '
                     f'{row["preferencia"]["baseline"]} / {row["preferencia"]["skill"]} / {row["preferencia"]["empate"]} | '
                     f'{row["correcao"]["baseline"]} / {row["correcao"]["skill"]} | {row["critico"]["baseline"]} / {row["critico"]["skill"]} |')
    lines.extend(['', 'Médias pareadas, peso igual por par/configuração. Críticas: numerador sobre n de cada braço.',
                  'Ausente = null, nunca zero. Três votos sobre os mesmos textos não são experimentos independentes.',
                  'Telemetria observada e todos os campos da rubrica estão em SUMMARY.json.'])
    for pair in data['pairs']:
        spec = pair['configuration']
        lines.extend(['', f'## {pair["case"]}, r{pair["route"]:02}', '',
                      f'{spec["model"]}, {spec["mode"]}, {spec["endpoint"]["tag"]}', '',
                      '### Pedido literal', '', fence(pair['prompt'])])
        for arm, version in data['versions'].items():
            row = pair['texts'][arm]
            lines.extend(['', f'### {version} ({arm}): {row["status"]}', '',
                          fence(row['text']) if isinstance(row['text'], str) else 'Sem texto disponível; consultar estado/raw.'])
        lines.extend(['', f'H do par: {pair["H"]}; ΔH: {pair["delta_H"]}.'])
        for name, row in pair['judgments'].items():
            lines.extend(['', f'### Juiz {name}: {row["status"]}', '',
                          fence(json.dumps(row, ensure_ascii=False, indent=2))])
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    g.immutable(output / 'SUMMARY.json', data)
    g.immutable(output / 'REPORT.md', ('\n'.join(lines) + '\n').encode('utf-8'))
    return dict(summary=str(output / 'SUMMARY.json'), report=str(output / 'REPORT.md'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='offline freeze, never calls an API')
    for name in ('output', 'baseline-repo', 'candidate', 'history', 'prompts', 'sample'):
        prep.add_argument('--' + name, type=Path, required=True)
    for name in ('route-config', 'catalog', 'endpoints', 'probe-dir', 'probes-accounting', 'protocol'):
        prep.add_argument('--' + name, type=Path)
    prep.add_argument('--trust-snapshot-code', action='store_true')
    for name in ('step', 'run'):
        execute = commands.add_parser(name, help='read-only by default; explicit paid opt-in')
        execute.add_argument('--root', type=Path, required=True)
        execute.add_argument('--dry-run', action='store_true')
        execute.add_argument('--execute-paid', action='store_true')
        execute.add_argument('--expected-manifest-sha256')
        execute.add_argument('--key-env', default='OPENROUTER_API_KEY')
        if name == 'run':
            execute.add_argument('--max-new-calls', type=int, required=True)
    export = commands.add_parser('report', help='read-only audit, new JSON/Markdown directory')
    export.add_argument('--root', type=Path, required=True)
    export.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'prepare':
        values = vars(args).copy()
        values.pop('command')
        result = prepare(**values)
        result = {k: v for k, v in result.items() if k != 'sha256'}
        result['manifest_sha256'] = g.digest((args.output / 'manifest.json').read_bytes())
    elif args.command == 'report':
        result = write_report(args.root, args.output)
    else:
        if args.dry_run and args.execute_paid:
            parser.error('--dry-run and --execute-paid are mutually exclusive')
        result = run(args.root, max_new_calls=getattr(args, 'max_new_calls', 1),
                     dry_run=not args.execute_paid, execute_paid=args.execute_paid,
                     key=os.environ.get(args.key_env, '') if args.execute_paid else '',
                     expected_manifest_sha256=args.expected_manifest_sha256)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 2 if result.get('status') == 'blocked' else 0


if __name__ == '__main__':
    raise SystemExit(main())
