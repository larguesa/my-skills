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
# Protocol 2, rule 4: only calls without text output, after ledger reconciliation, at most twice.
RESUBMITTABLE = {'ambiguous_intent_without_raw', 'billing_uncertain'}
MAX_ATTEMPTS = 2
SETTLE_SECONDS = 1800
CLOCK_MARGIN_SECONDS = 60
TRANSPORT_TIMEOUT_SECONDS = 180
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


def carries_output(value):
    """Conservative: only null, blank text or an empty container prove that nothing came back."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)  # content blocks or an unknown shape are never proof of no output
    return True


def raw_output(raw):
    """True when a stored response carries candidate text or a judgment, whatever its status."""
    try:
        data = json.loads(base64.b64decode(raw['body_base64'], validate=True))
    except (ValueError, UnicodeDecodeError):
        return raw.get('http_status') == 200
    if not isinstance(data, dict):
        return raw.get('http_status') == 200
    choices = data.get('choices')
    if not isinstance(choices, list):
        return carries_output(choices) or carries_output(data.get('answers'))
    for choice in choices:
        if not isinstance(choice, dict):
            values = [choice]
        else:
            message = choice.get('message')
            # Content, refusal, tool calls or any other message field besides the role.
            values = ([v for k, v in message.items() if k != 'role'] if isinstance(message, dict) else [message])
            values.append(choice.get('text'))
        if any(carries_output(v) for v in values):
            return True
    return carries_output(data.get('answers'))


def moment(value):
    from datetime import datetime
    stamp = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if stamp.tzinfo is None:
        raise ValueError('timestamp without time zone')
    return stamp


def prior_files(path):
    files = {}
    for name in ('intent', 'raw', 'transport-error'):
        target = path / (name + '.json')
        files[name] = g.read_json(target) if target.exists() else None
    return files


def binding(call, files):
    return dict(call_sha256=g.digest(call), prior_intent_sha256=g.digest(files['intent']),
                prior_raw_sha256=g.digest(files['raw']) if files['raw'] is not None else None,
                prior_transport_error_sha256=(g.digest(files['transport-error'])
                                              if files['transport-error'] is not None else None))


def reconcile(store, call, ledger_bytes, decided_by, authorization, known_generation_ids, clock=None):
    """Evidence that a call produced neither output nor charge; frozen before any new submission."""
    clock = clock or g.now
    current = store.recover(call)
    if current is None:
        raise ValueError('no intent for this slot; nothing to reconcile')
    if current['status'] not in RESUBMITTABLE:
        raise ValueError('only calls without text output can be resubmitted; status is ' + current['status'])
    attempt = current.get('attempt', 0) + 1
    if attempt > MAX_ATTEMPTS:
        raise ValueError(f'at most {MAX_ATTEMPTS} resubmissions per call')
    path = store.paths(call['slot'])
    prior = path / f'attempt-{attempt - 1}' if attempt > 1 else path
    files = prior_files(prior)
    if files['raw'] is not None and raw_output(files['raw']):
        raise ValueError('stored response carried text output; it is never resubmitted')
    try:
        ledger = json.loads(ledger_bytes)
        assert isinstance(ledger, dict) and ledger.get('kind') == 'key_activity_export'
        exported, start, end = (moment(ledger[k]) for k in ('exported_at', 'period_start', 'period_end'))
        entries = ledger['entries']
        assert isinstance(entries, list)
        rows = [(entry, moment(entry['created_at'])) for entry in entries]
        assert all(isinstance(entry.get('model'), str) for entry, _ in rows)
    except (AssertionError, KeyError, TypeError, ValueError):
        raise ValueError('not a key activity ledger export with dated entries') from None
    from datetime import timedelta
    started = moment(files['intent']['started_at'])
    if files['raw'] is not None:
        finished = moment(files['raw']['received_at'])
    elif files['transport-error'] is not None:
        finished = moment(files['transport-error']['finished_at'])
    else:
        finished = started + timedelta(seconds=TRANSPORT_TIMEOUT_SECONDS)
    window = (started - timedelta(seconds=CLOCK_MARGIN_SECONDS), finished + timedelta(seconds=SETTLE_SECONDS))
    if start > window[0] or end < window[1]:
        raise ValueError('ledger export does not cover the call window plus settlement time')
    if exported < end or exported > moment(clock()):
        raise ValueError('ledger exported before the end of its period or in the future')
    models = {call['model'], call['endpoint']['name'].split(' | ')[-1]}
    raw_id = None
    if files['raw'] is not None:
        try:
            raw_id = json.loads(base64.b64decode(files['raw']['body_base64'])).get('id')
        except (ValueError, UnicodeDecodeError, AttributeError):
            raw_id = None
    matching = [entry for entry, created in rows
                if (raw_id and entry.get('generation_id') == raw_id)
                or (entry['model'] in models and window[0] <= created <= window[1]
                    and entry.get('generation_id') not in known_generation_ids)]
    if matching:
        raise ValueError('ledger shows a generation or charge for this model in the window; resubmission refused')
    if not isinstance(decided_by, str) or not decided_by.strip() or not isinstance(authorization, str) \
            or not authorization.strip():
        raise ValueError('reconciliation needs who decided and the explicit authorization')
    decided_at = moment(clock())
    record = dict(schema=1, kind='resubmission_reconciliation', slot=call['slot'], attempt=attempt,
                  prior_status=current['status'], **binding(call, files),
                  ledger_file=f'ledger-{attempt}.json', ledger_sha256=g.digest(ledger_bytes),
                  window=dict(start=window[0].isoformat(), end=window[1].isoformat(),
                              settle_seconds=SETTLE_SECONDS, clock_margin_seconds=CLOCK_MARGIN_SECONDS),
                  entries_checked=len(rows), matching_entries=0,
                  evidence='no stored text output; ledger covers the window and has no generation or charge '
                           'for this model there, except generations already recorded by this run',
                  decided_by=decided_by, autorizacao_texto=authorization, decided_at=decided_at.isoformat(),
                  resubmission_authorized=True)
    if (path / f'reconciliation-{attempt}.json').exists():
        raise FileExistsError('reconciliation already frozen for this attempt')
    ledger = path / f'ledger-{attempt}.json'
    if not ledger.exists():
        g.immutable(ledger, ledger_bytes)
    elif ledger.read_bytes() != ledger_bytes:
        # Interrupted publication: only the byte-identical ledger completes it; never replace evidence.
        raise FileExistsError('a different ledger is already frozen for this attempt')
    g.immutable(path / f'reconciliation-{attempt}.json', record)
    return record


class Store:
    def __init__(self, root, mode, readonly=False):
        self.root, self.mode, self.readonly = Path(root), mode, readonly
        self.requests = self.root / 'requests'
        if not readonly:
            self.requests.mkdir(exist_ok=True, mode=0o700)

    def paths(self, slot):
        if not isinstance(slot, str) or not slot or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789.-' for c in slot):
            raise ValueError('unsafe logical slot')
        return self.requests / slot

    def load(self, path, call, attempt=0, reconciliation_sha256=None):
        """One submission folder: intent, raw and derived result; cache written unless read-only."""
        intent = g.read_json(path / 'intent.json')
        if intent['call'] != call or intent['call_sha256'] != g.digest(call):
            raise ValueError('intent payload mismatch')
        if intent['execution_mode'] != self.mode:
            raise ValueError('OFFLINE and LIVE artifacts cannot be mixed')
        if attempt and (intent.get('attempt') != attempt or intent.get('reconciliation_sha256') != reconciliation_sha256):
            raise ValueError('resubmission intent is not bound to its reconciliation')
        if not (path / 'raw.json').exists():
            if (path / 'result.json').exists():
                raise ValueError('result without raw')
            return dict(slot=call['slot'], status='ambiguous_intent_without_raw', telemetry={})
        raw = g.read_json(path / 'raw.json')
        if raw['call_sha256'] != g.digest(call) or raw['intent_sha256'] != g.digest(intent):
            raise ValueError('raw/intent hash mismatch')
        result = derive(call, intent, raw)
        result_path = path / 'result.json'
        if result_path.exists():
            if g.read_json(result_path) != result:
                raise ValueError('cached result differs from immutable raw')
        elif not self.readonly:
            g.immutable(result_path, result)
        return result

    def recover(self, call):
        path = self.paths(call['slot'])
        if not (path / 'intent.json').exists():
            if path.exists() and list(path.glob('*.json')):
                raise ValueError('orphan request without intent')
            return None
        result = self.load(path, call)
        original = result['status']
        for attempt in range(1, MAX_ATTEMPTS + 2):
            folder, decision = path / f'attempt-{attempt}', path / f'reconciliation-{attempt}.json'
            if not folder.exists():
                break
            if attempt > MAX_ATTEMPTS or not decision.exists() or result['status'] not in RESUBMITTABLE:
                raise ValueError('resubmission without valid reconciliation or beyond the limit')
            result = dict(self.load(folder, call, attempt, g.digest(self.reconciliation(call, attempt))),
                          attempt=attempt, original_status=original)
        return result

    def reconciliation(self, call, attempt):
        """Frozen decision bytes, checked against the prior record and its own ledger file."""
        path = self.paths(call['slot'])
        decision = (path / f'reconciliation-{attempt}.json').read_bytes()
        data = json.loads(decision)
        prior = path / f'attempt-{attempt - 1}' if attempt > 1 else path
        expected, ledger = binding(call, prior_files(prior)), path / f'ledger-{attempt}.json'
        if (not 1 <= attempt <= MAX_ATTEMPTS or not isinstance(data, dict)
                or data.get('resubmission_authorized') is not True or data.get('attempt') != attempt
                or {k: data.get(k) for k in expected} != expected or data.get('ledger_file') != ledger.name
                or not ledger.is_file() or g.digest(ledger.read_bytes()) != data.get('ledger_sha256')):
            raise ValueError('reconciliation does not match the prior record or its ledger')
        return decision

    def pending_resubmission(self, call):
        """Next attempt number when a valid frozen reconciliation waits for its submission, else None.

        Corrupt or swapped evidence raises here, before any new intent or transport call.
        """
        record = self.recover(call)
        if record is None or record['status'] not in RESUBMITTABLE:
            return None
        attempt = record.get('attempt', 0) + 1
        path = self.paths(call['slot'])
        if (path / f'reconciliation-{attempt}.json').exists() and not (path / f'attempt-{attempt}').exists():
            self.reconciliation(call, attempt)
            prior = prior_files(path / f'attempt-{attempt - 1}' if attempt > 1 else path)
            if prior['raw'] is not None and raw_output(prior['raw']):
                raise ValueError('stored response carried text output; it is never resubmitted')
            return attempt
        return None

    def audit(self):
        records = {}
        if self.readonly and not self.requests.exists():
            return records
        for path in sorted(self.requests.iterdir()):
            if not path.is_dir():
                raise ValueError('unexpected file in request store')
            intent = g.read_json(path / 'intent.json')
            call = intent['call']
            if call['slot'] != path.name or call['slot'] in records:
                raise ValueError('duplicate/mismatched slot')
            records[call['slot']] = (call, self.recover(call))
        return records

    def resubmit(self, call, transport, attempt):
        """Protocol 2 only: a new submission bound to its frozen reconciliation; the original stays."""
        if self.pending_resubmission(call) != attempt:
            raise ValueError('no frozen reconciliation waiting for this attempt')
        path = self.paths(call['slot'])
        decision = self.reconciliation(call, attempt)  # the intent binds the same bytes just validated
        intent = dict(schema=1, call=call, call_sha256=g.digest(call), execution_mode=self.mode,
                      started_at=g.now(), attempt=attempt, reconciliation_sha256=g.digest(decision))
        self.send(path / f'attempt-{attempt}', call, intent, transport)
        return self.recover(call)

    def submit(self, call, transport):
        previous = self.recover(call)
        if previous is not None:
            return previous
        path = self.paths(call['slot'])
        intent = dict(schema=1, call=call, call_sha256=g.digest(call),
                      execution_mode=self.mode, started_at=g.now())
        if self.send(path, call, intent, transport):
            return dict(slot=call['slot'], status='ambiguous_intent_without_raw', telemetry={})
        return self.recover(call)

    def send(self, path, call, intent, transport):
        """Intent first, then one POST; returns True when the transport failed without raw bytes."""
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
            return True
        return False
