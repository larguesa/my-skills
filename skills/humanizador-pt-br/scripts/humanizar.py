#!/usr/bin/env python3
"""Auxílio local à redação e revisão em PT-BR, sobre rascunhos ou originais.

Não gera prosa, consulta fontes ou identifica autoria. Use a skill para redigir;
este script prepara o briefing editorial, inspeciona o texto produzido e aplica
apenas edições aprovadas.
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
VERSION = '0.8.1'


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


FENCE_OPEN = re.compile(r'(?m)^[ \t]{0,3}(`{3,}|~{3,})(.*)$')
BACKTICKS = re.compile(r'`+')
PARAGRAPH_BREAK = re.compile(r'\n[ \t]*\r?\n')
QUOTE_CLOSERS = {'“': '”', '«': '»', '‘': '’', '"': '"', "'": "'"}
BLOCKQUOTE = re.compile(r'(?m)^[ \t]*>[^\n]*')


def literal_spans(text):
    """Código Markdown e citações, num só reconhecedor para edição, comparação e entrega.

    Cerca fecha com o mesmo caractere e comprimento igual ou maior; crases inline fecham
    com sequência do mesmo tamanho; aspas fecham no mesmo parágrafo (aspas retas simples,
    na mesma linha, sem confundir apóstrofo). closed=False marca trecho aberto: a edição o
    protege de forma conservadora, mas a entrega não o trata como literal.
    """
    spans, gaps, position = [], [], 0
    while True:
        opening = FENCE_OPEN.search(text, position)
        while opening and opening.group(1)[0] == '`' and '`' in opening.group(2):
            opening = FENCE_OPEN.search(text, opening.end() + 1)  # crases na linha: código inline
        if not opening:
            break
        marker = opening.group(1)
        closer = re.compile(r'(?m)^[ \t]{0,3}' + re.escape(marker[0]) + '{%d,}[ \t]*\r?$' % len(marker))
        closing = closer.search(text, opening.end())
        gaps.append((position, opening.start()))
        end = closing.end() if closing else len(text)
        spans.append({'start': opening.start(), 'end': end, 'kind': 'código', 'closed': bool(closing)})
        position = end
        if not closing:
            break
    gaps.append((position, len(text)))
    for start, stop in gaps:
        _inline_literals(text, start, stop, spans)
        for match in BLOCKQUOTE.finditer(text, start, stop):
            spans.append({'start': match.start(), 'end': match.end(), 'kind': 'citação', 'closed': True})
    return sorted(spans, key=lambda s: (s['start'], s['end']))


def _inline_literals(text, start, stop, spans):
    i = start
    while i < stop:
        character = text[i]
        brk = PARAGRAPH_BREAK.search(text, i, stop)
        paragraph_end = brk.start() if brk else stop
        line_end = text.find('\n', i, stop)
        line_end = stop if line_end < 0 else line_end
        if character == '`':
            size = len(BACKTICKS.match(text, i).group())
            closing = next((m for m in BACKTICKS.finditer(text, i + size, paragraph_end) if len(m.group()) == size), None)
            if closing:
                spans.append({'start': i, 'end': closing.end(), 'kind': 'código', 'closed': True})
                i = closing.end()
            else:
                spans.append({'start': i, 'end': line_end, 'kind': 'código', 'closed': False})
                i += size
            continue
        if character in QUOTE_CLOSERS and not (character in '"\'' and i > 0 and _word_character(text[i - 1])):
            closer, limit, k = QUOTE_CLOSERS[character], (line_end if character == "'" else paragraph_end), i + 1
            while True:
                k = text.find(closer, k, limit)
                if k < 0 or closer not in '’\'' or k + 1 >= len(text) or not _word_character(text[k + 1]):
                    break
                k += 1  # apóstrofo dentro da palavra, como em d’água
            closed = k >= 0
            spans.append({'start': i, 'end': k + 1 if closed else limit, 'kind': 'citação', 'closed': closed})
            i = k + 1 if closed else i + 1
            continue
        i += 1


def _folded(text):
    """Texto sem acentos e em minúsculas, com o índice original de cada caractere (NFC ou NFD)."""
    chars, index = [], []
    for i, character in enumerate(text):
        for base in unicodedata.normalize('NFD', character):
            if not unicodedata.combining(base):
                for folded in base.casefold():
                    chars.append(folded)
                    index.append(i)
    return ''.join(chars), index


NEGATION = re.compile(r'\b(?:nao|nunca|jamais|nem|sem|se|caso|desde que|contanto que|a menos que|exceto|salvo|somente se|apenas se)\b')
ABBREVIATION = re.compile(r'(?i)(?<!\w)(?:sr|sra|srta|dr|dra|prof|profa|av|p|ex|etc|art|inc|ltda|cia|pág|vol|cap|fig|obs|aprox|jr)$')


def _boundaries(text, literals):
    """Fins de oração: ponto de abreviação, ponto decimal e pontuação dentro de literal não contam."""
    marks = []
    for match in re.finditer(r'[!?\n]|(?<!\d)\.|\.(?!\d)', text):
        p = match.start()
        if text[p] == '.' and ABBREVIATION.search(text, max(0, p - 6), p):
            continue
        if not any(s['start'] <= p < s['end'] for s in literals):
            marks.append(p)
    return marks


def protected_spans(text, protected_terms=()):
    """Bloqueio heurístico conservador, não reconhecimento completo de entidades."""
    patterns = {
        'número': r'[+−-]?\d+(?:[.,:/%-]\d+)*[ºª°]?(?:[^\S\r\n]*%)?',
        'URL': r'(?:https?://|www\.)[^\s<>]+',
    }
    spans = []
    for kind, pattern in patterns.items():
        spans.extend({'start': m.start(), 'end': m.end(), 'kind': kind} for m in re.finditer(pattern, text))
    literals = literal_spans(text)
    spans.extend({'start': s['start'], 'end': s['end'], 'kind': s['kind']} for s in literals)
    folded, index = _folded(text)
    boundaries = None
    for match in NEGATION.finditer(folded):
        start, end = index[match.start()], index[match.end() - 1] + 1
        if boundaries is None:
            boundaries = _boundaries(text, literals)
        # Conservar a oração inteira evita inverter seu alcance.
        start = max((p for p in boundaries if p < start), default=-1) + 1
        end = min((p for p in boundaries if p >= end), default=len(text))
        spans.append({'start': start, 'end': end, 'kind': 'negação/condição'})
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


DELIVERY = [
    'Responda somente com o artefato pedido: sem preâmbulo ("Aqui está"), bastidores, nota ao solicitante ou oferta final. Comandos, JSON ou plano só quando o pedido exigir esse formato.',
    'Estes retornos já foram calculados pela skill: não repita comandos nem chamadas de ferramenta.',
    'Prosa sem travessão (U+2014) e sem traço substituto (meia-risca ou hífen entre espaços): use ponto, vírgula, dois-pontos ou parênteses; diálogo novo vai entre aspas.',
    'Norma culta e acentuação em todos os perfis, inclusive coloquial, informal e caricato.',
    'Redação: frases próprias, com fatos, citações e termos exatos do pedido. Revisão: só vício, clareza ou precisão, '
    'no escopo pedido; não troque a voz nem a estrutura que funciona. Diagnóstico: trecho, motivo e prioridade, '
    'sem versão nova.',
    'Antes de entregar, leia como o leitor: o gênero está completo? Tudo o que o pedido fixa continua igual?',
    'Termine quando uma nova revisão não trouxer melhoria concreta.',
]


def brief(profile='neutro-claro', genre=None, breadth=2, randomness=0, seed=None, rules=None):
    """Ofício do gênero, plano, perfil e catálogo inteiro em instruções curtas, sem gerar prosa."""
    plan = generate_structure(profile, genre, breadth, randomness, seed)
    data = json.loads((REFERENCES / 'estilos.json').read_bytes().decode('utf-8'))
    guidance = load_profiles()[profile]
    rules = load_catalog(REFERENCES / 'catalogo.json') if rules is None else rules
    structure = next(s for s in data['structures'] if s['id'] == plan['structure_id'])
    focus = structure.get('focus', [])
    if not set(focus) <= {r['id'] for r in rules}:
        raise ValueError('focus cita regra ausente do catálogo.')
    material = structure.get('material', 'fatos')
    # O material do gênero é só o padrão: o tipo pedido (fato, opinião ou ficção) prevalece.
    types = data.get('material_types', {})
    alternatives = [kind['when_requested'] for key, kind in types.items() if key != material]
    # positive/negative_example seguem a polaridade do detector; aqui recebem o papel editorial.
    compact = [{'id': r['id'], 'name': r.get('name', ''), 'foco': r['id'] in focus,
                'evite': r.get('positive_example'), 'prefira': r.get('negative_example'),
                'como': r.get('suggestion'), 'termos': r.get('avoid', []),
                'excecoes': r.get('exceptions', [])} for r in rules]
    return {'kind': 'writing_brief', 'version': VERSION, 'profile': profile, 'genre': plan['genre'],
            'genre_name': structure.get('name', plan['genre']), 'structure_id': plan['structure_id'],
            'breadth': breadth, 'randomness': randomness, 'seed': seed,
            'craft': structure.get('craft', []), 'material': material,
            'material_label': types.get(material, {}).get('label', material),
            'material_policy': data.get('material', {}).get(material, ''),
            'material_alternatives': alternatives,
            'adjustments': guidance['adjustments'], 'avoid': guidance.get('avoid', []),
            'plan': plan['blocks'], 'voice_invariants': data.get('voice_invariants', []),
            'forbidden': data.get('forbidden', []), 'focus': focus, 'rules': compact,
            'delivery': DELIVERY}


def brief_text(data):
    """Ofício primeiro, contrato de entrega por último, perto do pedido."""
    lines = [f"Briefing editorial humanizador-pt-br {data['version']}: perfil {data['profile']}, "
             f"gênero {data['genre']}, estrutura {data['structure_id']}.", '']
    if data['craft']:
        lines += [f"Ofício do gênero: {data['genre_name']}"] + [f'- {item}' for item in data['craft']] + ['']
    lines.append('Plano: funções do texto, não seções nem parágrafos obrigatórios. Funda, divida ou reordene '
                 'quando o gênero pedir e não use os nomes dos blocos como títulos.')
    lines += [f"{i}. {b['id']}, {'obrigatório' if b['required'] else 'opcional'}: {b['instruction']}"
              for i, b in enumerate(data['plan'], 1)]
    lines += ['', f"Perfil {data['profile']}", 'Faça: ' + '; '.join(data['adjustments']) + '.']
    if data['avoid']:
        lines.append('Evite: ' + '; '.join(data['avoid']) + '.')
    lines.append('')
    if data['material_policy']:
        lines += ['Material: o tipo de texto pedido (fato, opinião ou ficção) prevalece.',
                  f"- Padrão do gênero, {data['material_label']}. {data['material_policy']}"]
        lines += [f'- {item}' for item in data['material_alternatives']]
    # voice_invariants seguem no JSON; no texto, a seção Fidelidade da SKILL.md já os declara.
    lines += ['Nunca: ' + '; '.join(data['forbidden']) + '.', '']
    by_id = {r['id']: r for r in data['rules']}

    def salvo(r):
        return ' Salvo: ' + ' '.join(r['excecoes']) if r['excecoes'] else ''
    if data['focus']:
        lines.append('Pontos de atenção do gênero (a forma preferida só retira o vício)')
        for r in (by_id[rule_id] for rule_id in data['focus']):
            line = f"- {r['id']} {r['name']}. Evite: \"{' '.join(r['evite'].split())}\" Prefira: \"{r['prefira']}\""
            if r['termos']:
                line += ' Termos: ' + '; '.join(r['termos']) + '.'
            if r['como']:
                line += ' Como: ' + r['como']
            lines.append(line + salvo(r))
        lines.append('')
    others = [r for r in data['rules'] if not r['foco']]
    lines.append(f'Demais regras do catálogo ({len(others)}): evite os termos, salvo citação, código, '
                 'termo técnico, uso pedido ou exceção da regra')
    for r in others:
        lines.append(f"- {r['id']} {r['name']}: " + '; '.join(r['termos'] or [r['evite']]) + '.' + salvo(r))
    lines += ['', 'Entrega'] + [f'- {item}' for item in data['delivery']]
    return '\n'.join(lines) + '\n'


TOOL_BLOCK = re.compile(r'<tool_call>[\s\S]*?(?:</tool_call>|\Z)|<invoke\b[\s\S]*?(?:</invoke>|\Z)', re.I)
TOOL_MARKUP = re.compile(r'</?tool_call>|<function=|</?invoke\b|"tool_calls"\s*:', re.I)
COMMAND_LINE = re.compile(r'(?m)^[ \t]*(?:\$[ \t]*)?(?:python3?|cd|bash|sh|zsh|ls|cat|pip3?|npm|npx|node|git|curl|wget'
                          r'|docker|make|sudo|echo|export|mkdir|rm|cp|mv|chmod|grep|sed|awk|apt(?:-get)?|brew|yarn|pnpm'
                          r'|pytest|uv)(?:[ \t][^\n]*)?$')
SKILL_COMMAND = re.compile(r'\bhumanizar\.py\b')
WEEKDAY = r'(?:(?:segunda|ter[cç]a|quarta|quinta|sexta)(?:-feira)?|s[aá]bado|domingo)'
RELATIVE_DATE = re.compile(
    r'(?i)\b(?:(?:nesta|neste|nessa|nesse|esta|este|essa|esse|pr[oó]xim[oa]|[uú]ltim[oa]|passad[oa])[ \t]+' + WEEKDAY
    + r'|(?:na|no)[ \t]+' + WEEKDAY + r'(?![ \t]+(?:etapa|vers[aã]o|fase|linha|s[eé]rie|vez|parte|edi[cç][aã]o|chamada'
    r'|rodada|op[cç][aã]o|tentativa|semana|colocad[oa]|posi[cç][aã]o)\b)'
    r'|(?:segunda|ter[cç]a|quarta|quinta|sexta)-feira|s[aá]bado|domingo|hoje|ontem|amanh[aã]|anteontem'
    r'|(?:n?est|n?ess)[ae][ \t]+(?:semana|manh[aã]|tarde|noite)|semana[ \t]+(?:que[ \t]+vem|passada)'
    r'|(?:pr[oó]xima|[uú]ltima)[ \t]+semana)\b')
NUMBER = re.compile(r'(?<![\w.,])[+−-]?\d+(?:[.,]\d+)*(?:[ºª°]|[^\S\r\n]?%)?')
ARTIFACTS = ('prosa', 'codigo')
COURTESY_LINE = re.compile(r'(?i)^[ \t]*[*_]*(?:claro|certo|perfeito|pronto|ok|beleza|ótimo|com certeza|certamente'
                           r'|sem problemas|entendido)[!.,]*[*_]*[ \t]*\r?$')
# Anúncio do próprio artefato ao solicitante. "Seguem os documentos:" pode pertencer à mensagem.
PREAMBLE_OBJECT = re.compile(r'(?i)^[\W_]*(?:(?:claro|certo|perfeito|pronto|com certeza)\W+)?(?:aqui\b|(?:seguem?|abaixo'
                             r'(?:[ \t]+(?:está|estão|segue|seguem))?)[\W_]*:|.*\b(?:revisad|reescrit|corrigid|ajustad'
                             r'|solicitad|pedid)|.*\b(?:texto|versão|versões|resposta|rascunho|sugestão|sugestões|revisão'
                             r'|revisões|notícia|matéria|reportagem|reportagens|artigo|post|roteiro|conto|crônica|ensaio'
                             r'|redação|explicação|comunicado)s?\b)')


def _normalized(value):
    return ' '.join(unicodedata.normalize('NFC', value).split())


def _number(value):
    return re.sub(r'\s+', '', value).replace('−', '-')


def _blank(text, spans):
    chars = list(text)
    for span in spans:
        chars[span['start']:span['end']] = ' ' * (span['end'] - span['start'])
    return ''.join(chars)


def _dash_origin(text, position, closed, sources, original):
    """Motivo pelo qual um travessão é conteúdo original, ou None se for prosa produzida."""
    around = [s for s in closed if s['start'] <= position < s['end']]
    if any(s['kind'] == 'código' for s in around):
        return 'código'
    found = [_normalized(s) for s in sources]
    for span in (s for s in around if s['kind'] == 'citação'):
        body = text[span['start']:span['end']]
        body = re.sub(r'^[ \t]*>', '', body) if body.lstrip().startswith('>') else body[1:-1]
        if _normalized(body) and any(_normalized(body) in source for source in found):
            return 'citação conferida na fonte'
    left, right = position, position + 1
    while left > 0 and not text[left - 1].isspace():
        left -= 1
    while right < len(text) and not text[right].isspace():
        right += 1
    token = text[left:right].strip('.,;:!?()[]“”"«»‘’\'')
    if re.search(r'\w—\w', token) and any(token in source for source in found):
        return 'dado literal conferido na fonte'
    if original is not None:
        marks = _boundaries(text, closed)
        start = max((p for p in marks if p < position), default=-1) + 1
        end = min((p for p in marks if p > position), default=len(text))
        if _normalized(text[start:end]) and _normalized(text[start:end]) in _normalized(original):
            return 'trecho mantido do original'
    return None


def check(text, rules, briefing=None, artifact='prosa', original=None):
    """Verificação final da entrega; alertas exigem leitura, não provam defeito.

    artifact='codigo' é contrato explícito do pedido (só código, comando ou JSON):
    o texto inteiro vale como literal. O padrão é prosa; a intenção não é adivinhada.
    original é o texto do usuário numa revisão: frase mantida dele conserva o travessão.
    """
    blocking, review = [], []

    def item(target, code, match=None, **extra):
        entry = {'code': code}
        if match is not None:
            entry.update(start=match.start(), end=match.end(), original=match.group())
        entry.update(extra)
        target.append(entry)

    if artifact not in ARTIFACTS:
        raise ValueError('artifact deve ser prosa ou codigo.')
    if not text.strip():
        item(blocking, 'texto_vazio')
    # Só trechos fechados contam como literais: marcação crua ou aberta continua bloqueando.
    literals = literal_spans(text)
    closed = ([{'start': 0, 'end': len(text), 'kind': 'código', 'closed': True}] if artifact == 'codigo'
              else [s for s in literals if s['closed']])
    code = [s for s in closed if s['kind'] == 'código']

    def inside(match, spans=closed):
        return any(s['start'] <= match.start() and match.end() <= s['end'] for s in spans)
    for match in TOOL_MARKUP.finditer(text):
        if inside(match):
            item(review, 'chamada_de_ferramenta_literal', match)
        else:
            item(blocking, 'chamada_de_ferramenta', match)
    # Comando em bloco de código fechado é documentação; comando da própria skill nunca é o artefato.
    had_commands = bool(TOOL_MARKUP.search(text) or COMMAND_LINE.search(_blank(text, code))
                        or SKILL_COMMAND.search(text))
    prose = COMMAND_LINE.sub(' ', TOOL_BLOCK.sub(' ', _blank(text, [s for s in literals if s['kind'] == 'código'])))
    if artifact == 'prosa' and had_commands and len(re.findall(r'[^\W\d_]{2,}', prose)) < 8:
        item(blocking, 'saida_somente_comandos', message='A resposta traz comandos em vez do artefato pedido.')
    if artifact == 'prosa' and text.strip()[:1] in '{[':
        try:
            structured = isinstance(json.loads(text), (dict, list))
        except ValueError:
            structured = False
        if structured:
            item(blocking, 'saida_somente_json', message='A resposta é JSON em vez do artefato pedido.')
    sources = [s for s in (briefing, original) if s is not None]
    for match in re.finditer('—', text):
        reason = 'código' if artifact == 'codigo' else _dash_origin(text, match.start(), closed, sources, original)
        if reason:
            item(review, 'travessao_protegido', match, motivo=reason)
        else:
            item(blocking, 'travessao', match)
    lines = [m for m in re.finditer(r'[^\n]*', text) if m.group().strip()]
    opening = next((m for m in lines if not COURTESY_LINE.match(m.group())), None)
    for finding in audit(text, rules)['findings'] if text else []:
        if finding['rule_id'] == 'PTBR-21':
            continue
        entry = {k: finding[k] for k in ('rule_id', 'start', 'end', 'original', 'protected')}
        if (finding['rule_id'] == 'PTBR-27' and opening and finding['start'] <= opening.end()
                and PREAMBLE_OBJECT.match(finding['original'].strip())):
            blocking.append(dict(entry, code='preambulo_de_entrega'))
        elif artifact == 'prosa':
            review.append(dict(entry, code='catalogo', suggestion=finding['suggestion']))
    if briefing is not None:
        source = {_number(m.group()) for m in NUMBER.finditer(briefing)}
        numbers = [m for m in NUMBER.finditer(text) if not inside(m, code)]
        produced = {_number(m.group()) for m in numbers}
        seen = set()
        for match in numbers:
            if _number(match.group()) not in source and _number(match.group()) not in seen:
                seen.add(_number(match.group()))
                item(review, 'acrescimo_numerico', match)
        for match in NUMBER.finditer(briefing):
            if _number(match.group()) not in produced and _number(match.group()) not in seen:
                seen.add(_number(match.group()))
                item(review, 'omissao_numerica', match, source='briefing')
        known = _search_text(briefing)
        for match in RELATIVE_DATE.finditer(text):
            expression = re.sub(r'^n[ao]\s+', '', _search_text(match.group()))
            if not re.search(r'(?<!\w)' + re.escape(expression) + r'(?!\w)', known):
                item(review, 'data_inferida', match)
    return {'kind': 'delivery_check', 'version': VERSION, 'artifact': artifact, 'input_sha256': sha256(text),
            'briefing_sha256': sha256(briefing) if briefing is not None else None,
            'original_sha256': sha256(original) if original is not None else None,
            'deliverable': not blocking, 'blocking': blocking, 'review': review,
            'aviso': 'Verificação mecânica da entrega: não prova fidelidade, qualidade nem autoria. Leia cada alerta no contexto; omissões e números podem ser legítimos.'}


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
    sub = commands.add_parser('brief', help='Briefing compacto antes de redigir: perfil, plano e catálogo inteiro')
    sub.add_argument('--profile', default='neutro-claro')
    sub.add_argument('--genre', help='Gênero exato compatível com o perfil e estrutura')
    sub.add_argument('--breadth', type=int, default=2, help='Máximo de blocos opcionais; obrigatórios sempre preservados')
    sub.add_argument('--randomness', type=float, default=0, help='Probabilidade [0,1] de variar opções editoriais locais')
    sub.add_argument('--seed', type=int, help='Semente local reproduzível')
    sub.add_argument('--format', choices=('texto', 'json'), default='texto', help='texto para leitura do redator; json para ferramentas')
    sub = commands.add_parser('check', help='Verificar a entrega final; código 1 indica bloqueio')
    sub.add_argument('input', type=Path, help='Texto final em UTF-8')
    sub.add_argument('--briefing', type=Path, help='Pedido ou briefing em UTF-8, para comparar números e datas')
    sub.add_argument('--original', type=Path, help='Texto do usuário numa revisão: frase mantida conserva o travessão')
    sub.add_argument('--catalog', type=Path, default=REFERENCES / 'catalogo.json', help='Catálogo JSON externo')
    sub.add_argument('--artifact', choices=ARTIFACTS, default='prosa',
                     help='codigo somente quando o pedido exige explicitamente código, comando ou JSON')
    args = parser.parse_args(argv)
    try:
        if args.command == 'brief':
            data = brief(args.profile, args.genre, args.breadth, args.randomness, args.seed)
            print(brief_text(data) if args.format == 'texto' else json.dumps(data, ensure_ascii=False, indent=2), end='' if args.format == 'texto' else '\n')
            return 0
        if args.command == 'check':
            briefing = args.briefing.read_bytes().decode('utf-8') if args.briefing else None
            original = args.original.read_bytes().decode('utf-8') if args.original else None
            result = check(args.input.read_bytes().decode('utf-8'), load_catalog(args.catalog), briefing,
                           args.artifact, original)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result['deliverable'] else 1
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
