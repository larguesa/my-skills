#!/usr/bin/env python3
"""Auxílio local à redação e revisão em PT-BR, sobre rascunhos ou originais.

Não gera prosa, consulta fontes ou identifica autoria. Use a skill para redigir;
este script inspeciona o texto produzido e aplica apenas edições aprovadas.
"""
import hashlib
import unicodedata
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
    protected = None
    for edit in edits:
        if not isinstance(edit, dict) or edit.get('approved') is not True:
            raise ValueError('Toda edição exige approved: true explícito.')
        start, end = edit.get('start'), edit.get('end')
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError('Offsets inválidos; use índices Unicode, fim exclusivo.')
        if edit.get('original') != text[start:end] or not isinstance(edit.get('replacement'), str):
            raise ValueError('Trecho original divergente ou substituição inválida.')
        if edit['replacement'] != edit['original']:
            if protected is None:
                protected = protected_spans(text, protected_terms)
            if any(start < s['end'] and end > s['start'] for s in protected):
                raise ValueError('Edição toca conteúdo protegido; mantenha o trecho.')
            if protected_spans(edit['replacement'], protected_terms):
                raise ValueError('Substituição introduz conteúdo protegido novo.')
        validated.append(edit)
    validated.sort(key=lambda e: e['start'])
    if any(a['end'] > b['start'] for a, b in zip(validated, validated[1:])):
        raise ValueError('Edições sobrepostas.')
    for edit in reversed(validated):
        text = text[:edit['start']] + edit['replacement'] + text[edit['end']:]
    if protected is None:
        protected = protected_spans(original_text, protected_terms)
    inventories = [Counter((s['kind'], value[s['start']:s['end']]) for s in spans)
                   for value, spans in ((original_text, protected), (text, protected_spans(text, protected_terms)))]
    if inventories[0] != inventories[1]:
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


def _search_text(value):
    """Normalização só para consulta; valores retornados permanecem intactos."""
    if isinstance(value, dict):
        value = ' '.join(_search_text(v) for v in value.values())
    elif isinstance(value, (list, tuple)):
        value = ' '.join(_search_text(v) for v in value)
    return ''.join(c for c in unicodedata.normalize('NFD', str(value).casefold())
                   if not unicodedata.combining(c))


def search_catalog(rules, query='', genre=None, limit=10):
    """Busca id, nome e orientação editorial; ordem do catálogo preservada."""
    fields = ('id', 'name', 'suggestion', 'instruction', 'instructions', 'context',
              'pattern', 'avoid', 'positive_example', 'negative_example', 'exceptions')
    return _search_entries(rules, fields, query, genre, limit)


def _search_entries(entries, fields, query, genre, limit):
    if type(limit) is not int or limit <= 0:
        raise ValueError('limit deve ser inteiro positivo.')
    needle = _search_text(query)
    return [entry for entry in entries
            if (genre is None or genre in entry.get('genres', []))
            and needle in _search_text([entry.get(field, '') for field in fields])][:limit]


def search_styles(query='', genre=None, limit=10):
    """Busca perfis por id, nome e instruções, sem acento/case na consulta."""
    fields = ('id', 'name', 'instruction', 'instructions', 'adjustments', 'avoid')
    return _search_entries(load_profiles().values(), fields, query, genre, limit)


