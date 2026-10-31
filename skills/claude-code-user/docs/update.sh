#!/usr/bin/env bash
# Re-downloads the official Claude Code docs (markdown) into this folder.
set -euo pipefail
cd "$(dirname "$0")"
base=https://code.claude.com/docs/en
for f in cli-reference commands env-vars tools-reference interactive-mode checkpointing hooks channels-reference glossary headless; do
  curl -fsSL "$base/$f.md" -o "$f.md.tmp"
  if head -c 300 "$f.md.tmp" | grep -qi '<!doctype\|<html'; then echo "HTML for $f, skipped" >&2; rm "$f.md.tmp"; else mv "$f.md.tmp" "$f.md"; fi
done
curl -fsSL "$base/../llms.txt" -o llms.txt 2>/dev/null || curl -fsSL https://code.claude.com/docs/llms.txt -o llms.txt
echo "updated $(date +%F)"
