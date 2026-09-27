---
name: animation-pixel-art
description: Use when animating grid-based sprites and stepped motion.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Pixel-art motion

## Use and avoid
- Use for discrete changes, maintenance journeys and small-system metaphors.
- Avoid where visual realism, exact device interfaces or fine curves matter.
- Create original sprites; do not imitate a recognizable game world.

## Visual grammar
- Establish one logical grid, such as 16 pixels in a Full HD canvas.
- Construct silhouettes from occupied cells in short binary row strings.
- Use flat fills without anti-aliased curves for the illustrated world.
- Keep brand typography smooth and readable instead of pixelating body copy.
- Limit the sprite palette to dark structure, green foliage and one warm token.
- Build an uninterrupted ground plane to anchor the scene.
- Use modular blocks with intentional negative-space doors and windows.
- Never introduce scores, health bars or coins that could imply measured gains.

## Storyboard
- 0–5 seconds: establish a small landscape and the first-release proposition.
- 5–10 seconds: populate another part of the world with an integration metaphor.
- 10–17 seconds: hold the complete environment and name ongoing stewardship.
- 17–20 seconds: switch to the runtime's shared static CTA.
- Keep the scene explanatory, not a pretend playable game.

## Build the actual drawing
1. Choose a logical grid before placing any terrain or sprite.
2. Encode each sprite as rows of zeroes and ones in original source code.
3. Iterate rows and columns, drawing only occupied grid cells.
4. Snap all sprite movement with floor or round applied to time-derived steps.
5. Construct terrain with repeated tiles, not scaled photographic textures.
6. Use separate colors for buildings, living elements and the moving token.
7. Place readable labels above the landscape, outside sprite travel lanes.
8. Derive sprite arrival from time; never append sprites frame by frame.
9. Align the lowest occupied sprite cell with the top of the ground plane.
10. Test low-resolution previews for accidental silhouette mergers.

## Motion direction
- Use discrete frame positions rather than continuous subpixel translation.
- Move a delivery token along a fixed track without implying completion.
- Reveal buildings in ordered beats while the text holds still.
- A lower drawing cadence can be simulated at a normal export frame rate.
- Avoid flashing tile colors, collectible counts and rapid full-screen cuts.

## Content and rights
- State when the environment is illustrative rather than product footage.
- Do not use extracted game sprites, maps, logos, audio or character likenesses.
- Verify any improvement claim independently of the metaphor.
- Keep role, capacity and outcome statements tied to the service source.

## QA pitfalls
- Fractional scaling introduces inconsistent pixel widths.
- A sprite that clips into the ground looks like a rendering error.
- Check the first frame: the world should read before all elements arrive.
- Test long labels against their exact tile-strip width.
- Inspect intermediate steps for unintended jumps across the safe area.
- Never let decorative pixelation degrade the official logo.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/pixel-art/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/pixel-art/index.html output.mp4 --duration 20 --fps 30`
