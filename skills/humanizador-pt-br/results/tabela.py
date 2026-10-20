"""Tabelas de resultados do Humanizador PT-BR, calculadas dos julgamentos gravados.

Na raiz do repositório:
    python3 -B skills/humanizador-pt-br/results/tabela.py --write   # atualiza os blocos dos READMEs
    python3 -B skills/humanizador-pt-br/results/tabela.py           # confere tabelas, números, links, pedidos e SHA256SUMS
"""
import collections
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

RESULTS = Path(__file__).resolve().parent
SKILL = RESULTS.parent
REPO = SKILL.parents[1]
JUDGES = ('jev', 'astra', 'opus')
NAMES = dict(jev='Jev', astra='Astra', opus='Opus')
OLD = ('https://github.com/larguesa/my-skills/blob/d14174698015e66f2c3814d0fe0110770509a242'
       '/skills/humanizador-pt-br/tests/README.md')

# Uma linha por teste, sempre com "referencia" explícita: "sem skill", "não se aplica" ou a versão aceita.
# Ordem de publicação: a última linha alimenta resumo_ultimo nos READMEs de entrada.
# Rodada nova: acrescente pasta, referência e situação, depois rode --write.
# Só acrescente uma ROW após publicar OBJETIVO.json, README.md,
# relatórios por pedido e SHA256SUMS.
# Preserve a linha funcional e informe a situação real, inclusive bloqueada/inconclusiva.
# Linhas "fixo" não são recalculadas: a 0.2.0 traz valores históricos fixos, conferidos em 20/10/2026
# contra os votos do commit d141746 (link da linha).
ROWS = [
    dict(versao='0.2.0, 2 contos', referencia='sem skill',
         situacao='Completa. Pedidos antigos, fora dos 24 aprovados. Sem decisão. Valores históricos fixos, conferidos em 20/10/2026.',
         fixo=dict(amostra='38 de 38 pares; 2 contos; 19 configurações', h=(30.0, 41.19298245614035), votos=(71, 43, 0)),
         links=[('índice com textos e votos', OLD)]),
    dict(versao='0.2.0, 02/10', referencia='sem skill',
         situacao='Encerrada com 64 saídas inválidas e 102 pares sem juízes. Pedidos com texto antigo. Sem decisão. '
                  'Valores históricos fixos, conferidos em 20/10/2026.',
         fixo=dict(amostra='308 de 456 pares; 24 de 24 pedidos; 19 de 19 configurações',
                   h=(31.07683982683982, 35.003246753246756), votos=(456, 428, 40)),
         links=[('índice com textos e votos', OLD)]),
    dict(versao='0.5.1, 10 e 13/10', run='2026-10-13', referencia='sem skill',
         situacao='Parcial: parou no limite do Qwen Flash; 2 respostas com skill só trouxeram comandos. Sem decisão.',
         links=[('início em 10/10', 'runs/2026-10-10/README.md')]),
    dict(versao='0.6.0, 19/10', run='2026-10-19', referencia='sem skill', situacao='Parcial: parou no limite do Qwen Flash. Sem decisão.'),
    dict(versao='0.7.0, 19/10', run='2026-10-19-max', referencia='sem skill', situacao='Parcial: parou sem capacidade do Grok. Sem decisão.'),
    dict(versao='0.8.0', referencia='não se aplica', situacao='Teste funcional concluído, sem avaliação de percepção.',
         fixo=dict(amostra='Sem A/B: 5 textos do MiMo 2.6 Pro, sem juízes'),
         links=[('teste funcional', 'reviews/0.8.0/SMOKE.md'), ('revisão', 'reviews/0.8.0/REVISAO.md')]),
    dict(versao='0.8.0, 20/10', run='2026-10-20-0.8.0', referencia='sem skill',
         situacao='Parcial e inconclusiva: interrompida após mais de 15 minutos sem resposta completa do Opus no terceiro pedido.'),
]
TARGETS = [(REPO / 'README.md', 'skills/humanizador-pt-br/results/'), (SKILL / 'README.md', 'results/'),
           (RESULTS / 'README.md', '')]
DOCS = [REPO / 'README.md', REPO / 'AGENTS.md', REPO / 'skills/index.md', SKILL / 'README.md', SKILL / 'AGENTS.md',
        RESULTS / 'README.md', RESULTS / 'PROMPTS.md', RESULTS / 'scripts/RUNNER.md',
        RESULTS / 'reviews/0.8.0/README.md', RESULTS / 'reviews/0.8.0/REVISAO.md', RESULTS / 'reviews/0.8.0/SMOKE.md',
        *sorted(RESULTS.glob('runs/*/README.md')),
        *(RESULTS / name for name in ('PROTOCOLO-0.6.0.md', 'PROTOCOLO-0.7.0.md', 'REVISAO-2026-10-19.md', 'REVISAO-0.7.0.md'))]


