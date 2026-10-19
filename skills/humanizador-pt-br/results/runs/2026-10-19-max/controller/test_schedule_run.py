"""Testes OFFLINE_FAKE. Snapshot 19/10 somente leitura, saídas em tempfile."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import os
HERE = Path(__file__).resolve().parent
RELATIVE_FIXTURE = HERE.parent.parent / '2026-10-19/evidence'
SOURCE = Path(os.environ.get('HUMANIZADOR_SCHEDULE_FIXTURE', str(RELATIVE_FIXTURE if RELATIVE_FIXTURE.is_dir() else Path('/home/hermes/projects/my-skills-humanizador/skills/humanizador-pt-br/results/runs/2026-10-19/evidence'))))


def controller():
    path = HERE / 'schedule_run.py'
    assert path.exists(), 'controlador standalone ainda não implementado'
    spec = importlib.util.spec_from_file_location('schedule_run', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path):
    return json.loads(path.read_bytes())


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class FakeOfflineTransport:
    """Fake explícito só nos testes; respostas sintéticas nunca são evidência LIVE."""
    offline_only = True

    def __init__(self, execution):
        self.execution, self.calls = execution, []

    def __call__(self, call):
        assert (self.execution / 'SCHEDULE.json').is_file()
        assert read(self.execution / 'execution-mode.json')['mode'] == 'OFFLINE_FAKE'
        assert read(self.execution / 'requests' / call['slot'] / 'intent.json')['call'] == call
        self.calls.append(call)
        data = dict(id='OFFLINE-FAKE-' + call['slot'], model=call['model'],
                    provider=call['endpoint']['provider_name'],
                    usage=dict(prompt_tokens=10, completion_tokens=20, cost=0.000001))
        if call['api'] == 'decisions':
            data['usage'] = dict(input_tokens=10, output_tokens=20, cost=0.000001)
            data['answers'] = {}
            for key, question in call['payload']['questions'].items():
                kind = question['type']
                value = {'type': kind}
                value.update({'noul': 0.5} if kind == 'noul' else {'score': 3} if kind == 'score'
                             else {'choice': 'no' if key.endswith('_critico') else 'empate'})
                data['answers'][key] = value
        else:
            text = 'OFFLINE FAKE: nunca evidência de modelo.\u2028Texto preservado.'
            if call['phase'] == 'judge':
                state = call['judge_state']
                text = json.dumps(dict(deteccao={t: 50 for t in state['textos']},
                    preferencia={p: 'empate' for p in state['pares']},
                    qualidade={t: dict(naturalidade=75, clareza=75, adequacao=75,
                        correcao=75, critico=False, justificativa='OFFLINE FAKE') for t in state['textos']}))
            data['choices'] = [dict(finish_reason='stop', message=dict(content=text))]
        return dict(http_status=200, body=json.dumps(data).encode())


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='humanizador-schedule-offline-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.execution = self.root / 'execution'
        shutil.copytree(SOURCE / 'frozen', self.execution / 'frozen')
        shutil.copy2(SOURCE / 'manifest.json', self.execution / 'manifest.json')
        self.before = hashes(self.execution / 'frozen')
        # Any accidental network or credential access is a test failure.
        self.network = patch('urllib.request.urlopen', side_effect=AssertionError('network forbidden'))
        self.network.start()
        self.addCleanup(self.network.stop)
        original = Path.read_bytes
        def guarded(path):
            if path.name == 'inference-key.json':
                raise AssertionError('credential read forbidden in offline tests')
            return original(path)
        self.guard = patch.object(Path, 'read_bytes', guarded)
        self.guard.start()
        self.addCleanup(self.guard.stop)

    def test_schedule_exact_coverage_hashes_order_and_blind_groups(self):
        s = controller()
        schedule = s.prepare_schedule(self.root)
        self.assertEqual(schedule, read(self.execution / 'SCHEDULE.json'))
        self.assertEqual(schedule['controller_sha256'], hashlib.sha256((HERE / 'schedule_run.py').read_bytes()).hexdigest())
        self.assertEqual(schedule['monetary_ceiling'], None)
        self.assertEqual(schedule['automatic_retry'], False)
        self.assertEqual(schedule['generation_count'], 912)
        self.assertEqual(schedule['judge_count'], 432)
        events = schedule['order']
        generation = [e for e in events if e['phase'] == 'generation']
        original = read(self.execution / 'frozen/generation-plan.json')
        self.assertEqual({e['slot']: e['payload_sha256'] for e in generation},
                         {e['slot']: e['payload_sha256'] for e in original})
        self.assertEqual(len({e['slot'] for e in events}), 1344)
        config = read(self.execution / 'frozen/config.json')
        for i, case in enumerate(config['cases']):
            chunk = events[i * 5:(i + 1) * 5]
            self.assertEqual([e['slot'] for e in chunk], [
                f'g.{case["id"]}.r00.baseline', f'g.{case["id"]}.r00.skill',
                f'j.{case["id"]}.c00.jev', f'j.{case["id"]}.c00.astra', f'j.{case["id"]}.c00.opus'])
        self.assertEqual([e['route'] for e in generation],
                         [r for r in [*range(15), 17, 18, 15, 16] for _ in range(48)])
        blinds = read(self.execution / 'frozen/blind-plan.json')
        self.assertEqual(schedule['blind_plan_sha256'], hashlib.sha256((self.execution / 'frozen/blind-plan.json').read_bytes()).hexdigest())
        seen, by_case = set(), {b['case']: b for b in blinds}
        for event in events:
            if event['phase'] == 'generation':
                seen.add(event['slot'])
            else:
                blind = by_case[event['case']]
                expected = [blind['mapping'][tid] for pid in blind['groups'][event['chunk']]
                            for tid in blind['pairs'][pid].values()]
                self.assertEqual(event['dependencies'], expected)
                self.assertTrue(set(expected) <= seen)
                # No generation is allowed between the final dependency and its judges.
                final_dep = max(i for i, e in enumerate(events) if e['slot'] in expected)
                idx = events.index(event)
                self.assertFalse(any(e['phase'] == 'generation' for e in events[final_dep + 1:idx]))
        self.assertEqual(self.before, hashes(self.execution / 'frozen'))
        self.assertFalse((self.execution / 'requests').exists())
        self.assertEqual(schedule, s.prepare_schedule(self.root))
    def run_fake(self, **options):
        s = controller()
        self.assertTrue(callable(getattr(s, 'run', None)), 'execução standalone não implementada')
        fake = options.pop('transport', FakeOfflineTransport(self.execution))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            summary = s.run(self.root, offline=True, transport=fake, **options)
        progress = [json.loads(line) for line in output.getvalue().split('\n') if line]
        return summary, fake, progress

    def test_pilot_then_resume_does_not_repeat_baseline_or_judges(self):
        summary, fake, progress = self.run_fake(pilot=True)
        self.assertEqual(len(fake.calls), 5)
        self.assertEqual(summary['new_calls'], 5)
        self.assertEqual(summary['scope'], 'pilot')
        self.assertIsNone(summary['stop_reason'])
        self.assertEqual(summary, read(self.execution / 'runtime-summary.json'))
        self.assertEqual(len(progress), 5)
        prior = hashes(self.execution / 'requests')
        again, fake2, _ = self.run_fake(pilot=True)
        self.assertEqual(again['new_calls'], 0)
        self.assertEqual(fake2.calls, [])
        self.assertEqual(prior, hashes(self.execution / 'requests'))
        resumed, fake3, progress3 = self.run_fake(max_new_calls=2)
        self.assertEqual(resumed['new_calls'], 2)
        self.assertEqual(resumed['stop_reason'], 'requested_call_boundary')
        self.assertEqual(len(progress3), 2)
        self.assertTrue(all('.r00.' in c['slot'] and c['case'] != fake.calls[0]['case'] for c in fake3.calls))
        self.assertFalse(set(c['slot'] for c in fake.calls) & set(c['slot'] for c in fake3.calls))
        self.assertEqual(self.before, hashes(self.execution / 'frozen'))
    def test_unexpected_request_artifact_blocks_resume(self):
        _, fake, _ = self.run_fake(pilot=True)
        directory = self.execution / 'requests' / fake.calls[0]['slot']
        (directory / 'unknown.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'unexpected request artifact'):
            self.run_fake(max_new_calls=1)
    def test_cli_without_paid_only_freezes_and_missing_execution_is_safe(self):
        s = controller()
        self.assertTrue(callable(getattr(s, 'main', None)), 'CLI explícita não implementada')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = s.main(['--root', str(self.root)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['event'], 'schedule_prepared')
        self.assertFalse((self.execution / 'requests').exists())
        self.assertFalse((self.execution / 'execution-mode.json').exists())
        missing = self.root / 'missing'
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = s.main(['--root', str(missing)])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())['event'], 'blocked')
        self.assertFalse(missing.exists())
    def test_full_offline_matrix_source_equality_renderer_and_resume(self):
        summary, fake, progress = self.run_fake()
        self.assertEqual((summary['submitted_generations'], summary['submitted_judge_calls']), (912, 432))
        self.assertEqual(summary['completed'], 1344)
        self.assertIsNone(summary['stop_reason'])
        self.assertEqual(len(progress), 1344)
        self.assertEqual([c['slot'] for c in fake.calls],
                         [e['slot'] for e in read(self.execution / 'SCHEDULE.json')['order']])
        allowed = {'event', 'execution_mode', 'slot', 'phase', 'status', 'new_calls',
                   'submitted_generations', 'submitted_judge_calls'}
        self.assertTrue(all(set(p) == allowed and p['execution_mode'] == 'OFFLINE_FAKE' for p in progress))
        self.assertNotIn('OFFLINE FAKE: nunca', json.dumps(progress))
        s = controller()
        with s.frozen_runner(self.execution) as (g, storage, config, manifest, blinds):
            records = storage.Store(self.execution, 'OFFLINE_FAKE').audit()
            expected = {c['slot']: c for c in g.generation_calls(self.execution, config)}
            for case, blind in zip(config['cases'], blinds):
                for index in range(len(blind['groups'])):
                    calls, missing = g.judge_calls(config, case, blind, index, records)
                    self.assertEqual(missing, [])
                    expected.update({c['slot']: c for c in calls})
            self.assertEqual({c['slot']: g.digest(c) for c in fake.calls},
                             {slot: g.digest(c) for slot, c in expected.items()})
            spec = importlib.util.spec_from_file_location('offline_renderer', self.execution / 'frozen/runner/eval_render.py')
            renderer = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(renderer)
            rendered = renderer.render(self.execution, self.root / 'offline-reports')
            self.assertEqual(rendered['execution_mode'], 'OFFLINE_FAKE')
            self.assertEqual(rendered['pair_judgments'], 1368)
            self.assertEqual(rendered['valid_judge_calls'], 432)
        prior = hashes(self.execution / 'requests')
        resumed, fake2, _ = self.run_fake()
        self.assertEqual(resumed['new_calls'], 0)
        self.assertEqual(fake2.calls, [])
        self.assertEqual(prior, hashes(self.execution / 'requests'))
        self.assertEqual(self.before, hashes(self.execution / 'frozen'))

    def exercise_failure(self, fault, expected, fail_on=1):
        base = FakeOfflineTransport(self.execution)
        class Fault:
            offline_only = True
            def __call__(self, call):
                response = base(call)
                if len(base.calls) != fail_on:
                    return response
                if fault == 'exception':
                    raise TimeoutError('secret-sentinel-never-print')
                if fault == 'http':
                    return dict(http_status=429, body=b'{"error":"secret-sentinel-never-print"}')
                data = json.loads(response['body'])
                data['provider'] = 'wrong route'
                return dict(http_status=200, body=json.dumps(data).encode())
        result, _, progress = self.run_fake(transport=Fault())
        self.assertEqual(result['stop_reason'], expected)
        self.assertEqual(result['new_calls'], fail_on)
        self.assertEqual(len(base.calls), fail_on)
        self.assertNotIn('secret-sentinel', json.dumps(progress))
        before = hashes(self.execution / 'requests')
        resumed, fake, progress = self.run_fake(pilot=True)
        self.assertEqual(resumed['stop_reason'], expected)
        self.assertEqual(resumed['new_calls'], 0)
        self.assertEqual(fake.calls, [])
        self.assertEqual(progress, [])
        self.assertEqual(before, hashes(self.execution / 'requests'))

    def test_transport_error_and_incomplete_intent_never_replayed(self):
        self.exercise_failure('exception', 'ambiguous_intent_without_raw')

    def test_http_rejection_stops_including_resume(self):
        self.exercise_failure('http', 'billing_uncertain')

    def test_route_mismatch_stops_including_resume(self):
        self.exercise_failure('route', 'route_mismatch')

    def test_judge_ambiguity_stops_without_replaying_generations(self):
        self.exercise_failure('exception', 'ambiguous_intent_without_raw', fail_on=3)

    def test_nonterminal_outside_pilot_blocks_even_pilot_resume(self):
        self.exercise_failure('exception', 'ambiguous_intent_without_raw', fail_on=6)

    def test_raw_without_result_is_recovered_without_call(self):
        _, fake, _ = self.run_fake(pilot=True)
        path = self.execution / 'requests' / fake.calls[0]['slot'] / 'result.json'
        previous = path.read_bytes()
        path.unlink()
        result, fake, _ = self.run_fake(pilot=True)
        self.assertEqual(result['new_calls'], 0)
        self.assertEqual(fake.calls, [])
        self.assertEqual(path.read_bytes(), previous)

    def test_terminal_invalid_is_preserved_never_regrouped_or_replayed(self):
        base = FakeOfflineTransport(self.execution)
        class Invalid:
            offline_only = True
            def __call__(self, call):
                response = base(call)
                if len(base.calls) == 2:
                    data = json.loads(response['body'])
                    data['choices'][0]['finish_reason'] = 'length'
                    response['body'] = json.dumps(data).encode()
                return response
        result, _, _ = self.run_fake(pilot=True, transport=Invalid())
        self.assertEqual(result['new_calls'], 2)
        self.assertEqual(result['invalid'], 1)
        self.assertIsNone(result['stop_reason'])
        self.assertEqual(len(result['skipped_chunks']), 1)
        resumed, fake, _ = self.run_fake(max_new_calls=5)
        self.assertEqual(resumed['invalid'], 1)
        self.assertEqual(len(result['skipped_chunks']), 1)
        self.assertTrue(all(c['case'] != base.calls[0]['case'] for c in fake.calls))
        self.assertEqual(self.before, hashes(self.execution / 'frozen'))

    def test_modes_permissions_and_boundaries_block_without_credentials(self):
        s = controller()
        fake = FakeOfflineTransport(self.execution)
        for options in [dict(), dict(transport=fake, execute_paid=True), dict(offline=True),
                        dict(offline=True, execute_paid=True, transport=fake),
                        dict(offline=True, transport=fake, max_new_calls=-1),
                        dict(offline=True, transport=fake, max_new_calls=True)]:
            with self.subTest(options=list(options)), self.assertRaises(ValueError):
                s.run(self.root, **options)
        result, fake, _ = self.run_fake(max_new_calls=0)
        self.assertEqual(result['new_calls'], 0)
        self.assertEqual(fake.calls, [])
        with self.assertRaisesRegex(ValueError, 'cannot be mixed'):
            s.run(self.root, execute_paid=True, max_new_calls=0)
        # A fresh zero-boundary LIVE marker is not a simulated live API result.
        marker = self.execution / 'execution-mode.json'
        marker.unlink()
        with contextlib.redirect_stdout(io.StringIO()):
            result = s.run(self.root, execute_paid=True, max_new_calls=0)
        self.assertEqual(result['new_calls'], 0)
        self.assertEqual(read(marker), dict(mode='LIVE_API', synthetic=False))
        with self.assertRaisesRegex(ValueError, 'cannot be mixed'):
            self.run_fake()

    def test_lock_held_before_first_transport_and_through_all_calls(self):
        s = controller()
        base = FakeOfflineTransport(self.execution)
        parent = self
        class LockedFake:
            offline_only = True
            def __call__(self, call):
                with parent.assertRaisesRegex(ValueError, 'lock held'):
                    s.prepare_schedule(parent.root)
                return base(call)
        self.run_fake(pilot=True, transport=LockedFake())
        self.assertEqual(len(base.calls), 5)
        s.prepare_schedule(self.root)  # Lock released at end.

    def test_changed_schedule_blocks_before_any_new_call(self):
        self.run_fake(pilot=True)
        path = self.execution / 'SCHEDULE.json'
        data = read(path)
        data['controller_sha256'] = '0' * 64
        path.chmod(0o600)
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'SCHEDULE mismatch'):
            self.run_fake()

    def test_source_audit_rejects_rehashed_generation_and_judge_payloads(self):
        self.run_fake(pilot=True)
        s = controller()
        # A self-consistent Store chain is insufficient: compare exact source payloads.
        with s.frozen_runner(self.execution) as (g, storage, config, manifest, blinds):
            original = storage.Store(self.execution, 'OFFLINE_FAKE').audit()
            for phase in ('generation', 'judge'):
                records = dict(original)
                slot = next(slot for slot, (call, _) in records.items() if call['phase'] == phase)
                call, result = records[slot]
                changed = json.loads(json.dumps(call))
                changed['payload']['model'] = 'changed-model'
                records[slot] = (changed, result)
                with self.subTest(phase=phase), self.assertRaisesRegex(ValueError, 'frozen source matrix'):
                    s.audit_records(self.execution, g, config, blinds, records)

    def test_frozen_input_hashes_and_incomplete_probes_are_required(self):
        s = controller()
        manifest_path = self.execution / 'manifest.json'
        manifest = read(manifest_path)
        manifest_path.chmod(0o600)
        manifest_path.write_text(json.dumps(dict(manifest, probes_complete=False)))
        with self.assertRaisesRegex(ValueError, 'complete reconciled probes'):
            s.prepare_schedule(self.root)
        manifest_path.write_text(json.dumps(manifest))
        path = self.execution / 'frozen/config.json'
        path.chmod(0o600)
        path.write_bytes(path.read_bytes() + b' ')
        with self.assertRaisesRegex(ValueError, 'frozen hash mismatch'):
            s.prepare_schedule(self.root)

    def test_blind_groups_cannot_be_redefined_even_with_new_manifest_hash(self):
        s = controller()
        path = self.execution / 'frozen/blind-plan.json'
        blinds = read(path)
        blinds[0]['groups'][1].reverse()
        path.chmod(0o600)
        path.write_text(json.dumps(blinds))
        manifest_path = self.execution / 'manifest.json'
        manifest = read(manifest_path)
        manifest['sha256']['frozen/blind-plan.json'] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.chmod(0o600)
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'blind map differs'):
            s.prepare_schedule(self.root)
    def test_original_runner_pilot_baseline_is_reused_without_rerun(self):
        s = controller()
        s.prepare_schedule(self.root)
        base = FakeOfflineTransport(self.execution)
        with s.frozen_runner(self.execution) as (g, storage, config, manifest, blinds):
            original = g.run(self.execution, offline=True, transport=base, pilot=True, max_new_calls=1)
        self.assertEqual(original['new_calls'], 1)
        self.assertEqual(base.calls[0]['arm'], 'baseline')
        baseline_path = self.execution / 'requests' / base.calls[0]['slot']
        before = hashes(baseline_path)
        result, fake, _ = self.run_fake(pilot=True)
        self.assertEqual(result['new_calls'], 4)
        self.assertNotIn(base.calls[0]['slot'], [c['slot'] for c in fake.calls])
        self.assertEqual(before, hashes(baseline_path))

    def test_bare_intent_without_raw_stops_before_transport(self):
        s = controller()
        with s.frozen_runner(self.execution) as (g, storage, config, manifest, blinds):
            call = next(g.generation_calls(self.execution, config))
            g.immutable(self.execution / 'requests' / call['slot'] / 'intent.json',
                        dict(schema=1, call=call, call_sha256=g.digest(call),
                             execution_mode='OFFLINE_FAKE', started_at=g.now()))
        result, fake, progress = self.run_fake()
        self.assertEqual(result['stop_reason'], 'ambiguous_intent_without_raw')
        self.assertEqual(result['new_calls'], 0)
        self.assertEqual(fake.calls, [])
        self.assertEqual(progress, [])

    def test_rehashed_judge_tamper_is_rejected_by_execution_audit(self):
        _, fake, _ = self.run_fake(pilot=True)
        slot = next(c['slot'] for c in fake.calls if c.get('judge') == 'astra')
        directory = self.execution / 'requests' / slot
        s = controller()
        with s.frozen_runner(self.execution) as (g, storage, config, manifest, blinds):
            intent = read(directory / 'intent.json')
            call = intent['call']
            call['payload']['messages'][0]['content'] += ' Tampered rubric.'
            intent['call_sha256'] = g.digest(call)
            raw = read(directory / 'raw.json')
            raw.update(call_sha256=g.digest(call), intent_sha256=g.digest(intent))
            result = storage.derive(call, intent, raw)
            for name, value in [('intent', intent), ('raw', raw), ('result', result)]:
                path = directory / (name + '.json')
                path.chmod(0o600)
                path.write_bytes(g.encoded(value))
            self.assertEqual(storage.Store(self.execution, 'OFFLINE_FAKE').audit()[slot][1]['status'], 'completed')
        with self.assertRaisesRegex(ValueError, 'frozen source matrix'):
            self.run_fake()

    def test_complete_probe_flag_cannot_hide_missing_route_evidence(self):
        s = controller()
        manifest_path = self.execution / 'manifest.json'
        manifest = read(manifest_path)
        # Remove all native Jev probes, rehash inventory. Coverage still must be recomputed.
        for path in (self.execution / 'frozen/probe-evidence').glob('*.json'):
            if read(path).get('model') == 'typesafe/jev-1.13':
                del manifest['sha256'][path.relative_to(self.execution).as_posix()]
                path.unlink()
        manifest['raw_probes'] = len(list((self.execution / 'frozen/probe-evidence').glob('*.json')))
        manifest_path.chmod(0o600)
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'probe coverage/accounting mismatch'):
            s.prepare_schedule(self.root)


if __name__ == '__main__':
    unittest.main()
