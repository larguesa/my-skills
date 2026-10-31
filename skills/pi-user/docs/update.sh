#!/usr/bin/env bash
# Re-downloads the official pi coding-agent docs (markdown + docs.json) into this folder.
set -euo pipefail
cd "$(dirname "$0")"
api=https://api.github.com/repos/earendil-works/pi/contents/packages/coding-agent/docs
raw=https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/docs
files=$(curl -fsSL "$api" | jq -r '.[]|select(.type=="file")|.name|select(test("\\.(md|json)$"))')
for f in $files; do
  curl -fsSL "$raw/$f" -o "$f.tmp"
  if head -c 300 "$f.tmp" | grep -qi '<!doctype\|<html'; then echo "HTML for $f, skipped" >&2; rm "$f.tmp"; else mv "$f.tmp" "$f"; fi
done
echo "updated $(date +%F): $(echo $files | wc -w) files"
