---
name: animation-bauhaus
description: Animate ideas with disciplined geometric composition.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Bauhaus geometric animation

Make an argument with circles, rectangles, diagonals and negative space.
The geometry must change relationships, not merely decorate a slide.

## Use and avoid
- Use for problem framing, prioritization, bounded experiments and decisions.
- Use when a small vocabulary can express an idea without literal illustration.
- Avoid complex architecture requiring many named components.
- Avoid implying quantitative growth with unexplained rising bars.
- Historical design grammar is inspiration, not permission to reproduce artworks.

## Visual grammar
- Start with a warm paper field and one near-black structural ink.
- Assign separate functions to a circle, a square and a diagonal.
- Limit accents to three deliberate colors; retain brand legibility.
- Let asymmetry create balance: dense illustration opposite compact copy.
- Align text to a shared vertical edge rather than centering every element.
- Use solid fills and decisive edges; avoid gradients and soft UI shadows.
- Reserve thin rules for organization, thick strokes for the argument.
- Keep optical gaps between shapes even when their mathematical bounds align.
- Do not distort the authorized logo to fit the geometric vocabulary.

## Storyboard a twenty-second argument
1. At 0–5 seconds, introduce a meaningful arrangement of separate primitives.
2. At 5–10 seconds, place them in a bounded experiment or shared frame.
3. At 10–17 seconds, organize them into a clear next-step relationship.
4. At 17–20 seconds, use the shared static closing frame.
- Carry at least two primitives across beats so the transformation is legible.
- Finish the movement within roughly two seconds of each beat.
- Leave at least three seconds for reading each key message.
- Never spin or bounce an element merely because the timeline has spare time.

## Construct the scene
1. Read the [core workflow](../../SKILL.md) and verified content first.
2. Sketch the three arrangements using shape bounds and text bounds separately.
3. Create `scene.js` as a strict IIFE exposing `window.scene(t)`.
4. Call `A.frame(...)` first; draw only inside the creative safe region.
5. Use native Canvas rectangles, arcs, clipped groups and small path helpers.
6. Derive rotation and translation from absolute time with clamped easing.
7. Move one dominant relationship at a time; keep supporting copy stationary.
8. Measure every heading at its final font before approving its width.
9. Use at least 60 px for headings and 30 px for body text at 1080p.
10. Export a complete English narrative as `window.TRANSCRIPT`.
11. Let the runtime own readiness, controls, fonts, logos and the final CTA.
12. Follow the [runtime contract](../../references/runtime.md); add no dependencies.

## Evidence and rights
- Abstract geometry is still a claim when it resembles a chart or verdict.
- Label conceptual diagrams; do not invent percentages, outcomes or guarantees.
- Use original compositions instead of tracing a recognizable historical poster.
- Preserve font licenses and treat example branding separately from MIT code.
- The [T2S discovery example](../../examples/bauhaus/index.html) is not a universal brief.
- Consult [source and rights notes](../../references/sources.md) before adaptation.

## Inspect and export
- Test the missing scene contract before adding implementation.
- Inspect samples at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Check diagonal endpoints, clipping masks, gaps and optical balance at full size.
- Check that red, blue and yellow never compete with the headline hierarchy.
- Seek backward and compare identical-time frames byte-for-byte.
- Require loaded fonts, no browser errors and an unchanged 17–20 second CTA.
- Use an ephemeral headless browser, not a personal browser profile.
- From the package root, render with the canonical command:
```sh
python scripts/render.py examples/bauhaus/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the actual encoded video separately; PNG sampling does not prove motion quality.
