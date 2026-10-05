#!/usr/bin/env python3
"""Auxílio local à redação e revisão em PT-BR, sobre rascunhos ou originais.

Não gera prosa, consulta fontes ou identifica autoria. Use a skill para redigir;
este script inspeciona o texto produzido e aplica apenas edições aprovadas.
"""
import hashlib
import re
import random
import difflib
import argparse
import json
from pathlib import Path
import sys
from collections import Counter


def verify(original, revised, protected_terms=()):
    """Compara texto e inventário protegido, sem alegar equivalência semântica."""
    differences = []
    for tag, a, b, c, d in difflib.SequenceMatcher(None, original, revised, autojunk=False).get_opcodes():
        if tag != 'equal':
            differences.append({'operation': tag, 'original_start': a, 'original_end': b, 'revised_start': c, 'revised_end': d, 'original': original[a:b], 'revised': revised[c:d]})
    inventories = [Counter((s['kind'], text[s['start']:s['end']]) for s in protected_spans(text, protected_terms)) for text in (original, revised)]
    return {'input_sha256': sha256(original), 'output_sha256': sha256(revised), 'unchanged': original == revised, 'semantic_review_needed': original != revised, 'protected_content_preserved': inventories[0] == inventories[1], 'differences': differences, 'aviso': 'A comparação mecânica não garante fidelidade semântica. Toda alteração exige revisão humana de fatos, intenção e contexto.'}

REFERENCES = Path(__file__).resolve().parents[1] / 'references'


def load_profiles(path=None):
    data = json.loads(Path(path or REFERENCES / 'estilos.json').read_bytes().decode('utf-8'))
    return {profile['id']: profile for profile in data['profiles']}


def suggest(text, rules, seed=0, profile='neutro-claro', protected_terms=()):
    """Escolhe poucas alternativas já previstas no perfil, sem aprová-las."""
    profiles = load_profiles()
    if profile not in profiles:
        raise ValueError('Perfil desconhecido.')
    report = audit(text, rules, protected_terms)
    rng = random.Random(seed)
    edits = []
    for finding in report['findings']:
        rule = finding['metadata']
        if profile not in rule.get('profiles', profiles):
            continue
        variants = rule.get('variants', {}).get(profile, [rule.get('replacement')])
        options = [v for v in variants if isinstance(v, str) and v != finding['original']]
        if not options:
            continue
        edit = {k: finding[k] for k in ('start', 'end', 'original', 'rule_id')}
        edit.update(replacement=rng.choice(options), approved=True)
        try:
            apply_edits(text, {'input_sha256': report['input_sha256'], 'edits': edits + [edit]}, protected_terms)
        except ValueError:
            continue
        edits.append(edit)
        if len(edits) >= 2:
            break
    for edit in edits:
        edit['approved'] = False
    # ponytail: sortear só uma ênfase do perfil; ampliar apenas com novas opções revisadas.
    style_focus = rng.choice(profiles[profile]['adjustments'])
    return {'input_sha256': report['input_sha256'], 'profile': profile, 'profile_guidance': profiles[profile], 'style_focus': style_focus, 'protected_terms': list(protected_terms), 'seed': seed, 'edits': edits, 'recommendations': report['findings'], 'semantic_review_needed': bool(edits), 'aviso': 'Sugestões exigem aprovação por trecho e revisão humana de sentido; manter o original é válido.'}


def sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def protected_spans(text, protected_terms=()):
    """Bloqueio heurístico conservador, não reconhecimento completo de entidades."""
    patterns = {
        'número': r'[+−-]?\d+(?:[.,:/%-]\d+)*(?:[^\S\r\n]*%)?',
        'URL': r'(?:https?://|www\.)[^\s<>]+',
        'código': r'```[\s\S]*?(?:```|\Z)|~~~[\s\S]*?(?:~~~|\Z)|`[^`\n]*(?:`|$)',
        'citação': r'“[^”]*(?:”|\Z)|"[^"]*(?:"|\Z)|‘[^’]*(?:’|\Z)|\x27[^\x27\n]*\x27|(?m:^\s*>[^\n]*)',
        'negação/condição': r'(?i:\b(?:não|nunca|jamais|nem|sem|se|caso|desde que|contanto que|a menos que|exceto|salvo|somente se|apenas se)\b)',
    }
    spans = []
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            start, end = match.span()
            if kind == 'negação/condição':
                # Conservar a oração inteira evita inverter seu alcance.
                boundaries = [m.start() for m in re.finditer(r'[!?\n]|(?<!\d)\.|\.(?!\d)', text)]
                start = max((p for p in boundaries if p < start), default=-1) + 1
                end = min((p for p in boundaries if p >= end), default=len(text))
            spans.append({'start': start, 'end': end, 'kind': kind})
    for match in re.finditer(r'\b\w+\b', text):
        if any(c.isupper() for c in match.group()):
            spans.append({'start': match.start(), 'end': match.end(), 'kind': 'possível nome'})
    for term in protected_terms:
        if not isinstance(term, str) or not term:
            raise ValueError('Termos protegidos devem ser textos não vazios.')
        spans.extend({'start': m.start(), 'end': m.end(), 'kind': 'termo do usuário'} for m in re.finditer(re.escape(term), text, re.I))
    return sorted(spans, key=lambda s: (s['start'], s['end']))


def apply_edits(text, plan, protected_terms=()):
    if not isinstance(plan, dict) or plan.get('input_sha256') != sha256(text):
        raise ValueError('SHA256 divergente: plano não pertence à entrada.')
    stored_terms = plan.get('protected_terms', [])
    if not isinstance(stored_terms, list):
        raise ValueError('protected_terms deve ser lista.')
    protected_terms = list(protected_terms) + stored_terms
    original_text = text
    edits = plan.get('edits')
    if not isinstance(edits, list):
        raise ValueError('edits deve ser uma lista.')
    validated = []
    for edit in edits:
        if not isinstance(edit, dict) or edit.get('approved') is not True:
            raise ValueError('Toda edição exige approved: true explícito.')
        start, end = edit.get('start'), edit.get('end')
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError('Offsets inválidos; use índices Unicode, fim exclusivo.')
        if edit.get('original') != text[start:end] or not isinstance(edit.get('replacement'), str):
            raise ValueError('Trecho original divergente ou substituição inválida.')
        if edit['replacement'] != edit['original']:
            if any(start < s['end'] and end > s['start'] for s in protected_spans(text, protected_terms)):
                raise ValueError('Edição toca conteúdo protegido; mantenha o trecho.')
            if protected_spans(edit['replacement'], protected_terms):
                raise ValueError('Substituição introduz conteúdo protegido novo.')
        validated.append(edit)
    validated.sort(key=lambda e: e['start'])
    if any(a['end'] > b['start'] for a, b in zip(validated, validated[1:])):
        raise ValueError('Edições sobrepostas.')
    for edit in reversed(validated):
        text = text[:edit['start']] + edit['replacement'] + text[edit['end']:]
    if not verify(original_text, text, protected_terms)['protected_content_preserved']:
        raise ValueError('Edições alteram o inventário protegido ou seus limites.')
    return text


def audit(text, rules, protected_terms=()):
    words = len(re.findall(r'\w+', text))
    protected = protected_spans(text, protected_terms)
    repeated = Counter()
    for sentence in re.split(r'[.!?\n;]+', text):
        tokens = re.findall(r'\w+', sentence.casefold())
        for size in (2, 3, 4):
            repeated.update(' '.join(tokens[i:i + size]) for i in range(len(tokens) - size + 1))
    phrases = [{'phrase': phrase, 'count': count, 'per_1000_words': round(count * 1000 / words, 3)} for phrase, count in sorted(repeated.items()) if count > 1]
    findings, counts = [], {}
    for rule in rules:
        matches = list(re.finditer(re.escape(rule['pattern']) if rule.get('pattern_type') == 'literal' else rule['pattern'], text, re.IGNORECASE))
        counts[rule['id']] = {'count': len(matches), 'per_1000_words': round(len(matches) * 1000 / words, 3) if words else None}
        for match in matches:
            findings.append({'rule_id': rule['id'], 'start': match.start(), 'end': match.end(), 'original': match.group(), 'suggestion': rule.get('suggestion'), 'metadata': rule, 'protected': any(match.start() < s['end'] and match.end() > s['start'] for s in protected)})
    return {'input_sha256': sha256(text), 'word_count': words, 'findings': findings, 'rule_counts': counts, 'repeated_phrases': phrases, 'protected_spans': protected, 'aviso': 'Diagnóstico editorial contextual; não identifica autoria nem comprova defeito. Repetições podem ser intencionais.'}