def generate_structure(profile='neutro-claro', genre=None, breadth=3, randomness=0, seed=None):
    """Plano de instruções locais; breadth limita só blocos opcionais."""
    data = json.loads((REFERENCES / 'estilos.json').read_bytes().decode('utf-8'))
    if type(breadth) is not int or breadth < 0:
        raise ValueError('breadth deve ser inteiro não negativo.')
    if type(randomness) not in (int, float) or not 0 <= randomness <= 1:
        raise ValueError('randomness deve ser número finito entre 0 e 1.')
    if seed is not None and type(seed) is not int:
        raise ValueError('seed deve ser inteiro ou None.')
    profiles = load_profiles()
    if not isinstance(profile, str) or profile not in profiles:
        raise ValueError('Perfil desconhecido.')
    guidance = profiles[profile]
    if genre is not None and genre not in guidance['genres']:
        raise ValueError('Gênero incompatível com o perfil; use um de: ' + ', '.join(guidance['genres']))
    raw = data.get('structures')
    ids = guidance.get('structure_ids')
    if not isinstance(raw, list) or not raw or not isinstance(ids, list) or not ids:
        raise ValueError('Estilos precisam de structures e structure_ids não vazios.')
    structures = {}
    for item in raw:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str) or not item['id'] or item['id'] in structures:
            raise ValueError('Estrutura precisa de id único não vazio.')
        if not isinstance(item.get('genres'), list) or not item['genres'] or not all(isinstance(g, str) and g for g in item['genres']):
            raise ValueError('Estrutura precisa de genres não vazios.')
        blocks = item.get('blocks')
        if not isinstance(blocks, list) or not blocks:
            raise ValueError('Estrutura precisa de blocks não vazios.')
        seen = set()
        for block in blocks:
            if not isinstance(block, dict) or not isinstance(block.get('id'), str) or not block['id'] or block['id'] in seen:
                raise ValueError('Bloco precisa de id único não vazio.')
            seen.add(block['id'])
            if type(block.get('required')) is not bool:
                raise ValueError('Bloco precisa de required: true/false explícito.')
            if not isinstance(block.get('instruction'), str) or not block['instruction'].strip():
                raise ValueError('Bloco precisa de instruction não vazia.')
            alternatives = block.get('alternatives', [])
            if not isinstance(alternatives, list) or not all(isinstance(a, str) and a.strip() for a in alternatives):
                raise ValueError('alternatives deve ser lista de instruções não vazias.')
        structures[item['id']] = item
    if not all(isinstance(sid, str) and sid in structures for sid in ids):
        raise ValueError('structure_ids contém estrutura desconhecida.')
    candidates = [structures[sid] for sid in guidance['structure_ids']
                  if (genre in structures[sid]['genres'] if genre is not None
                      else any(g in structures[sid]['genres'] for g in guidance['genres']))]
    if not candidates:
        raise ValueError('Nenhuma estrutura compatível com o perfil e gênero.')
    structure = candidates[0]
    selected_genre = genre if genre is not None else next(g for g in guidance['genres'] if g in structure['genres'])
    rng = random.Random(seed)
    optional = [i for i, block in enumerate(structure['blocks']) if not block['required']]
    count = min(breadth, len(optional))
    optional = (rng.sample(optional, count) if randomness and rng.random() < randomness
                else optional[:count])
    blocks = []
    for i, block in enumerate(structure['blocks']):
        if not block['required'] and i not in optional:
            continue
        instruction = block['instruction']
        if not block['required'] and randomness and block.get('alternatives') and rng.random() < randomness:
            instruction = rng.choice([instruction] + block['alternatives'])
        blocks.append({'id': block['id'], 'required': block['required'], 'instruction': instruction})
    return {'kind': 'structure_plan', 'profile': profile, 'genre': selected_genre,
            'structure_id': structure['id'], 'breadth': breadth, 'randomness': randomness,
            'seed': seed, 'blocks': blocks,
            'semantics': {'breadth_unit': 'optional_blocks',
                          'optional_blocks_selected': len(optional),
                          'required_blocks_preserved': True,
                          'breadth': 'Máximo de blocos opcionais (uma instrução selecionada por bloco); todos os obrigatórios permanecem, na ordem do catálogo.',
                          'randomness': 'Probabilidade de sortear o subconjunto opcional e, independentemente por bloco opcional, uma instrução uniforme entre a principal e alternativas locais; zero usa as primeiras opções. A estrutura é sempre a primeira compatível; nunca reordena blocos nem troca instruções obrigatórias.',
                          'seed': 'Gerador random.Random local; mesma configuração, controles e seed reproduzem o plano, sem alterar o gerador global.'},
            'aviso': 'Plano editorial local: não gera prosa nem fatos. Preencher apenas com o briefing e fontes disponíveis.'}


