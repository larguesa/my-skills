# Runtime, preview and export

## Requirements

Python 3.10+, Playwright 1.48+ (the release was tested with 1.62.0), its Chromium browser, FFmpeg with libx264, and ffprobe on PATH. Reuse installed dependencies. The live tests ran on Linux; Windows/macOS instructions are intended to be portable, not certified on those systems.

If setup is necessary, use an isolated environment from the package directory:

```sh
python -m venv .venv
# POSIX:
.venv/bin/python -m pip install playwright==1.62.0
.venv/bin/python -m playwright install chromium
# Windows equivalents:
.venv\Scripts\python.exe -m pip install playwright==1.62.0
.venv\Scripts\python.exe -m playwright install chromium
```

Use your OS package manager for FFmpeg, then verify `ffmpeg -version` and `ffprobe -version`. Browser/OS libraries may be needed on a minimal Linux host; installing them requires operator permission. No API key is required. Commands below use `python` to denote this environment's interpreter.

## Preview

Open `gallery.html` or `examples/<style>/index.html`. Keep the complete folder tree: scenes share assets. For a browser that restricts local font files, serve the package locally:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/gallery.html`. This is an optional localhost server, not a deployment. Do not expose a development server publicly. The browser does not upload anything. Each example has pause/replay, a text transcript and a source link. Reduced motion starts paused; playing is an explicit user choice.

## Render

From the package root, through the agent's terminal tool:

```sh
python scripts/render.py examples/blueprint/index.html preview.mp4 --samples-only
python scripts/render.py examples/blueprint/index.html video.mp4 --duration 20 --fps 30
```

`--browser /path/to/chrome` selects an existing compatible executable; otherwise Playwright Chromium is used. This never uses the user's logged-in browser profile. `--overwrite` is required if the video, QA file or sample directory already exists.

Outputs:
- `video.mp4`: H.264/yuv420p, no audio, faststart enabled.
- `video.qa.json`: actual errors, hashes, browser version, ffprobe results and timing.
- `video.samples/`: six lossless PNGs across the declared duration.
- On failure, a uniquely named failure report; an existing successful video stays intact.

The renderer uses JPEG frames streamed into FFmpeg rather than thousands of disk files. Export cost is CPU/browser time, not an inference API charge. It checks dimensions, frame count, duration and fps before replacing the destination. Publishing the MP4 is atomic; the neighboring samples/QA are not a multi-file transaction.

## Scene contract

The HTML loads, in order: `assets/brand.js`, `assets/runtime.js`, the local `scene.js`, then calls `A.start(options)`. Each original scene exports:

```js
window.TRANSCRIPT = 'A complete, accessible description of the message.';
window.scene = function (t) {
  A.frame('#f5f8fc', false, 'EXAMPLE');
  A.text('A clear idea.', 96, 330, 80, A.ink, 800);
  // Draw all state from t, with balanced save()/restore().
};
```

Runtime API:
- `A.ctx`, `A.canvas`: native Canvas 2D context and fixed 1920×1080 canvas.
- `A.frame(background, dark, tag)`: clear, exact T2S logo, service and footer.
- `A.text(text,x,y,size,color,weight,align,family)`: baseline coordinates, embedded Rubik/Montserrat defaults.
- `A.line(points,color,width,progress)`: polyline with arc-length reveal.
- `A.clamp`, `A.ease`: bounded normalized easing.
- `window.ready`: fonts and image Promise; always await before export.
- `window.DURATION=20`, `renderFrame(t)`, `draw({t})`: deterministic scene export; draw returns JPEG base64 without a data-URI prefix.
- `?render=1`: autoplay disabled, controls hidden.

The shared CTA occupies seconds 17–20. Main artwork stays in x96–1824, y200–930. Reserve top and bottom strips for branding. Use body type >=30px and titles >=60px. Put complete narration in the transcript, not tiny on-screen paragraphs.

To change branding, replace the brand assets and their embedded equivalents in `brand.js`, then adjust `frame()` and `end()` in runtime.js. Preserve the source brand's rights. Font files retain OFL notices. `brand.js` embeds exact SVG bytes because file-origin image loading can taint a Canvas and break export.

## Security and limitations

The renderer disables HTTP(S) requests, WebSockets, service workers and downloads, uses an ephemeral browser and opens only one page. **This is not a sandbox for hostile HTML.** File access is enabled for reviewed local assets. Review unknown JavaScript before rendering, avoid sensitive directories and use OS/container isolation for untrusted content. No network access is needed by the examples themselves.

An infinite JavaScript loop can block a browser evaluation. Run untrusted or exploratory jobs under an external process deadline; API/socket timeouts are not total job deadlines. No script automatically changes system/browser configuration or installs dependencies.

`ponytail:` geometry is deliberately fixed at 1920×1080. Other dimensions require updating runtime, scene layout, renderer validation and tests together. Other durations require changing the scene timeline and CTA as well as `DURATION`; CLI duration alone only selects an export interval within the declared animation. A shorter preview is not a complete creative result.

## Tests

```sh
python scripts/test_render.py
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

Renderer tests cover output preservation, bad arguments, JS/console failures, deterministic rendering, network rejection, duration limits and ffprobe failure. Package tests check metadata, catalog coverage, links and public-content constraints. Browser checks inspect all 20 source animations, but neither tests nor contact sheets replace visual judgment or source verification.
