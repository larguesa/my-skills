"""Testes incrementais do editor conservador, apenas com biblioteca padrão."""
from collections import Counter
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
    def test_documented_profiles_match_registered_profiles(self):
        import re
        skill = (SCRIPT.parent.parent / 'SKILL.md').read_text(encoding='utf-8')
        lines = re.findall(r'^Perfis: (.+)$', skill, re.MULTILINE)
        self.assertEqual(len(lines), 1, 'A skill deve declarar uma única lista de perfis')
        documented = re.findall(r'`([a-z0-9-]+)`', lines[0])
        self.assertTrue(documented, 'A lista documentada não pode estar vazia')
        self.assertEqual(len(documented), len(set(documented)), 'Perfil documentado duplicado')
        data = json.loads((SCRIPT.parent.parent / 'references/estilos.json').read_text(encoding='utf-8'))
        registered = [profile['id'] for profile in data['profiles']]
        self.assertEqual(len(registered), len(set(registered)), 'Perfil cadastrado duplicado')
        self.assertEqual(set(documented), set(registered),
                         'Os perfis da skill e do JSON precisam corresponder')

    def test_new_profiles_work_through_lookup_structure_and_suggestion_cli(self):
        h = module()
        profiles = h.load_profiles()
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'entrada.txt'
            original = 'vale destacar que o cadastro mudou. “ação” custa 20 reais.\r\n'
            source.write_bytes(original.encode('utf-8'))
            for profile_id in ['coloquial', 'informal', 'caricato']:
                with self.subTest(profile=profile_id):
                    lookup = subprocess.run(
                        [sys.executable, '-W', 'error', str(SCRIPT), 'styles',
                         '--query', profile_id.upper()], capture_output=True, text=True)
                    self.assertEqual(lookup.returncode, 0, lookup.stderr)
                    matches = json.loads(lookup.stdout)
                    self.assertIn(profile_id, [profile['id'] for profile in matches],
                                  'O novo perfil precisa aparecer na busca')
                    guidance = profiles[profile_id]
                    for genre in guidance['genres']:
                        planned = subprocess.run(
                            [sys.executable, '-W', 'error', str(SCRIPT), 'structure',
                             '--profile', profile_id, '--genre', genre,
                             '--breadth', '0', '--randomness', '1', '--seed', '17'],
                            capture_output=True, text=True)
                        self.assertEqual(planned.returncode, 0, planned.stderr)
                        plan = json.loads(planned.stdout)
                        self.assertEqual(plan, h.generate_structure(profile_id, genre, 0, 1, 17))
                        self.assertTrue(plan['blocks'])
                        self.assertTrue(all(block['required'] for block in plan['blocks']))
                    suggested = subprocess.run(
                        [sys.executable, '-W', 'error', str(SCRIPT), 'suggest', str(source),
                         '--profile', profile_id, '--seed', '17'], capture_output=True, text=True)
                    self.assertEqual(suggested.returncode, 0, suggested.stderr)
                    suggestion = json.loads(suggested.stdout)
                    self.assertEqual(suggestion['profile'], profile_id)
                    self.assertEqual(suggestion['profile_guidance'], guidance)
                    self.assertIn(suggestion['style_focus'], guidance['adjustments'])
                    self.assertEqual(suggestion['edits'], [])
                    self.assertTrue(suggestion['recommendations'])
                    self.assertEqual(source.read_bytes(), original.encode('utf-8'))

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


SKILL_DIR = SCRIPT.parent.parent
RUN_13 = SKILL_DIR / 'results/scripts/fixtures/evidence-2026-10-13/requests'
LEGACY_13 = SKILL_DIR / 'results/scripts/fixtures/evidence-2026-10-13/frozen/skill'
PROMPTS = SKILL_DIR / 'results/PROMPTS.md'
README = SKILL_DIR / 'README.md'
SIZES_081_FILE = SKILL_DIR / 'results/tamanhos-0.8.1.json'


def requer(path):
    """Fixture do repositório completo; numa cópia isolada da skill o teste é pulado com o motivo declarado."""
    return unittest.skipUnless(path.exists(), f'fixture ausente nesta cópia: {path.relative_to(SKILL_DIR)}')
PROMPT_01 = ('Redija uma notícia curta para um portal local. A Prefeitura de Vila Clara anunciou '
             'em 1º de outubro de 2026 a abertura de 1.200 vagas gratuitas em oficinas de leitura '
             'nas seis bibliotecas municipais. As inscrições vão de 5 a 16 de outubro, '
             'presencialmente nas bibliotecas, para pessoas a partir de 12 anos. As oficinas '
             'começam em 3 de novembro. Os horários e a distribuição das vagas por unidade ainda '
             'não foram divulgados.')


def cli_run(*args):
    return subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def generated_13_10():
    """Textos reais preservados de 13/10, lidos sem alteração."""
    texts = {}
    for folder in sorted(RUN_13.glob('g.*')):
        result = json.loads((folder / 'result.json').read_text(encoding='utf-8'))
        if isinstance(result.get('text'), str):
            texts[folder.name] = result['text']
    return texts


class CatalogGaps20261019Tests(unittest.TestCase):
    """Lacunas observadas nas saídas de 13/10 e na lista de vetos da skill."""

    def rule_count(self, text, rule_id):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        return h.audit(text, rules)['rule_counts'].get(rule_id, {}).get('count')

    def test_delivery_preamble_is_flagged_only_as_its_own_line(self):
        for text in ['Aqui está a notícia:\n\n**Título**', 'Aqui está uma sugestão de notícia para o portal:\n\nTexto.',
                     'Segue o e-mail revisado:\nPrezada equipe,']:
            with self.subTest(text=text):
                self.assertEqual(self.rule_count(text, 'PTBR-27'), 1)
        for text in ['Aqui está o problema: a fila não andou.', 'O texto segue: duas partes.', 'Introdução: Aqui está o texto']:
            with self.subTest(text=text):
                self.assertEqual(self.rule_count(text, 'PTBR-27'), 0)

    def test_dash_substitutes_in_prose_are_flagged_but_ranges_and_lists_are_not(self):
        for text in ['**VILA CLARA** – A Prefeitura anunciou.', 'O prazo - que já venceu - foi mantido.', 'Ela saiu ― e voltou.']:
            with self.subTest(text=text):
                self.assertGreaterEqual(self.rule_count(text, 'PTBR-28'), 1)
        for text in ['Inscrições de 5–16 de outubro.', '- item de lista\n  - subitem', 'bem-estar e pré-requisito']:
            with self.subTest(text=text):
                self.assertEqual(self.rule_count(text, 'PTBR-28'), 0)

    def test_vetoed_vocabulary_matches_plural_and_conjugated_forms(self):
        for text, rule_id in [('Dois pontos cruciais.', 'PTBR-22'), ('Etapas fundamentais.', 'PTBR-22'),
                              ('A equipe está otimizando o fluxo.', 'PTBR-11'),
                              ('O curso potencializa resultados.', 'PTBR-11'),
                              ('A campanha alavancou vendas.', 'PTBR-11'),
                              ('Em resumo, o prazo acabou.', 'PTBR-24'),
                              ('Em síntese, o prazo acabou.', 'PTBR-24'),
                              ('Neste artigo, vamos ver o cadastro.', 'PTBR-02')]:
            with self.subTest(text=text):
                self.assertEqual(self.rule_count(text, rule_id), 1)
        for text, rule_id in [('A agência de fomento aprovou.', 'PTBR-11'),
                              ('A otimização convexa tem restrições.', 'PTBR-11')]:
            with self.subTest(text=text):
                self.assertEqual(self.rule_count(text, rule_id), 0)


class BriefTests(unittest.TestCase):
    """Briefing compacto: catálogo e estilo aplicados sem despejar JSONs integrais."""

    def test_brief_text_contains_every_rule_profile_plan_and_delivery_contract(self):
        # 0.7.0: exemplos só nas regras típicas do gênero; as demais aparecem por termos explícitos.
        # 0.9.0 (plano, seção 3.4): a lista das demais regras encurta; termo já declarado na SKILL.md,
        # que acompanha todo briefing, não se repete. O pacote SKILL.md + briefing continua com todos.
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        for profile_id, profile in h.load_profiles().items():
            for genre in profile['genres']:
                with self.subTest(profile=profile_id, genre=genre):
                    result = cli_run('brief', '--profile', profile_id, '--genre', genre)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    text = result.stdout
                    focus = h.brief(profile_id, genre)['focus']
                    for rule in rules:
                        # 0.9.0: fora do foco, a linha da regra traz id, termos e exceções, sem o nome.
                        self.assertIn(f"{rule['id']} {rule['name']}" if rule['id'] in focus else f"- {rule['id']}", text)
                        for term in rule['avoid']:
                            self.assertIn(term.casefold(), (text + skill).casefold())
                        if rule['id'] in focus:
                            self.assertIn(f'Evite: "{" ".join(rule["positive_example"].split())}"', text)
                            self.assertIn(f'Prefira: "{rule["negative_example"]}"', text)
                    for item in profile['adjustments'] + profile.get('avoid', []):
                        self.assertIn(item, text)
                    for block in h.generate_structure(profile_id, genre, 2, 0, None)['blocks']:
                        self.assertIn(block['instruction'], text)
                    self.assertIn('crucial', text + skill)
                    self.assertIn('não repita comandos', text.casefold())
                    self.assertIn('somente com o artefato', text.casefold())
                    self.assertNotIn('—', text)
                    # 0.8.0: exceções de todas as regras e orientação das de foco entram no texto.
                    self.assertLessEqual(len(text), 11500, 'O briefing deve ser compacto')

    def test_brief_labels_examples_by_role_not_by_test_polarity(self):
        text = cli_run('brief', '--profile', 'neutro-claro').stdout
        line = next(l for l in text.splitlines() if l.startswith('- PTBR-25'))
        self.assertLess(line.index('Evite: "Você já se perguntou'), line.index('Prefira: "O cadastro falha quando'))
        self.assertNotIn('positive_example', text)

    @requer(PROMPTS)
    def test_skill_material_does_not_copy_approved_prompts(self):
        import re
        prompts = re.findall(r'```text\n(.*?)\n```', (SKILL_DIR / 'results/PROMPTS.md').read_text(encoding='utf-8'), re.S)
        self.assertEqual(len(prompts), 24)

        def grams(text, size=5):
            words = re.findall(r'\w+', text.casefold())
            return {' '.join(words[i:i + size]) for i in range(len(words) - size + 1)}
        approved = set().union(*map(grams, prompts))
        material = [(SKILL_DIR / name).read_text(encoding='utf-8')
                    for name in ('SKILL.md', 'references/catalogo.json', 'references/estilos.json')]
        h = module()
        # Todo briefing que pode entrar no tratamento, não só o da notícia.
        material += [h.brief_text(h.brief(p, g, 2, 0, 17))
                     for p, profile in h.load_profiles().items() for g in profile['genres']]
        for text in material:
            self.assertEqual(grams(text) & approved, set())
        self.assertNotIn('Vila Clara', ''.join(material))

    def test_brief_json_and_every_profile_genre(self):
        h = module()
        for profile_id, profile in h.load_profiles().items():
            for genre in profile['genres']:
                with self.subTest(profile=profile_id, genre=genre):
                    data = h.brief(profile_id, genre)
                    self.assertEqual(data['profile'], profile_id)
                    self.assertEqual(data['genre'], genre)
                    self.assertEqual(len(data['rules']), len(h.load_catalog(SKILL_DIR / 'references/catalogo.json')))
                    self.assertTrue(all(b['required'] for b in data['plan'] if b['required']))
        result = cli_run('brief', '--profile', 'caricato', '--genre', 'cronica', '--format', 'json',
                         '--randomness', '0.4', '--seed', '17')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data, h.brief('caricato', 'cronica', 2, 0.4, 17))
        self.assertEqual(data['kind'], 'writing_brief')
        for args in [('--profile', 'ausente'), ('--profile', 'jornalistico', '--genre', 'conto'),
                     ('--profile', 'jornalistico', '--format', 'xml')]:
            failed = cli_run('brief', *args)
            self.assertEqual(failed.returncode, 2)
            self.assertNotIn('Traceback', failed.stderr)


