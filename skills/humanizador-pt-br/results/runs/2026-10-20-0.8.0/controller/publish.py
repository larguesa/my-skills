#!/usr/bin/env python3
"""Projeção pública local 0.8.0. Sem API, Git, e-mail ou alteração da fonte.

Reutiliza o encadeamento de publish.py/sanitize-publication.py da 0.7.0,
com sanitização antes da cópia e auditoria somente leitura do agregador.
--check valida em diretório temporário; --write exige autorização explícita.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
DEST = Path('/home/hermes/projects/my-skills-humanizador/skills/humanizador-pt-br/results/runs/2026-10-20-0.8.0')
AGENTS_SHA256 = 'f6e47e43365fb6b09e45c6ab763a28c37c4473aafa8dd1891828986bc164b56c'
JUDGES = ('jev', 'astra', 'opus')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, relative):
    rel = Path(relative)
    require(not rel.is_absolute() and '..' not in rel.parts and rel.parts, 'caminho fora da projeção')
    require(not any(p in ('private', '.git', '__pycache__') for p in rel.parts), 'pasta não publicável')
    path = root / rel
    require(path.resolve().is_relative_to(root.resolve()), 'escape de caminho')
    require(not any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root)), 'link simbólico')
    return path


def inventory(root, ignore_lock=False):
    return {p.relative_to(root).as_posix(): sha(safe_path(root, p.relative_to(root)).read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file() and not (ignore_lock and p.name == '.runner.lock')}


def software_passed(receipt):
    suites = receipt.get('suites', [])
    required = {'test_humanizar.py', 'test_generation_eval.py', 'test_objetivo.py', 'test_schedule_run.py'}
    return (bool(suites) and required <= {s.get('suite') for s in suites}
            and all(type(s.get('exit_code')) is int and s['exit_code'] == 0
                    and type(s.get('passed')) is int and s['passed'] > 0 for s in suites))


def verdict(rows, planned_pairs, valid_pairs, software):
    groups = defaultdict(dict)
    for row in rows:
        key = (row['case'], row['route'])
        require(row['judge'] in JUDGES and row['judge'] not in groups[key], 'juiz duplicado/desconhecido')
        groups[key][row['judge']] = row
    complete = [list(group.values()) for group in groups.values() if set(group) == set(JUDGES)]
    mean = lambda values: sum(values) / len(values) if values else None
    h = {arm: mean([mean([100 - r['detection_' + arm] for r in group]) for group in complete])
         for arm in ('baseline', 'skill')}
    delta = h['skill'] - h['baseline'] if complete else None
    judge_deltas = {j: mean([r['detection_baseline'] - r['detection_skill'] for r in rows if r['judge'] == j]) for j in JUDGES}
    votes = {a: sum(r['preference'] == a for r in rows) for a in ('baseline', 'skill', 'empate')}
    require(sum(votes.values()) == len(rows), 'preferência desconhecida')
    critical = {a: sum(r[a + '_critical'] is True for r in rows) for a in ('baseline', 'skill')}
    full = valid_pairs == planned_pairs == len(complete) and len(rows) == planned_pairs * len(JUDGES)
    status = 'inconclusivo'
    reason = 'Pré-requisitos incompletos: software ou todos os pares válidos e julgados pelos três juízes.'
    if full and software:
        if delta <= 0 or votes['baseline'] > votes['skill'] or critical['skill'] > critical['baseline']:
            status, reason = 'rejeitada', 'ΔH não positivo, preferência inferior ou mais falhas críticas na candidata.'
        elif delta >= 5 and sum(v is not None and v > 0 for v in judge_deltas.values()) >= 2:
            status, reason = 'aceita', 'Todos os critérios de aceitação do AGENTS congelado foram atendidos.'
        else:
            reason = 'Plano completo, mas os limiares de aceitação não foram atingidos.'
    return dict(status=status, motivo=reason, h_ciclo=h, delta_h=delta, delta_h_por_juiz=judge_deltas,
                preferencias=votes, falhas_criticas=critical, denominador_votos=len(rows),
                denominador_falhas_por_braco=len(rows), pares_tres_juizes=len(complete),
                pares_planejados=planned_pairs, plano_completo=full, software_passando=software,
                referencia='sem skill', agents_sha256=AGENTS_SHA256)


def failure_inventory(config, records, blinds):
    planned = {f'g.{case["id"]}.r{ri:02}.{arm}' for case in config['cases']
               for ri in range(len(config['routes'])) for arm in ('baseline', 'skill')}
    planned.update(f'j.{cid}.c{ci:02}.{judge}' for cid, blind in blinds.items()
                   for ci in range(len(blind['groups'])) for judge in JUDGES)
    require(set(records) <= planned, 'chamada fora do plano')
    return dict(chamadas_planejadas=len(planned), chamadas_observadas=len(records),
                chamadas_ausentes=sorted(planned - set(records)),
                registros_nao_completos=[dict(slot=slot, fase=call['phase'], status=result['status'],
                    categorias=result.get('validation_issues', []),
                    texto_preservado=isinstance(result.get('text'), str),
                    evidencia='evidence/requests/' + slot + '/')
                    for slot,(call,result) in sorted(records.items()) if result['status'] != 'completed'])


def durations(records):
    starts, ends, elapsed = [], [], []
    for _, result in records.values():
        for field, output in [('started_at', starts), ('finished_at', ends)]:
            if result.get(field):
                dt = datetime.fromisoformat(result[field].replace('Z', '+00:00'))
                require(dt.tzinfo is not None, 'timestamp sem fuso')
                output.append(dt)
        value = result.get('elapsed_seconds')
        if type(value) in (int, float) and math.isfinite(value) and value >= 0:
            elapsed.append(value)
    return dict(inicio_observado=min(starts).isoformat() if starts else None,
                fim_observado=max(ends).isoformat() if ends else None,
                janela_observada_segundos=(max(ends) - min(starts)).total_seconds() if starts and ends else None,
                soma_chamadas_segundos_conhecidos=sum(elapsed) if elapsed else None,
                chamadas_com_medicao=len(elapsed), chamadas_observadas=len(records),
                nota='Janela entre timestamps preservados, incluindo pausas. Não estima término nem duração de chamadas sem resposta.')


def fmt(value):
    return 'indisponível' if value is None else f'{value:.2f}'.replace('.', ',') if type(value) in (int, float) else str(value)


def cell(value):
    return str(value).replace('|', '&#124;').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')


def cost_time(records):
    values = [r for _, r in records.values()]
    costs = [Decimal(str(r['telemetry']['cost_usd'])) for r in values if r.get('telemetry', {}).get('cost_usd') is not None]
    times = [r['elapsed_seconds'] for r in values if type(r.get('elapsed_seconds')) in (int, float)]
    return (str(sum(costs, Decimal(0))) if costs else 'indisponível', len(values)-len(costs),
            sum(times) if times else None, len(times))


def readme(config, objective, account, decision, duration, records, runtime, failures):
    h = decision['h_ciclo']
    t, timing = objective['tokens']['total'], objective['tempo']['geracao_api']
    coverage = objective['cobertura']
    lines = ['# Humanizador PT-BR 0.8.0: rodada de 20/10/2026', '',
        f'**Situação: {decision["status"]}.** {decision["motivo"]}', '',
        'Referência: sem skill. Critério: [AGENTS congelado](AGENTS-frozen.md), vinculado ao [protocolo](PROTOCOL.json).', '',
        '## Resultado do ciclo', '', '| Indicador | Sem skill | Com skill | Variação |', '|---|---:|---:|---:|',
        f'| H do ciclo | {fmt(h["baseline"])} | {fmt(h["skill"])} | {fmt(decision["delta_h"])} pontos |',
        f'| Tokens totais por geração, média | {fmt(t["baseline"]["media"])} | {fmt(t["skill"]["media"])} | {fmt(t["variacao_percentual_razao_somas"])}% |',
        f'| Tempo da geração API, média em segundos | {fmt(timing["baseline"]["media"])} | {fmt(timing["skill"]["media"])} | {fmt(timing["variacao_percentual_razao_somas"])}% |', '',
        f'H = 100 menos impressão de IA. H do ciclo é a média dos pares com os três juízes, conforme AGENTS: {decision["pares_tres_juizes"]}/{decision["pares_planejados"]} pares. Não é probabilidade de autoria. O agregado de configurações com peso igual permanece em OBJETIVO.md; numa matriz parcial ele pode diferir do H do ciclo.',
        f'Tokens: {t["pares"]} pares, entrada completa mais saída, sem somar reasoning novamente. Tempo API: {timing["pares"]} pares, sem juízes nem preparação local. Ausência não vale zero.', '',
        '## Preferência, falhas e decisão', '',
        f'Preferência: sem skill {decision["preferencias"]["baseline"]}, com skill {decision["preferencias"]["skill"]}, empates {decision["preferencias"]["empate"]}; total {decision["denominador_votos"]} votos. Empates entram no total, não em um braço.',
        f'Falhas críticas: sem skill {decision["falhas_criticas"]["baseline"]}/{decision["denominador_falhas_por_braco"]}, com skill {decision["falhas_criticas"]["skill"]}/{decision["denominador_falhas_por_braco"]} julgamentos por braço.',
        f'Testes de software passando: {"sim" if decision["software_passando"] else "não comprovado"}. Plano completo: {"sim" if decision["plano_completo"] else "não"}. Aceitação requer ΔH ≥ 5, ganho em ao menos dois juízes, votos não inferiores e falhas críticas não superiores. Falta de pré-requisito torna a rodada inconclusiva.',
        f'Falhas/alertas API: {len(objective["erros"]["registros"])}; falhas mecânicas de entrega: {len(objective["erros"]["falhas_de_entrega"])}; grupos bloqueados: {len(objective["erros"]["grupos_bloqueados"])}. Nenhum texto ou escore foi corrigido ou excluído da fonte.',
        f'Chamadas ausentes: {len(failures["chamadas_ausentes"])}/{failures["chamadas_planejadas"]}; registros não completos: {len(failures["registros_nao_completos"])}. [Lista integral de ausências e falhas](FAILURES.json), com slots e categorias; saídas inválidas disponíveis permanecem nos 24 relatórios.',
        'Motivo de parada registrado: ' + cell(runtime.get('stop_reason') or 'nenhum registrado') + '.', '',
        '## Cobertura', '', '| Etapa | Observado | Previsto |', '|---|---:|---:|']
    lines += [f'| {cell(key)} | {row["observado"]} | {row["esperado"]} |' for key, row in coverage.items()]
    lines += ['', '## Modelos e modos', '',
              '| Modelo | Modo | Provedor | USD nativo conhecido | Chamadas sem custo | Soma duração API (s) | Chamadas cronometradas |',
              '|---|---|---|---:|---:|---:|---:|']
    for index, route in enumerate(config['routes']):
        subset = {k:v for k,v in records.items() if v[0]['phase'] == 'generation' and v[0]['route'] == index}
        cost, unknown, seconds, measured = cost_time(subset)
        lines.append('| ' + ' | '.join(map(cell, [route['model'], route['mode'], route['endpoint']['tag'], cost, unknown, fmt(seconds), measured])) + ' |')
    judge_models = {j['name']: j['model'] for j in config['judges']}
    judge_models['jev'] = 'typesafe/jev-1.13'
    lines += ['', '## Juízes', '', '| Juiz | Modelo | Modo | ΔH | Votos observados | USD nativo conhecido | Duração API conhecida (s) |', '|---|---|---|---:|---:|---:|---:|']
    for judge in JUDGES:
        subset = {k:v for k,v in records.items() if v[0]['phase'] == 'judge' and v[0]['judge'] == judge}
        modes = sorted({str(v[0].get('payload', {}).get('reasoning', 'Decisions nativo')) for v in subset.values()})
        cost, _, seconds, _ = cost_time(subset)
        lines.append('| ' + ' | '.join(map(cell, [judge, judge_models[judge], ', '.join(modes) or 'sem chamada observada',
            fmt(decision['delta_h_por_juiz'][judge]), objective['por_juiz'][judge]['cobertura']['observado'], cost, fmt(seconds)])) + ' |')
    lines += ['', '## Custo e duração mensurada', '',
        f'Ledger da chave dedicada: USD {account.get("dedicated_key_ledger_usd", "indisponível")}. Soma nativa conhecida: USD {account.get("known_native_total_usd", "indisponível")}. Diferença ledger menos soma nativa: USD {account.get("difference_usd", "indisponível")}.',
        f'Reconciliação na resolução observada: {account.get("reconciled_at_observed_resolution", False)}. Chamadas sem custo nativo: {len(account.get("unpriced_native_records", []))}. Valores ausentes não são custo zero; a publicação não reclassifica cobranças.',
        f'Novas sondagens: USD {account.get("new_probe_cost_usd", "indisponível")}. Custo histórico excluído do ledger novo: {account.get("historical_probe_cost_excluded", "indisponível")}. Geração e juízes separados em [ACCOUNTING.json](ACCOUNTING.json).',
        f'Janela observada: {duration["inicio_observado"]} a {duration["fim_observado"]}; {fmt(duration["janela_observada_segundos"])} s, incluindo pausas. Soma das chamadas cronometradas: {fmt(duration["soma_chamadas_segundos_conhecidos"])} s em {duration["chamadas_com_medicao"]}/{duration["chamadas_observadas"]} chamadas. Não representa prazo para completar a matriz.',
        'Preparação local: ' + cell(json.dumps(objective['tempo']['consultas_locais'], ensure_ascii=False)) + '.', '',
        '## Evidências', '',
        '- [Métricas e denominadores](OBJETIVO.md), [dados objetivos](OBJETIVO.json), [decisão reproduzível](DECISION.json).',
        '- [Resumo do renderer](SUMMARY.md), [telemetria](TELEMETRY.json), [contabilização](ACCOUNTING.json).',
        '- [Auditoria local](AUDIT.json), [sanitização e hashes de origem](SANITIZATION.json), [inventário da fonte](SOURCE-SHA256.json), [SHA256SUMS](SHA256SUMS).',
        '- [Manifesto público rederivado](evidence/manifest.json). SCHEDULE conserva a identidade histórica privada; a projeção não deve ser usada para retomar chamadas.',
        '## Textos completos dos 24 casos', '']
    supervision_path = ROOT / 'SUPERVISION.json'
    if supervision_path.exists():
        supervision = json.loads(supervision_path.read_bytes())
        lines[2:2] = [f'A execução foi interrompida após {fmt(supervision["elapsed_wait_seconds"] / 60)} minutos de espera sem resposta completa do Opus no terceiro pedido. Os dois primeiros pares foram avaliados por Jev, Astra e Opus. A matriz de 24 pedidos e 19 configurações ficou pendente.', '',
                      'A interrupção operacional está registrada em [SUPERVISION.json](SUPERVISION.json). A chamada sem conclusão foi preservada e não foi repetida; não recebeu nota.', '']
    lines += [f'- [{cell(c["id"])}: {cell(c["title"])}](experiments/{c["id"]}/REPORT.md)' for c in config['cases']]
    lines += ['', 'Cada caso inclui pedido literal, respostas completas e escores disponíveis dos três juízes. Ausências e falhas permanecem explícitas. Não há reclassificação das rodadas anteriores.', '']
    return '\n'.join(lines).encode('utf-8')


def transform_evidence(files, modules, sanitizer):
    """Todas as transformações ocorrem em memória antes do scanner e da cópia."""
    original = dict(files)
    g, store = modules['generation_eval'], modules['eval_store']
    removed = []
    for name, data in list(files.items()):
        if name.endswith('/raw.json') or name.startswith('evidence/frozen/probe-evidence/'):
            files[name], identifiers = sanitizer.sanitize_bytes(data)
            removed.extend(identifiers)
    for name in list(files):
        if not name.startswith('evidence/requests/') or not name.endswith('/raw.json'):
            continue
        prefix = name.rsplit('/', 1)[0]
        intent = json.loads(files[prefix + '/intent.json'])
        old = store.derive(intent['call'], intent, json.loads(original[name]))
        new = store.derive(intent['call'], intent, json.loads(files[name]))
        strip = lambda r: {k:v for k,v in r.items() if k != 'raw_sha256'}
        require(strip(new) == strip(old), 'sanitização alterou resultado/telemetria')
        result_name = prefix + '/result.json'
        if result_name in original:
            require(json.loads(original[result_name]) == old, 'cache privado inconsistente')
        if result_name not in files or new != old:
            files[result_name] = g.encoded(new) + b'\n'
    for name in list(files):
        if name.startswith('evidence/judge-inputs/') and name.endswith('.json'):
            data = json.loads(files[name])
            new = dict(data)
            new['raw_sha256'] = {slot: json.loads(files['evidence/requests/' + slot + '/result.json'])['raw_sha256'] for slot in data['raw_sha256']}
            if new != data:
                files[name] = g.encoded(new) + b'\n'
    manifest = json.loads(files['evidence/manifest.json'])
    for name in manifest['sha256']:
        manifest['sha256'][name] = sha(files['evidence/' + name])
    if manifest != json.loads(original['evidence/manifest.json']):
        files['evidence/manifest.json'] = g.encoded(manifest) + b'\n'
    changes = [dict(file=name, private_original_sha256=sha(original[name]) if name in original else None,
                    public_sha256=sha(data), reason='metadados sanitizados ou hash/cache dependente rederivado')
               for name, data in sorted(files.items()) if data != original.get(name)]
    return changes, removed


def freeze(files):
    require('SHA256SUMS' not in files, 'manifesto final já existe')
    files['SHA256SUMS'] = ''.join(sha(data) + '  ' + name + '\n' for name, data in sorted(files.items())).encode()


def verify(destination):
    manifest = safe_path(destination, 'SHA256SUMS').read_text('utf-8')
    listed = {}
    for line in manifest.split('\n'):
        if not line:
            continue
        digest, name = line.split('  ', 1)
        require(name not in listed and name != 'SHA256SUMS', 'manifesto duplicado')
        require(sha(safe_path(destination, name).read_bytes()) == digest, 'hash público divergente')
        listed[name] = digest
    actual = inventory(destination)
    actual.pop('SHA256SUMS', None)
    require(actual == listed, 'inventário público divergente')
    return len(listed)


def build(root, destination, write=False):
    source = root / 'execution'
    aggregate = load('publication_aggregate', root / 'analysis/agregar_objetivo.py')
    sanitizer = load('publication_sanitizer', root / 'sanitize-publication.py')
    modules = aggregate.load_modules(source / 'frozen/runner')
    g, renderer = modules['generation_eval'], modules['eval_render']
    files, inputs = {}, {}
    def take(path, name):
        path = safe_path(root, path.relative_to(root))
        require(name not in files, 'destino duplicado')
        files[name] = path.read_bytes()
        inputs[path.relative_to(root).as_posix()] = sha(files[name])
    with aggregate.existing_shared_lock(source):
        before = inventory(source, ignore_lock=True)
        source_manifest = g.read_json(source / 'manifest.json')
        for name in source_manifest['sha256']:
            safe_path(source, name)
        config = g.load_frozen(source)
        require(len(config['cases']) == 24 and len({c['id'] for c in config['cases']}) == 24, 'casos incompatíveis')
        require(len(config['routes']) == 19 and source_manifest['expected'] == aggregate.EXPECTED, 'matriz incompatível')
        require(config.get('skill_version') == '0.8.0', 'versão da skill incompatível')
        marker = g.read_json(source / 'execution-mode.json') if (source / 'execution-mode.json').exists() else {'mode':'PREPARED_NOT_EXECUTED'}
        require(marker['mode'] in ('LIVE_API', 'PREPARED_NOT_EXECUTED') and marker.get('synthetic') is not True, 'execução artificial não publicável')
        records, blinds = aggregate.readonly_audited(source, config, marker['mode'], modules)
        objective = g.read_json(root / 'analysis/resultado/OBJETIVO.json')
        account = g.read_json(root / 'ACCOUNTING.json')
        local, _ = aggregate.local_timings(source, config, marker['mode'], modules)
        current = aggregate.aggregate(config, records, blinds, modules, local)
        require(all(objective.get(k) == v for k,v in current.items()), 'OBJETIVO desatualizado ou divergente')
        require(objective.get('execucao', {}).get('modo') == marker['mode'], 'modo de OBJETIVO divergente')
        rows = renderer.metric_rows(config, records, blinds)
        costs = {phase: sum((Decimal(str(r['telemetry']['cost_usd'])) for c,r in records.values() if c['phase'] == phase and r.get('telemetry', {}).get('cost_usd') is not None), Decimal(0)) for phase in ('generation', 'judge')}
        require(all(Decimal(str(account['native_known_subtotals_usd'][phase])) == value for phase,value in costs.items()), 'ACCOUNTING desatualizado')
        require(Decimal(str(account['known_native_total_usd'])) == sum(costs.values()), 'total ACCOUNTING divergente')
        unknown = {(c['slot'], r['status']) for c,r in records.values() if r.get('telemetry', {}).get('cost_usd') is None}
        require(unknown == {(r['slot'], r['status']) for r in account['unpriced_native_records']}, 'custos ausentes divergentes')
        for path in sorted((root / 'report').rglob('*')):
            if path.is_file():
                name = path.relative_to(root / 'report').as_posix()
                require(name in ('SUMMARY.md', 'SUMMARY.json', 'TELEMETRY.json', 'DELIVERY.json', 'DELIVERY.md') or name.startswith('experiments/'), 'arquivo fora da allowlist do renderer')
                take(path, name)
        for name in ('OBJETIVO.md', 'OBJETIVO.json'):
            take(root / 'analysis/resultado' / name, name)
        require(files['OBJETIVO.md'] == aggregate.write_markdown(objective).encode('utf-8'), 'OBJETIVO.md diverge do JSON')
        for name in ('agregar_objetivo.py', 'test_objetivo.py'):
            take(root / 'analysis' / name, 'analysis/' + name)
        for name in ('ACCOUNTING.json', 'AGENTS-frozen.md', 'PROTOCOL.json', 'SCHEDULE.json'):
            take(root / name, name)
        for name in ('SOFTWARE-TESTS.json', 'FREEZE-VERIFIED.json', 'GENERATION-COST-LOOKUPS.json', 'SUPERVISION.json'):
            if (root / name).is_file():
                take(root / name, name)
        for name in ('publish.py', 'sanitize-publication.py', 'test_publication.py', 'schedule_run.py', 'test_schedule_run.py', 'SCHEDULE-POLICY.md'):
            if (root / name).is_file():
                take(root / name, 'controller/' + name)
        protocol = json.loads(files['PROTOCOL.json'])
        require(sha(files['AGENTS-frozen.md']) == protocol['agents_sha256'] == AGENTS_SHA256, 'AGENTS congelado divergente')
        require(protocol['reference'] == 'sem skill' and protocol['version'] == '0.8.0', 'protocolo divergente')
        if 'FREEZE-VERIFIED.json' in files:
            require(json.loads(files['FREEZE-VERIFIED.json'])['protocol_sha256'] == sha(files['PROTOCOL.json']), 'protocolo difere da verificação congelada')
        for name in source_manifest['sha256']:
            take(source / name, 'evidence/' + name)
        for name in ('manifest.json', 'execution-mode.json', 'runtime-summary.json', 'SCHEDULE.json'):
            if (source / name).is_file():
                take(source / name, 'evidence/' + name)
        for folder in ('requests', 'judge-inputs'):
            for path in sorted((source / folder).rglob('*')):
                if path.is_file():
                    require(path.suffix == '.json' and (folder != 'requests' or path.name in ('intent.json', 'raw.json', 'result.json', 'transport-error.json')), 'arquivo inesperado na evidência')
                    take(path, 'evidence/' + path.relative_to(source).as_posix())
        changes, removed = transform_evidence(files, modules, sanitizer)
        for data in files.values():
            sanitizer.scan(data, removed)
        # Primeira cópia em disco contém somente bytes já sanitizados e escaneados.
        with tempfile.TemporaryDirectory(prefix='humanizador-publication-') as temporary:
            stage = Path(temporary)
            for name, data in files.items():
                path = safe_path(stage, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            projected = g.load_frozen(stage / 'evidence')
            public_records, public_blinds = aggregate.readonly_audited(stage / 'evidence', projected, marker['mode'], modules)
            require(projected == config and public_blinds == blinds and set(public_records) == set(records), 'projeção mudou plano ou cobertura')
            for slot, (call, result) in records.items():
                public_call, public_result = public_records[slot]
                require(call == public_call and {k:v for k,v in result.items() if k != 'raw_sha256'} == {k:v for k,v in public_result.items() if k != 'raw_sha256'}, 'projeção mudou texto/escore/telemetria')
            # O renderer deriva somente no temporário. A fonte privada não recebe cache.
            renderer.render(stage / 'evidence', stage / 'regenerated')
            regenerated = {p.relative_to(stage / 'regenerated').as_posix(): p.read_bytes() for p in (stage / 'regenerated').rglob('*') if p.is_file()}
            report_names = {n for n in files if n.startswith('experiments/') or n in ('SUMMARY.md', 'SUMMARY.json', 'TELEMETRY.json')}
            require(report_names == set(regenerated), 'inventário do renderer divergente')
            require(all(files[name] == data for name,data in regenerated.items()), 'renderer diverge dos textos/escores da fonte')
        software = json.loads(files['SOFTWARE-TESTS.json']) if 'SOFTWARE-TESTS.json' in files else {}
        decision = verdict(rows, source_manifest['expected']['pairs'], current['cobertura']['pares_geracao_validos']['observado'], software_passed(software))
        duration = durations(records)
        failures = failure_inventory(config, records, blinds)
        runtime = json.loads(files.get('evidence/runtime-summary.json', b'{}'))
        files['DECISION.json'] = encoded(decision)
        files['DURATION.json'] = encoded(duration)
        files['FAILURES.json'] = encoded(failures)
        files['README.md'] = readme(config, objective, account, decision, duration, records, runtime, failures)
        files['.gitattributes'] = b'* -text\nexperiments/**/outputs/*.txt -whitespace\n'
        require(inventory(source, ignore_lock=True) == before, 'execução mudou durante a auditoria')
        require(all(sha(safe_path(root, name).read_bytes()) == digest for name,digest in inputs.items()), 'entrada alterada durante a auditoria')
        files['SOURCE-SHA256.json'] = encoded(dict(execution=before, publication_inputs=inputs))
        files['SANITIZATION.json'] = encoded(dict(scope='public_projection_only', private_execution_unchanged=True,
            transformed_files=changes, distinct_private_values_removed=len(set(removed)),
            all_candidate_text_and_judgments_equal_source=True, all_status_and_telemetry_equal_source=True,
            all_intents_and_payloads_equal_source=True, dependent_result_judge_input_and_manifest_hashes_rederived=True,
            note='Projeção sanitizada atestada contra fonte privada; não é cópia byte a byte de toda evidência HTTP. Não usar para retomar execução.'))
        audit = dict(kind='local_mechanical_attestation_not_independent_review', observed_at=datetime.now(timezone.utc).isoformat(),
            private_execution_unchanged=True, public_frozen_integrity_verified=True, renderer_bytes_verified=True,
            all_candidate_text_and_judgments_equal_source=True, literal_case_reports=24,
            unique_requests=len(records), pair_judgments=len(rows), status=decision['status'],
            credential_and_account_metadata_scan_passed=True, source_provenance='SOURCE-SHA256.json',
            ledger_reconciled_at_observed_resolution=account.get('reconciled_at_observed_resolution', False))
        files['AUDIT.json'] = encoded(audit)
        for data in files.values():
            sanitizer.scan(data, removed)
        freeze(files)
        if write:
            require(destination == DEST, 'destino fixo obrigatório')
            require(not destination.exists(), 'publicação existente preservada')
            destination.parent.mkdir(parents=True, exist_ok=True)
            stage = Path(tempfile.mkdtemp(prefix='.2026-10-20-0.8.0-', dir=destination.parent))
            try:
                for name, data in files.items():
                    target = safe_path(stage, name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as stream:
                        stream.write(data)
                verify(stage)
                # mkdir exclusivo impede sobreposição mesmo se outro processo publicar.
                destination.mkdir(exist_ok=False)
                for path in stage.iterdir():
                    os.rename(path, destination / path.name)
                stage.rmdir()
                verify(destination)
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
        return dict(mode='write' if write else 'check', files=len(files), **audit)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check', action='store_true', help='audita em temporário, sem publicar')
    group.add_argument('--write', action='store_true', help='grava somente o destino novo fixo, após auditoria')
    group.add_argument('--verify', action='store_true', help='confere SHA256SUMS e inventário do destino, sem alterar')
    args = parser.parse_args(argv)
    def no_network(*unused, **kwargs):
        raise RuntimeError('rede desabilitada neste publicador')
    try:
        with patch.object(socket, 'create_connection', no_network), patch.object(socket.socket, 'connect', no_network):
            result = {'verified_files': verify(DEST)} if args.verify else build(ROOT, DEST, args.write)
    except Exception as exc:
        # Não imprimir mensagens arbitrárias que poderiam conter resposta privada.
        print(f'Publicação bloqueada ({type(exc).__name__}); confira pré-requisitos e integridade local.', file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
