---
name: animation-generative-geometry
description: Use when creating recursive or procedural motion art.
version: 0.2.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
---
# Generative geometry

Create a visual system whose rules produce an intentional composition. Recursion, repetition and periodic motion are drawing techniques, not substitutes for art direction or evidence.

## Appropriate briefs
Use for abstract identities, spatial interludes, loops, ambient portrait pieces and conceptual transitions. Do not imply mathematical accuracy, scientific simulation or measured data unless independently verified. Avoid this style when the viewer needs to read a long argument or inspect an actual interface.

## Choose the rule before the effect
1. Define a dominant shape and a spatial question: nested doorways, folded planes, orbiting intersections or a field pulled toward a focal point. Write the rule in one sentence.
2. Choose a bounded layer count and a scale ratio. For nested portals, `scale(i) = ratio ** i` gives a predictable depth hierarchy. Stop when inner details are smaller than a useful pixel footprint. More layers usually add aliasing, not quality.
3. Establish the silhouette at thumbnail size. Reserve quiet regions for labels. Portrait needs a vertically composed focal field, not a horizontally rendered image stretched tall.
4. Build a limited depth palette. Alternate luminous and dark layers so occlusion describes depth without expensive blur. Use one small focal highlight rather than global bloom.
5. Parameterize motion by absolute seconds. For a loop of length L, use `phase = 2*pi*t/L`; integer-frequency sine and cosine terms return to their initial values and derivatives. Index-dependent offsets create a traveling rhythm without accumulated state.
6. Keep rotation, zoom and travel gentle enough to follow. Do not alternate high-contrast full frames or create strobing patterns. In reduced-motion mode show a deliberate representative still and require an explicit play action.
7. Save and restore the Canvas state around every transformed layer. Clip the field once to a deliberate outer silhouette. Draw largest to smallest; verify that the inner layer does not accidentally hide the focal point.

## Editable reference
The [portrait portal study](../../demos/recursive-portal/index.html) uses rounded contours, nineteen bounded layers, periodic deformation and a small central glow. The [scene source](../../demos/recursive-portal/scene.js) is original and deterministic. It is procedural 2D art, not ray tracing or a physics simulation. The eight-second source is silent; the final MP4 adds locally synthesized audio through the documented command in the [demo notes](../../demos/README.md).

## Rendering contract
Preserve readiness, declared duration, absolute-time rendering, JPEG-base64 export and transcript. Keep dimensions even. Export at a declared frame rate, using the package renderer and existing browser environment. Runtime state must not depend on frame order, wall time, random calls or external services. Shared/local fonts must be loaded before the first exported frame.

## Verify the system, not just a hero frame
- Hash matching timestamps after reverse-order seeks.
- Compare t=0 and t=L for a declared loop, then inspect t=L-1/fps against the start for perceptual continuity.
- Decode a contact sheet from the actual MP4. Look for moire, banding, shape inversion, clipped text and subpixel shimmer.
- Inspect dense and sparse moments, not only the central composition.
- Probe duration, dimensions, frame count and audio streams separately. A waveform existing does not prove its amplitude or mux timing is correct.
- Keep source code, synthesis command and silent source so the piece can be revised without a paid service.

Original guide and demonstration: Ricardo Pupo Larguesa, Hermes Agent. MIT code and prose; bundled fonts retain their own licenses.
