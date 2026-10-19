#!/usr/bin/env python3
"""Agregação local do benchmark. Sem rede, modelos, publicação ou e-mail."""
import math


def number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def compare_pairs(pairs):
    pairs = list(pairs)
    if any(not number(b) or not number(s) for b, s in pairs):
        raise ValueError('valor numérico inválido')
    n = len(pairs)
    b = sum(row[0] for row in pairs) if n else None
    s = sum(row[1] for row in pairs) if n else None
    positive = [100 * (s1 / b1 - 1) for b1, s1 in pairs if b1 > 0]
    ratio = s / b if b is not None and b > 0 else None
    variation = 100 * (ratio - 1) if ratio is not None else None
    return dict(pares=n, baseline=dict(soma=b, media=b / n if n else None),
                skill=dict(soma=s, media=s / n if n else None),
                diferenca_soma=s - b if n else None,
                diferenca_media=(s - b) / n if n else None,
                razao_somas=ratio, variacao_percentual_razao_somas=variation,
                razao_medias=ratio, variacao_percentual_razao_medias=variation,
                pares_baseline_positivo=len(positive),
                media_variacoes_pareadas_percentuais=sum(positive) / len(positive) if positive else None)


import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
DEFAULT_SCRIPTS = Path('/home/hermes/projects/my-skills-humanizador/skills/humanizador-pt-br/results/scripts')
JUDGES = ('jev', 'astra', 'opus')


def load_modules(scripts=DEFAULT_SCRIPTS):
    modules = {}
    for name in ('eval_judges', 'generation_eval', 'eval_store', 'eval_render'):
        path = Path(scripts) / (name + '.py')
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def coverage(observed, expected):
    if not 0 <= observed <= expected:
        raise ValueError('cobertura incompatível')
    return dict(observado=observed, esperado=expected,
                percentual=100 * observed / expected if expected else None)


def perception(rows):
    return dict(humanizacao=compare_pairs([(100 - r['detection_baseline'],
                                           100 - r['detection_skill']) for r in rows]),
                naturalidade_bruta=compare_pairs([(r['naturalidade_baseline'],
                                                    r['naturalidade_skill']) for r in rows]),
                preferencias=dict(Counter(r['preference'] for r in rows)))


def collapse_judges(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['case'], row['route'])].append(row)
    result = []
    for key, group in sorted(groups.items()):
        if {r['judge'] for r in group} != set(JUDGES):
            continue
        if len(group) != len(JUDGES):
            raise ValueError('julgamento duplicado')
        row = dict(case=key[0], route=key[1], preference='nao_agregada')
        for field in ('detection_baseline', 'detection_skill',
                      'naturalidade_baseline', 'naturalidade_skill'):
            row[field] = sum(r[field] for r in group) / len(group)
        result.append(row)
    return result


def balanced_perception(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['route']].append(row)
    collapsed = []
    for route, group in sorted(groups.items()):
        row = dict(route=route, preference='nao_agregada')
        for field in ('detection_baseline', 'detection_skill',
                      'naturalidade_baseline', 'naturalidade_skill'):
            row[field] = sum(r[field] for r in group) / len(group)
        collapsed.append(row)
    result = perception(collapsed)
    result['configuracoes_observadas'] = len(collapsed)
    result['pares_tres_juizes'] = len(rows)
    result['unidade'] = 'média da configuração; casos e três juízes com pesos iguais internamente'
    return result


