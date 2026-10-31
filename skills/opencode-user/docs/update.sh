#!/usr/bin/env bash
# Re-downloads the official OpenCode docs (English .mdx from the repo) and converts them to .md here.
set -euo pipefail
cd "$(dirname "$0")"
repo=anomalyco/opencode; branch=dev; path=packages/web/src/content/docs
files=$(curl -fsSL "https://api.github.com/repos/$repo/contents/$path?ref=$branch" | jq -r '.[]|select(.type=="file")|.name|select(endswith(".mdx"))')
n=0
for f in $files; do
  curl -fsSL "https://raw.githubusercontent.com/$repo/$branch/$path/$f" -o "/tmp/oc_$f"
  if head -c 300 "/tmp/oc_$f" | grep -qi '<!doctype\|<html'; then echo "HTML for $f, skipped" >&2; continue; fi
  python3 mdx2md.py "/tmp/oc_$f" "${f%.mdx}.md"; rm -f "/tmp/oc_$f"; n=$((n+1))
done
echo "updated $(date +%F): $n files"
