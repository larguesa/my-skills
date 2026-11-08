#!/usr/bin/env bash
# Re-downloads the official Antigravity CLI docs (markdown) into this folder.
# Page list comes from llms.txt: every /docs/cli/* link, plus general pages with CLI content.
set -euo pipefail
cd "$(dirname "$0")"
base=https://antigravity.google
get() { curl -fsSL "$1" -o "$2.tmp" && if head -c 300 "$2.tmp" | grep -qi '<!doctype\|<html'; then echo "HTML for $2, skipped" >&2; rm "$2.tmp"; else mv "$2.tmp" "$2"; fi || echo "failed $1" >&2; }
curl -fsSL "$base/llms.txt" -o llms.txt
pages=$(grep -o "$base/docs/cli/[a-z0-9/_-]*" llms.txt | sed "s#$base/docs/##" | sort -u)
general="getting-started install features permissions sandbox rules hooks mcp skills subagents plugins settings enterprise"
for p in $general $pages; do
  name=${p#cli/}; get "$base/docs/$p.md" "${name//\//-}.md"   # cli/commands/agents -> commands-agents.md
done
echo "updated $(date +%F)"