def generation_metrics(pairs, local_seconds=None, allocations=None):
    token_pairs, elapsed_pairs = [], []
    excluded = Counter()
    for pair in pairs:
        b, s = pair['baseline'], pair['skill']
        usages = [r.get('telemetry', {}).get('usage', {}) for r in (b, s)]
        if all(type(u.get(f)) is int and u[f] >= 0 for u in usages
               for f in ('prompt_tokens', 'completion_tokens')):
            token_pairs.append((usages[0], usages[1]))
        else:
            excluded['tokens_incompletos_ou_invalidos'] += 1
        if all(number(r.get('elapsed_seconds')) for r in (b, s)):
            elapsed_pairs.append(pair)
        else:
            excluded['tempo_incompleto_ou_invalido'] += 1
    tokens = {}
    for key, fields in [('entrada', ('prompt_tokens',)), ('saida', ('completion_tokens',)),
                        ('total', ('prompt_tokens', 'completion_tokens'))]:
        tokens[key] = compare_pairs([(sum(b[f] for f in fields), sum(s[f] for f in fields))
                                    for b, s in token_pairs])
    api = compare_pairs([(p['baseline']['elapsed_seconds'], p['skill']['elapsed_seconds'])
                         for p in elapsed_pairs])
    local_seconds = local_seconds or {}
    relevant = {p['case'] for p in elapsed_pairs}
    known = relevant & set(local_seconds)
    local_known = sum(local_seconds[c] for c in known)
    extended = None
    if relevant and relevant <= set(local_seconds):
        allocation = allocations or Counter(p['case'] for p in elapsed_pairs)
        extended = compare_pairs([(p['baseline']['elapsed_seconds'], p['skill']['elapsed_seconds'] +
                                   local_seconds[p['case']] / allocation[p['case']]) for p in elapsed_pairs])
    local = dict(casos_relevantes=len(relevant), casos_com_medicao=len(known),
                 segundos_conhecidos=local_known, soma_completa=local_known if relevant and relevant <= known else None,
                 criterio='consulta compartilhada de preparação por caso, rateada entre pares de tempo válidos; não repetida por configuração')
    return dict(tokens=tokens, tempo=dict(geracao_api=api, consultas_locais=local,
                                         com_consultas_locais=extended), exclusoes=dict(excluded))


