"""Testes offline das regras de tabela.py, só com biblioteca padrão."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('tabela', Path(__file__).resolve().parent / 'tabela.py')
tabela = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tabela)


class TabelaTests(unittest.TestCase):
    def test_duplicate_judge_in_pair_fails(self):
        vote = dict(case='01-x', route=0, pair_id='p000', judge='jev')
        with self.assertRaisesRegex(ValueError, 'juiz duplicado'):
            tabela.pairs_of([vote, dict(vote)])
        self.assertEqual(len(tabela.pairs_of([vote, dict(vote, judge='astra')])), 1)

    def test_reference_comes_from_each_row(self):
        row = dict(versao='0.9.0', referencia='0.8.0', situacao='Aceita.',
                   fixo=dict(amostra='456 de 456 pares', h=(40.0, 46.0), votos=(30, 20, 2)))
        line = tabela.main_table('', [row]).splitlines()[2]
        self.assertIn('| 0.9.0 | 0.8.0 |', line)
        self.assertNotIn('sem skill', line)
        self.assertTrue(all('referencia' in r for r in tabela.ROWS))
        self.assertIn('| 0.8.0 | não se aplica |', tabela.main_table(''))

    def test_removed_link_target_and_anchor_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, other = Path(tmp) / 'doc.md', Path(tmp) / 'outro.md'
            other.write_text('# Título certo\n', encoding='utf-8')
            doc.write_text('[a](removido.md) [b](outro.md#titulo-errado) [c](outro.md#título-certo) [d](https://x.y)\n',
                           encoding='utf-8')
            bad = tabela.broken_links([doc])
        self.assertEqual([b.split(': ')[1] for b in bad], ['removido.md', 'outro.md#titulo-errado'])


if __name__ == '__main__':
    unittest.main()
