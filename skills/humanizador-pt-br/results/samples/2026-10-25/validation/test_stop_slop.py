"""0.9.1: três diagnósticos condicionais adaptados do parecer STOP-SLOP, apenas com biblioteca padrão.

Os diagnósticos chegam ao uso pela SKILL.md e por metadados do catálogo consultados por catalog e audit. Os
briefings protegidos por impressão digital não mudam, e nenhum veto universal do upstream entra na skill.
"""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
SCRIPT = SKILL_DIR / 'scripts/humanizar.py'
CATALOG = SKILL_DIR / 'references/catalogo.json'
UPSTREAM_COMMIT = '8da1f030185bdfe8471220585162991eaeb970e9'
BASELINE_COMMIT = '72c1d8522b5764f5b36f0aafa6df2c09bee6efa5'
# Diagnóstico: regra que o carrega e trechos que a ação ou as exceções precisam declarar.
DIAGNOSTICS = {
    'tranquilizacao-automatica': ('PTBR-17', ('sem função no artefato', 'acolhimento', 'voz do autor')),
    'fechos-repetidos': ('PTBR-16', ('desenvolvimento', 'frase curta', 'fecho memorável', 'pergunta legítima')),
    'responsabilidade-escondida': ('PTBR-30', ('material', 'importar', 'nunca invente agente',
                                               'sujeito não humano legítimo', 'o servidor envia a resposta')),
}
# Vetos universais e exemplos do upstream que o parecer manda não importar.
REJECTED = ('advérbio', 'passiva', 'formalidade', 'lista de três', 'grupos de três')
UPSTREAM_EXAMPLES = ("that's okay", 'most teams', 'nobody admits', 'move faster')


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def module():
    return _load('humanizar', SCRIPT)


# A suíte original fornece as impressões digitais 0.9.0; só o módulo é carregado, sem expor suas classes aqui.
SUITE = _load('test_humanizar', HERE / 'test_humanizar.py')