def aggregate(config, records, blinds, modules=None, local_seconds=None):
    modules = modules or load_modules()
    rows = modules['eval_render'].metric_rows(config, records, blinds)
    for row in rows:
        result = records[f'j.{row["case"]}.c{next(i for i, group in enumerate(blinds[row["case"]]["groups"]) if row["pair_id"] in group):02}.{row["judge"]}'][1]
        for arm in ('baseline', 'skill'):
            row['humanizacao_' + arm] = 100 - row['detection_' + arm]
            row['naturalidade_' + arm] = result['judgment']['qualidade'][row[arm + '_id']]['naturalidade']
    complete = collapse_judges(rows)
    complete_keys = {(r['case'], r['route']) for r in complete}
    pair_count = len(config['cases']) * len(config['routes'])
    gen_pairs, exclusions = [], Counter()
    generation, judge_records = [], []
    for call, result in records.values():
        (generation if call['phase'] == 'generation' else judge_records).append(result)
    for case in config['cases']:
        cid = case['id']
        for ri in range(len(config['routes'])):
            entries = [records.get(f'g.{cid}.r{ri:02}.{arm}') for arm in ('baseline', 'skill')]
            if any(e is None for e in entries):
                exclusions['par_com_geracao_ausente'] += 1
                continue
            if any(e[1]['status'] != 'completed' for e in entries):
                exclusions['par_com_geracao_invalida_ou_ambigua'] += 1
                continue
            if any(e[0]['case'] != cid or e[0]['route'] != ri or e[0]['arm'] != arm
                   for e, arm in zip(entries, ('baseline', 'skill'))):
                raise ValueError('par de geração não equivalente')
            gen_pairs.append(dict(case=cid, route=ri, baseline=entries[0][1], skill=entries[1][1]))
    allocations = Counter(p['case'] for p in gen_pairs if all(number(p[a].get('elapsed_seconds'))
                           for a in ('baseline', 'skill')))
    overall_gen = generation_metrics(gen_pairs, local_seconds, allocations)
    expected_judge_calls = sum(len(b['groups']) for b in blinds.values()) * len(JUDGES)
    judge_chunk_missing = []
    for cid, blind in blinds.items():
        for ci, group in enumerate(blind['groups']):
            candidates = {blind['mapping'][tid] for pid in group for tid in blind['pairs'][pid].values()}
            blocked = [s for s in sorted(candidates) if s not in records or records[s][1]['status'] != 'completed']
            if blocked:
                valid_pairs = sum(all(blind['mapping'][tid] in records and
                    records[blind['mapping'][tid]][1]['status'] == 'completed'
                    for tid in blind['pairs'][pid].values()) for pid in group)
                judge_chunk_missing.append(dict(caso=cid, grupo=ci, geracoes_bloqueadoras=blocked,
                    pares_validos_sem_julgamento_no_grupo=valid_pairs))
    by_config = []
    for ri, route in enumerate(config['routes']):
        group = [r for r in rows if r['route'] == ri]
        fully = [r for r in complete if r['route'] == ri]
        generators = [p for p in gen_pairs if p['route'] == ri]
        metrics = generation_metrics(generators, local_seconds, allocations)
        by_config.append(dict(indice=ri, modelo=route['model'], modo=route['mode'],
            provedor=route['endpoint']['tag'],
            cobertura=dict(pares_validos=coverage(len(generators), len(config['cases'])),
                pares_tres_juizes=coverage(len(fully), len(config['cases'])),
                julgamentos_pares=coverage(len(group), len(config['cases']) * len(JUDGES)),
                tokens=coverage(metrics['tokens']['total']['pares'], len(config['cases'])),
                tempo=coverage(metrics['tempo']['geracao_api']['pares'], len(config['cases']))),
            percepcao=dict(pares_tres_juizes=perception(fully), pool_julgamentos=perception(group)),
            por_juiz={name: perception([r for r in group if r['judge'] == name]) for name in JUDGES},
            **metrics))
    by_model = []
    for model in sorted({r['model'] for r in config['routes']}):
        routes = {i for i, r in enumerate(config['routes']) if r['model'] == model}
        metrics = generation_metrics([p for p in gen_pairs if p['route'] in routes], local_seconds, allocations)
        by_model.append(dict(modelo=model, configuracoes=len(routes),
            percepcao=balanced_perception([r for r in complete if r['route'] in routes]), **metrics))
    issues = []
    for slot, (call, result) in sorted(records.items()):
        if result['status'] != 'completed' or result.get('validation_issues'):
            issues.append(dict(slot=slot, fase=call['phase'], estado=result['status'],
                categorias=result.get('validation_issues', [])))
    gen_valid = sum(r['status'] == 'completed' for r in generation)
    judged_valid = sum(r['status'] == 'completed' for r in judge_records)
    delivery_failures = []
    for slot, (call, result) in sorted(records.items()):
        if call['phase'] != 'generation' or result['status'] != 'completed':
            continue
        text = result.get('text')
        if isinstance(text, str) and re.fullmatch(r'\s*(?:<tool_call>[\s\S]*?</tool_call>\s*)+', text):
            delivery_failures.append(dict(slot=slot, caso=call['case'], configuracao=call['route'],
                braco=call['arm'], categoria='comando_em_vez_de_texto',
                incluido_nas_metricas_principais=True, comando_executado=False))
    valid_cases = {c['case'] for c, r in records.values() if c['phase'] == 'generation' and r['status'] == 'completed'}
    return dict(schema=1,
        percepcao=dict(principal_configuracoes_peso_igual=balanced_perception(complete),
                      pares_tres_juizes=perception(complete), pool_julgamentos=perception(rows)),
        por_juiz={name: dict(todos_pares_validos=perception([r for r in rows if r['judge'] == name]),
            mesmos_pares_tres_juizes=perception([r for r in rows if r['judge'] == name and
                                              (r['case'], r['route']) in complete_keys]),
            cobertura=coverage(sum(r['judge'] == name for r in rows), pair_count)) for name in JUDGES},
        por_configuracao=by_config, por_modelo=by_model, **overall_gen,
        cobertura=dict(geracoes_submetidas=coverage(len(generation), pair_count * 2),
            respostas_api_validadas=coverage(gen_valid, pair_count * 2),
            textos_redigidos=coverage(gen_valid - len(delivery_failures), pair_count * 2),
            respostas_somente_comandos=coverage(len(delivery_failures), pair_count * 2),
            pedidos_com_resposta_api_validada=coverage(len(valid_cases), len(config['cases'])),
            pedidos_com_julgamento=coverage(len({r['case'] for r in rows}), len(config['cases'])),
            pares_geracao_validos=coverage(len(gen_pairs), pair_count),
            chamadas_juizes_submetidas=coverage(len(judge_records), expected_judge_calls),
            chamadas_juizes_validas=coverage(judged_valid, expected_judge_calls),
            julgamentos_pares=coverage(len(rows), pair_count * len(JUDGES)),
            escores_individuais=coverage(len(rows) * 2, pair_count * len(JUDGES) * 2),
            pares_com_algum_juiz=coverage(len({(r['case'], r['route']) for r in rows}), pair_count),
            pares_tres_juizes=coverage(len(complete), pair_count),
            configuracoes_com_tres_juizes=coverage(len({r['route'] for r in complete}), len(config['routes'])),
            pares_tokens=coverage(overall_gen['tokens']['total']['pares'], pair_count),
            pares_tempo=coverage(overall_gen['tempo']['geracao_api']['pares'], pair_count)),
        erros=dict(estados=dict(Counter(r['status'] for _, r in records.values())),
            registros=issues, falhas_de_entrega=delivery_failures, exclusoes_geracao=dict(exclusions),
            grupos_bloqueados=judge_chunk_missing),
        julgamentos_pareados=rows,
        limites=[
            'H = 100 menos detecção. Índice descritivo não calibrado, não probabilidade de autoria humana.',
            'Completed valida a resposta API, não a entrega editorial. Saídas compostas somente por tool_call são comandos, não textos redigidos; ficam nas métricas principais sem execução e sem exclusão silenciosa.',
            'Humanização percebida não comprova autoria nem qualidade. Naturalidade é a dimensão bruta 0 a 100.',
            'Principal: mesmo par avaliado pelos três juízes, média dos juízes e casos em cada configuração; média com peso igual entre configurações observadas.',
            'Configurações e casos ausentes não valem zero; cobertura parcial não permite concluir sobre toda a matriz.',
            'Pool: peso igual por caso, configuração e juiz observado. Juízes repetidos sobre os mesmos textos não são observações independentes.',
            'Tokens = prompt_tokens + completion_tokens. Reasoning não é somado, nem subtraído; cache permanece no contador nativo de entrada.',
            'Tokens e tempo usam pares completos equivalentes por caso e configuração, não exigem julgamento. Percentual principal é a razão das somas menos 1, vezes 100.',
            'Razão das médias equivale à razão das somas no mesmo conjunto. Média dos percentuais pareados é auxiliar e usa somente baseline positivo.',
            'Tempo API é elapsed_seconds das gerações, inclui eventual fila da requisição, exclui juízes, retries e pausas entre requisições. Não é tempo humano de redação.',
            'Consultas locais compartilhadas na preparação não foram cronometradas pelo runner original; indisponibilidade não equivale a zero. Medição posterior não substitui a original.',
            'Sem inferência estatística, causalidade geral ou calibração humana; uma geração por braço e configuração. Avaliação humana não medida.'
        ])


