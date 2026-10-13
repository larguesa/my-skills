"""Audited projections only: raw candidate text, per-judge results and telemetry."""
from collections import Counter
from decimal import Decimal
import html
import json
from pathlib import Path
import re
import generation_eval as g
from eval_store import Store

NOTICE = ('Impressão de IA é julgamento não calibrado, não prova de autoria. '
          'Preferência e qualidade são medidas separadas. Três votos sobre os mesmos textos '
          'não são três experimentos independentes. Avaliação humana pendente.')


def mean(values):
    return sum(values) / len(values) if values else None


def shown(value):
    return 'PENDENTE' if value is None else f'{value:.2f}'


def fenced(text):
    longest = max((len(m.group()) for m in re.finditer(r'`+', text)), default=0)
    fence = '`' * max(3, longest + 1)
    return fence + 'text\n' + text + '\n' + fence


def cell(text):
    return '<pre>' + html.escape(text).replace('|', '&#124;').replace('\n', '&#10;').replace('\r', '&#13;') + '</pre>'


def aggregate_telemetry(rows):
    costs = [Decimal(r['telemetry']['cost_usd']) for r in rows if r.get('telemetry', {}).get('cost_usd') is not None]
    result = dict(requests=len(rows), costs_known=len(costs), costs_unknown=len(rows) - len(costs),
                  known_cost_usd=str(sum(costs, Decimal(0))),
                  total_usd=str(sum(costs, Decimal(0))) if len(costs) == len(rows) else None)
    for field in ['cache_read_tokens', 'cache_write_tokens', 'reasoning_tokens']:
        values = [r.get('telemetry', {}).get(field) for r in rows]
        known = [v for v in values if type(v) is int and v >= 0]
        result[field] = dict(known_sum=sum(known), known_count=len(known),
                            total=sum(known) if len(known) == len(rows) else None)
    for field, alternate in [('prompt_tokens', 'input_tokens'), ('completion_tokens', 'output_tokens')]:
        values = [r.get('telemetry', {}).get('usage', {}).get(field,
                  r.get('telemetry', {}).get('usage', {}).get(alternate)) for r in rows]
        known = [v for v in values if type(v) is int and v >= 0]
        result[field] = dict(known_sum=sum(known), known_count=len(known),
                            total=sum(known) if len(known) == len(rows) else None)
    return result


def audited(root, config, mode):
    store = Store(root, mode)
    records = store.audit()
    expected = {c['slot']: c for c in g.generation_calls(root, config)}
    blinds = {b['case']: b for b in g.read_json(root / 'frozen/blind-plan.json')}
    for case in config['cases']:
        blind = blinds[case['id']]
        for index in range(len(blind['groups'])):
            calls, _ = g.judge_calls(config, case, blind, index, records)
            expected.update({c['slot']: c for c in calls})
    for slot, (call, _) in records.items():
        if slot not in expected or call != expected[slot]:
            raise ValueError('request/anonymous mapping outside frozen plan: ' + slot)
    return records, blinds


def metric_rows(config, records, blinds):
    rows = []
    for case in config['cases']:
        blind = blinds[case['id']]
        for index, group in enumerate(blind['groups']):
            for name in g.JUDGES:
                slot = f'j.{case["id"]}.c{index:02}.{name}'
                entry = records.get(slot)
                if not entry or entry[1]['status'] != 'completed':
                    continue
                call, result = entry
                judgment = result['judgment']
                for pid in group:
                    pair = blind['pairs'][pid]
                    by_arm = {}
                    for letter, tid in pair.items():
                        source = records[blind['mapping'][tid]][0]
                        by_arm[source['arm']] = dict(letter=letter, tid=tid, route=source['route'])
                    base, skill = by_arm['baseline'], by_arm['skill']
                    if base['route'] != skill['route']:
                        raise ValueError('paired route mismatch')
                    preference = judgment['preferencia'][pid]
                    winner = 'empate' if preference == 'empate' else next(
                        arm for arm, row in by_arm.items() if row['letter'] == preference)
                    row = dict(case=case['id'], route=base['route'], judge=name, pair_id=pid,
                        baseline_id=base['tid'], skill_id=skill['tid'], preference=winner,
                        detection_baseline=judgment['deteccao'][base['tid']],
                        detection_skill=judgment['deteccao'][skill['tid']],
                        quality_baseline=result['quality_aggregate'][base['tid']]['total'],
                        quality_skill=result['quality_aggregate'][skill['tid']]['total'],
                        baseline_reason=judgment['qualidade'][base['tid']]['justificativa'],
                        skill_reason=judgment['qualidade'][skill['tid']]['justificativa'],
                        baseline_critical=judgment['qualidade'][base['tid']]['critico'],
                        skill_critical=judgment['qualidade'][skill['tid']]['critico'])
                    row['detection_delta'] = row['detection_skill'] - row['detection_baseline']
                    row['quality_delta'] = row['quality_skill'] - row['quality_baseline']
                    rows.append(row)
    if len({(r['case'], r['route'], r['judge']) for r in rows}) != len(rows):
        raise ValueError('duplicate pair judgment')
    return rows


