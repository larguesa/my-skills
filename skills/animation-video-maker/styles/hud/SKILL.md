---
name: animation-hud
description: Explain controls with honest instrument-like interfaces.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Conceptual HUD animation

Use instrument geometry to organize controls, categories and responsibility.
An interface illustration must never masquerade as measured system state.

## Use and avoid
- Use for control surfaces, observability scope and review responsibilities.
- Use when an overview and a focused explanation need to coexist.
- Avoid invented dashboards with percentages, latency values or green health badges.
- Avoid radar sweeps that imply real surveillance or detected events.
- Avoid decorative code, fake logs and unreadably dense instrumentation.

## Instrument grammar
- Build a dark field with quiet structural blue and one bright focus accent.
- Use concentric rings for grouping, not automatic numerical measurement.
- Divide a ring into categorical segments without fabricated scales or units.
- Keep minor ticks subdued; no viewer should need to count them.
- Pair an overview on one side with a larger editorial detail on the other.
- Place labels outside the circular geometry and leave clean radial gutters.
- Match the highlighted category to the detail text in the same frame.
- Keep all names horizontal and readable without rotating the viewer's head.
- Use corner brackets and rules sparingly; avoid luminous clutter.

## Focus sequence
1. At 0–5 seconds, assemble the overview and focus the first responsibility.
2. At 5–10 seconds, change focus to a complementary responsibility.
3. At 10–17 seconds, connect the overview to accountable human review.
4. At 17–20 seconds, hold the shared clean CTA with no instrument motion.
- Reveal arcs once rather than spinning rings endlessly.
- Keep the complete category map stable while the editorial focus changes.
- Let the focused sentence hold for at least three seconds.
- A focus shift means attention, not a change in actual operational health.

## Implementation steps
1. Read the [core workflow](../../SKILL.md) and classify each input as fact or illustration.
2. Choose category names before constructing any radial divisions.
3. Allocate the circle, external labels, detail column and disclosure line.
4. Draw arcs with native Canvas paths; use absolute-time easing for one-time assembly.
5. Map each editorial phase explicitly to its category index.
6. Use that same active index for the arc, marker and label accent.
7. Test the mapping by recording label colors at representative phase times.
8. Do not use live-state words such as healthy, approved or passed without evidence.
9. Use at least 60 px for main headings and 30 px for explanatory labels.
10. Expose `window.scene(t)` in a strict IIFE and call `A.frame(...)` first.
11. Publish the complete English `window.TRANSCRIPT`, including the illustrative disclaimer.
12. Follow the [runtime contract](../../references/runtime.md); do not add a polling loop.

## Truth, consent and rights
- State visibly that the interface is conceptual and not live telemetry.
- If real data is later provided, preserve its units, date, source and uncertainty.
- Never fabricate a measured quantity to make an otherwise sparse interface look active.
- Do not reveal secrets, actual access tokens or private operational identifiers.
- Use original UI geometry, licensed fonts and authorized logos.
- Consult [source notes](../../references/sources.md).
- The [quality example](../../examples/hud/index.html) is categorical and contains no performance metrics.

## QA and rendering
- Run a missing-scene contract test before implementation and rerun after changes.
- Inspect frames at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Compare the active label with the editorial heading at each phase boundary.
- Check tick contrast, ring-label clearance and the disclosure's full-size legibility.
- Check that decorative marks cannot reasonably be read as a numeric chart.
- Verify font loading, no JavaScript errors and equal output after backward seeking.
- Verify identical CTA frames across the final three seconds.
- Use a clean ephemeral browser and render from the package root:
```sh
python scripts/render.py examples/hud/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the encoded video separately for arc motion and focus-change pacing.