import argparse
import fcntl
import json
import re
from contextlib import contextmanager
from unittest.mock import patch

BASE = Path(__file__).resolve().parent
EXPECTED = dict(generations=912, pairs=456, judge_calls=432,
                pair_judgments=1368, individual_impression_scores=2736)


@contextmanager
def existing_shared_lock(root):
    path = root / '.runner.lock'
    if not path.exists():
        yield
        return
    with path.open('rb') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('execução concorrente ativa; aguarde sem interferir') from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def fingerprint(root, g):
    paths = [root / 'manifest.json']
    if (root / 'execution-mode.json').exists():
        paths.append(root / 'execution-mode.json')
    for name in ('frozen', 'requests', 'judge-inputs'):
        folder = root / name
        if folder.is_symlink():
            raise ValueError('link simbólico na fonte')
        if folder.exists():
            for path in sorted(folder.rglob('*')):
                if path.is_symlink() or not path.resolve().is_relative_to(root):
                    raise ValueError('caminho fora da fonte')
                if path.is_file():
                    paths.append(path)
    return {p.relative_to(root).as_posix(): g.digest(p.read_bytes()) for p in paths}


def readonly_audited(root, config, mode, modules):
    g, store, renderer = (modules[n] for n in ('generation_eval', 'eval_store', 'eval_render'))
    class ReadOnlyStore(store.Store):
        def __init__(self, root, mode):
            self.root, self.mode = Path(root), mode
            self.requests = self.root / 'requests'

        def recover(self, call):
            path = self.paths(call['slot'])
            intent = g.read_json(path / 'intent.json')
            if intent['call'] != call or intent['call_sha256'] != g.digest(call):
                raise ValueError('intent payload mismatch')
            if intent['execution_mode'] != self.mode:
                raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
            if not (path / 'raw.json').exists():
                return dict(slot=call['slot'], status='ambiguous_intent_without_raw', telemetry={})
            raw = g.read_json(path / 'raw.json')
            if raw['call_sha256'] != g.digest(call) or raw['intent_sha256'] != g.digest(intent):
                raise ValueError('raw/intent hash mismatch')
            result = store.derive(call, intent, raw)
            cached = path / 'result.json'
            if cached.exists() and g.read_json(cached) != result:
                raise ValueError('cached result differs from immutable raw')
            return result

        def audit(self):
            return super().audit() if self.requests.exists() else {}
    # Reusa Store.audit e eval_render.audited. Só recover deixa de criar cache.
    with patch.object(renderer, 'Store', ReadOnlyStore):
        return renderer.audited(root, config, mode)


