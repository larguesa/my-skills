---
name: animation-retro-70s
description: Use when animating warm print bands and slow reveals.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Retro 1970s motion

## Use and avoid
- Use for reflective discovery, gradual convergence and warm editorial stories.
- Avoid when nostalgia would undermine urgency or contemporary evidence.
- Borrow broad period grammar, not an existing album cover or brand campaign.

## Visual grammar
- Use warm paper, dark brown, burnt orange, mustard and muted olive.
- Create parallel rounded bands with mathematically related arc radii.
- Give typography broad, heavy forms while preserving licensed house fonts.
- Balance a dense band illustration with a generous open text column.
- Add sparse fixed overprint marks rather than animated film scratches.
- A seal can name an output, but must not resemble a certification badge.
- Use flat color and light procedural print texture, not fake archival footage.
- Keep brand colors in a subordinate band if the project requires them.

## Storyboard
- 0–5 seconds: state the question worth pursuing beside an open horizon.
- 5–10 seconds: name the hypothesis and prototype with a slow seal change.
- 10–17 seconds: hold the plan and the next decision.
- 17–20 seconds: allow the shared brand CTA to replace the illustration.
- Use deliberate five-second editorial beats, not a fast montage.

## Build the actual drawing
1. Reserve a left type column and a right band field with no overlap.
2. Specify a common arc center and reduce radius by the band pitch.
3. Set band width smaller than pitch so paper gutters remain visible.
4. Draw a vertical stem, quarter-circle arc and horizontal exit per band.
5. Use round caps consistently on all printed strokes.
6. Clamp the outermost arc to the creative area below the branding.
7. Generate fixed texture coordinates through deterministic modular arithmetic.
8. Set texture opacity low enough that typography remains clean.
9. Draw a plain circular output seal with a modest eased settling rotation.
10. Keep the seal clear of the headline and readable against the bands.

## Motion direction
- Reveal the bands with a dash length derived from stem, arc and exit lengths.
- Stagger starts slightly, then leave the complete band field still.
- Prefer a gentle settling rotation to perpetual ornament spinning.
- Replace complete phrases on measured cuts while the bands anchor continuity.
- Let the final output hold longer than its entry transition.
- Never fake mechanical film jitter with random per-frame coordinates.
- Keep this procedural print interpretation explicit when describing the work.

## Content and rights
- Use cleared fonts and original band construction.
- Do not present the artwork as historical footage or authentic printed material.
- An output seal names a deliverable, not a guarantee of certification.
- Separate a credible production path from a claim of production already achieved.

## QA pitfalls
- Small inner radii can collapse the gutters between adjacent bands.
- Large outer arcs can trespass into the service-title row.
- Warm colors still require sufficient contrast on cream backgrounds.
- Check that a circular seal does not mask a critical path label.
- Texture must remain subtle after video compression.
- Inspect the still composition without texture to confirm hierarchy.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/retro-70s/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/retro-70s/index.html output.mp4 --duration 20 --fps 30`
