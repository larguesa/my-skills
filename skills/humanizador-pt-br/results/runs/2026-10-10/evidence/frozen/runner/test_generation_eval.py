"""OFFLINE only: explicit fake transport fixtures, never API evidence."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SKILL = HERE.parents[1]
FIXTURES = HERE / 'fixtures'
HISTORY = Path(os.environ.get('HUMANIZADOR_HISTORY', FIXTURES / 'history.json'))
CATALOG = Path(os.environ.get('HUMANIZADOR_CATALOG', FIXTURES / 'catalog.json'))
ENDPOINTS = Path(os.environ.get('HUMANIZADOR_ENDPOINTS', FIXTURES / 'endpoints.json'))
AMENDMENTS = Path(os.environ.get('HUMANIZADOR_AMENDMENTS', FIXTURES / 'amendments.json'))
PROBES = Path(os.environ.get('HUMANIZADOR_PROBES', FIXTURES / 'probes'))


def runner():
    assert (HERE / 'generation_eval.py').exists(), 'prepare/run/render runner not implemented'
    import generation_eval
    return generation_eval


class PreparationTests(unittest.TestCase):
    def test_real_inputs_frozen_independent_generation_contract(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            manifest = g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            self.assertEqual(manifest['expected']['generations'], 912)
            self.assertEqual(manifest['expected']['pair_judgments'], 1368)
            self.assertEqual(manifest['expected']['judge_calls'], 432)
            self.assertIsNone(manifest['monetary_ceiling'])
            config = g.load_frozen(root)
            calls = list(g.generation_calls(root, config))
            self.assertEqual(len({c['slot'] for c in calls}), 912)
            cases = g.parse_prompts((SKILL / 'results/PROMPTS.md').read_text())
            self.assertEqual(len(cases), 24)
            for base, treat in zip(calls[::2], calls[1::2]):
                prompt = next(c['prompt'] for c in cases if c['ordinal'] == base['ordinal'])
                self.assertEqual(base['payload']['messages'], [{'role': 'user', 'content': prompt}])
                self.assertEqual(treat['payload']['messages'][-1], base['payload']['messages'][0])
                self.assertEqual(len(treat['payload']['messages']), 5)
                for message, path in zip(treat['payload']['messages'][:3],
                    ['SKILL.md', 'references/catalogo.json', 'references/estilos.json']):
                    self.assertEqual(message, {'role': 'system', 'content': (SKILL / path).read_text()})
                local = json.loads(treat['payload']['messages'][3]['content'])
                self.assertTrue(local['catalog']['result'])
                self.assertTrue(local['styles']['result'])
                self.assertTrue(local['structure']['result']['blocks'])
                self.assertEqual(base['payload']['reasoning'], treat['payload']['reasoning'])
                self.assertFalse(base['payload']['provider']['allow_fallbacks'])
            self.assertEqual([c['prompt'] for c in config['cases']], [c['prompt'] for c in cases])
            self.assertEqual(config['routes'], json.loads(HISTORY.read_text())['routes'])
            with self.assertRaises(FileExistsError):
                g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            (root / 'frozen/skill/SKILL.md').chmod(0o600)
            (root / 'frozen/skill/SKILL.md').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash'):
                g.load_frozen(root)
    def test_explicit_amendments_preserve_originals_and_do_not_import_probes_as_candidates(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            amendments = AMENDMENTS
            manifest = g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS,
                amendments=amendments, probe_dir=PROBES)
            config = g.load_frozen(root)
            self.assertEqual(config['historical_routes'], json.loads(HISTORY.read_text())['routes'])
            for original, effective in zip(config['historical_routes'], config['routes']):
                self.assertEqual(original['model'], effective['model'])
                self.assertEqual(original['mode'], effective['mode'])
                self.assertEqual(original['reasoning'], effective['reasoning'])
                declared = next((a for a in json.loads(amendments.read_text())['amendments']
                                 if a['model'] == original['model']), None)
                if declared:
                    self.assertEqual(effective['endpoint']['tag'], declared['effective_provider'])
                else:
                    self.assertEqual(original, effective)
            self.assertEqual(manifest['distinct_models'], 14)
            self.assertFalse((root / 'requests').exists())
            self.assertTrue(list((root / 'frozen/probe-evidence').glob('*.json')))


class FakeOfflineTransport:
    """Synthetic test data. Explicitly OFFLINE; no network, no API credentials."""
    offline_only = True

    def __init__(self, root):
        self.root = Path(root)
        self.calls = []

    def __call__(self, call):
        g = runner()
        intent = self.root / 'requests' / call['slot'] / 'intent.json'
        assert intent.exists(), 'intent must be durable before transport'
        assert g.read_json(intent)['call'] == call
        self.calls.append(call)
        data = {'id': 'OFFLINE-FAKE-' + call['slot'], 'model': call['model'],
                'provider': call['endpoint']['provider_name'],
                'usage': {'prompt_tokens': 10, 'completion_tokens': 20,
                          'cost': 0.000001, 'prompt_tokens_details': {'cached_tokens': 2,
                          'cache_write_tokens': 0}, 'completion_tokens_details': {'reasoning_tokens': 5}}}
        if call['api'] == 'decisions':
            data['usage'] = {'input_tokens': 10, 'output_tokens': 20, 'cost': 0.000001}
            data['answers'] = {}
            for key, question in call['payload']['questions'].items():
                kind = question['type']
                value = {'type': kind}
                value.update({'noul': 0.5} if kind == 'noul' else {'score': 3} if kind == 'score'
                             else {'choice': 'no' if key.endswith('_critico') else 'empate'})
                data['answers'][key] = value
        else:
            text = 'OFFLINE FAKE: texto de teste, nunca evidência de geração.\u2028Continuação.'
            if call['phase'] == 'judge':
                state = call['judge_state']
                text = json.dumps({'deteccao': {tid: 50 for tid in state['textos']},
                    'preferencia': {pid: 'empate' for pid in state['pares']},
                    'qualidade': {tid: {'naturalidade': 75, 'clareza': 75, 'adequacao': 75,
                        'correcao': 75, 'critico': False, 'justificativa': 'OFFLINE FAKE'}
                        for tid in state['textos']}}, ensure_ascii=False)
            data['choices'] = [{'finish_reason': 'stop', 'message': {'content': text}}]
        return {'http_status': 200, 'body': json.dumps(data, ensure_ascii=False).encode()}


class RuntimeTests(unittest.TestCase):
    def test_full_offline_matrix_unique_coverage_no_replay_and_aggregate(self):
        g = runner()
        from eval_render import render
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            result = g.run(root, offline=True, transport=fake)
            self.assertIsNone(result['stop_reason'])
            self.assertEqual(result['submitted_generations'], 912)
            self.assertEqual(result['submitted_judge_calls'], 432)
            self.assertEqual(len({c['slot'] for c in fake.calls}), 1344)
            self.assertTrue(all(len(c['judge_state']['pares']) <= 4 for c in fake.calls if c['phase'] == 'judge'))
            summary = render(root, Path(tmp) / 'reports')
            self.assertEqual(summary['pair_judgments'], 1368)
            self.assertEqual(summary['individual_impression_scores'], 2736)
            self.assertEqual(summary['preferences'], {'empate': 1368})
            again = g.run(root, offline=True, transport=fake)
            self.assertEqual(again['new_calls'], 0)
            self.assertEqual(len(fake.calls), 1344)
            path = root / 'requests' / fake.calls[0]['slot'] / 'raw.json'
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                g.immutable(path, {'forged': 'OFFLINE negative test'})
            self.assertEqual(before, path.read_bytes())
            result_path = path.with_name('result.json')
            data = g.read_json(result_path)
            data['text'] = 'tampered OFFLINE fixture'
            result_path.chmod(0o600)
            result_path.write_bytes(g.encoded(data))
            with self.assertRaisesRegex(ValueError, 'cached result'):
                g.run(root, offline=True, transport=fake)

    def test_transport_ambiguity_blocks_all_new_slots_and_never_replays(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)

            class AmbiguousOffline:
                offline_only = True
                calls = 0
                def __call__(self, call):
                    self.calls += 1
                    self_intent = root / 'requests' / call['slot'] / 'intent.json'
                    assert self_intent.exists()
                    raise TimeoutError('explicit offline fixture: unknown submission')
            transport = AmbiguousOffline()
            result = g.run(root, offline=True, transport=transport, pilot=True)
            self.assertEqual(result['stop_reason'], 'ambiguous_intent_without_raw')
            self.assertEqual(transport.calls, 1)
            g.run(root, offline=True, transport=fake)
            self.assertEqual(fake.calls, [])
            with g.locked(root):
                with self.assertRaisesRegex(RuntimeError, 'lock'):
                    g.run(root, offline=True, transport=fake)

    def test_render_offline_pilot_preserves_text_and_reports_pending_denominators(self):
        g = runner()
        self.assertTrue((HERE / 'eval_render.py').exists(), 'render not implemented')
        from eval_render import render
        with tempfile.TemporaryDirectory() as tmp:
            root, reports = Path(tmp) / 'study', Path(tmp) / 'reports'
            g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            g.run(root, offline=True, transport=fake, pilot=True)
            summary = render(root, reports)
            self.assertEqual(summary['valid_generations'], 2)
            self.assertEqual(summary['pair_judgments'], 3)
            self.assertEqual(summary['individual_impression_scores'], 6)
            self.assertEqual(len(list((reports / 'experiments').glob('*/REPORT.md'))), 24)
            self.assertIn('OFFLINE_FAKE', (reports / 'SUMMARY.md').read_text())
            report = reports / 'experiments' / fake.calls[0]['case'] / 'REPORT.md'
            text = report.read_text()
            self.assertIn('| Jev | Astra | Opus |', text)
            self.assertIn('PENDENTE', text)
            prompt = g.load_frozen(root)['cases'][0]['prompt']
            self.assertIn('\n' + prompt + '\n', text)
            result = g.read_json(root / 'requests' / fake.calls[0]['slot'] / 'result.json')
            output = report.parent / 'outputs/r00-baseline.txt'
            self.assertEqual(output.read_bytes(), result['text'].encode())
            self.assertIsNone(summary['accounting']['probes']['total_usd'])
            self.assertEqual(summary['accounting']['generation']['costs_known'], 2)

    def test_offline_pilot_intent_raw_cache_and_three_blind_judges(self):
        g = runner()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'study'
            g.prepare(root, SKILL, HISTORY, CATALOG, ENDPOINTS)
            fake = FakeOfflineTransport(root)
            result = g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(result['execution_mode'], 'OFFLINE_FAKE')
            self.assertEqual(len(fake.calls), 5)
            self.assertEqual([c['phase'] for c in fake.calls], ['generation'] * 2 + ['judge'] * 3)
            self.assertEqual({c['judge'] for c in fake.calls[2:]}, {'jev', 'astra', 'opus'})
            for call in fake.calls[2:]:
                self.assertEqual(len(call['judge_state']['pares']), 1)
                self.assertNotIn('mapping', call['judge_state'])
            before = {p: p.read_bytes() for p in (root / 'requests').rglob('*') if p.is_file()}
            again = g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(len(fake.calls), 5)
            self.assertEqual(result['completed'], again['completed'])
            self.assertEqual(before, {p: p.read_bytes() for p in before})
            with self.assertRaisesRegex(ValueError, 'OFFLINE|offline'):
                g.run(root, key='not-a-real-key', execute_paid=True)
            first = root / 'requests' / fake.calls[0]['slot']
            (first / 'result.json').chmod(0o600)
            (first / 'result.json').unlink()
            g.run(root, offline=True, transport=fake, pilot=True)
            self.assertEqual(len(fake.calls), 5, 'raw-only recovery must never POST again')
            self.assertEqual(before[first / 'result.json'], (first / 'result.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