def _word_character(character):
    return character.isalnum() or character == '_' or unicodedata.category(character).startswith('M')


def plan_replacements(text, from_text, to_text, protected_terms=()):
    """Plano literal sensível a maiúsculas; nenhuma edição é aprovada."""
    if not isinstance(text, str) or not isinstance(from_text, str) or not from_text:
        raise ValueError('Entrada e --from devem ser textos; --from não pode ser vazio.')
    if not isinstance(to_text, str):
        raise ValueError('--to deve ser texto, inclusive vazio.')
    protected_terms = list(protected_terms)
    pattern = re.escape(from_text)
    protected = protected_spans(text, protected_terms)
    edits = []
    for match in re.finditer(pattern, text):
        if (_word_character(from_text[0]) and match.start() > 0 and _word_character(text[match.start() - 1])) or (_word_character(from_text[-1]) and match.end() < len(text) and _word_character(text[match.end()])):
            continue
        if from_text == to_text or any(match.start() < span['end'] and match.end() > span['start'] for span in protected):
            continue
        edit = {'start': match.start(), 'end': match.end(), 'original': match.group(),
                'replacement': to_text, 'rule_id': 'literal-replacement', 'approved': True}
        try:
            apply_edits(text, {'input_sha256': sha256(text), 'edits': edits + [edit]}, protected_terms)
        except ValueError:
            continue
        edits.append(edit)
    for edit in edits:
        edit['approved'] = False
    return {'kind': 'replacement_plan', 'input_sha256': sha256(text),
            'from_text': from_text, 'to_text': to_text, 'case_sensitive': True,
            'protected_terms': list(protected_terms), 'edits': edits,
            'semantic_review_needed': bool(edits),
            'aviso': 'Plano literal sensível a maiúsculas, com limites de palavra Unicode nas extremidades alfanuméricas, sublinhados e marcas combinantes; omite trechos protegidos e mudanças rejeitadas por apply_edits. Exige aprovação por trecho e revisão de sentido. Não escreve arquivos.'}


