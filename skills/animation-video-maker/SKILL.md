---
name: animation-video-maker
description: Use when creating styled animation videos from a brief.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Animation Video Maker

Turn a verified brief into an original, editable animation and a checked MP4. This package combines a production workflow, 20 style specializations, a shared Canvas runtime and 20 examples. It is not a generative-video model, stock-footage library or autonomous publishing service.

## When to use

Use for explainers, service introductions, visual process narratives and typographic messages. Prefer actual product footage when the claim depends on demonstrating real software. Prefer a 3D or generative-video tool when physically realistic camera motion or photorealism is essential.

## Requirements

- A brief, intended audience, factual sources and rights to brand/content.
- A current browser to preview the bundled examples. No account, API key or network is needed for playback.
- To export: Python 3.10+, Playwright 1.48+, Chromium, FFmpeg with libx264 and ffprobe. See [runtime](references/runtime.md).
- Jev is optional. Its absence must not block a manual style choice or rendering.

## Production procedure

1. **Bound the brief.** Record audience, message, channel, language, duration, aspect ratio, CTA, brand assets and source links. Resolve missing information that changes production before starting an expensive render. The bundled defaults are English, 20 seconds, 1920×1080, 30 fps, no audio.
2. **Verify the claims.** Read the primary sources. Keep exact names and numbers, distinguish illustrative diagrams from production architecture, and preserve units and denominators. Never fabricate metrics, live telemetry, certifications, headcount or guarantees.
3. **Choose one primary visual language.** Honor an explicit style. Otherwise use the style index below and [selection guide](references/style-selection.md); optionally use configured Jev to retrieve/rank relevant style descriptions. Use the result as evidence for a choice, not as a calibrated quality score. Ask only when ambiguity materially changes the output.
4. **Load the chosen specialization.** Read `styles/<id>/SKILL.md`. If the agent does not discover nested skills, read this file directly. Each specialization supplies visual grammar, drawing techniques, pacing and style-specific checks. Load only the relevant style rather than all 20.
5. **Write a storyboard.** Define the question/hook, explanation, proof or qualification, and next step. Assign readable holds. The examples reserve seconds 17–20 for a static CTA. Do not force one storyboard on every style; panel storytelling, continuous drawing and kinetic text need different structures.
6. **Create original scene code.** Start from an appropriate example and adapt its composition, not just its colors. Reuse `assets/runtime.js` and `scripts/render.py`; use native Canvas before adding a library. Replace T2S brand/copy when creating work for another organization. The core workflow does not require T2S.
7. **Make time deterministic.** Implement `window.scene(t)` from absolute seconds and a full accessible `window.TRANSCRIPT`. Do not derive exported motion from wall-clock time, frame accumulation, network calls or unseeded randomness. Preserve `window.ready`, `DURATION`, `renderFrame(t)` and `draw({t})` supplied by the runtime.
8. **Preview before full export.** Use the agent's terminal tool to run `python scripts/render.py examples/<id>/index.html preview.mp4 --samples-only`. Inspect real frames for overlaps, margin violations, exact logos, source accuracy and readability. Check transitions as well as settled scenes. A passing metadata test does not prove visual quality.
9. **Export and verify.** Run `python scripts/render.py examples/<id>/index.html output.mp4 --duration 20 --fps 30`. Check the exit status, QA JSON, decoded video frames and ffprobe metadata. Preserve any previous successful output if export fails. The script refuses an existing destination unless `--overwrite` is explicit.
10. **Deliver a reproducible result.** Include MP4, editable HTML/scene, required local assets, chosen style, source attribution and actual validation status. State audio/format limitations. Publish only to the authorized destination; never change repository visibility or social-post content implicitly.

## Style index

| Style | Start here | Best suited to |
|---|---|---|
| Bauhaus | [Guide](styles/bauhaus/SKILL.md) | Geometric hierarchy and focused framing |
| 16 mm documentary | [Guide](styles/film-documentary/SKILL.md) | Editorial operational context |
| Whiteboard | [Guide](styles/whiteboard/SKILL.md) | Progressive teaching |
| Blueprint | [Guide](styles/blueprint/SKILL.md) | Technical relationships and boundaries |
| Comic book | [Guide](styles/comic-book/SKILL.md) | Challenge, intervention and decision |
| HUD | [Guide](styles/hud/SKILL.md) | Controls and state interpretation |
| Isometric | [Guide](styles/isometric/SKILL.md) | Spatial relationships and roles |
| Paper cutout | [Guide](styles/paper-cutout/SKILL.md) | Layered, tactile concept assembly |
| Chalkboard | [Guide](styles/chalkboard/SKILL.md) | Cumulative reasoning and teaching |
| Pencil sketch | [Guide](styles/pencil-sketch/SKILL.md) | Exploratory design and construction |
| Clay-inspired | [Guide](styles/clay/SKILL.md) | Approachable tactile explanations |
| Kinetic typography | [Guide](styles/kinetic-typography/SKILL.md) | Short verbal messages |
| Flat-vector explainer | [Guide](styles/flat-vector-explainer/SKILL.md) | Accessible illustrated systems |
| Linocut | [Guide](styles/linocut/SKILL.md) | Limited-ink editorial imagery |
| Memphis | [Guide](styles/memphis/SKILL.md) | Playful geometric energy |
| Pixel art | [Guide](styles/pixel-art/SKILL.md) | Discrete process changes |
| Retro 1970s | [Guide](styles/retro-70s/SKILL.md) | Warm print-inspired narratives |
| Single line | [Guide](styles/single-line/SKILL.md) | Connection and continuity |
| Terminal | [Guide](styles/terminal/SKILL.md) | Developer-facing explanations |
| Data storytelling | [Guide](styles/data-storytelling/SKILL.md) | Evidence and categorical composition |

[Gallery](gallery.html) · [Machine-readable catalog](references/catalog.json) · [Sources and rights](references/sources.md)

## Portability and scope

Install/copy this entire directory into the chosen agent's documented skill location. Nested `SKILL.md` files are local specialization documents; discovery behavior differs by agent. The root skill and relative file reads are the portable fallback. Do not register 20 global skills unnecessarily. Do not copy only a child directory: its shared runtime and references are in this package.

`ponytail:` the shared renderer intentionally targets Full HD horizontal, silent video. Recompose layouts and adjust/verify geometry before adding vertical output; do not stretch. Audio, live data, physics and true 3D are separate additions only when the brief requires them. Clay, film and print textures here are procedural visual treatments, not claims of physical capture.

## Verification checklist

- Chosen style fits the request; explicit preferences take precedence over routing.
- Sources, units, brand proportions and rights checked.
- Storyboard readable; opening nonblank; CTA held; no flashing effects.
- Fonts loaded, no unexpected requests or JavaScript errors.
- Out-of-order seeks reproduce the same images.
- Preview controls, reduced motion and accessible transcript work.
- Real MP4 has intended codec, dimensions, fps, duration and frame count.
- Editable package and license notices retained; limitations reported honestly.

See [validation report](references/validation.md) for what this release actually tested. A style guide is not a quality guarantee: inspect each new output.
