#!/usr/bin/env python3
"""Continua uma recuperação já reconciliada; preserva o HTTP real de novas falhas."""
import json
import os
from pathlib import Path
import re
import urllib.error
import benchmark as b
import contos as c

original_run = b.run_plan
original_chat = c.run_chat
original_spend = c.spend


def amended_calls(calls, directory):
    path = directory / 'attempts/route-amendment.json'
    if not path.exists():
        return calls
    amendment = c.load(path)
    # ponytail: one documented unavailable route; general failover is out of scope.
    return [c.make_call(call['model'], amendment['endpoint'], call['payload']['reasoning'],
                       call['payload']['messages'], call['case'], call['arm'], call['mode'],
                       call['payload']['max_tokens'])
            if call['model'] == amendment['model'] and call['case'] == amendment['case']
            else call for call in calls]


def run_amended_chat(calls, directory, name, budget, key):
    amendment = directory / 'attempts/route-amendment.json'
    if name == 'generation' and amendment.exists():
        calls = amended_calls(calls, directory)
        budget -= b.money(c.load(amendment)['probe_cost_usd'])
    return original_chat(calls, directory, name, budget, key)


def spend_with_probes(directory):
    path = directory / 'attempts/route-amendment.json'
    return original_spend(directory) + (b.money(c.load(path)['probe_cost_usd']) if path.exists() else 0)


def observed_send(payload, key):
    try:
        return b.raw_send(payload, key)
    except urllib.error.HTTPError as error:
        raw = error.read(65536).decode('utf-8', errors='replace')
        raw = re.sub(r'sk-or-[A-Za-z0-9_-]+', '[REDACTED]', b.redact(raw, key))
        try:
            parsed = json.loads(raw)
            details = parsed.get('error', {})
        except ValueError:
            details = {'message': 'HTTP body was not JSON'}
        b.save_json(c.TESTS / 'results/attempts/last-http-error.json', {
            'http_status': error.code, 'api_error': details,
            'model': payload['model'], 'observed_at': b.datetime.now(b.timezone.utc).isoformat()})
        print('External HTTP failure, evidence retained:', error.code, flush=True)
        raise


def run_observed(plan, state_path, key, **kwargs):
    return original_run(plan, state_path, key, send=observed_send, **kwargs)


if __name__ == '__main__':
    amendment = c.TESTS / 'results/attempts/route-amendment.json'
    if amendment.exists():
        if c.hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != c.load(amendment)['runner_sha256']:
            raise SystemExit('Recovery runner changed after amendment freeze')
    b.run_plan = run_observed
    c.run_chat = run_amended_chat
    c.spend = spend_with_probes
    try:
        c.execute(c.TESTS / 'frozen/config.json', c.TESTS / 'results', os.environ.get('OPENROUTER_API_KEY', ''))
    except Exception as error:
        print('Stopped safely: ' + type(error).__name__)
        raise SystemExit(2)
