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
        self.assertIn('Humanização percebida não medida', text)
        self.assertIn('[Teste funcional](results/reviews/0.8.0/SMOKE.md)', text)
        self.assertIn('[Relatório legível](results/README.md#avaliação-mais-recente)', text)
        self.assertIn('[Histórico](results/README.md#histórico-das-avaliações)', text)
        for old in ('0.7.0', '40,27', '+13,53', '| Versão |', '| Indicador |', 'ΔH'):
            self.assertNotIn(old, text)

    def test_resumo_atual_traz_conclusao_situacao_curta_e_tabela_simples(self):
        run = '2026-10-20-0.8.0'
        row = next(r for r in tabela.ROWS if r.get('run') == run)
        text = tabela.resumo_ultimo('results/', rows=[row])
        lines = text.split('\n\n')
        # Conclusão ligada à amostra, sem números antes da tabela; situação numa frase curta.
        self.assertIn('pareceram mais humanos', lines[0])
        self.assertIn('receberam mais votos de preferência', lines[0])
        self.assertNotRegex(lines[0], r'\d')
        self.assertEqual(lines[1], 'Avaliação parcial de 20/10: 2 de 456 pares, gerados com Opus 5.5 '
                                   'e avaliados por Jev, Astra e Opus; ciclo ainda inconclusivo.')
        self.assertIn('| Indicador | Sem skill | Com a skill 0.8.0 | Variação |', text)
        self.assertIn('| Humanização percebida, 0 a 100 | 31,67 | 47,33 | +15,67 pontos |', text)
        self.assertIn('| Preferência dos juízes, votos | 2 de 6 | 4 de 6 | +2 |', text)
        self.assertIn('| Falhas factuais críticas, julgamentos | 1 de 6 | 0 de 6 | -1 |', text)
        self.assertIn('| Tokens por texto, média | 1766,00 | 10264,50 | +481,23% |', text)
        self.assertIn('| Segundos de geração por texto, média | 16,66 | 18,93 | +13,62% |', text)
        self.assertIn('três modelos juízes', text)
        self.assertIn('de 0 a 100', text)
        self.assertIn('[Relatório legível](results/README.md#avaliação-mais-recente)', text)
        self.assertIn(f'[Evidência original da rodada](results/runs/{run}/README.md)', text)
        self.assertIn('[Histórico](results/README.md#histórico-das-avaliações)', text)
        for detail in ('15 minutos', 'exige', '97,72', 'acréscimo', 'Leitura', 'ΔH', 'baseline', 'Situação'):
            self.assertNotIn(detail, text)

    def test_resumo_calcula_denominadores_e_cobertura_por_metrica(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        text = tabela.resumo_ultimo('', rows=[row])
        self.assertIn('Avaliação parcial de 19/10: 22 de 456 pares, gerados com Opus 5.5', text)
        self.assertIn('; sem decisão registrada.', text)
        self.assertIn('| 31 de 66 | 35 de 66 | +4 |', text)
        self.assertIn('| 2 de 66 | 1 de 66 | -1 |', text)
        self.assertIn('| Tokens por texto, média de 49 pares | 1362,31 | 6983,69 | +412,64% |', text)
        self.assertIn('| Segundos de geração por texto, média de 49 pares | 16,65 | 19,55 | +17,43% |', text)
        s = copy.deepcopy(tabela.SUM[row['run']])
        s['data']['cobertura']['pares_tres_juizes']['esperado'] = 100
        s['decisao'] = dict(status='aceita')
        text = tabela.resumo_ultimo('', rows=[row], summaries={row['run']: s})
        self.assertIn('Avaliação parcial de 19/10: 22 de 100 pares', text)
        self.assertIn('; versão aceita.', text)
        s['data']['cobertura']['pares_tres_juizes']['esperado'] = s['n']
        text = tabela.resumo_ultimo('', rows=[row], summaries={row['run']: s})
        self.assertIn('Avaliação completa de 19/10: 22 de 22 pares', text)
        self.assertNotIn('parcial', text)

    def test_ganho_negativo_nao_vira_ganho(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        s = copy.deepcopy(tabela.SUM[row['run']])
        s['h'] = (s['h'][1], s['h'][0])
        s['votos'] = (s['votos'][1], s['votos'][0], s['votos'][2])
        text = tabela.resumo_ultimo('', rows=[row], summaries={row['run']: s})
        self.assertIn('pareceram menos humanos', text.split('\n\n')[0])
        self.assertIn('receberam menos votos de preferência', text.split('\n\n')[0])
        self.assertIn('-13,53 pontos', text)
        self.assertNotIn('mais humanos', text)

    def test_relatorio_atual_traz_situacao_juizes_recursos_textos_e_evidencia_bruta(self):
        run = '2026-10-20-0.8.0'
        row = next(r for r in tabela.ROWS if r.get('run') == run)
        text = tabela.relatorio_atual('', rows=[row])
        self.assertIn('pareceram mais humanos', text)
        self.assertIn('Amostra: 2 de 456 pares; 2 de 24 pedidos; só claude-opus-5.5; juízes Jev, Astra e Opus.', text)
        self.assertIn('**Situação:** ' + row['situacao'], text)
        self.assertIn('exige os 456 pares planejados', text)
        self.assertIn('| 31,67 | 47,33 | +15,67 pontos |', text)
        self.assertIn('| 2 de 6 | 4 de 6 | +2 |', text)
        self.assertIn('| 1 de 6 | 0 de 6 | -1 |', text)
        self.assertIn('| 1766,00 | 10264,50 | +481,23% |', text)
        self.assertIn('| 16,66 | 18,93 | +13,62% |', text)
        self.assertIn('97,72% do acréscimo de tokens vem da entrada', text)
        self.assertIn('Jev 36,50 → 42,00 (+5,50); Astra 21,00 → 45,00 (+24,00); Opus 37,50 → 55,00 (+17,50)', text)
        self.assertIn(f'[01. Jornalístico: notícia sobre bibliotecas](runs/{run}/experiments/01-noticia-bibliotecas/REPORT.md)', text)
        self.assertIn(f'[02. Jornalístico: reportagem sobre drenagem](runs/{run}/experiments/02-reportagem-drenagem/REPORT.md)', text)
        for title, target in (('relatório da rodada', 'README.md'), ('dados objetivos', 'OBJETIVO.json'),
                              ('decisão', 'DECISION.json'), ('SHA256SUMS', 'SHA256SUMS')):
            self.assertIn(f'[{title}](runs/{run}/{target})', text)
        self.assertNotIn('#avaliação-mais-recente', text)
        self.assertNotIn('ΔH', text)

    def test_relatorio_atual_pendente_nao_inventa_metricas(self):
        text = tabela.relatorio_atual('', rows=[PENDING])
        self.assertIn('Humanização percebida não medida', text)
        self.assertIn('[Teste funcional](reviews/0.8.0/SMOKE.md)', text)
        self.assertNotIn('| Indicador |', text)

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
        self.assertIn('Humanização percebida não medida', text)
        self.assertIn('0 de 456 pares', text)
        self.assertIn('sem decisão registrada', text)
        self.assertIn('Bloqueada. Inconclusiva.', tabela.relatorio_atual('', rows=[row], summaries={run: s}))
        self.assertNotIn('Tokens', text)
        self.assertNotIn('Segundos de geração', text)
        self.assertNotIn('| Indicador |', text)
        self.assertNotIn('nan', text)
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
        self.assertIn('### Por juiz', text)
        self.assertIn('### Textos e votos por pedido', text)

    def test_render_separa_resumo_e_historico(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results = root / 'results'
            results.mkdir()
            readme = root / 'README.md'
            history = results / 'README.md'
            readme.write_text('<!-- resumo:inicio -->\n<!-- resumo:fim -->', encoding='utf-8')
            history.write_text('<!-- atual:inicio -->\n<!-- atual:fim -->\n<!-- tabela:inicio -->\n<!-- tabela:fim -->',
                               encoding='utf-8')
            history_rows = [PENDING] + [r for r in tabela.ROWS if r.get('run') == '2026-10-19-max']
            with patch.object(tabela, 'ROWS', history_rows), patch.object(tabela, 'RESULTS', results), patch.object(
                    tabela, 'TARGETS', [(readme, 'results/'), (history, '')]):
                out = tabela.rendered()
        self.assertIn('0.7.0', out[readme])
        self.assertIn('| Indicador |', out[readme])
        self.assertNotIn('| Versão |', out[readme])
        self.assertNotIn('pendente', out[readme])
        current, past = out[history].split('<!-- tabela:inicio -->')
        self.assertIn('| Indicador |', current)
        self.assertIn('runs/2026-10-19-max/OBJETIVO.json', current)
        self.assertNotIn('| Versão |', current)
        self.assertIn('| Versão |', past)
        self.assertIn('pendente', past)

    def test_render_sem_marcador_atual_mantem_historico(self):
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / 'README.md'
            history.write_text('<!-- tabela:inicio -->\n<!-- tabela:fim -->', encoding='utf-8')
            with patch.object(tabela, 'RESULTS', Path(tmp)), patch.object(tabela, 'TARGETS', [(history, '')]):
                out = tabela.rendered()
        self.assertIn('| Versão |', out[history])
        self.assertNotIn('| Indicador |', out[history])

    def test_metricas_opcionais_aceitam_nulo_sem_inventar_percentual(self):
        row = next(r for r in tabela.ROWS if r.get('run') == '2026-10-19-max')
        s = copy.deepcopy(tabela.SUM[row['run']])
        s['data']['tokens'] = None
        s['data']['tempo']['geracao_api']['variacao_percentual_razao_somas'] = None
        for render in (tabela.resumo_ultimo, tabela.relatorio_atual):
            text = render('', rows=[row], summaries={row['run']: s})
            self.assertNotIn('Tokens', text)
            self.assertNotIn('tokens', text)
            self.assertIn('| Segundos de geração por texto, média de 49 pares | 16,65 | 19,55 | n/d |', text)
            self.assertNotIn('%', text)

    def test_nova_run_substitui_pendencia_somente_no_resumo(self):
        # Fixture de apresentação; os números continuam na memória, sem publicar uma rodada.
        run = '2026-10-20-0.8.0'
        row = dict(versao='0.8.0', run=run, referencia='sem skill', situacao='Parcial. Inconclusiva.')
        s = tabela.SUM['2026-10-19-max']
        text = tabela.resumo_ultimo('results/', rows=[PENDING, row], summaries={run: s})
        self.assertIn('skill 0.8.0', text)
        self.assertIn('Parcial. Inconclusiva.', tabela.relatorio_atual('', rows=[PENDING, row], summaries={run: s}))
        self.assertIn(f'[Evidência original da rodada](results/runs/{run}/README.md)', text)
        self.assertNotIn('pendente', text)
        self.assertNotIn('SMOKE.md', text)
        self.assertNotIn('0.7.0', text)
        with patch.dict(tabela.SUM, {run: s}):
            table = tabela.main_table('', rows=[PENDING, row])
        self.assertIn('SMOKE.md', table)
        self.assertIn(f'runs/{run}/README.md', table)


if __name__ == '__main__':
    unittest.main()