def pairs_of(judgments):
    pairs = collections.defaultdict(dict)
    for j in judgments:
        pair = pairs[j['case'], j['route'], j['pair_id']]
        if j['judge'] in pair:
            raise ValueError(f'juiz duplicado no par: {j["case"]} {j["route"]} {j["pair_id"]} {j["judge"]}')
        pair[j['judge']] = j
    return pairs


def summary(run):
    data = json.loads((RESULTS / 'runs' / run / 'OBJETIVO.json').read_text(encoding='utf-8'))
    full = [p for p in pairs_of(data['julgamentos_pareados']).values() if set(p) == set(JUDGES)]

    def h(arm, judges=JUDGES):
        return statistics.fmean(statistics.fmean(p[j]['humanizacao_' + arm] for j in judges) for p in full)

    def votes(judges=JUDGES):
        c = collections.Counter(p[j]['preference'] for p in full for j in judges)
        return c['skill'], c['baseline'], c['empate']

    s = dict(data=data, n=len(full), h=(h('baseline'), h('skill')) if full else None, votos=votes(),
             casos=collections.Counter(p['jev']['case'] for p in full), rotas=sorted({p['jev']['route'] for p in full}),
             juizes={j: dict(h=(h('baseline', [j]), h('skill', [j])) if full else None, votos=votes([j]),
                             criticas=(sum(p[j]['baseline_critical'] for p in full),
                                       sum(p[j]['skill_critical'] for p in full))) for j in JUDGES})
    # A tabela só sai se bater com os agregados que a análise da rodada gravou.
    rec = data['percepcao']['pares_tres_juizes']['humanizacao']
    assert data['cobertura']['pares_tres_juizes']['observado'] == rec['pares'] == s['n'], run
    assert all(rec[a]['media'] is None if v is None else abs(rec[a]['media'] - v) < 1e-9
               for a, v in zip(('baseline', 'skill'), s['h'] or (None, None))), run
    for j in JUDGES:
        same = data['por_juiz'][j]['mesmos_pares_tres_juizes']
        assert all(same['humanizacao'][a]['media'] is None if v is None
                   else abs(same['humanizacao'][a]['media'] - v) < 1e-9
                   for a, v in zip(('baseline', 'skill'), s['juizes'][j]['h'] or (None, None))), (run, j)
        p = same['preferencias']
        assert (p.get('skill', 0), p.get('baseline', 0), p.get('empate', 0)) == s['juizes'][j]['votos'], (run, j)
    return s


SUM = {row['run']: summary(row['run']) for row in ROWS if 'run' in row}


def num(x):
    return f'{x:.2f}'.replace('.', ',')


def delta(h):
    return f'{h[1] - h[0]:+.2f}'.replace('.', ',')


def votos(v):
    return f'{v[0]} / {v[1]} / {v[2]} de {sum(v)}'


def link(text, target, prefix):
    return f'[{text}]({target if target.startswith("http") else prefix + target})'


def sample(s):
    cob = s['data']['cobertura']
    casos, rotas = s['casos'], s['rotas']
    pedidos = (f'pedido {next(iter(casos))[:2]}' if len(casos) == 1
               else f'{len(casos)} de {cob["pedidos_com_julgamento"]["esperado"]} pedidos')
    if len(rotas) == 1:
        modelo = next(c['modelo'] for c in s['data']['por_configuracao'] if c['indice'] == rotas[0])
        geradores = 'só ' + modelo.split('/')[1]
    else:
        geradores = f'{len(rotas)} de {cob["configuracoes_com_tres_juizes"]["esperado"]} configurações'
    return f'{s["n"]} de {cob["pares_tres_juizes"]["esperado"]} pares; {pedidos}; {geradores}'


