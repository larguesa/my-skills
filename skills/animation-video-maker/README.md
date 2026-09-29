# Animation Video Maker

**22 visual styles, original creative recipes, motion techniques and a reproducible code-animation path.**

An English-language skill package for agents that can read files, write JavaScript and run local tools. Use AI to direct and author editable code animation, plan generative footage, or combine both. The bundled Canvas-to-MP4 path needs no video-generation API or framework. Generative/hybrid routes provide briefs and quality gates, not preconfigured provider adapters.

**Start here:** [Agent skill](SKILL.md) · [Creative brief](templates/creative-brief.md) · [Visual direction card](templates/LOOK.md) · [Minimum smoke test](references/smoke-test.md) · [Recipe library](recipes/README.md) · [Creative demos](demos/index.html) · [Runtime/setup](references/runtime.md) · [Source library](references/creative-sources.md)

[Creative direction](references/creative-direction.md) · [Style selection and optional Jev](references/style-selection.md) · [Legacy gallery](gallery.html) · [Original validation](references/validation.md) · [Expansion validation](references/validation-0.2.md)

The HTML gallery runs after downloading/cloning the package. GitHub's source viewer does not execute HTML. Each row in the gallery below links to the video file, editable player and style instructions.

## What is included

- One operational root skill and 22 style-specific `SKILL.md` guides.
- Original recipe templates and technique/backend guidance, with source attribution and licensing caveats.
- Brand-neutral creative demos with editable scenes, local previews and real MP4 exports.
- 20 original examples featuring five verified [T2S Tech services](https://t2stech.com/#services), four treatments per service.
- Legacy MP4s at 1920×1080, 30 fps, 20 seconds; intentionally no audio. New demos explore other durations, aspect ratios and an explicit optional audio finishing step.
- Editable scenes, official example brand assets, embedded fonts, local playback controls and accessible transcripts.
- Shared native Canvas runtime, Python/Playwright/FFmpeg renderer and regression checks.
- Optional Jev-assisted style retrieval, with an ordinary manual-selection fallback.

The examples demonstrate the library and introduce T2S. The skills themselves are reusable for other organizations. **Replace T2S brand and content when creating your own examples.**

## Use with an agent

Copy this whole `animation-video-maker` directory into the agent's documented skill location, or point the agent at `SKILL.md` in your checkout. Do not assume all agents discover nested skills: the root explicitly loads the chosen style guide by relative path. Keep the complete package together, including shared assets, scripts, templates, references, recipes, techniques, backends, demos, examples and styles.

Example request:

> Create a 20-second animation explaining our migration approach to nontechnical managers. Use the Animation Video Maker workflow. Suggest a style if none is explicit, verify the claims against the supplied source, then deliver the editable scene and a validated MP4.

No Jev setup is required. A configured Jev installation may shortlist descriptions for an ambiguous request, but an explicit user choice takes precedence. See the selection guide for privacy, setup and fallback rules.

Some agents recursively discover the nested guides as separate skills. If you already installed earlier standalone `animation-*` skills, check for duplicate names before installing this bundle. Migrating or removing those older installations is an explicit local decision; cloning this repository does not modify them.

## Choose the right route

- **AI-authored code animation:** exact text, diagrams, repeatable UI motion, procedural geometry. Runs locally with the bundled tools.
- **Generative footage:** organic environments, character motion or imagery that is costly to draw. Use the backend guide with a separately configured and authorized provider; outputs are stochastic and require selection and review.
- **Hybrid:** generated or real footage plus precise graphics, typography, logos and editing. Source footage rights and continuity are part of the brief.

For a new creative request, start with the [brief template](templates/creative-brief.md), [direction matrix](references/creative-direction.md) and [recipe library](recipes/README.md). For example:

> Create a short brand-neutral film in which a thought becomes an interface and returns to its starting form. Choose a primary visual style and a motion recipe. Label any fictional UI, keep the message understandable without sound, and deliver editable source plus a verified looping MP4. Use local code unless there is a clear need for paid generation.

The catalogs are references, not commands to execute. Borrow concepts, write original direction, and check licenses before using external code, footage, music or brands.

## Preview and export

Open `gallery.html` locally, or serve this directory on localhost with `python -m http.server 8000 --bind 127.0.0.1`. The preview itself needs no API credentials or external requests.

To export, install/reuse Python, Playwright/Chromium and FFmpeg as described in [runtime.md](references/runtime.md), then run from this directory through the agent's terminal tool:

```sh
python scripts/render.py examples/blueprint/index.html my-animation.mp4 --duration 20 --fps 30
```

Use `--samples-only` for still-frame QA first. Existing outputs are protected unless `--overwrite` is explicitly supplied. Only render reviewed local HTML; browser request blocking is not an OS-level sandbox.

## Gallery

| Preview | Style and service | Open |
|---|---|---|
| ![Bauhaus](examples/bauhaus/poster.jpg) | **Bauhaus**<br>AI-First Discovery | [Video](examples/bauhaus/video.mp4) · [Edit](examples/bauhaus/index.html) · [Skill](styles/bauhaus/SKILL.md) |
| ![16 mm documentary](examples/film-documentary/poster.jpg) | **16 mm documentary**<br>Modernization and Integration | [Video](examples/film-documentary/video.mp4) · [Edit](examples/film-documentary/index.html) · [Skill](styles/film-documentary/SKILL.md) |
| ![Whiteboard](examples/whiteboard/poster.jpg) | **Whiteboard**<br>AI-First Discovery | [Video](examples/whiteboard/video.mp4) · [Edit](examples/whiteboard/index.html) · [Skill](styles/whiteboard/SKILL.md) |
| ![Blueprint](examples/blueprint/poster.jpg) | **Blueprint**<br>AI Quality and Reliability | [Video](examples/blueprint/video.mp4) · [Edit](examples/blueprint/index.html) · [Skill](styles/blueprint/SKILL.md) |
| ![Comic book](examples/comic-book/poster.jpg) | **Comic book**<br>AI Quality and Reliability | [Video](examples/comic-book/video.mp4) · [Edit](examples/comic-book/index.html) · [Skill](styles/comic-book/SKILL.md) |
| ![HUD](examples/hud/poster.jpg) | **HUD**<br>AI Quality and Reliability | [Video](examples/hud/video.mp4) · [Edit](examples/hud/index.html) · [Skill](styles/hud/SKILL.md) |
| ![Isometric](examples/isometric/poster.jpg) | **Isometric**<br>AI-Native Delivery Pods | [Video](examples/isometric/video.mp4) · [Edit](examples/isometric/index.html) · [Skill](styles/isometric/SKILL.md) |
| ![Paper cutout](examples/paper-cutout/poster.jpg) | **Paper cutout**<br>Managed Evolution | [Video](examples/paper-cutout/video.mp4) · [Edit](examples/paper-cutout/index.html) · [Skill](styles/paper-cutout/SKILL.md) |
| ![Chalkboard](examples/chalkboard/poster.jpg) | **Chalkboard**<br>AI-First Discovery | [Video](examples/chalkboard/video.mp4) · [Edit](examples/chalkboard/index.html) · [Skill](styles/chalkboard/SKILL.md) |
| ![Pencil sketch](examples/pencil-sketch/poster.jpg) | **Pencil sketch**<br>Modernization and Integration | [Video](examples/pencil-sketch/video.mp4) · [Edit](examples/pencil-sketch/index.html) · [Skill](styles/pencil-sketch/SKILL.md) |
| ![Clay-inspired](examples/clay/poster.jpg) | **Clay-inspired**<br>Managed Evolution | [Video](examples/clay/video.mp4) · [Edit](examples/clay/index.html) · [Skill](styles/clay/SKILL.md) |
| ![Kinetic typography](examples/kinetic-typography/poster.jpg) | **Kinetic typography**<br>AI-Native Delivery Pods | [Video](examples/kinetic-typography/video.mp4) · [Edit](examples/kinetic-typography/index.html) · [Skill](styles/kinetic-typography/SKILL.md) |
| ![Flat-vector explainer](examples/flat-vector-explainer/poster.jpg) | **Flat-vector explainer**<br>AI-Native Delivery Pods | [Video](examples/flat-vector-explainer/video.mp4) · [Edit](examples/flat-vector-explainer/index.html) · [Skill](styles/flat-vector-explainer/SKILL.md) |
| ![Linocut](examples/linocut/poster.jpg) | **Linocut**<br>Modernization and Integration | [Video](examples/linocut/video.mp4) · [Edit](examples/linocut/index.html) · [Skill](styles/linocut/SKILL.md) |
| ![Memphis](examples/memphis/poster.jpg) | **Memphis**<br>Managed Evolution | [Video](examples/memphis/video.mp4) · [Edit](examples/memphis/index.html) · [Skill](styles/memphis/SKILL.md) |
| ![Pixel art](examples/pixel-art/poster.jpg) | **Pixel art**<br>Managed Evolution | [Video](examples/pixel-art/video.mp4) · [Edit](examples/pixel-art/index.html) · [Skill](styles/pixel-art/SKILL.md) |
| ![Retro 1970s](examples/retro-70s/poster.jpg) | **Retro 1970s**<br>AI-First Discovery | [Video](examples/retro-70s/video.mp4) · [Edit](examples/retro-70s/index.html) · [Skill](styles/retro-70s/SKILL.md) |
| ![Single line](examples/single-line/poster.jpg) | **Single line**<br>Modernization and Integration | [Video](examples/single-line/video.mp4) · [Edit](examples/single-line/index.html) · [Skill](styles/single-line/SKILL.md) |
| ![Terminal](examples/terminal/poster.jpg) | **Terminal**<br>AI Quality and Reliability | [Video](examples/terminal/video.mp4) · [Edit](examples/terminal/index.html) · [Skill](styles/terminal/SKILL.md) |
| ![Data storytelling](examples/data-storytelling/poster.jpg) | **Data storytelling**<br>AI-Native Delivery Pods | [Video](examples/data-storytelling/video.mp4) · [Edit](examples/data-storytelling/index.html) · [Skill](styles/data-storytelling/SKILL.md) |

## Design principles

- A different style changes drawing, composition and movement, not just color.
- Real evidence beats plausible metrics. Illustrated diagrams, simulated terminals and HUDs are labeled as such.
- Words and logos stay exact. Body text remains readable; the final CTA is stable.
- A single shared runtime/renderer avoids 20 duplicate dependencies.
- A reliable result includes real export, visual inspection, metadata checks and editable files.

`ponytail:` local rendering remains native Canvas plus Playwright/FFmpeg. The renderer exports silent frames; audio is a separate, explicitly validated finishing step. Recompose for portrait/square rather than stretching legacy scenes. True 3D and generative providers remain external options, not dependencies. Clay/film/pencil/print appearances are procedural interpretations, not physical capture.

## Rights and attribution

Original code and documentation in this directory are MIT licensed. T2S trademarks/logo assets are excluded from that grant; Montserrat and Rubik retain their OFL notices. See [LICENSE](LICENSE), [NOTICE](NOTICE.md) and [sources](references/sources.md).

The visual taxonomy was inspired by [yasinozmeen/animasyon-stil-katalogu](https://github.com/yasinozmeen/animasyon-stil-katalogu). This is a new implementation, not a redistribution of that repository's source or its author's private skill. No endorsement or affiliation is implied.
