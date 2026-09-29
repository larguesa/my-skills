# Creative expansion validation (0.2.0)

## Scope

This release expands a working code-animation skill into a creative production library. It does not claim that the upstream videos were reproduced, that every recipe was rendered, or that a generative-video provider was integrated or benchmarked.

The library includes 22 visual style guides, the original 20 T2S service examples, original creative recipes and three brand-neutral demonstrations. The [style catalog](style-catalog.json), [legacy example catalog](catalog.json), [demo manifest](../demos/catalog.json) and [research ledger](creative-research.json) have distinct roles.

## Source analysis

The upstream revision `1c092195b7bda246455827bc0be820be6d6a7b97` was inventoried as 282 entries containing 229 exact distinct supplied texts. Each distinct text received a concept-level note and an adapt/reject rationale; each entry retained provenance and a source-text hash in the private review. Independent reconciliation matched all 282 source hashes and all 229 notes. Five source entries are explicitly marked partial. Unflagged entries may still depend on missing attachments.

The public ledger contains original notes and pinned source links, not upstream prompt bodies. General principles were synthesized into new guidance. No upstream executable code or media was imported, and no reuse license was assumed. See [sources and rights](creative-sources.md).

## Runtime and renderer changes

- Missing `brand.js` no longer prevents the runtime from starting. Omitting it gives an unbranded frame; the legacy branded examples keep their appearance.
- `A.start` accepts a finite positive duration up to 600 seconds and `endcard:false`. Playback stops and restarts using the declared duration.
- Canvas clearing and background filling use actual dimensions. The renderer validates even dimensions, side and pixel-count bounds, and probes the exported dimensions.
- Existing offline/network protections, error reporting, determinism checks and output-preservation behavior remain covered by regression tests.

The original and updated runtimes were compared in the same browser at 0, 4, 5, 8, 10, 12, 16, 17, 19.9 and 20 seconds for every legacy style. All 200 sampled frame hashes matched exactly. This is a sampled backward-compatibility check, not proof that every possible frame or custom scene is identical across browser versions.

## New encoded demonstrations

| Demo | Format | Duration / fps | Audio | Purpose |
|---|---|---|---|---|
| UI morph | 1280 x 720 | 9 s / 30 | None | A single idea chip grows into a card and board, then returns |
| Type match cut | 1280 x 720 | 10 s / 30 | None | Letter spacing and a shared line express space becoming connection |
| Recursive portal | 720 x 1280 | 8 s / 30 | Original synthesized stereo AAC, 48 kHz | Portrait recursive geometry with a quiet sound bed |

The portal is a recursive geometric study, not footage of a physically traversed world or proof of an infinite-zoom provider. Its visual recurrence and its audio fade are different properties. The silent source is retained separately from the audio-muxed final.

The actual H.264/yuv420p files were decoded and checked with ffprobe. Player checks cover offline operation, readiness, transcripts, accessible canvas labels, reduced-motion behavior, playback controls and out-of-order deterministic seeks. The manifest is checked against the real streams, including dimensions, duration, fps and audio presence.

Visual review included decoded overview frames and denser transition samples. The first UI and typography pass exposed overlapping copy; the corrected versions delay incoming text until there is room and use sequential typography with an opaque closing panel. New exports, not merely corrected source, were reviewed after these fixes. Endpoint equality for visual loops is useful but is not by itself proof of smooth velocity at the join.

The portal audio was technically measured: mean -26.9 dB and peak -18.1 dB using FFmpeg volumedetect. It is nonzero and has peak headroom. This is not a listening-quality judgment; no listening session is claimed. The final soundtrack fades and is not advertised as a seamless audio loop.

Both galleries were checked at desktop and mobile viewport widths for horizontal overflow and JavaScript errors. Their HTML is a local preview, not a hosted web application; GitHub's source viewer does not execute it.

## Reproduce the checks

From this package directory, use an agent's terminal tool with the documented Python/Playwright environment, Chrome/Chromium and FFmpeg:

```sh
python -m unittest discover -s tests -v
python scripts/test_render.py
python scripts/check_examples.py --output ./legacy-qa
python demos/verify.py --browser /path/to/chrome --evidence ./demo-evidence
```

Replace the illustrative browser path with the installed executable. `RENDER_BROWSER` selects the browser for the test suites. `scripts/render.py` itself takes `--browser`. The legacy checker validates the 20 T2S examples only. Read [demo reproduction](../demos/README.md) for output filenames, durations and the explicit audio-finishing step.

Browser-dependent tests skip when Playwright is absent; a skipped suite is not evidence of a successful render. Rendering tests require FFmpeg/ffprobe. Keep private machine paths, raw QA logs and credentials outside the distributable.

## Incremental workflow validation

The visual direction card, minimum smoke procedure and optional product-launch recipe were added without changing production code or dependencies. The source post was consulted via an X Search summary only; its performance, cost and model claims were not independently verified. The launch recipe is documentation, not a newly captured product demonstration.

A fresh Linux run used the existing Playwright environment and Chrome browser: all 15 package/runtime/demo tests and all 12 renderer integration tests passed with no skips. The demo verifier passed for all three existing demos. No new audio was generated or muxed for this smoke test.

The documented UI-morph prefix was actually exported as H.264/yuv420p, 1280 x 720, 30 fps, 60 frames and 2.000 seconds, with no audio. A separate full nine-second export contained 270 frames. Both QA reports recorded successful reverse-seek equality for all six source samples, with no JavaScript, console or blocked-request entries. Source sampling covered the declared nine-second scene, not only the encoded two-second prefix.

The full export was decoded into an 18-frame overview and a nine-frame adjacent-transition sheet around frames 110-112, 128-130 and 146-148. Those sheets were visually inspected: no obvious text collisions or clipping appeared at those samples; the intermediate overlapping colored carriers were intentional and their incoming text remained hidden until the handoff. Small body copy in the overview is not evidence of mobile readability. No normal-speed human playback review or frame-by-frame visual certification is claimed.

The native FFmpeg scene scan ran successfully at threshold 0.10 on the full export and selected zero frames. Its empty-output warning was expected. This result is advisory, not proof of defect absence; localized glitches can be missed. Audio sync was not applicable to these silent exports. Existing portal audio stream checks do not establish newly measured sync or listening quality.

The refreshed distributable includes an updated SHA256 manifest and is verified by extraction and exact member/hash comparison. Raw logs, sample PNGs, decoded sheets, probe JSON and the source-retrieval note are retained separately from the portable package.

## Boundaries

- Generative footage, provider selection, reference-image conditioning and hybrid compositing are documented production routes, not newly tested provider adapters.
- No paid video generation, stock acquisition or publication was performed for this expansion.
- Recipes and external references are not guarantees of quality. Every new brief needs its own rights check, factual review, visual review and real export verification.
- Original T2S example media remain covered by the [0.1.0 validation](validation.md); they were not needlessly re-encoded.
- External link availability is a point-in-time check. Asset-specific licenses and commercial permissions must be rechecked at use time.