def local_timings(root, config, mode, modules, receipt=None):
    g = modules['generation_eval']
    values, sources = {}, []
    for case in config['cases']:
        path = root / 'frozen/local' / (case['id'] + '.json')
        obj = g.read_json(path)
        commands = ('catalog', 'styles', 'structure')
        if all(isinstance(obj.get(c), dict) and number(obj[c].get('elapsed_seconds')) for c in commands):
            values[case['id']] = sum(obj[c]['elapsed_seconds'] for c in commands)
            sources.append(dict(caso=case['id'], fonte='frozen/local', sha256=g.digest(path.read_bytes())))
    receipt_sha256 = None
    if receipt is not None:
        receipt_bytes = Path(receipt).read_bytes()
        data = json.loads(receipt_bytes)
        if (data.get('schema') != 1 or data.get('kind') != 'local_skill_queries_timing'
            or data.get('execution_mode') != mode or data.get('scope') != 'shared_preparation_per_case'
            or type(data.get('synthetic')) is not bool or data['synthetic'] != (mode == 'OFFLINE_FAKE')
            or not isinstance(data.get('cases'), dict)):
            raise ValueError('recibo de tempo local incompatível')
        known_ids = {c['id'] for c in config['cases']}
        if not set(data['cases']) <= known_ids:
            raise ValueError('caso desconhecido no recibo')
        for cid, row in data['cases'].items():
            path = root / 'frozen/local' / (cid + '.json')
            if not number(row.get('elapsed_seconds')) or row.get('local_sha256') != g.digest(path.read_bytes()):
                raise ValueError('tempo local ou hash inválido')
            if cid in values and values[cid] != row['elapsed_seconds']:
                raise ValueError('medições locais conflitantes')
            values[cid] = row['elapsed_seconds']
            sources.append(dict(caso=cid, fonte='recibo_explicito', sha256=row['local_sha256']))
        receipt_sha256 = g.digest(receipt_bytes)
    return values, dict(fontes=sources, recibo_sha256=receipt_sha256,
                        aviso='Somente cronometração original; jamais reconstruir tempo com uma nova consulta.')


def shown(value, suffix=''):
    return 'indisponível' if value is None else f'{value:.2f}{suffix}'