def metrics(rows):
    fields = ['detection_baseline', 'detection_skill', 'detection_delta',
              'quality_baseline', 'quality_skill', 'quality_delta']
    return dict(pair_judgments=len(rows), individual_impression_scores=len(rows) * 2,
        preferences=dict(Counter(r['preference'] for r in rows)),
        fields={field: dict(mean=mean([r[field] for r in rows]), denominator=len(rows)) for field in fields})


def render(root, reports):
    root, reports = Path(root), Path(reports)
    config = g.load_frozen(root)
    if reports.resolve() == root.resolve() or any(
        reports.resolve().is_relative_to((root / d).resolve()) for d in ['frozen', 'requests', 'judge-inputs']):
        raise ValueError('reports must not overwrite the evidence store')
    with g.locked(root):
        marker = root / 'execution-mode.json'
        mode = g.read_json(marker)['mode'] if marker.exists() else 'PREPARED_NOT_EXECUTED'
        records, blinds = audited(root, config, mode)
        rows = metric_rows(config, records, blinds)
        generated = [r for c, r in records.values() if c['phase'] == 'generation']
        judged = [r for c, r in records.values() if c['phase'] == 'judge']
        accounting = dict(generation=aggregate_telemetry(generated), judges=aggregate_telemetry(judged),
            judges_by_name={name: aggregate_telemetry([r for c, r in records.values()
                if c['phase'] == 'judge' and c['judge'] == name]) for name in g.JUDGES},
            probes=dict(total_usd=None, known_cost_usd=None, receipt=None))
        probe_receipt = root / 'frozen/probes-accounting.json'
        if probe_receipt.exists():
            receipt = g.read_json(probe_receipt)
            accounting['probes'] = dict(total_usd=None, known_cost_usd=receipt.get('native_cost_usd'),
                receipt=receipt, note='Separate preflight ledger; no candidate or judge attribution.')
        summary = dict(execution_mode=mode, expected=g.read_json(root / 'manifest.json')['expected'],
            submitted_generations=len(generated), valid_generations=sum(r['status'] == 'completed' for r in generated),
            invalid_generations=sum(r['status'] == 'invalid_response' for r in generated),
            submitted_judge_calls=len(judged), valid_judge_calls=sum(r['status'] == 'completed' for r in judged),
            **metrics(rows), judges={name: metrics([r for r in rows if r['judge'] == name]) for name in g.JUDGES},
            accounting=accounting, automatic_retry=False, monetary_ceiling=None, human_evaluation='pending',
            detection_interpretation='uncalibrated impression, not proof of authorship',
            status_counts=dict(Counter(r['status'] for _, r in records.values())))
        summary['by_configuration'] = [dict(model=route['model'], mode=route['mode'],
            provider=route['endpoint']['tag'], judges={name: metrics([r for r in rows if
            r['route'] == index and r['judge'] == name]) for name in g.JUDGES})
            for index, route in enumerate(config['routes'])]
        g.derived_write(reports / 'SUMMARY.json', summary)
        g.derived_write(reports / 'TELEMETRY.json', dict(accounting=accounting, requests=[dict(
            slot=c['slot'], phase=c['phase'], status=r['status'], telemetry=r.get('telemetry', {}),
            elapsed_seconds=r.get('elapsed_seconds'), started_at=r.get('started_at'), finished_at=r.get('finished_at'),
            usage_issues=r.get('validation_issues', [])) for c, r in records.values()]))
        intro = ['# Nova avaliação: geração independente', '', f'Execução: **{mode}**.', '', NOTICE, '',
            '## Resumo agregado', '',
            f'Gerações válidas: {summary["valid_generations"]}/912. Chamadas de juízes válidas: '
            f'{summary["valid_judge_calls"]}/432. Julgamentos de pares: {len(rows)}/1368; '
            f'escores individuais de impressão: {len(rows)*2}/2736.', '',
            'Cada configuração tem o mesmo peso por par observado. Ausências não valem zero; '
            'médias e deltas usam somente pares completos de cada juiz. Valores B/S = baseline/skill. '
            'Δ = skill − baseline; menor impressão não demonstra maior qualidade.', '',
            '| Configuração | Jev | Astra | Opus |', '|---|---|---|---|']
        for index, route in enumerate(config['routes']):
            values = []
            for name in g.JUDGES:
                selected = [r for r in rows if r['route'] == index and r['judge'] == name]
                if not selected:
                    values.append('PENDENTE (n=0)')
                else:
                    m = metrics(selected)
                    fields = m['fields']
                    values.append(f'Impressão B/S {shown(fields["detection_baseline"]["mean"])}/'
                        f'{shown(fields["detection_skill"]["mean"])}; Δ {shown(fields["detection_delta"]["mean"])}; '
                        f'qualidade Δ {shown(fields["quality_delta"]["mean"])}; n={len(selected)}; votos {m["preferences"]}')
            intro.append('| ' + f'{route["model"]} / {route["mode"]}' + ' | ' + ' | '.join(values) + ' |')
        intro += ['', '## Custos e telemetria separados', '',
            f'Geração: conhecido USD {accounting["generation"]["known_cost_usd"]}; '
            f'custo completo {accounting["generation"]["total_usd"]}; '
            f'{accounting["generation"]["costs_unknown"]} chamadas sem custo nativo.',
            f'Juízes: conhecido USD {accounting["judges"]["known_cost_usd"]}; '
            f'custo completo {accounting["judges"]["total_usd"]}; '
            f'{accounting["judges"]["costs_unknown"]} chamadas sem custo nativo.',
            f'Probes: conhecido USD {accounting["probes"]["known_cost_usd"]}; reconciliação no recibo separado.', '',
            'Sem teto monetário. Cache read/write e tokens nativos em TELEMETRY.json; counters ausentes '
            'permanecem null. Reasoning não é somado à completion. Custos sintéticos OFFLINE_FAKE '
            'são fixtures, nunca gasto real.', '', '## Casos', '']
        for case in config['cases']:
            intro.append(f'- [{case["title"]}](experiments/{case["id"]}/REPORT.md)')
            report = ['# ' + case['title'], '', f'Execução: **{mode}**.', '', NOTICE, '',
                      '## Prompt literal', '', fenced(case['prompt']), '', '## Comparação completa', '',
                      '| Modelo / modo | Baseline | Skill 0.5.1 | Jev | Astra | Opus |',
                      '|---|---|---|---|---|---|']
            case_dir = reports / 'experiments' / case['id']
            for index, route in enumerate(config['routes']):
                texts = []
                for arm in g.ARMS:
                    slot = f'g.{case["id"]}.r{index:02}.{arm}'
                    entry = records.get(slot)
                    text = entry[1].get('text') if entry else None
                    if isinstance(text, str):
                        filename = f'outputs/r{index:02}-{arm}.txt'
                        g.derived_write(case_dir / filename, text.encode('utf-8'))
                        telemetry = entry[1]['telemetry']
                        texts.append(cell(text) + f'<br>[UTF-8 literal]({filename}); '
                            f'{entry[1]["status"]}; USD {telemetry["cost_usd"]}; '
                            f'{entry[1]["elapsed_seconds"]:.3f}s; '
                            f'tokens entrada/saída {telemetry["usage"].get("prompt_tokens")}/'
                            f'{telemetry["usage"].get("completion_tokens")}')
                    else:
                        texts.append('PENDENTE' if not entry else entry[1]['status'])
                judges = []
                for name in g.JUDGES:
                    selected = [r for r in rows if r['case'] == case['id'] and
                                r['route'] == index and r['judge'] == name]
                    if not selected:
                        judges.append('PENDENTE')
                    else:
                        row = selected[0]
                        judges.append(f'Impressão B/S {shown(row["detection_baseline"])}/'
                            f'{shown(row["detection_skill"])}; qualidade B/S '
                            f'{shown(row["quality_baseline"])}/{shown(row["quality_skill"])}; '
                            f'preferência: {row["preference"]}; crítico B/S '
                            f'{row["baseline_critical"]}/{row["skill_critical"]}; '
                            + html.escape(str(row['baseline_reason'] or 'Justificativa indisponível em Decisions'))
                            .replace('|', '&#124;').replace('\n', '<br>') + ' / '
                            + html.escape(str(row['skill_reason'] or 'Justificativa indisponível em Decisions'))
                            .replace('|', '&#124;').replace('\n', '<br>'))
                report.append('| ' + f'{route["model"]} / {route["mode"]}' + ' | '
                              + ' | '.join(texts + judges) + ' |')
            report += ['', '## Protocolo e limitações', '',
                'Chamadas novas e independentes. Baseline recebe só o prompt literal; tratamento recebe '
                'SKILL.md 0.5.1, JSONs completos de catálogo/estilos e consultas/plano locais congelados. '
                'Nenhum texto de outro braço, preferência pessoal ou feedback de juiz entra nos candidatos.',
                'Mapeamento anônimo e grupos de até quatro pares são congelados; grupo com candidato '
                'inválido fica sem julgamento, sem reagrupamento oportunista.',
                'Modelos, modos e providers efetivos são os congelados, incluindo amendments explícitos. '
                'Aliases na resposta não comprovam a versão efetiva nem o uso do reasoning solicitado.',
                'Juízes chat: máximo 16384 tokens histórico. Jev Decisions: payload nativo histórico '
                'sem max_tokens artificial. Agregado de qualidade: média das quatro dimensões; '
                'erro crítico limita correção a 25 e total a 49, preservando notas brutas.',
                '', '[Resumo agregado](../../SUMMARY.md)', '']
            g.derived_write(case_dir / 'REPORT.md', '\n'.join(report).encode())
        g.derived_write(reports / 'SUMMARY.md', '\n'.join(intro).encode())
        return summary
