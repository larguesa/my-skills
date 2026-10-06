"""Testes incrementais do editor conservador, apenas com biblioteca padrão."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/humanizar.py'


def module(script=SCRIPT):
    spec = importlib.util.spec_from_file_location('humanizar', script)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class EditorTests(unittest.TestCase):
    def test_audit_literal_catalog_and_normalized_counts(self):
        self.assertTrue(SCRIPT.exists(), 'O editor ainda não existe')
        h = module()
        report = h.audit('vale destacar vale destacar', [{'id': 'enchimento', 'pattern': 'vale destacar', 'replacement': 'destaco', 'fonte': 'exemplo'}])
        self.assertEqual(report['rule_counts']['enchimento']['count'], 2)
        self.assertEqual(report['rule_counts']['enchimento']['per_1000_words'], 500)
        self.assertEqual(report['findings'][0]['start'], 0)
        self.assertEqual(report['findings'][0]['end'], 13)
        self.assertEqual(report['input_sha256'], h.sha256('vale destacar vale destacar'))

    def test_cli_documents_explicit_unit_protection(self):
        result = subprocess.run([sys.executable, str(SCRIPT), 'apply', '--help'], capture_output=True, text=True)
        self.assertIn('--protect kg', result.stdout)
        h = module()
        text = 'peso 20 kg'
        start = text.index('kg')
        with self.assertRaises(ValueError):
            h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [
                {'start': start, 'end': start + 2, 'original': 'kg',
                 'replacement': 'g', 'approved': True}]}, ['kg'])

    def test_empty_audit_rates_are_undefined(self):
        h = module()
        for text in ['', '...']:
            report = h.audit(text, [{'id': 'r', 'pattern': 'texto'}])
            self.assertEqual(report['word_count'], 0)
            self.assertIsNone(report['rule_counts']['r']['per_1000_words'])
            self.assertEqual(report['rule_counts']['r']['count'], 0)

    def test_negation_scope_does_not_end_at_numeric_separator(self):
        h = module()
        for text in ['não pagar 1.500 reais hoje', 'não pagar 1.50 reais hoje',
                     'pagar 1.500 reais hoje não convém']:
            start = text.index('hoje')
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [
                        {'start': start, 'end': start + 4, 'original': 'hoje',
                         'replacement': 'amanhã', 'approved': True}]})
                self.assertFalse(h.verify(text, text.replace('hoje', 'amanhã'))['protected_content_preserved'])

    def test_complete_numeric_literals_are_protected(self):
        h = module()
        for text, token in [('saldo -20 reais', '-'), ('saldo +20 reais', '+'),
                            ('saldo −20 reais', '−'), ('taxa 20%', '%'),
                            ('taxa 20 %', ' %'), ('taxa -1.500,25 %', '-')]:
            start = text.index(token)
            revised = text[:start] + text[start + len(token):]
            with self.subTest(text=text):
                self.assertFalse(h.verify(text, revised)['protected_content_preserved'])
                with self.assertRaises(ValueError):
                    h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [
                        {'start': start, 'end': start + len(token), 'original': token,
                         'replacement': '', 'approved': True}]})

    def test_apply_requires_hash_approval_and_exact_spans(self):
        h = module()
        text = 'vale destacar; vale destacar.'
        edit = {'start': 0, 'end': 13, 'original': 'vale destacar', 'replacement': 'destaco', 'approved': True}
        plan = {'input_sha256': h.sha256(text), 'edits': [edit]}
        self.assertTrue(hasattr(h, 'apply_edits'), 'Falta aplicação segura')
        self.assertEqual(h.apply_edits(text, plan), 'destaco; vale destacar.')
        for change in ({'approved': False}, {'approved': 1}, {'start': -1}, {'end': 100}, {'start': True}, {'original': 'errado'}, {'replacement': 3}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                h.apply_edits(text, dict(plan, edits=[dict(edit, **change)]))
        with self.assertRaises(ValueError):
            h.apply_edits(text, dict(plan, input_sha256='0' * 64))
        with self.assertRaises(ValueError):
            h.apply_edits(text, dict(plan, edits=[edit, edit]))

    def test_protection_independent_from_catalog(self):
        h = module()
        samples = ['custa 1.200,50 reais', 'acesse https://exemplo.com/a', '`vale destacar`', '```py\nx = 1\n```', '“vale destacar”', '"vale destacar"', "'vale destacar'", 'Maria Silva chegou', 'a marca iPhone mudou', 'não aceito', 'nunca aceito', 'se chover, fico', 'aceito desde que funcione', 'exceto aos sábados', 'termo reservado']
        for text in samples:
            with self.subTest(text=text), self.assertRaises(ValueError):
                h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [{'start': 0, 'end': len(text), 'original': text, 'replacement': 'alterado', 'approved': True}]}, ['termo reservado'])
        text = 'vale destacar'
        for replacement in ['agora são 20', 'não', 'Maria', 'https://exemplo.com', 'se der certo']:
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [{'start': 0, 'end': len(text), 'original': text, 'replacement': replacement, 'approved': True}]})

    def test_seeded_profile_suggestions_are_unapproved_and_protected(self):
        h = module()
        self.assertTrue(hasattr(h, 'suggest'), 'Falta plano de sugestões')
        rules = [{'id': 'r', 'pattern': 'vale destacar', 'replacement': 'destaco', 'profiles': ['neutro-claro'], 'variants': {'neutro-claro': ['destaco', 'ressalto'], 'conversacional-contido': ['olha']}}]
        text = 'vale destacar. vale destacar. “vale destacar”.'
        plan = h.suggest(text, rules, seed=17, profile='neutro-claro')
        self.assertEqual(plan, h.suggest(text, rules, seed=17, profile='neutro-claro'))
        self.assertTrue(plan['edits'])
        self.assertLessEqual(len(plan['edits']), 2)
        self.assertTrue(all(not e['approved'] and e['replacement'] in ['destaco', 'ressalto'] and e['start'] < 30 for e in plan['edits']))
        self.assertEqual(h.suggest(text, rules, profile='tecnico-preciso')['edits'], [])
        self.assertEqual(h.suggest('texto simples', rules)['edits'], [])
        with self.assertRaises(ValueError):
            h.suggest(text, rules, profile='inexistente')

    def test_actual_catalog_seed_selects_style_focus_without_rewriting(self):
        h = module()
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        plans = [h.suggest('texto simples', rules, seed=seed) for seed in range(12)]
        self.assertTrue(all('style_focus' in p for p in plans), 'Falta escolha sutil de estilo')
        allowed = h.load_profiles()['neutro-claro']['adjustments']
        self.assertTrue(all(p['style_focus'] in allowed and p['edits'] == [] for p in plans))
        self.assertGreater(len({p['style_focus'] for p in plans}), 1)
        self.assertEqual(plans[7], h.suggest('texto simples', rules, seed=7))

    def test_verify_reports_changes_and_limits(self):
        h = module()
        self.assertTrue(hasattr(h, 'verify'), 'Falta verificação explícita')
        result = h.verify('custa 20 reais', 'custa 30 reais')
        self.assertTrue(result['semantic_review_needed'])
        self.assertFalse(result['protected_content_preserved'])
        self.assertTrue(result['differences'])
        self.assertIn('não garante', result['aviso'])
        same = h.verify('nunca mude', 'nunca mude')
        self.assertFalse(same['semantic_review_needed'])
        self.assertTrue(same['unchanged'])
        self.assertTrue(h.verify('ela aprovou', 'ela rejeitou')['semantic_review_needed'])

    def test_repeated_phrases_and_protected_diagnostics(self):
        h = module()
        report = h.audit('vale destacar aqui. vale destacar aqui. “vale destacar”.', [{'id': 'r', 'pattern': 'vale destacar'}])
        self.assertIn('repeated_phrases', report)
        repeats = {r['phrase']: r for r in report['repeated_phrases']}
        self.assertEqual(repeats['vale destacar aqui']['count'], 2)
        self.assertTrue(report['findings'][-1]['protected'])
        self.assertEqual(h.audit('', [])['repeated_phrases'], [])
        self.assertIn('não identifica autoria', report['aviso'])

    def test_cli_audit_suggest_apply_verify_utf8_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, catalog, planfile, output = [root / name for name in ('in.txt', 'rules.json', 'plan.json', 'out.txt')]
            source.write_bytes('vale destacar: ação.\r\n'.encode())
            catalog.write_text(json.dumps({'rules': [{'id': 'r', 'pattern': 'vale destacar', 'replacement': 'destaco', 'arbitrary_metadata': True}]}), encoding='utf-8')
            def cli(*args):
                return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)
            result = cli('audit', source, '--catalog', catalog)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(result.stdout.strip(), 'CLI não produziu relatório')
            self.assertEqual(json.loads(result.stdout)['rule_counts']['r']['count'], 1)
            result = cli('suggest', source, '--catalog', catalog, '--seed', '7', '--profile', 'neutro-claro')
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            planfile.write_text(json.dumps(plan), encoding='utf-8')
            refused = cli('apply', source, '--plan', planfile, '--output', output)
            self.assertEqual(refused.returncode, 2)
            self.assertFalse(output.exists())
            for edit in plan['edits']:
                edit['approved'] = True
            planfile.write_text(json.dumps(plan), encoding='utf-8')
            applied = cli('apply', source, '--plan', planfile, '--output', output)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual(output.read_bytes(), 'destaco: ação.\r\n'.encode())
            self.assertTrue(json.loads(applied.stdout)['semantic_review_needed'])
            checked = cli('verify', source, output)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertTrue(json.loads(checked.stdout)['semantic_review_needed'])
            self.assertEqual(cli('apply', source, '--plan', planfile, '--output', source).returncode, 2)
            catalog.write_text('{invalid', encoding='utf-8')
            self.assertEqual(cli('audit', source, '--catalog', catalog).returncode, 2)

    def test_catalog_regex_guidance_is_not_a_replacement(self):
        h = module()
        rules = [{'id': 'r', 'pattern': r'(?i)\bvale (?:destacar|ressaltar)\b', 'suggestion': 'considerar remover a abertura', 'allowed_action': ['audit', 'suggest']}]
        self.assertEqual(len(h.audit('vale ressaltar', rules)['findings']), 1)
        self.assertEqual(h.suggest('vale ressaltar', rules)['edits'], [])
        self.assertTrue(h.suggest('vale ressaltar', rules)['recommendations'])
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder) / 'rules.json'
            for invalid in ({}, [None], [{'id': 'x', 'pattern': ''}], [{'id': 'x', 'pattern': '['}], [{'id': 'x', 'pattern': 'a'}, {'id': 'x', 'pattern': 'b'}]):
                catalog.write_text(json.dumps(invalid), encoding='utf-8')
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    h.load_catalog(catalog)

    def test_real_catalog_and_style_profiles(self):
        h = module()
        references = SCRIPT.parent.parent / 'references'
        rules = h.load_catalog(references / 'catalogo.json')
        report = h.audit('Na sociedade atual, vale destacar que o cadastro mudou.', rules)
        self.assertTrue(report['findings'])
        profiles = json.loads((references / 'estilos.json').read_text())['profiles']
        self.assertTrue(hasattr(h, 'load_profiles'), 'Falta carregar perfis editoriais reais')
        self.assertEqual(set(h.load_profiles()), {p['id'] for p in profiles})
        for profile in profiles:
            plan = h.suggest('vale destacar que o cadastro mudou.', rules, profile=profile['id'])
            self.assertEqual(plan['profile'], profile['id'])
            self.assertEqual(plan['profile_guidance'], profile)
            self.assertEqual(plan['edits'], [])
            self.assertTrue(plan['recommendations'])

    def test_protected_terms_travel_in_plan_and_boundaries_cannot_merge(self):
        h = module()
        text = 'marca exclusiva'
        plan = h.suggest(text, [], protected_terms=['marca exclusiva'])
        self.assertEqual(plan.get('protected_terms'), ['marca exclusiva'])
        plan['edits'] = [{'start': 0, 'end': len(text), 'original': text, 'replacement': 'outra', 'approved': True}]
        with self.assertRaises(ValueError):
            h.apply_edits(text, plan)
        for text, start, end in [('1 2', 1, 2), ('Maria Silva', 5, 6), ('não vale destacar', 4, 17)]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [{'start': start, 'end': end, 'original': text[start:end], 'replacement': '', 'approved': True}]})


class CatalogTests(unittest.TestCase):
    def test_ptbr_17_requires_complete_words_and_keeps_exclamations(self):
        h = module()
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        word_phrases = ['Espero que isso ajude', 'Espero que isto ajude',
                        'Se quiser, posso', 'Aqui está o texto', 'Aqui está um texto']
        word_phrases += [f'Como {article}{term}' for article in ['', 'um ', 'uma ']
                        for term in ['IA', 'inteligência artificial']]
        negatives = ['A lancha navegava como um iate.']
        negatives += [phrase + suffix for phrase in word_phrases for suffix in ['s', '2', '_']]
        for text in negatives:
            with self.subTest(text=text):
                report = h.audit(text, rules)
                self.assertEqual(report['rule_counts']['PTBR-17']['count'], 0)
                self.assertEqual([f for f in report['findings'] if f['rule_id'] == 'PTBR-17'], [])
        for phrase in word_phrases + ['Com certeza!', 'Certamente!']:
            for ending in ['', '.', '!', ' Mais detalhes.']:
                text = 'Introdução: ' + phrase + ending
                with self.subTest(text=text):
                    report = h.audit(text, rules)
                    self.assertEqual(report['rule_counts']['PTBR-17']['count'], 1)
                    findings = [f for f in report['findings'] if f['rule_id'] == 'PTBR-17']
                    start = text.index(phrase)
                    self.assertEqual([(f['start'], f['end'], f['original']) for f in findings],
                                     [(start, start + len(phrase), phrase)])

    def test_catalog_search_includes_expressions_examples_and_exceptions(self):
        h = module()
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        for query, expected in [('crucial', 'PTBR-22'), ('é importante', 'PTBR-03')]:
            result = subprocess.run([sys.executable, str(SCRIPT), 'catalog', '--query', query], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, [r['id'] for r in json.loads(result.stdout)])
        rule = {'id': 'r', 'genres': ['artigo'], 'pattern': 'expressão buscada',
                'avoid': ['evitada'], 'positive_example': 'exemplo assinalado',
                'negative_example': 'exemplo alternativo', 'exceptions': ['exceção técnica']}
        for query in ['expressao buscada', 'EVITADA', 'assinalado', 'alternativo', 'EXCECAO TECNICA']:
            self.assertEqual(h.search_catalog([rule], query), [rule])

    def test_catalog_limits_and_strict_filters(self):
        h = module()
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        for limit in [0, -1, True, 1.5, '2']:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                h.search_catalog(rules, limit=limit)
        self.assertEqual(len(h.search_catalog(rules, limit=2)), 2)
        self.assertEqual(h.search_catalog(rules, 'inexistente'), [])
        self.assertEqual(h.search_catalog(rules, genre='ARTIGO'), [])
        for args in [('catalog', '--limit', '0'), ('catalog', '--limit', '-1')]:
            result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)
        for args in [('catalog', '--query', 'inexistente'), ('catalog', '--genre', 'ARTIGO')]:
            result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), [])

    def test_catalog_search_and_cli_are_accent_insensitive(self):
        h = module()
        self.assertTrue(hasattr(h, 'search_catalog'), 'Falta busca local no catálogo')
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        self.assertEqual(h.search_catalog(rules, 'PTBR-06')[0]['id'], 'PTBR-06')
        self.assertEqual(h.search_catalog(rules, 'ATRIBUIR SOMENTE')[0]['id'], 'PTBR-06')
        self.assertEqual(h.search_catalog(rules, 'IMPORTÂNCIA', genre='artigo', limit=1)[0]['id'], 'PTBR-07')
        result = subprocess.run([sys.executable, str(SCRIPT), 'catalog', '--query', 'ATRIBUIR SOMENTE', '--genre', 'artigo', '--limit', '1'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), h.search_catalog(rules, 'ATRIBUIR SOMENTE', 'artigo', 1))


class StyleTests(unittest.TestCase):
    def test_styles_search_and_cli(self):
        h = module()
        self.assertTrue(hasattr(h, 'search_styles'), 'Falta busca local de estilos')
        self.assertEqual(h.search_styles('TÉCNICO', genre='tecnico')[0]['id'], 'tecnico-preciso')
        self.assertEqual(h.search_styles('QUALIFICADORES')[0]['id'], 'tecnico-preciso')
        self.assertEqual(h.search_styles(genre='POST', limit=1), [])
        self.assertEqual(h.search_styles('perfil-ausente'), [])
        self.assertEqual(len(h.search_styles(limit=1)), 1)
        for limit in [0, -2, True, 0.5, '3']:
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                h.search_styles(limit=limit)
        for query, genre in [('TÉCNICO', 'tecnico'), ('perfil-ausente', 'post'), ('', 'POST')]:
            result = subprocess.run([sys.executable, str(SCRIPT), 'styles', '--query', query, '--genre', genre, '--limit', '1'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), h.search_styles(query, genre, 1))
        result = subprocess.run([sys.executable, str(SCRIPT), 'styles', '--limit', '0'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn('Traceback', result.stderr)


class StructureTests(unittest.TestCase):
    def test_every_real_profile_genre_and_template(self):
        actual = json.loads((SCRIPT.parent.parent / 'references/estilos.json').read_text(encoding='utf-8'))
        structures = {s['id']: s for s in actual['structures']}
        h = module()
        referenced = set()
        for profile in actual['profiles']:
            for sid in profile['structure_ids']:
                self.assertIn(sid, structures)
                referenced.add(sid)
            for genre in profile['genres']:
                with self.subTest(profile=profile['id'], genre=genre):
                    plan = h.generate_structure(profile['id'], genre, breadth=0)
                    expected = next(sid for sid in profile['structure_ids'] if genre in structures[sid]['genres'])
                    self.assertEqual(plan['structure_id'], expected)
                    source = structures[expected]['blocks']
                    self.assertEqual(plan['blocks'], [{k: b[k] for k in ['id', 'required', 'instruction']} for b in source if b['required']])
                    result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), 'structure', '--profile', profile['id'], '--genre', genre, '--breadth', '0'], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(result.stdout), plan)
        self.assertEqual(referenced, set(structures))
        for sid, structure in structures.items():
            owner = next(p for p in actual['profiles'] if sid in p['structure_ids'])
            self.data = json.loads(json.dumps(actual))
            selected = next(p for p in self.data['profiles'] if p['id'] == owner['id'])
            selected['structure_ids'] = [sid]
            genre = next(g for g in owner['genres'] if g in structure['genres'])
            self.write_styles()
            for breadth, randomness in [(0, 0), (99, 0), (1, 1)]:
                plan = self.h.generate_structure(owner['id'], genre, breadth, randomness, seed=17)
                self.assertEqual(plan['structure_id'], sid)
                self.assertEqual(plan, self.h.generate_structure(owner['id'], genre, breadth, randomness, seed=17))
                original = {b['id']: b for b in structure['blocks']}
                ids = [b['id'] for b in plan['blocks']]
                self.assertEqual(ids, [b['id'] for b in structure['blocks'] if b['id'] in ids])
                self.assertEqual(sum(not b['required'] for b in plan['blocks']), min(breadth, sum(not b['required'] for b in structure['blocks'])))
                for block in plan['blocks']:
                    self.assertIn(block['instruction'], [original[block['id']]['instruction']] + original[block['id']]['alternatives'])
                self.assertEqual({b['id']: b['instruction'] for b in plan['blocks'] if b['required']}, {b['id']: b['instruction'] for b in structure['blocks'] if b['required']})

    def test_randomness_never_replaces_essential_instructions(self):
        source = {block['id']: block['instruction'] for block in self.data['structures'][1]['blocks'] if block['required']}
        for seed in range(12):
            plan = self.h.generate_structure(genre='artigo', breadth=0, randomness=1, seed=seed)
            self.assertEqual({block['id']: block['instruction'] for block in plan['blocks']}, source)

    def test_structure_configuration_errors_are_clear(self):
        for mutate in [lambda d: d.pop('structures'),
                       lambda d: d['profiles'][0].update(structure_ids=['ausente']),
                       lambda d: d['profiles'][0].update(structure_ids=[]),
                       lambda d: d['structures'][1]['blocks'][0].pop('required'),
                       lambda d: d['structures'][1]['blocks'][0].update(required='true'),
                       lambda d: d['structures'][1]['blocks'][0].update(alternatives=[None]),
                       lambda d: d['structures'][1].update(blocks=[]),
                       lambda d: d['structures'][1].update(genres=['email'])]:
            original = json.loads(json.dumps(self.data))
            mutate(self.data)
            self.write_styles()
            with self.assertRaises(ValueError):
                self.h.generate_structure(genre='artigo')
            result = self.cli('structure', '--genre', 'artigo')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.data = original

    def test_structure_randomness_is_seeded_local_and_order_preserving(self):
        import random
        state = random.getstate()
        plans = [self.h.generate_structure(genre='artigo', breadth=1, randomness=1, seed=s) for s in range(20)]
        self.assertGreater(len({json.dumps(p['blocks']) for p in plans}), 1)
        for s, plan in enumerate(plans):
            self.assertEqual(plan, self.h.generate_structure(genre='artigo', breadth=1, randomness=1, seed=s))
            ids = [b['id'] for b in plan['blocks']]
            self.assertTrue(all(i in ids for i in ['abertura', 'evidencia', 'fecho']))
            self.assertEqual(ids, sorted(ids, key=['abertura', 'contexto', 'evidencia', 'limite', 'fecho'].index))
            self.assertEqual(plan['structure_id'], 'base')
            self.assertEqual(sum(not b['required'] for b in plan['blocks']), 1)
        self.assertEqual(random.getstate(), state)
        self.assertEqual(self.h.generate_structure(randomness=0, seed=1)['blocks'], self.h.generate_structure(randomness=0, seed=999)['blocks'])
        result = self.cli('structure', '--randomness', '1', '--seed', '7', '--breadth', '1', '--genre', 'artigo')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), plans[7])

    def test_structure_rejects_invalid_controls_and_incompatible_genres(self):
        for options in [{'profile': 'ausente'}, {'genre': 'email'}, {'genre': 'ARTIGO'},
                        {'breadth': -1}, {'breadth': True}, {'breadth': 1.5},
                        {'randomness': -0.1}, {'randomness': 1.1}, {'randomness': float('nan')},
                        {'randomness': float('inf')}, {'randomness': True}, {'randomness': '0'},
                        {'seed': True}, {'seed': []}]:
            with self.subTest(options=options), self.assertRaises(ValueError):
                self.h.generate_structure(**options)
        for args in [('--profile', 'ausente'), ('--genre', 'email'), ('--genre', 'ARTIGO'),
                     ('--breadth', '-1'), ('--randomness', '-0.1'), ('--randomness', '1.1'),
                     ('--randomness', 'nan'), ('--randomness', 'inf')]:
            result = self.cli('structure', *args)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertNotIn('Traceback', result.stderr)
        self.assertEqual([b['id'] for b in self.h.generate_structure(breadth=0)['blocks']], ['abertura', 'evidencia', 'fecho'])
        self.assertEqual(len(self.h.generate_structure(breadth=99)['blocks']), 5)
        self.assertEqual(self.h.generate_structure()['genre'], 'artigo')
        self.assertEqual(self.h.generate_structure(genre='post')['structure_id'], 'base')

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.script = self.root / 'scripts/humanizar.py'
        self.script.parent.mkdir()
        self.script.write_bytes(SCRIPT.read_bytes())
        references = self.root / 'references'
        references.mkdir()
        self.styles = references / 'estilos.json'
        self.data = {'profiles': [{'id': 'neutro-claro', 'genres': ['artigo', 'post'], 'adjustments': ['Manter precisão'], 'structure_ids': ['email', 'base', 'outro']}],
            'structures': [
                {'id': 'email', 'genres': ['email'], 'blocks': [{'id': 'mensagem', 'required': True, 'instruction': 'Planejar pedido', 'alternatives': []}]},
                {'id': 'base', 'genres': ['artigo', 'post'], 'blocks': [
                    {'id': 'abertura', 'required': True, 'instruction': 'Delimitar o assunto fornecido', 'alternatives': ['Apresentar o assunto autorizado']},
                    {'id': 'contexto', 'required': False, 'instruction': 'Planejar contexto pertinente', 'alternatives': ['Selecionar contexto já fornecido']},
                    {'id': 'evidencia', 'required': True, 'instruction': 'Organizar evidências disponíveis', 'alternatives': []},
                    {'id': 'limite', 'required': False, 'instruction': 'Planejar explicação adicional', 'alternatives': []},
                    {'id': 'fecho', 'required': True, 'instruction': 'Preservar ressalvas essenciais no encerramento', 'alternatives': []}]},
                {'id': 'outro', 'genres': ['post'], 'blocks': [{'id': 'ponto', 'required': True, 'instruction': 'Organizar o ponto fornecido', 'alternatives': []}]}]}
        self.write_styles()
        self.h = module(self.script)

    def write_styles(self):
        self.styles.write_text(json.dumps(self.data), encoding='utf-8')

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.script), *map(str, args)], capture_output=True, text=True)

    def test_structure_plan_keeps_required_blocks_and_logical_order(self):
        h = self.h
        self.assertTrue(hasattr(h, 'generate_structure'), 'Falta plano estrutural local')
        plan = h.generate_structure(genre='artigo', breadth=1)
        self.assertEqual(plan['kind'], 'structure_plan')
        self.assertEqual(plan['structure_id'], 'base')
        self.assertEqual([b['id'] for b in plan['blocks']], ['abertura', 'contexto', 'evidencia', 'fecho'])
        self.assertEqual(plan['blocks'][0]['instruction'], self.data['structures'][1]['blocks'][0]['instruction'])
        self.assertEqual(plan['semantics']['breadth_unit'], 'optional_blocks')
        self.assertEqual(plan['semantics']['optional_blocks_selected'], 1)
        self.assertTrue(plan['semantics']['required_blocks_preserved'])
        self.assertIn('não gera prosa', plan['aviso'])
        result = self.cli('structure', '--profile', 'neutro-claro', '--genre', 'artigo', '--breadth', '1')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), plan)


class ReplacementTests(unittest.TestCase):
    def test_short_text_replacement_plan_finishes_within_timeout(self):
        text = 'com o intuito de validar, revise o texto.\n' * 100
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'entrada.txt'
            source.write_bytes(text.encode('utf-8'))
            try:
                result = subprocess.run(
                    [sys.executable, '-W', 'error', str(SCRIPT), 'replace', str(source),
                     '--from', 'com o intuito de', '--to', 'para'],
                    capture_output=True, text=True, timeout=10)
            except subprocess.TimeoutExpired:
                self.fail('Planejar 100 substituições em texto curto excedeu 10 segundos.')
            self.assertEqual(result.returncode, 0, result.stderr)
            plan = json.loads(result.stdout)
            self.assertEqual(len(plan['edits']), 100)
            self.assertTrue(all(e['approved'] is False for e in plan['edits']))
            self.assertEqual(source.read_bytes(), text.encode('utf-8'))
        h = module()
        with self.assertRaises(ValueError):
            h.apply_edits(text, plan)
        for edit in plan['edits']:
            edit['approved'] = True
        self.assertEqual(h.apply_edits(text, plan), 'para validar, revise o texto.\n' * 100)

    def test_replace_plan_apply_cli_keeps_bytes_and_refuses_tampering(self):
        h = module()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, planfile, output = [root / n for n in ['in.txt', 'plan.json', 'out.txt']]
            original = 'vale destacar: ação.\r\n“vale destacar” e custo 20 reais.\r\n'
            source.write_bytes(original.encode('utf-8'))
            source.chmod(0o444)
            def cli(*args):
                return subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *map(str, args)], capture_output=True, text=True)
            planned = cli('replace', source, '--from', 'vale destacar', '--to', 'destaco', '--protect', 'reais')
            self.assertEqual(planned.returncode, 0, planned.stderr)
            plan = json.loads(planned.stdout)
            self.assertEqual(len(plan['edits']), 1)
            self.assertEqual(plan['protected_terms'], ['reais'])
            for edits in [plan['edits'], [dict(plan['edits'][0], approved=1)], [dict(plan['edits'][0], approved=True)] * 2]:
                planfile.write_text(json.dumps(dict(plan, edits=edits)), encoding='utf-8')
                refused = cli('apply', source, '--plan', planfile, '--output', output)
                self.assertEqual(refused.returncode, 2, refused.stderr)
                self.assertNotIn('Traceback', refused.stderr)
                self.assertFalse(output.exists())
            approved = dict(plan, edits=[dict(plan['edits'][0], approved=True)])
            planfile.write_text(json.dumps(approved), encoding='utf-8')
            applied = cli('apply', source, '--plan', planfile, '--output', output)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual(output.read_bytes(), original.replace('vale destacar', 'destaco', 1).encode('utf-8'))
            self.assertEqual(source.read_bytes(), original.encode('utf-8'))
            self.assertEqual(cli('apply', source, '--plan', planfile, '--output', output).returncode, 2)
            self.assertEqual(cli('apply', source, '--plan', planfile, '--output', source).returncode, 2)
            approved['input_sha256'] = '0' * 64
            planfile.write_text(json.dumps(approved), encoding='utf-8')
            refused = cli('apply', source, '--plan', planfile, '--output', root / 'bad.txt')
            self.assertEqual(refused.returncode, 2)
            self.assertFalse((root / 'bad.txt').exists())
            self.assertTrue(json.loads(cli('verify', source, output).stdout)['protected_content_preserved'])

    def test_replacement_never_matches_inside_unicode_words(self):
        h = module()
        self.assertEqual([e['start'] for e in h.plan_replacements('a_b _', '_', '-')['edits']], [4])
        text = 'cafe\u0301 cafe\u0301ina'
        self.assertEqual([e['start'] for e in h.plan_replacements(text, 'cafe\u0301', 'bebida')['edits']], [0])
        self.assertEqual(h.plan_replacements('cafe\u0301', 'cafe', 'bebida')['edits'], [])

    def test_replacement_invalid_inputs_and_unsafe_changes(self):
        h = module()
        for source, target in [('', 'ato'), (None, 'ato'), ('ação', None), ('ação', 1)]:
            with self.subTest(source=source, target=target), self.assertRaises(ValueError):
                h.plan_replacements('ação', source, target)
        self.assertEqual(h.plan_replacements('ação', 'ação', 'ação')['edits'], [])
        self.assertEqual(h.plan_replacements('texto simples', 'ausente', '')['edits'], [])
        for target in ['20', 'não', 'Maria', 'https://exemplo.com', '`ato`']:
            self.assertEqual(h.plan_replacements('ação', 'ação', target)['edits'], [])
        self.assertEqual(h.plan_replacements('1 2', ' ', '')['edits'], [])
        self.assertEqual(h.plan_replacements('ação ação', 'ação', '')['edits'][0]['replacement'], '')
        self.assertEqual(len(h.plan_replacements('a+b aab', 'a+b', 'item')['edits']), 1)
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'entrada.txt'
            source.write_bytes('ação.\r\n'.encode('utf-8'))
            result = subprocess.run([sys.executable, str(SCRIPT), 'replace', str(source), '--from', '', '--to', 'ato'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn('Traceback', result.stderr)

    def test_replacement_boundaries_and_protected_content_are_omitted(self):
        h = module()
        text = 'ação reação açãozinha préação ação_1 ação2. “ação” \"ação\" `ação` 20 ação.\r\n> ação\r\n```ação```\r\ncaso ação, fica. marca ação. ação.'
        plan = h.plan_replacements(text, 'ação', 'ato', protected_terms=['marca ação'])
        expected = [0, text.index('ação.', text.index('20')), text.rindex('ação.')]
        self.assertEqual([e['start'] for e in plan['edits']], expected)
        self.assertEqual(plan['protected_terms'], ['marca ação'])
        self.assertEqual(h.plan_replacements('alvo alvos subalvo alvo_1 alvo2. Alvo.', 'alvo', 'item')['edits'][0]['start'], 0)
        self.assertEqual(len(h.plan_replacements('alvo alvos subalvo alvo_1 alvo2. Alvo.', 'alvo', 'item')['edits']), 1)
        for sample in ['“ação”', '\"ação\"', "'ação'", '`ação`', '```ação', '~~~ação~~~', '> ação', 'não ação.', 'caso ação.', 'https://acao.ex/ação', 'Maria ação']:
            term = 'Maria' if sample.startswith('Maria') else 'ação'
            self.assertEqual(h.plan_replacements(sample, term, 'ato')['edits'], [], sample)
        for sample, term in [('taxa 20%', '20'), ('saldo -1.500,25', '-'), ('taxa 20 %', '%')]:
            self.assertEqual(h.plan_replacements(sample, term, '')['edits'], [])
        for edit in plan['edits']:
            edit['approved'] = True
        result = h.apply_edits(text, plan)
        self.assertTrue(h.verify(text, result, ['marca ação'])['protected_content_preserved'])

    def test_literal_replacement_plan_and_cli_are_readonly(self):
        h = module()
        self.assertTrue(hasattr(h, 'plan_replacements'), 'Falta plano de substituição literal')
        text = 'ação vale destacar. vale destacar: ação.\r\n'
        plan = h.plan_replacements(text, 'vale destacar', 'destaco')
        self.assertEqual(plan['kind'], 'replacement_plan')
        self.assertEqual(plan['input_sha256'], h.sha256(text))
        self.assertEqual(len(plan['edits']), 2)
        self.assertTrue(all(e['approved'] is False for e in plan['edits']))
        self.assertTrue(plan['case_sensitive'])
        with self.assertRaises(ValueError):
            h.apply_edits(text, plan)
        for edit in plan['edits']:
            edit['approved'] = True
        self.assertEqual(h.apply_edits(text, plan), 'ação destaco. destaco: ação.\r\n')
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'entrada.txt'
            source.write_bytes(text.encode('utf-8'))
            before = source.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), 'replace', str(source), '--from', 'vale destacar', '--to', 'destaco'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertEqual(output, h.plan_replacements(text, 'vale destacar', 'destaco'))
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(list(Path(folder).iterdir()), [source])


class RhythmTests(unittest.TestCase):
    def test_rhythm_cli_does_not_offer_ignored_protection_flags(self):
        result = subprocess.run([sys.executable, str(SCRIPT), 'rhythm', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('--protect', result.stdout)

    def test_rhythm_handles_empty_text_and_numeric_separators(self):
        h = module()
        for text in ['', ' \r\n\r\n', '...!?']:
            report = h.rhythm(text)
            self.assertEqual(report['sentence_count'], 0)
            self.assertEqual(report['paragraph_count'], 0)
            self.assertEqual(report['repeated_openings'], [])
            self.assertEqual(report['sentence_character_lengths'], [])
        text = 'valor 1.500,25 reais. valor 2.0 reais!\r\ncontinua aqui\r\n \r\noutra parte.'
        report = h.rhythm(text)
        self.assertEqual(report['sentence_count'], 4)
        self.assertEqual(report['paragraph_count'], 2)
        self.assertEqual(report['sentence_word_lengths'], [5, 4, 2, 2])
        self.assertEqual(h.rhythm('frase sem ponto')['sentence_count'], 1)
        self.assertEqual(h.rhythm('ação\ncontinua aqui')['sentence_count'], 2)
        with self.assertRaises(ValueError):
            h.rhythm(None)

    def test_rhythm_reports_lengths_and_repeated_openings_without_scores(self):
        h = module()
        self.assertTrue(hasattr(h, 'rhythm'), 'Falta descrição local de ritmo')
        text = 'Além disso, chegou. Além disso, saiu!\r\n\r\nAlém disso, esperou? Uma frase bem mais longa aparece aqui.'
        report = h.rhythm(text)
        self.assertEqual(report['input_sha256'], h.sha256(text))
        self.assertEqual(report['sentence_count'], 4)
        self.assertEqual(report['paragraph_count'], 2)
        self.assertEqual(report['sentence_word_lengths'], [3, 3, 3, 7])
        self.assertEqual(report['paragraph_word_lengths'], [6, 10])
        self.assertEqual(report['repeated_openings'], [{'opening': 'além disso', 'count': 3}])
        for field in ['score', 'threshold', 'ai_probability', 'authorship']:
            self.assertNotIn(field, report)
        self.assertIn('não identifica autoria', report['aviso'])
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'entrada.txt'
            source.write_bytes(text.encode('utf-8'))
            result = subprocess.run([sys.executable, str(SCRIPT), 'rhythm', str(source)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), report)
            self.assertEqual(source.read_bytes(), text.encode('utf-8'))


class LocalContractTests(unittest.TestCase):
    def test_invalid_cli_inputs_never_emit_tracebacks(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'bad.txt'
            source.write_bytes(b'\xff')
            for command in ['rhythm', 'replace']:
                tail = ['--from', 'texto', '--to', 'outro'] if command == 'replace' else []
                for path in [source, Path(folder) / 'missing.txt']:
                    result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), command, str(path), *tail], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertNotIn('Traceback', result.stderr)
            for args in [('catalog', '--limit', 'abc'), ('styles', '--limit', '-3'),
                         ('structure', '--profile', 'ausente'), ('structure', '--genre', 'NOTICIA'),
                         ('structure', '--randomness', 'nan'), ('structure', '--breadth', '-2'),
                         ('structure', '--seed', 'a')]:
                result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)

    def test_real_catalog_is_locally_searchable_and_imports_are_stdlib(self):
        import ast
        tree = ast.parse(SCRIPT.read_text(encoding='utf-8'))
        imports = [name.name.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
        imports.extend(node.module.split('.')[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
        self.assertTrue(all(name in sys.stdlib_module_names for name in imports))
        h = module()
        rules = h.load_catalog(SCRIPT.parent.parent / 'references/catalogo.json')
        for rule in rules:
            self.assertIn(rule, h.search_catalog(rules, rule['id'], limit=len(rules)))
        for query in ['autoridade', 'robustez']:
            result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), 'catalog', '--query', query], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout))


if __name__ == '__main__':
    unittest.main()
