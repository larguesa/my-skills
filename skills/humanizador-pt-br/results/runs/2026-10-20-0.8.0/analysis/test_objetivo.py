"""Testes artificiais explícitos. Nunca representam resultados reais."""
import importlib.util
import math
from pathlib import Path
import unittest
import base64
import copy
import json
import hashlib
import socket
import tempfile
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load_subject():
    path = HERE / 'agregar_objetivo.py'
    if not path.exists():
        raise AssertionError('agregador ainda não implementado')
    spec = importlib.util.spec_from_file_location('agregar_objetivo', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ComparacoesArtificiais(unittest.TestCase):
    def test_razao_das_somas_nao_media_dos_percentuais(self):
        subject = load_subject()
        result = subject.compare_pairs([(10, 20), (100, 110)])
        self.assertEqual(result['pares'], 2)
        self.assertEqual(result['baseline']['soma'], 110)
        self.assertEqual(result['skill']['media'], 65)
        self.assertAlmostEqual(result['variacao_percentual_razao_somas'], 100 * (130 / 110 - 1))
        self.assertAlmostEqual(result['media_variacoes_pareadas_percentuais'], 55)
        self.assertEqual(result['baseline']['media'], 55)
        self.assertEqual(result['diferenca_media'], 10)
        self.assertAlmostEqual(result['variacao_percentual_razao_medias'], result['variacao_percentual_razao_somas'])
        self.assertIsNone(subject.compare_pairs([])['baseline']['soma'])
        zero = subject.compare_pairs([(0, 10)])
        self.assertIsNone(zero['variacao_percentual_razao_somas'])
        self.assertEqual(zero['baseline']['soma'], 0)
        self.assertEqual(zero['skill']['soma'], 10)
        self.assertEqual(zero['pares_baseline_positivo'], 0)
        for value in [float('nan'), float('inf'), True, -1]:
            with self.assertRaises(ValueError):
                subject.compare_pairs([(value, 1)])


def artificial_records():
    """Dados inventados exclusivamente para testar aritmética e mapeamento."""
    routes = [dict(model='artificial/modelo', mode=mode, endpoint=dict(tag='offline'))
              for mode in ('off', 'on')]
    config = dict(cases=[dict(id='caso-01'), dict(id='caso-02')], routes=routes)
    records, blinds = {}, {}
    for ci, case in enumerate(config['cases']):
        cid = case['id']
        mapping, pairs = {}, {}
        for ri in range(2):
            pid = f'p{ri:03}'
            pair = {'A': f't{ri * 2:03}', 'B': f't{ri * 2 + 1:03}'}
            pairs[pid] = pair
            for ai, arm in enumerate(('baseline', 'skill')):
                slot = f'g.{cid}.r{ri:02}.{arm}'
                mapping[pair['AB'[ai]]] = slot
                p, c, elapsed = ((10, 90, 2) if ai == 0 else (30, 120, 4)) if ri == 0 else (
                    (100, 100, 20) if ai == 0 else (120, 100, 22))
                call = dict(slot=slot, phase='generation', case=cid, route=ri, arm=arm,
                            model=routes[ri]['model'], mode=routes[ri]['mode'])
                result = dict(status='completed', text='TEXTO ARTIFICIAL  \n\u2028preservado',
                    elapsed_seconds=elapsed, validation_issues=[],
                    telemetry=dict(usage=dict(prompt_tokens=p, completion_tokens=c), reasoning_tokens=50))
                records[slot] = (call, result)
        blinds[cid] = dict(case=cid, mapping=mapping, pairs=pairs, groups=[list(pairs)])
        for judge in ('jev', 'astra', 'opus'):
            slot = f'j.{cid}.c00.{judge}'
            quality = {tid: dict(naturalidade=75 if tid.endswith(('0', '2')) else 100,
                clareza=80, adequacao=80, correcao=100, critico=True, justificativa='artificial') for tid in mapping}
            detection = {tid: 80 if tid.endswith(('0', '2')) else 60 for tid in mapping}
            judgment = dict(deteccao=detection, qualidade=quality, preferencia={p: 'B' for p in pairs})
            result = dict(status='completed', judgment=judgment, validation_issues=[],
                quality_aggregate={tid: dict(total=49) for tid in mapping})
            records[slot] = (dict(slot=slot, phase='judge', case=cid, chunk=0, judge=judge), result)
    return config, records, blinds


class AgregacaoArtificial(unittest.TestCase):
    def test_matriz_parcial_e_comandos_nao_sao_prosa_mas_continuam_no_principal(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        records['g.caso-01.r00.skill'][1]['text'] = '<tool_call>{"cmd":"NUNCA EXECUTAR"}</tool_call>'
        records['g.caso-02.r01.skill'][1]['text'] = '<tool_call>{"cmd":"NUNCA EXECUTAR"}</tool_call>'
        result = subject.aggregate(config, records, blinds)
        self.assertEqual(result['cobertura']['respostas_api_validadas']['observado'], 8)
        self.assertEqual(result['cobertura']['textos_redigidos']['observado'], 6)
        self.assertEqual(result['cobertura']['respostas_somente_comandos']['observado'], 2)
        self.assertEqual(len(result['erros']['falhas_de_entrega']), 2)
        self.assertEqual(result['tokens']['total']['pares'], 4)
        self.assertEqual(result['percepcao']['pool_julgamentos']['humanizacao']['pares'], 12)
        self.assertEqual(result['percepcao']['principal_configuracoes_peso_igual']['humanizacao']['skill']['media'], 40)
        self.assertEqual(result['cobertura']['pedidos_com_resposta_api_validada']['observado'], 2)

    def test_tres_respostas_pares_equivalentes_notas_brutas_e_cobertura(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        result = subject.aggregate(config, records, blinds)
        human = result['percepcao']['principal_configuracoes_peso_igual']['humanizacao']
        self.assertEqual(human['baseline']['media'], 20)
        self.assertEqual(human['skill']['media'], 40)
        self.assertEqual(human['diferenca_media'], 20)
        self.assertEqual(human['variacao_percentual_razao_medias'], 100)
        natural = result['percepcao']['pool_julgamentos']['naturalidade_bruta']
        self.assertEqual(natural['baseline']['media'], 75)
        self.assertEqual(natural['skill']['media'], 100)
        self.assertEqual(result['tokens']['total']['baseline']['soma'], 600)
        self.assertEqual(result['tokens']['total']['skill']['soma'], 740)
        self.assertAlmostEqual(result['tokens']['total']['variacao_percentual_razao_somas'], 100 * (740 / 600 - 1))
        self.assertEqual(result['tokens']['entrada']['baseline']['soma'], 220)
        self.assertEqual(result['tokens']['saida']['baseline']['soma'], 380)
        self.assertAlmostEqual(result['tempo']['geracao_api']['variacao_percentual_razao_somas'], 100 * (52 / 44 - 1))
        self.assertEqual(result['cobertura']['pares_tres_juizes']['observado'], 4)
        self.assertEqual(result['cobertura']['julgamentos_pares']['esperado'], 12)
        self.assertIsNone(result['tempo']['com_consultas_locais'])
        self.assertEqual(len(result['por_configuracao']), 2)
        self.assertEqual(len(result['por_juiz']), 3)


def write_artificial_run(root, modules, completed_routes=1, judge_groups=(0,)):
    """Construção offline, sem transporte, Store.submit, prepare ou inferência."""
    g = modules['generation_eval']
    store = modules['eval_store']
    judges = modules['eval_judges']
    root = Path(root)
    ep = dict(name='Offline | artificial/modelo-20990101', tag='offline',
              model_id='artificial/modelo', provider_name='Offline')
    routes = [dict(model='artificial/modelo', mode=f'controle-{i:02}',
        reasoning=dict(enabled=False), endpoint=ep) for i in range(19)]
    cases = [dict(id=f'artificial-{i:02}', ordinal=i, title='ARTIFICIAL OFFLINE',
                  prompt=f'PEDIDO ARTIFICIAL {i:02}. Nunca dado real.') for i in range(1, 25)]
    config = dict(cases=cases, routes=routes, blind_seed='ARTIFICIAL-OFFLINE', max_tokens=1000,
        judge_max_tokens=1000, jev=dict(model='typesafe/jev-1.13', mode='native', endpoint=ep),
        judges=[dict(name=n, model='artificial/modelo', mode='offline', endpoint=ep,
                     reasoning=dict(enabled=False)) for n in ('astra', 'opus')])
    for name in ('SKILL.md', 'references/catalogo.json', 'references/estilos.json'):
        g.immutable(root / 'frozen/skill' / name, b'ARTIFICIAL OFFLINE')
    prompt_text = '\n\n'.join(f'### {c["ordinal"]:02}. {c["title"]}\n\n```text\n{c["prompt"]}\n```' for c in cases) + '\n'
    g.immutable(root / 'frozen/skill/results/PROMPTS.md', prompt_text.encode())
    for case in cases:
        g.immutable(root / 'frozen/local' / (case['id'] + '.json'), dict(artificial=True))
    g.immutable(root / 'frozen/config.json', config)
    for name in ('generation_eval', 'eval_store', 'eval_judges', 'eval_render'):
        g.immutable(root / 'frozen/runner' / (name + '.py'), Path(modules[name].__file__).read_bytes())
    all_gen = list(g.generation_calls(root, config))
    g.immutable(root / 'frozen/generation-plan.json', [dict(slot=c['slot'], payload_sha256=g.digest(c['payload'])) for c in all_gen])
    all_blinds = [g.blind_case(config, c) for c in cases]
    g.immutable(root / 'frozen/blind-plan.json', all_blinds)
    hashes = {p.relative_to(root).as_posix(): g.digest(p.read_bytes()) for p in (root / 'frozen').rglob('*') if p.is_file()}
    g.immutable(root / 'manifest.json', dict(schema=1, sha256=hashes, synthetic=True,
        expected=dict(generations=912, pairs=456, judge_calls=432, pair_judgments=1368,
                      individual_impression_scores=2736)))
    g.immutable(root / 'execution-mode.json', dict(mode='OFFLINE_FAKE', synthetic=True))
    records = {}
    def save(call, response, elapsed):
        intent = dict(call=call, call_sha256=g.digest(call), execution_mode='OFFLINE_FAKE', started_at='2099-01-01T00:00:00Z')
        raw = dict(call_sha256=g.digest(call), intent_sha256=g.digest(intent),
            received_at='2099-01-01T00:00:02Z', elapsed_seconds=elapsed, http_status=200,
            body_base64=base64.b64encode(g.encoded(response)).decode('ascii'))
        result = store.derive(call, intent, raw)
        if result['status'] != 'completed':
            raise AssertionError('fixture artificial inválida: ' + str(result['validation_issues']))
        for filename, value in [('intent.json', intent), ('raw.json', raw)]:
            g.immutable(root / 'requests' / call['slot'] / filename, value)
        # Ausência proposital de result.json: auditoria deve derivar em memória.
        records[call['slot']] = (call, result)
    first_case = cases[0]
    for call in all_gen:
        if call['case'] != first_case['id'] or call['route'] >= completed_routes:
            continue
        response = dict(id='ARTIFICIAL-NUNCA-REAL', model=call['model'], provider='Offline',
            usage=dict(prompt_tokens=10, completion_tokens=100, cost=0,
                       completion_tokens_details=dict(reasoning_tokens=90)),
            choices=[dict(finish_reason='stop', message=dict(content='TEXTO ARTIFICIAL  \n\u2028\u2029sem ajuste  '))])
        save(call, response, 2 if call['arm'] == 'baseline' else 3)
    calls = []
    for index in judge_groups:
        group_calls, missing = g.judge_calls(config, first_case, all_blinds[0], index, records)
        if missing:
            raise AssertionError('grupo artificial incorreto')
        calls.extend(group_calls)
    for call in calls:
        state = call['judge_state']
        if call['api'] == 'decisions':
            answers = {}
            for qid, question in call['payload']['questions'].items():
                kind = question['type']
                answers[qid] = dict(type=kind)
                if kind == 'noul':
                    arm = records[all_blinds[0]['mapping'][qid]][0]['arm']
                    answers[qid]['noul'] = .8 if arm == 'baseline' else .6
                elif kind == 'score':
                    answers[qid]['score'] = 3
                else:
                    answers[qid]['choice'] = 'no' if qid.endswith('_critico') else 'empate'
            response = dict(answers=answers, id='ARTIFICIAL', model=call['model'], provider='Offline',
                            usage=dict(input_tokens=10, output_tokens=10, cost=0))
        else:
            detection = {tid: 80 if records[all_blinds[0]['mapping'][tid]][0]['arm'] == 'baseline' else 60 for tid in state['textos']}
            quality = {tid: dict(naturalidade=75, clareza=75, adequacao=75, correcao=75,
                                 critico=False, justificativa='ARTIFICIAL') for tid in state['textos']}
            judgment = dict(deteccao=detection, qualidade=quality,
                            preferencia={pid: 'empate' for pid in state['pares']})
            response = dict(id='ARTIFICIAL', model=call['model'], provider='Offline',
                usage=dict(prompt_tokens=10, completion_tokens=100, cost=0),
                choices=[dict(finish_reason='stop', message=dict(content=json.dumps(judgment)))])
        save(call, response, 99999)
    return config


def tree_bytes(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in Path(root).rglob('*') if p.is_file()}


class AuditoriaArtificial(unittest.TestCase):
    def test_relatorio_end_to_end_somente_leitura_e_sintetico_explicito(self):
        subject = load_subject()
        modules = subject.load_modules()
        with tempfile.TemporaryDirectory(prefix='.offline-test-', dir=HERE) as temp:
            root = Path(temp) / 'fonte-artificial'
            write_artificial_run(root, modules)
            before = tree_bytes(root)
            with patch.object(socket, 'socket', side_effect=AssertionError('rede proibida')):
                with self.assertRaises(ValueError):
                    subject.report(root, Path(temp) / 'nao-autorizado')
                summary = subject.report(root, Path(temp) / 'relatorio-artificial', allow_synthetic=True)
            self.assertEqual(before, tree_bytes(root))
            self.assertEqual(summary['execucao']['modo'], 'OFFLINE_FAKE')
            self.assertFalse(summary['execucao']['evidencia_de_escrita_real'])
            self.assertEqual(summary['cobertura']['respostas_api_validadas']['esperado'], 912)
            self.assertEqual(summary['cobertura']['chamadas_juizes_validas']['esperado'], 432)
            self.assertEqual(summary['cobertura']['julgamentos_pares']['observado'], 3)
            self.assertEqual(summary['cobertura']['pares_tres_juizes']['observado'], 1)
            self.assertEqual(summary['tokens']['total']['baseline']['soma'], 110)
            self.assertEqual(summary['tempo']['geracao_api']['baseline']['soma'], 2)
            output = Path(temp) / 'relatorio-artificial'
            self.assertEqual(json.loads((output / 'OBJETIVO.json').read_text()), summary)
            md = (output / 'OBJETIVO.md').read_text()
            self.assertIn('ARTIFICIAL OFFLINE', md)
            self.assertIn('1. **Humanização percebida', md)
            self.assertLess(md.index('3. **Tempo'), md.index('## Modelos'))
            self.assertNotIn('\u2014', md)
            self.assertNotIn('\u2013', md)
            with self.assertRaises(FileExistsError):
                subject.report(root, output, allow_synthetic=True)


class LimitesArtificiais(unittest.TestCase):
    def test_juiz_ausente_nao_vira_zero_nem_peso_extra(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        records.pop('j.caso-02.c00.opus')
        result = subject.aggregate(config, records, blinds)
        self.assertEqual(result['cobertura']['julgamentos_pares']['observado'], 10)
        self.assertEqual(result['cobertura']['pares_tres_juizes']['observado'], 2)
        self.assertEqual(result['percepcao']['principal_configuracoes_peso_igual']['humanizacao']['skill']['media'], 40)
        self.assertEqual(result['por_juiz']['opus']['cobertura']['observado'], 2)
        self.assertEqual(result['tokens']['total']['pares'], 4)

    def test_telemetria_incompleta_preserva_denominadores_separados(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        records['g.caso-01.r00.skill'][1]['telemetry']['usage'].pop('prompt_tokens')
        records['g.caso-02.r01.baseline'][1]['elapsed_seconds'] = None
        result = subject.aggregate(config, records, blinds)
        self.assertEqual(result['tokens']['total']['pares'], 3)
        self.assertEqual(result['tempo']['geracao_api']['pares'], 3)
        self.assertEqual(result['cobertura']['pares_geracao_validos']['observado'], 4)
        self.assertEqual(result['exclusoes']['tokens_incompletos_ou_invalidos'], 1)
        self.assertEqual(result['exclusoes']['tempo_incompleto_ou_invalido'], 1)

    def test_tempo_local_compartilhado_nao_e_repetido_por_modelo(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        result = subject.aggregate(config, records, blinds, local_seconds={'caso-01': 10, 'caso-02': 20})
        self.assertEqual(result['tempo']['com_consultas_locais']['skill']['soma'], 82)
        self.assertEqual(result['tempo']['consultas_locais']['soma_completa'], 30)
        self.assertEqual(sum(r['tempo']['com_consultas_locais']['skill']['soma'] for r in result['por_configuracao']), 82)
        partial = subject.aggregate(config, records, blinds, local_seconds={'caso-01': 10})
        self.assertIsNone(partial['tempo']['com_consultas_locais'])
        self.assertEqual(partial['tempo']['consultas_locais']['segundos_conhecidos'], 10)
        self.assertIsNone(partial['tempo']['consultas_locais']['soma_completa'])

    def test_resposta_invalida_e_intencao_ambigua_nao_viram_par(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        # Retira os juízes do grupo que depende da resposta inválida.
        for name in ('jev', 'astra', 'opus'):
            records.pop(f'j.caso-01.c00.{name}')
        records['g.caso-01.r00.skill'][1]['status'] = 'invalid_response'
        records['g.caso-01.r01.baseline'][1]['status'] = 'ambiguous_intent_without_raw'
        result = subject.aggregate(config, records, blinds)
        self.assertEqual(result['tokens']['total']['pares'], 2)
        self.assertEqual(result['cobertura']['pares_geracao_validos']['observado'], 2)
        self.assertEqual(result['erros']['exclusoes_geracao']['par_com_geracao_invalida_ou_ambigua'], 2)
        self.assertEqual(result['cobertura']['pares_tres_juizes']['observado'], 2)

    def test_matriz_de_quinze_pares_sem_extrapolar_para_456(self):
        subject = load_subject()
        modules = subject.load_modules()
        with tempfile.TemporaryDirectory(prefix='.offline-partial-', dir=HERE) as temp:
            root = Path(temp) / 'artificial'
            write_artificial_run(root, modules, completed_routes=15, judge_groups=(0,))
            summary = subject.report(root, Path(temp) / 'saida', allow_synthetic=True)
            self.assertEqual(summary['cobertura']['respostas_api_validadas']['observado'], 30)
            self.assertEqual(summary['cobertura']['pares_geracao_validos']['observado'], 15)
            self.assertEqual(summary['cobertura']['pares_geracao_validos']['esperado'], 456)
            self.assertEqual(summary['cobertura']['pedidos_com_resposta_api_validada']['observado'], 1)
            self.assertEqual(summary['cobertura']['pedidos_com_resposta_api_validada']['esperado'], 24)
            self.assertEqual(summary['tokens']['total']['pares'], 15)
            self.assertEqual(summary['tempo']['geracao_api']['pares'], 15)
            self.assertEqual(summary['percepcao']['principal_configuracoes_peso_igual']['humanizacao']['pares'], 1)

    def test_manipulacao_de_evidencia_e_cache_rejeitada_sem_escrita(self):
        subject = load_subject()
        modules = subject.load_modules()
        for tamper in ('freeze', 'raw_hash', 'cache', 'mapping'):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory(prefix='.offline-tamper-', dir=HERE) as temp:
                root = Path(temp) / 'artificial'
                write_artificial_run(root, modules)
                request = root / 'requests/g.artificial-01.r00.baseline'
                if tamper == 'freeze':
                    path = root / 'frozen/config.json'
                    path.chmod(0o600)
                    path.write_bytes(path.read_bytes() + b' ')
                elif tamper == 'raw_hash':
                    path = request / 'raw.json'
                    path.chmod(0o600)
                    data = json.loads(path.read_bytes())
                    data['intent_sha256'] = '0' * 64
                    path.write_text(json.dumps(data))
                elif tamper == 'cache':
                    (request / 'result.json').write_text('{"inventado":true}')
                else:
                    path = request / 'intent.json'
                    data = json.loads(path.read_bytes())
                    data['call']['case'] = 'caso-inventado'
                    path.chmod(0o600)
                    path.write_text(json.dumps(data))
                before = tree_bytes(root)
                with self.assertRaises(ValueError):
                    subject.report(root, Path(temp) / 'saida', allow_synthetic=True)
                self.assertEqual(before, tree_bytes(root))
                self.assertFalse((Path(temp) / 'saida').exists())

    def test_recibo_local_exige_hash_e_modo_equivalentes(self):
        subject = load_subject()
        modules = subject.load_modules()
        with tempfile.TemporaryDirectory(prefix='.offline-local-', dir=HERE) as temp:
            root = Path(temp) / 'artificial'
            write_artificial_run(root, modules)
            cid = 'artificial-01'
            receipt = Path(temp) / 'tempo-artificial.json'
            data = dict(schema=1, kind='local_skill_queries_timing', execution_mode='OFFLINE_FAKE',
                synthetic=True, scope='shared_preparation_per_case', cases={cid: dict(elapsed_seconds=10,
                    local_sha256=modules['generation_eval'].digest((root / 'frozen/local' / (cid + '.json')).read_bytes()))})
            receipt.write_text(json.dumps(data))
            result = subject.report(root, Path(temp) / 'saida', allow_synthetic=True, local_receipt=receipt)
            self.assertEqual(result['tempo']['com_consultas_locais']['skill']['soma'], 13)
            data['cases'][cid]['local_sha256'] = '0' * 64
            receipt.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                subject.report(root, Path(temp) / 'invalida', allow_synthetic=True, local_receipt=receipt)

    def test_configuracoes_com_cobertura_desigual_tem_pesos_iguais(self):
        subject = load_subject()
        config, records, blinds = artificial_records()
        for cid, blind in blinds.items():
            blind['groups'] = [['p000'], ['p001']]
            for name in ('jev', 'astra', 'opus'):
                call, result = records[f'j.{cid}.c00.{name}']
                extra_call = dict(call, slot=f'j.{cid}.c01.{name}', chunk=1)
                extra_result = copy.deepcopy(result)
                extra_result['judgment']['deteccao']['t002'] = 20
                extra_result['judgment']['deteccao']['t003'] = 20
                if cid == 'caso-01':
                    records[extra_call['slot']] = (extra_call, extra_result)
        result = subject.aggregate(config, records, blinds)
        primary = result['percepcao']['principal_configuracoes_peso_igual']['humanizacao']
        pool = result['percepcao']['pool_julgamentos']['humanizacao']
        self.assertEqual(primary['baseline']['media'], 50)
        self.assertEqual(primary['skill']['media'], 60)
        self.assertEqual(pool['baseline']['media'], 40)
        self.assertEqual(result['cobertura']['pares_tres_juizes']['observado'], 3)

    def test_preparacao_sem_execucao_nao_produz_zeros_ficticios(self):
        subject = load_subject()
        modules = subject.load_modules()
        with tempfile.TemporaryDirectory(prefix='.offline-empty-', dir=HERE) as temp:
            root = Path(temp) / 'artificial'
            write_artificial_run(root, modules, completed_routes=0, judge_groups=())
            (root / 'execution-mode.json').unlink()
            before = tree_bytes(root)
            result = subject.report(root, Path(temp) / 'saida')
            self.assertEqual(before, tree_bytes(root))
            self.assertEqual(result['execucao']['modo'], 'PREPARED_NOT_EXECUTED')
            self.assertEqual(result['cobertura']['pares_tokens']['observado'], 0)
            self.assertIsNone(result['tokens']['total']['baseline']['soma'])
            self.assertIsNone(result['tempo']['geracao_api']['skill']['media'])
            self.assertIsNone(result['percepcao']['principal_configuracoes_peso_igual']['humanizacao']['baseline']['media'])
            self.assertFalse((root / 'requests').exists())
            self.assertFalse((root / '.runner.lock').exists())

    def test_falha_cli_nao_imprime_conteudo_arbitrario(self):
        import io
        from contextlib import redirect_stderr
        subject = load_subject()
        error = io.StringIO()
        with redirect_stderr(error):
            code = subject.main(['--root', str(HERE / 'MARCADOR_ARTIFICIAL_INEXISTENTE'),
                                 '--output', str(HERE / '.saida-nao-criada')])
        self.assertEqual(code, 2)
        self.assertNotIn('MARCADOR_ARTIFICIAL', error.getvalue())
        self.assertIn('FileNotFoundError', error.getvalue())
        self.assertFalse((HERE / '.saida-nao-criada').exists())

    def test_runner_ativo_nao_e_interrompido_nem_lock_recriado(self):
        import fcntl
        subject = load_subject()
        modules = subject.load_modules()
        with tempfile.TemporaryDirectory(prefix='.offline-lock-', dir=HERE) as temp:
            root = Path(temp) / 'artificial'
            write_artificial_run(root, modules)
            with (root / '.runner.lock').open('wb') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                before = tree_bytes(root)
                with self.assertRaises(RuntimeError):
                    subject.report(root, Path(temp) / 'saida', allow_synthetic=True)
                self.assertEqual(before, tree_bytes(root))
                self.assertFalse((Path(temp) / 'saida').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
