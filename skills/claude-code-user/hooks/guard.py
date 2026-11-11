"""Fail-closed Claude PreToolUse tripwire. No command is executed here."""
import json
import os
import re
import shlex
import sys

COMMAND_TOOLS = {'Bash'}
FILE_TOOLS = {'Read', 'Edit', 'Write'}
DEPLOY = {'vercel', 'netlify', 'wrangler', 'flyctl', 'kubectl', 'terraform', 'sudo', 'su'}


def sensitive(path):
    path = path.replace('\\', '/').lower()
    parts = [p for p in path.split('/') if p]
    return any(p in {'.secrets', '.ssh', 'auth.json', '.credentials.json', 'credentials.json', 'id_rsa', 'id_ed25519'} or (p == '.env' or p.startswith('.env.')) and p != '.env.example' for p in parts)


def protected_removal(path):
    path = path.replace('\\', '/').rstrip('/') or '/'
    lexical = path.lower()
    if lexical in {'/', '/*', '/**', '~', '~/*', '$home', '$home/*', '${home}', '${home}/*', '/home', '/home/*', '/users', '/users/*'}:
        return True
    if re.fullmatch(r'[a-z]:/?\*?', lexical) or re.fullmatch(r'(?:[a-z]:)?/(?:home|users)/[^/]+(?:/\*)?', lexical):
        return True
    normalized = os.path.normpath(os.path.expanduser(path.rstrip('*').rstrip('/') or '/'))
    return normalized in {'/', os.path.expanduser('~')}


def git_verb(tokens, index):
    i = index + 1
    while i < len(tokens):
        value = tokens[i]
        if value in {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--config-env'}:
            i += 2
        elif value.startswith('-'):
            i += 1
        else:
            return value
    return ''


def simple_commands(command):
    """Split only at unquoted, unescaped shell command boundaries."""
    start, quote, escaped = 0, '', False
    for i, char in enumerate(command):
        if escaped:
            escaped = False
        elif char == '\\' and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = ''
        elif char in "\"'":
            quote = char
        elif char == '&' and (i > 0 and command[i-1] in '<>' or command[i+1:i+2] == '>'):
            continue  # Descriptor duplication and &> redirection do not end a command.
        elif char in ';&|()\n':
            yield command[start:i]
            start = i + 1
    yield command[start:]


def command_reason(command):
    command = command.replace('\\\r\n', '').replace('\\\n', '')
    for statement in simple_commands(command):
        lexer = shlex.shlex(statement, posix=True, punctuation_chars=';&|()\n')
        lexer.whitespace_split = True
        lexer.commenters = ''
        tokens = list(lexer)
        for i, token in enumerate(tokens):
            name = token.replace('\\', '/').rsplit('/', 1)[-1]
            tail = tokens[i+1:]
            if sensitive(token):
                return 'credential or secrets path'
            if name == 'git' and git_verb(tokens, i) in {'push', 'remote', 'config'}:
                return 'git publication or configuration'
            if name in DEPLOY:
                return 'deployment or elevated authority'
            if name in {'npm', 'pnpm', 'yarn', 'cargo', 'uv'} and 'publish' in tail:
                return 'package publication'
            if name == 'twine' and 'upload' in tail:
                return 'package publication'
            if name == 'gh' and tail:
                group = tail[0]
                if group in {'api', 'secret'} or group in {'pr', 'issue', 'release', 'repo'} and any(v in tail[1:] for v in {'create', 'edit', 'delete', 'close', 'reopen', 'merge', 'comment', 'upload', 'publish', 'fork', 'rename', 'set'}):
                    return 'GitHub mutation'
            if name == 'curl':
                for j, arg in enumerate(tail):
                    next_arg = tail[j+1] if j+1 < len(tail) else ''
                    if arg in {'-X', '--request'} and next_arg.upper() not in {'GET', 'HEAD', 'OPTIONS'}:
                        return 'mutating HTTP request'
                    if arg.startswith('-X') and len(arg) > 2 and arg[2:].upper() not in {'GET', 'HEAD', 'OPTIONS'}:
                        return 'mutating HTTP request'
                    if arg.startswith('--request=') and arg.split('=', 1)[1].upper() not in {'GET', 'HEAD', 'OPTIONS'}:
                        return 'mutating HTTP request'
                    if arg in {'-d', '-F', '-T'} or arg.startswith(('--data', '--json', '--form', '--upload-file')) or len(arg) > 2 and arg[:2] in {'-d', '-F', '-T'}:
                        return 'HTTP upload or body'
            if name in {'rm', 'Remove-Item', 'remove-item', 'ri'}:
                recursive = any(v.startswith('-') and ('r' in v.lstrip('-') or v.lower() in {'--recursive', '-recurse'}) for v in tail)
                force = any(v.startswith('-') and ('f' in v.lstrip('-') or v.lower() in {'--force', '-force'}) for v in tail)
                if recursive and force and any(not v.startswith('-') and protected_removal(v) for v in tail):
                    return 'protected root or home removal'
    return None


def check(event):
    if not isinstance(event, dict) or not isinstance(event.get('tool_name'), str) or not isinstance(event.get('tool_input'), dict):
        return 'malformed hook payload'
    name, data = event['tool_name'], event['tool_input']
    if name in COMMAND_TOOLS:
        command = data.get('command')
        if not isinstance(command, str) or not command.strip() or '\x00' in command:
            return 'malformed command'
        return command_reason(command)
    if name in FILE_TOOLS:
        path = data.get('file_path')
        if not isinstance(path, str) or not path.strip() or '\x00' in path:
            return 'malformed file path'
        return 'credential or secrets path' if sensitive(path) else None
    return 'unexpected guarded tool'


def main():
    try:
        reason = check(json.load(sys.stdin))
    except Exception:
        reason = 'unreadable or malformed hook input'
    if reason:
        print('Blocked by guard: ' + reason, file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
