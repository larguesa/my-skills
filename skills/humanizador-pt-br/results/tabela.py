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
# Ordem de publicação: a última linha alimenta resumo_ultimo nos READMEs de entrada
# e relatorio_atual na seção "Avaliação mais recente" de results/README.md.
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
    # Situação vem da decisão gravada pela rodada, quando existe; precisa bater com os mesmos pares.
    decision = RESULTS / 'runs' / run / 'DECISION.json'
    s['decisao'] = json.loads(decision.read_text(encoding='utf-8')) if decision.exists() else None
    if s['decisao']:
        d = s['decisao']
        assert d['pares_tres_juizes'] == s['n'], run
        assert (d['preferencias']['skill'], d['preferencias']['baseline'], d['preferencias']['empate']) == s['votos'], run
        assert (d['falhas_criticas']['baseline'], d['falhas_criticas']['skill']) == tuple(
            sum(s['juizes'][j]['criticas'][i] for j in JUDGES) for i in (0, 1)), run
    return s


SUM = {row['run']: summary(row['run']) for row in ROWS if 'run' in row}
TITLES = dict(re.findall(r'^### (\d\d)\. (.+)$', (RESULTS / 'PROMPTS.md').read_text(encoding='utf-8'), re.M))


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


def pct(x):
    return f'{x:+.2f}'.replace('.', ',') + '%'


# Nome de apresentação do gerador; modelo fora daqui aparece pelo identificador.
MODELS = {'anthropic/claude-opus-5.5': 'Opus 5.5'}
# Valores de status gravados em DECISION.json pelo publish.py da rodada.
STATUS = dict(aceita='versão aceita', rejeitada='versão rejeitada', inconclusivo='ciclo ainda inconclusivo')
JUIZES = ', '.join(NAMES[j] for j in JUDGES[:-1]) + ' e ' + NAMES[JUDGES[-1]]
NOTA = ('Humanização percebida é a nota de 0 a 100 que três modelos juízes dão a cada texto, sem saber qual usou '
        'a skill; maior é mais humano. Nos votos, cada juiz escolhe o texto que atende melhor ao pedido.')


def metric_of(s, section, key):
    """Métrica de recurso com médias nos dois braços, ou None; ausência não vira zero."""
    metric = (s['data'].get(section) or {}).get(key)
    if metric and metric.get('pares') and all(metric.get(a, {}).get('media') is not None for a in ('baseline', 'skill')):
        return metric
    return None


def conclusao(s):
    h, v = s['h'], s['votos']
    if h is None:
        return '**Humanização percebida não medida: nenhum par com os três juízes.**'
    diff = h[1] - h[0]
    word = 'mais humanos' if diff > 0 else 'menos humanos' if diff < 0 else 'igualmente humanos'
    votes = ('receberam mais votos de preferência' if v[0] > v[1] else
             'receberam menos votos de preferência' if v[0] < v[1] else 'empataram nos votos de preferência')
    return f'**Na amostra avaliada, os textos escritos com a skill pareceram {word} aos juízes e {votes}.**'


def situacao_curta(row, s):
    """Cobertura e estado numa frase; denominadores e status vêm de OBJETIVO.json e DECISION.json."""
    cob = s['data']['cobertura']
    expected = cob['pares_tres_juizes']['esperado']
    data = row['versao'].partition(', ')[2]
    if len(s['rotas']) == 1:
        modelo = next(c['modelo'] for c in s['data']['por_configuracao'] if c['indice'] == s['rotas'][0])
        gerados = 'gerados com ' + MODELS.get(modelo, modelo.split('/')[-1])
    else:
        gerados = f'gerados por {len(s["rotas"])} de {cob["configuracoes_com_tres_juizes"]["esperado"]} configurações'
    d = s.get('decisao')
    status = STATUS.get(d['status'], 'situação ' + d['status']) if d else 'sem decisão registrada'
    return (f'Avaliação {"parcial" if s["n"] < expected else "completa"}{" de " + data if data else ""}: '
            f'{s["n"]} de {expected} pares, {gerados} e avaliados por {JUIZES}; {status}.')


def tabela_simples(row, s):
    """Cinco indicadores, referência, valor com skill e variação; linha sem dado fica fora."""
    versao, ref, h, n = row['versao'].partition(', ')[0], row['referencia'], s['h'], s['n']
    table = []
    if h is not None:
        v, total = s['votos'], n * len(JUDGES)
        crit = [sum(s['juizes'][j]['criticas'][i] for j in JUDGES) for i in (0, 1)]
        table += [('Humanização percebida, 0 a 100', num(h[0]), num(h[1]), f'{delta(h)} pontos'),
                  ('Preferência dos juízes, votos', f'{v[1]} de {sum(v)}', f'{v[0]} de {sum(v)}', f'{v[0] - v[1]:+d}'),
                  ('Falhas factuais críticas, julgamentos', f'{crit[0]} de {total}', f'{crit[1]} de {total}',
                   f'{crit[1] - crit[0]:+d}')]
    for section, key, label in (('tokens', 'total', 'Tokens por texto'),
                                ('tempo', 'geracao_api', 'Segundos de geração por texto')):
        metric = metric_of(s, section, key)
        if metric:
            percent = metric.get('variacao_percentual_razao_somas')
            label += ', média' + (f' de {metric["pares"]} pares' if metric['pares'] != n else '')
            table.append((label, num(metric['baseline']['media']), num(metric['skill']['media']),
                          pct(percent) if percent is not None else 'n/d'))
    if not table:
        return None
    head = ('Indicador', 'Sem skill' if ref == 'sem skill' else f'Referência {ref}', f'Com a skill {versao}', 'Variação')
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '|---|---:|---:|---:|',
                      *('| ' + ' | '.join(r) + ' |' for r in table)])


