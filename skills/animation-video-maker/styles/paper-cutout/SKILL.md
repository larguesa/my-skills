---
name: animation-paper-cutout
description: Create layered paper-cutout animation with Canvas.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Paper-cutout animation

Build an original paper theatre: separate shapes, imperfect edges, visible layering.
The medium is procedural Canvas2D, not photographed paper or a physical craft shoot.

## Use and avoid
- Use for growth, assembly, stewardship, learning and human-scale explanations.
- Use depth to explain dependencies rather than to decorate unrelated copy.
- Avoid photoreal product claims, dense interfaces and quantitative comparisons.
- Choose another style when exact technical geometry is the message.

## Visual grammar
- Limit the scene to cream stock, three paper colors and a dark text ink.
- Draw each piece as a closed polygon with a few deliberate off-axis vertices.
- Keep cut edges legible; do not turn every edge into random saw teeth.
- Use one soft shadow direction throughout the composition.
- Draw back layers first: ground, stem, foliage, foreground labels.
- Put a narrow pale edge on selected front pieces, not on every polygon.
- Simulate fibres with fixed small marks at low opacity.
- Keep texture off logos and reduce it behind body text.
- Set cards slightly irregular while leaving their text unrotated.
- Preserve a large quiet region around the main metaphor.

## Storyboard
1. Establish the proposition and a single incomplete paper object.
2. Add a structural layer that gives the object meaning.
3. Add one related concept per card; retain earlier cards for comparison.
4. Complete the object and hold the accumulated explanation.
5. Hand off to the shared static end card.

## Motion direction
- Move pieces along short paths into their final layer order.
- Resolve a landing in roughly 0.6–1.0 seconds, then stop completely.
- Offset related pieces by 0.2–0.6 seconds so assembly can be followed.
- Let a stem grow before its leaves; do not scale the entire poster.
- Keep each completed message readable for at least three seconds.
- Avoid perpetual bobbing: the paper should feel placed, not weightless.

## Implementation procedure
1. Read the [package workflow](../../SKILL.md) and verify the message source.
2. Sketch final silhouettes at 1920×1080 before animating their entrance.
3. Allocate separate art and text regions inside x96–1824, y200–930.
4. Call `A.frame` first and preserve its branding and footer bands.
5. Make one local polygon helper that balances every save and restore.
6. Fix fibre positions using integer index arithmetic, never random calls.
7. Derive each layer's progress from `t` and a named entrance time.
8. Draw text after its card; use at least 30px body and 60px headings.
9. Measure the longest label in the final font; shorten rather than squeeze.
10. Provide the complete narrative in `window.TRANSCRIPT`.
11. Follow the [runtime contract](../../references/runtime.md), without replacing it.

## QA and export
- First verify the missing scene fails the player contract test.
- Capture actual frames at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect final shadows for doubled edges or accidental dark blobs.
- Check that leaves do not grow through titles during intermediate frames.
- Verify identical pixels after out-of-order seeks and local font loading.
- Inspect the full composition at thumbnail size as well as at 100%.
- Export from the package root only after the visual checks pass:
```sh
python scripts/render.py examples/paper-cutout/index.html output.mp4 --duration 20 --fps 30
```
- Check the encoded video's dimensions, duration and temporal motion separately.

## Truth, rights and example
- A growth metaphor is not evidence of revenue, adoption or measured improvement.
- Use authorized logos and licensed fonts; do not trace someone else's collage.
- Source factual language through the [source notes](../../references/sources.md).
- The [Managed Evolution example](../../examples/paper-cutout/index.html) uses an original paper plant.
- Its brand and service copy belong to the example, not to this generic style.
