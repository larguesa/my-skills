"""Offline: desenho A/B, anonimização e validação, não qualidade literária."""
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import contos as c


class StoryTests(unittest.TestCase):
    def test_first_generation_changes_only_skill_context(self):
        config = c.checked_config(Path(__file__).parent / 'frozen/config.json')
        calls = c.generation_calls(config, Path(__file__).parent / 'frozen')
        self.assertEqual(len(calls), len(config['routes']) * len(config['cases']) * 2)
        for original, skill in zip(calls[::2], calls[1::2]):
            self.assertEqual(original['payload']['messages'][1], skill['payload']['messages'][1])
            self.assertTrue(skill['payload']['messages'][0]['content'].startswith(original['payload']['messages'][0]['content']))
            for field in ('model', 'provider', 'reasoning', 'max_tokens', 'stream'):
                self.assertEqual(original['payload'][field], skill['payload'][field])
            self.assertNotIn('SKILL E REFERÊNCIAS', original['payload']['messages'][0]['content'])
            self.assertNotIn('SOUL.md', json.dumps(original['payload']))

    def test_judge_fails_closed_on_missing_ids_nan_and_invalid_choices(self):
        state = {'textos': {'t000': 'texto', 't001': 'outro'}, 'pares': {'p000': {'A': 't000', 'B': 't001'}}}
        valid = {'deteccao': {'t000': 50, 't001': 20}, 'preferencia': {'p000': 'empate'}}
        self.assertEqual(c.validate_judge(valid, state), valid)
        for bad in [dict(valid, deteccao={'t000': 50}), dict(valid, deteccao={'t000': float('nan'), 't001': 20}),
                    dict(valid, preferencia={'p000': 'original'}), dict(valid, deteccao={'t000': True, 't001': 20})]:
            with self.assertRaises(ValueError):
                c.validate_judge(bad, state)

    def test_native_decisions_are_not_chat_and_preserve_real_scores(self):
        state = {'prompt': 'conto', 'textos': {'t000': 'texto', 't001': 'outro'}, 'pares': {'p000': {'A': 't000', 'B': 't001'}}}
        payload = c.decisions_payload(state)
        self.assertNotIn('messages', payload)
        self.assertEqual(payload['model'], 'typesafe/jev-1.13')
        self.assertEqual(set(payload['questions']), {'t000', 't001', 'p000'})
        response = {'answers': {'t000': {'type': 'noul', 'noul': 0.9}, 't001': {'type': 'noul', 'noul': 0.1},
                                'p000': {'type': 'choice', 'choice': 'B'}}}
        self.assertEqual(c.validate_judge(response, state, True), {'deteccao': {'t000': 90, 't001': 10}, 'preferencia': {'p000': 'B'}})

    def test_freeze_detects_changed_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / 'input.txt').write_text('antes')
            config = {'sha256': {'input.txt': c.hashlib.sha256(b'antes').hexdigest()}}
            (p / 'config.json').write_text(json.dumps(config))
            c.checked_config(p / 'config.json')
            (p / 'input.txt').write_text('depois')
            with self.assertRaises(ValueError):
                c.checked_config(p / 'config.json')

    def test_effective_plan_keeps_pairs_and_preserves_completed_outputs(self):
        import continuar
        tests = Path(__file__).parent
        config = c.checked_config(tests / 'frozen/config.json')
        original = c.generation_calls(config, tests / 'frozen')
        effective = continuar.amended_calls(original, tests / 'results')
        self.assertEqual(effective, c.load(tests / 'results/generation-plan.json')['calls'])
        changed = [(a, b) for a, b in zip(original, effective) if a['id'] != b['id']]
        self.assertEqual(len(changed), 8)
        for before, after in changed:
            self.assertEqual(before['case'], 'bolo')
            self.assertIn(before['model'], ('xiaomi/mimo-v2.6-pro', 'xiaomi/mimo-v2.6-flash'))
            for field in ('messages', 'model', 'reasoning', 'max_tokens'):
                self.assertEqual(before['payload'][field], after['payload'][field])
        for original_arm, skill_arm in zip(effective[::2], effective[1::2]):
            self.assertEqual(original_arm['payload']['provider'], skill_arm['payload']['provider'])
        current = {r['id']: r for r in c.load(tests / 'results/generation-state.json')['records'] if r['status'] == 'completed'}
        for file in ('generation-attempt1.json', 'generation-attempt4.json', 'generation-attempt5.json'):
            for record in c.load(tests / 'results/attempts' / file)['records']:
                if record['status'] == 'completed':
                    self.assertEqual(current[record['id']], record)

    def test_renderer_rejects_request_metadata_tampering(self):
        import copy
        import relatorio
        from unittest.mock import patch
        original_load = relatorio.load
        state = copy.deepcopy(original_load(Path(__file__).parent / 'results/generation-state.json'))
        state['records'][0]['payload']['messages'][1]['content'] = 'Incorrect recorded request'
        with patch.object(relatorio, 'load', side_effect=lambda path: state if Path(path).name == 'generation-state.json' else original_load(path)):
            with self.assertRaisesRegex(ValueError, 'request metadata'):
                relatorio.results()

    def test_markdown_cells_preserve_text_without_extra_columns(self):
        import relatorio
        self.assertEqual(relatorio.cell('A | B\n<teste> & fim'), 'A \\| B<br>&lt;teste&gt; &amp; fim')

    def test_story_tables_have_one_detection_column_per_judge(self):
        import relatorio
        _, _, tables = relatorio.results()
        rendered = relatorio.table_blocks(tables)
        header = '| Modelo | Resposta original | Resposta com skill | Detecção Jev | Detecção Astra | Detecção Opus 5.5 |'
        self.assertEqual(rendered.count(header), 2)
        rows = [line for line in rendered.splitlines() if line.startswith('| ') and line != header]
        self.assertEqual(len(rows), 38)
        for line, row in zip(rows, [row for _, entries in tables for row in entries]):
            columns = line.split(' | ')
            self.assertEqual(len(columns), 6)
            self.assertEqual(columns[1], relatorio.cell(row['original']))
            self.assertEqual(columns[2], relatorio.cell(row['skill']))
        self.assertIn('| 64.0 → 58.0; prefere original | 86.0 → 78.0; prefere com skill | 60.0 → 45.0; prefere com skill |', rendered)

    def test_aggregate_results_keeps_preferences_separate_from_detection(self):
        import relatorio
        self.assertTrue(callable(getattr(relatorio, 'aggregate_results', None)), 'Missing judgment aggregation')
        rows = [{'detection': {name: dict(original=a, skill=b, preference=p)
                              for name in ('Jev', 'Astra', 'Opus')}}
                for a, b, p in ((80, 20, 'original'), (10, 70, 'skill'), (50, 50, 'empate'))]
        result = relatorio.aggregate_results([({}, rows)])
        for stats in result.values():
            self.assertEqual(stats['pairs'], 3)
            self.assertAlmostEqual(stats['original_mean'], 140 / 3)
            self.assertAlmostEqual(stats['skill_mean'], 140 / 3)
            self.assertEqual(stats['delta_mean'], 0)
            self.assertEqual((stats['lower'], stats['equal'], stats['higher']), (1, 1, 1))
            self.assertEqual((stats['skill'], stats['original'], stats['empate']), (1, 1, 1))

    def test_aggregate_results_rejects_empty_sample(self):
        import relatorio
        self.assertTrue(callable(getattr(relatorio, 'aggregate_results', None)), 'Missing judgment aggregation')
        with self.assertRaisesRegex(ValueError, 'empty'):
            relatorio.aggregate_results([])

    def test_renderer_puts_consolidated_results_before_story_tables(self):
        import relatorio
        from unittest.mock import patch
        documents = {}
        with patch.object(Path, 'write_text', autospec=True,
                          side_effect=lambda path, text, **kwargs: documents.setdefault(path.name, text)):
            relatorio.render()
        for name in ('README.md', 'REPORT.md'):
            text = documents[name]
            self.assertIn('## Resultados consolidados', text)
            self.assertLess(text.index('## Resultados consolidados'), text.index('## Como ler as colunas de detecção'))
            self.assertLess(text.index('## Resultados consolidados'), text.index('## A chave no ônibus'))
            self.assertIn('114 julgamentos de pares', text)
            self.assertIn('228 índices individuais', text)
            self.assertIn('| Jev | 60.29 | 52.63 | -7.66 | 33 / 0 / 5 |', text)
            self.assertIn('| Astra | 84.45 | 72.61 | -11.84 | 34 / 0 / 4 |', text)
            self.assertIn('| Opus 5.5 | 65.26 | 51.18 | -14.08 | 36 / 1 / 1 |', text)
            self.assertIn('| Total (114 julgamentos) | 71/114 (62.3%) | 43/114 (37.7%) | 0/114 (0.0%) |', text)
            self.assertIn('| A chave no ônibus | 19 | 36/57 (63.2%) | 21/57 (36.8%) | 0/57 (0.0%) |', text)
            self.assertIn('| O bolo na portaria | 19 | 35/57 (61.4%) | 22/57 (38.6%) | 0/57 (0.0%) |', text)
            self.assertIn('| Entre 80 e 120 palavras | 34/38 | 36/38 |', text)
            self.assertIn('| Sem travessão longo | 36/38 | 34/38 |', text)
            self.assertIn('| Ambas as verificações | 33/38 | 33/38 |', text)

    def test_experiment_documents_preserve_all_real_pairs(self):
        import relatorio
        self.assertTrue(callable(getattr(relatorio, 'experiment_documents', None)),
                        'Missing per-experiment reports and summary index')
        _, records, tables = relatorio.results()
        documents = relatorio.experiment_documents(tables, records, [])
        self.assertEqual(set(documents), {'README.md', 'experiments/chave/REPORT.md',
                                         'experiments/bolo/REPORT.md'})
        self.assertIn('experiments/chave/REPORT.md', documents['README.md'])
        self.assertNotIn(tables[0][1][0]['original'], documents['README.md'])
        for case, rows in tables:
            report = documents['experiments/' + case['id'] + '/REPORT.md']
            self.assertIn(case['prompt'], report)
            self.assertIn('✅', report)
            self.assertIn('🟩', report)
            self.assertIn('avaliação humana', report.lower())
            self.assertIn('Custo original (USD)', report)
            self.assertIn('Tempo com skill (s)', report)
            self.assertEqual(report.count('| anthropic/claude-opus-5.5 (raciocínio ligado)'), 1)
            for row in rows:
                self.assertIn(relatorio.cell(row['original']), report)
                self.assertIn(relatorio.cell(row['skill']), report)
            self.assertEqual(sum(line.startswith('| ') and 'raciocínio ' in line
                                 for line in report.splitlines()), 19)

    def test_experiment_documents_reject_duplicate_or_unsafe_ids(self):
        import relatorio
        _, records, tables = relatorio.results()
        for identifier in ('chave', '../escape', 'Case Name'):
            planned = [dict(id=identifier, genre='Didático', title='Caso', prompt='Pedido', checks=['Preservar fatos'])]
            with self.assertRaisesRegex(ValueError, 'experiment ID'):
                relatorio.experiment_documents(tables, records, planned)

    def test_render_experiments_writes_26_reports_without_paid_calls(self):
        import relatorio
        from collections import Counter
        from unittest.mock import patch
        self.assertTrue(callable(getattr(relatorio, 'render_experiments', None)),
                        'Missing offline experiment publication')
        cases = relatorio.load(Path(__file__).parent / 'experiments/cases.json')['cases']
        self.assertEqual(len(cases), 24)
        self.assertEqual(set(Counter(c['genre'] for c in cases).values()), {2})
        self.assertEqual(len({c['genre'] for c in cases}), 12)
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder)
            with patch.object(c.urllib.request, 'urlopen', side_effect=AssertionError('Paid request forbidden')):
                relatorio.render_experiments(destination)
            self.assertEqual(len(list(destination.glob('experiments/*/REPORT.md'))), 26)
            index = (destination / 'README.md').read_text()
            self.assertEqual(index.count('⏸️ aguardando orçamento'), 24)
            for case in cases:
                report = (destination / 'experiments' / case['id'] / 'REPORT.md').read_text()
                prompt_block = re.search(r'\n(`{3,})\n(.*?)\n\1\n', report, re.DOTALL)
                self.assertIsNotNone(prompt_block, case['id'])
                fence, prompt = prompt_block.groups()
                self.assertEqual(prompt, case['prompt'])
                self.assertTrue(all(len(run) < len(fence) for run in re.findall(r'`+', prompt)))
                self.assertEqual(sum(' | pendente | pendente | pendente | pendente | pendente |' in line
                                     for line in report.splitlines()), 19)
                self.assertNotIn('✅', report)

    def test_prepared_reports_preserve_literal_token_and_nested_python(self):
        from html.parser import HTMLParser
        import relatorio
        cases = {case['id']: case for case in relatorio.load(
            Path(__file__).parent / 'experiments/cases.json')['cases']}
        _, records, tables = relatorio.results()
        documents = relatorio.experiment_documents(tables, records, list(cases.values()))
        for identifier, fence, literal in (
                ('03-documentacao-api', '```', '<TOKEN>'),
                ('04-analise-bug', '````', '```python\ndef collect(item, bucket=[]):\n'
                 '    bucket.append(item)\n    return bucket\n```')):
            with self.subTest(identifier=identifier):
                report = documents['experiments/' + identifier + '/REPORT.md']
                block = report.split('ainda.\n\n', 1)[1].split('\n\n## Resumo dos resultados', 1)[0]
                opening, body = block.split('\n', 1)
                prompt, closing = body.rsplit('\n', 1)
                self.assertEqual(opening, fence)
                self.assertEqual(closing, fence)
                self.assertEqual(prompt, cases[identifier]['prompt'])
                self.assertIn(literal, prompt)
        with self.subTest(section='criterios-api'):
            criteria = documents['experiments/03-documentacao-api/REPORT.md'].split(
                '## Critérios previstos', 1)[1].split('## Tabela completa', 1)[0]
            text = []
            parser = HTMLParser()
            parser.handle_data = text.append
            parser.feed(criteria)
            self.assertIn('<TOKEN>', ''.join(text))
            self.assertIn('&lt;TOKEN&gt;', criteria)

    def test_linkedin_check_only_forbids_the_requested_follower_cta(self):
        import relatorio
        cases = relatorio.load(Path(__file__).parent / 'experiments/cases.json')['cases']
        case = next(case for case in cases if case['id'] == '21-linkedin-aprendizado')
        self.assertIn('sem pedir seguidores', case['prompt'])
        self.assertEqual(case['checks'][-1],
                         'Sem causalidade exclusiva, hashtags, pedido de seguidores ou experiência de Ricardo.')

    def test_existing_uncertain_jev_call_is_never_replayed(self):
        state = {'prompt': 'conto', 'textos': {'t000': 'texto'}, 'pares': {}}
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            c.b.save_json(p / 'jev-caso.json', {'request': c.decisions_payload(state), 'status': 'started'})
            with self.assertRaises(ValueError):
                c.run_jev(state, p, 'jev-caso', c.Decimal('1'), 'no-credential')