def rhythm(text):
    """Contagens descritivas de ritmo; nunca um score ou detector."""
    if not isinstance(text, str):
        raise ValueError('rhythm exige texto Unicode.')
    paragraphs = [p.strip() for p in re.split(r'(?:\r?\n)[ \t]*(?:\r?\n)+', text)
                  if re.search(r'\w', p)]
    sentences = [s.strip() for p in paragraphs for s in re.split(r'[!?\r\n]+|(?<!\d)\.|\.(?!\d)', p)
                 if re.search(r'\w', s)]
    tokens = [re.findall(r'\w+', s) for s in sentences]
    openings = Counter(' '.join(words[:2]).casefold() for words in tokens)
    return {'input_sha256': sha256(text), 'sentence_count': len(sentences),
            'paragraph_count': len(paragraphs),
            'sentence_word_lengths': [len(words) for words in tokens],
            'sentence_character_lengths': [len(s) for s in sentences],
            'paragraph_word_lengths': [len(re.findall(r'\w+', p)) for p in paragraphs],
            'paragraph_character_lengths': [len(p) for p in paragraphs],
            'repeated_openings': [{'opening': opening, 'count': count}
                                  for opening, count in sorted(openings.items()) if count > 1],
            'semantics': r'Contagem aproximada: palavras são tokens Unicode \w+; parágrafos são separados por linhas em branco; frases por .!? ou quebra de linha (pontos entre dígitos não separam frases); aberturas são os dois primeiros tokens, sem distinção de maiúsculas. Comprimentos em caracteres excluem separadores e espaços externos. Abreviações, citações e código exigem interpretação humana.',
            'aviso': 'Descrição editorial de ritmo, sem score ou limiar: não identifica autoria nem comprova defeito. Repetições podem ser intencionais.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Auxílio à redação e revisão: inspeciona rascunhos ou originais, sem gerar texto, verificar fontes ou detectar autoria.')
    commands = parser.add_subparsers(dest='command', required=True)
    for command, description in [('audit', 'Diagnosticar sem alterar'), ('suggest', 'Propor trechos não aprovados'), ('apply', 'Aplicar somente trechos aprovados'), ('verify', 'Comparar versões e pedir revisão semântica'), ('replace', 'Planejar substituições literais não aprovadas'), ('rhythm', 'Descrever frases, parágrafos e aberturas repetidas')]:
        sub = commands.add_parser(command, help=description)
        sub.add_argument('input', type=Path, help='Rascunho recém-redigido ou original recebido, em UTF-8')
        if command != 'rhythm':
            sub.add_argument('--protect', action='append', default=[], help='Termo protegido; pode repetir. Unidades não são inferidas: use --protect kg ou --protect reais.')
        if command in ('audit', 'suggest'):
            sub.add_argument('--catalog', type=Path, default=Path(__file__).resolve().parents[1] / 'references/catalogo.json', help='Catálogo JSON externo')
        if command == 'suggest':
            sub.add_argument('--seed', type=int, default=0, help='Semente para variantes sutis')
            sub.add_argument('--profile', default='neutro-claro', help='Perfil editorial')
        if command == 'apply':
            sub.add_argument('--plan', type=Path, required=True, help='JSON com input_sha256 e edits aprovadas')
            sub.add_argument('--output', type=Path, required=True, help='Novo arquivo, nunca sobrescrever')
        if command == 'replace':
            sub.add_argument('--from', dest='from_text', required=True, help='Texto literal sensível a maiúsculas')
            sub.add_argument('--to', dest='to_text', required=True, help='Substituição literal, inclusive vazia')
        if command == 'verify':
            sub.add_argument('revised', type=Path, help='Versão revisada UTF-8')
    for command, description in [('catalog', 'Buscar regras editoriais locais'), ('styles', 'Buscar perfis editoriais locais')]:
        sub = commands.add_parser(command, help=description)
        sub.add_argument('--query', default='', help='Texto no id, nome, expressões ou instruções; ignora acentos e maiúsculas')
        sub.add_argument('--genre', help='Gênero exato; filtro estrito')
        sub.add_argument('--limit', type=int, default=10, help='Máximo de resultados; inteiro positivo')
    sub = commands.add_parser('structure', help='Planejar estrutura, nunca gerar prosa ou fatos')
    sub.add_argument('--profile', default='neutro-claro')
    sub.add_argument('--genre', help='Gênero exato compatível com o perfil e estrutura')
    sub.add_argument('--breadth', type=int, default=3, help='Máximo de blocos opcionais; obrigatórios sempre preservados')
    sub.add_argument('--randomness', type=float, default=0, help='Probabilidade [0,1] de variar opções editoriais locais')
    sub.add_argument('--seed', type=int, help='Semente local reproduzível')
    args = parser.parse_args(argv)
    try:
        if args.command == 'structure':
            result = generate_structure(args.profile, args.genre, args.breadth, args.randomness, args.seed)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command in ('catalog', 'styles'):
            result = (search_catalog(load_catalog(REFERENCES / 'catalogo.json'), args.query, args.genre, args.limit)
                      if args.command == 'catalog' else search_styles(args.query, args.genre, args.limit))
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        text = args.input.read_bytes().decode('utf-8')
        if args.command == 'rhythm':
            result = rhythm(text)
        elif args.command == 'replace':
            result = plan_replacements(text, args.from_text, args.to_text, args.protect)
        elif args.command == 'audit':
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
