# my-skills

Ricardo Pupo Larguesa's personal skills for AI agents, reused across several projects. Each skill stands alone: copy its folder into the agent's skills directory and load the `SKILL.md`; the `results/` and `tests/` subfolders belong to the evaluation and can be left out. Catalog: [skills/index.md](skills/index.md).

| Skill | What it is for | What was measured |
|---|---|---|
| [Humanizador PT-BR](#humanizador-pt-br) | Portuguese text, written or rewritten by the agent, that reads like a good human writer's | Sample comparison 0.9.1 vs 0.8.1, interrupted, 68 of 95 writing pairs judged |
| [Animation Video Maker](#animation-video-maker) | Short explainer video from a brief, with an editable scene and an MP4 rendered on your machine | 20 examples and 3 demos rendered and checked |
| [Telegraphist](#telegraphist) | Economical conversation with the agent, to spend fewer tokens | Interrupted sample, no judges: shorter answers, higher total tokens |
| [Claude Code User](#claude-code-user) | Guide for the agent to use Claude Code headless (`claude -p`), with the official docs in markdown | Tested on Claude Code 2.1.316: create and resume a session, structured output, fallback model and guard hook |
| [Pi User](#pi-user) | Guide for the agent to use pi (pi.dev) headless (`pi -p --mode json`), with the official docs in markdown | Tested on pi 1.4.0: JSON output, session resume, guard extension and MCP server |
| [OpenCode User](#opencode-user) | Guide for the agent to use OpenCode headless (`opencode run --format json`), with the official docs in markdown | Tested on OpenCode 1.19.5: JSON output, session resume, guard permission rules and cost with and without MCP |
| [Codex User](#codex-user) | Guide for the agent to use the OpenAI Codex CLI headless (`codex exec --json`), with the official docs in markdown | Checked on codex-cli 0.166.0: options via `--help`, sandbox and guard rules tested; model runs not tested (quota exhausted) |
| [Antigravity User](#antigravity-user) | Guide for the agent to use the Google Antigravity CLI headless (`agy -p`), with the official docs in markdown | Tested on agy 1.4.2 (Windows): JSON and streaming output, resume, structured output, silent command denial and guard rules; auto mode and sandbox not tested |
| [Agentic Orchestrator](#agentic-orchestrator) | Orchestration of several agents through natural language only, with flow, state and events in YAML, JSON or Markdown, no frameworks or scripts | Examples checked for format (valid YAML and JSON, no broken references); no evaluation with and without the skill |

## Humanizador PT-BR

For when the agent is going to write in Brazilian Portuguese, or when you have AI-generated text that sounds like AI. The agent delivers what a good writer of the genre would: natural, in the right register, free of the clichés that give AI away, with the author's facts and voice preserved. Works for news, email, documentation, reports, proposals, essays, posts, short stories and chronicles. The skill itself is in Portuguese, since Portuguese text is its purpose.

Ask, for example: "Reescreva este texto gerado por IA para soar humano, sem mudar fatos nem números: [...]. Use humanizador-pt-br."

The goal is to humanize text produced or revised by AI. Improvement in judged humanization is the success criterion; saving time or tokens is not a goal of this skill. The evaluation compares anonymized texts while keeping them faithful to the facts and the request. [Latest comparison, with coverage and full texts](skills/humanizador-pt-br/results/samples/2026-10-25/README.md).

[Humanizador PT-BR 0.8.1: installation and examples](skills/humanizador-pt-br/README.md) · [evaluation](skills/humanizador-pt-br/results/README.md)

## Animation Video Maker

Turns a brief into a short explainer, product or typographic video. The agent writes the scene in code, with exact text and logos, and exports it to MP4 on your machine, with no video-generation API; the source scene stays editable. Exporting requires Python, Playwright with Chromium, and FFmpeg. For organic imagery, the package describes generative and hybrid routes with a separately configured provider, without a ready-made adapter.

Includes 22 visual styles, original creative recipes and motion techniques, for explainers, product demos, kinetic typography and data storytelling. Ask, for example: "Create a 20-second animation explaining our migration approach to non-technical managers. Use the Animation Video Maker workflow, suggest a style, and deliver the editable scene and a validated MP4."

To look before using: 20 original examples, each with MP4, editable source scene and style guide, checked in the [validation report](skills/animation-video-maker/references/validation.md), and three unbranded demos in the [0.2.0 validation](skills/animation-video-maker/references/validation-0.2.md). The 20 examples use the T2S Tech brand, which is excluded from the MIT license; replace brand and content when reusing them.

[Animation Video Maker](skills/animation-video-maker/README.md) · [agent skill](skills/animation-video-maker/SKILL.md) · [gallery](skills/animation-video-maker/gallery.html), which runs locally after downloading the package · [license and notices](skills/animation-video-maker/NOTICE.md)

## Telegraphist

Saves tokens in the conversation with the agent: it answers like a telegraphist, in short sentences with abbreviations and symbols such as `->`, `=` and `+`, without restating the question, delivering only the requested fact or next step. You read less, too.

Ask, for example: "Use telegraphist: what is the difference between TCP and UDP?"

Measured so far, without judges: shorter answers, not overall savings. The only run with the current instruction was interrupted at 67 of 336 episodes. In 18 pairs with a complete answer in both arms (3 other pairs ended empty or truncated in both arms and were excluded), the skill version used 40.8% fewer words and 27.3% fewer output tokens, but 49.8% more input tokens, because the instruction goes with every request; the total rose 14.7% and the cost 1.6%. No judge checked whether the short answers kept the necessary information.

[Telegraphist](skills/telegraphist/SKILL.md) · [test report](skills/telegraphist/tests/REPORT.md)

## Claude Code User

Teaches the agent to delegate coding work to Claude Code unattended: when delegating pays off, the standard `claude -p` call, permissions, turn and spend limits, session resume, long jobs, a hook that blocks `git push` and dangerous commands, and how to check the result instead of trusting the summary. Includes a quick-reference cheat-sheet and markdown copies of the official docs (CLI, commands, environment variables, tools, interactive mode, checkpoints, hooks, channels, glossary and headless), refreshable with `docs/update.sh`.

Ask, for example: "Use claude-code-user and delegate the refactoring of this module to Claude Code, with tests."

[Claude Code User](skills/claude-code-user/SKILL.md) · [cheat-sheet](skills/claude-code-user/reference.md) · [official docs](skills/claude-code-user/docs/README.md)

## Pi User

Teaches the agent to delegate coding work to pi unattended: when to use pi instead of Claude Code, the standard `pi -p --mode json` call, how to read the JSON events and the cost, session resume and fork, RPC mode for long-running agents, models via OpenRouter, native MCP (since 1.x), an extension that blocks `git push`, secret access and dangerous commands, and how to check the result. Includes a quick-reference cheat-sheet and markdown copies of the 43 files of the official docs, refreshable with `docs/update.sh`.

Ask, for example: "Use pi-user and have pi write a script with tests, using MiMo through OpenRouter."

[Pi User](skills/pi-user/SKILL.md) · [cheat-sheet](skills/pi-user/reference.md) · [official docs](skills/pi-user/docs/README.md)

## OpenCode User

Teaches the agent to delegate coding work to OpenCode unattended: when to use OpenCode instead of pi or Claude Code, the standard `opencode run --format json` call, how to read the JSON events and the cost, session resume and fork, a persistent server (`opencode serve` and `--attach`), the build and plan agents, models via OpenRouter, MCP, permission rules that block `git push`, secret access and dangerous commands, and how to check the result. Includes a quick-reference cheat-sheet and markdown copies of the 33 files of the official docs (converted from MDX), refreshable with `docs/update.sh`.

Ask, for example: "Use opencode-user and have OpenCode fix this bug and run the tests."

[OpenCode User](skills/opencode-user/SKILL.md) · [cheat-sheet](skills/opencode-user/reference.md) · [official docs](skills/opencode-user/docs/README.md)

## Codex User

Teaches the agent to delegate coding work to the OpenAI Codex CLI unattended: when to use Codex instead of Claude Code, pi or OpenCode, the standard `codex exec --json` call, the final answer in a file (`-o`) or in a fixed format (`--output-schema`), sandbox and approval modes, execution rules (`.rules`) that block `git push`, publishing, deploys, `sudo` and secret access, session resume and fork, code review (`codex exec review`), AGENTS.md, skills, MCP, ChatGPT plan usage limits, and how to check the result. Includes a quick-reference cheat-sheet and markdown copies of 20 pages of the official docs, refreshable with `docs/update.sh`. Model runs have not been tested yet, because the account's quota was exhausted.

Ask, for example: "Use codex-user and have Codex review the uncommitted changes in this repository."

[Codex User](skills/codex-user/SKILL.md) · [cheat-sheet](skills/codex-user/reference.md) · [official docs](skills/codex-user/docs/README.md)

## Antigravity User

Teaches the agent to delegate coding work to Google's Antigravity CLI (`agy`) unattended. Covers when to use Antigravity instead of the other agents, the standard `agy -p --output-format stream-json` call, and how to read the events and token usage. It also shows how to catch silent denials: in headless mode, a command without permission is refused and the run still ends as a success, with the notice only on stderr. The rest: permission rules that block `git push`, publishing, deploys, `sudo` and secret access; execution modes and sandbox; conversation resume; fixed-format output (`--json-schema`); the risk of the repository's own hooks, which run without asking; AGENTS.md, skills, MCP, Google plan quotas, and how to check the result. Includes a quick-reference cheat-sheet and markdown copies of 42 pages of the official docs, refreshable with `docs/update.sh`.

Ask, for example: "Use antigravity-user and have Antigravity fix this bug and run the tests."

[Antigravity User](skills/antigravity-user/SKILL.md) · [cheat-sheet](skills/antigravity-user/reference.md) · [official docs](skills/antigravity-user/docs/README.md) · [guard rules](skills/antigravity-user/rules/README.md)

## Agentic Orchestrator

Teaches any agent to orchestrate other agents through natural language only, with no framework and no orchestration script. The agent itself is the engine: it reads a flow file in YAML or JSON, delegates work to subagents or to other command-line agents (with this repository's `*-user` skills), checks the results, records state and events in files, and decides the next step. That is why another session can audit or resume the work.

The content is conceptual and prescriptive:
- **Flow patterns:** 19, including sequential, parallel fan-out/fan-in, hierarchical, router, producer-verifier, adaptive, competing hypotheses, consensus, judge panel, debate and council.
- **Communication patterns:** direct, tool-mediated, manager hub, broadcast, blackboard, handoff and mailbox.
- **Loop and graph engineering:** exit criteria, budgets, file ownership and resume.
- **File format:** one format for flow and state, with four complete examples.

Synthesized from four skill repositories (wshobson/agents, affaan-m/ECC, cobusgreyling/loop-engineering and qodex-ai/ai-agent-skills) and a compilation on harness, loop and graph engineering.

Ask, for example: "Use agentic-orchestrator: implement this feature with Claude Code, get an independent review from Codex, and only show me the result once the tests pass."

[Agentic Orchestrator](skills/agentic-orchestrator/SKILL.md) · [flow patterns](skills/agentic-orchestrator/references/flow-patterns.md) · [file format](skills/agentic-orchestrator/references/flow-spec.md)

## Structure

- **AGENTS.md**: repository purpose and rules for agents.
- **skills/**: one folder per skill, plus the `index.md` catalog.
  - **SKILL.md**: the instructions the agent loads.
  - **README.md** (when present): usage, installation and status.
  - **AGENTS.md** (optional): rules for changing and testing the skill.
  - **references/**, **assets/**, **scripts/** (optional): reference material, media and scripts used by the skill.
  - **reference.md**, **docs/**, **hooks/** or **rules/** (in the `*-user` skills): cheat-sheet, official docs in markdown (refreshable with `docs/update.sh`) and guards that block push, deploys and secret access.
  - **results/** or **tests/** (optional): evaluation and tests; they need not go into the agent's skills directory.
