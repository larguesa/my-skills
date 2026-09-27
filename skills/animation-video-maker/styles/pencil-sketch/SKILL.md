---
name: animation-pencil-sketch
description: Draw graphite-style systems studies with Canvas.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Pencil-sketch animation

Present an idea as a considered working study: exploratory lines, clear relationships.
Use procedural graphite marks, not a claim of filmed hand drawing.

## Use and avoid
- Use for architecture exploration, incremental change and early concept design.
- Make existing structures visible before proposing additions.
- Avoid implying an unapproved sketch is an as-built technical drawing.
- Choose clean vector diagrams when precise coordinates are the actual content.

## Graphite vocabulary
- Start with warm off-white paper and a dark neutral graphite line.
- Use one restrained colored annotation to distinguish the current point.
- Combine a principal line with two faint, slightly displaced companions.
- Keep displacement below a few pixels at Full HD, not a cartoon wobble.
- Hatch along a consistent material direction to describe surface depth.
- Cross-hatch selected shadows, never every interior space.
- Vary line weight by function: silhouette, subdivision, construction mark.
- Leave objects unfilled when their relationship matters more than their volume.
- Preserve clean label zones outside the illustrative boxes.
- Avoid decorative rulers or measurements that imply unsupported precision.

## Storyboard
1. Identify the existing structure in its final position.
2. Add the boundary or adapter that enables change.
3. Draw the new capability on the far side of the connection.
4. Group the complete study with a light enclosing annotation.
5. Hold the study before the shared closing card.

## Motion
- Reveal primary outlines before their hatching and internal divisions.
- Draw long connections steadily over about one second.
- Keep graphite marks stationary once drawn; fixed imperfections feel intentional.
- Change a short explanatory caption only at major reasoning boundaries.
- Give each caption at least three seconds of unhurried reading time.
- Avoid hand cursors unless they materially clarify the drawing order.

## Implementation
1. Read the [core instructions](../../SKILL.md) and verify the proposed relationship.
2. Compose all objects and connectors on a single coordinate plan.
3. Separate illustration bounds from label and annotation baselines.
4. Use `A.frame` first; keep scene content within x96–1824, y200–930.
5. Build a sketch helper using a fixed displacement formula for each stroke.
6. Pass explicit reveal progress to `A.line` for true length-based drawing.
7. Add hatching as short clipped or bounded line segments.
8. Draw paper grain with a stable index formula; never animate its seed.
9. Reveal additions through `t` without storing drawing history.
10. Set headings at least 60px and labels at least 30px in loaded fonts.
11. Supply `window.TRANSCRIPT` and rely on the [shared runtime](../../references/runtime.md).

## Review and export
- Start from a failing missing-scene check, then exercise the actual player.
- Save frames at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect hatching at full resolution and thumbnail scale.
- Look for moire, muddy outlines and labels lost among construction marks.
- Check connectors stop at boundaries rather than penetrating caption text.
- Test that partial reveals do not suggest a misleading completed connection.
- Verify fonts, JavaScript errors, deterministic seeking and the held CTA.
```sh
python scripts/render.py examples/pencil-sketch/index.html output.mp4 --duration 20 --fps 30
```
- Check the encoded video's actual timing and image quality before publication.

## Truth and rights
- Mark diagrams as conceptual when viewers might infer a deployed architecture.
- Do not invent interface contracts, product capabilities or migration guarantees.
- Draw original geometry; do not trace confidential drawings or third-party art.
- Keep factual provenance in the [source notes](../../references/sources.md).
- The [modernization example](../../examples/pencil-sketch/index.html) uses an original system–API–capability study.
- It illustrates service scope, not an actual customer's infrastructure.
