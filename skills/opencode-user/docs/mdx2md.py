#!/usr/bin/env python3
"""Convert an OpenCode docs .mdx (Starlight) to plain markdown: frontmatter -> H1 + description,
drop imports, turn common components into markdown. Usage: mdx2md.py in.mdx out.md"""
import re, sys
src = open(sys.argv[1], encoding="utf-8").read()
title = desc = ""
m = re.match(r"^---\n(.*?)\n---\n", src, re.S)
if m:
    fm = m.group(1); src = src[m.end():]
    t = re.search(r"^title:\s*(.+)$", fm, re.M); d = re.search(r"^description:\s*(.+)$", fm, re.M)
    title = t.group(1).strip().strip("\"'") if t else ""; desc = d.group(1).strip().strip("\"'") if d else ""
out, fence = [], False
for line in src.split("\n"):
    if line.lstrip().startswith("```"): fence = not fence; out.append(line); continue
    if fence: out.append(line); continue
    if re.match(r"^:::\s*$", line.strip()): continue
    mm = re.match(r"^:::(\w+)", line.strip())
    if mm: out.append("> **" + mm.group(1).capitalize() + ":**"); continue
    if re.match(r"^\s*import .* from ['\"].*['\"];?\s*$", line): continue
    line = re.sub(r"<nobr><code>\{\"([^\"]*)\"\}</code></nobr>", r"`\1`", line)
    line = re.sub(r"<code>\{\"([^\"]*)\"\}</code>", r"`\1`", line)
    line = re.sub(r"<TabItem\s+label=\"([^\"]+)\"[^>]*>", r"**\1**", line)
    line = re.sub(r"<Aside\s+type=\"([^\"]+)\"[^>]*>", lambda m: "> **" + m.group(1).capitalize() + ":**", line)
    line = re.sub(r"<Aside[^>]*>", "> **Note:**", line)
    line = re.sub(r"</?(Tabs|TabItem|Aside|Steps|CardGrid|Card|LinkCard|Badge|FileTree)\b[^>]*>", "", line)
    line = re.sub(r"\]\(/docs/([^)#]*)", lambda m: "](" + (m.group(1).strip("/") or "index") + ".md", line)
    out.append(line)
body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
head = (f"# {title}\n\n" if title else "") + (f"> {desc}\n\n" if desc else "")
open(sys.argv[2], "w", encoding="utf-8").write(head + body + "\n")
