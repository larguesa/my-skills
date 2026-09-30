"""Offline tests. Fixtures are synthetic; never call paid APIs."""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tests/scripts/benchmark.py'

def load():
    spec = importlib.util.spec_from_file_location('benchmark', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class BenchmarkTests(unittest.TestCase):
    def test_duplicate_case_and_model_ids_are_rejected(self):
        b = load()
        models = [{'id': 'test/model', 'status': 'missing'}]
        cases = [{'id': 'c', 'original': 'Texto'}]
        for ms, cs in [(models, cases * 2), (models * 2, cases)]:
            with self.subTest(models=len(ms), cases=len(cs)), self.assertRaisesRegex(ValueError, 'duplicate'):
                b.make_plan(ms, cs, 'Skill')

    def test_exact_catalog_missing_is_not_substituted(self):
        self.assertTrue(SCRIPT.exists(), 'benchmark.py missing')
        b = load()
        result = b.resolve_models(['vendor/exact', 'vendor/missing'], [{'id': 'vendor/exact'}, {'id': 'vendor/missing-new'}])
        self.assertEqual([x['status'] for x in result], ['available', 'missing'])
        self.assertEqual(result[1]['id'], 'vendor/missing')

    def test_reservation_fails_closed_and_reasoning_is_explicit(self):
        b = load()
        self.assertTrue(hasattr(b, 'reserve_cost'), 'cost guard missing')
        ep = {'pricing': {'prompt': '0.01', 'completion': '0.02'},
              'supported_parameters': ['reasoning', 'max_tokens']}
        self.assertEqual(b.reserve_cost(ep, 100, 20), b.Decimal('1.40'))
        self.assertEqual(b.reasoning_params(ep, 'on'), {'enabled': True, 'max_tokens': 1024})
        with self.assertRaises(ValueError): b.reasoning_params(ep, 'off')
        ep['reasoning_modes'] = ['on', 'off']
        self.assertEqual(b.reasoning_params(ep, 'off'), {'enabled': False})
        for pricing in ({}, {'prompt': '-1', 'completion': '0.1'},
                        {'prompt': 'NaN', 'completion': '0.1'},
                        {'prompt': '0.1', 'completion': '0.1', 'mystery': '1'}):
            with self.assertRaises(ValueError): b.reserve_cost({'pricing': pricing}, 100, 20)
        ep['pricing']['overrides'] = [{'prompt': '0.03', 'completion': '0.04'}]
        self.assertEqual(b.reserve_cost(ep, 100, 20), b.Decimal('3.80'))

    def test_plan_three_arms_skips_unsupported_no_paid_calls(self):
        b = load()
        self.assertTrue(hasattr(b, 'make_plan'), 'planner missing')
        ep = {'tag': 'test', 'context_length': 10000, 'max_completion_tokens': 1000,
              'pricing': {'prompt': '0.000001', 'completion': '0.000002'},
              'supported_parameters': ['reasoning', 'max_tokens']}
        models = [{'id': 'test/model', 'status': 'available', 'endpoints': [ep]},
                  {'id': 'test/missing', 'status': 'missing', 'endpoints': []}]
        cases = [{'id': 'c1', 'original': 'Texto sintético.', 'provenance': 'synthetic_authored'}]
        p = b.make_plan(models, cases, 'Skill textual.', max_tokens=100, audit=lambda t: {'flags': ['teste']})
        self.assertEqual(len(p['calls']), 3)
        self.assertEqual({c['arm'] for c in p['calls']}, {'simple', 'skill', 'skill_audit'})
        self.assertEqual(len(p['coverage']), 12)
        self.assertTrue(all(c['payload']['reasoning'] == {'enabled': True, 'max_tokens': 1024} for c in p['calls']))
        self.assertNotIn('Skill textual.', p['calls'][0]['payload']['messages'][0]['content'])
        self.assertIn('flags', p['calls'][2]['payload']['messages'][0]['content'])
        self.assertLess(b.money(p['reserved_total_usd']), b.Decimal('10'))
        with self.assertRaises(ValueError): b.make_plan(models, cases, 'x', budget='10.01')

    def test_duplicate_call_ids_rejected_before_send(self):
        import tempfile
        b = load()
        ep = {'tag': 'test', 'context_length': 50000, 'max_completion_tokens': 1000,
              'pricing': {'prompt': '0.000001', 'completion': '0.000002'},
              'supported_parameters': ['reasoning', 'max_tokens']}
        plan = b.make_plan([{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}],
                           [{'id': 'c', 'original': 'Texto'}], 'Skill', max_tokens=100, audit=lambda t: {})
        plan['calls'] *= 2
        plan['fingerprint'] = b.digest({k: v for k, v in plan.items() if k != 'fingerprint'})
        sent = []
        def send(payload, key):
            sent.append(payload)
            return {'model': payload['model'], 'choices': [{'message': {'content': 'Texto'}, 'finish_reason': 'stop'}],
                    'usage': {'cost': 0.001, 'prompt_tokens': 20, 'completion_tokens': 10}}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'duplicate call'):
                b.run_plan(plan, pathlib.Path(tmp)/'state.json', 'SECRET', send=send, endpoints=lambda m: [ep])
            self.assertEqual(sent, [])
            self.assertFalse((pathlib.Path(tmp)/'state.json').exists())

    def test_run_resumes_and_stops_on_unknown_billing(self):
        import tempfile
        b = load()
        self.assertTrue(hasattr(b, 'run_plan'), 'runner missing')
        ep = {'tag': 'test', 'context_length': 50000, 'max_completion_tokens': 1000,
              'pricing': {'prompt': '0.000001', 'completion': '0.000002'},
              'supported_parameters': ['reasoning', 'max_tokens']}
        p = b.make_plan([{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}],
                        [{'id': 'c', 'original': 'Original'}], 'Skill', max_tokens=100, audit=lambda t: {})
        calls = []
        def send(payload, key):
            calls.append(payload)
            return {'id': 'generation-1', 'model': payload['model'], 'provider': 'Test',
                    'choices': [{'message': {'content': 'Editado', 'reasoning': 'trace'}, 'finish_reason': 'stop'}],
                    'usage': {'cost': 0.001, 'prompt_tokens': 30, 'completion_tokens': 10}}
        with tempfile.TemporaryDirectory() as tmp:
            state = pathlib.Path(tmp)/'state.json'
            s = b.run_plan(p, state, 'SECRET', send=send, endpoints=lambda m: [ep])
            self.assertEqual(len(calls), 3)
            self.assertEqual(len(s['records']), 3)
            self.assertIn('diff', s['records'][0])
            b.run_plan(p, state, 'SECRET', send=send, endpoints=lambda m: [ep])
            self.assertEqual(len(calls), 3)
            self.assertNotIn('SECRET', state.read_text())
            def uncertain(payload, key):
                r = send(payload, key); del r['usage']['cost']; return r
            s = b.run_plan(p, pathlib.Path(tmp)/'unknown.json', 'SECRET', send=uncertain, endpoints=lambda m: [ep])
            self.assertEqual(s['records'][0]['status'], 'billing_uncertain')
            self.assertEqual(len(s['records']), 1)
            b.run_plan(p, pathlib.Path(tmp)/'unknown.json', 'SECRET', send=send, endpoints=lambda m: [ep])
            self.assertEqual(len(calls), 4)

    def test_requested_reasoning_probe_is_not_verified(self):
        b = load()
        self.assertTrue(hasattr(b, 'requested_reasoning'), 'probe parameters missing')
        ep = {'supported_parameters': ['reasoning', 'reasoning_effort']}
        self.assertEqual(b.requested_reasoning(ep, 'off'), {'enabled': False, 'effort': 'none'})
        self.assertEqual(b.requested_reasoning(ep, 'on'), {'enabled': True, 'effort': 'medium'})
        ep['supported_parameters'] = ['reasoning']
        self.assertEqual(b.requested_reasoning(ep, 'on'), {'enabled': True, 'max_tokens': 1024})
        with self.assertRaises(ValueError): b.requested_reasoning({}, 'off')

    def test_probe_plan_and_unused_modalities(self):
        b = load()
        ep = {'tag': 'test', 'context_length': 100000, 'max_completion_tokens': 4096,
              'supported_parameters': ['reasoning', 'reasoning_effort', 'max_tokens'],
              'pricing': {'prompt': '0.000001', 'completion': '0.000002',
                          'input_cache_write_1h': '0.000003', 'input_audio_cache': '0.01'}}
        self.assertTrue('probe' in __import__('inspect').signature(b.make_plan).parameters, 'probe planning missing')
        p = b.make_plan([{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}],
             [{'id': 'c', 'original': 'Texto'}], 'Skill', audit=lambda t: {}, probe=True, max_tokens=2048)
        self.assertEqual(len(p['calls']), 6)
        self.assertEqual({c['reasoning_status'] for c in p['calls']}, {'requested_unverified'})
        self.assertEqual(b.reserve_cost(ep, 100, 20), b.Decimal('0.000340'))

    def test_cli_plan_local_and_no_paid_default(self):
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            plan = pathlib.Path(tmp)/'plan.json'
            result = subprocess.run(['python3', str(SCRIPT), 'plan', '--out', str(plan), '--case-limit', '1', '--probe'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(plan.exists(), 'CLI planner missing')
            import json
            data = json.loads(plan.read_text())
            self.assertEqual(len(data['coverage']), 84)
            self.assertEqual({c['arm'] for c in data['calls']}, {'simple','skill','skill_audit'})
            result = subprocess.run(['python3', str(SCRIPT), 'run', '--plan', str(plan), '--state', str(pathlib.Path(tmp)/'state.json')], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_sequential_budget_uses_actual_and_never_overcommits(self):
        import tempfile
        b = load()
        ep = {'tag': 'test', 'context_length': 50000, 'max_completion_tokens': 4096,
              'pricing': {'prompt': '0.00001', 'completion': '0.000002'},
              'supported_parameters': ['reasoning', 'max_tokens']}
        p = b.make_plan([{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}],
                        [{'id': 'c', 'original': 'Texto', 'prompt': 'Tom informal'}], 'Skill',
                        budget='0.06', max_tokens=100, audit=lambda t: {})
        self.assertEqual(len(p['calls']), 3, 'planning must not spend future reservations')
        self.assertIn('Tom informal', str(p['calls'][0]['payload']))
        counter = []
        def send(payload, key):
            counter.append(1)
            return {'model': payload['model'], 'choices': [{'message': {'content': 'Texto'}, 'finish_reason': 'stop'}],
                    'usage': {'cost': 0.03, 'prompt_tokens': 20, 'completion_tokens': 10}}
        with tempfile.TemporaryDirectory() as tmp:
            s = b.run_plan(p, pathlib.Path(tmp)/'state.json', 'SECRET', send=send, endpoints=lambda m: [ep])
        self.assertEqual(len(counter), 1)
        self.assertEqual(s['stop_reason'], 'budget_insufficient_for_next_reservation')

    def test_blind_report_escapes_text_and_has_empty_rating_export(self):
        b = load()
        self.assertTrue(hasattr(b, 'render_report'), 'report missing')
        plan = {'fingerprint': 'abc123', 'coverage': [{'status': 'planned', 'model': 'secret/model'}]}
        state = {'records': [{'id': 'call-secret', 'model': 'secret/model', 'arm': 'skill', 'mode': 'off',
                 'case': 'c', 'status': 'completed', 'original': '<script>alert(1)</script>',
                 'edited': '<img src=x onerror=evil()>', 'task_prompt': 'Revise', 'cost_usd': '0.01'}]}
        page, key = b.render_report(plan, state)
        self.assertNotIn('secret/model', page)
        self.assertNotIn('call-secret', page)
        self.assertNotIn('<img src=x', page)
        self.assertIn('&lt;img', page)
        self.assertIn('download', page)
        self.assertIn('<option value="">', page)
        self.assertIn('human_ratings', page)
        self.assertEqual(len(key['labels']), 1)
        self.assertEqual(key['labels'][0]['model'], 'secret/model')

    def test_availability_evidence_controls_routes_not_hidden_compute(self):
        b = load()
        self.assertTrue(hasattr(b, 'apply_availability'), 'availability integration missing')
        ep = {'tag': 'route', 'supported_parameters': ['reasoning']}
        models = [{'id': 'vendor/model', 'status': 'available', 'endpoints': [ep]}]
        records = [{'mode': 'off', 'request': {'model': 'vendor/model', 'reasoning': {'enabled': False}, 'provider': {'only': ['route']}},
                    'response': {'error': {'message': 'reasoning required', 'code': 400}}, 'status': 'response'},
                   {'mode': 'on', 'request': {'model': 'vendor/model', 'reasoning': {'enabled': True, 'max_tokens': 1024}, 'provider': {'only': ['route']}},
                    'response': {'choices': [{}], 'usage': {'completion_tokens_details': {'reasoning_tokens': 0}}}, 'status': 'response'}]
        result = b.apply_availability(models, records)
        with self.assertRaises(ValueError): b.requested_reasoning(result[0]['endpoints'][0], 'off')
        with self.assertRaisesRegex(ValueError, 'rejected'):
            b.reasoning_params(result[0]['endpoints'][0], 'off')
        self.assertEqual(b.requested_reasoning(result[0]['endpoints'][0], 'on')['max_tokens'], 1024)
        self.assertEqual(result[0]['endpoints'][0]['availability']['on']['reasoning_tokens'], 0)

    def test_cli_availability_bundle_and_pending_route(self):
        import json, subprocess, tempfile
        b = load()
        ep = {'tag': 'route', 'context_length': 1000000, 'max_completion_tokens': 4096,
              'supported_parameters': ['reasoning', 'max_tokens'],
              'pricing': {'prompt': '0.000001', 'completion': '0.000002'}}
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            (tmp/'models.json').write_text(json.dumps({'models': [{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}]}))
            probes = tmp/'probes'; probes.mkdir()
            for mode, response in [('off', {'error': {'code': 400}}), ('on', {'choices': [{}], 'model': 'test/model-20260901'})]:
                (probes/(mode+'.json')).write_text(json.dumps({'mode': mode, 'request': {'model': 'test/model', 'provider': {'only': ['route']}, 'reasoning': {'enabled': mode == 'on', 'max_tokens': 1024}}, 'response': response}))
            (probes/'reconciliation.json').write_text('{"ignored": true}')
            result = subprocess.run(['python3', str(SCRIPT), 'plan', '--out', str(tmp/'plan.json'), '--models', str(tmp/'models.json'), '--availability', str(probes), '--probe', '--case-limit', '1'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            p = json.loads((tmp/'plan.json').read_text())
            self.assertEqual(len(p['calls']), 3)
            self.assertEqual({c['status'] for c in p['coverage'] if c['mode'] == 'off'}, {'unsupported'})
            self.assertEqual({c['mode'] for c in p['calls']}, {'on'})
            self.assertEqual({c['reasoning_status'] for c in p['calls']}, {'api_accepted_not_hidden_compute_verified'})
            text = p['calls'][1]['payload']['messages'][0]['content']
            self.assertIn('CATALOGO EDITORIAL', text)
            self.assertIn('ESTILOS', text)
            self.assertTrue(p['calls'][2]['payload']['messages'][0]['content'].startswith(text))
            self.assertNotIn('"metadata"', json.dumps(p['calls'][2]['input_audit']))
            self.assertEqual(p['calls'][0]['payload']['provider']['data_collection'], 'allow')
        ep['availability'] = {'on': {'status': 'pending', 'reasoning': {'enabled': True}}}
        with self.assertRaises(ValueError): b.reasoning_params(ep, 'on')
        ep['context_length'] = 1000000
        p = b.make_plan([{'id': 'test/model', 'status': 'available', 'endpoints': [ep]}],
                        [{'id': 'c', 'original': 'Texto', 'prompt': 'Pedido'}], 'Skill', audit=lambda t: {})
        pending = [c for c in p['coverage'] if c['mode'] == 'on']
        self.assertEqual({c['status'] for c in pending}, {'pending'})
        self.assertEqual(pending[0]['original'], 'Texto')
        self.assertEqual(pending[0]['availability'][0]['tag'], 'route')

    def test_comparison_full_messages_are_escaped_and_collapsed(self):
        import json
        from html import unescape
        b = load()
        messages = [{'role': 'system', 'content': 'Skill <script>unsafe</script>\nAuditoria completa'},
                    {'role': 'user', 'content': 'Original & texto'}]
        record = {'id': 'r', 'status': 'completed', 'original': 'Original & texto', 'edited': 'Revisado',
                  'task_prompt': 'Pedido breve', 'payload': {'messages': messages, 'max_tokens': 100}}
        page = b.render_comparison({'calls': [], 'coverage': []}, {'records': [record]})
        self.assertIn(json.dumps(messages, ensure_ascii=False, indent=2), unescape(page))
        self.assertNotIn('<script>unsafe', page)
        self.assertIn('<details><summary>Prompt completo', page)
        self.assertIn('name="viewport"', page)
        self.assertIn('overflow-x:auto', page)
        self.assertIn('max-height:400px;overflow:auto', page)
        self.assertLessEqual(page.count('<th>'), 6)
        for title in ['Parâmetros', 'Tokens / uso', 'Reasoning', 'Diff']:
            self.assertIn('<details><summary>' + title, page)

    def test_cli_comparison_and_blind_reports(self):
        import json, subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            plan = {'fingerprint': 'abc', 'calls': [], 'coverage': [{'status': 'unsupported', 'model': 'blocked', 'case': 'c', 'arm': 'skill', 'mode': 'off'}]}
            state = {'plan_fingerprint': 'abc', 'records': [{'id': 'r', 'status': 'completed', 'model': 'test/model', 'arm': 'skill', 'mode': 'on', 'original': '<original>', 'edited': '<edited>', 'task_prompt': 'pedido', 'cost_usd': '0.01', 'provider_returned': 'Route', 'diff': '-old\n+new'}]}
            for name, data in [('plan', plan), ('state', state)]: (tmp/(name+'.json')).write_text(json.dumps(data))
            result = subprocess.run(['python3', str(SCRIPT), 'report', '--plan', str(tmp/'plan.json'), '--state', str(tmp/'state.json'), '--out', str(tmp/'report.html')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            page = (tmp/'report.html').read_text()
            for value in ['<table', 'test/model', 'Route', 'pedido', '&lt;original&gt;', '&lt;edited&gt;', 'Parâmetros', 'Custo', 'Tokens', 'Reasoning', 'Latência', 'Diff', 'Erros', 'blocked']:
                self.assertIn(value, page)
            blind = (tmp/'report-blind.html').read_text()
            self.assertNotIn('—', page)
            self.assertNotIn('—', blind)
            self.assertNotIn('Autoria percebida', blind)
            for name in ['naturalidade', 'fidelidade', 'adequacao', 'selecao', 'economia']:
                self.assertIn(f'name="{name}"', blind)
            self.assertNotIn('selecao_economia', blind)
            self.assertIn('Rejeição factual crítica', blind)
            self.assertNotIn('test/model', blind)
            self.assertTrue((tmp/'report-key.json').exists())

    def test_key_validation_and_observed_alias(self):
        b = load()
        from unittest.mock import patch
        for key in [' secret', 'secret\n', 'sécret', 'sec\tret', '']:
            with patch.object(b.urllib.request, 'urlopen') as network:
                with self.assertRaises(ValueError): b.raw_send({}, key)
                network.assert_not_called()
        call = {'model': 'test/model', 'endpoint': {'availability': {'on': {'status': 'accepted', 'model_returned': 'test/model-20260901'}}}}
        self.assertTrue(b.model_matches(call, 'test/model-20260901'))
        self.assertFalse(b.model_matches(call, 'test/other'))
        self.assertFalse(b.model_matches(call, 'test/model-20990101'))

if __name__ == '__main__':
    unittest.main()
