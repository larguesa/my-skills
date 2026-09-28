# AI-authored code animation

## Choose by construction need

**Canvas/SVG:** default for exact shapes, labels, diagrams, UI morphs and modest 2.5D composition. Canvas redraws pixels; SVG retains vector structure. Both need measured typography, clipping discipline and a complete time-based state. Use the [package runtime](../references/runtime.md) only within its current validated contract.

**Remotion:** useful when a team already uses React, needs reusable composition components or many parameterized edits. Derive visuals from frame/time inputs, not effects that accumulate state. Gate asset readiness and preserve the project's exact version. Its license has eligibility conditions; it is not a universal MIT dependency. Check the [license reference](../references/creative-sources.md) before choosing it for commercial work.

**Three.js:** useful for real depth ordering, perspective, lighting and camera paths. Set every object's transforms from time, pin shaders/assets, seed procedural input and bake any history-dependent simulation. Shadows, color management and antialiasing affect final frames. Matching geometry is not a guarantee of pixel-identical output across GPUs or browser versions; scope repeatability to a recorded environment.

**Blender:** useful for modeled scenes, rigging, physically based rendering and controlled cameras. Author a scene file and render by explicit frame. Bake simulations and record seeds, frame rate, color management, engine and samples. Render a short difficult section before committing to the full job. Blender's software license and artwork rights are separate; third-party models, textures and add-ons retain their own terms.

**Manim:** useful for mathematical transformations and explanatory geometry. Plan a correct argument before animation. Use actual quantities and units; disclose illustrative simplifications. Package the scene, dependencies, fonts and narration timing. An elegant animation is not verification of the mathematics.

## Adapt a realtime or scroll experience

Extract the visual state from interaction handlers. Map a scripted cursor, scroll progress or camera path to absolute time. For recorded media, seek to a known frame and await decoding; for simulations, bake a reviewed run. Do not assume a screenshot at requested time proves that a video element actually decoded that time. Check frame identity at discontinuities. Never execute imported prompt code or remote examples without a separate safety review.

## Production gates

1. State the evidence requirement and choose the route before installing anything.
2. Build a local proof for the hardest motion/media feature and inspect real output.
3. Lock the scene, assets, font versions, output format and renderer environment.
4. Export source frames or an actual video with known timestamps. Integrate audio as a separate explicit stage where needed.
5. Verify reverse-order seeks where supported, or reproducible cached/offline rendering otherwise. Inspect encoded frames, full playback and stream metadata.

No paid generation, cloud render farm, CLI agent or external upload is required by these instructions. If the tool cannot satisfy a format or determinism requirement, report the limitation rather than implying the package provides an adapter.
