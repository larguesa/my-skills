---
name: animation-memphis
description: Use when animating playful patterned geometry.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Memphis motion

## Use and avoid
- Use for energetic product stories, recurring work and approachable change.
- Avoid for solemn testimony, dense financial analysis or precise schematics.
- Translate the design movement into original compositions, not copied posters.

## Visual grammar
- Build a sculpture from circles, triangles, striped blocks and zigzags.
- Choose cream, deep navy and two warm accents; retain a brand accent.
- Give every large shape a different silhouette, not just a different color.
- Put an asymmetric cluster opposite a quiet type column.
- Use dots in bounded patches, never across body copy.
- Draw stripes inside a rectangular shape with a saved local transform.
- Draw a ring as two filled circles when the backdrop is flat.
- Keep pattern strokes materially thicker than texture dots.
- Let an orbital rail suggest recurrence without labeling it as a measured cycle.

## Storyboard
- 0–5 seconds: a bold proposition beside independent geometric pieces.
- 5–10 seconds: pieces shift around a shared loop as the next need is named.
- 10–17 seconds: hold the assembled relationship and the practical takeaway.
- 17–20 seconds: let the shared runtime draw the stable brand CTA.
- Hold each key sentence at least three seconds after its entrance.

## Build the actual drawing
1. Sketch three distinct silhouettes before adding any text.
2. Reserve the left column for two headline lines and two short body lines.
3. Construct the loop with a native ellipse, not a stock animation asset.
4. Place shapes using fixed angles and a bounded eased rotation.
5. Use small angular rocking on local transforms; avoid camera shake.
6. Build a zigzag from alternating polyline vertices of equal spacing.
7. Place a single flat color strip under a supporting keyword.
8. Restrict decorative dot arrays to a separate lower-right patch.
9. Measure every sentence at its final font before committing the layout.
10. Check that motion never carries a shape into the logo or footer.

## Motion direction
- Favor quick arrivals followed by slow geometric drift.
- Give only one cluster a major movement during a sentence.
- Use cubic-out interpolation for reassembly, with no spring overshoot.
- Keep the typography still while ornaments rock gently.
- A shape moving on a rail is metaphor, not a claim of operational throughput.

## Content and rights
- Obtain permission for brand assets and preserve font licenses.
- Use source-supported service descriptions rather than invented outcomes.
- Do not borrow an identifiable designer's poster or proprietary illustration.
- In the example, geometry represents recurring engineering, not telemetry.

## QA pitfalls
- Ring holes must retain the actual background color.
- Rotated squares need clearance beyond their unrotated bounding box.
- Dots must remain visible without turning into moire at delivery resolution.
- Inspect pauses as compositions, not only the moving sequence.
- Avoid a visual hierarchy where confetti wins over the headline.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/memphis/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/memphis/index.html output.mp4 --duration 20 --fps 30`
