#!/usr/bin/env python3
"""Independent PT-BR generation study. Stdlib, explicit paid entrypoint only.

Adapted from generos.py at d14174698015e66f2c3814d0fe0110770509a242.
No rewriting, inherited conversation, retries, fallback or spending ceiling.
"""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ARMS = ('baseline', 'skill')
JUDGES = ('jev', 'astra', 'opus')
HISTORY_COMMIT = 'd14174698015e66f2c3814d0fe0110770509a242'
# Fixed editorial selectors, frozen before any generation. No candidate-dependent selection.
SELECTORS = [
    ('jornalistico', 'noticia'), ('jornalistico', 'reportagem'),
    ('tecnico-preciso', 'tecnico'), ('tecnico-preciso', 'tecnico'),
    ('didatico', 'didatico'), ('tecnico-preciso', 'relatorio'),
    ('didatico', 'didatico'), ('tecnico-preciso', 'relatorio'),
    ('didatico', 'didatico'), ('tecnico-preciso', 'relatorio'),
    ('academico', 'academico'), ('academico', 'academico'),
    ('didatico', 'didatico'), ('didatico', 'didatico'),
    ('executivo-direto', 'proposta'), ('executivo-direto', 'negocios'),
    ('conversacional-contido', 'email'), ('executivo-direto', 'relatorio'),
    ('argumentativo-sobrio', 'artigo'), ('argumentativo-sobrio', 'ensaio'),
    ('conversacional-contido', 'post'), ('conversacional-contido', 'roteiro'),
    ('literario', 'conto'), ('literario', 'cronica')]


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                      allow_nan=False).encode('utf-8')


