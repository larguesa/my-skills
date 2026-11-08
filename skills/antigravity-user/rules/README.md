# Guard permission rules
`guard-permissions.json` holds Antigravity CLI `permissions.deny` rules: shell commands with `git push`, `git remote|config`, `gh pr|release|repo|secret|api`, `npm|pnpm|yarn publish`, deploy CLIs (vercel, netlify, wrangler, flyctl, kubectl, terraform), mutating `curl -X`, `sudo`, `rm -rf /`, anything mentioning `.secrets`; file reads (and so writes) of the workspace-root `.env` and a secrets folder. Deny beats ask and allow, and the docs say deny rules apply in every mode, including `--dangerously-skip-permissions` (docs/permissions.md, docs/reference.md `toolPermission`).

Install: back up `~/.gemini/antigravity-cli/settings.json`, then append the list to `permissions.deny` (keeps rules already there):
```bash
f=~/.gemini/antigravity-cli/settings.json
jq -s '.[0].permissions.deny = ((.[0].permissions.deny // []) + .[1].permissions.deny | unique) | .[0]' "$f" guard-permissions.json > new.json
```
Review `new.json`, replace the file, then edit the secrets path. `~` is not expanded. Use an absolute path: `/home/<you>/.secrets` on Linux, `/Users/<you>/.secrets` on macOS. On Windows use the drive letter with forward slashes, `C:/Users/<you>/.secrets`. The docs say drive letters are stripped, but with 1.4.2 only the `C:/...` form matched.

Tested on agy 1.4.2 (Windows, headless, rules in a temporary HOME): `git push`, `echo hi && git push origin main` and `type ...\.secrets\token.txt` were blocked even with `command(git)`, `command(echo)` and `command(type)` allowed; `read_file` of `.env` and of `C:/Users/.../.secrets` was blocked. The blocked tool step ends with `state: "ERROR"` and `"... Matches user-configured deny rule."`; the model sees the error. Not tested: the rules under `--dangerously-skip-permissions`.

Limits: regex rules match the whole command string, so they also catch chained commands, but a determined model can still obfuscate (variables, scripts). `read_file(.env)` covers only the workspace root; nested `.env` files need their own rules (the terminal sandbox also blocks `.env` and `~/.ssh` for commands). The CLI silently ignores rules it can't parse: after editing, run a quick test like the one above. A tripwire, not a sandbox.