def resumo_ultimo(prefix, rows=None, summaries=None):
    """Resumo da última entrada publicada, sem montar a tabela histórica.

    Uma candidata sem A/B continua pendente; nunca herda métricas anteriores.
    ROWS segue a ordem de publicação. Acrescente a rodada só com evidência publicada.
    """
    row = (ROWS if rows is None else rows)[-1]
    lines = [f'**{row["versao"]}: {row["situacao"]}**']
    if 'run' in row:
        s = (SUM if summaries is None else summaries)[row['run']]
        h = s['h']
        if h is None:
            lines.append('H e ΔH não medidos: nenhum par com os três juízes.')
        else:
            lines.append(f'**H {num(h[1])}** com a skill, contra {num(h[0])} na referência '
                         f'({row["referencia"]}). **ΔH {delta(h)} pontos**. '
                         'H vai de 0 a 100: quanto maior, mais humano o texto pareceu aos juízes.')
        lines.append(f'Cobertura: {sample(s)}. Votos versão / referência / empate: {votos(s["votos"])}.')
        expected = s['data']['cobertura']['pares_tres_juizes']['esperado']
        for section, key, label, unit in (
                ('tokens', 'total', 'Tokens totais', ''),
                ('tempo', 'geracao_api', 'Tempo de geração na API', ' s')):
            metric = (s['data'].get(section) or {}).get(key)
            if metric and metric.get('pares') and all(metric.get(a, {}).get('media') is not None
                                                    for a in ('baseline', 'skill')):
                percent = metric.get('variacao_percentual_razao_somas')
                change = (' (' + f'{percent:+.2f}'.replace('.', ',') + '%)' if percent is not None else '')
                lines.append(f'{label}, média por texto (referência → versão): '
                             f'{num(metric["baseline"]["media"])} → {num(metric["skill"]["media"])}{unit}{change}; '
                             f'{metric["pares"]} de {expected} pares.')
        report = f'runs/{row["run"]}/README.md'
    else:
        lines.append(f'{row["fixo"]["amostra"]}. H e ΔH não medidos.')
        report = next(target for title, target in row['links'] if title == 'teste funcional')
    lines.append(link('Relatório', report, prefix) + ' · ' + link('Histórico', 'README.md', prefix))
    return '\n\n'.join(lines)


def main_table(prefix, rows=None):
    lines = ['| Versão | Referência | Amostra julgada | H referência | H versão | Δ H '
             '| Votos versão / referência / empate | Situação | Textos e votos |',
             '|---|---|---|---:|---:|---:|---|---|---|']
    for row in rows or ROWS:
        links = list(row.get('links', []))
        if 'run' in row:
            s, run = SUM[row['run']], row['run']
            amostra, h, v = sample(s), s['h'], s['votos']
            casos = sorted(s['casos'])
            first = (('textos e votos', f'runs/{run}/experiments/{casos[0]}/REPORT.md') if len(casos) == 1
                     else ('textos e votos por pedido', 'README.md#textos-e-votos-por-pedido'))
            links = [first, ('relatório', f'runs/{run}/README.md')] + links
        else:
            amostra, h, v = row['fixo']['amostra'], row['fixo'].get('h'), row['fixo'].get('votos')
        cells = [row['versao'], row['referencia'], amostra, num(h[0]) if h else 'não medido', num(h[1]) if h else 'não medido',
                 delta(h) if h else 'n/d', votos(v) if v else 'n/d', row['situacao'],
                 ', '.join(link(t, a, prefix) for t, a in links)]
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines)


def details():
    runs = [(row['versao'].split(',')[0], row['run']) for row in ROWS if 'run' in row]
    judges = ['| Versão | Juiz | H referência | H versão | Δ H | Votos versão / referência / empate '
              '| Falhas críticas referência / versão |', '|---|---|---:|---:|---:|---|---|']
    for versao, run in runs:
        for j in JUDGES:
            d = SUM[run]['juizes'][j]
            metrics = (f'{num(d["h"][0])} | {num(d["h"][1])} | {delta(d["h"])}'
                       if d['h'] is not None else 'não medido | não medido | n/d')
            judges.append(f'| {versao} | {NAMES[j]} | {metrics} '
                          f'| {votos(d["votos"])} | {d["criticas"][0]} / {d["criticas"][1]} de {SUM[run]["n"]} |')
    keys = [('geracoes_submetidas', 'Gerações enviadas'), ('respostas_api_validadas', 'Respostas completas'),
            ('pares_geracao_validos', 'Pares completos'), ('chamadas_juizes_validas', 'Chamadas de juízes'),
            ('pares_tres_juizes', 'Pares com três juízes')]
    cover = ['| Versão | ' + ' | '.join(t for _, t in keys) + ' |', '|---|' + '---:|' * len(keys)]
    for versao, run in runs:
        cob = SUM[run]['data']['cobertura']
        cover.append(f'| {versao} | ' + ' | '.join(f'{cob[k]["observado"]} de {cob[k]["esperado"]}' for k, _ in keys) + ' |')
    titles = re.findall(r'^### (\d\d)\. (.+)$', (RESULTS / 'PROMPTS.md').read_text(encoding='utf-8'), re.M)
    prompts = ['| Pedido | ' + ' | '.join(v for v, _ in runs) + ' |', '|---|' + '---|' * len(runs)]
    for number, title in titles:
        cells = []
        for _, run in runs:
            folder = next((RESULTS / 'runs' / run / 'experiments').glob(number + '-*'))
            n, report = SUM[run]['casos'][folder.name], f'runs/{run}/experiments/{folder.name}/REPORT.md'
            cells.append(f'[{n} {"par" if n == 1 else "pares"}]({report})' if n
                         else f'[textos sem juízes]({report})' if any(folder.glob('outputs/*.txt')) else 'não rodou')
        prompts.append(f'| {number}. {title} | ' + ' | '.join(cells) + ' |')
    return '\n\n'.join([
        '## Por juiz', 'Mesmos pares da tabela acima.', '\n'.join(judges),
        '## Cobertura', 'Observado sobre planejado em cada rodada.', '\n'.join(cover),
        '## Textos e votos por pedido',
        'Cada link abre o pedido literal, os textos completos lado a lado, da referência e da versão, e as notas de Jev, Astra e '
        'Opus, com as justificativas de Astra e Opus. A 0.2.0 usou outra redação dos pedidos e está no '
        f'[índice antigo]({OLD}).', '\n'.join(prompts)])