def digest(data):
    return hashlib.sha256(data if isinstance(data, bytes) else encoded(data)).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def fsync_dir(path):
    fd = os.open(path, os.O_DIRECTORY | os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def immutable(path, data):
    """Atomic no-clobber publication: fsynced temp -> hardlink -> directory fsync."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = data if isinstance(data, bytes) else encoded(data)
    fd, temp = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.fchmod(stream.fileno(), 0o400)
        os.link(temp, path)  # EEXIST rather than replacing another artifact.
        fsync_dir(path.parent)
    finally:
        os.unlink(temp)
        fsync_dir(path.parent)
    return digest(data)


@contextmanager
def locked(root):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    with open(root / '.runner.lock', 'a') as stream:
        os.chmod(stream.name, 0o600)
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('runner lock held; no concurrent execution') from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def parse_prompts(text):
    """Preserve the literal inside each approved text fence, excluding fence LF."""
    pattern = r'^### (\d{2})\. ([^\n]+)\n\n```text\n(.*?)\n```(?=\n|$)'
    cases = [dict(ordinal=int(n), title=title, prompt=prompt)
             for n, title, prompt in re.findall(pattern, text, flags=re.M | re.S)]
    if [c['ordinal'] for c in cases] != list(range(1, 25)):
        raise ValueError('expected literal 24 ordered approved prompt fences')
    return cases


def route_evidence(route, catalog, endpoints):
    model, ep = route['model'], route['endpoint']
    canonical = ep['name'].split(' | ')[-1]
    # Native Jev decisions is absent from /models, but has an exact dated endpoint.
    native_jev = model == 'typesafe/jev-1.13' and route['mode'] == 'native'
    if (model not in catalog and not native_jev) or (model in catalog and
            catalog[model]['canonical_slug'] != canonical):
        raise ValueError('model/version unavailable or changed: ' + model)
    matches = [e for e in endpoints.get(model, {}).get('endpoints', [])
               if e['tag'] == ep['tag'] and e['name'] == ep['name']
               and e['model_id'] == ep['model_id'] and e['provider_name'] == ep['provider_name']]
    if len(matches) != 1 or matches[0].get('status') != 0:
        raise ValueError('exact historical route unavailable: ' + model + '/' + ep['tag'])
    return dict(model=model, mode=route['mode'], canonical_slug=canonical,
                historical_endpoint=ep['name'], live_endpoint=matches[0])


def local_selection(skill, ordinal):
    profile, genre = SELECTORS[ordinal - 1]
    commands = {
        'catalog': ['catalog', '--query', '', '--genre', genre, '--limit', '5'],
        'styles': ['styles', '--query', profile, '--genre', genre, '--limit', '5'],
        'structure': ['structure', '--profile', profile, '--genre', genre,
                      '--breadth', '2', '--randomness', '0', '--seed', '17']}
    result = {}
    for name, args in commands.items():
        proc = subprocess.run([sys.executable, 'scripts/humanizar.py', *args], cwd=skill,
                              capture_output=True, check=True, timeout=30)
        value = json.loads(proc.stdout)
        if not value:
            raise ValueError('empty local selection: ' + name)
        result[name] = dict(argv=['python3', 'scripts/humanizar.py', *args], result=value,
                            stdout_utf8=proc.stdout.decode('utf-8'))
    return result


def apply_amendments(routes, amendments, endpoints):
    effective = json.loads(json.dumps(routes))
    seen = set()
    for item in amendments.get('amendments', []):
        if item.get('model_changed') is not False or item.get('candidate_outputs_replayed') is not False:
            raise ValueError('amendment must preserve model and prohibit replay')
        targets = [r for r in effective if r['model'] == item['model'] and r['mode'] in item['modes']]
        if len(targets) != len(item['modes']):
            raise ValueError('amendment modes must exist exactly once')
        for route in targets:
            identity = route['model'], route['mode']
            if identity in seen or route['endpoint']['tag'] != item['original_provider']:
                raise ValueError('conflicting route amendment')
            seen.add(identity)
            canonical = route['endpoint']['name'].split(' | ')[-1]
            matches = [e for e in endpoints[route['model']]['endpoints']
                       if e['tag'] == item['effective_provider'] and
                       e['name'].split(' | ')[-1] == canonical and e['model_id'] == route['model']]
            if len(matches) != 1:
                raise ValueError('exact same-version amended route missing')
            route['endpoint'] = matches[0]
    return effective


def probe_coverage(routes, probes):
    coverage = []
    for route in routes:
        matching = []
        for path in probes:
            p = read_json(path)
            payload = p.get('payload', {})
            response = p.get('response', {})
            provider = payload.get('provider', {})
            native = route['mode'] == 'native'
            usage = response.get('usage', {})
            token_fields = ('input_tokens', 'output_tokens') if native else ('prompt_tokens', 'completion_tokens')
            choice = (response.get('choices') or [{}])[0]
            valid_text = native or (choice.get('finish_reason') == 'stop' and
                isinstance(choice.get('message', {}).get('content'), str) and
                bool(choice['message']['content'].strip()) and not choice['message'].get('refusal'))
            if (p.get('kind') == 'availability_probe_not_candidate' and p.get('status') == 'accepted'
                and p.get('model') == route['model'] and p.get('mode') == route['mode']
                and payload.get('model') == route['model'] and
                (native or payload.get('reasoning') == route['reasoning']) and
                provider.get('only') == [route['endpoint']['tag']] and provider.get('allow_fallbacks') is False
                and response.get('provider') == route['endpoint']['provider_name']
                and response.get('model') in {route['model'], route['endpoint']['name'].split(' | ')[-1]}
                and response.get('id') and not response.get('error') and valid_text
                and all(type(usage.get(f)) is int and usage[f] >= 0 for f in token_fields)
                and type(usage.get('cost')) in (int, float) and usage['cost'] >= 0):
                matching.append(path.name)
        coverage.append(dict(model=route['model'], mode=route['mode'],
            tag=route['endpoint']['tag'], accepted_evidence=matching))
    return coverage


def prepare(root, skill, history, catalog, endpoints, probes=(), amendments=None,
            probe_dir=None, probes_accounting=None):
    """Materialize snapshots and a reviewable matrix; no network calls or API key."""
    root, skill = Path(root), Path(skill)
    root.mkdir(parents=True, exist_ok=False, mode=0o700)
    with locked(root):
        historical = read_json(history)
        if historical.get('budget_usd', 'missing') is not None:
            raise ValueError('historical matrix must be explicitly uncapped')
        if len(historical['routes']) != 19:
            raise ValueError('only original 19 configurations approved')
        observed_models = len({r['model'] for r in historical['routes']})
        if observed_models != 14:
            raise ValueError('only the corrected 14 original model IDs approved')
        if len({(r['model'], r['mode']) for r in historical['routes']}) != 19:
            raise ValueError('duplicate historical configuration')
        frozen = root / 'frozen'
        sources = ['SKILL.md', 'references/catalogo.json', 'references/estilos.json',
                   'scripts/humanizar.py', 'results/PROMPTS.md']
        for name in sources:
            immutable(frozen / 'skill' / name, (skill / name).read_bytes())
        skill_text = (frozen / 'skill/SKILL.md').read_text('utf-8')
        if not re.search(r'^version: 0\.5\.1$', skill_text, re.M):
            raise ValueError('treatment must be exactly SKILL.md 0.5.1')
        immutable(frozen / 'history.json', Path(history).read_bytes())
        immutable(frozen / 'catalog.json', Path(catalog).read_bytes())
        immutable(frozen / 'endpoints.json', Path(endpoints).read_bytes())
        catalog_map = {m['id']: m for m in read_json(frozen / 'catalog.json')['data']}
        live_endpoints = read_json(frozen / 'endpoints.json')
        routes = historical['routes']
        amendment_data = read_json(amendments) if amendments else {'amendments': []}
        immutable(frozen / 'route-amendments.json', amendment_data)
        routes = apply_amendments(routes, amendment_data, live_endpoints)
        judges = historical['judges']
        if {j['name'] for j in judges} != {'astra', 'opus'}:
            raise ValueError('expected original Astra and Opus judges')
        evidence = [route_evidence(r, catalog_map, live_endpoints) for r in routes + judges]
        jev = dict(model='typesafe/jev-1.13', mode='native', endpoint=dict(
            name='TypeSafe | typesafe/jev-1.13-20260917', model_id='typesafe/jev-1.13',
            tag='typesafe', provider_name='TypeSafe'))
        evidence.append(route_evidence(jev, catalog_map, live_endpoints))
        immutable(frozen / 'route-evidence.json', evidence)
        probes = list(probes) + (sorted(Path(probe_dir).glob('*.json')) if probe_dir else [])
        for i, path in enumerate(probes):
            immutable(frozen / 'probe-evidence' / f'{i:03}-{Path(path).name}', Path(path).read_bytes())
        coverage = probe_coverage(routes + judges + [jev], probes)
        immutable(frozen / 'probe-coverage.json', coverage)
        reconciled = False
        if probes_accounting:
            immutable(frozen / 'probes-accounting.json', Path(probes_accounting).read_bytes())
            receipt = read_json(frozen / 'probes-accounting.json')
            reconciled = receipt.get('ledger_reconciliation') not in (None, False, 'pending', 'unknown')
        cases = parse_prompts((frozen / 'skill/results/PROMPTS.md').read_text('utf-8'))
        old_cases = historical['cases']
        if len(old_cases) != 24:
            raise ValueError('expected original 24 case identifiers')
        for case, old in zip(cases, old_cases):
            if not re.fullmatch(r'[a-z0-9][a-z0-9-]+', old['id']):
                raise ValueError('unsafe case ID')
            case['id'] = old['id']
            case['genre'] = case['title'].split(':')[0]
            # Old prompts/checks are provenance, never input to either candidate or judge.
            local = local_selection(frozen / 'skill', case['ordinal'])
            immutable(frozen / 'local' / (case['id'] + '.json'), local)
        config = dict(schema=1, study='independent-generation', skill_version='0.5.1',
                      cases=cases, routes=routes, historical_routes=historical['routes'], judges=judges, jev=jev,
                      max_tokens=historical['max_tokens'], judge_max_tokens=historical['judge_max_tokens'],
                      chunk_pairs=4, blind_seed='humanizador-0.5.1-independent-v1',
                      monetary_ceiling=None, automatic_retry=False,
                      pilot='first-case-first-route-singleton; same full-matrix slots',
                      rubric_provenance=HISTORY_COMMIT)
        immutable(frozen / 'config.json', config)
        plan = [dict(slot=c['slot'], payload_sha256=digest(c['payload']))
                for c in generation_calls(root, config)]
        if len(plan) != 912 or len({c['slot'] for c in plan}) != 912:
            raise ValueError('generation coverage mismatch')
        immutable(frozen / 'generation-plan.json', plan)
        immutable(frozen / 'blind-plan.json', [blind_case(config, case) for case in cases])
        runner_files = sorted(HERE.glob('*.py'))
        for path in runner_files:
            immutable(frozen / 'runner' / path.name, path.read_bytes())
        hashes = {p.relative_to(root).as_posix(): digest(p.read_bytes())
                  for p in sorted(frozen.rglob('*')) if p.is_file()}
        manifest = dict(schema=1, frozen_at=now(), sha256=hashes,
            monetary_ceiling=None, paid_calls=0, expected=dict(generations=912, pairs=456,
            judge_calls=432, pair_judgments=1368, individual_impression_scores=2736),
            preparation_only=True, raw_probes=len(probes), historical_commit=HISTORY_COMMIT,
            configurations=len(routes), distinct_models=observed_models,
            declared_models=14, model_count_discrepancy=observed_models != 14,
            probes_complete=all(c['accepted_evidence'] for c in coverage),
            probes_accounting_present=bool(probes_accounting),
            probes_accounting_reconciled=reconciled,
            limitations=['AI impression is not proof of authorship or a calibrated probability.',
                        'Offline tests are not model-writing evidence.',
                        'Catalog/route identity does not verify reasoning acceptance; separate raw probes required.',
                        'Same texts judged three times are descriptive votes, not independent experiments.'])
        immutable(root / 'manifest.json', manifest)
        return manifest


def load_frozen(root):
    root = Path(root)
    manifest = read_json(root / 'manifest.json')
    for name, expected in manifest['sha256'].items():
        path = root / name
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError('frozen hash mismatch: ' + name)
        if name.startswith('frozen/runner/'):
            current = HERE / Path(name).name
            if not current.exists() or digest(current.read_bytes()) != expected:
                raise ValueError('runner hash changed: ' + name)
    config = read_json(root / 'frozen/config.json')
    prompts = parse_prompts((root / 'frozen/skill/results/PROMPTS.md').read_text('utf-8'))
    if [c['prompt'] for c in prompts] != [c['prompt'] for c in config['cases']]:
        raise ValueError('literal prompt/config mismatch')
    actual = [dict(slot=c['slot'], payload_sha256=digest(c['payload']))
              for c in generation_calls(root, config)]
    if actual != read_json(root / 'frozen/generation-plan.json'):
        raise ValueError('payload hash mismatch')
    return config


def chat_payload(route, messages, max_tokens):
    ep = route['endpoint']
    return dict(model=route['model'], messages=messages, max_tokens=max_tokens,
                reasoning=route['reasoning'], stream=False, usage={'include': True},
                provider=dict(only=[ep['tag']], allow_fallbacks=False,
                              require_parameters=True, data_collection='allow'))


def generation_calls(root, config):
    frozen = Path(root) / 'frozen'
    context = [dict(role='system', content=(frozen / 'skill' / name).read_bytes().decode('utf-8'))
               for name in ['SKILL.md', 'references/catalogo.json', 'references/estilos.json']]
    for case in config['cases']:
        local = (frozen / 'local' / (case['id'] + '.json')).read_bytes().decode('utf-8')
        user = dict(role='user', content=case['prompt'])
        for index, route in enumerate(config['routes']):
            for arm in ARMS:
                messages = ([*context, dict(role='system', content=local), user]
                            if arm == 'skill' else [user])
                yield dict(slot=f'g.{case["id"]}.r{index:02}.{arm}', phase='generation',
                           case=case['id'], ordinal=case['ordinal'], route=index, arm=arm,
                           model=route['model'], mode=route['mode'], endpoint=route['endpoint'],
                           api='chat', payload=chat_payload(route, messages, config['max_tokens']))


def blind_case(config, case):
    rng = random.Random(config['blind_seed'] + case['id'])
    routes = list(range(len(config['routes'])))
    rng.shuffle(routes)
    mapping, pairs = {}, {}
    for i, index in enumerate(routes):
        arms = list(ARMS)
        rng.shuffle(arms)
        pair = {}
        for j, arm in enumerate(arms):
            tid = f't{i * 2 + j:03}'
            mapping[tid] = f'g.{case["id"]}.r{index:02}.{arm}'
            pair['AB'[j]] = tid
        pairs[f'p{i:03}'] = pair
    first = next(pid for pid, pair in pairs.items() if '.r00.' in mapping[pair['A']])
    rest = [pid for pid in pairs if pid != first]
    groups = [[first]] + [rest[i:i + 4] for i in range(0, len(rest), 4)]
    return dict(case=case['id'], mapping=mapping, pairs=pairs, groups=groups)


def judge_calls(config, case, blind, index, records):
    from eval_judges import JUDGE, decisions_payload
    group = blind['groups'][index]
    pairs = {pid: blind['pairs'][pid] for pid in group}
    tids = [tid for pair in pairs.values() for tid in pair.values()]
    slots = [blind['mapping'][tid] for tid in tids]
    if any(slot not in records or records[slot][1]['status'] != 'completed' for slot in slots):
        return [], slots
    state = dict(prompt=case['prompt'], textos={tid: records[blind['mapping'][tid]][1]['text']
                 for tid in tids}, pares=pairs)
    # Exact same anonymous input for all three judges, without model/arm mapping.
    native = config['jev']
    calls = [dict(slot=f'j.{case["id"]}.c{index:02}.jev', phase='judge', case=case['id'],
                  judge='jev', chunk=index, api='decisions', model=native['model'],
                  mode=native['mode'], endpoint=native['endpoint'], judge_state=state,
                  payload=decisions_payload(state))]
    for judge in config['judges']:
        payload = chat_payload(judge, [dict(role='system', content=JUDGE),
            dict(role='user', content=encoded(state).decode('utf-8'))], config['judge_max_tokens'])
        payload['response_format'] = {'type': 'json_object'}
        calls.append(dict(slot=f'j.{case["id"]}.c{index:02}.{judge["name"]}',
            phase='judge', case=case['id'], judge=judge['name'], chunk=index,
            api='chat', model=judge['model'], mode=judge['mode'], endpoint=judge['endpoint'],
            judge_state=state, payload=payload))
    return calls, []


def derived_write(path, obj):
    """Atomic replace only for explicitly derived reports/status, never raw/cache."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = obj if isinstance(obj, bytes) else encoded(obj)
    fd, temp = tempfile.mkstemp(prefix='.derived-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        fsync_dir(path.parent)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run(root, key='', execute_paid=False, offline=False, transport=None, pilot=False,
        max_new_calls=None):
    from eval_store import Store, TERMINAL, real_transport
    root = Path(root)
    config = load_frozen(root)
    mode = 'OFFLINE_FAKE' if offline else 'LIVE_API'
    if max_new_calls is not None and (type(max_new_calls) is not int or max_new_calls < 0):
        raise ValueError('max-new-calls must be nonnegative; never a monetary cap')
    with locked(root):
        marker = root / 'execution-mode.json'
        if marker.exists() and read_json(marker)['mode'] != mode:
            raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
        if offline:
            if key or execute_paid or not getattr(transport, 'offline_only', False):
                raise ValueError('offline execution requires explicit fake and no API key')
        else:
            if not execute_paid or transport is not None:
                raise ValueError('live calls require --execute-paid; injected transports are offline only')
            if any((parent / '.git').exists() for parent in [root.resolve(), *root.resolve().parents]):
                raise ValueError('live raw store must be private and outside any Git repository')
            manifest = read_json(root / 'manifest.json')
            if not manifest['probes_complete'] or not manifest['probes_accounting_reconciled']:
                raise ValueError('complete accepted route/mode probes and reconciled separate accounting required before paid calls')
            transport = real_transport(key)
        if not marker.exists():
            immutable(marker, dict(mode=mode, synthetic=offline))
        store = Store(root, mode)
        records = store.audit()
        generation = list(generation_calls(root, config))
        expected_gen = {call['slot']: call for call in generation}
        for slot, (call, _) in records.items():
            if call['phase'] == 'generation' and (slot not in expected_gen or call != expected_gen[slot]):
                raise ValueError('stored generation outside frozen matrix')
        stop = next((r['status'] for _, r in records.values() if r['status'] not in TERMINAL), None)
        new_calls, skipped = 0, []
        blinds = {b['case']: b for b in read_json(root / 'frozen/blind-plan.json')}
        expected_judges = {}
        for case in config['cases']:
            for index in range(len(blinds[case['id']]['groups'])):
                calls, _ = judge_calls(config, case, blinds[case['id']], index, records)
                expected_judges.update({c['slot']: c for c in calls})
        for slot, (call, _) in records.items():
            if call['phase'] == 'judge' and (slot not in expected_judges or call != expected_judges[slot]):
                raise ValueError('stored judge outside frozen anonymous matrix')

        def submit(call):
            nonlocal new_calls, stop
            is_new = call['slot'] not in records
            if is_new and max_new_calls is not None and new_calls >= max_new_calls:
                stop = 'requested_call_boundary'
                return
            record = store.submit(call, transport)
            records[call['slot']] = (call, record)
            new_calls += int(is_new)
            if record['status'] not in TERMINAL:
                stop = record['status']

        for case in (config['cases'][:1] if pilot else config['cases']):
            if stop:
                break
            calls = [c for c in generation if c['case'] == case['id']]
            for call in (calls[:2] if pilot else calls):
                submit(call)
                if stop:
                    break
            if stop:
                break
            blind = blinds[case['id']]
            for index in range(1 if pilot else len(blind['groups'])):
                calls, missing = judge_calls(config, case, blind, index, records)
                if missing:
                    skipped.append(dict(case=case['id'], chunk=index, slots=missing,
                        reason='frozen_chunk_not_regrouped; missing/invalid candidate'))
                    continue
                plan_path = root / 'judge-inputs' / f'{case["id"]}.c{index:02}.json'
                plan = dict(calls=calls, raw_sha256={slot: records[slot][1]['raw_sha256']
                    for slot in {blind['mapping'][tid] for c in calls for tid in c['judge_state']['textos']}})
                if plan_path.exists():
                    if read_json(plan_path) != plan:
                        raise ValueError('frozen judge input changed')
                else:
                    immutable(plan_path, plan)
                for call in calls:
                    submit(call)
                    if stop:
                        break
                if stop:
                    break
        results = [record for _, record in records.values()]
        summary = dict(execution_mode=mode, scope='pilot' if pilot else 'full',
            submitted_generations=sum(c['phase'] == 'generation' for c, _ in records.values()),
            submitted_judge_calls=sum(c['phase'] == 'judge' for c, _ in records.values()),
            completed=sum(r['status'] == 'completed' for r in results),
            invalid=sum(r['status'] == 'invalid_response' for r in results), new_calls=new_calls,
            expected=read_json(root / 'manifest.json')['expected'], stop_reason=stop,
            skipped_chunks=skipped, monetary_ceiling=None, automatic_retry=False,
            human_evaluation='pending', model_writing_evidence=not offline)
        derived_write(root / 'runtime-summary.json', summary)
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    prep = subs.add_parser('prepare', help='offline snapshots for review, no API')
    prep.add_argument('--output', type=Path, required=True)
    prep.add_argument('--skill', type=Path, default=HERE.parents[1])
    prep.add_argument('--history', type=Path, required=True)
    prep.add_argument('--catalog', type=Path, required=True)
    prep.add_argument('--endpoints', type=Path, required=True)
    prep.add_argument('--probe-evidence', action='append', type=Path, default=[])
    prep.add_argument('--amendments', type=Path)
    prep.add_argument('--probe-dir', type=Path)
    prep.add_argument('--probes-accounting', type=Path)
    execute = subs.add_parser('run', help='explicit paid generation/judging; no automatic retry')
    execute.add_argument('--root', type=Path, required=True)
    execute.add_argument('--execute-paid', action='store_true')
    execute.add_argument('--key-env', default='OPENROUTER_API_KEY')
    execute.add_argument('--pilot', action='store_true')
    execute.add_argument('--max-new-calls', type=int)
    report = subs.add_parser('render', help='read-only raw audit and regenerated Markdown reports')
    report.add_argument('--root', type=Path, required=True)
    report.add_argument('--reports', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == 'prepare':
        result = prepare(args.output, args.skill, args.history, args.catalog, args.endpoints,
                         args.probe_evidence, args.amendments, args.probe_dir, args.probes_accounting)
        print(json.dumps({k: v for k, v in result.items() if k != 'sha256'}, ensure_ascii=False))
    elif args.command == 'run':
        result = run(args.root, key=os.environ.get(args.key_env, ''),
                     execute_paid=args.execute_paid, pilot=args.pilot, max_new_calls=args.max_new_calls)
        print(json.dumps(result, ensure_ascii=False))
        return 2 if result['stop_reason'] else 0
    elif args.command == 'render':
        from eval_render import render
        print(json.dumps(render(args.root, args.reports), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
