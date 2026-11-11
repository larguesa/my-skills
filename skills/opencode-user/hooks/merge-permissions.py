"""Prepare an OpenCode guard overlay without widening existing permissions.
Writes a separate candidate file; it never replaces active configuration.
"""
from copy import deepcopy
from fnmatch import fnmatchcase
from pathlib import Path
import json
import os
import sys
from typing import Any

ACTIONS = {'allow', 'ask', 'deny'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key requires review')
        result[key] = value
    return result


def mapping(value) -> dict[str, Any]:
    if isinstance(value, str) and value in ACTIONS:
        return {'*': value}
    if isinstance(value, dict):
        return deepcopy(value)
    raise ValueError('unsupported permission shape')


def effective(config, tool, target):
    permission = mapping(config.get('permission', {}))
    decision = None  # Unknown native default must not be turned into allow.
    for selector, rule in permission.items():
        if selector not in ('*', tool):
            continue
        for pattern, action in mapping(rule).items():
            if action not in ACTIONS:
                raise ValueError('invalid permission action')
            if fnmatchcase(target, pattern):
                decision = action
    return decision


def merge(config, overlay):
    if not isinstance(config, dict) or not isinstance(overlay, dict):
        raise ValueError('configuration must be an object')
    candidate = deepcopy(config)
    original = deepcopy(config)
    permission = mapping(candidate.get('permission', {}))
    guards = overlay.get('permission')
    if not isinstance(guards, dict):
        raise ValueError('guard permission object required')
    for tool in (*permission, *guards):
        if not isinstance(tool, str) or tool != '*' and any(c in tool for c in '*?'):
            raise ValueError('unsupported tool-name pattern; only literal names and "*" are supported')
    if '*' in guards:
        raise ValueError('unsupported guard tool-name pattern; overlay tool names must be literal')
    for tool, denies in guards.items():
        if not isinstance(denies, dict):
            raise ValueError('guard tool policy must be an object')
        inherited = {}
        for selector, rule in permission.items():
            if selector in ('*', tool):
                for pattern, action in mapping(rule).items():
                    inherited.pop(pattern, None)
                    inherited[pattern] = action
        current = mapping(inherited)
        for pattern, action in denies.items():
            if action != 'deny':
                if not (pattern == '*.env.example' and action == 'allow'):
                    raise ValueError('overlay may not introduce broad allows')
                # Preserve an existing ask/deny, including a matching specific rule.
                # If the effective template policy cannot be established, do not widen it.
                if effective(original, tool, '.env.example') != 'allow':
                    continue
                if permission.get('*') in ('ask', 'deny') or any(v in ('ask', 'deny') for v in mapping(inherited).values()):
                    continue
            current.pop(pattern, None)  # Move duplicate patterns to the final guard position.
            current[pattern] = action
        permission.pop(tool, None)  # Keep guard rules after matching global tool rules too.
        permission[tool] = current
    candidate['permission'] = permission
    return candidate


def main():
    if len(sys.argv) != 4:
        raise SystemExit('usage: merge-permissions.py existing.json guard.json candidate.json')
    source, guard, destination = map(Path, sys.argv[1:])
    if destination.resolve() in {source.resolve(), guard.resolve()}:
        raise SystemExit('candidate must be a separate file')
    try:
        config = json.loads(source.read_text(), object_pairs_hook=unique_object)
        overlay = json.loads(guard.read_text(), object_pairs_hook=unique_object)
        result = merge(config, overlay)
        fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as output:
            json.dump(result, output, ensure_ascii=False, indent=2)
            output.write('\n')
    except ValueError as error:
        raise SystemExit(f'could not prepare candidate; input/configuration requires review: {error}')
    except (OSError, TypeError):
        raise SystemExit('could not prepare candidate; input/configuration requires review')


if __name__ == '__main__':
    main()
