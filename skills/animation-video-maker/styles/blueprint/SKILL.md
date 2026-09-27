---
name: animation-blueprint
description: Draft technical relationships with explicit boundaries.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Animated technical blueprint

Construct a readable technical relationship from boundaries, routes and annotations.
The drafting aesthetic does not turn a conceptual diagram into deployed architecture.

## Use and avoid
- Use for system scope, dependencies, safeguards and review boundaries.
- Use when an outside reviewer needs to understand what belongs inside a system.
- Avoid decorative dimensions that look like verified engineering measurements.
- Avoid neon-heavy science fiction when the purpose is operational clarity.
- Avoid more labels than the reading time can support.

## Drafting grammar
- Choose a deep technical blue, a quiet grid and bright structural linework.
- Establish three weights: grid, component contour and highlighted relationship.
- Use dashed lines for conceptual boundaries, never arbitrary emphasis.
- Add center marks or registration crosses only at meaningful reference points.
- Separate connectors from boxes by visible entry and exit gaps.
- Use orthogonal routes where they make dependencies easier to trace.
- Keep annotations horizontal; technical drawing is not an excuse for tiny text.
- Give the human review boundary its own location outside automated activity.
- Do not enclose a component just to fill an empty patch of the grid.

## Construction sequence
1. At 0–4 seconds, establish scope and the first control.
2. At 4–8 seconds, reveal a related control and its connector.
3. At 8–11 seconds, complete the complementary controls.
4. At 11–17 seconds, add the review gate and hold the complete relationship.
5. At 17–20 seconds, use the shared static close.
- Structure should appear before its explanatory label becomes necessary.
- Give each label at least three seconds of stable reading time.
- Avoid endless travelling pulses that imply monitored live traffic.

## Implementation procedure
1. Read the [core workflow](../../SKILL.md) and distinguish facts from diagram metaphors.
2. Plan all component rectangles, connector channels and annotation gutters.
3. Use a single coordinate system with generous spacing between unrelated routes.
4. Implement strict-IIFE `window.scene(t)` with `A.frame(...)` as its first call.
5. Draw the grid only within the reserved creative area.
6. Reveal paths with `A.line` using absolute-time progress and true path length.
7. Do not stroke zero-progress paths; this prevents premature endpoint dots.
8. Wrap dashed boundaries in balanced `save()` and `restore()` calls.
9. Keep labels at least 30 px and the principal headline at least 60 px.
10. Place route intersections intentionally; separate crossing from joining.
11. Export a complete English `window.TRANSCRIPT` describing the actual relation.
12. Retain shared controls, readiness and CTA behavior from the [runtime](../../references/runtime.md).

## Content truth and rights
- Label a conceptual control diagram as conceptual in the visible frame.
- Do not fabricate certifications, security guarantees or deployed topology.
- A human gate is a responsibility metaphor, not proof that a release passed review.
- Base control descriptions on verified scope rather than imagined capabilities.
- Use original geometry and preserve licensed fonts and authorized brand assets.
- Consult [source notes](../../references/sources.md) before adapting the copy.
- The [quality example](../../examples/blueprint/index.html) is illustrative, not a system specification.

## QA and delivery
- Establish a failing scene-contract test before implementing the drawing.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds in an ephemeral browser.
- Inspect partial outlines, dashed perimeters and all connector junctions.
- Ensure no route crosses a word and no label touches the boundary it describes.
- Verify diagram art stays below branding and above the footer.
- Test font readiness, no JavaScript errors, non-sequential seeks and a static CTA.
- Check the complete diagram at 1080p; contact sheets may hide thin-line defects.
- From the package root:
```sh
python scripts/render.py examples/blueprint/index.html output.mp4 --duration 20 --fps 30
```
- Confirm encoded output separately; sample review is not a full motion review.