def pendente(row):
    return [f'**{row["versao"]}: {row["situacao"]}**', f'{row["fixo"]["amostra"]}. Humanização percebida não medida.']


def resumo_ultimo(prefix, rows=None, summaries=None):
    """Resumo da última entrada publicada, sem montar a tabela histórica.

    Uma candidata sem A/B continua pendente; nunca herda métricas anteriores.
    ROWS segue a ordem de publicação. Acrescente a rodada só com evidência publicada.
    """
    row = (ROWS if rows is None else rows)[-1]
    links = [('Relatório legível', 'README.md#avaliação-mais-recente')]
    if 'run' in row:
        s = (SUM if summaries is None else summaries)[row['run']]
        table = tabela_simples(row, s)
        lines = [conclusao(s), situacao_curta(row, s)] + ([table] if table else []) + ([NOTA] if s['h'] else [])
        links.append(('Evidência original da rodada', f'runs/{row["run"]}/README.md'))
    else:
        lines = pendente(row)
        links.append(('Teste funcional', next(target for title, target in row['links'] if title == 'teste funcional')))
    links.append(('Histórico', 'README.md#histórico-das-avaliações'))
    lines.append(' · '.join(link(t, a, prefix) for t, a in links))
    return '\n\n'.join(lines)


def relatorio_atual(prefix, rows=None, summaries=None):
    """Relatório legível da última entrada: situação completa, tabela, juízes, recursos, textos e evidência original."""
    row = (ROWS if rows is None else rows)[-1]
    if 'run' not in row:
        target = next(target for title, target in row['links'] if title == 'teste funcional')
        return '\n\n'.join(pendente(row) + [link('Teste funcional', target, prefix)])
    run = row['run']
    s = (SUM if summaries is None else summaries)[run]
    expected = s['data']['cobertura']['pares_tres_juizes']['esperado']
    context = f'Amostra: {sample(s)}; juízes {JUIZES}. **Situação:** {row["situacao"]}'
    if s['n'] < expected:
        context += f' A decisão exige os {expected} pares planejados julgados pelos três juízes.'
    table = tabela_simples(row, s)
    lines = [conclusao(s), context] + ([table] if table else [])
    seen = [(j, s['juizes'][j]['h']) for j in JUDGES if s['juizes'][j]['h'] is not None]
    if seen:
        sem = 'sem a skill' if row['referencia'] == 'sem skill' else f'referência {row["referencia"]}'
        lines.append(f'Humanização percebida por juiz ({sem} → com a skill): '
                     + '; '.join(f'{NAMES[j]} {num(h[0])} → {num(h[1])} ({delta(h)})' for j, h in seen) + '.')
    notes = []
    tokens = metric_of(s, 'tokens', 'total')
    entrada = ((s['data'].get('tokens') or {}).get('entrada') or {}).get('diferenca_soma')
    if tokens and tokens.get('diferenca_soma') and entrada is not None:
        notes.append(f'{num(100 * entrada / tokens["diferenca_soma"])}% do acréscimo de tokens vem da entrada, '
                     'onde vão as instruções da skill.')
    if metric_of(s, 'tempo', 'geracao_api'):
        notes.append('O tempo de geração inclui eventual fila da API, sem juízes nem preparação local.')
    if notes:
        lines.append('Recursos: ' + ' '.join(notes))
    casos = sorted(s['casos'])
    if casos:
        lines.append('Textos completos lado a lado, notas e justificativas: '
                     + ', '.join(link(f'{c[:2]}. {TITLES.get(c[:2], c)}', f'runs/{run}/experiments/{c}/REPORT.md', prefix)
                                 for c in casos) + '.')
    evidence = [(t, f) for t, f in (('relatório da rodada', 'README.md'), ('dados objetivos', 'OBJETIVO.json'),
                                    ('decisão', 'DECISION.json'), ('SHA256SUMS', 'SHA256SUMS'))
                if f in ('README.md', 'OBJETIVO.json') or (RESULTS / 'runs' / run / f).exists()]
    lines.append('Evidência original: ' + ' · '.join(link(t, f'runs/{run}/{f}', prefix) for t, f in evidence) + '.')
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
        '### Por juiz', 'Mesmos pares da tabela acima.', '\n'.join(judges),
        '### Cobertura', 'Observado sobre planejado em cada rodada.', '\n'.join(cover),
        '### Textos e votos por pedido',
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
        if history and '<!-- atual:inicio -->' in text:
            text = fill(text, 'atual', relatorio_atual(prefix))
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
