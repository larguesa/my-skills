---
name: animation-comic-book
description: Tell a professional story through original comic panels.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Original editorial comic animation

Tell a short argument through sequential panels and readable illustrative action.
Use comic grammar without copying a named artist, franchise or recognizable character.

## Use and avoid
- Use for a challenge, an intervention and an accountable decision.
- Use when visual contrast makes a technical trade-off approachable.
- Avoid trivializing safety incidents, vulnerable people or serious customer harm.
- Avoid superheroes as shorthand for unbounded capability.
- Do not treat an energetic style as permission to invent a success story.

## Panel language
- Establish a clear left-to-right reading order and visibly separated gutters.
- Angle one panel edge for energy while keeping caption baselines horizontal.
- Use heavy dark contours, a paper base and restrained accent fills.
- Clip halftone dots to the illustrated area, never across body copy.
- Choose one dominant silhouette per panel so it survives downscaling.
- Separate narration bands from the action; speech balloons are optional.
- Use a burst to emphasize an action, not to imply measured performance.
- Design original people and tools from simple geometric shapes.
- Keep expressive drawing subordinate to the actual professional message.

## Three-panel timing
1. At 0–5 seconds, introduce the challenge in the first panel.
2. At 5–10 seconds, reveal examination or intervention in the second.
3. At 10–17 seconds, reveal the responsible decision in the third.
4. At 17–20 seconds, leave the page for the shared static branded CTA.
- Earlier panels remain visible so the viewer can reconstruct the argument.
- Unrevealed panels should be quiet paper, not ghosted text competing for attention.
- Use a short entrance within a panel, then hold its caption for at least three seconds.
- Do not zoom the whole page if that makes the reading order unstable.

## Draw the page
1. Read the [core workflow](../../SKILL.md) and reduce the story to three truthful beats.
2. Allocate panel polygons, gutters, illustration boxes and caption bands.
3. Construct silhouettes using original polygons, arcs and polyline details.
4. Draw each panel fill, save context, clip to its polygon and draw the action.
5. Add a fixed halftone pattern behind the action with low-opacity ink.
6. Limit movement to the illustration group; do not slide captions while reading.
7. Restore context and redraw the panel border to keep its edge crisp.
8. Measure every caption inside its narrowest available panel width.
9. Use at least 30 px supporting text and 60 px for the page headline.
10. Export strict-IIFE `window.scene(t)` and the complete English `window.TRANSCRIPT`.
11. Call `A.frame(...)` first and leave logo, footer and closing frame unobstructed.
12. Use the [runtime contract](../../references/runtime.md), not another animation loop.

## Responsible storytelling
- Show review as an activity, not as proof of approval or perfect safety.
- A pictured person is an illustrative role unless explicitly sourced otherwise.
- Never invent client quotes, incidents, before/after results or telemetry.
- Use authorized branding and licensed fonts; create character silhouettes yourself.
- Review [sources and rights](../../references/sources.md) before adapting the scenario.
- The [quality example](../../examples/comic-book/index.html) is a conceptual story, not a case study.

## QA and export
- First demonstrate that the scene-contract test detects a missing implementation.
- Inspect frames at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Check narrow caption bands, angled gutters and clipping at entrance offsets.
- Inspect the final page in grayscale to verify silhouette and reading hierarchy.
- Check that halftone dots do not merge into distracting interference at small sizes.
- Verify fonts, no page errors, deterministic seeking and a static closing frame.
- Use an ephemeral browser without saved accounts or remote assets.
- Render from the package root:
```sh
python scripts/render.py examples/comic-book/index.html output.mp4 --duration 20 --fps 30
```
- Review the encoded result for pacing rather than claiming full QA from PNGs alone.