def load_catalog(path):
    data = json.loads(Path(path).read_bytes().decode('utf-8'))
    rules = data.get('rules') if isinstance(data, dict) else data
    if not isinstance(rules, list):
        raise ValueError('Catálogo deve ser lista ou objeto com rules.')
    seen = set()
    for rule in rules:
        if not isinstance(rule, dict) or not isinstance(rule.get('id'), str) or not rule['id'] or rule['id'] in seen:
            raise ValueError('Regra sem id único válido.')
        seen.add(rule['id'])
        pattern = rule.get('pattern')
        if not isinstance(pattern, str) or not pattern or len(pattern) > 4096:
            raise ValueError('Padrão deve conter de 1 a 4096 caracteres.')
        if rule.get('pattern_type', 'regex') not in ('regex', 'literal'):
            raise ValueError('pattern_type deve ser regex ou literal.')
        try:
            compiled = re.compile(re.escape(pattern) if rule.get('pattern_type') == 'literal' else pattern, re.I)
        except re.error as error:
            raise ValueError(f'Regex inválida: {error}') from error
        if compiled.search(''):
            raise ValueError('Padrão não pode corresponder ao texto vazio.')
    return rules


def main(argv=None):
    parser = argparse.ArgumentParser(description='Auxílio à redação e revisão: inspeciona rascunhos ou originais, sem gerar texto, verificar fontes ou detectar autoria.')
    commands = parser.add_subparsers(dest='command', required=True)
    for command, description in [('audit', 'Diagnosticar sem alterar'), ('suggest', 'Propor trechos não aprovados'), ('apply', 'Aplicar somente trechos aprovados'), ('verify', 'Comparar versões e pedir revisão semântica')]:
        sub = commands.add_parser(command, help=description)
        sub.add_argument('input', type=Path, help='Rascunho recém-redigido ou original recebido, em UTF-8')
        sub.add_argument('--protect', action='append', default=[], help='Termo protegido; pode repetir. Unidades não são inferidas: use --protect kg ou --protect reais.')
        if command in ('audit', 'suggest'):
            sub.add_argument('--catalog', type=Path, default=Path(__file__).resolve().parents[1] / 'references/catalogo.json', help='Catálogo JSON externo')
        if command == 'suggest':
            sub.add_argument('--seed', type=int, default=0, help='Semente para variantes sutis')
            sub.add_argument('--profile', default='neutro-claro', help='Perfil editorial')
        if command == 'apply':
            sub.add_argument('--plan', type=Path, required=True, help='JSON com input_sha256 e edits aprovadas')
            sub.add_argument('--output', type=Path, required=True, help='Novo arquivo, nunca sobrescrever')
        if command == 'verify':
            sub.add_argument('revised', type=Path, help='Versão revisada UTF-8')
    args = parser.parse_args(argv)
    try:
        text = args.input.read_bytes().decode('utf-8')
        if args.command == 'audit':
            result = audit(text, load_catalog(args.catalog), args.protect)
        elif args.command == 'suggest':
            result = suggest(text, load_catalog(args.catalog), args.seed, args.profile, args.protect)
        elif args.command == 'verify':
            result = verify(text, args.revised.read_bytes().decode('utf-8'), args.protect)
        else:
            plan = json.loads(args.plan.read_bytes().decode('utf-8'))
            revised = apply_edits(text, plan, args.protect)
            result = verify(text, revised, args.protect)
            with args.output.open('xb') as output:
                output.write(revised.encode('utf-8'))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
