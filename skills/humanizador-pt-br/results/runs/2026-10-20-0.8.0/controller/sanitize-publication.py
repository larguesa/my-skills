#!/usr/bin/env python3
"""Sanitização em memória antes da projeção. Não escreve na fonte nem usa rede.

Adapta sanitize-publication.py de 0.7.0. A rederivação e a atestação ficam
em publish.py; este módulo nunca sanitiza uma publicação já selada.
"""
import base64
import json
import re

REDACTED = '[REDACTED_PRIVATE_METADATA]'
PRIVATE_KEYS = {'user_id', 'account_id', 'organization_id', 'authorization',
                'proxy_authorization', 'cookie', 'set_cookie', 'api_key',
                'access_token', 'refresh_token', 'email', 'user_email',
                'account_email', 'key_hash'}
CREDENTIAL = re.compile(rb'(?:sk-or-v1-|sk-proj-|gh[pousr]_)[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._~-]{16,}', re.I)
ACCOUNT = re.compile(rb'\b(?:user|acct|org)_[A-Za-z0-9]{16,}\b')

def keyname(key):
    return key.lower().replace('-', '_')


def sanitize_bytes(data):
    """Troca só spans de metadados e body_base64, preservando demais lexemas.

    Não reserializa números nem strings de textos/escores. Corpos não JSON
    ficam intactos e passam pelo scanner. Nunca mascara prosa arbitrária.
    """
    text = data.decode('utf-8')
    decoder = json.JSONDecoder()
    removed = []
    edits = []

    def whitespace(i):
        while i < len(text) and text[i] in ' \r\n\t':
            i += 1
        return i

    def private_strings(value):
        if isinstance(value, str) and value and value != REDACTED:
            removed.append(value)
        elif isinstance(value, dict):
            for item in value.values():
                private_strings(item)
        elif isinstance(value, list):
            for item in value:
                private_strings(item)

    def walk(i):
        i = whitespace(i)
        if text[i] == '{':
            i = whitespace(i + 1)
            while text[i] != '}':
                key, end = decoder.raw_decode(text, i)
                i = whitespace(end)
                if text[i] != ':':
                    raise ValueError('objeto JSON inválido')
                start = whitespace(i + 1)
                value, end = decoder.raw_decode(text, start)
                if keyname(key) in PRIVATE_KEYS:
                    if value != REDACTED:
                        private_strings(value)
                        edits.append((start, end, json.dumps(REDACTED)))
                elif key == 'body_base64' and isinstance(value, str):
                    body = base64.b64decode(value, validate=True)
                    try:
                        json.loads(body)
                    except (ValueError, UnicodeDecodeError):
                        pass
                    else:
                        clean, identifiers = sanitize_bytes(body)
                        removed.extend(identifiers)
                        if clean != body:
                            edits.append((start, end, json.dumps(base64.b64encode(clean).decode('ascii'))))
                else:
                    walk(start)
                i = whitespace(end)
                if text[i] == ',':
                    i = whitespace(i + 1)
                elif text[i] != '}':
                    raise ValueError('separador JSON inválido')
            return i + 1
        if text[i] == '[':
            i = whitespace(i + 1)
            while text[i] != ']':
                i = whitespace(walk(i))
                if text[i] == ',':
                    i = whitespace(i + 1)
                elif text[i] != ']':
                    raise ValueError('lista JSON inválida')
            return i + 1
        return decoder.raw_decode(text, i)[1]

    json.loads(text)
    walk(0)
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text.encode('utf-8'), removed


def scan(data, removed=()):
    """Falha fechada, sem imprimir conteúdos nem identificadores removidos."""
    if CREDENTIAL.search(data) or ACCOUNT.search(data):
        raise ValueError('padrão privado na projeção')
    if any(value.encode('utf-8') in data for value in removed if value):
        raise ValueError('metadado privado reaparece na projeção')
    try:
        parsed = json.loads(data)
    except (ValueError, UnicodeDecodeError):
        return
    def inspect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                spending_authorization = (key == 'authorization' and isinstance(item, dict)
                                          and set(item) == {'decision', 'thread_id', 'scope'})
                if keyname(key) in PRIVATE_KEYS and item != REDACTED and not spending_authorization:
                    raise ValueError('metadado de conta não sanitizado')
                if key == 'body_base64' and isinstance(item, str):
                    scan(base64.b64decode(item, validate=True), removed)
                else:
                    inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
        elif isinstance(value, str):
            raw = value.encode('utf-8')
            if CREDENTIAL.search(raw) or ACCOUNT.search(raw) or any(v.encode() in raw for v in removed if v):
                raise ValueError('conteúdo privado em string JSON')
    inspect(parsed)

if __name__ == '__main__':
    raise SystemExit('Módulo somente em memória. Use publish.py --help; não altera evidência existente.')
