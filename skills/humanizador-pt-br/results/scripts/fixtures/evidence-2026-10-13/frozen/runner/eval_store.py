"""Durable single-submit store. Raw bytes stay private, immutable and hashed."""
import base64
from decimal import Decimal, InvalidOperation
import json
import math
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import generation_eval as g
from eval_judges import aggregate_quality, validate_judge

TERMINAL = {'completed', 'invalid_response'}
URLS = {'chat': 'https://openrouter.ai/api/v1/chat/completions',
        'decisions': 'https://openrouter.ai/api/alpha/decisions'}


def validate_key(key):
    if not isinstance(key, str) or not key or not key.isascii() or any(
            c.isspace() or ord(c) < 33 or ord(c) == 127 for c in key):
        raise ValueError('key must be nonempty ASCII without whitespace or controls')


def real_transport(key):
    validate_key(key)

    def send(call):
        request = urllib.request.Request(URLS[call['api']], data=g.encoded(call['payload']),
            headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                return dict(http_status=response.status, body=response.read())
        except urllib.error.HTTPError as exc:
            return dict(http_status=exc.code, body=exc.read())
    return send


def telemetry(data, body):
    usage = data.get('usage') if isinstance(data.get('usage'), dict) else {}
    money = None
    try:
        cost = json.loads(body, parse_float=Decimal)['usage']['cost']
        if isinstance(cost, bool):
            raise ValueError('bool is not money')
        value = Decimal(str(cost))
        if not value.is_finite() or value < 0:
            raise ValueError('invalid cost')
        money = str(value)
    except (ValueError, KeyError, TypeError, InvalidOperation):
        pass
    prompt = usage.get('prompt_tokens_details') or {}
    completion = usage.get('completion_tokens_details') or {}
    return dict(usage=usage, cost_usd=money, generation_id=data.get('id'),
                model_returned=data.get('model'), provider_returned=data.get('provider'),
                cache_read_tokens=prompt.get('cached_tokens'),
                cache_write_tokens=prompt.get('cache_write_tokens'),
                reasoning_tokens=completion.get('reasoning_tokens'))


def derive(call, intent, raw):
    body = base64.b64decode(raw['body_base64'], validate=True)
    result = dict(slot=call['slot'], call_sha256=g.digest(call), raw_sha256=g.digest(raw),
                  execution_mode=intent['execution_mode'], started_at=intent['started_at'],
                  finished_at=raw['received_at'], elapsed_seconds=raw['elapsed_seconds'],
                  status='billing_uncertain', validation_issues=[], text=None, judgment=None)
    try:
        data = json.loads(body)
        if not isinstance(data, dict):
            raise ValueError('response must be object')
    except (ValueError, UnicodeDecodeError):
        result['validation_issues'] = ['unparseable_raw_body']
        result['telemetry'] = dict(cost_usd=None, usage={})
        return result
    result['telemetry'] = telemetry(data, body)
    native = call['api'] == 'decisions'
    fields = ('input_tokens', 'output_tokens') if native else ('prompt_tokens', 'completion_tokens')
    usage = result['telemetry']['usage']
    if raw['http_status'] != 200 or data.get('error'):
        result['validation_issues'].append('api_or_http_rejection_requires_ledger_reconciliation')
        return result
    if result['telemetry']['cost_usd'] is None or any(
            type(usage.get(f)) is not int or usage[f] < 0 for f in fields):
        result['validation_issues'].append('missing_or_invalid_native_usage')
        return result
    if not isinstance(data.get('id'), str) or not data['id']:
        result['validation_issues'].append('missing_generation_id')
        return result
    expected = {call['model'], call['endpoint']['name'].split(' | ')[-1]}
    if data.get('model') not in expected or data.get('provider') != call['endpoint']['provider_name']:
        result['status'] = 'route_mismatch'
        result['validation_issues'].append('returned_model_or_provider_mismatch')
        return result
    result['model_version_evidence'] = 'dated_return' if data['model'] != call['model'] else 'alias_only'
    result['reasoning_observation'] = 'native_counter_not_proof_of_requested_reasoning'
    result['status'] = 'invalid_response'
    try:
        if not native:
            if len(data.get('choices', [])) != 1:
                raise ValueError('expected_one_choice')
            choice = data['choices'][0]
            message = choice['message']
            result['text'] = message.get('content')
            result['finish_reason'] = choice.get('finish_reason')
            # Do not count reasoning tokens on top of completion; flag impossible counters.
            reasoning = result['telemetry']['reasoning_tokens']
            if reasoning is not None and (type(reasoning) is not int or reasoning < 0
                                         or reasoning > usage['completion_tokens']):
                result['validation_issues'].append('inconsistent_reasoning_counter')
            if not isinstance(result['text'], str) or not result['text'].strip():
                raise ValueError('empty_or_nonstring_content')
            if message.get('refusal') or choice.get('finish_reason') != 'stop':
                raise ValueError('refusal_or_nonstop_finish')
            if usage['completion_tokens'] > call['payload']['max_tokens']:
                raise ValueError('completion_exceeds_frozen_max_tokens')
        if call['phase'] == 'judge':
            parsed = data if native else json.loads(result['text'])
            result['judgment'] = validate_judge(parsed, call['judge_state'], native)
            result['quality_aggregate'] = {tid: aggregate_quality(row)
                for tid, row in result['judgment']['qualidade'].items()}
        result['status'] = 'completed'
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        # Static validation category only; never log exception values that may contain secrets.
        result['validation_issues'].append(type(error).__name__ + ':invalid_content_or_judgment')
    return result


class Store:
    def __init__(self, root, mode):
        self.root, self.mode = Path(root), mode
        self.requests = self.root / 'requests'
        self.requests.mkdir(exist_ok=True, mode=0o700)

    def paths(self, slot):
        if not isinstance(slot, str) or not slot or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789.-' for c in slot):
            raise ValueError('unsafe logical slot')
        return self.requests / slot

    def recover(self, call):
        path = self.paths(call['slot'])
        if not (path / 'intent.json').exists():
            if path.exists() and list(path.glob('*.json')):
                raise ValueError('orphan request without intent')
            return None
        intent = g.read_json(path / 'intent.json')
        if intent['call'] != call or intent['call_sha256'] != g.digest(call):
            raise ValueError('intent payload mismatch')
        if intent['execution_mode'] != self.mode:
            raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
        if not (path / 'raw.json').exists():
            return dict(slot=call['slot'], status='ambiguous_intent_without_raw', telemetry={})
        raw = g.read_json(path / 'raw.json')
        if raw['call_sha256'] != g.digest(call) or raw['intent_sha256'] != g.digest(intent):
            raise ValueError('raw/intent hash mismatch')
        result = derive(call, intent, raw)
        result_path = path / 'result.json'
        if result_path.exists():
            if g.read_json(result_path) != result:
                raise ValueError('cached result differs from immutable raw')
        else:
            g.immutable(result_path, result)
        return result

    def audit(self):
        records = {}
        for path in sorted(self.requests.iterdir()):
            if not path.is_dir():
                raise ValueError('unexpected file in request store')
            intent = g.read_json(path / 'intent.json')
            call = intent['call']
            if call['slot'] != path.name or call['slot'] in records:
                raise ValueError('duplicate/mismatched slot')
            records[call['slot']] = (call, self.recover(call))
        return records

    def submit(self, call, transport):
        previous = self.recover(call)
        if previous is not None:
            return previous
        path = self.paths(call['slot'])
        intent = dict(schema=1, call=call, call_sha256=g.digest(call),
                      execution_mode=self.mode, started_at=g.now())
        g.immutable(path / 'intent.json', intent)  # Must finish BEFORE a POST is possible.
        start = time.monotonic()
        try:
            response = transport(call)
            body = response['body']
            if not isinstance(body, bytes) or type(response['http_status']) is not int:
                raise ValueError('transport must preserve exact response bytes/status')
            raw = dict(schema=1, call_sha256=g.digest(call), intent_sha256=g.digest(intent),
                       received_at=g.now(), elapsed_seconds=time.monotonic() - start,
                       http_status=response['http_status'], body_base64=base64.b64encode(body).decode('ascii'))
            g.immutable(path / 'raw.json', raw)
        except Exception as error:
            g.immutable(path / 'transport-error.json', dict(error_type=type(error).__name__,
                        finished_at=g.now(), billing='unknown', replay_allowed=False))
            return dict(slot=call['slot'], status='ambiguous_intent_without_raw', telemetry={})
        return self.recover(call)
