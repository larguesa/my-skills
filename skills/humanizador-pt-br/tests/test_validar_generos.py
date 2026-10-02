"""Offline synthetic fixtures only. No generated texts or model calls."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

TESTS = Path(__file__).resolve().parent
SCRIPT = TESTS / 'scripts/validar_generos.py'
CASES = json.loads((TESTS / 'experiments/cases.json').read_text(encoding='utf-8'))['cases']
BOUNDS = [(150, 220), (250, 350), (250, 400), (220, 320), (180, 260),
          (180, 260), (180, 260), (200, 280), (170, 240), (200, 280),
          (180, 240), (250, 350), (170, 240), (200, 280), (220, 320),
          (200, 280), (90, 140), (100, 160), (280, 380), (250, 350),
          (130, 200), (100, 140), (180, 240), (200, 280)]


def load():
    if not SCRIPT.exists():
        return None
    spec = importlib.util.spec_from_file_location('validar_generos', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(result, name, group='mechanical'):
    entries = [entry for entry in result[group] if entry['name'] == name]
    if len(entries) != 1:
        raise AssertionError(f'Expected one {group} observation named {name}, found {len(entries)}')
    return entries[0]


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.v = load()
        self.assertIsNotNone(self.v, 'deterministic validator is missing')
        self.assertTrue(callable(getattr(self.v, 'validate', None)), 'validate is missing')


class GeneralContractTests(ValidatorTestCase):
    def test_all_24_ids_have_json_serializable_pending_semantics(self):
        self.assertEqual(len(CASES), 24)
        for case in CASES:
            with self.subTest(case=case['id']):
                result = self.v.validate(case, '')
                self.assertEqual(result['word_count'], 0)
                self.assertEqual(result['semantic_review'], 'pending')
                self.assertEqual(check(result, 'nonempty')['status'], 'fail')
                self.assertIsInstance(result['factual_support'], list)
                for group in ('mechanical', 'factual_support'):
                    names = [entry['name'] for entry in result[group]]
                    self.assertEqual(len(names), len(set(names)))
                    for entry in result[group]:
                        self.assertEqual(set(entry), {'name', 'status', 'detail'})
                        self.assertIn(entry['status'], ('pass', 'fail', 'pending'))
                        self.assertIsInstance(entry['detail'], str)
                json.dumps(result, allow_nan=False)

    def test_exact_inclusive_word_bounds_include_title_and_code(self):
        for index, (low, high) in enumerate(BOUNDS):
            for count in (0, low - 1, low, high, high + 1):
                with self.subTest(case=index + 1, count=count):
                    text = ' '.join(['palavra'] * count)
                    result = self.v.validate(CASES[index]['id'], text)
                    self.assertEqual(result['word_count'], count)
                    expected = 'pending' if index == 21 else ('pass' if low <= count <= high else 'fail')
                    self.assertEqual(check(result, 'word_count')['status'], expected)
                    self.assertIn(str(low), check(result, 'word_count')['detail'])
                    self.assertIn(str(high), check(result, 'word_count')['detail'])
        text = 'Título\n\n```python\na = 1\n```\ntexto\tfinal'
        self.assertEqual(self.v.validate(CASES[3], text)['word_count'], len(text.split()))

    def test_whitespace_empty_dash_and_literal_identifier_validation(self):
        result = self.v.validate(CASES[0], ' \n\t ')
        self.assertEqual(check(result, 'nonempty')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[0], 'texto\u2014fim'), 'no_long_dash')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[0], 'texto - fim'), 'no_long_dash')['status'], 'pass')
        for bad in ('01', ' 01-noticia-bibliotecas', '../01-noticia-bibliotecas', None):
            with self.assertRaises((ValueError, TypeError)):
                self.v.validate(bad, 'texto')
        with self.assertRaises(TypeError):
            self.v.validate(CASES[0], None)
        with self.assertRaises(ValueError):
            self.v.validate(dict(CASES[0], prompt='changed'), 'texto')

    def test_video_never_invents_spoken_format_or_duration(self):
        for text in ('fala ' * 110, 'FALA:\n' + 'fala ' * 110 + '\n[imagem]\n[imagem]\n[imagem]',
                     'Narração: texto\nVisual: imagem\nVisual: outra\nVisual: terceira'):
            result = self.v.validate(CASES[21], text)
            self.assertEqual(check(result, 'word_count')['status'], 'pending')
            self.assertEqual(check(result, 'visual_cues')['status'], 'pending')
            self.assertEqual(check(result, 'duration')['status'], 'pending')


class StructureTests(ValidatorTestCase):
    def test_required_sections_order_and_alternative_markup(self):
        for index, labels, ordered in (
            (2, ['Autenticação', 'Criar tarefa', 'Erros', 'Limitações'], True),
            (3, ['Reprodução', 'Causa', 'Correção', 'Limitações'], True),
            (5, ['Dados', 'Resultado', 'Limites'], False),
            (9, ['Observações', 'Limitações'], False),
            (14, ['Escopo', 'Prazo', 'Investimento', 'Exclusões', 'Próximo passo'], True)):
            for style in ('plain', 'markdown', 'bold', 'inline', 'numbered', 'setext'):
                def heading(label):
                    return {'plain': label, 'markdown': '## ' + label, 'bold': '**' + label + '**',
                            'inline': label + ': conteúdo.', 'numbered': '1. ' + label,
                            'setext': label + '\n---------'}[style]
                text = '\n\n'.join(heading(label) + '\n\nconteúdo.' for label in labels)
                with self.subTest(index=index, style=style):
                    result = self.v.validate(CASES[index], text)
                    self.assertEqual(check(result, 'sections')['status'], 'pass')
                    if ordered:
                        self.assertEqual(check(result, 'section_order')['status'], 'pass')
                    backwards = '\n\n'.join(heading(label) + '\n\nconteúdo.' for label in reversed(labels))
                    reverse_result = self.v.validate(CASES[index], backwards)
                    if ordered:
                        self.assertEqual(check(reverse_result, 'section_order')['status'], 'fail')
                    else:
                        self.assertNotIn('section_order', [e['name'] for e in reverse_result['mechanical']])
            self.assertEqual(check(self.v.validate(CASES[index], 'texto'), 'sections')['status'], 'fail')
        result = self.v.validate(CASES[2], 'Autenticação\n\nCriar tarefa\n\nErros\n\nLimitações\n\nErros')
        self.assertEqual(check(result, 'sections')['status'], 'fail')

    def test_exact_paragraph_counts_exclude_titles(self):
        for index, count, title in ((1, 3, True), (6, 3, False), (8, 3, False),
                                    (10, 1, False), (11, 4, False), (12, 3, False),
                                    (17, 2, True), (18, 4, True), (19, 5, False)):
            paragraphs = ['Um parágrafo com conteúdo.' for _ in range(count)]
            text = ('Título de teste\n\n' if title else '') + '\n\n'.join(paragraphs)
            with self.subTest(index=index):
                result = self.v.validate(CASES[index], text)
                self.assertEqual(check(result, 'paragraph_count')['status'], 'pass')
                bad = text + '\n\nOutro parágrafo adicional.'
                self.assertEqual(check(self.v.validate(CASES[index], bad), 'paragraph_count')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[11], 'a\n\nb\n\nc\n\nd'),
                               'paragraph_order')['status'], 'pending')
        self.assertNotIn('sections', [e['name'] for e in self.v.validate(CASES[15], 'texto')['mechanical']])

    def test_title_variants_no_title_and_not_arbitrary_paragraph_lengths(self):
        for index in (0, 1, 17, 18):
            for text in ('Título\n\nCorpo.', '# Título\nCorpo.', '**Título**\n\nCorpo.',
                         'Título\n======\n\nCorpo.'):
                self.assertEqual(check(self.v.validate(CASES[index], text), 'title')['status'], 'pass')
            self.assertEqual(check(self.v.validate(CASES[index], 'Um corpo único sem título.'), 'title')['status'], 'fail')
        for index in (19, 22):
            self.assertEqual(check(self.v.validate(CASES[index], '## Subtítulo\n\nCorpo.'),
                                   'no_headings')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[22], 'Entrei.\n\nVi o relógio.'),
                               'no_headings')['status'], 'pending')

    def test_mandatory_exact_quotes_beginning_and_title(self):
        quotes = ['O sensor avisa que o nível subiu; ele não aumenta a capacidade do canal.',
                  'Queremos saber quem recebe o alerta e em quanto tempo age.']
        result = self.v.validate(CASES[1], '\n'.join(quotes))
        self.assertEqual(check(result, 'literal_quotes')['status'], 'pass')
        for changed in ('\n'.join(quotes).replace('canal.', 'canal!'), quotes[0], ''):
            self.assertEqual(check(self.v.validate(CASES[1], changed), 'literal_quotes')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[20], 'Exemplo fictício para avaliação editorial.\ntexto'),
                               'literal_beginning')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[20], 'texto\nExemplo fictício para avaliação editorial.'),
                               'literal_beginning')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[22], 'O bilhete dizia “não acerte a hora”.'),
                               'literal_quote')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[22], 'não ajuste a hora'), 'literal_quote')['status'], 'fail')
        for title in ('Crônica ficcional: a meia no recibo', '# Crônica ficcional: a meia no recibo',
                      '**Crônica ficcional: a meia no recibo**'):
            self.assertEqual(check(self.v.validate(CASES[23], title + '\n\nCorpo.'), 'literal_title')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[23], 'texto\nCrônica ficcional: a meia no recibo'),
                               'literal_title')['status'], 'fail')

    def test_tables_and_physics_lines_are_syntax_not_semantic_truth(self):
        for table in ('| Leitura | Volume |\n|---|---|\n|1|12,40 mL|\n|2|12,50 mL|\n|3|12,60 mL|',
                      'Leitura\tVolume\n1\t12,40 mL\n2\t12,50 mL\n3\t12,60 mL'):
            text = table + '\n\nPrimeiro parágrafo.\n\nSegundo parágrafo.'
            result = self.v.validate(CASES[7], text)
            self.assertEqual(check(result, 'table')['status'], 'pass')
            self.assertEqual(check(result, 'measurement_rows')['status'], 'pass')
            self.assertEqual(check(result, 'paragraph_count')['status'], 'pass')
            self.assertEqual(check(self.v.validate(CASES[7], text.replace('3\t12,60 mL', '').replace('|3|12,60 mL|', '')),
                                   'measurement_rows')['status'], 'fail')
        for index in (7, 9, 13, 15):
            self.assertEqual(check(self.v.validate(CASES[index], 'Texto sem tabela.'), 'table')['status'], 'fail')
        text = 'Primeiro parágrafo.\n\nSegundo parágrafo.\n\nE_p = 2 * 10 * 5 = 100 J\nv = sqrt(100) = 10 m/s'
        result = self.v.validate(CASES[4], text)
        self.assertEqual(check(result, 'paragraph_count')['status'], 'pass')
        self.assertEqual(check(result, 'calculation_lines')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[4], text + '\nE_c = 100 J'), 'calculation_lines')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[20], '#etiqueta\nExemplo fictício para avaliação editorial.'),
                               'no_hashtags')['status'], 'fail')


class FactualSupportTests(ValidatorTestCase):
    def test_decimal_reference_results_are_recalculated_and_not_semantic_truth(self):
        fixtures = (
            (4, 'energy_initial', 'E_p = 2 * 10 * 5 = 100 J', 'E_p = 2 * 10 * 5 = 99 J', '100'),
            (4, 'speed_final', 'Rapidez final = 10 m/s', 'Rapidez final = 9 m/s', '10'),
            (5, 'period_mean', 'Média = 1,20 s', 'Média = 1,21 s; leituras: 1,20 s', '1.20'),
            (6, 'reaction_quotient', 'Q_c = 0,80 / 0,40 = 2', 'Q_c = 0,80 / 0,40 = 4', '2'),
            (7, 'volume_mean', 'Volume médio = 12,50 mL', 'Volume médio = 12,40 mL', '12.50'),
            (7, 'hcl_concentration', 'Concentração média de HCl = 0,05000 mol/L',
             'Concentração média de HCl = 0,5000 mol/L', '0.05000'),
            (9, 'oxygen_upstream_mean', 'Média a montante: 7,1 mg/L', 'Média a montante: 7,0 mg/L', '7.1'),
            (9, 'oxygen_downstream_mean', 'Média a jusante: 6,0 mg/L', 'Média a jusante: 6,1 mg/L', '6.0'),
            (9, 'oxygen_difference', 'Diferença jusante menos montante = -1,1 mg/L',
             'Diferença jusante menos montante = +1,1 mg/L', '-1.1'),
            (10, 'gain_a', 'Ganho do grupo A: 68 - 50 = 18 pontos', 'Ganho do grupo A: 17 pontos', '18'),
            (10, 'gain_b', 'Ganho do grupo B: 61 - 50 = 11 pontos', 'Ganho do grupo B: 12 pontos', '11'),
            (10, 'final_difference', 'Diferença final: 68 - 61 = 7 pontos', 'Diferença final: 8 pontos', '7'),
            (11, 'final_difference', 'Diferença final: 7 pontos', 'Diferença final: 8 pontos', '7'),
            (13, 'conditional_probability', '180/670 = 26,9%', '180/670 = 90%', '26.9'),
            (14, 'installment', 'Cada parcela: R$ 15.000', 'Cada parcela: R$ 30.000', '15000'),
            (15, 'cost_local', 'Total local: R$ 216.000', 'Total local: R$ 144.000', '216000'),
            (15, 'cost_cloud', 'Total nuvem: R$ 144.000', 'Total nuvem: R$ 216.000', '144000'),
            (15, 'cost_difference', 'Diferença: R$ 72.000', 'Diferença: R$ 70.000', '72000'),
            (17, 'outage_minutes', 'Duração: 32 minutos', 'Duração: 31 minutos', '32'),
        )
        for index, name, good, bad, expected in fixtures:
            with self.subTest(case=index + 1, name=name):
                result = self.v.validate(CASES[index], good)
                observation = check(result, name, 'factual_support')
                self.assertEqual(observation['status'], 'pass')
                self.assertIn(expected, observation['detail'])
                self.assertIn('semantic', observation['detail'])
                self.assertEqual(result['semantic_review'], 'pending')
                self.assertEqual(check(self.v.validate(CASES[index], bad), name, 'factual_support')['status'], 'fail')
                self.assertEqual(check(self.v.validate(CASES[index], ''), name, 'factual_support')['status'], 'fail')

    def test_numeric_notations_tables_and_uncertainty_literal(self):
        for text in ('Concentração de HCl = 5e-2 mol/L', 'Concentração de HCl: 0.05 mol/L',
                     '| Resultado | Valor |\n|---|---|\n|Concentração HCl|0,05000 mol/L|'):
            self.assertEqual(check(self.v.validate(CASES[7], text), 'hcl_concentration', 'factual_support')['status'], 'pass')
        for text in ('Total local: R$ 216.000,00', 'Custo total local: 216000 reais',
                     '| Opção | Custo total |\n|Local|R$ 216 mil|\n|Nuvem|R$ 144 mil|'):
            self.assertEqual(check(self.v.validate(CASES[15], text), 'cost_local', 'factual_support')['status'], 'pass')
        for text in ('Média = 1,20 ±0,02 s', 'Média = 1.20 +/- 0.02 s'):
            result = self.v.validate(CASES[5], text)
            self.assertEqual(check(result, 'period_mean', 'factual_support')['status'], 'pass')
            self.assertEqual(check(result, 'instrument_uncertainty', 'factual_support')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[5], '±0,03 s'), 'instrument_uncertainty', 'factual_support')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[9], 'Diferença = −1,1 mg/L'), 'oxygen_difference', 'factual_support')['status'], 'pass')
        self.assertEqual(check(self.v.validate(CASES[15], 'Compra local: R$ 120.000. Operação: R$ 4.000.'),
                               'cost_local', 'factual_support')['status'], 'fail')

    def test_conditional_counts_are_checked_in_table_not_numbers_elsewhere(self):
        table = '| Categoria | Sinalizado | Não sinalizado |\n|---|---|---|\n|Defeito|180|20|\n|Sem defeito|490|9.310|'
        self.assertEqual(check(self.v.validate(CASES[13], table), 'conditional_counts', 'factual_support')['status'], 'pass')
        transposed = '| Sinal | Defeito | Sem defeito |\n|---|---|---|\n|Sinalizado|180|490|\n|Não sinalizado|20|9310|'
        self.assertEqual(check(self.v.validate(CASES[13], transposed), 'conditional_counts', 'factual_support')['status'], 'pass')
        for text in (table.replace('|490|9.310|', '|20|9.310|'), table.replace('|180|20|', '|20|180|'),
                     'Defeito 180 20. Sem defeito 490 9310.'):
            self.assertEqual(check(self.v.validate(CASES[13], text), 'conditional_counts', 'factual_support')['status'], 'fail')

    def test_literal_data_support_for_each_case_stays_separate(self):
        fixtures = {0: 'Vila Clara: 1.200 vagas gratuitas em seis bibliotecas, a partir de 12 anos.',
                    1: '48 sensores em oito pontos; dois meses e duas chuvas; R$ 180 mil.',
                    8: 'Carbono retorna como CO2.', 12: 'Até trinta segundos.',
                    16: 'Marina, assunto: prazo. Paula, equipe de integração.',
                    17: '14h10 às 14h42, UTC-3.',
                    20: '28 e 35 deploys, 12 e três rollbacks; medianas 30 e 18 minutos.'}
        for index, text in fixtures.items():
            result = self.v.validate(CASES[index], text)
            self.assertTrue(result['factual_support'], index)
            self.assertIn('literal_data', [e['name'] for e in result['factual_support']])
            self.assertEqual(result['semantic_review'], 'pending')
        for case in CASES:
            self.assertTrue(self.v.validate(case, '')['factual_support'], case['id'])


class CodeAndBoundTests(ValidatorTestCase):
    GOOD_CODE = '''def collect(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

assert collect("A") == ["A"]
assert collect("B") == ["B"]
provided = []
assert collect("C", provided) is provided
'''
    GOOD_CURL = '''curl -X POST https://api.example.com/v1/jobs \\
  -H 'Authorization: Bearer <TOKEN>' \\
  -H 'Content-Type: application/json' \\
  --data '{"name":"backup"}' '''

    def code(self, code):
        return 'Correção\n\n```python\n' + code + '\n```\n\nLimitações\n\nTexto.'

    def api(self, curl=None, response='{"id":"job_123","status":"queued"}'):
        return '```bash\n' + (curl or self.GOOD_CURL) + '\n```\n\n```json\n' + response + '\n```'

    def test_python_restricted_ast_and_contract_without_host_execution(self):
        from unittest.mock import patch
        import builtins
        import subprocess
        import socket
        validator = self.v
        text = self.code(self.GOOD_CODE)
        with patch.object(builtins, 'exec', side_effect=AssertionError('host exec forbidden')), \
             patch.object(subprocess, 'run', side_effect=AssertionError('candidate subprocess forbidden without sandbox')), \
             patch.object(socket, 'socket', side_effect=AssertionError('network forbidden')):
            result = validator.validate(CASES[3], text)
        for name in ('python_syntax', 'python_safe_subset', 'python_correction', 'independent_asserts', 'identity_assert'):
            self.assertEqual(check(result, name)['status'], 'pass', name)
        self.assertEqual(check(result, 'python_runtime')['status'], 'pending')
        self.assertIn('sandbox', check(result, 'python_runtime')['detail'])
        self.assertEqual(result['semantic_review'], 'pending')

    def test_python_alternative_guard_list_allocation_and_assert_aliases(self):
        code = self.GOOD_CODE.replace('bucket is None', 'None is bucket').replace('bucket = []', 'bucket = list()')
        code = code.replace('assert collect("A") == ["A"]', 'first = collect("A")\nassert first == ["A"]')
        code = code.replace('assert collect("C", provided) is provided', 'result = collect("C", bucket=provided)\nassert result is provided')
        result = self.v.validate(CASES[3], self.code(code))
        for name in ('python_syntax', 'python_safe_subset', 'python_correction', 'independent_asserts', 'identity_assert'):
            self.assertEqual(check(result, name)['status'], 'pass', name)
        original = 'def collect(item, bucket=[]):\n    bucket.append(item)\n    return bucket'
        both = self.code(original) + '\n' + self.code(self.GOOD_CODE)
        self.assertEqual(check(self.v.validate(CASES[3], both), 'python_correction')['status'], 'pass')

    def test_python_bad_syntax_logic_missing_asserts_and_dangerous_ast(self):
        for code, observation in ((self.GOOD_CODE.replace('if bucket is None:', 'if bucket is None'), 'python_syntax'),
                                  (self.GOOD_CODE.replace('bucket is None', 'not bucket'), 'python_correction'),
                                  (self.GOOD_CODE.replace('bucket=None', 'bucket=[]'), 'python_correction'),
                                  (self.GOOD_CODE.replace('return bucket', 'return []'), 'python_correction'),
                                  (self.GOOD_CODE.replace('assert collect("B") == ["B"]', ''), 'independent_asserts'),
                                  (self.GOOD_CODE.replace(' is provided', ' == provided'), 'identity_assert')):
            with self.subTest(observation=observation):
                self.assertEqual(check(self.v.validate(CASES[3], self.code(code)), observation)['status'], 'fail')
        for extra in ('import os\nos.system("touch /tmp/forbidden")',
                      '__import__("socket").socket()', 'open("/tmp/forbidden", "w")',
                      'while True:\n    pass', 'print("x" * 999999999)',
                      '@evil\ndef collect(item, bucket=None):\n    return bucket',
                      'x = [i for i in range(100)]'):
            result = self.v.validate(CASES[3], self.code(self.GOOD_CODE + '\n' + extra))
            self.assertEqual(check(result, 'python_safe_subset')['status'], 'fail', extra)
            self.assertEqual(check(result, 'python_runtime')['status'], 'pending')
        self.assertEqual(check(self.v.validate(CASES[3], ''), 'python_syntax')['status'], 'fail')

    def test_curl_json_parse_contract_and_dummy_tokens_never_execute(self):
        from unittest.mock import patch
        import subprocess
        import urllib.request
        with patch.object(subprocess, 'run', side_effect=AssertionError('curl never executes')), \
             patch.object(urllib.request, 'urlopen', side_effect=AssertionError('HTTP forbidden')):
            result = self.v.validate(CASES[2], self.api())
        for name in ('curl_syntax', 'curl_contract', 'dummy_token', 'json_syntax', 'success_json'):
            self.assertEqual(check(result, name)['status'], 'pass', name)
        alternatives = (self.GOOD_CURL.replace('-X POST ', '').replace('--data ', '--data-raw '),
                        self.GOOD_CURL.replace('-X POST ', '--request=POST ').replace('<TOKEN>', '***'),
                        self.GOOD_CURL.replace('-H ', '--header ').replace('Content-Type', 'content-type'))
        for curl in alternatives:
            self.assertEqual(check(self.v.validate(CASES[2], self.api(curl)), 'curl_contract')['status'], 'pass')
        for changed in (self.GOOD_CURL.replace('POST', 'GET'), self.GOOD_CURL.replace('/v1/jobs', '/v1/tasks'),
                        self.GOOD_CURL.replace('"backup"', '""'), self.GOOD_CURL.replace('application/json', 'text/plain'),
                        self.GOOD_CURL + '; touch /tmp/forbidden', self.GOOD_CURL.replace('--data ', '--data @secret ')):
            self.assertEqual(check(self.v.validate(CASES[2], self.api(changed)), 'curl_contract')['status'], 'fail')
        result = self.v.validate(CASES[2], self.api(self.GOOD_CURL.replace('<TOKEN>', 'sk-real-secret')))
        self.assertEqual(check(result, 'dummy_token')['status'], 'fail')
        self.assertNotIn('sk-real-secret', json.dumps(result))
        for response in ('{"id":"job_123","status":"queued",}',
                         '{"id":"job_123","status":NaN}',
                         '{"id":"job_123","status":"queued","status":"completed"}'):
            self.assertEqual(check(self.v.validate(CASES[2], self.api(response=response)), 'json_syntax')['status'], 'fail')
        self.assertEqual(check(self.v.validate(CASES[2], self.api(response='{"id":"job_123","status":"completed"}')),
                               'success_json')['status'], 'fail')

    def test_resource_bounds_and_deep_code_fail_closed(self):
        result = self.v.validate(CASES[3], 'x ' * 100000)
        self.assertEqual(result['word_count'], 100000)
        self.assertEqual(check(result, 'resource_limit')['status'], 'fail')
        huge = self.GOOD_CODE + '\n' + 'a = 1\n' * 10000
        result = self.v.validate(CASES[3], self.code(huge))
        self.assertEqual(check(result, 'python_safe_subset')['status'], 'fail')
        self.assertEqual(check(result, 'python_runtime')['status'], 'pending')
        deep = 'def collect(item, bucket=None):\n    return ' + '[' * 500 + '0' + ']' * 500
        result = self.v.validate(CASES[3], self.code(deep))
        self.assertEqual(check(result, 'python_syntax')['status'], 'fail')


class AlternativeAndAdversarialTests(ValidatorTestCase):
    def test_alternative_table_formats_reversed_columns_and_totals(self):
        table = '| Categoria | Não sinalizado | Sinalizado | Total |\n|---|---|---|---|\n|Com defeito|20|180|200|\n|Sem defeito|9310|490|9800|'
        self.assertEqual(check(self.v.validate(CASES[13], table), 'conditional_counts', 'factual_support')['status'], 'pass')
        html = '<table><tr><th>Leitura</th><th>Volume</th></tr><tr><td>1</td><td>12,40 mL</td></tr><tr><td>2</td><td>12,50 mL</td></tr><tr><td>3</td><td>12,60 mL</td></tr></table>'
        result = self.v.validate(CASES[7], html + '\n\nUm parágrafo.\n\nOutro parágrafo.')
        for name in ('table', 'measurement_rows', 'paragraph_count'):
            self.assertEqual(check(result, name)['status'], 'pass')
        table = '| Opção | Inicial | Operação | Total |\n|---|---|---|---|\n|Local|120000|96000|216000|\n|Nuvem|0|144000|144000|'
        for name in ('cost_local', 'cost_cloud'):
            self.assertEqual(check(self.v.validate(CASES[15], table), name, 'factual_support')['status'], 'pass')

    def test_valid_but_unrecognized_semantics_and_numeric_labels_are_pending(self):
        result = self.v.validate(CASES[0], 'Na cidade, mil e duzentas vagas estão disponíveis para pessoas de doze anos; seis bibliotecas participam.')
        self.assertEqual(check(result, 'literal_data', 'factual_support')['status'], 'pending')
        result = self.v.validate(CASES[10], 'Os grupos ganharam 18 e 11 pontos; a diferença entre eles foi de sete pontos.')
        for name in ('gain_a', 'gain_b', 'final_difference'):
            self.assertNotEqual(check(result, name, 'factual_support')['status'], 'fail')
        result = self.v.validate(CASES[5], 'Média = 1.200 s')
        self.assertNotEqual(check(result, 'period_mean', 'factual_support')['status'], 'fail')
        text = 'E_p = 100 J, rapidez final = 10 m/s'
        for name in ('energy_initial', 'speed_final'):
            self.assertEqual(check(self.v.validate(CASES[4], text), name, 'factual_support')['status'], 'pass')

    def test_observed_interval_without_inventing_requirement_for_duration_literal(self):
        for text in ('Das 14h10 às 14h42 (UTC-3).', 'Das 14:10 às 14:42 (UTC-3).'):
            result = self.v.validate(CASES[17], text)
            self.assertEqual(check(result, 'outage_minutes', 'factual_support')['status'], 'pass')
        wrong = 'Das 14h10 às 14h42. Duração: 31 minutos.'
        self.assertEqual(check(self.v.validate(CASES[17], wrong), 'outage_minutes', 'factual_support')['status'], 'fail')

    def test_unfenced_code_and_more_general_correct_ast_are_not_false_failed(self):
        code = CodeAndBoundTests.GOOD_CODE
        for text in (code, '\n'.join('    ' + line for line in code.splitlines())):
            result = self.v.validate(CASES[3], text)
            self.assertEqual(check(result, 'python_syntax')['status'], 'pass')
            self.assertEqual(check(result, 'python_correction')['status'], 'pass')
        valid_other = code.replace('    if bucket is None:\n        bucket = []',
                                   '    if bucket is None:\n        bucket = []\n    else:\n        bucket = bucket')
        result = self.v.validate(CASES[3], '```python\n' + valid_other + '\n```')
        self.assertNotEqual(check(result, 'python_correction')['status'], 'fail')
        self.assertEqual(check(result, 'python_runtime')['status'], 'pending')

    def test_inline_json_malformed_quotes_and_curl_substitution_are_nonexecution(self):
        curl = CodeAndBoundTests.GOOD_CURL.replace('\\\n', '')
        text = curl + '\n\nSucesso: `{"status":"queued","id":"job_123"}`'
        for name in ('curl_contract', 'json_syntax', 'success_json'):
            self.assertEqual(check(self.v.validate(CASES[2], text), name)['status'], 'pass')
        text = text.replace('"id":"job_123"}', '"id":"job_123",}')
        self.assertEqual(check(self.v.validate(CASES[2], text), 'json_syntax')['status'], 'fail')
        dangerous = curl.replace('<TOKEN>', '$(cat /tmp/secret)')
        self.assertEqual(check(self.v.validate(CASES[2], dangerous), 'curl_contract')['status'], 'fail')

    def test_determinism_under_changed_decimal_context_and_repeated_calls(self):
        from decimal import localcontext
        text = 'Total local: R$ 216 mil. Total nuvem: R$ 144 mil. Diferença: R$ 72 mil.'
        expected = self.v.validate(CASES[15], text)
        with localcontext() as context:
            context.prec = 2
            self.assertEqual(self.v.validate(CASES[15], text), expected)
        self.assertEqual(self.v.validate(CASES[15], text), expected)
        self.assertEqual(CASES, json.loads((TESTS / 'experiments/cases.json').read_text())['cases'])

    def test_fuzzed_candidates_are_bounded_json_safe_and_never_crash(self):
        import random
        rng = random.Random(17)
        alphabet = '0123456789 abcDEF.,;()[]{}\\n\\t|#*_±−\\x00á'
        for _ in range(40):
            text = ''.join(rng.choice(alphabet) for _ in range(rng.randrange(0, 250)))
            for case in CASES:
                result = self.v.validate(case, text)
                self.assertEqual(result['word_count'], len(text.split()))
                self.assertEqual(result['semantic_review'], 'pending')
                json.dumps(result, allow_nan=False)


if __name__ == '__main__':
    unittest.main()
