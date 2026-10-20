"""Fixtures artificiais offline; não são resultados da rodada."""
import base64
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent

def load(name, filename):
    path = ROOT / filename
    if not path.exists():
        raise AssertionError('script de publicação ainda não implementado')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class PublicationTests(unittest.TestCase):
    def test_spending_authorization_is_not_an_http_header(self):
        s = load('sanitize_publication', 'sanitize-publication.py')
        authorization = {'decision': 'Autorizado.', 'thread_id': 'test', 'scope': 'offline'}
        s.scan(json.dumps({'authorization': authorization}).encode())
        with self.assertRaises(ValueError):
            s.scan(json.dumps({'authorization': 'Bearer fixture-token'}).encode())
        authorization['decision'] = 'Bearer ' + 'abcdefghijklmnopqrstuv'
        with self.assertRaises(ValueError):
            s.scan(json.dumps({'authorization': authorization}).encode())

    def test_sanitize_before_scan_preserves_literals_and_numbers(self):
        s = load('sanitize_publication', 'sanitize-publication.py')
        body = b'{"user_id":"account-fixture", "usage":{"cost":0.123456789012345678901},"choices":[{"message":{"content":"literal  \\n user_id unchanged"}}]}'
        raw = json.dumps({'body_base64': base64.b64encode(body).decode(), 'headers': {'Set-Cookie':'fixture-cookie'}}).encode()
        clean, removed = s.sanitize_bytes(raw)
        parsed = json.loads(clean)
        decoded = base64.b64decode(parsed['body_base64'])
        self.assertNotIn(b'account-fixture', decoded)
        self.assertNotIn(b'fixture-cookie', clean)
        self.assertIn(b'0.123456789012345678901', decoded)
        self.assertEqual(json.loads(body)['choices'], json.loads(decoded)['choices'])
        self.assertEqual(s.sanitize_bytes(clean)[0], clean)
        self.assertEqual(set(removed), {'account-fixture', 'fixture-cookie'})

    def test_verdict_requires_complete_plan_and_software(self):
        p = load('publication', 'publish.py')
        def row(judge, delta=6, preference='skill', critical=False):
            return dict(case='artificial', route=0, judge=judge,
                        detection_baseline=80, detection_skill=80-delta,
                        preference=preference, baseline_critical=False, skill_critical=critical)
        rows = [row(j) for j in ('jev', 'astra', 'opus')]
        self.assertEqual(p.verdict(rows, 1, 1, True)['status'], 'aceita')
        self.assertEqual(p.verdict(rows, 2, 1, True)['status'], 'inconclusivo')
        self.assertEqual(p.verdict(rows, 1, 1, False)['status'], 'inconclusivo')
        self.assertEqual(p.verdict([row(j, 0) for j in ('jev', 'astra', 'opus')], 1, 1, True)['status'], 'rejeitada')
        self.assertEqual(p.verdict([row(j, 4) for j in ('jev', 'astra', 'opus')], 1, 1, True)['status'], 'inconclusivo')
        self.assertEqual(p.verdict([row(j, critical=True) for j in ('jev', 'astra', 'opus')], 1, 1, True)['status'], 'rejeitada')
        self.assertEqual(p.verdict([row(j, preference='baseline') for j in ('jev', 'astra', 'opus')], 1, 1, True)['status'], 'rejeitada')
        with self.assertRaises(ValueError):
            p.verdict(rows + rows[:1], 1, 1, True)

    def test_scan_decodes_bodies_without_modifying_output(self):
        s = load('sanitize_publication', 'sanitize-publication.py')
        raw = json.dumps({'body_base64':base64.b64encode(b'Bearer ' + b'abcdefghijklmnopqrstuv').decode()}).encode()
        with self.assertRaises(ValueError):
            s.scan(raw)
        clean, _ = s.sanitize_bytes(b'{"text":"user_id literal", "scores":[3.20,0]}')
        self.assertEqual(clean, b'{"text":"user_id literal", "scores":[3.20,0]}')
        s.scan(clean)

    def test_measured_duration_and_software_receipt(self):
        p = load('publication', 'publish.py')
        records = {'fixture': ({'phase':'generation'}, {'started_at':'2026-01-01T00:00:00+00:00',
                   'finished_at':'2026-01-01T00:00:03+00:00','elapsed_seconds':2.5})}
        duration = p.durations(records)
        self.assertEqual(duration['janela_observada_segundos'], 3)
        self.assertEqual(duration['soma_chamadas_segundos_conhecidos'], 2.5)
        self.assertFalse(p.software_passed({}))
        suites = [{'suite':n, 'passed':1, 'exit_code':0} for n in
                  ('test_humanizar.py', 'test_generation_eval.py', 'test_objetivo.py', 'test_schedule_run.py')]
        self.assertTrue(p.software_passed({'suites':suites}))
        suites[0]['exit_code'] = 1
        self.assertFalse(p.software_passed({'suites':suites}))

    def test_missing_calls_and_invalid_outputs_remain_explicit(self):
        p = load('publication', 'publish.py')
        config = {'cases':[{'id':'fixture'}], 'routes':[{}]}
        blinds = {'fixture':{'groups':[['p0']]}}
        records = {'g.fixture.r00.baseline':({'phase':'generation'}, {'status':'invalid_response', 'text':'preservado', 'validation_issues':['truncated']})}
        inv = p.failure_inventory(config, records, blinds)
        self.assertEqual(inv['chamadas_planejadas'], 5)
        self.assertEqual(len(inv['chamadas_ausentes']), 4)
        self.assertEqual(inv['registros_nao_completos'][0]['slot'], 'g.fixture.r00.baseline')
        self.assertEqual(inv['registros_nao_completos'][0]['categorias'], ['truncated'])

    def test_hash_chain_sanitization_is_memory_only(self):
        p = load('publication', 'publish.py')
        s = load('sanitize_publication', 'sanitize-publication.py')
        a = load('aggregate_tests', 'analysis/agregar_objetivo.py')
        modules = a.load_modules(ROOT/'execution/frozen/runner')
        g, store = modules['generation_eval'], modules['eval_store']
        call = dict(slot='g.fixture.r00.baseline', phase='generation', api='chat', model='fixture/model',
                    endpoint={'name':'Fixture | fixture/model', 'provider_name':'Fixture'}, payload={'max_tokens':30})
        intent = dict(call=call, execution_mode='OFFLINE_FAKE', started_at='2026-01-01T00:00:00+00:00')
        body = b'{"user_id":"fixture-private-id","id":"fixture-generation","model":"fixture/model","provider":"Fixture","usage":{"cost":0.123456789012345678901,"prompt_tokens":10,"completion_tokens":20},"choices":[{"finish_reason":"stop","message":{"content":"Literal  \\ntexto"}}]}'
        raw = dict(body_base64=base64.b64encode(body).decode(), http_status=200,
                   received_at='2026-01-01T00:00:01+00:00', elapsed_seconds=1)
        result = store.derive(call, intent, raw)
        self.assertEqual(result['status'], 'completed')
        prefix = 'evidence/requests/g.fixture.r00.baseline/'
        probe = 'evidence/frozen/probe-evidence/fixture.json'
        files = {prefix+'intent.json':g.encoded(intent), prefix+'raw.json':g.encoded(raw),
                 prefix+'result.json':g.encoded(result), probe:b'{"account_id":"fixture-account"}',
                 'evidence/judge-inputs/fixture.json':g.encoded({'payload':{'unchanged':True},'raw_sha256':{call['slot']:result['raw_sha256']}}),
                 'evidence/manifest.json':g.encoded({'sha256':{'frozen/probe-evidence/fixture.json':'placeholder'}})}
        original = dict(files)
        changes, removed = p.transform_evidence(files, modules, s)
        self.assertEqual(original[prefix+'raw.json'], g.encoded(raw))
        projected = json.loads(files[prefix+'result.json'])
        self.assertEqual(projected['text'], result['text'])
        self.assertEqual(projected['telemetry'], result['telemetry'])
        self.assertNotEqual(projected['raw_sha256'], result['raw_sha256'])
        self.assertEqual(json.loads(files['evidence/judge-inputs/fixture.json'])['raw_sha256'][call['slot']], projected['raw_sha256'])
        self.assertEqual(json.loads(files['evidence/manifest.json'])['sha256']['frozen/probe-evidence/fixture.json'], p.sha(files[probe]))
        for data in files.values():
            s.scan(data, removed)
        self.assertEqual(len(changes), 5)

    def test_h_cycle_weights_pairs_not_observed_configurations(self):
        p = load('publication', 'publish.py')
        rows = [dict(case=case, route=route, judge=j, detection_baseline=80,
                     detection_skill=80-delta, preference='empate', baseline_critical=False, skill_critical=False)
                for case,route,delta in [('a',0,0),('b',0,0),('a',1,12)] for j in p.JUDGES]
        self.assertEqual(p.verdict(rows, 4, 3, True)['delta_h'], 4)

    def test_empty_readme_has_24_links_and_inconclusive_status(self):
        p = load('publication', 'publish.py')
        a = load('aggregate_tests', 'analysis/agregar_objetivo.py')
        empty = a.compare_pairs([])
        config = {'cases':[{'id':f'fixture-{i:02}', 'title':'Caso artificial'} for i in range(24)],
                  'routes':[], 'judges':[{'name':'astra','model':'artificial/astra'}, {'name':'opus','model':'artificial/opus'}]}
        objective = dict(tokens={'total':empty}, tempo={'geracao_api':empty,'consultas_locais':{}}, cobertura={},
                         erros={'registros':[],'falhas_de_entrega':[],'grupos_bloqueados':[]},
                         por_juiz={j:{'cobertura':{'observado':0}} for j in p.JUDGES})
        decision = p.verdict([],456,0,False)
        failures = {'chamadas_ausentes':[],'chamadas_planejadas':1344,'registros_nao_completos':[]}
        text = p.readme(config,objective,{},decision,p.durations({}),{}, {},failures).decode()
        self.assertIn('Situação: inconclusivo',text)
        self.assertEqual(text.count('](experiments/'),24)
        self.assertIn('indisponível',text)
        self.assertNotIn('\u2014', text)

    def test_manifest_verification_detects_tamper_and_extra_file(self):
        import tempfile
        p = load('publication', 'publish.py')
        files = {'fixture.txt':b'artificial'}
        p.freeze(files)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name,data in files.items():
                (root/name).write_bytes(data)
            self.assertEqual(p.verify(root),1)
            (root/'fixture.txt').write_bytes(b'alterado')
            with self.assertRaises(ValueError):
                p.verify(root)
            (root/'fixture.txt').write_bytes(b'artificial')
            (root/'extra.txt').write_bytes(b'extra')
            with self.assertRaises(ValueError):
                p.verify(root)
        with self.assertRaises(ValueError):
            p.safe_path(ROOT, 'private/inference-key.json')
        with self.assertRaises(ValueError):
            p.safe_path(ROOT, '../escape')

if __name__ == '__main__':
    unittest.main()
