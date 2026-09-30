import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().with_name('legacy_bench.py')

class BenchTests(unittest.TestCase):
    def test_schedule_is_frozen_balanced_and_blocked(self):
        self.assertTrue(SCRIPT.exists(), 'runner missing')
        spec = importlib.util.spec_from_file_location('bench', SCRIPT)
        b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(b)
        tasks = [{'id': str(n)} for n in range(12)]
        routes = [{'model': 'a'}, {'model': 'b'}]
        slots = b.schedule(tasks, routes, 42)
        self.assertEqual(len(slots), 96)
        self.assertEqual(slots, b.schedule(tasks, routes, 42))
        self.assertEqual(len({s['id'] for s in slots}), 96)
        for i in range(0, 96, 2):
            a, c = slots[i:i+2]
            self.assertEqual([a[k] for k in ('task','model','repeat')], [c[k] for k in ('task','model','repeat')])
            self.assertEqual({a['arm'], c['arm']}, {'baseline','skill'})

class ProtocolTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('bench', SCRIPT)
        self.b = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.b)

    def sample(self):
        config = {'budget':'10', 'reserve_per_request':'0.1',
                  'tasks':[{'id':'x','prompt':'x','expected':{'a':1}}],
                  'routes':[{'model':'a','provider':'Test','observed_provider':'Test',
                             'max_price':{'prompt':3,'completion':15,'request':0}}],
                  'slots':[{'id':'slot','task':'x','model':'a','repeat':0,'arm':'baseline'}]}
        response = {'id':'gen-x','model':'a','provider':'Test',
                    'choices':[{'message':{'content':'{"a":1}'},'finish_reason':'stop'}],
                    'usage':{'prompt_tokens':3,'completion_tokens':4,'total_tokens':7,'cost':0.01}}
        return config, response

    def test_malformed_responses_have_durable_failure_and_block_resume(self):
        import copy, tempfile
        _, valid = self.sample()
        variants = [None, [], 'bad', 1, float('nan'), {'usage':{'cost':float('inf')}}]
        for field, value in [('usage', []), ('usage', {'cost':0.01}), ('choices', [None]),
                             ('choices', {}), ('id', 3)]:
            response = copy.deepcopy(valid)
            response[field] = value
            variants.append(response)
        for field, value in [('message', {}), ('message', []), ('message', {'content':4}),
                             ('finish_reason', None), ('finish_reason', 3)]:
            response = copy.deepcopy(valid)
            response['choices'][0][field] = value
            variants.append(response)
        for field in ('prompt_tokens','completion_tokens','total_tokens'):
            for value in (None, True, -1, '3'):
                response = copy.deepcopy(valid)
                response['usage'][field] = value
                variants.append(response)
        for response in variants:
            with self.subTest(response=response), tempfile.TemporaryDirectory() as d:
                config, _ = self.sample()
                calls = []
                def call(request):
                    calls.append(request)
                    return 200, response
                outcome = self.b.run(Path(d), config, '', call)
                self.assertEqual(outcome, 'unknown_cost_or_protocol_error')
                result = self.b.rows(Path(d)/'attempts.jsonl')[-1]
                self.assertEqual(result['event'], 'result')
                self.assertEqual(result['score']['status'], 'operational_failure')
                self.b.run(Path(d), config, '', call)
                self.assertEqual(len(calls), 1)

    def test_valid_empty_and_refused_are_scored_fail_without_retry(self):
        import tempfile
        for message in ({'content':''}, {'content':None, 'refusal':'No'},
                        {'content':'{"a":1}', 'refusal':'No'}):
            with tempfile.TemporaryDirectory() as d:
                config, response = self.sample()
                response['choices'][0]['message'] = message
                calls = []
                def call(request):
                    calls.append(request)
                    return 200, response
                self.assertEqual(self.b.run(Path(d), config, '', call), 'complete')
                self.assertEqual(self.b.rows(Path(d)/'attempts.jsonl')[-1]['score']['status'], 'fail')
                self.b.run(Path(d), config, '', call)
                self.assertEqual(len(calls), 1)

    def test_final_cost_overruns_are_durable_and_block_resume(self):
        import tempfile
        for prior, cost, expected in [('0', '0.2', 'reserve_exceeded'),
                                      ('9.9', '0.2', 'budget_exceeded'),
                                      ('0', '11', 'budget_exceeded')]:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                config, response = self.sample()
                self.b.append(root/'attempts.jsonl', {'event':'result','slot':'prior','cost':prior})
                response['usage']['cost'] = cost
                calls = []
                def call(request):
                    calls.append(request)
                    return 200, response
                self.assertEqual(self.b.run(root, config, '', call), 'unknown_cost_or_protocol_error')
                result = self.b.rows(root/'attempts.jsonl')[-1]
                self.assertEqual(result['protocol_error'], expected)
                self.assertEqual(result['cost'], cost)
                self.b.run(root, config, '', call)
                self.assertEqual(len(calls), 1)

    def test_reserve_covers_full_input_output_and_route_caps(self):
        import copy, tempfile
        config, _ = self.sample()
        variants = []
        for reserve, skill in [('0.001', ''), ('0.1', 'é' * 30000)]:
            c = copy.deepcopy(config)
            c['reserve_per_request'] = reserve
            c['slots'][0]['arm'] = 'skill'
            variants.append((c, skill))
        for caps in (None, {'prompt':3}, {'prompt':3,'completion':15},
                     {'prompt':-1,'completion':15,'request':0},
                     {'prompt':'NaN','completion':15,'request':0}, {'prompt':3,'completion':15,'request':1}):
            c = copy.deepcopy(config)
            c['routes'][0]['max_price'] = caps
            variants.append((c, ''))
        for c, skill in variants:
            with self.subTest(config=c), tempfile.TemporaryDirectory() as d:
                calls = []
                with self.assertRaises(ValueError):
                    self.b.run(Path(d), c, skill, lambda request: calls.append(request))
                self.assertFalse(calls)
                self.assertFalse((Path(d)/'attempts.jsonl').exists())

    def test_strict_json_scoring(self):
        task = {'expected': {'id': '001', 'n': 1, 'hold': False}}
        self.assertEqual(self.b.score(task, '{"id":"001","n":1,"hold":false}', 'stop')['status'], 'pass')
        for text in ['{}', '{"id":"001","n":true,"hold":false}', '{"id":"001","n":1,"hold":false,"hold":true}', '```json\n{}\n```']:
            self.assertEqual(self.b.score(task, text, 'stop')['status'], 'fail')
        self.assertEqual(self.b.score({}, 'good prose', 'stop')['status'], 'unscored')
        self.assertEqual(self.b.score(task, '{}', 'length')['reason'], 'truncated')

    def test_payload_has_only_neutral_task_and_full_skill(self):
        slot = {'model': 'test/model', 'arm': 'skill'}
        route = {'provider': 'Test'}
        p = self.b.payload(slot, {'prompt':'task'}, route, '---\nFULL SKILL\n')
        self.assertEqual(p['messages'], [{'role':'system','content':self.b.NEUTRAL}, {'role':'system','content':'---\nFULL SKILL\n'}, {'role':'user','content':'task'}])
        self.assertFalse(p['provider']['allow_fallbacks'])
        self.assertEqual(p['provider']['only'], ['Test'])
        self.assertTrue(p['provider']['require_parameters'])
        slot['arm'] = 'baseline'
        base = self.b.payload(slot, {'prompt':'task'}, route, 'ignored')
        self.assertEqual(len(base['messages']), 2)
        self.assertEqual({k:v for k,v in base.items() if k!='messages'}, {k:v for k,v in p.items() if k!='messages'})

    def test_budget_rejects_unknown_negative_and_excess(self):
        from decimal import Decimal
        self.assertTrue(self.b.can_spend(Decimal('0.5'), Decimal('0.1'), Decimal('10')))
        for used, reserve in [(None,'1'), ('9.95','0.1'), ('-1','1'), ('NaN','1')]:
            self.assertFalse(self.b.can_spend(used, reserve, '10'))

    def test_actual_fixtures_are_balanced_and_validators_reject_empty(self):
        tasks = self.b.rows(SCRIPT.with_name('legacy_cases.jsonl'))
        self.assertEqual(len(tasks), 12)
        self.assertEqual(len({t['id'] for t in tasks}), 12)
        self.assertEqual(sum(t['language']=='pt' for t in tasks), 6)
        import json
        for task in tasks:
            if 'expected' in task:
                self.assertEqual(self.b.score(task,json.dumps(task['expected']),'stop')['status'],'pass')
                self.assertEqual(self.b.score(task,'{}','stop')['status'],'fail')
            else:
                self.assertEqual(sum(task['rubric'].values()),100)
                self.assertTrue(task['critical'])

    def test_reasoning_and_price_ceiling_are_explicit_when_configured(self):
        route={'provider':'Anthropic','reasoning':{'enabled':False},'max_price':{'prompt':3,'completion':15}}
        p=self.b.payload({'arm':'baseline','model':'a'},{'prompt':'x'},route,'')
        self.assertEqual(p['reasoning'], {'enabled':False})
        self.assertEqual(p['provider']['max_price'], route['max_price'])

    def test_api_redacts_credentials_but_preserves_normal_responses(self):
        import io, json, tempfile
        from unittest.mock import patch
        from urllib.error import HTTPError
        key = 'synthetic-private-value'
        secret = 'sk-or-v1-' + 'a' * 32
        ordinary = {'message':'Olá\n spaces  remain; sk-example is ordinary text', 'nested':[1, None, True]}
        sensitive = {'error':{'message':f'{key} Authorization: Bearer TEST_SECRET {secret}',
                              'api_key':'another-private-value'}, key:[ordinary]}
        for status, source in [(200, ordinary), (200, sensitive), (401, sensitive)]:
            stream = io.BytesIO(json.dumps(source).encode())
            stream.status = status
            with patch.object(self.b.urllib.request, 'urlopen') as opener:
                if status == 200:
                    opener.return_value = stream
                else:
                    opener.side_effect = HTTPError('https://example.invalid', status, 'bad', {}, stream)
                returned_status, response = self.b.api('chat/completions', key, {})
            self.assertEqual(returned_status, status)
            if source is ordinary:
                self.assertEqual(response, ordinary)
            else:
                encoded = json.dumps(response)
                for value in (key, secret, 'TEST_SECRET', 'another-private-value'):
                    self.assertNotIn(value, encoded)
                with tempfile.TemporaryDirectory() as d:
                    config, _ = self.sample()
                    self.b.run(Path(d), config, '', lambda request:(status, response))
                    logged = (Path(d)/'attempts.jsonl').read_text()
                    self.assertNotIn(key, logged)
                    self.assertNotIn(secret, logged)

    def test_api_transport_error_never_exposes_credential(self):
        from unittest.mock import patch
        key = 'synthetic-private-value'
        with patch.object(self.b.urllib.request, 'urlopen', side_effect=TimeoutError(key)):
            with self.assertRaises(Exception) as caught:
                self.b.api('key', key)
        self.assertNotIn(key, str(caught.exception))

    def test_network_exception_does_not_leak_secret(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            config={'budget':'10','reserve_per_request':'0.1','tasks':[{'id':'x','prompt':'x'}], 'routes':[{'model':'a','provider':'Test','observed_provider':'Test','max_price':{'prompt':3,'completion':15,'request':0}}], 'slots':[{'id':'x','task':'x','model':'a','repeat':0,'arm':'baseline'}]}
            def call(p):
                raise TimeoutError('secret-that-must-not-appear')
            self.b.run(Path(d),config,'',call)
            text=(Path(d)/'attempts.jsonl').read_text()
            self.assertNotIn('secret-that-must-not-appear',text)
            self.assertIn('TimeoutError',text)

    def test_freeze_rejects_wrong_design_and_typed_fixture_mismatch(self):
        import copy, json, tempfile
        base, _ = self.sample()
        base['tasks'] = [{'id':str(n),'prompt':'x','expected':{'n':1}} for n in range(12)]
        base['routes'].append(dict(base['routes'][0], model='b'))
        variants = []
        c = copy.deepcopy(base)
        c['tasks'] += [dict(t, id='extra'+t['id']) for t in c['tasks']]
        c['routes'] = c['routes'][:1]
        variants.append((c, c['tasks']))
        for change in ('duplicate_task', 'duplicate_model', 'typed_mismatch', 'unrelated', 'reserve'):
            c = copy.deepcopy(base)
            fixtures = copy.deepcopy(c['tasks'])
            if change == 'duplicate_task': c['tasks'][1]['id'] = c['tasks'][0]['id']
            if change == 'duplicate_model': c['routes'][1]['model'] = 'a'
            if change == 'typed_mismatch': fixtures[0]['expected']['n'] = True
            if change == 'unrelated': fixtures = [{'id':'unrelated'}]
            if change == 'reserve': c['reserve_per_request'] = '0.001'
            variants.append((c, fixtures))
        for config, fixtures in variants:
            with self.subTest(config=config), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                (root/'SKILL.snapshot.md').write_text('full')
                (root/'cases.jsonl').write_text(''.join(json.dumps(t)+'\n' for t in fixtures))
                with self.assertRaises(ValueError):
                    self.b.freeze(root, config)
                self.assertFalse((root/'manifest.json').exists())

    def test_freeze_detects_tampering(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'SKILL.snapshot.md').write_text('full')
            config, _ = self.sample()
            config['tasks'] = [{'id':str(n), 'prompt':'x'} for n in range(12)]
            config['routes'].append(dict(config['routes'][0], model='b'))
            (root/'cases.jsonl').write_text(''.join(self.b.json.dumps(t)+'\n' for t in config['tasks']))
            self.b.freeze(root, config)
            self.b.verify(root)
            (root/'SKILL.snapshot.md').write_text('changed')
            with self.assertRaises(ValueError):
                self.b.verify(root)

    def test_run_records_success_and_resumes_without_duplication(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            config = {'budget':'10','reserve_per_request':'0.1','tasks':[{'id':'x','prompt':'x','expected':{'a':1}}], 'routes':[{'model':'a','provider':'Test','observed_provider':'Test','max_price':{'prompt':3,'completion':15,'request':0}}], 'slots':[{'id':'slot','task':'x','model':'a','repeat':0,'arm':'baseline'}]}
            response = {'id':'gen-x','model':'a','provider':'Test','choices':[{'message':{'content':'{"a":1}'},'finish_reason':'stop'}],'usage':{'prompt_tokens':3,'completion_tokens':4,'total_tokens':7,'cost':0.01}}
            calls=[]
            def call(p):
                calls.append(p)
                return 200, response
            self.b.run(root, config, 'skill', call)
            self.b.run(root, config, 'skill', call)
            self.assertEqual(len(calls), 1)
            result = self.b.rows(root/'attempts.jsonl')[-1]
            self.assertEqual(result['score']['status'], 'pass')
            self.assertEqual(result['raw_response'], response)
            self.assertEqual(result['cost'], '0.01')

    def test_run_stops_on_unknown_charge_and_route_mismatch(self):
        import tempfile
        for response in [(503, {'error':{'message':'unavailable'}}), (200, {'model':'wrong','provider':'Test','usage':{'cost':0.01},'choices':[]})]:
            with tempfile.TemporaryDirectory() as d:
                config={'budget':'10','reserve_per_request':'0.1','tasks':[{'id':'x','prompt':'x'}], 'routes':[{'model':'a','provider':'Test','observed_provider':'Test','max_price':{'prompt':3,'completion':15,'request':0}}], 'slots':[{'id':str(n),'task':'x','model':'a','repeat':0,'arm':'baseline'} for n in range(2)]}
                calls=[]
                def call(p):
                    calls.append(p)
                    return response
                self.b.run(Path(d), config, '', call)
                self.assertEqual(len(calls), 1)
                self.b.run(Path(d), config, '', call)
                self.assertEqual(len(calls), 1)

    def test_resume_never_replays_started_slots(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'attempts.jsonl'
            self.b.append(p, {'event':'start','slot':'a'})
            self.b.append(p, {'event':'result','slot':'b','cost':'0.01'})
            self.assertEqual(self.b.started(p), {'a','b'})
            with p.open('a') as f:
                f.write('{bad\n')
            with self.assertRaises(ValueError):
                self.b.started(p)

if __name__ == '__main__':
    unittest.main()
