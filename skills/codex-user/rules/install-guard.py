"""Generate a separate instance-specific Codex guard candidate; no active config edits."""
from pathlib import Path
import argparse
import json
import os
import shlex


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--secrets-dir', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    raw = Path(args.secrets_dir).expanduser()
    if not raw.is_absolute():
        raise SystemExit('secrets directory must be absolute')
    secret = raw.resolve().as_posix()
    home = Path.home().resolve().as_posix()
    if any(c in secret for c in ('\n', '\r', '\x00')) or '/home/USER' in secret:
        raise SystemExit('invalid or unresolved secret-directory placeholder')
    text = Path(__file__).with_name('guard.rules').read_text()
    replacements = {
        '"/home/USER/.secrets"': json.dumps(secret),
        '"/home/USER"': json.dumps(home),
        '"cat /home/USER/.secrets"': json.dumps('cat ' + shlex.quote(secret)),
        '"rm -fr /home/USER"': json.dumps('rm -fr ' + shlex.quote(home)),
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    if '/home/USER' in text:
        raise SystemExit('unresolved guard placeholder')
    fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as output:
        output.write(text)


if __name__ == '__main__':
    main()
