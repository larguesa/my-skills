# Motion construction and continuity

Use motion to change a relationship. Choose one dominant mechanism per beat and keep supporting information still. These formulas describe new scene construction, not additional methods guaranteed by the shared runtime.

## Absolute-time contract

Represent shots and events as data: `start, duration, object, from, to, curve, anchor, content, cue`. Compute the complete frame from time, immutable assets and an explicit seed. Clear all drawing state on each call. Wait for fonts and media decodes. Test repeated timestamps after both forward and reverse seeks. A realtime application needs a separate deterministic export path or a baked simulation cache.

## Timing primitives

For `u=clamp((t-start)/duration,0,1)`, cubic smoothstep `u*u*(3-2*u)` gives stationary endpoints. Use it when the object starts and stops, not across a moving handoff that requires nonzero velocity. A short anticipation moves away from the intended action before commitment; it must explain weight or intent, not delay every interaction. An overshoot should converge, not keep all objects alive.

A critically damped displacement with target `q`, initial position `x0`, velocity `v0`, angular rate `w>0`, and elapsed `tau>=0` is:

`x(tau) = q + ((x0-q) + (v0+w*(x0-q))*tau) * exp(-w*tau)`

Evaluate analytically. Do not advance a spring by frame-count integration during seeking. Repeated target changes can use piecewise segments whose starting position and velocity are evaluated from the previous segment, or a correctly derived linear superposition. Simple target interpolation is not a general spring solution. Never clamp an overshooting spring's position if the resulting velocity snap is visible.

## Geometry and camera

- **Carrier morph:** interpolate compatible silhouette parameters; maintain one anchor. Clip internal content independently so labels do not stretch with the surface.
- **Path reveal:** use accumulated arc length, not vertex count. Skip a zero-length stroke to avoid round-cap dots.
- **Matched handoff:** compare output-space anchors after camera transforms. Match scale, direction and velocity where continuity is intended.
- **Occlusion:** hide a reset only after a cover reaches every corner, including rotated-camera bounds. Inspect adjacent frames.
- **Portal zoom:** interpolate positive scale in log space. Bound recursion and source magnification; full coverage conceals coordinate reset, not a velocity mismatch.
- **Parallax:** assign explicit depth and sufficient plate overscan. Fill revealed regions before movement; invented pixels are not documentary evidence.
- **Stepped material motion:** quantize object time, not the export clock. Keep type smooth if readability requires it. A lower pose cadence is an art choice, not dropped export frames.

Draw attention with a hierarchy of travel distances and holds. Camera motion should reveal information, follow a meaningful action or establish scale. Avoid moving the camera, text and every background layer independently.

## Temporal sampling, not frame trails

For output frame `n` at fps `F`, choose a shutter interval around `n/F` and evaluate `K` subframes inside it. Average those subframes into exactly one output image, preferably in linear light. Then encode one frame at `F`. Limit or disable blur for small text and sudden cuts. Clamp non-loop endpoints or wrap a genuinely periodic scene.

A rolling `tmix` over already encoded full-rate frames makes trails and can blend across unrelated shots; it is not automatically proper shutter integration. If using FFmpeg for averaging, verify disjoint groups, output frame count and timestamps. More samples increase render cost and do not repair bad timing.

## Loops and accessibility

Require both state and velocity continuity, then export `[0,L)`, not a duplicate endpoint. See [loop recipe](../recipes/seamless-loop.md). Prefer a deliberate still for reduced-motion preview and explicit play controls. Avoid rapid high-contrast or saturated-red flashes. Following a few samples or a rule of thumb is not a formal flash-safety assessment; consult the [accessibility source](../references/creative-sources.md) when relevant.

## Validation sequence

1. Check the final layout before motion, then the worst intermediate layout.
2. Render contact sheets at cues and at transition midpoints; add adjacent frames at discontinuities.
3. Compare exact-time hashes after scrambled seeks.
4. Inspect the encoded film at actual viewing size and normal speed.
5. Probe dimensions, duration, frame count, fps and streams. Report geometry, continuity, story and technical checks separately.
