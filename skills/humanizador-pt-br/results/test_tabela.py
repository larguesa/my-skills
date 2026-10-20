"""Testes locais da apresentação, sem chamadas de API nem escrita nas rodadas."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tabela


PENDING = dict(versao='0.8.0', referencia='não se aplica',
               situacao='Candidata do primeiro ciclo A/B, pendente.',
               fixo=dict(amostra='Sem A/B: 5 textos do MiMo 2.6 Pro, sem juízes'),
               links=[('teste funcional', 'reviews/0.8.0/SMOKE.md')])


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


class ResumoUltimoTests(unittest.TestCase):
    def test_pendente_nao_herda_numeros_da_versao_anterior(self):
        self.assertTrue(callable(getattr(tabela, 'resumo_ultimo', None)))
        with patch.object(tabela, 'main_table', side_effect=AssertionError('histórico')):
            text = tabela.resumo_ultimo('results/', rows=[PENDING])
        self.assertIn('0.8.0', text)
        self.assertIn('pendente', text)
        self.assertIn('5 textos', text)
        self.assertIn('H e ΔH não medidos', text)
        self.assertIn('[Relatório](results/reviews/0.8.0/SMOKE.md)', text)
        self.assertIn('[Histórico](results/README.md)', text)
        for old in ('0.7.0', '40,27', '+13,53', '| Versão |'):
            self.assertNotIn(old, text)

    def test_run_publicado_mostra_metricas_cobertura_e_recursos(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        text = tabela.resumo_ultimo('results/', rows=[row])
        self.assertIn('H 40,27', text)
        self.assertIn('26,74 na referência (sem skill)', text)
        self.assertIn('ΔH +13,53 pontos', text)
        self.assertIn('22 de 456 pares', text)
        self.assertIn('Parcial:', text)
        self.assertIn('35 / 31 / 0 de 66', text)
        self.assertIn('Tokens totais', text)
        self.assertIn('1362,31 → 6983,69', text)
        self.assertIn('+412,64%', text)
        self.assertIn('Tempo de geração na API', text)
        self.assertIn('16,65 → 19,55 s', text)
        self.assertIn('+17,43%', text)
        self.assertIn('49 de 456 pares', text)
        self.assertIn('[Relatório](results/runs/2026-10-19-max/README.md)', text)
        self.assertNotIn('0.8.0', text)

    def test_sem_pares_completos_nao_inventa_media(self):
        # Fixture sintética só em diretório temporário, nunca em runs/ real.
        data = copy.deepcopy(tabela.SUM['2026-10-19-max']['data'])
        data['julgamentos_pareados'] = []
        data['cobertura']['pares_tres_juizes']['observado'] = 0
        rec = data['percepcao']['pares_tres_juizes']['humanizacao']
        rec.update(pares=0, baseline={'media': None}, skill={'media': None})
        for j in tabela.JUDGES:
            same = data['por_juiz'][j]['mesmos_pares_tres_juizes']
            same['humanizacao'] = copy.deepcopy(rec)
            same['preferencias'] = {}
        data.pop('tokens')
        data.pop('tempo')
        run = '2026-10-20-0.8.0'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / 'runs' / run
            folder.mkdir(parents=True)
            (folder / 'OBJETIVO.json').write_text(json.dumps(data), encoding='utf-8')
            with patch.object(tabela, 'RESULTS', root):
                s = tabela.summary(run)
        self.assertIsNone(s['h'])
        row = dict(versao='0.8.0', run=run, referencia='sem skill', situacao='Bloqueada. Inconclusiva.')
        text = tabela.resumo_ultimo('results/', rows=[row], summaries={run: s})
        self.assertIn('H e ΔH não medidos', text)
        self.assertIn('0 de 456 pares', text)
        self.assertIn('Bloqueada. Inconclusiva.', text)
        self.assertNotIn('Tokens totais', text)
        self.assertNotIn('Tempo de geração', text)
        with patch.dict(tabela.SUM, {run: s}):
            table = tabela.main_table('', rows=[row])
        self.assertIn('não medido', table)
        self.assertNotIn('nan', table)

    def test_detalhes_sem_pares_mostra_nao_medido(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        s = copy.deepcopy(tabela.SUM[row['run']])
        for judge in s['juizes'].values():
            judge['h'] = None
        with patch.object(tabela, 'ROWS', [row]), patch.dict(tabela.SUM, {row['run']: s}):
            text = tabela.details()
        self.assertIn('| não medido | não medido | n/d |', text)

    def test_render_separa_resumo_e_historico(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / 'results'
            results.mkdir()
            readme = root / 'README.md'
            history = results / 'README.md'
            readme.write_text('<!-- resumo:inicio -->\n<!-- resumo:fim -->', encoding='utf-8')
            history.write_text('<!-- tabela:inicio -->\n<!-- tabela:fim -->', encoding='utf-8')
            history_rows = [r for r in tabela.ROWS if r.get('run') == '2026-10-19-max'] + [PENDING]
            with patch.object(tabela, 'ROWS', history_rows), patch.object(tabela, 'RESULTS', results), patch.object(
                    tabela, 'TARGETS', [(readme, 'results/'), (history, '')]):
                out = tabela.rendered()
        self.assertIn('0.8.0', out[readme])
        self.assertNotIn('| Versão |', out[readme])
        self.assertNotIn('0.7.0', out[readme])
        self.assertIn('| Versão |', out[history])
        self.assertIn('0.7.0', out[history])

    def test_metricas_opcionais_aceitam_nulo_sem_inventar_percentual(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        s = copy.deepcopy(tabela.SUM[row['run']])
        s['data']['tokens'] = None
        s['data']['tempo']['geracao_api']['variacao_percentual_razao_somas'] = None
        text = tabela.resumo_ultimo('', rows=[row], summaries={row['run']: s})
        self.assertNotIn('Tokens totais', text)
        self.assertIn('Tempo de geração na API', text)
        self.assertNotIn('%', text)

    def test_nova_run_substitui_pendencia_somente_no_resumo(self):
        # Fixture de apresentação; os números continuam na memória, sem publicar uma rodada.
        run = '2026-10-20-0.8.0'
        row = dict(versao='0.8.0', run=run, referencia='sem skill', situacao='Parcial. Inconclusiva.')
        s = tabela.SUM['2026-10-19-max']
        text = tabela.resumo_ultimo('results/', rows=[PENDING, row], summaries={run: s})
        self.assertIn('0.8.0: Parcial. Inconclusiva.', text)
        self.assertIn(f'[Relatório](results/runs/{run}/README.md)', text)
        self.assertNotIn('pendente', text)
        self.assertNotIn('SMOKE.md', text)
        self.assertNotIn('0.7.0', text)
        with patch.dict(tabela.SUM, {run: s}):
            table = tabela.main_table('', rows=[PENDING, row])
        self.assertIn('SMOKE.md', table)
        self.assertIn(f'runs/{run}/README.md', table)


if __name__ == '__main__':
    unittest.main()