def mdcell(value):
    return str(value).replace('|', '&#124;').replace('\n', '<br>').replace('\r', '')


def write_markdown(summary):
    p = summary['percepcao']['principal_configuracoes_peso_igual']
    h = p['humanizacao']
    t = summary['tokens']['total']
    time = summary['tempo']['geracao_api']
    mode = summary['execucao']['modo']
    label = 'ARTIFICIAL OFFLINE: teste, nunca resultado real' if mode == 'OFFLINE_FAKE' else mode
    text = ['# Resultado objetivo', '', f'Execução: **{label}**.', '',
        f'1. **Humanização percebida:** índice H médio baseline {shown(h["baseline"]["media"])}/100 e skill {shown(h["skill"]["media"])}/100; diferença {shown(h["diferenca_media"], " pontos")}; variação relativa {shown(h["variacao_percentual_razao_medias"], "%")}. Não calibrado, não probabilidade de autoria. {p["pares_tres_juizes"]} pares com três juízes em {p["configuracoes_observadas"]} configurações observadas.',
        f'2. **Tokens:** variação {shown(t["variacao_percentual_razao_somas"], "%")} pela razão das somas. Baseline/skill {shown(t["baseline"]["soma"])}/{shown(t["skill"]["soma"])} tokens; médias {shown(t["baseline"]["media"])}/{shown(t["skill"]["media"])} por geração; n={t["pares"]} pares completos. Entrada mais saída, sem somar reasoning.',
        f'3. **Tempo de redação via API:** variação {shown(time["variacao_percentual_razao_somas"], "%")}; somas baseline/skill {shown(time["baseline"]["soma"])}/{shown(time["skill"]["soma"])} s; médias {shown(time["baseline"]["media"])}/{shown(time["skill"]["media"])} s; n={time["pares"]} pares completos. Sem juízes, retries ou pausas.', '']
    failures = summary['erros']['falhas_de_entrega']
    if failures:
        slots = ', '.join(mdcell(r['slot']) for r in failures)
        text[4:4] = [f'**Nota essencial:** {len(failures)} respostas retornam somente comandos tool_call, sem entregar prosa: {slots}. Nenhum comando foi executado. As falhas permanecem nas métricas principais, inclusive H, tokens e tempo. Há {summary["cobertura"]["respostas_api_validadas"]["observado"]} respostas API validadas, mas {summary["cobertura"]["textos_redigidos"]["observado"]} textos redigidos.', '']
    local = summary['tempo']['consultas_locais']
    extended = summary['tempo']['com_consultas_locais']
    text.append(f'Consultas locais da skill: {local["casos_com_medicao"]}/{local["casos_relevantes"]} casos relevantes medidos; {shown(local["segundos_conhecidos"])} s conhecidos. Tempo incluindo preparo local compartilhado: ' +
        (shown(extended['variacao_percentual_razao_somas'], '%') + ' de variação, com rateio por caso.' if extended else 'indisponível, não tratado como zero.'))
    natural = p['naturalidade_bruta']
    pool = summary['percepcao']['pool_julgamentos']['humanizacao']
    text += ['', f'Naturalidade bruta média baseline/skill: {shown(natural["baseline"]["media"])}/{shown(natural["skill"]["media"])}, escala 0 a 100. Pool descritivo de julgamentos: H {shown(pool["baseline"]["media"])}/{shown(pool["skill"]["media"])}; n={pool["pares"]}.', '',
        '## Modelos', '', '| Modelo | Configurações | H baseline/skill | Diferença H em pontos | Tokens % | Tempo API % | Pares tokens/tempo |',
        '|---|---:|---|---:|---:|---:|---|']
    for row in summary['por_modelo']:
        m = row['percepcao']['humanizacao']
        text.append('| ' + ' | '.join(map(mdcell, [row['modelo'], row['configuracoes'],
            shown(m['baseline']['media']) + '/' + shown(m['skill']['media']), shown(m['diferenca_media']),
            shown(row['tokens']['total']['variacao_percentual_razao_somas']),
            shown(row['tempo']['geracao_api']['variacao_percentual_razao_somas']),
            f'{row["tokens"]["total"]["pares"]}/{row["tempo"]["geracao_api"]["pares"]}'])) + ' |')
    text += ['', '## Configurações', '', '| Modelo / modo / provedor | H baseline/skill | Diferença em pontos | Pares 3 juízes | Tokens % | Tempo % | Pares válidos |', '|---|---|---:|---:|---:|---:|---:|']
    for row in summary['por_configuracao']:
        m = row['percepcao']['pares_tres_juizes']['humanizacao']
        cov = row['cobertura']
        text.append('| ' + ' | '.join(map(mdcell, [f'{row["modelo"]} / {row["modo"]} / {row["provedor"]}',
            shown(m['baseline']['media']) + '/' + shown(m['skill']['media']), shown(m['diferenca_media']),
            f'{cov["pares_tres_juizes"]["observado"]}/{cov["pares_tres_juizes"]["esperado"]}',
            shown(row['tokens']['total']['variacao_percentual_razao_somas']),
            shown(row['tempo']['geracao_api']['variacao_percentual_razao_somas']),
            f'{cov["pares_validos"]["observado"]}/{cov["pares_validos"]["esperado"]}'])) + ' |')
    text += ['', '## Juízes', '', '| Juiz | H baseline/skill | Diferença em pontos | Naturalidade bruta baseline/skill | Julgamentos válidos |', '|---|---|---:|---|---:|']
    for name, row in summary['por_juiz'].items():
        m = row['todos_pares_validos']['humanizacao']
        n = row['todos_pares_validos']['naturalidade_bruta']
        cov = row['cobertura']
        text.append(f'| {name} | {shown(m["baseline"]["media"])}/{shown(m["skill"]["media"])} | {shown(m["diferenca_media"])} | {shown(n["baseline"]["media"])}/{shown(n["skill"]["media"])} | {cov["observado"]}/{cov["esperado"]} |')
    text += ['', '## Cobertura e decomposição', '']
    for key, row in summary['cobertura'].items():
        text.append(f'- {key}: {row["observado"]}/{row["esperado"]} ({shown(row["percentual"], "%")}).')
    for key in ('entrada', 'saida'):
        row = summary['tokens'][key]
        text.append(f'- Tokens de {key}, somas baseline/skill: {shown(row["baseline"]["soma"])}/{shown(row["skill"]["soma"])}; médias {shown(row["baseline"]["media"])}/{shown(row["skill"]["media"])}; variação {shown(row["variacao_percentual_razao_somas"], "%")}.')
    text += ['', '## Erros e limites', '',
        f'Registros com erro ou alerta: {len(summary["erros"]["registros"])}. Grupos bloqueados por candidatos ausentes ou inválidos: {len(summary["erros"]["grupos_bloqueados"])}. Detalhes e denominadores completos em OBJETIVO.json.', '']
    text.extend('- ' + note for note in summary['limites'])
    text += ['', 'Textos e respostas brutas permanecem intactos na fonte. Nenhuma normalização, nova consulta de modelo ou publicação.', '']
    return '\n'.join(text)


