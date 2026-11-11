#!/usr/bin/env bash
# PreToolUse: every launch/parser/helper failure maps to blocking exit 2.
if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' 'Blocked by guard: Python parser unavailable' >&2
  exit 2
fi
guard_dir="${BASH_SOURCE[0]%/*}"
if [[ ! -r "$guard_dir/guard.py" ]]; then
  printf '%s\n' 'Blocked by guard: policy helper unavailable' >&2
  exit 2
fi
python3 "$guard_dir/guard.py"
status=$?
if [[ "$status" -eq 0 ]]; then exit 0; fi
exit 2
