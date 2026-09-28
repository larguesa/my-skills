---
name: animation-product-interface
description: Use when animating UI states and product interactions.
version: 0.2.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
---
# Product interface motion

Make an interface explain itself through continuity. The meaningful unit is a persistent object changing state, not a sequence of decorated screenshot slides.

## Use and boundaries
Use for feature concepts, interaction studies, onboarding and workflow explanations. If the brief claims a real product works, use verified product footage or reproduce verified behavior exactly. Label invented interfaces as illustrative. Do not create fake customer results, performance counters or integrations.

## Design procedure
1. Identify a user intention and three visible states. Write what changes and what remains invariant. A captured thought can become a detailed card, then a focused board, while retaining its color and position.
2. Draw a state table with absolute start/end times, object bounds, corner radii, labels and opacity. Match identity before matching decoration. Keep the moving object's center or one edge anchored through each transition.
3. Choose a restrained surface system: one background, one ink, two supporting surface tints and one action accent. Distinguish active controls by shape or text, not color alone. Use borders and modest shadows instead of glass effects that destroy contrast.
4. Allocate roughly one second to each transformation and longer holds to anything that must be read. Animate size and position together. Crossfade details only inside their parent surface. Do not shrink body text into illegibility to fit a morph.
5. Use `p = smoothstep(clamp((t-start)/length))` and interpolate every property from its endpoints. Derive all branches from absolute time. Avoid mutable springs or per-frame particle updates. A loop must match both layout and velocity at its seam.
6. Recompose for portrait rather than cropping a desktop board. Keep a meaningful object on screen at the opening. Optional cursor movement must explain a real cause and effect, not decorate a transition.

## Implementation
The [editable UI study](../../demos/ui-morph/index.html) uses a chip, expanded card and three-column board. Its [scene](../../demos/ui-morph/scene.js) is the editable visual source; `demos/player.js` supplies offline fonts, a readiness Promise, deterministic JPEG frames, pause/replay and a seek slider. The study is not an application implementation.

For new shared-runtime work, use the root production procedure, declare duration and explicit neutral branding behavior, and preserve `window.ready`, `window.DURATION`, `window.renderFrame(t)`, `window.draw({t})` and `window.TRANSCRIPT`. Maintain even pixel dimensions for H.264. Render with the package renderer, not a screen recording.

## Acceptance checks
- Compare the first and endpoint frames for a declared seamless loop, and inspect neighboring frames for velocity discontinuity.
- Seek into every transition in reverse order. Confirm identical pixels on repeated timestamps.
- Inspect real decoded video at small/mobile scale. Check title fit, minimum card text size, surface clipping and shadow bounds.
- Test keyboard controls and reduced motion. A quiet default or static preview is preferable to compulsory autoplay.
- Ensure viewers can distinguish fictional demonstration, verified footage and functional application.
- Keep the silent render separate from any audio-muxed deliverable and report actual stream metadata.

## Avoid
Generic device mockups, fake analytics, aimless cursor movement, a new composition at every cut, and morphing text before it can be read. Motion should explain object identity and user intent.

Original guide and demonstration: Ricardo Pupo Larguesa, Hermes Agent. MIT code and prose; bundled fonts retain their own licenses.
