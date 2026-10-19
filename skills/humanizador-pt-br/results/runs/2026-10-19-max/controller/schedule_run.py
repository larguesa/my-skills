#!/usr/bin/env python3
"""Ordem diversificada sobre o runner congelado, sem alterar protocolo ou freeze."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

# Código vigente e congelado em 19/10, validado antes de executar qualquer import.
RUNNER_HASHES = {
    'generation_eval': '0126708df64c853067e1114b82703049e3d88cff446f5a2fee175f054e86186f',
    'eval_store': 'f7b50c117f210ff14bca4602182f1a07e6d7033e4eb5d41a6ef4fb3d587f6bc1',
    'eval_judges': '5cd1a369d4ac74e7a110789d18853dee4e9e1673128c37f629da6aba27e2a5a6',
}
EXPECTED = dict(generations=912, pairs=456, judge_calls=432,
                pair_judgments=1368, individual_impression_scores=2736)
ROUTES = (*range(15), 17, 18, 15, 16)


def read(path):
    return json.loads(Path(path).read_bytes())


def sha(data):
    return hashlib.sha256(data).hexdigest()


@contextmanager
def execution_lock(root):
    execution = Path(root).resolve() / 'execution'
    if not execution.is_dir():
        raise ValueError('execution not prepared')
    with (execution / '.runner.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('runner lock held') from None
        try:
            yield execution
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


@contextmanager
def frozen_runner(execution):
    """Validate bytes before import; never write pycache into the immutable tree."""
    manifest = read(execution / 'manifest.json')
    inventory = manifest['sha256']
    actual = {p.relative_to(execution).as_posix()
              for p in (execution / 'frozen').rglob('*') if p.is_file()}
    if actual != set(inventory):
        raise ValueError('frozen manifest inventory mismatch')
    for name, expected in inventory.items():
        path = execution / name
        if not name.startswith('frozen/') or path.is_symlink() or not path.resolve().is_relative_to(execution / 'frozen'):
            raise ValueError('unsafe frozen manifest path')
        if sha(path.read_bytes()) != expected:
            raise ValueError('frozen hash mismatch')
    for name, expected in RUNNER_HASHES.items():
        if inventory.get(f'frozen/runner/{name}.py') != expected:
            raise ValueError('runner differs from approved 19/10 source')
    saved = {name: sys.modules.get(name) for name in RUNNER_HASHES}
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        for name in ('eval_judges', 'generation_eval', 'eval_store'):
            spec = importlib.util.spec_from_file_location(name, execution / 'frozen/runner' / (name + '.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
        g, store = sys.modules['generation_eval'], sys.modules['eval_store']
        config = g.load_frozen(execution)
        if (manifest.get('expected') != EXPECTED or len(config['cases']) != 24
                or len(config['routes']) != 19 or len({r['model'] for r in config['routes']}) != 14
                or config.get('monetary_ceiling', 'missing') is not None
                or manifest.get('monetary_ceiling', 'missing') is not None
                or config.get('automatic_retry') is not False):
            raise ValueError('matrix or uncapped/no-retry contract mismatch')
        if [(config['routes'][i]['model'], config['routes'][i]['mode']) for i in (15, 16)] != [
                ('qwen/qwen3.8-flash', 'off'), ('qwen/qwen3.8-flash', 'on')]:
            raise ValueError('r15/r16 must be the frozen Qwen Flash routes')
        if (manifest.get('probes_complete') is not True or
                manifest.get('probes_accounting_present') is not True or
                manifest.get('probes_accounting_reconciled') is not True):
            raise ValueError('complete reconciled probes required')
        probes = sorted((execution / 'frozen/probe-evidence').glob('*.json'))
        coverage = g.probe_coverage(config['routes'] + config['judges'] + [config['jev']], probes)
        declared = read(execution / 'frozen/probe-coverage.json')
        identity = lambda rows: [(r['model'], r['mode'], r['tag']) for r in rows]
        if (manifest.get('raw_probes') != len(probes) or identity(coverage) != identity(declared)
                or not all(r['accepted_evidence'] for r in coverage + declared)
                or read(execution / 'frozen/probes-accounting.json').get('ledger_reconciliation')
                in (None, False, 'pending', 'unknown')):
            raise ValueError('probe coverage/accounting mismatch')
        blinds = read(execution / 'frozen/blind-plan.json')
        if blinds != [g.blind_case(config, case) for case in config['cases']]:
            raise ValueError('blind map differs from frozen source')
        yield g, store, config, manifest, blinds
    finally:
        sys.dont_write_bytecode = bytecode
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def build_schedule(execution, g, config, manifest, blinds):
    calls = list(g.generation_calls(execution, config))
    by_slot = {c['slot']: c for c in calls}
    if len(calls) != 912 or len(by_slot) != 912:
        raise ValueError('generation coverage mismatch')
    by_case = {b['case']: b for b in blinds}
    groups = []
    for case in config['cases']:
        blind = by_case[case['id']]
        for index, group in enumerate(blind['groups']):
            deps = [blind['mapping'][tid] for pid in group for tid in blind['pairs'][pid].values()]
            groups.append((case['id'], index, deps))
    order, seen, ready = [], set(), set()
    for route in ROUTES:
        for case in config['cases']:
            for arm in g.ARMS:
                slot = f'g.{case["id"]}.r{route:02}.{arm}'
                call = by_slot[slot]
                order.append(dict(slot=slot, phase='generation', route=route, case=case['id'],
                                  payload_sha256=g.digest(call['payload']), call_sha256=g.digest(call)))
                seen.add(slot)
                for cid, index, deps in groups:
                    if (cid, index) in ready or not set(deps) <= seen:
                        continue
                    ready.add((cid, index))
                    for judge in ['jev', *[j['name'] for j in config['judges']]]:
                        order.append(dict(slot=f'j.{cid}.c{index:02}.{judge}', phase='judge',
                                          case=cid, chunk=index, judge=judge, dependencies=deps))
    if len(order) != 1344 or len({e['slot'] for e in order}) != 1344:
        raise ValueError('schedule coverage mismatch')
    return dict(schema=1, policy='r00-all-cases; route-case; r15-r16-last; judge-immediately',
                controller_sha256=sha(Path(__file__).read_bytes()),
                manifest_sha256=sha((execution / 'manifest.json').read_bytes()),
                blind_plan_sha256=sha((execution / 'frozen/blind-plan.json').read_bytes()),
                generation_plan_sha256=sha((execution / 'frozen/generation-plan.json').read_bytes()),
                runner_sha256=RUNNER_HASHES, generation_count=912, judge_count=432,
                monetary_ceiling=None, automatic_retry=False, order=order)


def freeze_schedule(execution, g, config, manifest, blinds):
    schedule = build_schedule(execution, g, config, manifest, blinds)
    path = execution / 'SCHEDULE.json'
    if path.exists():
        if read(path) != schedule:
            raise ValueError('SCHEDULE mismatch; controller/order/freeze must not change')
    else:
        g.immutable(path, schedule)
    return schedule


def prepare_schedule(root):
    with execution_lock(root) as execution, frozen_runner(execution) as loaded:
        g, _, config, manifest, blinds = loaded
        return freeze_schedule(execution, g, config, manifest, blinds)


def audit_records(execution, g, config, blinds, records):
    expected = {c['slot']: c for c in g.generation_calls(execution, config)}
    cases = {c['id']: c for c in config['cases']}
    plans = {}
    for blind in blinds:
        for index, group in enumerate(blind['groups']):
            calls, missing = g.judge_calls(config, cases[blind['case']], blind, index, records)
            if missing:
                continue
            expected.update({c['slot']: c for c in calls})
            deps = {blind['mapping'][tid] for pid in group for tid in blind['pairs'][pid].values()}
            plans[f'{blind["case"]}.c{index:02}.json'] = dict(calls=calls,
                raw_sha256={slot: records[slot][1]['raw_sha256'] for slot in deps})
    for slot, (call, _) in records.items():
        if slot not in expected or call != expected[slot]:
            raise ValueError('stored call outside frozen source matrix')
    directory = execution / 'judge-inputs'
    if directory.exists():
        for path in directory.iterdir():
            if path.name not in plans or read(path) != plans[path.name]:
                raise ValueError('frozen judge input changed')
    return plans


def run(root, *, execute_paid=False, offline=False, transport=None, pilot=False, max_new_calls=None):
    """Only an explicit fake may be injected; live credentials stay inside memory."""
    if max_new_calls is not None and (type(max_new_calls) is not int or max_new_calls < 0):
        raise ValueError('max-new-calls must be nonnegative; never a monetary ceiling')
    if offline:
        if execute_paid or not getattr(transport, 'offline_only', False):
            raise ValueError('explicit offline fake required, never --execute-paid')
    elif not execute_paid or transport is not None:
        raise ValueError('live execution requires --execute-paid and no injected transport')
    mode = 'OFFLINE_FAKE' if offline else 'LIVE_API'
    with execution_lock(root) as execution, frozen_runner(execution) as loaded:
        g, storage, config, manifest, blinds = loaded
        if not offline and any((p / '.git').exists() for p in [execution, *execution.parents]):
            raise ValueError('live raw store must be outside Git')
        marker = execution / 'execution-mode.json'
        expected_marker = dict(mode=mode, synthetic=offline)
        if marker.exists() and read(marker) != expected_marker:
            raise ValueError('OFFLINE_FAKE and LIVE_API cannot be mixed')
        schedule = freeze_schedule(execution, g, config, manifest, blinds)
        if not marker.exists():
            g.immutable(marker, expected_marker)
        store = storage.Store(execution, mode)
        for directory in store.requests.iterdir():
            if directory.is_symlink() or not directory.is_dir():
                raise ValueError('unexpected request artifact')
            for path in directory.iterdir():
                if (path.is_symlink() or not path.is_file() or path.name not in
                        {'intent.json', 'raw.json', 'result.json', 'transport-error.json'}):
                    raise ValueError('unexpected request artifact')
        records = store.audit()
        audit_records(execution, g, config, blinds, records)
        stop = next((r['status'] for _, r in records.values() if r['status'] not in storage.TERMINAL), None)
        generation = {c['slot']: c for c in g.generation_calls(execution, config)}
        cases = {c['id']: c for c in config['cases']}
        by_case = {b['case']: b for b in blinds}
        new_calls, skipped = 0, {}
        judge_cache = {}

        def summary():
            results = [r for _, r in records.values()]
            value = dict(execution_mode=mode, scope='pilot' if pilot else 'full',
                submitted_generations=sum(c['phase'] == 'generation' for c, _ in records.values()),
                submitted_judge_calls=sum(c['phase'] == 'judge' for c, _ in records.values()),
                completed=sum(r['status'] == 'completed' for r in results),
                invalid=sum(r['status'] == 'invalid_response' for r in results), new_calls=new_calls,
                expected=manifest['expected'], stop_reason=stop, skipped_chunks=list(skipped.values()),
                monetary_ceiling=None, automatic_retry=False, human_evaluation='pending',
                model_writing_evidence=not offline, schedule_sha256=g.digest(schedule))
            g.derived_write(execution / 'runtime-summary.json', value)
            return value

        summary()
        for event in schedule['order'][:5] if pilot else schedule['order']:
            if stop:
                break
            if event['slot'] in records:
                # Only audited TERMINAL records can be reused; never submit them again.
                continue
            if max_new_calls is not None and new_calls >= max_new_calls:
                stop = 'requested_call_boundary'
                break
            if event['phase'] == 'generation':
                call = generation[event['slot']]
            else:
                identity = (event['case'], event['chunk'])
                if identity not in judge_cache:
                    calls, missing = g.judge_calls(config, cases[event['case']], by_case[event['case']],
                                                   event['chunk'], records)
                    if missing:
                        skipped[identity] = dict(case=event['case'], chunk=event['chunk'], slots=missing,
                            reason='frozen_chunk_not_regrouped; missing/invalid candidate')
                        continue
                    plan = dict(calls=calls, raw_sha256={slot: records[slot][1]['raw_sha256']
                                                        for slot in set(event['dependencies'])})
                    path = execution / 'judge-inputs' / f'{event["case"]}.c{event["chunk"]:02}.json'
                    if path.exists():
                        if read(path) != plan:
                            raise ValueError('frozen judge input changed')
                    else:
                        g.immutable(path, plan)
                    judge_cache[identity] = {c['slot']: c for c in calls}
                call = judge_cache[identity][event['slot']]
            if transport is None:
                # This branch is reachable only after --execute-paid and all audits.
                credential = read(Path(root).resolve() / 'private/inference-key.json')
                transport = storage.real_transport(credential['key'])
                del credential
            record = store.submit(call, transport)
            records[call['slot']] = (call, record)
            new_calls += 1
            if record['status'] not in storage.TERMINAL:
                stop = record['status']
            value = summary()
            print(json.dumps(dict(event='call', execution_mode=mode, slot=call['slot'],
                phase=call['phase'], status=record['status'], new_calls=new_calls,
                submitted_generations=value['submitted_generations'],
                submitted_judge_calls=value['submitted_judge_calls']), sort_keys=True), flush=True)
        return summary()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent,
                        help='diretório que contém execution/ e private/')
    parser.add_argument('--execute-paid', action='store_true', help='autoriza chamadas LIVE_API')
    parser.add_argument('--pilot', action='store_true', help='mesmos cinco slots iniciais, sem rerun')
    parser.add_argument('--max-new-calls', type=int, help='fronteira de novas chamadas, nunca teto monetário')
    args = parser.parse_args(argv)
    try:
        if args.execute_paid:
            result = run(args.root, execute_paid=True, pilot=args.pilot, max_new_calls=args.max_new_calls)
            print(json.dumps(dict(event='runtime_summary', **result), sort_keys=True), flush=True)
            return 2 if result['stop_reason'] else 0
        if args.max_new_calls is not None and args.max_new_calls < 0:
            raise ValueError('invalid call boundary')
        schedule = prepare_schedule(args.root)
        print(json.dumps(dict(event='schedule_prepared', generation_count=schedule['generation_count'],
            judge_count=schedule['judge_count'], controller_sha256=schedule['controller_sha256'],
            paid_calls=0, monetary_ceiling=None), sort_keys=True), flush=True)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        # Exception values can contain HTTP bodies or credentials. Never print them.
        print(json.dumps(dict(event='blocked', error_type=type(error).__name__,
                              automatic_retry=False), sort_keys=True), flush=True)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
