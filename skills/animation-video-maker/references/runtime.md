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

The HTML loads `assets/runtime.js`, the local `scene.js`, then calls `A.start(options)`. Load `assets/brand.js` before the runtime only for the original T2S identity. Without it, no logo, branded header/footer or shared CTA is drawn. Include a canvas with `id="canvas"` and buttons with `id="play"` and `id="replay"`. Each original scene exports:

```js
window.TRANSCRIPT = 'A complete, accessible description of the message.';
window.scene = function (t) {
  A.frame('#f5f8fc', false, 'EXAMPLE');
  A.text('A clear idea.', 96, 330, 80, A.ink, 800);
  // Draw all state from t, with balanced save()/restore().
};
```

Runtime API:
- `A.ctx`, `A.canvas`: native Canvas 2D context and canvas. Set its HTML `width` and `height` attributes before starting; clearing and background fills use these actual dimensions.
- `A.frame(background, dark, tag)`: fill the entire canvas background. With `brand.js`, also draw the original T2S logo, service, tag and footer. Without it, only the background is drawn.
- `A.text(text,x,y,size,color,weight,align,family)`: baseline coordinates, embedded Rubik/Montserrat defaults.
- `A.line(points,color,width,progress)`: polyline with arc-length reveal.
- `A.clamp`, `A.ease`: bounded normalized easing.
- `window.ready`: fonts and image Promise; always await before export.
- `A.start({title, description, service, duration, endcard})`: initialize once per page. `duration` defaults to 20 seconds and must be a finite number greater than zero and at most 600. `endcard:false` disables the shared CTA. With branding present, the default CTA occupies the final three seconds, or the entire duration if shorter than three seconds. Without branding, the scene always owns the full timeline. Invalid duration throws a `RangeError` synchronously.
- `window.DURATION`, `renderFrame(t)`, `draw({t})`: deterministic scene export. Time clamps to `[0, DURATION]`; draw returns JPEG base64 without a data-URI prefix.
- `?render=1`: autoplay disabled, controls hidden.

In the unchanged 20-second branded defaults, the shared CTA occupies seconds 17 to 20. Main artwork stays in x96–1824, y200–930. Reserve top and bottom strips for branding. Use body type >=30px and titles >=60px. Put complete narration in the transcript, not tiny on-screen paragraphs.

To change branding, replace the brand assets and their embedded equivalents in `brand.js`, then adjust `frame()` and `end()` in runtime.js. Preserve the source brand's rights. Font files retain OFL notices. `brand.js` embeds exact SVG bytes because file-origin image loading can taint a Canvas and break export.

## Security and limitations

The renderer disables HTTP(S) requests, WebSockets, service workers and downloads, uses an ephemeral browser and opens only one page. **This is not a sandbox for hostile HTML.** File access is enabled for reviewed local assets. Review unknown JavaScript before rendering, avoid sensitive directories and use OS/container isolation for untrusted content. No network access is needed by the examples themselves.

An infinite JavaScript loop can block a browser evaluation. Run untrusted or exploratory jobs under an external process deadline; API/socket timeouts are not total job deadlines. No script automatically changes system/browser configuration or installs dependencies.

The renderer reads the actual canvas dimensions after readiness and sizes its viewport accordingly. H.264/yuv420p export requires even dimensions, each from 2 to 8192 pixels, with at most 8,294,400 total pixels. The same bounds apply to samples-only runs. QA records `canvas.width` and `canvas.height`; ffprobe must match those dimensions. Keep canvas dimensions stable during rendering.

The runtime does not scale or reflow authored artwork or the legacy T2S overlays. Those overlays remain designed for 1920×1080. For portrait and square work, omit `brand.js` and lay out your scene using `A.canvas.width` and `A.canvas.height`. CSS resizing does not change export resolution.

CLI `--duration` still defaults to 20 and selects an interval within the declared animation. Pass the matching duration for shorter scenes; the CLI does not infer it. A shorter preview is not a complete creative result.

Example neutral eight-second scene initialization, with a 1080×1920 or 1080×1080 canvas and no `brand.js`:

```js
A.start({title: 'A clear idea', description: window.TRANSCRIPT, duration: 8, endcard: false});
```

```sh
python scripts/render.py path/to/index.html video.mp4 --duration 8 --fps 30
```

For a short export, deterministic seeks, transition review and an optional advisory native FFmpeg scene scan, follow the [minimum smoke test](smoke-test.md).

## Tests

```sh
python scripts/test_render.py
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

Renderer tests cover output preservation, bad arguments, JS/console failures, deterministic rendering, network rejection, duration limits, portrait/square video geometry, unsafe canvas bounds and ffprobe failure. Runtime browser tests cover optional branding, configurable duration, CTA opt-out, full-canvas clearing and filling, seek determinism and playback controls. Set `RENDER_BROWSER=/path/to/chrome` for these tests when using an existing browser instead of Playwright Chromium. `check_examples.py` remains specific to the 20 legacy examples. Runtime tests skip if Playwright is absent.  Package tests check metadata, catalog coverage, links and public-content constraints. Browser checks inspect all 20 source animations, but neither tests nor contact sheets replace visual judgment or source verification.
