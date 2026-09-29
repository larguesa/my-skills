# Minimum smoke test before production

Use the existing [runtime environment](runtime.md), renderer and FFmpeg through the agent's terminal tool. No extra framework or dependency is needed. Use a fresh evidence folder and record commands, exit codes, source revision, browser version and actual observations. Render only reviewed local HTML.

## 1. Prove the render path

From the package root, with `python` pointing to the environment that contains Playwright:

```sh
python -m unittest discover -s tests -v
python scripts/test_render.py
python scripts/render.py demos/ui-morph/index.html smoke/prefix.mp4 --duration 2 --fps 30
```

Add `--browser /path/to/chrome` to the renderer if needed; tests use `RENDER_BROWSER`. Require no skipped browser tests, successful exit codes and `status: ok` in QA. Check empty JS/console error lists, expected blocked requests, six matching forward/reverse sample hashes, H.264/yuv420p, 1280 x 720, 60 frames, 2 seconds, 30 fps and no audio stream.

**Sampling is not export coverage.** This command encodes only `[0,2)` of the nine-second scene. The renderer's six PNG samples span the declared `DURATION`, here 0, 1.8, 3.6, 5.4, 7.2 and 8.955 seconds, even with a short `--duration`. Their reverse-seek hashes prove those sampled source frames repeat in the same browser. They do not prove all frames, all transitions, or bit-identical compressed MP4s. `--samples-only` writes QA/PNGs, not an MP4.

## 2. Cover actual transitions

The prefix does not contain every UI handoff. Export this compact demo in full:

```sh
python scripts/render.py demos/ui-morph/index.html smoke/full.mp4 --duration 9 --fps 30
ffmpeg -hide_banner -i smoke/full.mp4 -vf "fps=2,scale=320:-1,tile=6x3" -frames:v 1 smoke/contact.png
ffmpeg -hide_banner -i smoke/full.mp4 -vf "select='between(n,110,112)+between(n,128,130)+between(n,146,148)',scale=426:-1,tile=3x3" -frames:v 1 smoke/transition.png
ffprobe -v error -count_frames -show_streams -show_format -of json smoke/full.mp4
```

Expect 270 video frames, nine seconds and no audio. The transition sheet samples adjacent frames around the board handoff's start, midpoint and end. For a new scene, derive these indices from its actual cue table, including label swaps and loop seams; do not blindly reuse this demo's numbers. Use one frame per beat when a verified beat grid exists, plus adjacent frames at discontinuities. A uniform overview alone can miss a one-frame defect.

Inspect decoded sheets at intended viewing size for text collisions, clipping, jumps, anchor drift and unwanted blur. Watch transitions and the full encoded clip at normal speed before accepting motion quality. Compare decoded frames from repeat exports if testing encoder repeatability; allow documented compression error when comparing lossless source PNGs with lossy video. Report visual review separately from technical success. A headless run without playback review must disclose that limit.

## 3. Optional advisory scene-change scan

Use FFmpeg's existing `select` scene score to shortlist large inter-frame changes, not a new scanner:

```sh
ffmpeg -hide_banner -nostdin -i smoke/full.mp4 -vf "select='gt(scene,0.10)',showinfo" -an -fps_mode vfr -f null - 2> smoke/scene-scan.log
```

Inspect selected `pts_time` entries and their neighboring decoded frames. `0.10` is an exploratory threshold, not a validated acceptance boundary. Log it with the input hash and reconcile candidates with intentional cuts. Lowering it produces more candidates; a smooth small-area text jump can still be missed. This native global scene score is **not** the source article's local-average frame-jump detector and is **not defect detection**. Intentional cuts can be flagged; defects can go unflagged. A successful zero-candidate run may print `Output file is empty`; no selected frames is expected in that case, not a render failure or QA pass. Zero candidates does not mean zero defects. Do not turn the count into a pass/fail quality score.

## 4. Audio only when authorized

Keep the smoke master silent unless the brief explicitly authorizes sound and its assets. Then follow [audio cues](../techniques/audio-cues.md): use the same absolute-time cue table, define onset versus peak, record frame/sample rounding and an agreed tolerance, and check decoded picture/sound offsets at beginning, middle and end after muxing. Listen for clicks, clipping and masking. Stream presence, source cue times or an external article's precision claim are not measured sync. If audio is absent, record `audio sync: not applicable`, not `passed`.

## Acceptance record

Record source path/revision, LOOK revision, exact export interval, QA/probe results, tested seek timestamps, transition frames, visual/playback observations, scan threshold/candidates and audio authorization/measurement state. Fix actual failures before full production. Keep technical, visual, factual and rights gates separate. See [validation](validation-0.2.md) for the bundled run's scope.