class DeliveryCheckTests(unittest.TestCase):
    """Verificação final da entrega, com textos reais preservados de 13/10."""

    @requer(RUN_13)
    def test_real_command_only_outputs_are_blocked_and_real_texts_pass(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        texts = generated_13_10()
        self.assertEqual(len(texts), 30)
        command_only = {slot for slot, text in texts.items()
                        if 'saida_somente_comandos' in {b['code'] for b in h.check(text, rules)['blocking']}}
        self.assertEqual(command_only, {'g.01-noticia-bibliotecas.r05.skill', 'g.01-noticia-bibliotecas.r12.skill'})
        preamble = {slot for slot, text in texts.items()
                    if 'preambulo_de_entrega' in {b['code'] for b in h.check(text, rules)['blocking']}}
        self.assertEqual(preamble, {'g.01-noticia-bibliotecas.r05.baseline', 'g.01-noticia-bibliotecas.r11.skill'})
        dashes = {slot for slot, text in texts.items()
                  if 'travessao' in {b['code'] for b in h.check(text, rules)['blocking']}}
        self.assertEqual(dashes, {'g.01-noticia-bibliotecas.r07.baseline', 'g.01-noticia-bibliotecas.r12.baseline',
                                  'g.01-noticia-bibliotecas.r13.baseline'})
        report = h.check(texts['g.01-noticia-bibliotecas.r00.skill'], rules, PROMPT_01)
        self.assertTrue(report['deliverable'])
        self.assertEqual(report['blocking'], [])

    def test_briefing_comparison_flags_inferred_weekday_and_numbers(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        text = 'A Prefeitura anunciou nesta quarta-feira (1º/10) 1.300 vagas. As oficinas começam em 3 de novembro.'
        report = h.check(text, rules, PROMPT_01)
        codes = [(r['code'], r['original']) for r in report['review']]
        self.assertIn(('data_inferida', 'nesta quarta-feira'), codes)
        self.assertIn(('acrescimo_numerico', '1.300'), codes)
        self.assertIn(('omissao_numerica', '1.200'), codes)
        self.assertTrue(report['deliverable'])
        self.assertIn('não prova', report['aviso'])

    def test_em_dash_in_quotes_or_code_is_reported_without_blocking(self):
        # 0.8.0: código basta; citação precisa estar na fonte (pedido ou original).
        h = module()
        text = 'Ele citou: “prazo — curto”. Use `a—b`.'
        report = h.check(text, [], briefing='A fonte disse: “prazo — curto”.')
        self.assertEqual(report['blocking'], [])
        self.assertEqual([r['motivo'] for r in report['review'] if r['code'] == 'travessao_protegido'],
                         ['citação conferida na fonte', 'código'])
        self.assertEqual([b['original'] for b in h.check(text, [])['blocking']], ['—'])
        self.assertFalse(h.check('', [])['deliverable'])
        self.assertFalse(h.check('<tool_call><function=terminal>ls</function></tool_call>', [])['deliverable'])
        mixed = 'Para instalar, rode o comando abaixo no terminal do projeto e confira a versão.\n\n```sh\npython3 -m pip install pacote\n```'
        self.assertTrue(h.check(mixed, [])['deliverable'])

    def test_tool_markup_inside_closed_code_or_quote_is_literal_with_offsets(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        docs = ['A documentação mostra o formato aceito pelo agente no exemplo abaixo:\n\n'
                '```xml\n<tool_call>exemplo</tool_call>\n```\n',
                'O agente rejeita a marcação `<tool_call>` quando ela aparece fora de código no texto final.',
                'O manual cita “<tool_call>exemplo</tool_call>” como formato que o leitor nunca deve copiar.']
        for text in docs:
            with self.subTest(text=text):
                report = h.check(text, rules)
                self.assertTrue(report['deliverable'], report['blocking'])
                literal = [r for r in report['review'] if r['code'] == 'chamada_de_ferramenta_literal']
                self.assertTrue(literal)
                self.assertTrue(all(text[r['start']:r['end']] == r['original'] for r in literal))
        raw = ['<tool_call><function=terminal>ls</function></tool_call>',
               'A documentação mostra o formato aceito pelo agente:\n```xml\n<tool_call>sem fechamento</tool_call>',
               'Texto com aspas abertas "<tool_call>exemplo</tool_call> e mais nada que feche',
               'Exemplo:\n\n```xml\n<tool_call>exemplo</tool_call>\n```\n']
        for text in raw:
            with self.subTest(text=text):
                report = h.check(text, rules)
                self.assertFalse(report['deliverable'])
                self.assertTrue(all(text[b['start']:b['end']] == b['original'] for b in report['blocking'] if 'start' in b))

    def test_explicit_code_artifact_contract_is_opt_in(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        commands = 'python3 -m venv .venv\npip install pacote\n'
        self.assertFalse(h.check(commands, rules)['deliverable'])
        coded = h.check(commands, rules, artifact='codigo')
        self.assertTrue(coded['deliverable'])
        self.assertEqual(coded['artifact'], 'codigo')
        payload = '{"tool_calls": [{"name": "busca"}]}'
        self.assertFalse(h.check(payload, rules)['deliverable'])
        literal = h.check(payload, rules, artifact='codigo')
        self.assertTrue(literal['deliverable'])
        self.assertIn('chamada_de_ferramenta_literal', {r['code'] for r in literal['review']})
        self.assertFalse(h.check('Aqui está o script:\nls -la\n', rules, artifact='codigo')['deliverable'])
        with self.assertRaises(ValueError):
            h.check(commands, rules, artifact='json')
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'saida.txt'
            source.write_text(commands, encoding='utf-8')
            self.assertEqual(cli_run('check', source).returncode, 1)
            self.assertEqual(cli_run('check', source, '--artifact', 'codigo').returncode, 0)
            failed = cli_run('check', source, '--artifact', 'xml')
            self.assertEqual(failed.returncode, 2)
            self.assertNotIn('Traceback', failed.stderr)
        brief = cli_run('brief', '--profile', 'tecnico-preciso', '--genre', 'tecnico').stdout
        self.assertIn('só quando o pedido exigir esse formato', brief)
        self.assertIn('salvo quando o pedido exigir explicitamente', (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8'))

    def test_check_cli_exit_codes_and_readonly(self):
        with tempfile.TemporaryDirectory() as folder:
            good, bad, briefing = [Path(folder) / n for n in ('bom.txt', 'ruim.txt', 'pedido.txt')]
            good.write_text('A Prefeitura abriu 1.200 vagas.', encoding='utf-8')
            bad.write_text('python3 scripts/humanizar.py brief --profile jornalistico\n', encoding='utf-8')
            briefing.write_text(PROMPT_01, encoding='utf-8')
            ok = cli_run('check', good, '--briefing', briefing)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertTrue(json.loads(ok.stdout)['deliverable'])
            blocked = cli_run('check', bad)
            self.assertEqual(blocked.returncode, 1, blocked.stderr)
            self.assertFalse(json.loads(blocked.stdout)['deliverable'])
            missing = cli_run('check', Path(folder) / 'ausente.txt')
            self.assertEqual(missing.returncode, 2)
            self.assertNotIn('Traceback', missing.stderr)
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()), ['bom.txt', 'pedido.txt', 'ruim.txt'])


class Documentation20261019Tests(unittest.TestCase):
    """Contrato documental: sem saída só com comandos e versões coerentes."""

    def test_skill_forbids_command_only_answers_and_handles_missing_terminal(self):
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('scripts/humanizar.py brief', skill)
        self.assertIn('scripts/humanizar.py check', skill)
        self.assertRegex(skill, r'Sem terminal')
        self.assertRegex(skill, r'Nunca responda apenas com comandos')
        for profile in ['coloquial', 'informal', 'caricato']:
            self.assertIn(f'`{profile}`', skill)
        self.assertIn('norma culta', skill)
        self.assertIn('nova revisão não trouxer melhoria concreta', skill)

    def test_frontmatter_description_is_json_quoted(self):
        # JSON entre aspas é YAML válido mesmo com ': ' no texto.
        import re
        line = re.search(r'^description: (.*)$', (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8'), re.M).group(1)
        self.assertIsInstance(json.loads(line), str)

    @requer(README)
    def test_versions_and_documented_lookup_commands_are_consistent(self):
        import re
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        version = re.search(r'^version: (\S+)$', skill, re.M).group(1)
        self.assertEqual(module().VERSION, version)
        self.assertIn(f'# Humanizador PT-BR {version}', (SKILL_DIR / 'README.md').read_text(encoding='utf-8'))
        self.assertIn(f'Humanizador PT-BR {version}', (SKILL_DIR.parents[1] / 'README.md').read_text(encoding='utf-8'))
        for doc in [SKILL_DIR / 'SKILL.md', SKILL_DIR / 'README.md']:
            text = doc.read_text(encoding='utf-8')
            self.assertNotIn('—', text)
            for line in re.findall(r'^python3 scripts/humanizar\.py ((?:catalog|styles|structure|brief) .*)$', text, re.M):
                with self.subTest(doc=doc.name, line=line):
                    args = [a.strip('"') for a in re.findall(r'"[^"]*"|\S+', line)]
                    result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *args],
                                            capture_output=True, text=True, cwd=SKILL_DIR)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertTrue(result.stdout.strip())


VAGUE_PREFERENCE = r'(?i)\b(?:informad[oa]s?|descrit[oa]s?|indicad[oa]s?|citad[oa]s?|acompanhad[oa]s?|briefing)\b'


class Catalog070Tests(unittest.TestCase):
    """0.7.0: termos explícitos, forma preferida concreta e lacunas de naturalidade."""

    def rules(self):
        return module().load_catalog(SKILL_DIR / 'references/catalogo.json')

    def count(self, text, rule_id):
        return module().audit(text, self.rules())['rule_counts'][rule_id]['count']

    def test_every_rule_lists_terms_and_a_concrete_preferred_form(self):
        import re
        h = module()
        rules = self.rules()
        self.assertEqual(len(rules), 32)
        described = {'PTBR-21', 'PTBR-26', 'PTBR-28'}  # o vício é descrito, sem o símbolo no texto
        for rule in rules:
            with self.subTest(rule=rule['id']):
                self.assertTrue(rule.get('avoid'), 'Toda regra precisa de termos explícitos')
                self.assertTrue(all(isinstance(t, str) and t.strip() for t in rule['avoid']))
                self.assertIsNone(re.search(VAGUE_PREFERENCE, rule['negative_example']),
                                  'A forma preferida deve dizer algo concreto, sem remeter a dado "informado"')
                self.assertEqual(h.audit(rule['negative_example'], rules)['findings'], [],
                                 'A forma preferida não pode conter vício do catálogo')
                if rule['id'] not in described:
                    self.assertGreaterEqual(h.audit(rule['positive_example'], [rule])['rule_counts'][rule['id']]['count'], 1,
                                            'O exemplo de vício precisa ser detectado pela própria regra')

    def test_naturalness_gaps_are_detected_without_literal_false_positives(self):
        cases = {
            'PTBR-29': (['Para realizar o pagamento, acesse o aplicativo.', 'A loja efetuou a entrega ontem.',
                         'Ela realizou uma análise dos dados.', 'O time trabalhou de forma eficiente.'],
                        ['Ela realizou o sonho de viajar.', 'O pagamento saiu ontem.', 'Trabalhou de forma isolada.']),
            'PTBR-30': (['A iniciativa visa fortalecer o comércio local.', 'O projeto busca incentivar a leitura.',
                         'A campanha tem como objetivo ampliar o acesso.', 'A feira abriu, reforçando o compromisso com o bairro.'],
                        ['A feira abre no sábado e reúne produtores da região.', 'Ele busca o filho na escola.']),
            'PTBR-31': (['Um silêncio pesado tomou a sala.', 'O tempo pareceu parar.', 'Senti um nó na garganta.',
                         'E foi ali que eu entendi tudo.', 'Ela soltou o ar que nem sabia que prendia.'],
                        ['O silêncio durou dois minutos.', 'O relógio parou às três.', 'Ali eu deixei a chave.']),
            'PTBR-32': (['A equipe vai endereçar o problema na próxima versão.', 'Ela aplicou para a vaga de analista.',
                         'O anúncio performou bem.'],
                        ['O envelope foi endereçado ao cliente.', 'Ela aplicou a tinta na parede.',
                         'A performance do servidor caiu.']),
        }
        for rule_id, (positives, negatives) in cases.items():
            for text in positives:
                with self.subTest(rule=rule_id, text=text):
                    self.assertGreaterEqual(self.count(text, rule_id), 1)
            for text in negatives:
                with self.subTest(rule=rule_id, text=text):
                    self.assertEqual(self.count(text, rule_id), 0)

    def test_common_variants_of_existing_vices_are_detected(self):
        for text, rule_id in [('Vale lembrar que o prazo acabou.', 'PTBR-03'),
                              ('Nesse contexto, o prazo acabou.', 'PTBR-04'),
                              ('O app não é só um cadastro, mas uma vitrine.', 'PTBR-05'),
                              ('O setor desempenha um papel essencial.', 'PTBR-07'),
                              ('O botão mudou, reforçando a marca.', 'PTBR-12'),
                              ('Desvendando os segredos do cadastro.', 'PTBR-23')]:
            with self.subTest(text=text):
                self.assertEqual(self.count(text, rule_id), 1)

    def test_service_box_is_a_listed_exception_for_labeled_lists(self):
        h = module()
        self.assertIn('PTBR-20', [r['id'] for r in h.search_catalog(self.rules(), 'quadro de serviço')])

    def test_purpose_rule_example_keeps_exactly_the_facts(self):
        import re
        rule = next(r for r in self.rules() if r['id'] == 'PTBR-30')

        def words(text):
            return set(re.findall(r'\w+', text.casefold()))
        self.assertLessEqual(words(rule['negative_example']), words(rule['positive_example']),
                             'A forma preferida de finalidade-presumida não pode acrescentar fato ausente do vício')
        self.assertEqual(module().audit(rule['negative_example'], [rule])['rule_counts']['PTBR-30']['count'], 0)


# Pares perfil/gênero fixados pelo runner (SELECTORS), mais um par neutro de relatório.
GENRE_PLANS = {('jornalistico', 'noticia'): 'noticia', ('jornalistico', 'reportagem'): 'reportagem',
               ('tecnico-preciso', 'tecnico'): 'procedimento', ('tecnico-preciso', 'relatorio'): 'relatorio',
               ('didatico', 'didatico'): 'explicacao', ('academico', 'academico'): 'academico',
               ('executivo-direto', 'proposta'): 'proposta', ('executivo-direto', 'negocios'): 'nota-executiva',
               ('executivo-direto', 'relatorio'): 'nota-executiva', ('conversacional-contido', 'email'): 'mensagem',
               ('argumentativo-sobrio', 'artigo'): 'argumento', ('argumentativo-sobrio', 'ensaio'): 'ensaio',
               ('conversacional-contido', 'post'): 'post', ('conversacional-contido', 'roteiro'): 'roteiro',
               ('literario', 'conto'): 'cena', ('literario', 'cronica'): 'cronica',
               ('neutro-claro', 'relatorio'): 'relatorio'}


class Structure070Tests(unittest.TestCase):
    """0.7.0: cada gênero recebe plano próprio, com ofício, vícios típicos e regra de material."""

    def test_each_genre_gets_its_own_plan(self):
        h = module()
        for (profile, genre), expected in GENRE_PLANS.items():
            with self.subTest(profile=profile, genre=genre):
                self.assertEqual(h.generate_structure(profile, genre, 2, 0, 17)['structure_id'], expected)
        for profile in h.load_profiles().values():
            if 'relatorio' in profile['genres']:
                with self.subTest(profile=profile['id']):
                    self.assertNotEqual(h.generate_structure(profile['id'], 'relatorio')['structure_id'], 'procedimento',
                                        'Relatório não pode receber o plano de comandos da documentação técnica')
        self.assertEqual(h.generate_structure('jornalistico', 'noticia', 0)['blocks'][0]['id'], 'titulo')

    def test_every_structure_carries_craft_focus_and_material(self):
        data = json.loads((SKILL_DIR / 'references/estilos.json').read_text(encoding='utf-8'))
        rules = {r['id'] for r in module().load_catalog(SKILL_DIR / 'references/catalogo.json')}
        self.assertEqual(set(data['material']), {'fatos', 'opiniao', 'ficcao'})
        self.assertTrue(all(isinstance(v, str) and v.strip() for v in data['material'].values()))
        for structure in data['structures']:
            with self.subTest(structure=structure['id']):
                self.assertTrue(structure.get('name'))
                self.assertTrue(3 <= len(structure.get('craft', [])) <= 6)
                self.assertTrue(all(isinstance(c, str) and c.strip() for c in structure['craft']))
                self.assertTrue(3 <= len(structure.get('focus', [])) <= 6)
                self.assertLessEqual(set(structure['focus']), rules)
                self.assertIn(structure.get('material'), data['material'])
        material = {s['id']: s['material'] for s in data['structures']}
        self.assertEqual({k for k, v in material.items() if v == 'ficcao'}, {'cena', 'cronica'})
        self.assertEqual({k for k, v in material.items() if v == 'opiniao'}, {'argumento', 'ensaio'})
        invented = [item for item in data['forbidden'] if 'inventada' in item]
        self.assertTrue(invented and all('não ficção' in item for item in invented),
                        'A proibição de vivência inventada vale para não ficção, não para conto e crônica')


class Brief070Tests(unittest.TestCase):
    """0.7.0: o briefing começa pelo ofício do gênero e termina no contrato de entrega."""

    def pairs(self):
        return [(p, g) for p, profile in module().load_profiles().items() for g in profile['genres']]

    def test_brief_leads_with_genre_craft_and_ends_with_delivery(self):
        h = module()
        data = json.loads((SKILL_DIR / 'references/estilos.json').read_text(encoding='utf-8'))
        structures = {s['id']: s for s in data['structures']}
        for profile, genre in self.pairs():
            with self.subTest(profile=profile, genre=genre):
                brief = h.brief(profile, genre, 2, 0, 17)
                text = h.brief_text(brief)
                structure = structures[brief['structure_id']]
                self.assertEqual(brief['craft'], structure['craft'])
                self.assertEqual(brief['material'], structure['material'])
                for item in structure['craft']:
                    self.assertIn(item, text)
                self.assertIn(data['material'][structure['material']], text)
                marks = ['Ofício do gênero: ' + structure['name'], 'Plano:', 'Perfil ' + profile,
                         'Pontos de atenção do gênero', 'Demais regras do catálogo', '\nEntrega\n']
                positions = [text.index(mark) for mark in marks]
                self.assertEqual(positions, sorted(positions))
                self.assertIn('não seções', text)
                self.assertTrue(text.rstrip().endswith('melhoria concreta.'))

    def test_fiction_invites_invention_and_nonfiction_keeps_fidelity(self):
        for profile, genre in [('literario', 'conto'), ('literario', 'cronica'),
                               ('coloquial', 'conto'), ('caricato', 'cronica')]:
            with self.subTest(profile=profile, genre=genre):
                text = cli_run('brief', '--profile', profile, '--genre', genre).stdout
                self.assertIn('Invente cena', text)
                self.assertNotIn('só com fatos do pedido', text)
                self.assertNotIn('fala ou vivência ausentes', text)
                self.assertIn('em não ficção', text)
        news = cli_run('brief', '--profile', 'jornalistico', '--genre', 'noticia').stdout
        self.assertIn('Use só fatos', news)
        self.assertIn('dia da semana', news)
        self.assertNotIn('Invente cena', news)
        essay = cli_run('brief', '--profile', 'argumentativo-sobrio', '--genre', 'ensaio').stdout
        self.assertIn('apresentados como hipótese', essay)

    def test_focus_rules_follow_the_genre_priority(self):
        h = module()
        brief = h.brief('jornalistico', 'noticia')
        text = h.brief_text(brief)
        self.assertEqual(brief['focus'][0], 'PTBR-30')
        positions = [text.index(f'- {rule_id} ') for rule_id in brief['focus']]
        self.assertEqual(positions, sorted(positions))
        self.assertTrue(all(r['foco'] == (r['id'] in brief['focus']) for r in brief['rules']))
        self.assertLess(positions[-1], text.index('Demais regras do catálogo'))


class Material070Tests(unittest.TestCase):
    """Material por gênero é padrão; o tipo pedido (fato, opinião ou ficção) prevalece."""

    def test_brief_marks_default_material_and_states_conditional_rules(self):
        h = module()
        data = json.loads((SKILL_DIR / 'references/estilos.json').read_text(encoding='utf-8'))
        for profile, genre, default in [('conversacional-contido', 'roteiro', 'fatos'),
                                        ('literario', 'cronica', 'ficcao')]:
            with self.subTest(profile=profile, genre=genre):
                brief = h.brief(profile, genre, 2, 0, 17)
                self.assertEqual(brief['material'], default, 'O padrão da matriz aprovada não muda')
                text = h.brief_text(brief)
                self.assertIn('o tipo de texto pedido (fato, opinião ou ficção) prevalece', text)
                lines = text.splitlines()
                default_line = next(l for l in lines if data['material'][default] in l)
                self.assertTrue(default_line.startswith('- Padrão do gênero, ' + data['material_types'][default]['label']))
                for other, kind in data['material_types'].items():
                    if other != default:
                        self.assertIn('- ' + kind['when_requested'], lines)
                # Nenhuma ordem de inventar ou de restringir aos fatos fica incondicional.
                for line in lines:
                    if 'invente' in line.casefold() or 'use só' in line.casefold():
                        self.assertTrue(line.startswith('- Padrão do gênero') or line.startswith('- Se o pedido for'), line)

    def test_skill_states_that_the_request_sets_the_material(self):
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        section = skill[skill.index('## Fidelidade'):skill.index('## Catálogo e estilo')]
        self.assertIn('O pedido define se o texto é fato, opinião ou ficção', section)
        self.assertIn('prevalece', section)
        for label in ['- Fato:', '- Opinião:', '- Ficção:']:
            self.assertIn(label, section)


class Skill070Tests(unittest.TestCase):
    """0.7.0: orientação editorial positiva antes dos vetos, contrato de Ricardo preservado."""

    FINAL_VALIDATION = ('Não economize tokens ou tempo. Substitua blocos, expressões ou palavras iterativamente '
                        'até atingir o resultado ideal, iterando e repetindo quantas vezes forem necessárias. '
                        'Finalize quando o texto atender ao pedido, preservar fatos e voz e uma nova revisão '
                        'não trouxer melhoria concreta.')

    def skill(self):
        return (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')

    def test_positive_craft_comes_before_the_explicit_vice_list(self):
        skill = self.skill()
        self.assertLess(skill.index('## Como escrever bem'), skill.index('## Evite explicitamente'))
        craft = skill[skill.index('## Como escrever bem'):skill.index('## Evite explicitamente')]
        for idea in ['leitor', 'matéria-prima', 'gênero completo', 'ritmo', 'concreto']:
            self.assertIn(idea, craft)

    def test_required_contract_survives_the_rewrite(self):
        # 0.9.0: o plano aprovado em 22/10/2026 troca a "Validação final" pelo critério de parada
        # (seção 3.2 e escolha editorial 2). O bloco antigo deixa de ser exigido literalmente.
        skill = self.skill()
        self.assertRegex(skill, r'(?m)^version: 0\.9\.\d+$')
        self.assertIn('NÃO USE travessão U+2014 na prosa produzida', skill)
        self.assertNotIn(self.FINAL_VALIDATION, skill)
        self.assertTrue(skill.rstrip().endswith('nova revisão não trouxer melhoria concreta.'))
        for item in ['Redação:', 'Revisão:', 'Diagnóstico:', 'Ficção', 'Exemplos editoriais não são fatos reutilizáveis',
                     'references/catalogo.json', 'references/estilos.json']:
            self.assertIn(item, skill)
        self.assertLessEqual(len(skill), 9100)

    @requer(LEGACY_13)
    def test_treatment_fits_the_frozen_runner_budget(self):
        # 0.8.0: o runner congelado exige tratamento abaixo de 40% do v1 de 13/10 (48.850 caracteres).
        # O teto geral evita inchaço nos pares fora do runner. Caracteres, não tokens.
        h = module()
        legacy = SKILL_DIR / 'results/scripts/fixtures/evidence-2026-10-13/frozen/skill'
        budget = 0.4 * sum(len((legacy / p).read_text(encoding='utf-8'))
                           for p in ('SKILL.md', 'references/catalogo.json', 'references/estilos.json'))
        runner = {('jornalistico', 'noticia'), ('jornalistico', 'reportagem'), ('tecnico-preciso', 'tecnico'),
                  ('tecnico-preciso', 'relatorio'), ('didatico', 'didatico'), ('academico', 'academico'),
                  ('executivo-direto', 'proposta'), ('executivo-direto', 'negocios'), ('executivo-direto', 'relatorio'),
                  ('conversacional-contido', 'email'), ('conversacional-contido', 'post'),
                  ('conversacional-contido', 'roteiro'), ('argumentativo-sobrio', 'artigo'),
                  ('argumentativo-sobrio', 'ensaio'), ('literario', 'conto'), ('literario', 'cronica')}
        skill = len(self.skill())
        for profile, data in h.load_profiles().items():
            for genre in data['genres']:
                with self.subTest(profile=profile, genre=genre):
                    size = skill + len(h.brief_text(h.brief(profile, genre, 2, 0, 17)))
                    self.assertLess(size, budget if (profile, genre) in runner else 20500)


class Literal080Tests(unittest.TestCase):
    """0.8.0: um único reconhecedor de literais para edição, comparação e entrega."""

    def test_multi_backtick_code_and_long_fences_protect_their_content(self):
        h = module()
        self.assertEqual(h.plan_replacements('``vale destacar``', 'vale destacar', 'destaco')['edits'], [])
        fence = '````md\n```\nvale destacar\n```\nvale destacar\n````\nvale destacar fora.'
        plan = h.plan_replacements(fence, 'vale destacar', 'destaco')
        self.assertEqual([e['start'] for e in plan['edits']], [fence.rindex('vale destacar')])
        self.assertEqual(h.plan_replacements('«vale destacar»', 'vale destacar', 'destaco')['edits'], [])

    def test_closed_quotes_recognized_by_check_are_the_ones_protected_in_editing(self):
        h = module()
        for text in ['‘prazo — curto’', '"prazo\n— curto"', '«prazo — curto»', '“O prazo\n— curto”']:
            with self.subTest(text=text):
                report = h.check(text, [], briefing=text)
                self.assertTrue(report['deliverable'], report['blocking'])
                self.assertIn('travessao_protegido', {r['code'] for r in report['review']})
                start = text.index('—')
                with self.assertRaises(ValueError):
                    h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [
                        {'start': start, 'end': start + 1, 'original': '—', 'replacement': ',', 'approved': True}]})
        # Aspas abertas e apóstrofos não viram literal fechado na entrega.
        for text in ['Ela disse "prazo — curto', 'A caixa-d\'água — e a bomba — falharam no pau-d\'alho.']:
            with self.subTest(text=text):
                self.assertIn('travessao', {b['code'] for b in h.check(text, [], briefing=text)['blocking']})


class Origin080Tests(unittest.TestCase):
    """0.8.0: aspas delimitam, mas só a fonte comprova que o travessão é original."""

    def test_new_dialogue_in_quotes_cannot_carry_an_em_dash(self):
        h = module()
        text = '“Agora — espere.”'
        self.assertIn('travessao', {b['code'] for b in h.check(text, [], briefing='Escreva um diálogo novo.')['blocking']})
        self.assertIn('travessao', {b['code'] for b in h.check(text, [])['blocking']})
        quoted = h.check('A diretora disse: “Agora — espere.”', [], briefing='Fala da diretora: “Agora — espere.”')
        self.assertTrue(quoted['deliverable'], quoted['blocking'])
        self.assertIn('travessao_protegido', {r['code'] for r in quoted['review']})

    def test_literal_name_and_unchanged_original_sentence_keep_their_dash(self):
        h = module()
        named = h.check('O protocolo A—B entra em teste.', [], briefing='Use o nome exato do protocolo A—B.')
        self.assertTrue(named['deliverable'], named['blocking'])
        original = 'O prazo — que já venceu — foi mantido. Vale destacar que a sala mudou.'
        revised = 'O prazo — que já venceu — foi mantido. A sala mudou.'
        kept = h.check(revised, [], original=original)
        self.assertTrue(kept['deliverable'], kept['blocking'])
        edited = h.check('O prazo — que venceu — foi mantido. A sala mudou.', [], original=original)
        self.assertIn('travessao', {b['code'] for b in edited['blocking']})
        added = h.check(revised + ' A equipe — enfim — voltou.', [], original=original)
        self.assertEqual([b['original'] for b in added['blocking'] if b['code'] == 'travessao'], ['—', '—'])
        self.assertIn('travessao', {b['code'] for b in h.check(original, [], briefing=original)['blocking']},
                      'Prosa do pedido copiada não é citação; só o original da revisão comprova a frase inteira')

    def test_check_cli_accepts_the_original_for_revisions(self):
        with tempfile.TemporaryDirectory() as folder:
            original, revised = Path(folder) / 'original.txt', Path(folder) / 'revisado.txt'
            original.write_text('O prazo — que já venceu — foi mantido. Vale destacar que a sala mudou.', encoding='utf-8')
            revised.write_text('O prazo — que já venceu — foi mantido. A sala mudou.', encoding='utf-8')
            self.assertEqual(cli_run('check', revised).returncode, 1)
            result = cli_run('check', revised, '--original', original)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class Delivery080Tests(unittest.TestCase):
    """0.8.0: formato da entrega pelo conteúdo, não pela extensão da explicação."""

    def rules(self):
        return module().load_catalog(SKILL_DIR / 'references/catalogo.json')

    def blocking(self, text, **options):
        return {b['code'] for b in module().check(text, self.rules(), **options)['blocking']}

    def test_bare_commands_other_executables_and_json_are_not_prose(self):
        for text in ['ls', 'curl https://exemplo.test', 'git status\n']:
            with self.subTest(text=text):
                self.assertIn('saida_somente_comandos', self.blocking(text))
        for text in ['{"titulo": "Cadastro"}', '[{"id": 1}]']:
            with self.subTest(text=text):
                self.assertIn('saida_somente_json', self.blocking(text))
                self.assertEqual(self.blocking(text, artifact='codigo'), set())

    def test_short_technical_answers_with_fenced_commands_are_deliverable(self):
        for text in ['Execute:\n```sh\nls -la\n```', 'Rode o comando.\n\n```sh\npython3 -m pip install pacote\n```']:
            with self.subTest(text=text):
                self.assertEqual(self.blocking(text), set())
        for text in ['Vou rodar:\n```sh\npython3 scripts/humanizar.py brief --profile jornalistico\n```',
                     'Exemplo:\n\n```xml\n<tool_call>exemplo</tool_call>\n```\n']:
            with self.subTest(text=text):
                self.assertIn('saida_somente_comandos', self.blocking(text))

    def test_preamble_after_courtesy_or_markdown_blocks_and_list_intro_does_not(self):
        for text in ['Claro!\nAqui está a notícia:\nO cadastro foi aberto.',
                     '**Aqui está a notícia:**\n\nO cadastro foi aberto.',
                     'Segue o e-mail revisado:\nPrezada equipe,']:
            with self.subTest(text=text):
                self.assertIn('preambulo_de_entrega', self.blocking(text))
        for text in ['Seguem os documentos:\n- contrato\n- recibo', 'Abaixo estão os horários:\n- 9h\n- 14h']:
            with self.subTest(text=text):
                report = module().check(text, self.rules())
                self.assertTrue(report['deliverable'], report['blocking'])
                self.assertIn('PTBR-27', {r.get('rule_id') for r in report['review']})

    def test_relative_dates_signs_percentages_and_whole_words(self):
        h = module()
        briefing = 'O cadastro abre em 1º de outubro de 2026, com saldo de -20 reais e taxa de 20%.'

        def review(text, source=briefing):
            return {(r['code'], r['original']) for r in h.check(text, [], briefing=source)['review']}
        for expression in ['nesta quinta', 'na terça', 'próxima sexta', 'esta semana', 'semana que vem',
                           'na terca-feira', 'no sabado', 'hoje']:
            with self.subTest(expression=expression):
                self.assertIn(('data_inferida', expression), review(f'O cadastro abre {expression}.'))
        for text in ['O cadastro vence na segunda etapa.', 'Ela está na quinta série.']:
            with self.subTest(text=text):
                self.assertNotIn('data_inferida', {code for code, _ in review(text)})
        self.assertNotIn('data_inferida', {c for c, _ in review('Abre na quinta-feira.', 'Abre quinta-feira, 2/10.')})
        self.assertIn(('data_inferida', 'domingo'), review('A entrega será domingo.', 'Domingos revisou o aviso.'))
        numbers = review('Saldo de 20 reais e taxa de 20.')
        self.assertIn(('omissao_numerica', '-20'), numbers)
        self.assertIn(('omissao_numerica', '20%'), numbers)
        self.assertIn(('acrescimo_numerico', '20'), numbers)
        coded = review('A rota responde assim:\n\n```text\nHTTP 404\n```\n\nConfira o painel.', 'Explique a rota.')
        self.assertNotIn(('acrescimo_numerico', '404'), coded)
        self.assertIn(('acrescimo_numerico', '404'), review('A rota responde 404.', 'Explique a rota.'))


class Protection080Tests(unittest.TestCase):
    """0.8.0: negações em NFD, abreviações e ordinais continuam protegidos."""

    def test_decomposed_negation_and_abbreviated_condition_keep_their_clause(self):
        h = module()
        self.assertEqual(h.plan_replacements('não aceito.', 'aceito', 'recuso')['edits'], [])
        self.assertEqual(h.plan_replacements('se o sr. pedir, aceite.', 'aceite', 'recuse')['edits'], [])
        self.assertEqual(h.plan_replacements('se ele disser "ok. pronto", aceite.', 'aceite', 'recuse')['edits'], [])
        text = 'não aceito.'
        self.assertFalse(h.verify(text, 'aceito.')['protected_content_preserved'])
        self.assertEqual(len(h.plan_replacements('Ele aceitou. Depois aceite.', 'aceite', 'recuse')['edits']), 1)

    def test_ordinal_and_degree_marks_belong_to_the_number(self):
        h = module()
        for text, mark in [('em 1º de outubro', 'º'), ('na 2ª chamada', 'ª'), ('a 20° de inclinação', '°')]:
            start = text.index(mark)
            with self.subTest(text=text), self.assertRaises(ValueError):
                h.apply_edits(text, {'input_sha256': h.sha256(text), 'edits': [
                    {'start': start, 'end': start + 1, 'original': mark, 'replacement': '', 'approved': True}]})


NEW_FACT = (r'(?i)\d|\b(?:janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro'
            r'|segunda|terça|quarta|quinta|sexta|sábado|domingo|hoje|amanhã|ontem|dois|duas|três|quatro|cinco|seis'
            r'|sete|oito|nove|dez|cem|mil|metade|dobro|todas?|todos)\b')
# Substitutos linguísticos admitidos na forma preferida: verbo no lugar da perífrase,
# conector, cópula e contrações. Nenhum acrescenta fato.
LINGUISTIC = {'há', 'também', 'além', 'da', 'do', 'para', 'é', 'pagar', 'tratar'}
NEGATIONS = {'não', 'nunca', 'jamais', 'nem', 'sem'}
MODALS = {'pode', 'podem', 'poderia', 'poderiam', 'possa', 'talvez', 'possivelmente', 'provavelmente', 'deve', 'devem'}


class Catalog080Tests(unittest.TestCase):
    """0.8.0: pares que só retiram o vício e detectores alinhados aos termos declarados."""

    def rules(self):
        return module().load_catalog(SKILL_DIR / 'references/catalogo.json')

    def count(self, text, rule_id):
        return module().audit(text, self.rules())['rule_counts'][rule_id]['count']

    def test_preferred_form_only_removes_the_vice(self):
        import re

        def words(text):
            return re.findall(r'\w+', text.casefold())
        described = {'PTBR-21', 'PTBR-26', 'PTBR-28'}
        creation = {'PTBR-31'}  # ficção: troca emoção pronta por gesto, sem número nem data novos
        for rule in self.rules():
            if rule['id'] in described:
                continue
            vice, preferred = words(rule['positive_example']), words(rule['negative_example'])
            with self.subTest(rule=rule['id']):
                fresh = set(preferred) - set(vice)
                self.assertEqual({w for w in fresh if re.search(NEW_FACT, w)}, set(), 'número, data ou alcance novo')
                if rule['id'] not in creation:
                    self.assertLessEqual(fresh, LINGUISTIC, 'a forma preferida não pode trazer fato ausente do vício')
                if rule['id'] != 'PTBR-05':  # o vício de PTBR-05 é a própria negação encenada
                    self.assertEqual(sum(w in NEGATIONS for w in preferred), sum(w in NEGATIONS for w in vice))
                self.assertEqual(set(preferred) & MODALS, set(vice) & MODALS, 'modalidade e certeza preservadas')

    def test_declared_terms_are_detected_and_literal_uses_are_not(self):
        schematic = {'PTBR-20', 'PTBR-21', 'PTBR-26', 'PTBR-28'}
        h = module()
        for rule in self.rules():
            if rule['id'] in schematic:
                continue
            for term in rule['avoid']:
                with self.subTest(rule=rule['id'], term=term):
                    self.assertGreaterEqual(h.audit(term, [rule])['rule_counts'][rule['id']]['count'], 1)
        for text, rule_id in [('Precisamos endereçar um problema.', 'PTBR-32'), ('Otimizamos o fluxo.', 'PTBR-11'),
                              ('Potencializamos os resultados.', 'PTBR-11'), ('Processos otimizados.', 'PTBR-11'),
                              ('O projeto foi fomentado.', 'PTBR-11'), ('Estudos recentes mostram que caiu.', 'PTBR-06'),
                              ('Pesquisas indicam queda.', 'PTBR-06'), ('Para concluir, o prazo acabou.', 'PTBR-24'),
                              ('- **Prazo:** O prazo é amanhã.', 'PTBR-20'), ('**Aqui está a notícia:**', 'PTBR-27')]:
            with self.subTest(text=text):
                self.assertGreaterEqual(self.count(text, rule_id), 1)
        for text, rule_id in [('Para concluir o pagamento, abra o aplicativo.', 'PTBR-24'),
                              ('- **Prazo:** 5 a 16 de outubro.', 'PTBR-20'), ('Explique de forma clara.', 'PTBR-29'),
                              ('Guarde a senha de forma segura.', 'PTBR-29'), ('Estudos do instituto mostram queda.', 'PTBR-06'),
                              ('A agência de fomento aprovou.', 'PTBR-11'), ('A otimização convexa converge.', 'PTBR-11')]:
            with self.subTest(text=text):
                self.assertEqual(self.count(text, rule_id), 0)


class Brief080Tests(unittest.TestCase):
    """0.8.0: orientação e exceções chegam ao texto; modos e lacunas sem pressão de reescrita."""

    def test_text_brief_carries_guidance_and_exceptions_of_the_catalog(self):
        h = module()
        for profile, genre in [('jornalistico', 'noticia'), ('academico', 'academico'), ('literario', 'conto')]:
            with self.subTest(profile=profile, genre=genre):
                data = h.brief(profile, genre)
                text = h.brief_text(data)
                for rule in data['rules']:
                    for exception in rule['excecoes']:
                        self.assertIn(exception, text)
                    if rule['foco']:
                        self.assertIn('Como: ' + rule['como'], text)
                self.assertIn('Pontos de atenção do gênero', text)
                self.assertNotIn('Vícios mais comuns', text)
                self.assertNotIn('–', text, 'meia-risca descrita, sem o glifo')
                self.assertNotIn('equipe de suporte, os erros de cadastro caíram pela metade', text)
        self.assertIn('estatística robusta', h.brief_text(h.brief('academico', 'academico')).casefold())
        self.assertIn('ocorrência isolada', h.brief_text(h.brief('jornalistico', 'noticia')).casefold())

    def test_delivery_contract_distinguishes_writing_revision_and_diagnosis(self):
        h = module()
        text = h.brief_text(h.brief('neutro-claro', 'artigo'))
        delivery = text[text.index('\nEntrega\n'):]
        for mode in ['Redação:', 'Revisão:', 'Diagnóstico:']:
            self.assertIn(mode, delivery)
        self.assertIn('não troque a voz', delivery)
        self.assertNotIn('As frases são suas', delivery)
        self.assertTrue(text.rstrip().endswith('melhoria concreta.'))

    def test_factual_policy_is_the_same_in_skill_and_brief(self):
        skill = (SKILL_DIR / 'SKILL.md').read_text(encoding='utf-8')
        news = cli_run('brief', '--profile', 'jornalistico', '--genre', 'noticia').stdout
        for text in [skill, news]:
            with self.subTest(source=text[:30]):
                self.assertIn('verificada nesta tarefa', text)
        self.assertIn('não divulgado', skill)
        self.assertIn('hipótese', skill[skill.index('## Fidelidade'):skill.index('## Catálogo e estilo')])


class Structure080Tests(unittest.TestCase):
    """0.8.0: instruções locais condicionadas ao material e pares de perfil compatíveis."""

    def brief(self, profile, genre):
        return module().brief_text(module().brief(profile, genre))

    def test_blocks_do_not_demand_material_the_request_may_lack(self):
        cases = [('jornalistico', 'reportagem', ['não invente aspas'], ['Dê voz às fontes com falas literais']),
                 ('conversacional-contido', 'email', ['quando o pedido trouxer o nome'], ['Saudação pelo nome;']),
                 ('didatico', 'didatico', ['conta só quando'], ['mostre contas com unidades']),
                 ('academico', 'academico', ['texto teórico'], ['Apresente os resultados com números e']),
                 ('literario', 'cronica', ['Pessoa narrativa do pedido'], ['Primeira pessoa próxima']),
                 ('executivo-direto', 'proposta', ['só se o pedido o indicar'], ['Defina entrega, exclusões e responsável']),
                 ('conversacional-contido', 'roteiro', ['em fala sem tela'], [])]
        for profile, genre, present, absent in cases:
            with self.subTest(profile=profile, genre=genre):
                text = self.brief(profile, genre)
                for item in present:
                    self.assertIn(item, text)
                for item in absent:
                    self.assertNotIn(item, text)

    def test_technical_email_and_argumentative_post_keep_genre_and_register(self):
        h = module()
        self.assertEqual(h.generate_structure('tecnico-preciso', 'email')['structure_id'], 'mensagem')
        self.assertEqual(h.generate_structure('tecnico-preciso')['structure_id'], 'procedimento')
        post = h.brief('argumentativo-sobrio', 'post')
        self.assertEqual(post['genre'], 'post')
        self.assertIn('post', post['genre_name'].casefold())
        self.assertIn('Conservar terminologia e qualificadores', self.brief('tecnico-preciso', 'email'))


DRAFT_090 = ('Assunto: Mudança no prazo de entrega\n\nPrezada Ana Ribeiro,\n\n'
             'O lote de 20 kg não será enviado antes de 15 de março de 2027. Se o fornecedor confirmar, '
             'a entrega pode sair até 20 de março. O laudo está em https://exemplo.test/laudo e o '
             'responsável disse: “Não há risco para o pedido.” Envie o formulário e o comprovante.\n\n'
             'Atenciosamente,\nEquipe de Logística')
FIELDS_090 = {'campos': [
    {'tipo': 'assunto', 'valor': 'Assunto: Mudança no prazo de entrega'},
    {'tipo': 'saudacao', 'valor': 'Prezada Ana Ribeiro,'},
    {'tipo': 'nome', 'valor': 'Ana Ribeiro'},
    {'tipo': 'numero', 'valor': '20 kg'},
    {'tipo': 'data', 'valor': '15 de março de 2027'},
    {'tipo': 'url', 'valor': 'https://exemplo.test/laudo'},
    {'tipo': 'citacao', 'valor': '“Não há risco para o pedido.”'},
    {'tipo': 'assinatura', 'valor': 'Equipe de Logística'}]}


class Campos090Tests(unittest.TestCase):
    """0.9.0: verify --campos marca cada campo declarado e só descreve o resto."""

    def states(self, revised, fields=FIELDS_090):
        report = module().verify_fields(DRAFT_090, revised, fields)
        return {(c['tipo'], c['valor']): c['estado'] for c in report['campos']}, report

    def test_unchanged_and_legitimately_restructured_texts_keep_every_field(self):
        same, report = self.states(DRAFT_090)
        self.assertEqual(set(same.values()), {'preservado'})
        self.assertEqual(report['resumo'], {'declarados': 8, 'preservado': 8, 'alterado': 0, 'ausente': 0,
                                            'ausente_na_referencia': 0})
        revised = ('Assunto: Mudança no prazo de entrega\n\nPrezada Ana Ribeiro,\n\n'
                   'O lote de 20 kg sai depois de 15 de março de 2027, não antes. Se o fornecedor confirmar, '
                   'a entrega pode sair até 20 de março. O responsável garantiu: "Não há risco para o pedido." '
                   'Laudo: https://exemplo.test/laudo. Envie o formulário e o comprovante.\n\n'
                   'Atenciosamente,\nEquipe de Logística')
        states, report = self.states(revised)
        self.assertEqual(set(states.values()), {'preservado'}, states)
        self.assertNotIn('protected_content_preserved', report, 'inventário inteiro não é veredito na reescrita')

    def test_each_field_is_marked_preserved_altered_or_absent(self):
        revised = ('Assunto: Prazo novo\n\nOlá, Ana Ribeira,\n\n'
                   'O lote de 20 g não será enviado antes de 15 de março. Se o fornecedor confirmar, '
                   'a entrega pode sair até 20 de março. O responsável disse: “Não há risco para o pedido.” '
                   'Envie o formulário e o comprovante.\n\nAtenciosamente,\nEquipe de Logística')
        states, report = self.states(revised)
        self.assertEqual(states[('numero', '20 kg')], 'alterado')
        self.assertEqual(states[('nome', 'Ana Ribeiro')], 'alterado')
        self.assertEqual(states[('data', '15 de março de 2027')], 'alterado')
        self.assertEqual(states[('url', 'https://exemplo.test/laudo')], 'ausente')
        self.assertEqual(states[('assunto', 'Assunto: Mudança no prazo de entrega')], 'ausente')
        self.assertEqual(states[('citacao', '“Não há risco para o pedido.”')], 'preservado')
        self.assertEqual(states[('assinatura', 'Equipe de Logística')], 'preservado')
        altered = {c['valor']: c for c in report['campos'] if c['estado'] == 'alterado'}
        self.assertIn('20 g', altered['20 kg']['candidato'])
        self.assertIn('Ana Ribeira', altered['Ana Ribeiro']['candidato'])
        self.assertEqual(report['resumo']['ausente'], 3, report['resumo'])
        missing = module().verify_fields('Texto sem o nome.', 'Texto sem o nome.', {'campos': [{'tipo': 'nome', 'valor': 'Rui'}]})
        self.assertEqual(missing['campos'][0]['estado'], 'ausente_na_referencia')
        # Número seguido de palavra comum continua sendo o mesmo número.
        money = module().verify_fields('R$ 1.000 aplicados e R$ 150 por mês.', 'Aplique R$ 1.000 hoje e R$150 por mês.',
                                       {'campos': [{'tipo': 'numero', 'valor': 'R$ 1.000'}, {'tipo': 'numero', 'valor': 'R$ 150'}]})
        self.assertEqual([c['estado'] for c in money['campos']], ['preservado', 'preservado'])
        self.assertEqual(module().verify_fields('peso de 120 kg', 'peso de 20 kg', {'campos': [{'tipo': 'numero', 'valor': '20 kg'}]})
                         ['campos'][0]['estado'], 'ausente_na_referencia')

    def test_reading_hints_follow_changed_counts_and_new_names(self):
        revised = DRAFT_090.replace('não será enviado antes', 'será enviado antes').replace(
            'pode sair', 'sai').replace('o formulário e o comprovante', 'o formulário ou o comprovante') + '\nCarlos Mendes'
        report = module().verify_fields(DRAFT_090, revised, FIELDS_090)
        hints = report['leitura']
        self.assertTrue(hints['negacao']['mudou'])
        self.assertEqual((hints['negacao']['original'], hints['negacao']['revisado']), (1, 0))
        self.assertTrue(hints['modal']['mudou'])
        self.assertTrue(hints['e_ou']['mudou'])
        self.assertFalse(hints['condicao']['mudou'])
        self.assertTrue(any('ou o comprovante' in trecho for trecho in hints['e_ou']['trechos_revisado']))
        self.assertEqual(hints['condicao']['trechos_revisado'], [])
        self.assertIn('Carlos', hints['possiveis_nomes_novos'])
        self.assertNotIn('Ana', hints['possiveis_nomes_novos'])
        added = module().verify_fields(DRAFT_090, DRAFT_090 + ' Foram 30% mais rápidas e 200 pessoas, em 2027.', FIELDS_090)
        self.assertEqual(added['leitura']['numeros_novos'], ['30%', '200'])
        self.assertEqual(report['leitura']['numeros_novos'], [])

    def test_structure_counts_and_five_word_reuse_are_descriptive(self):
        original = '# Título\n\nPrimeiro parágrafo com cinco palavras iguais aqui.\n\n- item um\n- item dois\n'
        revised = 'Primeiro parágrafo com cinco palavras iguais aqui.\n\nSegundo parágrafo novo.\n'
        report = module().verify_fields(original, revised, {'campos': []})
        self.assertEqual(report['estrutura']['titulos'], {'original': 1, 'revisado': 0})
        self.assertEqual(report['estrutura']['itens_de_lista'], {'original': 2, 'revisado': 0})
        self.assertEqual(report['estrutura']['paragrafos'], {'original': 3, 'revisado': 2})
        reuse = report['reaproveitamento_5_palavras']
        # Sequências distintas de 5 palavras no texto inteiro, como no teste de contaminação.
        self.assertEqual(reuse['sequencias_original'], 8)
        self.assertEqual(reuse['sequencias_revisado'], 6)
        self.assertEqual(reuse['em_comum'], 3)
        serialized = json.dumps(report, ensure_ascii=False)
        for verdict in ['limiar', 'aprovado', 'score']:
            self.assertNotIn(verdict, serialized)
        self.assertIn('não garante', report['aviso'])

    def test_invalid_case_declarations_are_rejected(self):
        h = module()
        for fields in [[], {'campos': 'x'}, {'campos': [{'tipo': 'cor', 'valor': 'azul'}]},
                       {'campos': [{'tipo': 'nome', 'valor': ' '}]}, {'campos': [{'tipo': 'nome'}]},
                       {'campos': [{'tipo': 'nome', 'valor': 'Ana'}, {'tipo': 'nome', 'valor': 'Ana'}]}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                h.verify_fields('Ana', 'Ana', fields)

    def test_verify_cli_with_fields_exit_codes_and_readonly(self):
        with tempfile.TemporaryDirectory() as folder:
            draft, good, bad, case, broken = [Path(folder) / n for n in
                                               ('rascunho.txt', 'bom.txt', 'ruim.txt', 'caso.json', 'quebrado.json')]
            draft.write_text(DRAFT_090, encoding='utf-8')
            good.write_text(DRAFT_090.replace('Envie o formulário', 'Mande o formulário'), encoding='utf-8')
            bad.write_text(DRAFT_090.replace('20 kg', '25 kg'), encoding='utf-8')
            case.write_text(json.dumps(FIELDS_090, ensure_ascii=False), encoding='utf-8')
            broken.write_text('{"campos": [{"tipo": "cor", "valor": "azul"}]}', encoding='utf-8')
            ok = cli_run('verify', draft, good, '--campos', case)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertEqual(json.loads(ok.stdout)['kind'], 'field_verification')
            lost = cli_run('verify', draft, bad, '--campos', case)
            self.assertEqual(lost.returncode, 1, lost.stderr)
            self.assertEqual(json.loads(lost.stdout)['resumo']['alterado'], 1)
            for args in [(draft, good, '--campos', broken), (draft, good, '--campos', Path(folder) / 'ausente.json')]:
                failed = cli_run('verify', *args)
                self.assertEqual(failed.returncode, 2)
                self.assertNotIn('Traceback', failed.stderr)
            legacy = cli_run('verify', draft, bad)
            self.assertEqual(legacy.returncode, 0, legacy.stderr)
            self.assertFalse(json.loads(legacy.stdout)['protected_content_preserved'])
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()),
                             ['bom.txt', 'caso.json', 'quebrado.json', 'rascunho.txt', 'ruim.txt'])


EXAMPLES = SKILL_DIR / 'references/exemplos.json'
REQUIRED_DEFECTS = {'cliche', 'uniformidade', 'invencao', 'prazo', 'tempo_verbal', 'e_ou'}


def words(text):
    import re
    return re.findall(r'\w+', text.casefold())


def ngrams(text, size):
    tokens = words(text)
    return {' '.join(tokens[i:i + size]) for i in range(len(tokens) - size + 1)}


class Exemplos090Tests(unittest.TestCase):
    """0.9.0: um exemplo de redação e um de revisão por plano de gênero, com origem declarada."""

    def examples(self):
        return module().load_examples()

    def test_every_genre_plan_has_one_writing_and_one_revision_example(self):
        structures = [s['id'] for s in json.loads((SKILL_DIR / 'references/estilos.json').read_text('utf-8'))['structures']]
        examples = self.examples()
        self.assertEqual(sorted(examples), sorted((s, m) for s in structures for m in ('redacao', 'revisao')))
        self.assertEqual(len(examples), 2 * len(structures))
        for (structure, mode), item in examples.items():
            with self.subTest(example=item['id']):
                expected = {'briefing', 'bom', 'ruim'} if mode == 'redacao' else {'rascunho', 'bom', 'ruim'}
                self.assertEqual(set(item['textos']), expected)
                self.assertTrue(item['motivo'].strip())

    def test_every_text_records_origin_and_synthetic_texts_name_model_and_date(self):
        import re
        for item in self.examples().values():
            self.assertIn(item['leitura_humana']['status'], {'pendente', 'aprovado', 'rejeitado'})
            if item['leitura_humana']['status'] == 'aprovado':
                self.assertTrue(item['leitura_humana'].get('leitor') and item['leitura_humana'].get('data'))
            for role, text in item['textos'].items():
                with self.subTest(example=item['id'], role=role):
                    self.assertIn(text['origem'], {'humano_documentado', 'editado', 'sintetico'})
                    if text['origem'] == 'sintetico':
                        self.assertTrue(text['modelo'])
                        self.assertRegex(text['data'], r'^\d{4}-\d{2}-\d{2}$')
                        self.assertIsNone(text['fonte'])
                    else:
                        for key in ('autor', 'fonte', 'licenca', 'url', 'data'):
                            self.assertTrue(text.get(key), key)

    def test_loader_rejects_unlabeled_or_incomplete_examples(self):
        h = module()
        data = json.loads(EXAMPLES.read_text('utf-8'))
        broken = []
        for change in [lambda d: d['exemplos'][0]['textos']['bom'].pop('modelo'),
                       lambda d: d['exemplos'][0]['textos']['bom'].update(origem='humano'),
                       lambda d: d['exemplos'][0]['textos']['bom'].update(origem='humano_documentado'),
                       lambda d: d['exemplos'][0].update(defeito='qualquer'),
                       lambda d: d['exemplos'].append(d['exemplos'][0]),
                       lambda d: d['exemplos'].pop(),
                       lambda d: d['exemplos'][0]['leitura_humana'].update(status='aprovado'),
                       lambda d: d['exemplos'][0]['textos']['bom'].update(texto=' ')]:
            copy = json.loads(json.dumps(data))
            change(copy)
            broken.append(copy)
        with tempfile.TemporaryDirectory() as folder:
            for n, item in enumerate(broken):
                path = Path(folder) / f'{n}.json'
                path.write_text(json.dumps(item, ensure_ascii=False), encoding='utf-8')
                with self.subTest(n=n), self.assertRaises(ValueError):
                    h.load_examples(path)

    def test_texts_have_comparable_length_and_no_dash(self):
        for item in self.examples().values():
            for role, text in item['textos'].items():
                with self.subTest(example=item['id'], role=role):
                    size = len(words(text['texto']))
                    low, high = (15, 120) if role == 'briefing' else (40, 140)
                    self.assertTrue(low <= size <= high, size)
                    self.assertNotIn('—', text['texto'])
                    self.assertNotIn('–', text['texto'])

    def test_good_versions_are_clean_and_bad_versions_vary_beyond_the_veto_list(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        defects = Counter(item['defeito'] for item in self.examples().values())
        self.assertLessEqual(REQUIRED_DEFECTS, set(defects))
        self.assertTrue(all(defects[d] >= 2 for d in REQUIRED_DEFECTS), defects)
        uncaught = 0
        for item in self.examples().values():
            good, bad = item['textos']['bom']['texto'], item['textos']['ruim']['texto']
            with self.subTest(example=item['id']):
                self.assertEqual(h.audit(good, rules)['findings'], [], 'versão boa sem vício do catálogo')
                self.assertTrue(h.check(good, rules)['deliverable'])
                findings = h.audit(bad, rules)['findings']
                if item['defeito'] == 'cliche':
                    self.assertTrue(findings, 'clichê precisa aparecer no catálogo')
                uncaught += not findings
        self.assertGreaterEqual(uncaught, 10, 'a maioria dos defeitos fica fora da lista de vetos')

    def test_writing_examples_do_not_copy_the_briefing(self):
        for item in self.examples().values():
            if item['modo'] != 'redacao':
                continue
            with self.subTest(example=item['id']):
                # 8 palavras, como o alerta de memorização: termos exatos do pedido podem repetir menos.
                shared = ngrams(item['textos']['briefing']['texto'], 8) & ngrams(item['textos']['bom']['texto'], 8)
                self.assertEqual(shared, set(), 'redação reescreve o briefing com frases próprias')

    def test_revision_examples_declare_fields_and_the_good_revision_keeps_them(self):
        h = module()
        states = Counter()
        for item in self.examples().values():
            if item['modo'] != 'revisao':
                continue
            states[item['estado_do_rascunho']] += 1
            draft, good = item['textos']['rascunho']['texto'], item['textos']['bom']['texto']
            with self.subTest(example=item['id']):
                self.assertTrue(item['campos'])
                kept = h.verify_fields(draft, good, {'campos': item['campos']})
                self.assertEqual(kept['resumo']['preservado'], len(item['campos']), kept['campos'])
                reuse = kept['reaproveitamento_5_palavras']
                share = reuse['em_comum'] / reuse['sequencias_original']
                if item['estado_do_rascunho'] == 'bom':
                    self.assertGreaterEqual(share, 0.6, 'rascunho bom pede poucas mudanças')
                if item['estado_do_rascunho'] == 'fraco':
                    self.assertLess(share, 0.6)
        self.assertEqual(set(states), {'bom', 'com_vicios', 'fraco'})

    @requer(PROMPTS)
    def test_examples_do_not_copy_approved_prompts(self):
        import re
        prompts = re.findall(r'```text\n(.*?)\n```', (SKILL_DIR / 'results/PROMPTS.md').read_text('utf-8'), re.S)
        approved = set().union(*(ngrams(p, 5) for p in prompts))
        text = EXAMPLES.read_text('utf-8')
        self.assertEqual(ngrams(text, 5) & approved, set())
        self.assertNotIn('Vila Clara', text)


SIZES_081 = json.loads(SIZES_081_FILE.read_text('utf-8')) if SIZES_081_FILE.exists() else None


class BriefModo090Tests(unittest.TestCase):
    """0.9.0: briefing com o exemplo do gênero pedido e modo revisão, sem crescer em relação à 0.8.1."""

    def pairs(self):
        return [(p, g) for p, profile in module().load_profiles().items() for g in profile['genres']]

    def test_writing_brief_carries_only_the_writing_example_of_its_genre(self):
        h = module()
        examples = h.load_examples()
        for profile, genre in self.pairs():
            with self.subTest(profile=profile, genre=genre):
                data = h.brief(profile, genre, 2, 0, 17)
                self.assertEqual(data['modo'], 'redacao')
                text = h.brief_text(data)
                own = examples[(data['structure_id'], 'redacao')]
                for role in ('briefing', 'bom', 'ruim'):
                    self.assertIn(own['textos'][role]['texto'], text)
                self.assertIn(own['motivo'], text)
                self.assertIn('sintético', text)
                for key, other in examples.items():
                    if key != (data['structure_id'], 'redacao'):
                        self.assertNotIn(other['textos']['bom']['texto'], text)
                self.assertLess(text.index('Demais regras do catálogo'), text.index(own['textos']['bom']['texto']))
                self.assertLess(text.index(own['textos']['bom']['texto']), text.index('\nEntrega\n'))

    def test_revision_mode_brings_the_contract_and_revision_example_without_writing_plan(self):
        h = module()
        examples = h.load_examples()
        for profile, genre in self.pairs():
            with self.subTest(profile=profile, genre=genre):
                data = h.brief(profile, genre, 2, 0, 17, modo='revisao')
                text = h.brief_text(data)
                own = examples[(data['structure_id'], 'revisao')]
                draft = own['textos']['rascunho']['texto']
                self.assertIn(draft, text)
                # Revisões aparecem inteiras ou pelo que muda: todo trecho novo em relação ao rascunho está no texto.
                for role in ('bom', 'ruim'):
                    revised = own['textos'][role]['texto']
                    if revised not in text:
                        for unit in h.example_units(revised):
                            if unit not in h.example_units(draft):
                                self.assertIn(unit, text, role)
                self.assertIn(own['motivo'], text)
                self.assertNotIn('Plano:', text)
                self.assertNotIn(examples[(data['structure_id'], 'redacao')]['textos']['bom']['texto'], text)
                contract = text[text.index('Revisão: o estado do texto define'):text.index('Exemplo de revisão')]
                for idea in ['Diagnostique', 'ritmo', 'ressalvas', 'só anunciam', 'abstração', 'fecho', 'gênero',
                             'frases boas', 'poucas mudanças', 'tempo verbal', 'provisório']:
                    self.assertIn(idea, contract)
                self.assertTrue(text.rstrip().endswith('melhoria concreta.'))
                self.assertIn('não repita comandos', text.casefold())
                self.assertNotIn('—', text)
        news = h.brief_text(h.brief('jornalistico', 'noticia', modo='revisao'))
        self.assertNotIn('Reescreva o material com frases próprias', news, 'ofício só de redação fica fora da revisão')
        self.assertIn('Reescreva o material com frases próprias', h.brief_text(h.brief('jornalistico', 'noticia')))
        result = cli_run('brief', '--profile', 'jornalistico', '--genre', 'noticia', '--modo', 'revisao')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, news)
        json_result = json.loads(cli_run('brief', '--profile', 'jornalistico', '--genre', 'noticia', '--modo', 'revisao',
                                         '--format', 'json').stdout)
        self.assertEqual(json_result['exemplo']['id'], 'noticia-revisao')
        for args in [('--modo', 'diagnostico'), ('--modo', 'REVISAO')]:
            failed = cli_run('brief', '--profile', 'jornalistico', *args)
            self.assertEqual(failed.returncode, 2)
            self.assertNotIn('Traceback', failed.stderr)
        with self.assertRaises(ValueError):
            h.brief('jornalistico', 'noticia', modo='diagnostico')

    @requer(SIZES_081_FILE)
    def test_no_brief_grows_beyond_the_0_8_1_brief_of_the_same_genre(self):
        h = module()
        self.assertEqual(set(SIZES_081['briefing_caracteres']), {f'{p}/{g}' for p, g in self.pairs()})
        for profile, genre in self.pairs():
            for mode in ('redacao', 'revisao'):
                with self.subTest(profile=profile, genre=genre, mode=mode):
                    size = len(h.brief_text(h.brief(profile, genre, 2, 0, 17, modo=mode)))
                    self.assertLessEqual(size, SIZES_081['briefing_caracteres'][f'{profile}/{genre}'])

    @requer(SIZES_081_FILE)
    def test_skill_md_is_not_larger_than_0_8_1(self):
        self.assertLessEqual(len((SKILL_DIR / 'SKILL.md').read_text('utf-8')), SIZES_081['skill_md_caracteres'])


    def test_skill_and_brief_together_carry_every_term_and_every_exception(self):
        h = module()
        rules = h.load_catalog(SKILL_DIR / 'references/catalogo.json')
        skill = (SKILL_DIR / 'SKILL.md').read_text('utf-8').casefold()
        for profile, genre in self.pairs():
            for mode in ('redacao', 'revisao'):
                with self.subTest(profile=profile, genre=genre, mode=mode):
                    data = h.brief(profile, genre, 2, 0, 17, modo=mode)
                    text = h.brief_text(data)
                    for rule in rules:
                        self.assertIn(f"{rule['id']} {rule['name']}" if rule['id'] in data['focus'] else f"- {rule['id']}", text)
                        for exception in rule.get('exceptions', []):
                            self.assertIn(exception, text)
                        for term in rule['avoid']:
                            self.assertTrue(term.casefold() in text.casefold() or term.casefold() in skill, term)


class Skill090Tests(unittest.TestCase):
    """0.9.0: revisão pelo estado do texto, exemplos do gênero e critério de parada."""

    def skill(self):
        return (SKILL_DIR / 'SKILL.md').read_text('utf-8')

    def section(self, title):
        skill = self.skill()
        start = skill.index('## ' + title)
        end = skill.find('\n## ', start + 1)
        return skill[start:end if end > 0 else len(skill)]

    def test_revision_is_one_contract_defined_by_the_request_and_the_state_of_the_text(self):
        mode = self.section('Modo')
        for idea in ['estado do texto', 'não a origem presumida', 'Diagnostique', 'ritmo', 'ressalvas', 'só anunciam',
                     'abstração', 'fecho', 'gênero', 'frases boas', 'poucas mudanças', 'resposta correta']:
            self.assertIn(idea, mode)
        self.assertLess(mode.index('Diagnostique'), mode.index('Mude só o que o diagnóstico justifica'))

    def test_writing_rereads_against_the_genre_example_and_tools_are_documented(self):
        skill = self.skill()
        self.assertIn('references/exemplos.json', skill)
        self.assertIn('--modo revisao', skill)
        self.assertIn('--campos', skill)
        self.assertIn('exemplo do gênero', self.section('Fluxo'))
        tools = self.section('Verificação e ferramentas')
        for state in ['preservado', 'alterado', 'ausente']:
            self.assertIn(state, tools)

    def test_stopping_criterion_replaces_the_old_final_validation(self):
        stop = self.section('Critério de parada')
        self.assertIn('editor', stop)
        self.assertTrue(stop.rstrip().endswith('nova revisão não trouxer melhoria concreta.'))
        self.assertNotIn('## Validação final', self.skill())
        self.assertNotIn('Não economize tokens', self.skill())
        self.assertTrue(self.skill().rstrip().endswith(stop.rstrip()))


# 0.9.0 preservada: a 0.9.1 só muda a redação (P1 e P2 do plano, com as correções do README de 23/10/2026).
DELIVERY_REVISION_090 = [
    'Responda somente com o artefato pedido, sem preâmbulo, bastidores ou oferta final; comandos, JSON ou plano só '
    'quando o pedido exigir esse formato.',
    'Estes retornos já foram calculados pela skill: não repita comandos nem chamadas de ferramenta.',
    'Travessão do original pode ficar na frase mantida; não acrescente travessão nem traço substituto.',
    'Compare com o texto recebido: cada mudança tem motivo no diagnóstico e os campos fixos continuam iguais; '
    'termine quando uma nova revisão não trouxer melhoria concreta.',
]
REVISION_CONTRACT_090 = [
    'Diagnostique antes de mexer: vícios do catálogo, ritmo e parágrafos uniformes, ressalvas que atenuam a posição, '
    'frases que só anunciam, abstração no lugar de exemplo, fecho que resume e desajuste ao gênero.',
    'Mude só o que o diagnóstico justifica. Fatos e frases boas ficam, venham do autor ou de um rascunho de IA; texto '
    'que já funciona pede poucas mudanças, e devolvê-lo quase igual é acerto.',
    'Citações, números com unidade, nomes, datas, URLs, código, saudação, assinatura e assunto ficam literais. Não '
    'troque tempo verbal, quem faz a ação, "e" por "ou", provisório por confirmado nem opinião por fato.',
]
REVISION_MODE_090 = (
    '- Revisão: texto do usuário ou rascunho de IA. O pedido e o estado do texto definem a extensão da edição, não a '
    'origem presumida. Diagnostique antes de mexer: vícios do catálogo, ritmo e parágrafos uniformes, ressalvas que '
    'atenuam a posição, frases que só anunciam, abstração no lugar de exemplo, fecho que resume e desajuste ao gênero. '
    'Mude só o que o diagnóstico justifica, no escopo pedido: fatos, estrutura útil, voz e frases boas ficam, venham do '
    'autor ou de IA. Texto que já funciona pede poucas mudanças; devolvê-lo quase igual é resposta correta.')
# Impressões digitais dos briefings 0.9.0 de todos os pares (breadth 2, randomness 0, seed 17), com a versão do
# cabeçalho neutralizada. Redação: tudo antes de "Entrega", sem a linha do rótulo do exemplo. Revisão: inteiro.
REDACAO_ESTAVEL_090 = 'd4732f564808af33159fae0dbc32f37ca7265de7fa45aa5b220353808f90115e'
REVISAO_090 = '39c0ba2819a85279e42bf3eb6208ab2bc5938178a46b7ba21726f7cd7bab79d8'
SKILL_MD_090 = 9061  # caracteres; a SKILL.md 0.9.0 já cabia no teto da 0.8.1 (results/tamanhos-0.8.1.json)
RUNNER_BUDGET = 0.4 * 48850  # o teto de Skill070Tests (40% do v1 de 13/10), sem depender da fixture antiga
RUNNER_PAIRS = {('jornalistico', 'noticia'), ('jornalistico', 'reportagem'), ('tecnico-preciso', 'tecnico'),
                ('tecnico-preciso', 'relatorio'), ('didatico', 'didatico'), ('academico', 'academico'),
                ('executivo-direto', 'proposta'), ('executivo-direto', 'negocios'), ('executivo-direto', 'relatorio'),
                ('conversacional-contido', 'email'), ('conversacional-contido', 'post'),
                ('conversacional-contido', 'roteiro'), ('argumentativo-sobrio', 'artigo'),
                ('argumentativo-sobrio', 'ensaio'), ('literario', 'conto'), ('literario', 'cronica')}
# Recusados pelo README: número uma vez só, veto a pergunta, seção ou formalidade, encurtamento como meta e
# incerteza que o pedido não exige. Nada disso entra no texto novo da 0.9.1.
NOT_ADOPTED = ('cada número', 'uma vez', 'pergunta', 'seção', 'seções', 'título', 'formal', 'curt', 'breve',
               'concis', 'enxut', 'incerteza')


def _sem_versao(text, version):
    return text.replace(f'Briefing editorial humanizador-pt-br {version}:', 'Briefing editorial humanizador-pt-br X:', 1)


def _redacao_estavel(text, version):
    """Briefing de redação sem o rótulo do exemplo e sem a entrega, as duas partes que a 0.9.1 reescreve."""
    text = '\n'.join(l for l in _sem_versao(text, version).split('\n') if not l.startswith('Exemplo do gênero, '))
    return text[:text.index('\nEntrega\n')]


class Redacao091Tests(unittest.TestCase):
    """0.9.1: o exemplo ensina ofício, não molde; na redação, o pedido inteiro é atendido antes de qualquer corte."""

    def pairs(self, h):
        return [(p, g) for p, profile in h.load_profiles().items() for g in profile['genres']]

    def skill(self):
        return (SKILL_DIR / 'SKILL.md').read_text('utf-8')

    def section(self, title):
        skill = self.skill()
        start = skill.index('## ' + title)
        end = skill.find('\n## ', start + 1)
        return skill[start:end if end > 0 else len(skill)]

    def step(self, number):
        return next(l for l in self.section('Fluxo').splitlines() if l.startswith(f'{number}. '))

    def fingerprint(self, h, modo, part):
        import hashlib
        texts = [f'{p}/{g}\n' + part(h.brief_text(h.brief(p, g, 2, 0, 17, modo=modo)), h.VERSION)
                 for p, g in self.pairs(h)]
        return hashlib.sha256('\x00'.join(texts).encode('utf-8')).hexdigest()

    def test_example_teaches_craft_without_fixing_facts_length_opening_structure_or_roles(self):
        h = module()
        for profile, genre in self.pairs(h):
            with self.subTest(profile=profile, genre=genre):
                text = h.brief_text(h.brief(profile, genre, 2, 0, 17))
                lines = text.splitlines()
                label = next(l for l in lines if l.startswith('Exemplo do gênero, '))
                self.assertTrue(lines[lines.index(label) + 1].startswith('Pedido: '),
                                'a ressalva acompanha o exemplo, antes do pedido dele')
                for item in ('fatos', 'extensão', 'abertura', 'estrutura', 'quem faz o quê'):
                    self.assertIn(item, label)
                self.assertIn('não vêm dele', label)
                delivery = text[text.index('\nEntrega\n'):]
                self.assertNotIn('versão boa', delivery, 'a entrega não manda medir o texto pelo exemplo')
        self.assertIn('o exemplo do gênero ensina ofício, não molde', self.step(2))
        self.assertNotIn('compare com a versão boa', self.section('Fluxo'))

    def test_writing_covers_every_requested_verb_and_concept_before_any_cut(self):
        h = module()
        for profile, genre in self.pairs(h):
            with self.subTest(profile=profile, genre=genre):
                text = h.brief_text(h.brief(profile, genre, 2, 0, 17))
                delivery = text[text.index('\nEntrega\n'):]
                found = [l for l in delivery.splitlines() if 'cada verbo do pedido' in l]
                self.assertEqual(len(found), 1, 'a entrega da redação confere cada verbo do pedido')
                order = [found[0].index(s) for s in ('Antes de cortar', 'cada verbo do pedido',
                                                     'explique o conceito pedido', 'corte só repetição sem função')]
                self.assertEqual(order, sorted(order), 'pedido inteiro atendido antes de qualquer corte')
                self.assertTrue(found[0].endswith('melhoria concreta.'))
                # Cada verbo ganha sua parte no texto, não uma seção obrigatória.
                self.assertIn('Plano: funções, não seções', text)
        step = self.step(4)
        self.assertIn('na redação, antes de cortar, cumpra cada verbo do pedido', step)
        self.assertIn('complete o que falta', step)

    def test_functional_repetition_stays_and_no_rejected_formula_enters(self):
        h = module()
        self.assertNotIn('corte o que repete', self.skill())
        self.assertIn('corte só repetição sem função', self.step(4))
        changed = [self.step(4), self.section('Critério de parada')]
        for profile, genre in self.pairs(h):
            text = h.brief_text(h.brief(profile, genre, 2, 0, 17))
            delivery = text[text.index('\nEntrega\n'):]
            self.assertIn('só repetição sem função', delivery)
            changed += [next(l for l in text.splitlines() if l.startswith('Exemplo do gênero, ')), delivery]
        for part in changed:
            for term in NOT_ADOPTED:
                with self.subTest(term=term, part=part[:40]):
                    self.assertNotIn(term, part.casefold())
        # Fechos, simetrias e bastidores ficam para teste separado: a opção de terminar em pergunta continua.
        essay = h.brief_text(h.brief('argumentativo-sobrio', 'ensaio', 2, 0, 17))
        self.assertIn('Termine numa pergunta concreta ou numa imagem', essay)

    def test_stopping_rule_keeps_unjustified_change_as_a_revision_defect(self):
        stop = self.section('Critério de parada')
        self.assertIn('Na revisão, mudar sem motivo também é defeito.', stop)
        self.assertNotIn('revisar sem motivo', stop, 'na redação, parte pedida que falta é motivo para completar')
        self.assertTrue(stop.rstrip().endswith('nova revisão não trouxer melhoria concreta.'))

    def test_revision_contract_and_revision_brief_are_unchanged(self):
        h = module()
        self.assertEqual(h.DELIVERY_REVISION, DELIVERY_REVISION_090)
        self.assertEqual(h.REVISION_CONTRACT, REVISION_CONTRACT_090)
        self.assertIn(REVISION_MODE_090, self.section('Modo'))
        self.assertEqual(self.fingerprint(h, 'revisao', _sem_versao), REVISAO_090,
                         'o briefing de revisão é o da 0.9.0, exceto pela versão')
        for profile, genre in self.pairs(h):
            text = h.brief_text(h.brief(profile, genre, 2, 0, 17, modo='revisao'))
            for phrase in ('cada verbo do pedido', 'conceito pedido', 'repetição sem função', 'quem faz o quê'):
                with self.subTest(profile=profile, genre=genre, phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_writing_brief_changes_only_the_example_label_and_the_delivery(self):
        h = module()
        self.assertEqual(self.fingerprint(h, 'redacao', _redacao_estavel), REDACAO_ESTAVEL_090,
                         'fora do rótulo do exemplo e da entrega, o briefing de redação é o da 0.9.0')

    def test_version_0_9_1_is_consistent_in_skill_script_and_outputs(self):
        import re
        skill = self.skill()
        self.assertEqual(re.search(r'^version: (\S+)$', skill, re.M).group(1), '0.9.1')
        h = module()
        self.assertEqual(h.VERSION, '0.9.1')
        for modo in ('redacao', 'revisao'):
            self.assertTrue(h.brief_text(h.brief('didatico', 'didatico', modo=modo))
                            .startswith('Briefing editorial humanizador-pt-br 0.9.1:'))
        self.assertEqual(h.check('O texto final.', [])['version'], '0.9.1')
        self.assertNotIn('—', skill)
        # Sem o README nesta cópia, ao menos os comandos de consulta da SKILL.md continuam executáveis.
        commands = re.findall(r'^python3 scripts/humanizar\.py ((?:catalog|styles|structure|brief) .*)$', skill, re.M)
        self.assertTrue(commands)
        for line in commands:
            with self.subTest(line=line):
                result = subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *line.split()],
                                        capture_output=True, text=True, cwd=SKILL_DIR)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('0.9.1', result.stdout)

    def test_skill_md_does_not_grow_and_the_treatment_fits_the_runner_budget(self):
        h = module()
        skill = len(self.skill())
        self.assertLessEqual(skill, SKILL_MD_090)
        for profile, genre in sorted(RUNNER_PAIRS):
            with self.subTest(profile=profile, genre=genre):
                self.assertLess(skill + len(h.brief_text(h.brief(profile, genre, 2, 0, 17))), RUNNER_BUDGET)


if __name__ == '__main__':
    unittest.main()
