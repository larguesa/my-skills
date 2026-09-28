# Select a production backend

A coding model can author an animation program without generating video pixels. Do not describe every AI-assisted animation as generative video. Choose the smallest route that satisfies the evidence and image requirements; do not install a framework merely because a source prompt named it.

| Requirement | Route | What must be proved |
|---|---|---|
| Exact text, UI states, charts, masks, repeatable timing | Canvas/SVG or a reviewed code timeline | Loaded local assets, deterministic frames, readable output |
| Component-based composition and many editorial variants | Remotion | Version-specific license, pinned dependencies, frame-driven state |
| Spatial camera, depth, lighting, complex surfaces | Three.js or Blender | Geometry, camera, sampling, cache/bake strategy, export quality |
| Mathematical derivation or geometric lesson | Manim | Mathematical correctness and readable pedagogical timing |
| Actual software behavior | Authorized capture plus code/editor overlays | Real actions, faithful results, privacy and claim provenance |
| Photoreal motion or character performance not economical to author | Generative video, only with approval | Provider capability, asset rights, cost bound, shot continuity |
| Generated or recorded imagery with exact typography/timing | Hybrid compositing | Clear stage boundaries and deterministic final edit |

Read [code backends](code-animation.md) or [generative and hybrid](generative-and-hybrid.md). These are workflow guidance, not bundled executable adapters or tested integrations. The package renderer remains its own documented contract. A playable game, scroll page or interactive world is not automatically an exported video.

## Common handoff contract

Record dimensions, fps, duration, color/alpha assumptions, audio policy, shot IDs, file hashes, licenses and immutable local paths. Keep exact text outside generative image/video stages. Produce a low-cost proof of the hardest transition before the complete sequence. Deliver source plus the actual encoded media, not a configuration file renamed as a video.

Every backend must support either exact-time frame access or a documented offline render/cache route. Treat tool/version claims in social prompts as unverified. Check official documentation and the installed version before writing commands. See [verified external references](../references/creative-sources.md).