def cli_run(*args):
    return subprocess.run([sys.executable, '-W', 'error', str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def diagnostics(rules):
    return {d['id']: (rule['id'], d) for rule in rules for d in rule.get('diagnosticos', [])}


def flagged(h, text, rules, diagnostic_id):
    return [item for item in h.audit(text, rules).get('diagnosticos_condicionais', [])
            if item['diagnostico'] == diagnostic_id]


def words(text):
    return set(re.findall(r'\w+', text.casefold()))


class CatalogMetadataTests(unittest.TestCase):
    """Os diagnósticos são metadados de regras existentes: o catálogo continua com 32 regras."""

    def test_three_rules_carry_one_conditional_diagnostic_each_with_exceptions_and_source(self):
        h = module()
        rules = h.load_catalog(CATALOG)
        self.assertEqual(len(rules), 32)
        found = diagnostics(rules)
        self.assertEqual(set(found), set(DIAGNOSTICS), 'só os três diagnósticos do parecer entram no catálogo')
        parecer = (SKILL_DIR / 'context/STOP-SLOP.md').read_text('utf-8')
        for diagnostic_id, (rule_id, required) in DIAGNOSTICS.items():
            with self.subTest(diagnostic=diagnostic_id):
                owner, item = found[diagnostic_id]
                self.assertEqual(owner, rule_id)
                self.assertTrue(item['excecoes'] and all(isinstance(e, str) and e.strip() for e in item['excecoes']))
                declared = ' '.join([item['acao']] + item['excecoes']).casefold()
                for phrase in required:
                    self.assertIn(phrase, declared)
                source = item['fonte']
                self.assertEqual(source['commit'], UPSTREAM_COMMIT)
                self.assertIn(BASELINE_COMMIT, source['baseline'])
                self.assertEqual(source['parecer'], 'context/STOP-SLOP.md')
                # Fonte registrada pelo parecer local, sem download: commit e trecho precisam constar dele.
                self.assertIn(UPSTREAM_COMMIT + '/' + source['trecho'], parecer)

    def test_examples_keep_the_facts_and_audit_tells_them_apart(self):
        h = module()
        rules = h.load_catalog(CATALOG)
        found = diagnostics(rules)
        self.assertEqual(set(found), set(DIAGNOSTICS))
        for diagnostic_id, (_, item) in found.items():
            example = item['exemplo']
            with self.subTest(diagnostic=diagnostic_id):
                self.assertLessEqual(words(example['revisado']),
                                     words(example['texto']) | words(example.get('material', '')),
                                     'a forma revisada não acrescenta fato ausente do texto ou do material')
                self.assertTrue(flagged(h, example['texto'], rules, diagnostic_id))
                self.assertEqual(flagged(h, example['revisado'], rules, diagnostic_id), [])
                for kept in item.get('mantem', []):
                    self.assertEqual(flagged(h, kept, rules, diagnostic_id), [], kept)

    def test_no_universal_veto_or_upstream_example_enters_the_catalog_or_the_skill(self):
        h = module()
        found = diagnostics(h.load_catalog(CATALOG))
        self.assertEqual(set(found), set(DIAGNOSTICS))
        for diagnostic_id, (_, item) in found.items():
            text = json.dumps(item, ensure_ascii=False).casefold()
            for term in REJECTED:
                with self.subTest(diagnostic=diagnostic_id, term=term):
                    self.assertNotIn(term, text)
        material = (CATALOG.read_text('utf-8') + (SKILL_DIR / 'SKILL.md').read_text('utf-8')).casefold()
        for example in UPSTREAM_EXAMPLES:
            self.assertNotIn(example, material)

    def test_malformed_diagnostics_are_rejected_when_the_catalog_loads(self):
        h = module()
        base = {'id': 'x', 'pattern': 'vale destacar'}
        good = {'id': 'd', 'acao': 'Leia.', 'excecoes': ['Uso literal.'], 'padrao': 'tudo bem'}
        structural = dict({k: v for k, v in good.items() if k != 'padrao'}, verificacao='fechos_repetidos')
        with tempfile.TemporaryDirectory() as folder:
            catalog = Path(folder) / 'rules.json'
            catalog.write_text(json.dumps([dict(base, diagnosticos=[good, dict(structural, id='e')])]),
                               encoding='utf-8')
            self.assertEqual(h.load_catalog(catalog)[0]['diagnosticos'], [good, dict(structural, id='e')])
            for invalid in ([dict(good, excecoes=[])], [dict(good, padrao='[')], [dict(good, padrao='a?')],
                            [{k: v for k, v in good.items() if k != 'padrao'}],
                            [{k: v for k, v in good.items() if k != 'acao'}],
                            [dict(good, verificacao='fechos_repetidos')], [dict(structural, verificacao='outra')],
                            [good, good], 'tudo bem'):
                catalog.write_text(json.dumps([dict(base, diagnosticos=invalid)]), encoding='utf-8')
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    h.load_catalog(catalog)


class ConsumptionTests(unittest.TestCase):
    """catalog e audit consomem os metadados; nada vira bloqueio nem vício contado."""

    def test_catalog_cli_finds_each_diagnostic_with_its_exceptions(self):
        for query, rule_id, diagnostic_id in [('tudo bem', 'PTBR-17', 'tranquilizacao-automatica'),
                                              ('frase de efeito', 'PTBR-16', 'fechos-repetidos'),
                                              ('a decisão surgiu', 'PTBR-30', 'responsabilidade-escondida')]:
            with self.subTest(query=query):
                result = cli_run('catalog', '--query', query)
                self.assertEqual(result.returncode, 0, result.stderr)
                rule = next(r for r in json.loads(result.stdout) if r['id'] == rule_id)
                item = next(d for d in rule['diagnosticos'] if d['id'] == diagnostic_id)
                self.assertTrue(item['excecoes'])

    def test_audit_cli_reports_conditional_review_with_exceptions_without_counting_a_vice(self):
        text = 'O formulário agora pede o CPF. E tudo bem.\n'
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'texto.txt'
            source.write_text(text, encoding='utf-8')
            result = cli_run('audit', source)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        items = report['diagnosticos_condicionais']
        self.assertEqual([(i['rule_id'], i['diagnostico'], i['original']) for i in items],
                         [('PTBR-17', 'tranquilizacao-automatica', 'E tudo bem')])
        self.assertEqual(text[items[0]['start']:items[0]['end']], 'E tudo bem')
        self.assertIn('sem função no artefato', items[0]['acao'])
        self.assertTrue(any('acolhimento' in e for e in items[0]['excecoes']))
        self.assertTrue(any('voz do autor' in e for e in items[0]['excecoes']))
        self.assertEqual(report['rule_counts']['PTBR-17']['count'], 0)
        self.assertNotIn('PTBR-17', [f['rule_id'] for f in report['findings']])
        h = module()
        self.assertTrue(h.check(text, h.load_catalog(CATALOG))['deliverable'], 'diagnóstico condicional não bloqueia')


class AuditBehaviorTests(unittest.TestCase):
    """Cada sinal é estreito: pede leitura do caso, nunca corte automático."""

    def rules(self):
        return module().load_catalog(CATALOG)

    def assertFlags(self, diagnostic_id, positives, negatives):
        h, rules = module(), self.rules()
        for text in positives:
            with self.subTest(text=text):
                self.assertEqual(len(flagged(h, text, rules, diagnostic_id)), 1)
        for text in negatives:
            with self.subTest(text=text):
                self.assertEqual(flagged(h, text, rules, diagnostic_id), [])

    def test_reassurance_needs_a_clause_of_its_own(self):
        self.assertFlags('tranquilizacao-automatica',
                         ['O formulário agora pede o CPF. E tudo bem.',
                          'Errar na primeira tentativa é comum, e tudo bem.',
                          'O servidor reiniciou. E não há problema nisso.',
                          'E está tudo bem se a primeira versão sair incompleta.'],
                         ['Está tudo bem com o servidor.', 'Tudo bem, vamos ao cadastro.',
                          'Ela perguntou se estava tudo bem.', 'O teste passou e não há problema de memória.'])

    def test_only_paragraph_endings_repeated_across_paragraphs_are_flagged(self):
        h, rules = module(), self.rules()
        text = 'O cadastro ficou mais rápido. E isso muda tudo.\n\nO suporte recebe menos chamados. E isso muda tudo.\n'
        items = flagged(h, text, rules, 'fechos-repetidos')
        self.assertEqual([(i['original'], i['repeticoes']) for i in items], [('E isso muda tudo.', 2)] * 2)
        self.assertEqual([text[i['start']:i['end']] for i in items], ['E isso muda tudo.'] * 2)
        self.assertTrue(all('frase curta' in ' '.join(i['excecoes']) for i in items))
        for kept in ['O cadastro ficou mais rápido. Simples assim.\n\nO suporte recebe menos chamados.',
                     'O cadastro ficou mais rápido.\n\nO suporte recebe menos chamados. Vale manter o balcão?',
                     'O cadastro ficou mais rápido. E isso muda tudo. E isso muda tudo.',
                     'O prazo é de dois dias.\n\nO custo é de 300 reais.\n\nA garantia é de um ano.']:
            with self.subTest(text=kept):
                self.assertEqual(flagged(h, kept, rules, 'fechos-repetidos'), [])

    def test_hidden_decision_is_flagged_but_named_agents_passives_and_non_human_subjects_are_not(self):
        self.assertFlags('responsabilidade-escondida',
                         ['A decisão surgiu na reunião de março.',
                          'A decisão de adiar a reforma da biblioteca surgiu.',
                          'As mudanças nasceram de uma conversa no corredor.',
                          'A medida surge como resposta ao atraso.'],
                         ['O servidor envia a resposta em JSON.', 'A diretoria decidiu adiar a reforma.',
                          'A reforma foi adiada.', 'A decisão foi tomada quando surgiu o problema.',
                          'A mudança aparece no relatório.'])


class SkillGuidanceTests(unittest.TestCase):
    """A orientação geral chega à redação e à revisão pela SKILL.md, dentro do teto de tamanho."""

    def test_skill_md_carries_the_three_diagnostics_with_their_exceptions_outside_the_mode_contract(self):
        skill = (SKILL_DIR / 'SKILL.md').read_text('utf-8')
        craft = ' '.join(skill[skill.index('## Como escrever bem'):skill.index('## Fidelidade')].split()).casefold()
        for phrase in ['"e tudo bem"', 'sem função no artefato', 'acolhimento pedido', 'voz do autor',
                       'frase de efeito', 'desenvolvimento', 'frase curta', 'fecho memorável', 'pergunta legítima',
                       '"a decisão surgiu"', 'só se o material', 'importar', 'nunca invente agente',
                       'sujeito não humano legítimo', '"o servidor envia a resposta"']:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, craft)
        mode = skill[skill.index('## Modo'):skill.index('## Como escrever bem')]
        self.assertNotIn('tudo bem', mode, 'o contrato de modo e revisão não muda')
        self.assertLessEqual(len(skill), SUITE.SKILL_MD_090)


class BriefPayloadTests(unittest.TestCase):
    """Metadados novos não entram no briefing: as impressões digitais 0.9.0 continuam valendo."""

    def test_diagnostics_reach_catalog_and_audit_but_not_the_fingerprinted_briefs(self):
        h = module()
        self.assertEqual(set(diagnostics(h.load_catalog(CATALOG))), set(DIAGNOSTICS))
        markers = ('E tudo bem', 'a decisão surgiu', 'frase de efeito', UPSTREAM_COMMIT)
        for profile, genre in SUITE.Redacao091Tests().pairs(h):
            for mode in ('redacao', 'revisao'):
                with self.subTest(profile=profile, genre=genre, mode=mode):
                    data = h.brief(profile, genre, 2, 0, 17, modo=mode)
                    self.assertTrue(all('diagnosticos' not in rule for rule in data['rules']))
                    text = h.brief_text(data)
                    for marker in markers:
                        self.assertNotIn(marker, text)
        helper = SUITE.Redacao091Tests()
        self.assertEqual(helper.fingerprint(h, 'redacao', SUITE._redacao_estavel), SUITE.REDACAO_ESTAVEL_090)
        self.assertEqual(helper.fingerprint(h, 'revisao', SUITE._sem_versao), SUITE.REVISAO_090)


class DocumentationTests(unittest.TestCase):
    """O README da candidata declara objetivo, diagnósticos e efeito ainda não medido."""

    def test_readme_states_goal_diagnostics_and_unmeasured_status(self):
        readme = (SKILL_DIR / 'README.md').read_text('utf-8')
        folded = readme.casefold()
        for phrase in ['humanização percebida', 'fidelidade', 'tokens', 'critério de sucesso', '"e tudo bem"',
                       'frase de efeito', '"a decisão surgiu"', 'não medido']:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, folded)
        self.assertRegex(readme, r'(?m)^python3 scripts/humanizar\.py catalog --query ')
        self.assertNotIn('—', readme)


if __name__ == '__main__':
    unittest.main()
