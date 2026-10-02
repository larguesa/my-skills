#!/usr/bin/env python3
"""Bounded, offline observations for the 24 frozen genre exercises.

A pass concerns only the named mechanical observation, not factual truth,
semantic fidelity, appropriate units, dimensional analysis or writing quality.
Candidate code and curl are data. Nothing supplied by a candidate is executed.
"""
import ast
import json
import shlex
import textwrap
from html.parser import HTMLParser
from pathlib import Path
import re
from collections.abc import Mapping
from decimal import Decimal, localcontext, ROUND_HALF_UP

_CASES = json.loads((Path(__file__).resolve().parents[1] /
                    'experiments/cases.json').read_text(encoding='utf-8'))['cases']
CASES = {case['id']: case for case in _CASES}
if len(CASES) != 24 or len(_CASES) != 24:
    raise ValueError('expected exactly 24 unique approved cases')
BOUNDS = {}
for _case in _CASES:
    _matches = re.findall(r'\b(\d+) a (\d+) palavras\b', _case['prompt'])
    if len(_matches) != 1:
        raise ValueError('ambiguous frozen word bounds: ' + _case['id'])
    BOUNDS[_case['id']] = tuple(map(int, _matches[0]))


def _entry(name, status, detail):
    return {'name': name, 'status': status, 'detail': detail}


def _observe(target, name, condition, detail):
    target.append(_entry(name, 'pass' if condition else 'fail', detail))


def _approved(case):
    identifier = case.get('id') if isinstance(case, Mapping) else case
    if not isinstance(identifier, str) or identifier not in CASES:
        raise ValueError('unknown approved case ID')
    approved = CASES[identifier]
    if isinstance(case, Mapping) and 'prompt' in case and case['prompt'] != approved['prompt']:
        raise ValueError('case prompt differs from frozen approved prompt')
    return approved


SECTIONS = {
    3: (('Autenticação', 'Criar tarefa', 'Erros', 'Limitações'), True),
    4: (('Reprodução', 'Causa', 'Correção', 'Limitações'), True),
    6: (('Dados', 'Resultado', 'Limites'), False),
    10: (('Observações', 'Limitações'), False),
    15: (('Escopo', 'Prazo', 'Investimento', 'Exclusões', 'Próximo passo'), True),
}
PARAGRAPHS = {2: 3, 5: 2, 7: 3, 8: 2, 9: 3, 11: 1, 12: 4, 13: 3,
              18: 2, 19: 4, 20: 5}
TITLES = {1, 2, 18, 19, 24}


def _plain_heading(line):
    line = re.sub(r'^\s*#{1,6}\s+', '', line.strip())
    line = re.sub(r'^\d+[.)]\s+', '', line)
    line = re.sub(r'\s+#+\s*$', '', line)
    return line.replace('**', '').replace('__', '').strip()


def _prose_lines(text):
    # Skip fenced data, never parse it as headings/prose.
    lines, fence = [], None
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            lines.append('')
        elif fence is None:
            lines.append(line)
        else:
            lines.append('')
    return lines


