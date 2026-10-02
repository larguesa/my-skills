"""Offline contracts for the uncapped genre runner; no real inference."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS / 'scripts'))
import benchmark as b
import contos as c
try:
    import generos as g
except ModuleNotFoundError:
    g = None


def config():
    return dict(schema=1, frozen_at='2026-10-02', budget_usd=None, max_tokens=4096,
                judge_max_tokens=16384, blind_seed='20261002-generos-v1',
                cases=[dict(id='case', genre='Técnico', prompt='Título e código solicitados.')],
                routes=[dict(model='test/model', mode='on', reasoning={'enabled': True},
                             endpoint=dict(tag='test', provider_name='Test', context_length=1000000,
                                           max_completion_tokens=20000,
                                           supported_parameters=['max_tokens', 'reasoning']))],
                judges=[], sha256={})


def response(payload, text='Texto válido', cost=500):
    return dict(id='gen-test', model=payload['model'], provider='Test',
                usage=dict(cost=cost, prompt_tokens=123, completion_tokens=42,
                           completion_tokens_details={'reasoning_tokens': 7}),
                choices=[dict(finish_reason='stop', message=dict(content=text))])


class GenreTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(g, 'The genre runner has not been implemented')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.frozen = self.folder / 'frozen'
        self.frozen.mkdir()
        (self.frozen / 'skill-bundle.txt').write_text('EXACT FULL BUNDLE\nλ\n', encoding='utf-8')
        self.out = self.folder / 'run'

    def calls(self):
        return g.generation_calls(config(), self.frozen)

    def test_912_slots_change_only_exact_skill_context_without_money_bounds(self):
        cfg = config()
        cfg['cases'] = c.load(TESTS / 'experiments/cases.json')['cases']
        cfg['routes'] = c.load(TESTS / 'frozen/config.json')['routes']
        calls = g.generation_calls(cfg, self.frozen)
        self.assertEqual(len(calls), 912)
        self.assertEqual(len({call['id'] for call in calls}), 912)
        for original, skill in zip(calls[::2], calls[1::2]):
            self.assertEqual(original['payload']['messages'][1], skill['payload']['messages'][1])
            system = original['payload']['messages'][0]['content']
            self.assertNotIn('conto', system.lower())
            self.assertNotIn('sem título', system.lower())
            self.assertEqual(skill['payload']['messages'][0]['content'],
                             system + '\n\nSKILL E REFERÊNCIAS:\nEXACT FULL BUNDLE\nλ\n')
            self.assertEqual({k:v for k,v in original['payload'].items() if k != 'messages'},
                             {k:v for k,v in skill['payload'].items() if k != 'messages'})
            self.assertNotIn('reservation_usd', original)
            self.assertNotIn('max_price', original['payload']['provider'])
            self.assertFalse(original['payload']['provider']['allow_fallbacks'])
        with self.assertRaises(ValueError):
            g.generation_calls(dict(cfg, budget_usd='1'), self.frozen)

    def test_durable_intent_precedes_submit_and_pilot_is_reused_uncapped(self):
        self.assertTrue(callable(getattr(g, 'run_chat', None)), 'Missing durable runner')
        calls = self.calls()
        submitted = []
        def send(payload, key):
            path = self.out / 'requests' / (calls[len(submitted)]['id'] + '.json')
            intent = c.load(path)
            self.assertEqual(intent['status'], 'started')
            self.assertEqual(intent['payload'], payload)
            self.assertTrue((self.out / 'runner-hashes.json').exists())
            submitted.append(payload)
            return response(payload, text='Texto ' + key)
        pilot = g.run_chat(calls[:1], self.out, 'generation', 'fake-key', send=send)
        self.assertEqual(pilot['records'][0]['status'], 'completed')
        first_bytes = (self.out / 'requests' / (calls[0]['id'] + '.json')).read_bytes()
        state = g.run_chat(calls, self.out, 'generation', 'fake-key', send=send)
        self.assertEqual(len(submitted), 2)
        self.assertEqual(len(state['records']), 2)
        self.assertEqual(first_bytes, (self.out / 'requests' / (calls[0]['id'] + '.json')).read_bytes())
        g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda *_: self.fail('Replay'))
        record = state['records'][0]
        self.assertEqual(record['cost_usd'], '500')
        self.assertEqual(record['usage']['completion_tokens_details']['reasoning_tokens'], 7)
        self.assertEqual((record['provider_returned'], record['model_returned']), ('Test', 'test/model'))
        self.assertIn('finished_at', record)
        self.assertIn('elapsed_seconds', record)
        self.assertNotIn('fake-key', json.dumps(record))
        self.assertEqual(record['edited'], 'Texto [REDACTED]')
    def test_invalid_first_outputs_are_retained_and_never_regenerated(self):
        calls = self.calls()
        for index, change in enumerate(('empty', 'refusal', 'length', 'missing_id', 'wrong_model', 'no_choices')):
            with self.subTest(change=change):
                out = self.folder / str(index)
                sent = []
                def send(payload, key):
                    data = response(payload)
                    if not sent:
                        if change == 'empty': data['choices'][0]['message']['content'] = '  '
                        if change == 'refusal': data['choices'][0]['message']['refusal'] = 'No'
                        if change == 'length': data['choices'][0]['finish_reason'] = 'length'
                        if change == 'missing_id': del data['id']
                        if change == 'wrong_model': data['model'] = 'other/model'
                        if change == 'no_choices': data['choices'] = []
                    sent.append(payload)
                    return data
                state = g.run_chat(calls, out, 'generation', 'fake-key', send=send)
                self.assertEqual([r['status'] for r in state['records']], ['invalid_response', 'completed'])
                self.assertNotIn('stop_reason', state)
                self.assertEqual(len(sent), 2)
                g.run_chat(calls, out, 'generation', 'fake-key', send=lambda *_: self.fail('Replay'))
                self.assertIn('response', state['records'][0])
    def test_billing_and_transport_ambiguity_stop_all_phases_without_replay(self):
        calls = self.calls()
        for index, kind in enumerate(('missing_cost', 'bad_tokens', 'transport', 'crash', 'rejection')):
            with self.subTest(kind=kind):
                out = self.folder / ('amb-' + str(index))
                def send(payload, key):
                    if kind == 'transport': raise TimeoutError(key)
                    if kind == 'crash': raise KeyboardInterrupt()
                    if kind == 'rejection': return {'error': {'code': 400, 'message': key + ' rejected'}}
                    data = response(payload)
                    if kind == 'missing_cost': del data['usage']['cost']
                    if kind == 'bad_tokens': data['usage']['prompt_tokens'] = True
                    return data
                if kind == 'crash':
                    with self.assertRaises(KeyboardInterrupt):
                        g.run_chat(calls, out, 'generation', 'fake-key', send=send)
                else:
                    state = g.run_chat(calls, out, 'generation', 'fake-key', send=send)
                    self.assertIn('stop_reason', state)
                    self.assertEqual(len(state['records']), 1)
                    if kind == 'rejection':
                        self.assertEqual(state['records'][0].get('outcome'), 'rejected')
                        self.assertNotIn('fake-key', json.dumps(state))
                blocked = g.run_chat(calls, out, 'another-phase', 'fake-key', send=lambda *_: self.fail('Replay'))
                self.assertIn('stop_reason', blocked)
                self.assertEqual(len(blocked['records']), 1)
                stored = c.load(out / 'requests' / (calls[0]['id'] + '.json'))
                self.assertNotIn('fake-key', json.dumps(stored))
    def test_anonymous_chunks_are_stable_for_pilot_full_resume_and_exclude_invalid(self):
        self.assertTrue(callable(getattr(g, 'anonymous_chunks', None)), 'Missing stable chunks')
        cfg = config()
        cfg['routes'] = [dict(cfg['routes'][0], model='test/model' + str(i)) for i in range(9)]
        calls = g.generation_calls(cfg, self.frozen)
        records = [dict(call, status='completed', edited=call['arm'] + str(i),
                        response={'id': 'gen-' + str(i)}) for i,call in enumerate(calls)]
        state = {'records': records}
        anon, mapping = g.anonymous_case(cfg, state, 'case')
        self.assertEqual((anon, mapping), c.anonymous_case(cfg, state, 'case'))
        chunks = g.anonymous_chunks(cfg, state, 'case')
        self.assertEqual([len(x['state']['pares']) for x in chunks], [1, 4, 4])
        self.assertEqual(sum(len(x['state']['textos']) for x in chunks), 18)
        pilot = g.anonymous_chunks(cfg, {'records': records[:2]}, 'case')
        self.assertEqual(pilot[0], chunks[0])
        self.assertTrue(pilot[0]['eligible'])
        self.assertFalse(pilot[1]['eligible'])
        self.assertNotIn('test/model', json.dumps(chunks[0]['state']))
        records[0]['status'] = 'invalid_response'
        records[0]['response'] = {}
        broken = g.anonymous_chunks(cfg, state, 'case')
        self.assertFalse(broken[0]['eligible'])
        self.assertTrue(broken[0]['invalid_ids'])
        records[0]['status'] = 'completed'
        with self.assertRaises(ValueError):
            g.anonymous_case(cfg, state, 'case')
    def test_native_score_quality_is_not_noul_confidence_and_caps_only_at_aggregation(self):
        self.assertTrue(callable(getattr(g, 'decisions_payload', None)), 'Missing native rubric')
        state = dict(prompt='API technique', textos={'t000': 'a', 't001': 'b'},
                     pares={'p000': {'A': 't000', 'B': 't001'}})
        payload = g.decisions_payload(state)
        self.assertEqual(payload['model'], 'typesafe/jev-1.13')
        self.assertNotIn('messages', payload)
        self.assertNotIn('max_price', payload['provider'])
        self.assertEqual(payload['questions']['t000']['type'], 'noul')
        self.assertEqual(payload['questions']['t000_naturalidade']['type'], 'score')
        self.assertEqual(len(payload['questions']['t000_naturalidade']['criteria']), 5)
        self.assertEqual(payload['questions']['t000_critico']['type'], 'choice')
        answers = {}
        for qid, question in payload['questions'].items():
            if question['type'] == 'noul': answers[qid] = dict(type='noul', noul=0.9)
            if question['type'] == 'score':
                answers[qid] = dict(type='score', score=4, confidence=0.01,
                                    legend={str(i):s for i,s in enumerate(question['criteria'])})
            if question['type'] == 'choice':
                answers[qid] = dict(type='choice', choice='yes' if qid.endswith('_critico') else 'B')
        result = g.validate_judge({'answers': answers}, state, decisions=True)
        self.assertEqual(result['deteccao']['t000'], 90)
        self.assertEqual(result['qualidade']['t000']['naturalidade'], 100)
        self.assertIsNone(result['qualidade']['t000']['justificativa'])
        self.assertEqual(result['justificativas_status'], 'unavailable_native_typed_decisions')
        self.assertEqual(result['qualidade']['t000']['correcao'], 100)
        capped = g.aggregate_quality(result['qualidade']['t000'])
        self.assertEqual((capped['correcao'], capped['total']), (25, 49))
        for bad in (True, float('nan'), 4.01, -1):
            data = copy.deepcopy(answers)
            data['t000_naturalidade']['score'] = bad
            with self.assertRaises(ValueError): g.validate_judge({'answers': data}, state, True)
        chat = dict(deteccao={'t000': 30, 't001': 40}, preferencia={'p000': 'A'},
                    qualidade={tid:dict(naturalidade=75, clareza=75, adequacao=75, correcao=75,
                                       critico=False, justificativa='Breve motivo.') for tid in state['textos']})
        self.assertEqual(g.validate_judge(chat, state), chat)
        for change in ('missing', 'boolean_score', 'critical_string', 'no_reason'):
            bad = copy.deepcopy(chat)
            if change == 'missing': del bad['qualidade']['t001']
            if change == 'boolean_score': bad['qualidade']['t000']['clareza'] = True
            if change == 'critical_string': bad['qualidade']['t000']['critico'] = 'false'
            if change == 'no_reason': bad['qualidade']['t000']['justificativa'] = None
            with self.assertRaises(ValueError): g.validate_judge(bad, state)
        with self.assertRaises(ValueError):
            g.decisions_payload(dict(state, textos={'t000': None}))
    def test_http_errors_preserve_redacted_rate_limit_evidence_without_retry(self):
        import io
        import urllib.error
        calls = self.calls()
        data = {'error': {'code': 429, 'message': 'fake-key Bearer other-token sk-or-v1-abcdef',
                          'metadata': {'retry_after': 60}}}
        def send(payload, key):
            raise urllib.error.HTTPError('https://openrouter.ai', 429, 'rate',
                                         {'Retry-After': '60'}, io.BytesIO(json.dumps(data).encode()))
        state = g.run_chat(calls, self.out, 'generation', 'fake-key', send=send)
        record = state['records'][0]
        self.assertEqual(record.get('http_status'), 429)
        self.assertEqual(record.get('api_error', {}).get('code'), 429)
        self.assertEqual(record['response']['error']['metadata']['retry_after'], 60)
        self.assertEqual(record['http_headers']['Retry-After'], '60')
        for secret in ('fake-key', 'other-token', 'sk-or-v1-abcdef'):
            self.assertNotIn(secret, json.dumps(state))
        g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda *_: self.fail('Replay'))
    def test_returned_provider_and_native_output_usage_are_checked_without_double_counting(self):
        calls = self.calls()[:1]
        for kind, expected in [('provider', 'invalid_response'), ('output_bound', 'invalid_response'),
                               ('reasoning', 'completed')]:
            with self.subTest(kind=kind):
                def send(payload, key):
                    data = response(payload, cost=0.1)
                    if kind == 'provider': data['provider'] = 'Unexpected'
                    if kind == 'output_bound': data['usage']['completion_tokens'] = 4097
                    if kind == 'reasoning': data['usage']['completion_tokens_details']['reasoning_tokens'] = 43
                    return data
                state = g.run_chat(calls, self.folder / kind, 'generation', 'fake-key', send=send)
                record = state['records'][0]
                self.assertEqual(record['status'], expected)
                self.assertEqual(record['cost_usd'], '0.1')
                if kind == 'reasoning':
                    self.assertEqual(record['usage']['completion_tokens'], 42)
                    self.assertIn('reasoning_exceeds_native_completion', record.get('usage_issues', []))
    def test_execute_interleaves_cases_reuses_pilot_and_sends_native_decisions(self):
        self.assertTrue(callable(getattr(g, 'execute', None)), 'Missing executable phases')
        cfg = config()
        cfg['cases'].append(dict(id='case2', genre='Didático', prompt='Outro pedido.'))
        cfg['routes'].append(dict(cfg['routes'][0], model='test/model2'))
        cfg['judges'] = [dict(cfg['routes'][0], name=name, model='test/' + name) for name in ('astra', 'opus')]
        cfg['sha256'] = {'skill-bundle.txt': c.hashlib.sha256((self.frozen / 'skill-bundle.txt').read_bytes()).hexdigest()}
        cp = self.frozen / 'config.json'
        b.save_json(cp, cfg)
        sent = []
        def chat_send(payload, key):
            sent.append(('chat', payload))
            if payload['messages'][0]['content'] == g.JUDGE:
                anon = json.loads(payload['messages'][1]['content'])
                judgment = dict(deteccao={tid:20 for tid in anon['textos']},
                    preferencia={pid:'empate' for pid in anon['pares']},
                    qualidade={tid:dict(naturalidade=75, clareza=75, adequacao=75,
                        correcao=75, critico=False, justificativa='Atende ao pedido.') for tid in anon['textos']})
                return response(payload, json.dumps(judgment))
            return response(payload)
        def decision_send(payload, key):
            sent.append(('decisions', payload))
            answers = {}
            for qid,q in payload['questions'].items():
                if q['type'] == 'noul': answers[qid] = dict(type='noul', noul=0.2)
                if q['type'] == 'score': answers[qid] = dict(type='score', score=3, confidence=0.01)
                if q['type'] == 'choice': answers[qid] = dict(type='choice', choice='no' if qid.endswith('_critico') else 'empate')
            return dict(id='gen-decision', model='typesafe/jev-1.13-20260917', provider='TypeSafe',
                        usage=dict(cost=0.1, input_tokens=100, output_tokens=100), answers=answers)
        with patch.object(g.urllib.request, 'urlopen', side_effect=AssertionError('Real network forbidden')):
            pilot = g.execute(cp, self.out, 'fake-key', pilot=True, send=chat_send, decisions_send=decision_send)
            self.assertEqual(len(sent), 5)
            self.assertEqual(pilot['status'], 'pilot_completed')
            before = {p.name:p.read_bytes() for p in (self.out / 'requests').glob('*.json')}
            full = g.execute(cp, self.out, 'fake-key', send=chat_send, decisions_send=decision_send)
            self.assertEqual(full['status'], 'completed')
            self.assertEqual(full['generations'], 8)
            self.assertEqual(full['judge_calls'], 12)
            self.assertEqual(len(sent), 20)
            for name,content in before.items(): self.assertEqual((self.out / 'requests' / name).read_bytes(), content)
            count = len(sent)
            g.execute(cp, self.out, 'fake-key', send=chat_send, decisions_send=decision_send)
            self.assertEqual(len(sent), count)
        first_case2 = next(i for i,(_,p) in enumerate(sent) if p.get('messages', [{}])[-1].get('content') == 'Outro pedido.')
        self.assertEqual(first_case2, 10)
        jev_state = next(p['state'] for api,p in sent if api == 'decisions')
        chat_state = next(json.loads(p['messages'][1]['content']) for api,p in sent if api == 'chat' and p['messages'][0]['content'] == g.JUDGE)
        self.assertEqual(jev_state, chat_state)
        cfg['blind_seed'] = 'changed'
        b.save_json(cp, cfg)
        with self.assertRaises(ValueError):
            g.execute(cp, self.out, 'fake-key', send=lambda *_:self.fail('Changed freeze'))
    def test_cli_is_offline_without_opt_in_and_native_transport_uses_exact_endpoint(self):
        self.assertTrue(callable(getattr(g, 'main', None)), 'Missing CLI')
        import contextlib
        import io
        cfg = config()
        b.save_json(self.frozen / 'config.json', cfg)
        args = ['--config', str(self.frozen / 'config.json'), '--out', str(self.out),
                '--key-file', str(self.folder / 'nonexistent-secret'), '--pilot']
        with patch.object(g.urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')):
            with contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(g.main(args), 0)
            self.assertEqual(json.loads(stream.getvalue())['paid_calls'], 0)
            self.assertFalse(self.out.exists())
        class Raw:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'not-json'
        requests = []
        def urlopen(req, timeout):
            requests.append(req)
            self.assertEqual(timeout, 180)
            return Raw()
        with patch.object(g.urllib.request, 'urlopen', side_effect=urlopen):
            self.assertEqual(g.raw_decisions({'model':'typesafe/jev-1.13'}, 'fake-key'), {'raw_body':'not-json'})
        self.assertEqual(requests[0].full_url, 'https://openrouter.ai/api/alpha/decisions')
        self.assertEqual(requests[0].get_header('Authorization'), 'Bearer fake-key')
        self.assertEqual(requests[0].get_method(), 'POST')
        self.assertEqual(json.loads(requests[0].data), {'model':'typesafe/jev-1.13'})
        key_file = self.folder / 'key'
        key_file.write_text('fake-key\n')
        with patch.object(g, 'execute', return_value={'status':'pilot_completed', 'stop_reason':None}) as execute:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(g.main(args[:4] + ['--key-file', str(key_file), '--execute-paid', '--pilot']), 0)
            self.assertEqual(execute.call_args.args[2], 'fake-key')
            self.assertTrue(execute.call_args.kwargs['pilot'])
    def test_lock_fingerprint_and_metadata_guards_prevent_any_new_submit(self):
        import fcntl
        calls = self.calls()
        self.out.mkdir()
        with (self.out / '.runner.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda *_:self.fail('Lock bypass'))
        bad = copy.deepcopy(calls)
        bad[0]['payload']['max_tokens'] = 1
        with self.assertRaises(ValueError):
            g.run_chat(bad, self.out, 'generation', 'fake-key', send=lambda *_:self.fail('Fingerprint bypass'))
        g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda p,k:response(p))
        path = self.out / 'requests' / (calls[0]['id'] + '.json')
        record = c.load(path)
        record['payload']['messages'][1]['content'] = 'tampered'
        b.save_json(path, record)
        with self.assertRaises(ValueError):
            g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda *_:self.fail('Metadata bypass'))
        hashes = c.load(self.out / 'runner-hashes.json')
        hashes['sha256']['generos.py'] = 'changed'
        b.save_json(self.out / 'runner-hashes.json', hashes)
        with self.assertRaises(ValueError):
            g.run_chat(calls, self.out, 'generation', 'fake-key', send=lambda *_:self.fail('Code freeze bypass'))

    def test_invalid_generations_and_invalid_judges_are_published_without_replay(self):
        cfg = config()
        cfg['judges'] = [dict(cfg['routes'][0], name='astra')]
        b.save_json(self.frozen / 'config.json', cfg)
        cp = self.frozen / 'config.json'
        # Empty first outputs cannot enter any judge payload.
        result = g.execute(cp, self.out, 'fake-key', send=lambda p,k:response(p, ''),
                           decisions_send=lambda *_:self.fail('Invalid text judged'))
        self.assertEqual(result['judge_calls'], 0)
        self.assertEqual(result['status'], 'completed_with_invalid_responses')
        g.execute(cp, self.out, 'fake-key', send=lambda *_:self.fail('Invalid generation replayed'))
        # A billed invalid typed answer remains visible and is never retried.
        out = self.folder / 'invalid-judge'
        result = g.execute(cp, out, 'fake-key', send=lambda p,k:response(p, '{}' if p['messages'][0]['content'] == g.JUDGE else 'Texto'),
            decisions_send=lambda p,k:dict(id='gen-d', model='typesafe/jev-1.13-20260917', provider='TypeSafe',
                usage=dict(cost=0.1, input_tokens=100, output_tokens=10), answers={}))
        self.assertEqual(result['statuses']['invalid_response'], 2)
        self.assertEqual(result['judge_calls'], 2)
        g.execute(cp, out, 'fake-key', send=lambda *_:self.fail('Invalid judge replayed'),
                  decisions_send=lambda *_:self.fail('Invalid decision replayed'))


if __name__ == '__main__':
    unittest.main()
