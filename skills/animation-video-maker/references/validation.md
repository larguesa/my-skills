# Release validation: 0.1.0

This report describes executed checks, not a quality guarantee or performance benchmark.

## Verified inventory

- One root workflow and 20 distinct style SKILL.md documents.
- 20 original English-language scene/player pairs, mapped to five services (four examples each).
- 20 complete MP4s, each 1920×1080, H.264/yuv420p, 30 fps, 20 seconds and 600 decoded frames. No audio.
- 20 posters, the local HTML gallery, source links and applicable notices.
- Exact media/source hashes in [SHA256SUMS.txt](../SHA256SUMS.txt); per-example technical evidence in [validation.json](validation.json).

## Executed checks

1. **Source/browser:** all 20 examples exercised across the timeline at quarter-second intervals. No JavaScript errors, external page requests or measured text-boundary overflows. Font files loaded.
2. **Determinism:** repeated out-of-order seeks reproduced the same images. The final three-second CTA was stable.
3. **Playback/accessibility:** play, pause, replay and reduced-motion startup exercised in each example. Narrative transcripts include the shared contact destination. A missing destination in seven transcripts was found during independent review, corrected and covered by a regression assertion.
4. **Visual review:** rendered source-frame contact sheets inspected for all styles, including initial and completed compositions. A comic-panel heading collision was corrected and reinspected. This is visual sampling, not frame-by-frame human review or formal accessibility certification.
5. **Actual video:** FFprobe counted frames and verified dimensions, duration and frame rate. Six frames per MP4 were decoded and compared with source-rendered PNGs, allowing less than 6 levels of mean absolute RGB compression error on the 0–255 scale. All 120 sampled comparisons passed. Decoder success and pixel agreement do not establish narrative quality.
6. **Packaging:** exact catalog coverage, distinct skill names, YAML metadata, local document links, candidate-file limits, and absence of deployment-specific paths/remote scene calls checked. Prior output preservation and export error paths are covered by the renderer regression suite.
7. **Optional Jev:** one authorized real request over the public style-candidate file returned whiteboard for a whiteboard-like query. This checks one integration path, not retrieval accuracy or improvement over manual selection. No Jev account/key is bundled or required.

## Environment and limits

Executed on Linux, Python 3.11, Playwright 1.62.0/Chromium and FFmpeg 6.1.1. Cross-platform file/CLI conventions are documented, but Windows and macOS were not tested. No API-based video generator, paid visual model, social posting or repository-visibility change was used for the examples.

The renderer blocks browser network requests but is not a hostile-code sandbox. Render only reviewed local HTML, with stronger isolation when needed. All figures are explanatory; no customer metrics or live system states were fabricated. Film, clay and print media are procedural treatments.

## Per-example export results

| Style | Frames | Duration | Size (bytes) | Source/video checks |
|---|---:|---:|---:|---|
| Bauhaus | 600 | 20.0 s | 362631 | Passed |
| 16 mm documentary | 600 | 20.0 s | 1276927 | Passed |
| Whiteboard | 600 | 20.0 s | 375780 | Passed |
| Blueprint | 600 | 20.0 s | 425544 | Passed |
| Comic book | 600 | 20.0 s | 593501 | Passed |
| HUD | 600 | 20.0 s | 389166 | Passed |
| Isometric | 600 | 20.0 s | 608417 | Passed |
| Paper cutout | 600 | 20.0 s | 468411 | Passed |
| Chalkboard | 600 | 20.0 s | 427823 | Passed |
| Pencil sketch | 600 | 20.0 s | 522571 | Passed |
| Clay-inspired | 600 | 20.0 s | 429404 | Passed |
| Kinetic typography | 600 | 20.0 s | 411274 | Passed |
| Flat-vector explainer | 600 | 20.0 s | 397464 | Passed |
| Linocut | 600 | 20.0 s | 399262 | Passed |
| Memphis | 600 | 20.0 s | 842718 | Passed |
| Pixel art | 600 | 20.0 s | 303695 | Passed |
| Retro 1970s | 600 | 20.0 s | 558443 | Passed |
| Single line | 600 | 20.0 s | 342196 | Passed |
| Terminal | 600 | 20.0 s | 445092 | Passed |
| Data storytelling | 600 | 20.0 s | 400744 | Passed |

## Reproduce the checks

From the package directory, through an agent terminal tool:

```sh
python scripts/test_render.py
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

The supplied MP4s were rendered in full. The renderer unit suite deliberately uses short fixtures to exercise failures quickly; it is not a substitute for the full-example results above.
