"""Read-only delivery check of stored generations. Descriptive; never excludes or retries.

Integrity is verified against the run's own manifest and frozen inputs, and every
result is re-derived in memory from intent/raw. Nothing in the source is written or
rebuilt, so historical evidence can be read with the compatible v1 contract.
"""
from collections import Counter
import importlib.util
from pathlib import Path
import sys
import generation_eval as g
from eval_store import derive

DEFAULT_CHECKER = g.HERE.parents[1] / 'scripts/humanizar.py'
REQUEST_FILES = {'intent.json', 'raw.json', 'result.json', 'transport-error.json'}


def load_checker(path):
    spec = importlib.util.spec_from_file_location('humanizar_checker', path)
    module = importlib.util.module_from_spec(spec)
    previous, sys.dont_write_bytecode = sys.dont_write_bytecode, True  # No __pycache__ beside a frozen checker.
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    if not hasattr(module, 'check'):
        raise ValueError('checker must provide check(); use humanizar.py 0.6.0 or later')
    return module


def safe_destination(root, output):
    """Reject outputs inside the evidence root, including through symlinks."""
    root, output = Path(root).resolve(), Path(output)
    if output.is_symlink():
        raise ValueError('delivery output must not be a symlink')
    target = output.parent.resolve() / output.name
    if target == root or root in target.parents:
        raise ValueError('delivery output must be outside the evidence root')
    return target


def verify_records(root):
    """Check manifest, config, payload plan, blind map and intent/raw/result; raise on drift."""
    root = Path(root)
    manifest = g.read_json(root / 'manifest.json')
    hashes = manifest['sha256']
    required = {'frozen/config.json', 'frozen/generation-plan.json', 'frozen/blind-plan.json',
                'frozen/skill/results/PROMPTS.md'}
    if not required <= set(hashes):
        raise ValueError('manifest must cover config, payload plan, blind map and prompts')
    for name, expected in hashes.items():
        path = root / name
        if not path.is_file() or g.digest(path.read_bytes()) != expected:
            raise ValueError('frozen hash mismatch: ' + name)
    config = g.read_json(root / 'frozen/config.json')
    prompts = g.parse_prompts((root / 'frozen/skill/results/PROMPTS.md').read_text('utf-8'))
    if [c['prompt'] for c in prompts] != [c['prompt'] for c in config['cases']]:
        raise ValueError('literal prompt/config mismatch')
    calls = {c['slot']: c for c in g.generation_calls(root, config)}
    plan = [dict(slot=slot, payload_sha256=g.digest(call['payload'])) for slot, call in calls.items()]
    if plan != g.read_json(root / 'frozen/generation-plan.json'):
        raise ValueError('payload hash mismatch')
    blinds = g.read_json(root / 'frozen/blind-plan.json')
    if blinds != [g.blind_case(config, case) for case in config['cases']]:
        raise ValueError('blind map mismatch')
    if {slot for blind in blinds for slot in blind['mapping'].values()} != set(calls):
        raise ValueError('blind map does not cover the generation matrix')
    mode = g.read_json(root / 'execution-mode.json')['mode']
    records, cached = {}, {}
    for folder in sorted((root / 'requests').iterdir()):
        if not folder.is_dir() or folder.is_symlink():
            raise ValueError('unexpected entry in request store')
        if {p.name for p in folder.iterdir()} - REQUEST_FILES:
            raise ValueError('unexpected file in request ' + folder.name)
        intent = g.read_json(folder / 'intent.json')
        call = intent['call']
        if call['slot'] != folder.name or intent['call_sha256'] != g.digest(call):
            raise ValueError('intent mismatch: ' + folder.name)
        if intent['execution_mode'] != mode:
            raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
        if call['phase'] == 'generation' and calls.get(call['slot']) != call:
            raise ValueError('stored generation outside frozen matrix: ' + folder.name)
        if not (folder / 'raw.json').exists():
            if (folder / 'result.json').exists():
                raise ValueError('result without raw: ' + folder.name)
            records[call['slot']] = (call, dict(status='ambiguous_intent_without_raw'))
            continue
        raw = g.read_json(folder / 'raw.json')
        if raw['call_sha256'] != g.digest(call) or raw['intent_sha256'] != g.digest(intent):
            raise ValueError('raw/intent hash mismatch: ' + folder.name)
        result = derive(call, intent, raw)  # In memory only; the source cache is never written.
        cached[call['slot']] = (folder / 'result.json').exists()
        if cached[call['slot']] and g.read_json(folder / 'result.json') != result:
            raise ValueError('cached result differs from immutable raw: ' + folder.name)
        records[call['slot']] = (call, result)
    cases = {case['id']: case for case in config['cases']}
    blind_by_case = {blind['case']: blind for blind in blinds}
    for slot, (call, _) in records.items():
        if call['phase'] == 'judge':
            expected, _ = g.judge_calls(config, cases[call['case']], blind_by_case[call['case']],
                                        call['chunk'], records)
            if call not in expected:
                raise ValueError('stored judge outside frozen anonymous map: ' + slot)
    return config, records, cached


def delivery(root, output, checker=DEFAULT_CHECKER):
    """Classify completed generation texts with humanizar.check against the literal prompt."""
    root, checker = Path(root), Path(checker)
    target = safe_destination(root, output)
    h = load_checker(checker)
    catalog = checker.parents[1] / 'references/catalogo.json'
    rules = h.load_catalog(catalog)
    config, records, cached = verify_records(root)
    prompts = {case['id']: case['prompt'] for case in config['cases']}
    rows = []
    for slot, (call, result) in sorted(records.items()):
        if call['phase'] != 'generation':
            continue
        row = dict(slot=slot, case=call['case'], route=call['route'], arm=call['arm'],
                   status=result['status'], result_cache=cached.get(slot, False),
                   deliverable=None, blocking=[], review={})
        if result['status'] == 'completed':
            report = h.check(result['text'], rules, prompts[call['case']])
            row.update(deliverable=report['deliverable'],
                       blocking=sorted({b['code'] for b in report['blocking']}),
                       review=dict(sorted(Counter(r['code'] for r in report['review']).items())))
        rows.append(row)
    summary = {}
    for arm in g.ARMS:
        selected = [r for r in rows if r['arm'] == arm and r['status'] == 'completed']
        summary[arm] = dict(completed=len(selected),
                            deliverable=sum(r['deliverable'] for r in selected),
                            blocking=dict(sorted(Counter(c for r in selected for c in r['blocking']).items())))
    report = dict(kind='delivery_check_report', treatment_packaging=config.get('treatment_packaging', 'v1-full-json'),
                  artifact='prosa', integrity='manifest, config, payload plan, blind map, intent/raw/result verified',
                  checker_sha256=g.digest(checker.read_bytes()), catalog_sha256=g.digest(catalog.read_bytes()),
                  summary=summary, rows=rows,
                  note='Descriptive mechanical check of stored texts. Blocked outputs stay in every metric; '
                       'nothing is excluded, repaired or resubmitted. Not proof of fidelity or quality.')
    g.immutable(target, report)
    return report