def report(root, output, allow_synthetic=False, scripts=DEFAULT_SCRIPTS, local_receipt=None):
    root, output = Path(root).resolve(), Path(output).resolve()
    if not output.is_relative_to(BASE) or output == BASE or output.is_relative_to(root):
        raise ValueError('saída deve ser subpasta nova de analysis, fora da evidência')
    if output.exists():
        raise FileExistsError('saída existente; não substituir artefatos concorrentes')
    modules = load_modules(scripts)
    g = modules['generation_eval']
    with existing_shared_lock(root):
        before = fingerprint(root, g)
        manifest = g.read_json(root / 'manifest.json')
        for name in manifest['sha256']:
            path = root / name
            if Path(name).is_absolute() or not path.resolve().is_relative_to(root):
                raise ValueError('manifesto com caminho fora da fonte')
        config = g.load_frozen(root)
        marker = root / 'execution-mode.json'
        state = g.read_json(marker) if marker.exists() else dict(mode='PREPARED_NOT_EXECUTED', synthetic=False)
        mode = state['mode']
        if mode not in ('LIVE_API', 'OFFLINE_FAKE', 'PREPARED_NOT_EXECUTED'):
            raise ValueError('modo de execução desconhecido')
        if mode == 'OFFLINE_FAKE' and not allow_synthetic:
            raise ValueError('dados artificiais exigem autorização offline explícita')
        if mode == 'LIVE_API' and (state.get('synthetic') is not False or manifest.get('synthetic') is True):
            raise ValueError('dados reais e artificiais incompatíveis')
        if mode == 'OFFLINE_FAKE' and state.get('synthetic') is not True:
            raise ValueError('execução offline deve ser marcada artificial')
        if len(config['cases']) != 24 or len(config['routes']) != 19 or manifest['expected'] != EXPECTED:
            raise ValueError('matriz diferente de 24 pedidos e 19 configurações')
        if len({c['id'] for c in config['cases']}) != 24 or len({(r['model'], r['mode']) for r in config['routes']}) != 19:
            raise ValueError('caso ou configuração duplicado')
        if {j['name'] for j in config['judges']} != {'astra', 'opus'}:
            raise ValueError('juízes incompatíveis')
        frozen_blinds = g.read_json(root / 'frozen/blind-plan.json')
        if frozen_blinds != [g.blind_case(config, c) for c in config['cases']]:
            raise ValueError('mapeamento anônimo diferente do plano reproduzido')
        records, blinds = readonly_audited(root, config, mode, modules)
        seconds, local_provenance = local_timings(root, config, mode, modules, local_receipt)
        summary = aggregate(config, records, blinds, modules, seconds)
        summary['execucao'] = dict(modo=mode, artificial=mode == 'OFFLINE_FAKE',
            evidencia_de_escrita_real=mode == 'LIVE_API', fonte=str(root), expected=EXPECTED)
        summary['auditoria'] = dict(rotinas=['generation_eval.load_frozen', 'eval_store.Store.audit',
            'eval_store.derive', 'eval_judges.validate_judge', 'eval_render.audited', 'eval_render.metric_rows'],
            modo='somente leitura; cache ausente derivado em memória',
            manifesto_sha256=g.digest((root / 'manifest.json').read_bytes()),
            fontes_sha256=before, consultas_locais=local_provenance)
        if fingerprint(root, g) != before:
            raise RuntimeError('fonte alterada durante leitura; resultado não emitido')
    # Os dois conteúdos são calculados antes de reservar a saída.
    json_bytes = json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False).encode('utf-8') + b'\n'
    md_bytes = write_markdown(summary).encode('utf-8')
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    g.immutable(output / 'OBJETIVO.json', json_bytes)
    g.immutable(output / 'OBJETIVO.md', md_bytes)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path, help='raiz real fornecida pelo controlador')
    parser.add_argument('--output', required=True, type=Path, help='subpasta nova de analysis')
    parser.add_argument('--scripts', type=Path, default=DEFAULT_SCRIPTS)
    parser.add_argument('--allow-synthetic', action='store_true', help='exclusivamente testes artificiais offline')
    parser.add_argument('--consultas-locais', type=Path, help='recibo original opcional com hashes das consultas')
    args = parser.parse_args(argv)
    try:
        summary = report(args.root, args.output, args.allow_synthetic, args.scripts, args.consultas_locais)
    except Exception as exc:
        # Não imprime mensagem arbitrária: respostas podem conter credenciais refletidas.
        print(f'Falha local ({type(exc).__name__}). Nenhum modelo foi chamado. Fonte não modificada.', file=sys.stderr)
        return 2
    print(json.dumps(dict(modo=summary['execucao']['modo'],
        julgamentos=summary['cobertura']['julgamentos_pares']['observado'],
        relatorios=[str(args.output / name) for name in ('OBJETIVO.json', 'OBJETIVO.md')]), ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
