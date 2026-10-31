#!/usr/bin/env bash
# Re-downloads the official Codex docs (markdown) into this folder.
set -euo pipefail
cd "$(dirname "$0")"
base=https://learn.chatgpt.com/docs
get() { curl -fsSL "$1" -o "$2.tmp" && if head -c 300 "$2.tmp" | grep -qi '<!doctype\|<html'; then echo "HTML for $2, skipped" >&2; rm "$2.tmp"; else mv "$2.tmp" "$2"; fi || echo "failed $1" >&2; }
for p in non-interactive-mode codex/cli:cli-overview cli/reference:cli-reference auth agent-approvals-security:approvals-security sandboxing \
         agent-configuration/agents-md:agents-md agent-configuration/rules:rules config-file/config-basic config-file/config-advanced \
         config-file/config-reference config-file/config-sample config-file/environment-variables extend/mcp:mcp hooks build-skills enterprise/usage-limits; do
  src=${p%%:*}; name=${p#*:}; [ "$name" = "$p" ] && name=$(basename "$src"); get "$base/$src.md" "$name.md"
done
get https://raw.githubusercontent.com/openai/codex/main/docs/config.md repo-config-notes.md
get https://raw.githubusercontent.com/openai/codex/main/docs/install.md repo-install.md
curl -fsSL https://developers.openai.com/codex/llms.txt -L -o llms.txt
echo "updated $(date +%F)"
