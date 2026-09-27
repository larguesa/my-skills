---
name: animation-clay
description: Build procedural clay-inspired animated objects.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Clay-inspired animation

Create approachable, weighty objects with rounded silhouettes and stepped movement.
This is native Canvas2D emulation, not real clay, photography or stop-motion footage.

## Use and avoid
- Use for modular growth, care, repair and tangible explanations of abstract work.
- Let the sculptural metaphor carry one relationship at a time.
- Avoid claims about physical product material, manufacture or surface quality.
- Avoid complicated perspective: simple frontal maquettes survive small screens.

## Material grammar
- Use broad rounded masses rather than thin vector strokes.
- Favor muted mineral colors against a warm studio-like background.
- Add a restrained directional gradient to suggest a kneaded surface.
- Keep highlights broad and matte, never chrome-like or wet.
- Place a soft contact shadow under every weight-bearing object.
- Make settled modules touch: a shadow is not physical contact.
- Overlap touching silhouettes slightly to avoid hairline gaps after scaling.
- Keep one light direction for all modules, including small decorative markers.
- Use a shallow ground ellipse to establish the sculpture's resting plane.
- Keep labels outside the sculpture rather than embossing tiny text into it.

## Storyboard
1. Establish a stable foundation and the main proposition.
2. Place one warm-colored module for the first capability.
3. Add a complementary module for the next capability.
4. Set a cap or joining piece to complete the relationship.
5. Hold the composed object and then use the common static CTA.

## Timing and physicality
- Quantize object movement with `floor(t * 12) / 12` for a restrained stepped cadence.
- Derive quantized time from `t`; never count animation callbacks.
- Let an arrival take 1.2–1.6 seconds, then rest.
- Reduce rotation as an object approaches its supporting surface.
- Avoid elastic rubber bouncing: clay has weight and does not endlessly spring.
- Keep type unwarped, with at least three seconds to read each key message.

## Implementation procedure
1. Follow the [package workflow](../../SKILL.md) and define the metaphor's limits.
2. Draw the final settled arrangement before planning any entrances.
3. Record each module's bounding box and intended support contact.
4. Call `A.frame` first and reserve x96–1824, y200–930 for scene content.
5. Implement a local rounded-mass helper with balanced save and restore.
6. Clear shadow settings inside that helper so typography remains sharp.
7. Use local coordinates for rotation and highlights.
8. Animate only position, small rotation and optional subtle shape compression.
9. Keep headings at least 60px and body labels at least 30px.
10. Use the [runtime contract](../../references/runtime.md) and provide a full transcript.
11. Explain procedural emulation in accompanying copy when authenticity matters.

## QA and export
- Verify a missing scene fails before implementing it.
- Render the player at 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect every settled contact at full resolution, not just its shadow.
- Add a pixel or geometry regression test for a discovered floating module.
- Check transient entrance bounds against headings and brand bands.
- Inspect gradients for banding and overlapping shadows for dirty seams.
- Repeat timestamps out of order and verify identical pixels and loaded fonts.
```sh
python scripts/render.py examples/clay/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the encoded motion: stills cannot validate the stepped cadence.

## Content and rights
- Do not imply a real studio shoot, model maker or material manufacturer.
- Do not reproduce a recognizable third-party character or toy design.
- A growing sculpture must not imply guaranteed business growth.
- Check claims against the [source notes](../../references/sources.md).
- The [Managed Evolution example](../../examples/clay/index.html) assembles an original modular sculpture.
- Its service narrative is example-specific, not part of the generic technique.
