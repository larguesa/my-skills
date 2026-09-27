---
name: animation-linocut
description: Animate bold relief-print forms and carved marks.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Linocut animation

Build a high-contrast editorial image from ink masses and light carved channels.
This is procedural relief-print emulation, not a scan of a physical print.

## Use and avoid
- Use for continuity, infrastructure, resilience and a strong editorial proposition.
- Choose one iconic silhouette that reads before its details are visible.
- Avoid delicate UI, photographic portraiture and dense quantitative dashboards.
- Do not imply archival provenance through artificial print imperfections.

## Relief-print grammar
- Begin with warm paper, one dark ink and at most one accent ink.
- Draw large filled silhouettes rather than graphite-like outlines.
- Carve light marks into those masses using the paper color.
- Align channels with the form: vertical for piers, diagonal for beams.
- Vary the channel lengths and spacing slightly, but keep their logic legible.
- Use a few irregular polygon corners to suggest cutting pressure.
- Preserve solid ink areas so the carving has contrast and weight.
- Keep accidental distress out of labels and brand marks.
- Do not replace carved channels with a generic grain overlay.
- Use the accent ink on one structural part that carries narrative meaning.

## Storyboard
1. Establish separated anchors and the main proposition.
2. Reveal a joining silhouette that connects the anchors.
3. Name the kind of connection above the assembled image.
4. Add the practical principle below it without covering the illustration.
5. Hold the print as a complete poster before the shared closing card.

## Motion direction
- Reveal broad ink shapes through a directional mask, like a controlled print pass.
- Keep the paper and carved marks fixed in world coordinates.
- Complete the primary image over roughly two seconds.
- Add captions on later beats with restrained opacity changes.
- Hold each key statement for at least three seconds.
- Avoid rubbery shape morphs: the image should retain carved solidity.
- Do not shake the image to suggest fake historical footage.

## Construction procedure
1. Read the [core workflow](../../SKILL.md) and select an accurate visual metaphor.
2. Design the completed silhouette in black and white before adding accent ink.
3. Allocate protected label bands above and below the relief image.
4. Call `A.frame` first and preserve the art region x96–1824, y200–930.
5. Build dark masses with original polygon coordinates.
6. Cut channels using paper-colored strokes contained inside those masses.
7. Mask the joining shape with a rectangle whose width comes from `t`.
8. Balance save and restore around each clip so labels remain unrestricted.
9. Keep fixed ink speckles sparse, and never place them over the brand.
10. Use display headings of at least 60px and labels of at least 30px.
11. Add the full `window.TRANSCRIPT` and use the [shared runtime](../../references/runtime.md).

## QA and export
- Observe the missing-scene failure before creating the drawing.
- Render 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds from the player.
- Examine carved lines at 100% for broken channels and accidental crossings.
- Check thumbnail readability: the silhouette must survive loss of texture detail.
- Inspect both ends of a joining structure for unintended gaps after reveal.
- Ensure accent ink and paper still contrast when seen in grayscale.
- Verify fonts, page errors, repeated-seek equality and a static final CTA.
```sh
python scripts/render.py examples/linocut/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the encoded print reveal for flicker, moire and timing problems.

## Rights and evidence
- Create original relief imagery; do not trace a print artist's composition.
- A bridge metaphor is not evidence of interoperability or guaranteed uptime.
- Identify illustrative geometry honestly when operational inference is possible.
- Use the [source notes](../../references/sources.md) for factual claims.
- The [modernization example](../../examples/linocut/index.html) uses an original carved bridge motif.
- Its labels describe service scope rather than an actual deployment diagram.
