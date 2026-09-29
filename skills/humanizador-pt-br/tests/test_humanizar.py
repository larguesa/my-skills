"""Testes incrementais do editor conservador, apenas com biblioteca padrão."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/humanizar.py'


def module():
    spec = importlib.util.spec_from_file_location('humanizar', SCRIPT)
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


if __name__ == '__main__':
    unittest.main()
