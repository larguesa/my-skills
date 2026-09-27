---
name: animation-single-line
description: Use when revealing continuous paths between systems.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Single-line motion

## Use and avoid
- Use for continuity, incremental change and connections between systems.
- Avoid for topology that requires explicit branching or multiple independent flows.
- Treat the unbroken line as a communication device, not an electrical schematic.

## Visual grammar
- Author one uninterrupted path from left to right.
- Form recognizable systems through repeated corners, loops and returns.
- Use a thin brand-colored stroke on a quiet near-white field.
- Keep pale guide lines subordinate to the principal path.
- Label structures outside the line field instead of inside small loops.
- Reserve two broad headline lines above the illustration.
- Avoid node circles and card boxes that turn the drawing into a generic graph.
- The line remains materially the same width across old and new structures.

## Storyboard
- 0–5 seconds: an existing structure begins the continuous path.
- 5–10 seconds: connectors and intermediate systems become legible.
- 10–17 seconds: complete the right-hand structure and hold the continuity claim.
- 17–20 seconds: shared runtime CTA, with no custom end-card transition.
- Introduce labels only when their associated structure has started to appear.

## Build the actual drawing
1. Sketch the complete path as an ordered list of original coordinates.
2. Walk every vertex to verify the pen never needs an unintended lift.
3. Return along deliberate segments when a box needs a closed outline.
4. Use the runtime's arc-length line helper for geometric reveal.
5. Never reveal one vertex per frame: unequal segments would change drawing speed.
6. Define progress from absolute time and clamp its final value.
7. Place labels on a separate horizontal baseline below the drawing.
8. Make optional background guides lighter and thinner than the hero stroke.
9. Preserve clearance around labels and generous space above the footer.
10. Verify the completed path with a high-resolution screenshot.

## Motion direction
- Let line reveal carry the motion; avoid simultaneous camera moves.
- Use a restrained ease so the viewer can follow the traveling endpoint.
- Start with a short visible segment to avoid an empty first frame.
- Finish the drawing early enough for a meaningful static reading hold.
- Keep transitions between text beats from erasing the line's continuity.

## Content and rights
- Ground any operational claim in the supplied service evidence.
- Do not imply a guaranteed zero-downtime migration from a visual connection.
- Label conceptual systems without inventing a client's architecture.
- Draw original structures; no traced proprietary system diagrams.

## QA pitfalls
- Crossing segments can suggest unintended connections.
- Backtracking too often makes a section look falsely heavier.
- Check arc-length reveal in nonsequential timestamp calls.
- Avoid labels that appear long before the corresponding structure.
- A path can be continuous yet semantically confusing; inspect at each beat.
- Confirm that the thin line survives downscaled mobile playback.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/single-line/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/single-line/index.html output.mp4 --duration 20 --fps 30`
