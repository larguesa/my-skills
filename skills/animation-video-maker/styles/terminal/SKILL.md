---
name: animation-terminal
description: Use when animating explicitly illustrative terminal UI.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Terminal explanation

## Use and avoid
- Use for technical audiences and explanatory control surfaces.
- Avoid when a simulated console could be mistaken for audit evidence.
- Never present invented command output as a completed test or deployment.

## Visual grammar
- Use a dark blue-black field, off-white text and a restrained mint accent.
- Keep large proportional headlines outside the monospace console.
- Build a console frame with a persistent illustrative-status banner.
- Prefer a compact definition list over a wall of scrolling text.
- Highlight one row without using success colors or a pass icon.
- Separate short domain labels from longer explanations in two aligned columns.
- Write pseudocommands that are explicitly labeled non-executable.
- Do not display shell prompts containing real usernames, hosts or paths.

## Storyboard
- 0–5 seconds: type an explanatory pseudocommand under a clear disclaimer.
- 5–10 seconds: reveal the complete control-surface vocabulary.
- 10–17 seconds: hold human review as the accountability point.
- 17–20 seconds: let the shared runtime draw the CTA.
- The transcript must state that no commands ran and no results are claimed.

## Build the actual drawing
1. Begin with a persistent banner reading illustrative or simulated.
2. Reserve a separate line that identifies the command as non-executable.
3. Draw the terminal as native rectangles; do not capture a personal shell.
4. Store authored rows as fixed label-and-explanation pairs.
5. Derive typed character count from absolute time, bounded by string length.
6. Reveal rows deterministically without timers, subprocesses or network calls.
7. Use sufficient column separation for the longest domain label.
8. Keep at least 30-pixel monospace text in a Full HD composition.
9. Leave the full explanation visible rather than scrolling away its context.
10. Display a second plain-language disclaimer near the console base.

## Motion direction
- Type the command quickly enough that the proposition is not delayed.
- Reveal explanatory rows at a steady cadence, never as frantic fake logs.
- Avoid blinking cursors during long holds and avoid flashing status text.
- Move emphasis from scope to accountability, not from failure to fabricated pass.
- Do not count up coverage, throughput or test totals without real source data.

## Content and rights
- Redact credentials, tokens, internal paths and personal hostnames.
- Real logs require authorization and faithful preservation of context.
- Generated examples must never be called measured evaluation results.
- A named service capability is different from a demonstrated outcome.

## QA pitfalls
- Confirm that both the opening and final explanatory frames retain disclaimers.
- Long monospace strings can exceed the console even at modest font sizes.
- Check row highlights do not reduce contrast or cover glyph descenders.
- Test partial typing for truncation that accidentally reads as executable advice.
- Keep the terminal illustration clear of the shared brand footer.
- Measure glyph descenders: a safe baseline alone does not guarantee safe text bounds.
- No browser actions may execute the pseudocommand.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/terminal/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/terminal/index.html output.mp4 --duration 20 --fps 30`
