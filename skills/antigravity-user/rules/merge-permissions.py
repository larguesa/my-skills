"""Prepare a new Antigravity settings candidate without replacing active settings."""
from copy import deepcopy
from pathlib import Path
import json
import os
import re
import sys


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def merge(config, overlay, secrets_dir):
    if not isinstance(config, dict) or not isinstance(overlay, dict):
        raise ValueError('configuration must be an object')
    secret = Path(secrets_dir).expanduser()
    if not secret.is_absolute() or any(c in str(secret) for c in ('\n', '\r', '\x00', ')')):
        raise ValueError('absolute valid secret directory required')
    secret_text = secret.resolve().as_posix()
    if '/home/USER' in secret_text:
        raise ValueError('unresolved secret placeholder')
    home = Path.home().resolve().as_posix()
    result = deepcopy(config)
    permissions = result.setdefault('permissions', {})
    if not isinstance(permissions, dict):
        raise ValueError('permissions must be an object')
    previous = permissions.get('deny', [])
    additions = overlay.get('permissions', {}).get('deny')
    if not isinstance(previous, list) or not isinstance(additions, list) or not all(isinstance(x, str) for x in previous + additions):
        raise ValueError('denials must be string arrays')
    generated = []
    for rule in additions:
        if rule.startswith('command(regex:') and rule.endswith(')'):
            expression = rule[len('command(regex:'):-1].replace('/home/USER', re.escape(home))
            re.compile(expression)
            rule = 'command(regex:' + expression + ')'
        else:
            rule = rule.replace('/home/USER/.secrets', secret_text)
        if '/home/USER' in rule:
            raise ValueError('unresolved placeholder')
        generated.append(rule)
    permissions['deny'] = list(dict.fromkeys(previous + generated))
    return result


def main():
    if len(sys.argv) != 5:
        raise SystemExit('usage: merge-permissions.py existing.json guard.json absolute-secrets-dir candidate.json')
    source, guard, secret, target = sys.argv[1:]
    destination = Path(target)
    if destination.resolve() in {Path(source).resolve(), Path(guard).resolve()}:
        raise SystemExit('candidate must be separate')
    try:
        config = json.loads(Path(source).read_text(), object_pairs_hook=unique_object)
        overlay = json.loads(Path(guard).read_text(), object_pairs_hook=unique_object)
        result = merge(config, overlay, secret)
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write('\n')
    except (ValueError, OSError, TypeError, re.error):
        raise SystemExit('could not prepare candidate; input or rules require review')


if __name__ == '__main__':
    main()
