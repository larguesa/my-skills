"""Offline renderer contracts: synthetic fixtures, never model calls."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

TESTS = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS / 'scripts'))
import contos as c
import generos as g
try:
    import relatorio_generos as r
except ModuleNotFoundError:
    r = None


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.run = self.base / 'evidence' / 'run-20261002'
        self.frozen = self.run / 'frozen'
        self.frozen.mkdir(parents=True)
        bundle = (TESTS / 'frozen/skill-bundle.txt').read_bytes()
        (self.frozen / 'skill-bundle.txt').write_bytes(bundle)
        self.config = copy.deepcopy(c.load(TESTS / 'frozen/config.json'))
        self.config.update(budget_usd=None, max_tokens=4096, judge_max_tokens=16384,
                           blind_seed='20261002-generos-v1',
                           cases=c.load(TESTS / 'experiments/cases.json')['cases'],
                           sha256={'skill-bundle.txt': hashlib.sha256(bundle).hexdigest()})
        self.config.pop('cumulative_pilot_cap_usd', None)
        self.config.pop('prior_usage_usd', None)
        save(self.frozen / 'config.json', self.config)
        self.calls = g.generation_calls(self.config, self.frozen)
        self.output = self.base / 'published-tests'
        self.output.mkdir()
        (self.output / 'README.md').write_bytes((TESTS / 'README.md').read_bytes())
        for name in ('chave', 'bolo'):
            target = self.output / 'experiments' / name / 'REPORT.md'
            target.parent.mkdir(parents=True)
            target.write_bytes((TESTS / 'experiments' / name / 'REPORT.md').read_bytes())
        self.historical = {name: (self.output / 'experiments' / name / 'REPORT.md').read_bytes()
                           for name in ('chave', 'bolo')}

    def renderer(self):
        self.assertIsNotNone(r, 'Evidence-only genre renderer is missing')
        return r

    def record(self, index, text='Linha | <TOKEN> & fim\n```python\nprint("ok")\n```', **changes):
        call = self.calls[index]
        response = dict(id='fixture-' + call['id'], model=call['model'], provider='Fixture',
                        choices=[dict(finish_reason='stop', message=dict(content=text))],
                        usage=dict(cost=0.125, prompt_tokens=20, completion_tokens=10))
        record = dict(call, status='completed', response=response, edited=text,
                      finish_reason='stop', usage=response['usage'], cost_usd='0.125',
                      elapsed_seconds=2.5)
        record.update(changes)
        return record

    def evidence(self, records):
        save(self.run / 'generation-plan.json', dict(schema=1, budget_usd=None, calls=self.calls))
        save(self.run / 'generation-state.json', dict(schema=1, records=records))
        for record in records:
            save(self.run / 'requests' / (record['id'] + '.json'), record)

    def test_partial_reports_cover_24_cases_19_rows_and_preserve_history(self):
        self.evidence([self.record(0)])
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['expected'], dict(cases=24, configurations=19, candidates=912,
                                                   pairs=456, judge_pairs=1368))
        self.assertEqual(summary['generation']['completed'], 1)
        self.assertEqual(summary['generation']['missing'], 911)
        self.assertEqual(summary['generation']['complete_pairs'], 0)
        reports = sorted(self.output / 'experiments' / case['id'] / 'REPORT.md' for case in self.config['cases'])
        self.assertEqual(len(reports), 24)
        for report in reports:
            text = report.read_text(encoding='utf-8')
            self.assertEqual(len([line for line in text.splitlines() if line.startswith('| Configuração: ')]), 19)
            self.assertIn('| Jev | Astra | Opus 5.5 |', text)
            self.assertIn('Revisão humana: pendente', text)
            self.assertIn('pendente', text)
        first = (self.output / 'experiments' / self.config['cases'][0]['id'] / 'REPORT.md').read_text()
        self.assertIn('Linha \\| &lt;TOKEN&gt; &amp; fim<br>\\`\\`\\`python', first)
        self.assertIn(self.config['cases'][0]['prompt'], first)
        self.assertIn('requests/', first)
        readme = (self.output / 'README.md').read_text()
        self.assertIn('| Jev | 60.29 → 52.63 (-7.66 pontos)', readme)
        self.assertLess(readme.index('## Ampliação 20261002'), readme.index('## Índice dos experimentos'))
        index = readme.split('## Índice dos experimentos', 1)[1].split('## ', 1)[0]
        self.assertEqual(len(re.findall(r'\]\([^\n]*REPORT\.md\)', index)), 26)
        self.assertNotIn('teto de gasto específico', readme)
        for name, original in self.historical.items():
            self.assertEqual((self.output / 'experiments' / name / 'REPORT.md').read_bytes(), original)
        machine = c.load(self.run / 'report-summary.json')
        self.assertEqual(summary, machine)
        self.assertEqual(self.renderer().render(self.run, self.output), summary)
    def test_integrity_fails_closed_before_writing_on_duplicates_and_tampering(self):
        renderer = self.renderer()
        record = self.record(0)
        for kind in ('duplicate', 'metadata', 'edited', 'durable_mismatch'):
            with self.subTest(kind=kind):
                self.evidence([record])
                if kind == 'duplicate':
                    save(self.run / 'generation-state.json', dict(records=[record, record]))
                elif kind == 'metadata':
                    changed = copy.deepcopy(record)
                    changed['payload']['messages'][1]['content'] = 'Tampered prompt'
                    self.evidence([changed])
                elif kind == 'edited':
                    changed = dict(record, edited='Invented replacement')
                    self.evidence([changed])
                else:
                    save(self.run / 'requests' / (record['id'] + '.json'), dict(record, cost_usd='88'))
                before = (self.output / 'README.md').read_bytes()
                with self.assertRaises(ValueError):
                    renderer.render(self.run, self.output)
                self.assertEqual((self.output / 'README.md').read_bytes(), before)
                self.assertFalse((self.output / 'experiments' / self.config['cases'][0]['id'] / 'REPORT.md').exists())

    def test_case_phase_states_missing_cost_and_pending_denominators(self):
        original, skill = self.record(0), self.record(1, status='request_failed_billing_uncertain')
        for field in ('response', 'edited', 'finish_reason', 'usage', 'cost_usd'):
            skill.pop(field, None)
        case_id = self.config['cases'][0]['id']
        save(self.run / ('generation-' + case_id + '-state.json'), dict(records=[original, skill]))
        save(self.run / ('generation-' + case_id + '-plan.json'), dict(calls=self.calls[:38]))
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['generation'], dict(completed=1, failed=1, missing=910, complete_pairs=0))
        costs = summary['accounting']['generation']
        self.assertEqual((costs['known_usd'], costs['known_calls'], costs['unknown_calls']), ('0.125', 1, 1))
        report = (self.output / 'experiments' / case_id / 'REPORT.md').read_text()
        self.assertIn('1/38 candidatos', report)
        self.assertIn('0/19 pares', report)
        self.assertIn('desconhecido', report)
        self.assertIn(r.cell('🟥 reprovado: word_count'), report)
        readme = (self.output / 'README.md').read_text()
        line = next(line for line in readme.splitlines() if '[Notícia sobre bibliotecas]' in line)
        self.assertIn('| ⏸️ parcial | 1 | 0 | 0.125 + desconhecido | 5.0 |', line)
        self.assertIn('1/912', readme)
        self.assertNotIn('24 novos casos preparados, sem geração paga ou resultados', readme)
    def judge_fixture(self, judges=('jev', 'astra', 'opus')):
        records = [self.record(0), self.record(1, text='Outro texto | literal')]
        self.evidence(records)
        case_id = self.config['cases'][0]['id']
        chunks = g.anonymous_chunks(self.config, dict(records=records), case_id)
        chunk = chunks[0]
        state, mapping = chunk['state'], chunk['mapping']
        suffix = case_id + '-chunk-00'
        save(self.run / ('mapping-' + case_id + '.json'), dict(chunks=chunks, note='PRIVATE mapping'))
        tids = {meta['arm']: tid for tid, meta in mapping.items()}
        pair_id = next(iter(state['pares']))
        choice = next(letter for letter, tid in state['pares'][pair_id].items() if tid == tids['skill'])
        data = dict(deteccao={tids['original']: 20, tids['skill']: 80}, preferencia={pair_id: choice},
                    qualidade={tids['original']: dict(naturalidade=90, clareza=95, adequacao=92, correcao=99,
                                                      critico=True, justificativa='<assert> | incorreto'),
                               tids['skill']: dict(naturalidade=70, clareza=80, adequacao=85, correcao=90,
                                                   critico=False, justificativa='Descrição fiel')})
        for judge in judges:
            call = next(call for call in g.judge_calls(self.config, state, case_id, 0) if call['judge'] == judge)
            if judge == 'jev':
                request = g.decisions_payload(state)
                answers = {}
                for qid, question in request['questions'].items():
                    if question['type'] == 'score':
                        tid, dimension = qid.rsplit('_', 1)
                        answers[qid] = dict(type='score', score=data['qualidade'][tid][dimension] / 25)
                    elif question['type'] == 'noul':
                        answers[qid] = dict(type='noul', noul=data['deteccao'][qid] / 100)
                    else:
                        selected = ('yes' if data['qualidade'][qid[:-8]]['critico'] else 'no') if qid.endswith('_critico') else choice
                        answers[qid] = dict(type='choice', choice=selected)
                response = dict(id='native-fixture', model='typesafe/jev-1.13', answers=answers,
                                usage=dict(cost=0.03, input_tokens=10, output_tokens=10))
                judgment = g.validate_judge(response, state, True)
                record = dict(call, status='completed', response=response, usage=response['usage'],
                              judgment=judgment, cost_usd='0.03', elapsed_seconds=4)
            else:
                route = next(route for route in self.config['judges'] if route['name'] == judge)
                response = dict(id=judge + '-fixture', model=route['model'], provider='Fixture',
                                choices=[dict(finish_reason='stop', message=dict(content=json.dumps(data, ensure_ascii=False)))],
                                usage=dict(cost=0.04, prompt_tokens=10, completion_tokens=10))
                record = dict(call, status='completed', response=response, edited=response['choices'][0]['message']['content'],
                              finish_reason='stop', usage=response['usage'], cost_usd='0.04', elapsed_seconds=5)
                judgment = g.validate_judge(data, state)
                save(self.run / ('judgment-' + judge + '-' + suffix + '.json'), judgment)
            record['judgment'] = judgment
            record['quality_aggregate'] = {tid: g.aggregate_quality(quality) for tid, quality in judgment['qualidade'].items()}
            save(self.run / (judge + '-' + suffix + '-state.json'), dict(records=[record]))
        return state, mapping, data

    def test_three_judges_native_score_caps_and_independent_preference(self):
        self.judge_fixture()
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['judgments']['judge_pairs_observed'], 3)
        for judge in ('jev', 'astra', 'opus'):
            data = summary['judgments'][judge]
            self.assertEqual(data['preference'], dict(skill=1, original=0, empate=0, n=1, missing=455))
            self.assertEqual(data['fields']['correcao']['original'], dict(mean=25.0, n=1, missing=455))
            self.assertEqual(data['fields']['correcao_raw']['original']['mean'], 99.0)
            self.assertEqual(data['fields']['total']['original']['mean'], 49.0)
            self.assertEqual(data['fields']['total_raw']['original']['mean'], 94.0)
            self.assertEqual(data['fields']['deteccao']['skill']['mean'], 80.0)
        report = (self.output / 'experiments' / self.config['cases'][0]['id'] / 'REPORT.md').read_text()
        for word in ('naturalidade', 'clareza', 'adequacao', 'correcao', 'impressão IA', 'prefere skill',
                     'justificativa indisponível', 'Score nativo', 'bruto 99.00', 'limitado 25.00', 'limitado 49.00'):
            self.assertIn(word, report)
        self.assertIn('&lt;assert&gt; \\| incorreto', report)
        self.assertEqual(summary['accounting']['jev']['known_usd'], '0.03')
        self.assertEqual(summary['accounting']['astra']['known_usd'], '0.04')
        readme = (self.output / 'README.md').read_text()
        self.assertIn('1/1 (100.0%)', readme)
        self.assertIn('455/456', readme)

    def test_rejects_changed_mapping_input_score_copy_and_raw_score_range(self):
        renderer = self.renderer()
        for kind in ('mapping', 'judge_input', 'score_copy', 'score_range'):
            with self.subTest(kind=kind):
                self.judge_fixture(judges=('astra',))
                suffix = self.config['cases'][0]['id'] + '-chunk-00'
                if kind == 'mapping':
                    path = self.run / ('mapping-' + self.config['cases'][0]['id'] + '.json')
                    payload = c.load(path)
                    mapping = payload['chunks'][0]['mapping']
                    mapping[next(iter(mapping))]['arm'] = 'wrong'
                elif kind == 'judge_input':
                    path = self.run / ('astra-' + suffix + '-state.json')
                    payload = c.load(path)
                    payload['records'][0]['payload']['messages'][1]['content'] = '{}'
                elif kind == 'score_copy':
                    path = self.run / ('judgment-astra-' + suffix + '.json')
                    payload = c.load(path)
                    payload['deteccao'][next(iter(payload['deteccao']))] = 99
                else:
                    path = self.run / ('astra-' + suffix + '-state.json')
                    payload = c.load(path)
                    record = payload['records'][0]
                    data = json.loads(record['edited'])
                    data['deteccao'][next(iter(data['deteccao']))] = 101
                    record['edited'] = json.dumps(data)
                    record['response']['choices'][0]['message']['content'] = record['edited']
                save(path, payload)
                with self.assertRaises(ValueError):
                    renderer.render(self.run, self.output)
    def test_actual_runner_durable_native_interface_score_decimal_and_accounting(self):
        from unittest.mock import patch
        providers = {route['endpoint']['tag']: route['endpoint']['provider_name']
                     for route in [*self.config['routes'], *self.config['judges']]}
        def chat_send(payload, key):
            if payload['messages'][0]['content'] == g.JUDGE:
                anon = json.loads(payload['messages'][1]['content'])
                data = dict(deteccao={tid: 30 for tid in anon['textos']},
                            preferencia={pid: 'empate' for pid in anon['pares']},
                            qualidade={tid: dict(naturalidade=75, clareza=75, adequacao=75, correcao=75,
                                               critico=False, justificativa='Fixture explícita') for tid in anon['textos']})
                text = json.dumps(data)
            else:
                text = 'Fixture do candidato; não é uma saída real de modelo.'
            return dict(id='fixture-' + c.b.digest(payload), model=payload['model'],
                        provider=providers[payload['provider']['only'][0]],
                        choices=[dict(finish_reason='stop', message=dict(content=text))],
                        usage=dict(cost=0.001, prompt_tokens=10, completion_tokens=10))
        def decisions_send(payload, key):
            answers = {}
            for qid, question in payload['questions'].items():
                kind = question['type']
                if kind == 'score': answers[qid] = dict(type=kind, score=3.99, confidence=0.01)
                elif kind == 'noul': answers[qid] = dict(type=kind, noul=0.2)
                else: answers[qid] = dict(type=kind, choice='no' if qid.endswith('_critico') else 'empate')
            return dict(id='fixture-native', model='typesafe/jev-1.13-20260917', provider='TypeSafe',
                        answers=answers, usage=dict(cost=0.002, input_tokens=10, output_tokens=10))
        with patch.object(g.urllib.request, 'urlopen', side_effect=AssertionError('Network forbidden')):
            pilot = g.execute(self.frozen / 'config.json', self.run, 'fake-key', pilot=True,
                              send=chat_send, decisions_send=decisions_send)
        self.assertEqual(pilot['judge_calls'], 3)
        probes = dict(records=[dict(cost_usd='0.1', elapsed_seconds=1, id='probe-' + str(i)) for i in range(19)]
                             + [dict(cost_usd='0.000018018', elapsed_seconds=0.6, id='probe-score')])
        accounting = self.base / 'probe-accounting.json'
        save(accounting, probes)
        summary = self.renderer().render(self.run, self.output, accounting=accounting)
        self.assertEqual(summary['judgments']['judge_pairs_observed'], 3)
        self.assertEqual(summary['judgments']['jev']['fields']['naturalidade']['skill']['mean'], 99.75)
        self.assertEqual(summary['methodology']['planned_judge_calls'], 432)
        self.assertEqual(summary['accounting']['probes_extra']['known_usd'], '1.900018018')
        self.assertEqual(summary['accounting']['probes_extra']['calls'], 20)
        native_file = next(path for path in (self.run / 'requests').glob('*.json')
                           if c.load(path).get('api') == 'decisions')
        native = c.load(native_file)
        native['quality_aggregate'][next(iter(native['quality_aggregate']))]['total'] = 1
        save(native_file, native)
        with self.assertRaisesRegex(ValueError, 'mismatch|correspondence'):
            self.renderer().render(self.run, self.output)
    def test_failed_judge_and_null_candidate_are_explicit_not_scored(self):
        self.judge_fixture(judges=('astra',))
        case_id = self.config['cases'][0]['id']
        phase = 'astra-' + case_id + '-chunk-00'
        judge_file = self.run / (phase + '-state.json')
        judge = c.load(judge_file)
        judge['records'][0]['status'] = 'billing_uncertain'
        for key in ('response', 'edited', 'usage', 'cost_usd', 'judgment', 'quality_aggregate'):
            judge['records'][0].pop(key, None)
        save(judge_file, judge)
        (self.run / ('judgment-' + phase + '.json')).unlink()
        # A third failed candidate has no returned text; do not turn None into prose.
        invalid = self.record(2, status='invalid_response', edited=None)
        invalid['response']['choices'] = []
        self.evidence([self.record(0), self.record(1, text='Outro texto | literal'), invalid])
        # Refresh the saved partial snapshot to the runner's actual current map.
        save(self.run / ('mapping-' + case_id + '.json'),
             dict(chunks=g.anonymous_chunks(self.config, c.load(self.run / 'generation-state.json'), case_id)))
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['judgments']['astra']['preference']['n'], 0)
        self.assertEqual(summary['judgments']['astra']['fields']['naturalidade']['original']['mean'], None)
        self.assertEqual(summary['accounting']['astra']['unknown_calls'], 1)
        text = (self.output / 'experiments' / case_id / 'REPORT.md').read_text()
        self.assertIn(r.cell('billing_uncertain'), text)
        self.assertIn(r.cell('invalid_response'), text)
        self.assertIn('sem texto retornado', text)
        self.assertNotIn('None', text)

    def test_markdown_literal_escaping_dynamic_fence_and_probe_rejection(self):
        renderer = self.renderer()
        self.assertEqual(renderer.cell('a\\|b `c` *d* [x] <tag>\nlinha'),
                         'a\\\\\\|b \\`c\\` \\*d\\* \\[x\\] &lt;tag&gt;<br>linha')
        prompt = 'Texto\n```python\nx = 1\n```\n```` literal\n'
        fenced = renderer.fence(prompt)
        self.assertTrue(fenced.startswith('`````text\n'))
        self.assertEqual(fenced.split('\n', 1)[1][:-5], prompt)
        self.evidence([self.record(0)])
        for extra in (dict(records=[dict(id='same', cost_usd='1'), dict(id='same', cost_usd='1')]),
                      dict(records=[dict(id=self.calls[0]['id'], cost_usd='1')]),
                      dict(records=[dict(cost_usd='3', response={'usage': {'cost': 4}})])):
            with self.assertRaises(ValueError):
                renderer.render(self.run, self.output, accounting=extra)

    def test_literal_support_is_separate_and_absence_never_red_failure(self):
        self.evidence([self.record(0)])
        summary = self.renderer().render(self.run, self.output)
        self.assertIn('factual_support', summary)
        self.assertTrue(summary['factual_support']['original'])
        report = (self.output / 'experiments' / self.config['cases'][0]['id'] / 'REPORT.md').read_text()
        self.assertIn('apoio literal', report)
        self.assertNotIn('🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥 0/0', report)

    def test_invalid_native_usage_preserves_returned_text_and_exact_reason(self):
        record = self.record(0, text='Texto retornado preservado sem conserto.', status='invalid_response',
                             usage_issues=['completion_exceeds_max_tokens'])
        record['response']['usage']['completion_tokens'] = 7530
        self.evidence([record])
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['generation']['failed'], 1)
        report = (self.output / 'experiments' / self.config['cases'][0]['id'] / 'REPORT.md').read_text()
        self.assertIn('Texto retornado preservado sem conserto.', report)
        self.assertIn(r.cell('completion_exceeds_max_tokens'), report)
        self.assertIn('7530', report)
        self.assertIn('4096', report)

    def test_stop_during_resumed_generation_accepts_prior_missing_snapshot_only(self):
        self.judge_fixture()
        # Runner stops before refreshing mapping when billing becomes uncertain.
        stopped = self.record(4, status='billing_uncertain')
        records = [self.record(0), self.record(1, text='Outro texto | literal'),
                   self.record(2), self.record(3), stopped]
        self.evidence(records)
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['generation']['completed'], 4)
        self.assertEqual(summary['generation']['failed'], 1)
        self.assertEqual(summary['judgments']['judge_pairs_observed'], 3)

    def test_all_19_routes_and_3_judges_mark_case_complete_not_pending(self):
        self.evidence([self.record(index) for index in range(38)])
        case_id = self.config['cases'][0]['id']
        records = c.load(self.run / 'generation-state.json')['records']
        chunks = g.anonymous_chunks(self.config, dict(records=records), case_id)
        save(self.run / ('mapping-' + case_id + '.json'), dict(chunks=chunks))
        for chunk in chunks:
            state = chunk['state']
            for call in g.judge_calls(self.config, state, case_id, chunk['index']):
                data = dict(deteccao={tid: 30 for tid in state['textos']},
                            preferencia={pid: 'empate' for pid in state['pares']},
                            qualidade={tid: dict(naturalidade=75, clareza=75, adequacao=75, correcao=75,
                                               critico=False, justificativa='Fixture explícita') for tid in state['textos']})
                if call['judge'] == 'jev':
                    answers = {qid: dict(type=q['type'], **({'score': 3} if q['type'] == 'score' else
                               {'noul': 0.3} if q['type'] == 'noul' else {'choice': 'no' if qid.endswith('_critico') else 'empate'}))
                               for qid, q in call['payload']['questions'].items()}
                    response = dict(answers=answers, usage={'cost': 0.01})
                    judgment = g.validate_judge(response, state, True)
                    record = dict(call, response=response, usage=response['usage'])
                else:
                    text = json.dumps(data)
                    response = dict(choices=[dict(finish_reason='stop', message={'content': text})], usage={'cost': 0.01})
                    judgment = g.validate_judge(data, state)
                    record = dict(call, response=response, usage=response['usage'], edited=text, finish_reason='stop')
                record.update(status='completed', judgment=judgment, cost_usd='0.01',
                              quality_aggregate={tid: g.aggregate_quality(q) for tid, q in judgment['qualidade'].items()})
                phase = call['judge'] + '-' + case_id + '-chunk-' + str(chunk['index']).zfill(2)
                save(self.run / (phase + '-state.json'), dict(records=[record]))
        summary = self.renderer().render(self.run, self.output)
        self.assertEqual(summary['judgments']['judge_pairs_observed'], 57)
        line = next(line for line in (self.output / 'README.md').read_text().splitlines() if '[Notícia sobre bibliotecas]' in line)
        self.assertIn('| ✅ concluído | 38 | 19 |', line)


if __name__ == '__main__':
    unittest.main()
