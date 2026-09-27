---
name: animation-film-documentary
description: Build editorial sequences with procedural film texture.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Procedural film documentary

Use framing, editorial cuts and restrained texture to explain operating context.
This is a procedural film aesthetic, not real 16 mm stock or archival footage.

## Use and avoid
- Use for modernization, institutional context, continuity and changing systems.
- Use when an editorial sequence explains more than a dense process chart.
- Avoid fabricated eyewitness scenes, invented historical records or fake timestamps.
- Avoid dramatic footage whose mood makes a stronger claim than the evidence.
- Without licensed footage, construct original schematic imagery and say so.

## Build an editorial image language
- Choose a charcoal field, warm off-white linework and one restrained accent.
- Draw a film gate with consistent margins, not a full-screen decorative border.
- Keep perforations outside the picture aperture and away from captions.
- Reserve a clean lower caption area rather than texturing the entire canvas.
- Use establishing view, connective detail and synthesis as distinct shot scales.
- Carry a baseline, route or object silhouette between shots for continuity.
- Distinguish the look of an old recording from a factual claim of provenance.
- Keep text and branding steady even if the picture has subtle camera movement.
- Treat grain as low-opacity texture, never as flicker that drives attention.

## Editorial timing
1. At 0–5 seconds, show the environment and establish what already exists.
2. At 5–10 seconds, cut closer to a connection or intervention.
3. At 10–17 seconds, compare complementary responsibilities or next steps.
4. At 17–20 seconds, hold the runtime's clean branded close.
- Let each shot settle before changing its explanatory sentence.
- Prefer a slow push of a few percent over simulated handheld shaking.
- Use straight cuts when the argument changes; avoid arbitrary crossfades.
- Keep every key caption on screen for at least three seconds.

## Construct original plates
1. Start with the [core workflow](../../SKILL.md) and a source-grounded shot list.
2. Identify the exact point of each image before drawing any grain.
3. Draw system racks, documents or connections using original Canvas geometry.
4. Add a picture-aperture clipping path and balance `save()` with `restore()`.
5. Apply camera transforms only inside that clipped picture group.
6. Make texture coordinates deterministic and independent of frame history.
7. Add no actual date, location or archive identifier without verified provenance.
8. Place headings at 60 px or larger and supporting text at 30 px or larger.
9. Export `window.scene(t)` and an English `window.TRANSCRIPT` from a strict IIFE.
10. Call `A.frame(...)` first and keep art between the reserved header and footer.
11. Use [shared runtime behavior](../../references/runtime.md), not another clock.
12. Test at both cuts and at the maximum camera scale for clipping.

## Content and permissions
- A schematic server bank is illustrative, not a photographed client deployment.
- Do not use grain to make invented evidence appear authoritative.
- Obtain rights for any later footage, music, voice or identifiable person.
- Preserve licensed fonts and authorized brand assets without recoloring logos.
- See [source and rights notes](../../references/sources.md).
- The [modernization example](../../examples/film-documentary/index.html) uses original diagrams only.

## Practical QA
- Prove the scene contract fails before implementation, then rerun it after changes.
- Inspect samples at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect grain at full resolution; downscaled contact sheets can hide heavy noise.
- Check that the push never clips a rack, diagram label or picture aperture.
- Check caption contrast without relying on the film border to provide separation.
- Verify fonts, no JavaScript errors, offline assets and out-of-order determinism.
- Ensure the last three seconds are static and have no residual film effect.
- Use a clean ephemeral browser rather than a signed-in profile.
- Render from the package root:
```sh
python scripts/render.py examples/film-documentary/index.html output.mp4 --duration 20 --fps 30
```
- Verify encoded motion and metadata separately from still-frame inspection.
