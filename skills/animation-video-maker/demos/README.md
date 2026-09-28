# Original motion studies

Three brand-neutral compositions, not product claims or adaptations of an upstream demo. Code and prose: Ricardo Pupo Larguesa (larguesa), Hermes Agent. MIT. The existing local Rubik and Montserrat fonts retain their OFL notices in the package assets directory.

## Studies

| Study | Composition | Export | Sound |
|---|---|---|---|
| [One thought. Many forms.](ui-morph/index.html) | A chip expands into a card, separates into a board, then returns | 1280×720, 9 s, 270 frames | Silent |
| [Space becomes connection](type-match-cut/index.html) | Letter spacing creates a gap; an underline match-cuts into a bridge | 1280×720, 10 s, 300 frames | Silent |
| [Within, another world](recursive-portal/index.html) | Portrait recursive rounded geometry with periodic deformation | 720×1280, 8 s, 240 frames | Original synthesized bed |

All exports are H.264, yuv420p, 30 fps. The portal is a recursive geometric study, not a camera traveling into a different scene or a scientific simulation. UI is fictional and explicitly labeled. There are no performance claims, stock assets, paid calls or remote runtime requests.

## Preview and edit

From the package root, run `python -m http.server 8000 --bind 127.0.0.1` and open `http://127.0.0.1:8000/demos/`. Serving locally avoids browser restrictions on file-URL font loading. All resources remain local. Each player begins paused, supplies semantic Play/Pause, Replay and seek controls, and includes a transcript. Reduced-motion preference prevents automatic motion, including after replay. Explicit Play still works. Canvas previews are silent, including the portal; the portal's exported MP4 contains the sound bed.

Edit each `scene.js` for copy, palette, geometry and timing. Edit its `index.html` for canvas geometry. Update `catalog.json` and its static gallery when these change. `player.js` is a small demo-specific neutral runtime with local fonts and no branding dependency. It exposes `ready`, `DURATION`, `renderFrame(t)`, `draw({t})` and `TRANSCRIPT`. Drawing is pure absolute time; playback timing does not drive exported state. `?render=1` disables interactive playback.

## Reproduce the renders

Use the existing Python/Playwright environment and installed Chrome. From the package root, set `PYTHON` and `CHROME` to those executable paths. Choose a new output location or explicitly pass `--overwrite` to the renderer when replacing an existing render and its QA files.

```sh
"$PYTHON" scripts/render.py demos/ui-morph/index.html ui-morph.mp4 --duration 9 --fps 30 --browser "$CHROME"
"$PYTHON" scripts/render.py demos/type-match-cut/index.html type-match-cut.mp4 --duration 10 --fps 30 --browser "$CHROME"
"$PYTHON" scripts/render.py demos/recursive-portal/index.html portal-silent.mp4 --duration 8 --fps 30 --browser "$CHROME"
python demos/synthesize_audio.py portal-silent.mp4 portal-with-audio.mp4
"$PYTHON" demos/verify.py --browser "$CHROME" --evidence ./demo-evidence
```

The last command verifies the bundled `demos/*/video.mp4` artifacts. To check new exports, explicitly replace those artifacts first or change their manifest paths. The renderer does not add sound. In the delivered portal directory, `silent-source.mp4` is the renderer output and `video.mp4` is the final audio-muxed artifact. `synthesize_audio.py` uses FFmpeg `aevalsrc` at 48 kHz: a 110 Hz fundamental, 164.813778 Hz fifth and 220 Hz octave, a periodic amplitude envelope, and short fades. It copies the H.264 stream without recompression and encodes stereo AAC at a requested 160 kb/s. No samples or generated model audio are used. The script refuses to overwrite its destination.

Equivalent native synthesis and mux command:

```sh
ffmpeg -i portal-silent.mp4 -f lavfi -i 'aevalsrc=0.085*(0.65+0.35*cos(2*PI*t/8))*sin(2*PI*110*t)+0.038*sin(2*PI*164.813778*t)+0.018*sin(2*PI*220*t)|0.085*(0.65+0.35*cos(2*PI*t/8))*sin(2*PI*110*t+0.12)+0.038*sin(2*PI*164.813778*t)+0.018*sin(2*PI*220*t):s=48000:d=8' -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 160k -af 'afade=t=in:d=0.6,afade=t=out:st=7:d=1' -t 8 -movflags +faststart portal-with-audio.mp4
```

## Actual validation

All three movies were rendered using the package's real renderer, the existing Playwright environment and installed Chrome. Renderer QA returned `ok`; every sampled repeat hash matched. `verify.py` passed for all three: pause/play/replay/seek, static reduced-motion preview, nonempty transcript, reverse-order frame determinism, no JavaScript errors, no remote requests, intended dimensions and frame counts. UI and portal endpoint JPEGs at t=0 and t=duration were identical. This endpoint test does not alone prove temporal smoothness.

Real MP4s were decoded into six-frame contact sheets. Additional transition-dense sheets covered UI at 1.8, 2.0, 2.2, 3.9, 4.2, 4.7, 7.1, 7.5 and 7.9 seconds; typography at 3.8, 4.0, 4.2, 4.4, 4.6, 7.4, 7.6, 8.0 and 8.4 seconds. Visual review found overlapping copy in the first pass. The final sources gate UI details until surfaces have room, sequence outgoing/incoming typography without overlap, and use an opaque closing panel. Both affected movies were rerendered and the corrected decoded sheets inspected. The portal's geometry and text remain within their intended silhouette and margins.

The portal final has stereo AAC at 48 kHz and an eight-second video stream. FFmpeg `volumedetect` measured mean -26.9 dB and maximum -18.1 dB in the decoded audio. This verifies nonzero audio and ample peak headroom, not a listening-quality judgment. No listening session is claimed. Source and final audio artifacts are separately retained.

Posters are decoded from the actual final MP4s. Detailed QA, ffprobe streams and contact sheets are retained outside the repository in the delivery evidence directory; no machine-specific paths are embedded here. Small UI labels are compositional detail rather than the primary narrative; do not use them to convey essential instructions at thumbnail scale.
