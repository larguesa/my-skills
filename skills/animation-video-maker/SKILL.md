---
name: animation-video-maker
description: Use when creating styled animation videos from a brief.
version: 0.2.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Animation Video Maker

Turn a verified brief into an original creative video and a checked deliverable. Combine visual style, motion technique, narrative recipe and execution route rather than treating each as the same choice. This package supplies original templates, local code-animation tools and examples, plus generative/hybrid planning guidance. It is not itself a video-generation model or an autonomous publishing service.

## When to use

Use for explainers, service introductions, visual process narratives and typographic messages. Prefer actual product footage when the claim depends on demonstrating real software. Prefer a 3D or generative-video tool when physically realistic camera motion or photorealism is essential.

## Requirements

- A brief, intended audience, factual sources and rights to brand/content.
- A current browser to preview the bundled examples. No account, API key or network is needed for playback.
- To export: Python 3.10+, Playwright 1.48+, Chromium, FFmpeg with libx264 and ffprobe. See [runtime](references/runtime.md).
- Jev is optional. Its absence must not block a manual style choice or rendering.

## Production procedure

1. **Bound the brief.** Complete the [creative brief](templates/creative-brief.md): audience, message, source claims, duration, aspect ratio, CTA, assets/rights, audio state, budget and paid-attempt ceiling. Resolve unknowns that change production before rendering. Legacy examples default to English, 20 seconds, 1920×1080, 30 fps, no audio; those are examples, not requirements for new work.
2. **Verify the claims.** Read the primary sources. Keep exact names and numbers, distinguish illustrative diagrams from production architecture, and preserve units and denominators. Never fabricate metrics, live telemetry, certifications, headcount or guarantees.
3. **Choose one primary visual language.** Honor an explicit style. Otherwise use the style index below and [selection guide](references/style-selection.md); optionally use configured Jev to retrieve/rank relevant style descriptions. Use the result as evidence for a choice, not as a calibrated quality score. Ask only when ambiguity materially changes the output.
4. **Choose the other creative layers.** Read the [direction matrix](references/creative-direction.md), selected [recipe](recipes/README.md) and `styles/<id>/SKILL.md`. If nested skills are not discovered, read files directly. Load only relevant technique/backend guidance. Code suits exact text, diagrams and UI; generative footage suits organic imagery; hybrid combines footage with deterministic graphics. Never infer provider availability or rights from a reference prompt.
5. **Write a timed storyboard.** Define hook, development, proof or qualification, and resolution. Assign focal points, continuity, anticipation, pauses and reading holds. Plan beat/phrase cues when audio is authorized. Looping work needs a continuous return, not a CTA interruption. Do not impose the legacy examples' three phases or final end card on every piece.
6. **Produce with the approved route.** For code, start from a [brand-neutral demo](demos/index.html) or suitable legacy example and reuse the shared runtime/renderer. Adapt composition, not just colors; native Canvas comes before dependencies. For generative/hybrid work, approve shot prompts, continuity and spending limits, then use a verified available provider. Keep exact text/logos in deterministic post-production. Do not run paid requests merely because a recipe mentions a tool.
7. **Make code animation deterministic.** Implement `window.scene(t)` from absolute seconds and a full accessible `window.TRANSCRIPT`. Do not derive exported motion from wall-clock time, frame accumulation, network calls or unseeded randomness. Preserve `window.ready`, `DURATION`, `renderFrame(t)` and `draw({t})` supplied by the runtime.
8. **Preview before full export.** Use the agent's terminal tool to run `python scripts/render.py examples/<id>/index.html preview.mp4 --samples-only`. Inspect real frames for overlaps, margin violations, exact logos, source accuracy and readability. Check transitions as well as settled scenes. A passing metadata test does not prove visual quality.
9. **Export and verify.** For a legacy 20-second example, run `python scripts/render.py examples/<id>/index.html output.mp4 --duration 20 --fps 30`. For new scenes, pass the declared duration and requested fps; do not truncate longer narratives silently. For generative/hybrid delivery, validate the final composited file rather than claiming the Canvas export tests cover the provider. Check the exit status, QA JSON, decoded video frames and ffprobe metadata. Preserve any previous successful output if export fails. The script refuses an existing destination unless `--overwrite` is explicit.
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
| Product interface | [Guide](styles/product-interface/SKILL.md) | Precise UI hierarchy and real interactions |
| Generative geometry | [Guide](styles/generative-geometry/SKILL.md) | Recursive forms and procedural spatial rhythm |

[Creative demos](demos/index.html) · [Recipes](recipes/README.md) · [Legacy gallery](gallery.html) · [Style catalog](references/style-catalog.json) · [Legacy example catalog](references/catalog.json) · [Sources and rights](references/sources.md)

## Portability and scope

Install/copy this entire directory into the chosen agent's documented skill location. Nested `SKILL.md` files are local specialization documents; discovery behavior differs by agent. The root skill and relative file reads are the portable fallback. Do not register every specialization globally unnecessarily. Do not copy only a child directory: its shared runtime and references are in this package.

`ponytail:` the shared renderer exports deterministic silent Canvas frames. Recompose for each supported canvas size; use a separately verified FFmpeg step for audio. Generative models, live data, physics and true 3D remain optional external routes, not bundled adapters. Clay, film and print treatments are procedural appearances, not claims of physical capture. External recipes inspire original work; the [source register](references/creative-sources.md) is not a redistribution license.

## Verification checklist

- Chosen style fits the request; explicit preferences take precedence over routing.
- Sources, units, brand proportions and rights checked.
- Storyboard readable; opening nonblank; CTA held when applicable; loops return cleanly; no flashing effects.
- Fonts loaded, no unexpected requests or JavaScript errors.
- Out-of-order seeks reproduce the same images.
- Preview controls, reduced motion and accessible transcript work.
- Real MP4 has intended codec, dimensions, fps, duration and frame count.
- Editable package and license notices retained; limitations reported honestly.

See the [0.2 validation report](references/validation-0.2.md) and [legacy validation report](references/validation.md) for what was actually tested. A style guide is not a quality guarantee: inspect each new output.