def fill(text, name, body):
    start, end = f'<!-- {name}:inicio -->', f'<!-- {name}:fim -->'
    i, j = text.index(start) + len(start), text.index(end)
    return text[:i] + '\n' + body + '\n' + text[j:]


def rendered():
    out = {}
    for path, prefix in TARGETS:
        history = path == RESULTS / 'README.md'
        text = fill(path.read_text(encoding='utf-8'), 'tabela' if history else 'resumo',
                    main_table(prefix) if history else resumo_ultimo(prefix))
        out[path] = fill(text, 'detalhes', details()) if '<!-- detalhes:inicio -->' in text else text
    return out


def slug(heading):
    return re.sub(r'[^\w\- ]', '', heading.strip().lower()).replace(' ', '-')


def broken_links(docs=None):
    bad = []
    for doc in docs or DOCS:
        for target in re.findall(r'\]\(([^)\s]+)\)', doc.read_text(encoding='utf-8')):
            if re.match(r'[a-z]+:', target):
                continue
            path, _, anchor = target.partition('#')
            dest = (doc.parent / path) if path else doc
            if not dest.exists():
                bad.append(f'{doc}: {target}')
            elif anchor and dest.suffix == '.md':
                heads = re.findall(r'^#+ (.+)$', dest.read_text(encoding='utf-8'), re.M)
                if anchor not in map(slug, heads):
                    bad.append(f'{doc}: {target}')
    return bad


def check_prompts():
    def blocks(path):
        return re.findall(r'```text\n(.*?)\n```', path.read_text(encoding='utf-8'), re.S)
    current = blocks(RESULTS / 'PROMPTS.md')
    frozen = sorted(RESULTS.glob('runs/*/evidence/frozen/skill/results/PROMPTS.md'))
    plan = json.loads((RESULTS / 'reviews/0.8.0/writing-smoke/plan.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256((RESULTS / 'PROMPTS.md').read_bytes()).hexdigest()
    errors = [] if len(current) == 24 else [f'PROMPTS.md tem {len(current)} pedidos']
    errors += [f'pedidos diferentes de {p.relative_to(RESULTS)}' for p in frozen if blocks(p) != current]
    errors += [] if plan['source_hashes']['results/PROMPTS.md'] == digest else ['PROMPTS.md mudou desde o teste da 0.8.0']
    return errors, len(frozen)


def check_seals():
    errors, counts = [], {}
    for sums in sorted(RESULTS.glob('runs/*/SHA256SUMS')):
        lines = sums.read_text(encoding='utf-8').splitlines()
        for line in lines:
            digest, name = line.split('  ', 1)
            path = sums.parent / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                errors.append(f'{sums.parent.name}/{name} difere do SHA256SUMS')
        counts[sums.parent.name] = len(lines)
    return errors, counts


def main():
    new = rendered()
    if '--write' in sys.argv[1:]:
        for path, text in new.items():
            path.write_text(text, encoding='utf-8')
        print('READMEs atualizados:', ', '.join(str(p.relative_to(REPO)) for p in new))
        return 0
    errors = [f'{p.relative_to(REPO)}: tabela desatualizada; rode --write'
              for p, text in new.items() if p.read_text(encoding='utf-8') != text]
    errors += ['link quebrado em ' + b for b in broken_links()]
    prompt_errors, frozen = check_prompts()
    seal_errors, counts = check_seals()
    errors += prompt_errors + seal_errors
    print(f'Números conferidos com OBJETIVO.json: {", ".join(SUM)}.')
    print(f'Pedidos: 24, iguais a {frozen} cópias congeladas e ao teste da 0.8.0.')
    print('SHA256SUMS: ' + ', '.join(f'{k} {v}' for k, v in counts.items()) + ' entradas.')
    print('\n'.join(errors) or 'Tabelas e links em dia.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
