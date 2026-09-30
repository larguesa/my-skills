#!/usr/bin/env python3
"""Historical v1 two-model pilot. Not the new frontier/judge benchmark."""
import random
import re
import json
import os
import argparse
import hashlib
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

NEUTRAL = 'Complete the user task accurately. Follow its requested language and output format.'


def payload(slot, task, route, skill):
    messages = [{'role': 'system', 'content': NEUTRAL}]
    if slot['arm'] == 'skill':
        messages.append({'role': 'system', 'content': skill})
    messages.append({'role': 'user', 'content': task['prompt']})
    result = dict(model=slot['model'], messages=messages, temperature=0,
                  max_tokens=2048, stream=False,
                  provider=dict(only=[route['provider']], allow_fallbacks=False,
                                require_parameters=True))
    if 'reasoning' in route:
        result['reasoning'] = route['reasoning']
    if 'max_price' in route:
        result['provider']['max_price'] = route['max_price']
    return result


def strict_json(text):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('duplicate key')
            out[k] = v
        return out
    def bad_constant(value):
        raise ValueError('nonfinite JSON')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad_constant)


def typed_equal(a, b):
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(typed_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(typed_equal(x, y) for x, y in zip(a, b))
    return a == b


def score(task, text, finish):
    if finish == 'length':
        return dict(status='fail', reason='truncated')
    if not isinstance(text, str) or not text.strip():
        return dict(status='fail', reason='empty_or_refused')
    if 'expected' not in task:
        return dict(status='unscored', reason='human_review_pending')
    try:
        good = typed_equal(strict_json(text), task['expected'])
        return dict(status='pass' if good else 'fail', reason='typed_json_equality')
    except (ValueError, TypeError):
        return dict(status='fail', reason='invalid_json')


def can_spend(used, reserve, limit):
    try:
        used, reserve, limit = map(lambda x: Decimal(str(x)), (used, reserve, limit))
        return all(x.is_finite() and x >= 0 for x in (used, reserve, limit)) and used + reserve <= limit <= 10
    except (InvalidOperation, TypeError, ValueError):
        return False


def append(path, row):
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
        f.flush()
        os.fsync(f.fileno())


def rows(path):
    return [strict_json(line) for line in path.read_text().splitlines()] if path.exists() else []


def started(path):
    return {r['slot'] for r in rows(path)}


def schedule(tasks, routes, seed):
    rng = random.Random(seed)
    blocks = [(t['id'], r['model'], n) for t in tasks for r in routes for n in range(2)]
    rng.shuffle(blocks)
    slots = []
    for task, model, repeat in blocks:
        arms = ['baseline', 'skill']
        rng.shuffle(arms)
        for arm in arms:
            slots.append(dict(id=f'{task}|{model}|{repeat}|{arm}', task=task,
                              model=model, repeat=repeat, arm=arm))
    return slots


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def freeze(root, config):
    if (root/'manifest.json').exists():
        raise ValueError('Already frozen; use a new artifact directory')
    tasks, routes = config['tasks'], config['routes']
    if (len(tasks) != 12 or len({t['id'] for t in tasks}) != 12
            or len(routes) != 2 or len({r['model'] for r in routes}) != 2):
        raise ValueError('Expected 12 unique tasks and two distinct models')
    if not typed_equal(tasks, rows(root/'cases.jsonl')):
        raise ValueError('Protocol tasks differ from frozen cases')
    validate_reserve(config, (root/'SKILL.snapshot.md').read_text())
    config = dict(config, version='telegraphist-pilot-v1', frozen_at=utc())
    config['slots'] = schedule(config['tasks'], config['routes'], 20260929)
    if len(config['slots']) != 96 or len({s['id'] for s in config['slots']}) != 96:
        raise ValueError('Expected 96 unique slots')
    save(root/'protocol.json', config)
    (root/'bench.snapshot.py').write_bytes(Path(__file__).read_bytes())
    names = ['SKILL.snapshot.md', 'cases.jsonl', 'protocol.json', 'bench.snapshot.py']
    names += [p.name for p in root.glob('*.endpoints.json')]
    if (root/'catalog.json').exists():
        names.append('catalog.json')
    save(root/'manifest.json', {name:digest(root/name) for name in names})


def verify(root):
    for name, expected in strict_json((root/'manifest.json').read_text()).items():
        if Path(name).name != name or digest(root/name) != expected:
            raise ValueError('Frozen input integrity failure')


def validate_reserve(config, skill):
    """Text-only bound: one token/UTF-8 byte + 1024 template tokens.

    max_tokens includes reasoning; request fees must be capped explicitly.
    Frozen provider caps are USD/million tokens, request cap is USD/request.
    """
    if not can_spend(0, config.get('reserve_per_request'), config.get('budget')):
        raise ValueError('Invalid reservation or budget')
    reserve = Decimal(str(config['reserve_per_request']))
    for route in config['routes']:
        try:
            caps = route['max_price']
            prompt, completion, fee = (Decimal(str(caps[k])) for k in ('prompt', 'completion', 'request'))
            if any(not n.is_finite() or n < 0 for n in (prompt, completion, fee)):
                raise ValueError('Invalid price caps')
        except (KeyError, TypeError, InvalidOperation) as exc:
            raise ValueError('Explicit prompt/completion/request caps required') from exc
        for task in config['tasks']:
            request = payload({'model':route['model'], 'arm':'skill'}, task, route, skill)
            # Charge all serialized input bytes, including roles/options, plus template margin.
            input_tokens = len(json.dumps(request, ensure_ascii=False).encode('utf-8')) + 1024
            bound = (input_tokens * prompt + request['max_tokens'] * completion) / 1000000 + fee
            if reserve < bound:
                raise ValueError('Reservation below conservative request bound')


def run(root, config, skill, call, max_new=96):
    # Single process per artifact directory required; no concurrent runners.
    validate_reserve(config, skill)
    log = root/'attempts.jsonl'
    history = rows(log)
    seen = started(log)
    results = [r for r in history if r['event'] == 'result']
    # A durable start without a result means unknown submission status: never replay.
    if seen - {r['slot'] for r in results} or any(r.get('cost') is None or r.get('protocol_error') for r in results):
        return 'blocked_by_prior_unknown_cost_or_protocol_error'
    used = sum((Decimal(r['cost']) for r in results), Decimal(0))
    tasks = {t['id']:t for t in config['tasks']}
    routes = {r['model']:r for r in config['routes']}
    count = 0
    for slot in config['slots']:
        if slot['id'] in seen:
            continue
        if count >= max_new or len(seen) >= 96:
            break
        if not can_spend(used, config['reserve_per_request'], config['budget']):
            return 'budget_stop'
        task, route = tasks[slot['task']], routes[slot['model']]
        request = payload(slot, task, route, skill)
        start = utc()
        append(log, dict(event='start', slot=slot['id'], started_at=start, payload=request,
                         reserve_usd=config['reserve_per_request']))
        monotonic = time.monotonic()
        error = None
        try:
            status, response = call(request)
        except Exception as exc:
            # Exception strings can expose credential-bearing headers; retain type only.
            status, response, error = None, {}, type(exc).__name__
        elapsed = time.monotonic() - monotonic
        try:
            json.dumps(response, allow_nan=False)
        except (TypeError, ValueError):
            response = {'error':{'type':'non_json_response'}}
        raw_response = response
        response = response if isinstance(response, dict) else {}
        usage = response.get('usage')
        usage = usage if isinstance(usage, dict) else {}
        cost = usage.get('cost')
        try:
            cost = Decimal(str(cost))
            if not cost.is_finite() or cost < 0:
                cost = None
        except (InvalidOperation, TypeError, ValueError):
            cost = None
        choices = response.get('choices')
        choice = choices[0] if isinstance(choices, list) and len(choices) == 1 and isinstance(choices[0], dict) else {}
        message = choice.get('message')
        message = message if isinstance(message, dict) else {}
        finish = choice.get('finish_reason')
        protocol_error = None
        if status != 200 or response.get('error'):
            protocol_error = 'http_or_api_error'
        elif (not isinstance(response.get('id'), str) or not response['id']
              or not isinstance(finish, str) or finish not in ('stop', 'length', 'content_filter', 'tool_calls')
              or ('content' not in message and not isinstance(message.get('refusal'), str))
              or (message.get('content') is not None and not isinstance(message['content'], str))
              or (message.get('refusal') is not None and not isinstance(message['refusal'], str))
              or any(type(usage.get(k)) is not int or usage[k] < 0
                     for k in ('prompt_tokens', 'completion_tokens', 'total_tokens'))
              or cost is None):
            protocol_error = 'malformed_response'
        elif response.get('model') not in route.get('returned_models', [slot['model']]):
            protocol_error = 'model_mismatch'
        elif response.get('provider') != route['observed_provider']:
            protocol_error = 'provider_mismatch'
        if cost is not None:
            if not can_spend(used, cost, config['budget']):
                protocol_error = 'budget_exceeded'
            elif cost > Decimal(str(config['reserve_per_request'])):
                protocol_error = 'reserve_exceeded'
        result = dict(event='result', slot=slot['id'], task=slot['task'], arm=slot['arm'],
                      model_requested=slot['model'], model_returned=response.get('model'),
                      provider_requested=route['provider'], provider_observed=response.get('provider'),
                      repeat=slot['repeat'], started_at=start, ended_at=utc(), elapsed_seconds=elapsed,
                      http_status=status, error_class=error, protocol_error=protocol_error,
                      generation_id=response.get('id'), usage=usage,
                      cost=str(cost) if cost is not None else None, finish_reason=finish,
                      raw_response=raw_response, validator_version='typed-json-v1',
                      score=score(task, None if message.get('refusal') or finish == 'content_filter' else message.get('content'), finish) if not protocol_error else
                      dict(status='operational_failure', reason=protocol_error))
        append(log, result)
        print(json.dumps({k:result[k] for k in ['slot','http_status','cost','protocol_error']}), flush=True)
        seen.add(slot['id'])
        count += 1
        if cost is None or protocol_error:
            return 'unknown_cost_or_protocol_error'
        used += Decimal(str(cost))
    return 'complete' if len(seen) == len(config['slots']) else 'paused'


def api(path, key, body=None, method=None):
    if not key or not key.isascii() or any(c.isspace() or ord(c)<33 for c in key):
        raise ValueError('Invalid credential')
    def redact(value):
        if isinstance(value, str):
            value = value.replace(key, '[REDACTED]')
            value = re.sub(r'\bsk-(?:or-v1-[A-Za-z0-9_-]+|[A-Za-z0-9_-]{20,})', '[REDACTED]', value)
            value = re.sub(r'(?i)\b(Bearer\s+)[^\s\"\'<>]+', r'\1[REDACTED]', value)
            return re.sub(r'(?i)\b((?:api[_-]?key|authorization|access[_-]?token)\s*[:=]\s*)[^\s\"\'<>]+',
                          r'\1[REDACTED]', value)
        if isinstance(value, list):
            return [redact(item) for item in value]
        if isinstance(value, dict):
            return {redact(k): '[REDACTED]' if k.lower() in
                    ('api_key', 'api-key', 'apikey', 'authorization', 'access_token', 'secret')
                    else redact(v) for k, v in value.items()}
        return value

    req = urllib.request.Request('https://openrouter.ai/api/v1/' + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Bearer '+key, 'Content-Type':'application/json'},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return response.status, redact(strict_json(response.read()))
    except urllib.error.HTTPError as exc:
        try:
            data = strict_json(exc.read())
        except Exception:
            data = {'error':{'type':'non_json_http_error'}}
        return exc.code, redact(data)
    except Exception:
        raise RuntimeError('API transport or response decoding failed') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['freeze','verify','run'])
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--max-new', type=int, default=96)
    args = parser.parse_args()
    root = args.artifacts
    if args.command == 'freeze':
        freeze(root, strict_json(args.config.read_text()))
    else:
        verify(root)
        if args.command == 'run':
            if digest(Path(__file__)) != digest(root/'bench.snapshot.py'):
                raise ValueError('Run the frozen runner, not a changed implementation')
            key = os.environ.get('TELEGRAPHIST_API_KEY', '')
            status, info = api('key', key)
            d = info.get('data', {})
            if status != 200 or d.get('limit') != 10 or d.get('is_management_key') or not can_spend(0, '0.10', d.get('limit_remaining')):
                raise ValueError('Dedicated $10 inference key preflight failed')
            config = strict_json((root/'protocol.json').read_text())
            outcome = run(root, config, (root/'SKILL.snapshot.md').read_text(),
                          lambda p:api('chat/completions', key, p), args.max_new)
            print(outcome)
            if outcome not in ('complete','paused'):
                raise SystemExit(2)


if __name__ == '__main__':
    main()