class _HTMLTable(HTMLParser):
    """Parse inert HTML table text. No rendering, fetches or script execution."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.row, self.cell = [], None, None
        self.table_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table_depth += 1
        elif self.table_depth and tag == 'tr':
            self.row = []
        elif self.row is not None and tag in ('td', 'th'):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.row.append(''.join(self.cell).strip())
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            if len(self.row) >= 2:
                self.rows.append(self.row)
            self.row = None
        elif tag == 'table':
            self.table_depth = max(0, self.table_depth - 1)


def _table_rows(lines):
    rows, indices = [], set()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if '|' not in stripped and '\t' not in line:
            continue
        cells = stripped.strip('|').split('|') if '|' in stripped else stripped.split('\t')
        cells = [cell.strip() for cell in cells]
        if len(cells) < 2:
            continue
        indices.add(i)
        if all(re.fullmatch(r':?-{2,}:?', cell) for cell in cells):
            continue
        rows.append(cells)
    if any('<table' in line.lower() for line in lines):
        parser = _HTMLTable()
        parser.feed('\n'.join(lines))
        rows.extend(parser.rows)
        inside = False
        for i, line in enumerate(lines):
            if '<table' in line.lower():
                inside = True
            if inside:
                indices.add(i)
            if '</table' in line.lower():
                inside = False
    return rows, indices


def _structure(number, text, mechanical):
    lines = _prose_lines(text)
    skip = set()
    active = [i for i, line in enumerate(lines) if line.strip()]
    title = None
    if number in TITLES:
        if active:
            first = active[0]
            # A standalone first line followed by body is recognizable, without
            # a made-up maximum title length. Body/lead meaning is still pending.
            if len(active) > 1:
                title = _plain_heading(lines[first])
                skip.add(first)
                if first + 1 < len(lines) and re.fullmatch(r'\s*(?:=+|-{3,})\s*', lines[first + 1]):
                    skip.add(first + 1)
        _observe(mechanical, 'title', title is not None, 'Separate first title line observed; content/lead requires review.')
    if number == 24:
        _observe(mechanical, 'literal_title', title == 'Crônica ficcional: a meia no recibo',
                 'Exact first title, ignoring only Markdown heading/bold adornment.')
    if number in SECTIONS:
        labels, ordered = SECTIONS[number]
        found = []
        for i, line in enumerate(lines):
            heading = _plain_heading(line)
            for label in labels:
                match = re.fullmatch(re.escape(label) + r'\s*(?::\s*(.*))?', heading, re.IGNORECASE)
                if match:
                    found.append(label)
                    if not match[1]:
                        skip.add(i)
                    else:
                        lines[i] = match[1]
        _observe(mechanical, 'sections', all(found.count(label) == 1 for label in labels),
                 'Recognized section labels: ' + ', '.join(found) + '; each required once.')
        if ordered:
            _observe(mechanical, 'section_order', tuple(found) == labels,
                     'Required label order: ' + ', '.join(labels) + '.')
    rows, table_indices = _table_rows(lines)
    if number in {8, 10, 14, 16}:
        _observe(mechanical, 'table', len(rows) >= 2, 'Pipe/tab table syntax observed; cell meanings not proved.')
        skip.update(table_indices)
    if number == 8:
        measurements = [row for row in rows if any(re.search(r'\d+[.,]\d+', cell) for cell in row)]
        _observe(mechanical, 'measurement_rows', len(measurements) == 3,
                 f'Observed {len(measurements)} numeric measurement rows; requires three.')
    if number == 5:
        calculations = [i for i, line in enumerate(lines) if '=' in line and re.search(r'\d', line)]
        _observe(mechanical, 'calculation_lines', len(calculations) == 2,
                 f'Observed {len(calculations)} separate lines with equation syntax; requires two. Dimensional meaning pending.')
        skip.update(calculations)
    if number in PARAGRAPHS:
        prose = '\n'.join('' if i in skip or re.fullmatch(r'\s*(?:=+|-{3,})\s*', line) else line
                          for i, line in enumerate(lines))
        paragraphs = [p for p in re.split(r'\n\s*\n', prose.strip()) if p.strip()]
        expected = PARAGRAPHS[number]
        _observe(mechanical, 'paragraph_count', len(paragraphs) == expected,
                 f'Observed {len(paragraphs)} blank-line-delimited prose paragraphs; requires {expected}.')
    if number == 12:
        mechanical.append(_entry('paragraph_order', 'pending',
            'Interpretation, alternatives, limits and cautious implication are semantic roles, not required labels.'))
    if number in {20, 23}:
        explicit = any(re.match(r'^\s*#{1,6}\s+', line) or re.match(r'^\s*Título\s*:', line, re.I)
                       or re.fullmatch(r'\s*\*\*[^*]+\*\*\s*', line) for line in lines)
        mechanical.append(_entry('no_headings', 'fail' if explicit else 'pending',
            'Explicit heading syntax found.' if explicit else 'No explicit heading syntax; plain-text title/subtitle intent remains ambiguous.'))
    if number == 2:
        quotes = ('O sensor avisa que o nível subiu; ele não aumenta a capacidade do canal.',
                  'Queremos saber quem recebe o alerta e em quanto tempo age.')
        _observe(mechanical, 'literal_quotes', all(quote in text for quote in quotes),
                 'Both mandatory quote strings must be exact; attribution remains semantic review.')
    if number == 21:
        _observe(mechanical, 'literal_beginning', text.lstrip().startswith('Exemplo fictício para avaliação editorial.'),
                 'Exact editorial warning at start, ignoring leading whitespace only.')
        _observe(mechanical, 'no_hashtags', not re.search(r'(?<!\w)#[\w]+', text), 'Literal hashtag scan, not a check for follower requests.')
    if number == 23:
        _observe(mechanical, 'literal_quote', 'não acerte a hora' in text, 'Exact note phrase required; narrative role pending.')


# Numeric tokens are lexical observations, not a unit or assertion parser.
_NUMBER = re.compile(r'(?<![\w])[-+−]?(?:\d{1,3}(?:[.\u00a0 ]\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)(?:[eE][-+]?\d{1,3})?(?![\w])')
_WORD_NUMBERS = {'duas': '2', 'dois': '2', 'três': '3', 'quatro': '4', 'cinco': '5',
                 'seis': '6', 'oito': '8', 'doze': '12', 'trinta': '30'}


def _numbers(text):
    observations = []
    for match in _NUMBER.finditer(text):
        raw = match[0].replace('−', '-').replace('\u00a0', '').replace(' ', '')
        if len(raw) > 64:
            continue
        if ',' in raw:
            raw = raw.replace('.', '').replace(',', '.')
        elif re.fullmatch(r'[-+]?[1-9]\d{0,2}(?:\.\d{3})+', raw):
            raw = raw.replace('.', '')
        value = Decimal(raw)
        suffix = re.match(r'\s*(mil|milhão|milhões)\b', text[match.end():match.end() + 16], re.I)
        if suffix:
            sign, digits, exponent = value.as_tuple()
            value = Decimal((sign, digits, exponent + (3 if suffix[1].lower() == 'mil' else 6)))
        observations.append((value, match.start(), match.end()))
    return observations


def _reference_results():
    # Independent Decimal calculations from the supplied fixtures. Local context
    # prevents callers' rounding/precision settings changing validation results.
    with localcontext() as context:
        context.prec = 40
        d = Decimal
        energy = d('2.0') * d('10') * d('5.0')
        period = sum(map(d, ('1.20', '1.22', '1.19', '1.21', '1.18'))) / d(5)
        volume = sum(map(d, ('12.40', '12.50', '12.60'))) / d(3)
        upstream = sum(map(d, ('7.1', '7.0', '7.2'))) / d(3)
        downstream = sum(map(d, ('5.9', '6.0', '6.1'))) / d(3)
        defects = d(10000) * d('0.02')
        positive = defects * d('0.90')
        false_positive = (d(10000) - defects) * d('0.05')
        local_cost = d(120000) + d(4000) * d(24)
        cloud_cost = d(6000) * d(24)
        return {
            'energy_initial': energy, 'speed_final': (d(2) * energy / d('2.0')).sqrt(),
            'period_mean': period, 'reaction_quotient': d('0.80') / d('0.40'),
            'volume_mean': volume, 'hcl_concentration': d('0.1000') * (volume / d(1000)) / (d('25.00') / d(1000)),
            'oxygen_upstream_mean': upstream, 'oxygen_downstream_mean': downstream,
            'oxygen_difference': downstream - upstream,
            'gain_a': d(68) - d(50), 'gain_b': d(61) - d(50), 'final_difference': d(68) - d(61),
            'conditional_probability': (positive / (positive + false_positive) * d(100)).quantize(d('0.1'), rounding=ROUND_HALF_UP),
            'installment': d(30000) / d(2), 'cost_local': local_cost, 'cost_cloud': cloud_cost,
            'cost_difference': local_cost - cloud_cost,
            'outage_minutes': (d(14) * d(60) + d(42)) - (d(14) * d(60) + d(10)),
            'tp': positive, 'fn': defects - positive, 'fp': false_positive,
            'tn': d(10000) - defects - false_positive,
        }


_RESULT_MARKERS = {
    5: {'energy_initial': r'\b(?:E_?p|energia potencial(?: inicial)?)\b',
        'speed_final': r'\b(?:rapidez(?: final)?|v)\b'},
    6: {'period_mean': r'\b(?:média|período médio|T_?m)\b'},
    7: {'reaction_quotient': r'\bQ_?c\b'},
    8: {'volume_mean': r'\bvolume médio\b',
        'hcl_concentration': r'(?:\bconcentração(?: média)?(?: de)? HCl\b|\[HCl\]|\bc_?HCl\b)'},
    10: {'oxygen_upstream_mean': r'\b(?:média (?:a |de |do trecho a )?montante|montante[^\d\n;]{0,30}média)\b',
         'oxygen_downstream_mean': r'\b(?:média (?:a |de |do trecho a )?jusante|jusante[^\d\n;]{0,30}média)\b',
         'oxygen_difference': r'\bdiferença\b'},
    11: {'gain_a': r'\bganho (?:do |no )?(?:grupo )?A\b',
         'gain_b': r'\bganho (?:do |no )?(?:grupo )?B\b', 'final_difference': r'\bdiferença(?: final)?\b'},
    12: {'final_difference': r'\bdiferença(?: final)?\b'},
    14: {'conditional_probability': r'180\s*/\s*670|\b(?:percentual|probabilidade|fração|proporção)\b'},
    15: {'installment': r'\bparcela(?:s)?\b'},
    16: {'cost_local': r'\b(?:(?:custo )?total local|local(?=\s*\|))\b',
         'cost_cloud': r'\b(?:(?:custo )?total (?:da )?nuvem|nuvem(?=\s*\|))\b',
         'cost_difference': r'\bdiferença\b'},
    18: {'outage_minutes': r'\b(?:duração|intervalo|indisponibilidade)\b'},
}


def _result_observation(text, marker, expected, name):
    values = []
    ambiguous = False
    for clause in re.split(r'[;\n]|\.(?!\d)', text):
        for match in re.finditer(marker, clause, re.I):
            tail = clause[match.end():match.end() + 240]
            # Do not mistake another result on the same line for this one.
            tail = re.split(r',\s+|\s+enquanto\s+', tail, maxsplit=1)[0]
            for markers in _RESULT_MARKERS.values():
                for next_marker in markers.values():
                    next_match = re.search(next_marker, tail, re.I)
                    if next_match:
                        tail = tail[:next_match.start()]
            # The final equality gives the reported result, not an operand.
            if '=' in tail:
                tail = tail.rsplit('=', 1)[-1]
            numbers = _numbers(tail)
            if numbers:
                values.append(numbers[0][0])
                raw = tail[numbers[0][1]:numbers[0][2]]
                if re.fullmatch(r'[1-9]\d{0,2}\.\d{3}', raw) and Decimal(raw) == expected and numbers[0][0] != expected:
                    ambiguous = True
    status = 'pass' if values and all(value == expected for value in values) else 'fail'
    if ambiguous or not values and text.strip() and (expected in {value for value, _, _ in _numbers(text)} or
            re.search(r'\b(?:cem|dez|sete|dezoito|onze|vinte|trinta|cinquenta|mil|meio)\b', text, re.I)):
        status = 'pending'
    observed = ', '.join(map(str, values)) if values else 'no recognized labeled numeric result'
    return _entry(name, status,
        f'Decimal fixture expected {expected}; observed {observed}. Numeric lexical support only; semantic relationships and units pending.')


# Fixed identifiers/quantities supplied by the prompts. Presence alone cannot
# establish their role, attribution, negation, causal meaning or unit correctness.
_LITERAL_DATA = {
    1: ('Vila Clara', '1200', '6', '12', '2026', 'outubro', 'novembro'),
    2: ('Porto Sereno', '48', '8', '2', '180000', 'Lia Prado', '07/2026'),
    3: ('/v1/jobs', 'Authorization', 'Content-Type', 'Idempotency-Key', 'Retry-After', '80', '201', '400', '401', '409', '429', '60', '24'),
    4: ('collect', 'bucket', 'None'),
    5: ('2', '5', '10'), 6: ('1.20', '1.22', '1.19', '1.21', '1.18'),
    7: ('4', '0.20', '0.80', '0.40'), 8: ('25.00', '0.1000', '12.40', '12.50', '12.60', 'HCl', 'NaOH'),
    9: ('carbon_dioxide',), 10: ('7.1', '7.0', '7.2', '5.9', '6.0', '6.1'),
    11: ('120', '60', '8', '50', '68', '61'), 12: ('120', '60', '8', '50', '68', '61'),
    13: ('30',), 14: ('10000', '2', '90', '5'),
    15: ('Estúdio Boreal', '30000', '600', '6', '2'), 16: ('24', '120000', '4000', '6000'),
    17: ('Marina', 'Paula', '9', '5', '7', '13', '2', 'outubro'),
    18: ('Painel Aurora', '14h10', '14h42', 'UTC-3', 'outubro', '2026', '12h'),
    20: ('2',), 21: ('28', '35', '12', '3', '30', '18', '4'),
    22: ('salt',), 23: ('não acerte a hora',), 24: ('Crônica ficcional: a meia no recibo',),
}


def _factual(number, text, factual):
    numeric = {value for value, _, _ in _numbers(text)}
    numeric.update(Decimal(value) for word, value in _WORD_NUMBERS.items() if re.search(r'\b' + word + r'\b', text, re.I))
    missing = []
    for literal in _LITERAL_DATA.get(number, ()):
        if re.fullmatch(r'\d+(?:\.\d+)?', literal):
            present = Decimal(literal) in numeric
        elif literal == 'carbon_dioxide':
            present = bool(re.search(r'CO[2₂]|dióxido de carbono|gás carbônico', text, re.I))
        else:
            present = literal.casefold() in text.casefold()
        if not present:
            missing.append(literal)
    if number in _LITERAL_DATA:
        factual.append(_entry('literal_data', 'pass' if not missing else ('pending' if text.strip() else 'fail'),
            'Supplied lexical data scan; unrecognized: ' + (', '.join(missing) or 'none') + '. Alternative wording/format may require review; does not establish semantic fidelity or units.'))
    else:
        factual.append(_entry('literal_data', 'pending', 'No mandatory factual numeric/literal payload; argument fidelity requires semantic review.'))
    references = _reference_results()
    for name, marker in _RESULT_MARKERS.get(number, {}).items():
        evidence = text
        if number == 16 and name in ('cost_local', 'cost_cloud'):
            rows, _ = _table_rows(_prose_lines(text))
            if rows:
                column = next((i for i, cell in enumerate(rows[0]) if 'total' in cell.casefold()), None)
                label = 'local' if name == 'cost_local' else 'nuvem'
                matched = [row[column] for row in rows[1:] if column is not None and len(row) > column and row[0].casefold() == label]
                if matched:
                    evidence = '\n'.join('Total ' + label + ': ' + value for value in matched)
        entry = _result_observation(evidence, marker, references[name], name)
        if number == 18 and not re.search(marker, text, re.I):
            interval = re.search(r'\b14(?:h|:)10\b[^\n]{0,40}\b14(?:h|:)42\b', text)
            if interval:
                entry = _entry(name, 'pass', f'Decimal fixture expected {references[name]}; supplied 14:10/14:42 interval observed. Timestamp lexical support only; semantic roles and units pending.')
        factual.append(entry)
    if number == 6:
        _observe(factual, 'instrument_uncertainty', bool(re.search(r'(?:±|\+\s*/\s*-)\s*0[.,]02\b', text)),
                 'Literal supplied uncertainty ±0.02; provenance and confidence-interval meaning need semantic review.')
    if number == 14:
        rows, _ = _table_rows(_prose_lines(text))
        observed = _conditional_cells(rows)
        expected = [references[k] for k in ('tp', 'fn', 'fp', 'tn')]
        status = 'pass' if observed == expected else ('pending' if rows and observed is None else 'fail')
        factual.append(_entry('conditional_counts', status,
                 f'Decimal 2x2 fixture {list(map(str, expected))}; recognized cells {observed}. Table syntax/labels only, semantic interpretation pending.'))


def _conditional_cells(rows):
    def defect(label):
        label = label.casefold()
        return None if 'defeit' not in label else not bool(re.search(r'\b(?:sem|não)\b', label))
    def signal(label):
        label = label.casefold()
        return None if 'sinal' not in label else not bool(re.search(r'\b(?:sem|não)\b', label))
    if len(rows) < 3:
        return None
    for column_axis, row_axis, transpose in ((signal, defect, False), (defect, signal, True)):
        columns = {column_axis(cell): i for i, cell in enumerate(rows[0][1:], 1) if column_axis(cell) is not None}
        if set(columns) != {False, True}:
            continue
        cells = {}
        for row in rows[1:]:
            category = row_axis(row[0])
            if category is None:
                continue
            for key, column in columns.items():
                values = _numbers(row[column]) if len(row) > column else []
                if len(values) == 1:
                    cells[(key, category) if transpose else (category, key)] = values[0][0]
        if len(cells) == 4:
            return [cells[key] for key in ((True, True), (True, False), (False, True), (False, False))]
        return []
    return None


MAX_TEXT = 100000
MAX_CODE = 20000
MAX_AST_NODES = 2000


def _blocks(text):
    blocks, current, body = [], None, []
    for line in text.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if current is None and marker:
            current = (marker[1], marker[2].strip().lower())
            body = []
        elif current is not None:
            if marker and marker[1][0] == current[0][0] and len(marker[1]) >= len(current[0]) and not marker[2].strip():
                blocks.append((current[1], '\n'.join(body)))
                current = None
            else:
                body.append(line)
    return blocks, current is None


def _is_name(node, name):
    return isinstance(node, ast.Name) and node.id == name


def _none(node):
    return isinstance(node, ast.Constant) and node.value is None


def _empty_list(node):
    return isinstance(node, ast.List) and not node.elts or (
        isinstance(node, ast.Call) and _is_name(node.func, 'list') and not node.args and not node.keywords)


def _safe_ast(tree):
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.If,
        ast.Compare, ast.Is, ast.IsNot, ast.Eq, ast.NotEq, ast.Name, ast.Load,
        ast.Store, ast.Constant, ast.List, ast.Return, ast.Expr, ast.Call,
        ast.Attribute, ast.Assign, ast.Assert, ast.UnaryOp, ast.Not,
        ast.keyword, ast.BoolOp, ast.And, ast.Or, ast.Tuple)
    nodes = list(ast.walk(tree))
    if len(nodes) > MAX_AST_NODES:
        return False
    for node in nodes:
        if not isinstance(node, allowed):
            return False
        if isinstance(node, ast.FunctionDef) and (node.name != 'collect' or node.decorator_list or node.returns is not None):
            return False
        if isinstance(node, ast.Name) and node.id.startswith('__'):
            return False
        if isinstance(node, ast.Attribute) and not (_is_name(node.value, 'bucket') and node.attr == 'append'):
            return False
        if isinstance(node, ast.Constant) and (isinstance(node.value, str) and len(node.value) > 1024 or
                                              isinstance(node.value, int) and node.value.bit_length() > 64):
            return False
        if isinstance(node, ast.Assign) and any(not isinstance(target, ast.Name) for target in node.targets):
            return False
        if isinstance(node, ast.Call):
            if _is_name(node.func, 'collect'):
                if not 1 <= len(node.args) <= 2 or any(keyword.arg != 'bucket' for keyword in node.keywords):
                    return False
            elif _is_name(node.func, 'list'):
                if node.args or node.keywords:
                    return False
            elif isinstance(node.func, ast.Attribute):
                if len(node.args) != 1 or node.keywords:
                    return False
            else:
                return False
    return True


def _correct_collect(function):
    args = function.args
    if [arg.arg for arg in args.posonlyargs + args.args] != ['item', 'bucket'] or args.kwonlyargs or args.vararg or args.kwarg:
        return False
    if len(args.defaults) != 1 or not _none(args.defaults[0]):
        return False
    body = function.body
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if len(body) != 3 or not isinstance(body[0], ast.If):
        return False
    guard, append, returned = body
    test = guard.test
    if not (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is)
            and len(test.comparators) == 1 and ((_is_name(test.left, 'bucket') and _none(test.comparators[0])) or
                                                (_none(test.left) and _is_name(test.comparators[0], 'bucket')))):
        return False
    if guard.orelse or len(guard.body) != 1:
        return False
    assignment = guard.body[0]
    if not (isinstance(assignment, ast.Assign) and len(assignment.targets) == 1 and
            _is_name(assignment.targets[0], 'bucket') and _empty_list(assignment.value)):
        return False
    call = append.value if isinstance(append, ast.Expr) else None
    return bool(isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and
                _is_name(call.func.value, 'bucket') and call.func.attr == 'append' and
                len(call.args) == 1 and _is_name(call.args[0], 'item') and not call.keywords and
                isinstance(returned, ast.Return) and _is_name(returned.value, 'bucket'))


def _assert_shapes(trees):
    # Resolve AST assignment aliases, never Python values or candidate bytecode.
    aliases, independent, identity = {}, set(), False
    def resolve(node):
        seen = set()
        while isinstance(node, ast.Name) and node.id in aliases and node.id not in seen:
            seen.add(node.id)
            node = aliases[node.id]
        return node
    for tree in trees:
        for statement in tree.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        aliases[target.id] = resolve(statement.value)
            if not isinstance(statement, ast.Assert):
                continue
            for comparison in ast.walk(statement.test):
                if not isinstance(comparison, ast.Compare) or len(comparison.ops) != 1 or len(comparison.comparators) != 1:
                    continue
                for raw_call, raw_other in ((comparison.left, comparison.comparators[0]),
                                            (comparison.comparators[0], comparison.left)):
                    call, other = resolve(raw_call), resolve(raw_other)
                    if not isinstance(call, ast.Call) or not _is_name(call.func, 'collect') or not call.args:
                        continue
                    bucket = call.args[1] if len(call.args) == 2 else next((k.value for k in call.keywords if k.arg == 'bucket'), None)
                    if isinstance(comparison.ops[0], ast.Eq) and (bucket is None or _none(bucket)) and isinstance(other, ast.List) and len(other.elts) == 1:
                        if ast.dump(call.args[0]) == ast.dump(other.elts[0]):
                            independent.add(id(call))
                    if isinstance(comparison.ops[0], ast.Is) and bucket is not None and isinstance(raw_other, ast.Name):
                        if resolve(bucket) is other and isinstance(other, ast.List):
                            identity = True
    return len(independent) >= 2, identity


def _python(text, mechanical):
    blocks, closed = _blocks(text)
    code = [body for language, body in blocks if language in ('python', 'py', 'python3') or
            not language and re.search(r'\bdef collect\s*\(', body)]
    if not blocks and re.match(r'\s*def collect\s*\(', text):
        code = [textwrap.dedent(text)]
    trees, syntax, subset = [], bool(code) and closed, bool(code) and closed
    for body in code:
        if len(body) > MAX_CODE:
            syntax = subset = False
            continue
        try:
            tree = ast.parse(body)
        except (SyntaxError, ValueError, RecursionError):
            syntax = subset = False
            continue
        trees.append(tree)
        subset = subset and _safe_ast(tree)
    functions = [node for tree in trees for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'collect']
    correction = syntax and subset and any(_correct_collect(function) for function in functions)
    correction_status = 'pass' if correction else 'fail'
    if syntax and subset and not correction and functions:
        # Other pure implementations may be valid. Refuse to equate absence of
        # one canonical shape with a runtime failure; obvious violations fail.
        alternatives = [f for f in functions if len(f.args.defaults) == 1 and _none(f.args.defaults[0])]
        if alternatives and all(not any(isinstance(n, ast.Return) and isinstance(n.value, ast.List) or
                                       isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.Not) and _is_name(n.operand, 'bucket') or
                                       isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or)
                                       for n in ast.walk(f)) for f in alternatives):
            correction_status = 'pending'
    independent, identity = _assert_shapes(trees) if syntax and subset else (False, False)
    _observe(mechanical, 'python_syntax', syntax, 'Bounded ast.parse of Python data only; no execution.')
    _observe(mechanical, 'python_safe_subset', subset, 'Restricted pure collect AST, no imports, arbitrary calls, loops, decorators or comprehensions; not an OS sandbox.')
    mechanical.append(_entry('python_correction', correction_status, 'Recognized None guard, fresh allocation, append(item), return same bucket. Static shape only; unrecognized pure implementations require review.'))
    _observe(mechanical, 'independent_asserts', independent, 'Two distinct default-call equality assertion ASTs observed; assertions not executed.')
    _observe(mechanical, 'identity_assert', identity, 'Explicit caller-list identity assertion AST observed; assertion not executed.')
    mechanical.append(_entry('python_runtime', 'pending',
        'No verified network-isolating sandbox provided. Candidate Python never executed on host or subprocess; runtime behavior pending.'))


def _strict_json(text):
    def pairs(items):
        output = {}
        for key, value in items:
            if key in output:
                raise ValueError('duplicate JSON key')
            output[key] = value
        return output
    def invalid_constant(value):
        raise ValueError('nonstandard JSON constant')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def _curl_parse(command):
    if len(command) > MAX_CODE:
        raise ValueError('curl bound')
    lexer = shlex.shlex(command.replace('\\\n', ''), posix=True, punctuation_chars=';&|<>')
    lexer.whitespace_split = True
    tokens = list(lexer)
    if not tokens or tokens.pop(0) != 'curl':
        raise ValueError('not curl')
    headers, data, urls, method = {}, None, [], None
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in (';', '&&', '&', '|', '||', '<', '>', '>>') or '$(' in token or '`' in token:
            raise ValueError('shell syntax unsupported')
        value = None
        if token.startswith('--') and '=' in token:
            token, value = token.split('=', 1)
        elif token.startswith('-H') and token != '-H':
            token, value = '-H', token[2:]
        elif token.startswith('-X') and token != '-X':
            token, value = '-X', token[2:]
        if token in ('-X', '--request', '-H', '--header', '-d', '--data', '--data-raw', '--data-binary', '--url'):
            if value is None:
                i += 1
                if i >= len(tokens):
                    raise ValueError('missing curl option value')
                value = tokens[i]
            if token in ('-X', '--request'):
                method = value
            elif token in ('-H', '--header'):
                if ':' not in value:
                    raise ValueError('header syntax')
                key, header_value = value.split(':', 1)
                key = key.strip().lower()
                if key in headers:
                    raise ValueError('duplicate header')
                headers[key] = header_value.strip()
            elif token == '--url':
                urls.append(value)
            else:
                if data is not None or value.startswith('@'):
                    raise ValueError('data must be single literal JSON')
                data = _strict_json(value)
        elif token in ('-s', '--silent', '-S', '--show-error', '-i', '--include', '--fail', '--fail-with-body'):
            pass
        elif token.startswith('https://'):
            urls.append(token)
        else:
            raise ValueError('unsupported curl syntax')
        i += 1
    dummy = headers.get('authorization') in ('Bearer <TOKEN>', 'Bearer ***')
    contract = (urls == ['https://api.example.com/v1/jobs'] and (method or ('POST' if data is not None else 'GET')) == 'POST'
                and headers.get('content-type', '').lower() == 'application/json' and dummy and data == {'name': 'backup'})
    return contract, dummy


def _api(text, mechanical):
    blocks, closed = _blocks(text)
    commands = [body for language, body in blocks if re.match(r'\s*curl\b', body)]
    if not commands:
        match = re.search(r'(?m)^\s*curl\b.*(?:\\\n[^\n]*)*', text)
        if match:
            commands = [match[0]]
    syntax, contract, dummy = bool(commands) and closed, bool(commands) and closed, bool(commands) and closed
    for command in commands:
        try:
            good, fake = _curl_parse(command)
        except (ValueError, RecursionError):
            syntax = contract = dummy = False
        else:
            contract = contract and good
            dummy = dummy and fake
    _observe(mechanical, 'curl_syntax', syntax, 'shlex literal parsing only; curl never executed. Unsupported shell constructions rejected.')
    _observe(mechanical, 'curl_contract', contract, 'Parsed POST URL, literal JSON body and required headers; not full API semantics or delivery.')
    _observe(mechanical, 'dummy_token', dummy, 'Only <TOKEN> or *** dummy bearer placeholders accepted. Token values never included in diagnostics.')
    json_blocks = [body for language, body in blocks if language == 'json']
    examples, json_ok = [], closed
    for body in json_blocks:
        try:
            if len(body) > MAX_CODE:
                raise ValueError('JSON bound')
            examples.append(_strict_json(body))
        except (ValueError, RecursionError):
            json_ok = False
    if not json_blocks:
        # Bounded inline JSON objects are another valid format, not a required
        # code-fence convention. Reject duplicate keys/NaN just as for fences.
        for match in list(re.finditer(r'\{', text))[:64]:
            fragment = text[match.start():match.start() + MAX_CODE]
            try:
                _, end = json.JSONDecoder().raw_decode(fragment)
                examples.append(_strict_json(fragment[:end]))
            except (ValueError, RecursionError):
                if re.match(r'\{\s*"(?:id|status)"\s*:', fragment):
                    json_ok = False
                continue
    _observe(mechanical, 'json_syntax', json_ok and bool(examples), 'Strict example JSON parsing, including duplicate-key/non-finite rejection; no execution.')
    _observe(mechanical, 'success_json', json_ok and any(example == {'id': 'job_123', 'status': 'queued'} for example in examples),
             'Success example exact id/status payload parsed; queued meaning needs semantic review.')


def validate(case, text):
    """Return JSON-safe observations, accepting an exact case ID or case mapping.

    Whitespace tokens include titles and code. For case 22 word_count remains
    the observed whole-output count; the speech-only bound cannot be resolved
    without inventing a format absent from the prompt and is therefore pending.
    """
    approved = _approved(case)
    if not isinstance(text, str):
        raise TypeError('candidate text must be a string')
    identifier = approved['id']
    count = len(text.split())
    mechanical, factual = [], []
    _observe(mechanical, 'nonempty', bool(text.strip()), 'Non-whitespace output required.')
    _observe(mechanical, 'no_long_dash', '\u2014' not in text,
             'Literal U+2014 scan; no stylistic or semantic inference.')
    low, high = BOUNDS[identifier]
    if identifier == '22-roteiro-hash':
        mechanical.append(_entry('word_count', 'pending',
            f'Speech requires {low} to {high} words; observed total {count}. Speech separation unspecified.'))
        mechanical.append(_entry('visual_cues', 'pending',
            'Exactly three separate visual cues requested; their syntax is unspecified.'))
        mechanical.append(_entry('duration', 'pending',
            '45 to 60 seconds requires timing a delivery, not counting text.'))
    else:
        _observe(mechanical, 'word_count', low <= count <= high,
                 f'Observed {count} whitespace tokens; inclusive bounds {low} to {high}, including title/code.')
    number = int(identifier[:2])
    _observe(mechanical, 'resource_limit', len(text) <= MAX_TEXT,
             f'At most {MAX_TEXT} characters analyzed; full whitespace count always observed.')
    sample = text if len(text) <= MAX_TEXT else ''
    _structure(number, sample, mechanical)
    _factual(number, sample, factual)
    if number == 4:
        _python(sample, mechanical)
    if number == 3:
        _api(sample, mechanical)
    if len(text) > MAX_TEXT:
        for entry in mechanical + factual:
            if entry['name'] not in {'word_count', 'nonempty', 'no_long_dash', 'resource_limit'}:
                entry['status'] = 'pending'
                entry['detail'] = 'Not analyzed: resource bound exceeded.'
    return {'word_count': count, 'mechanical': mechanical,
            'factual_support': factual, 'semantic_review': 'pending'}
