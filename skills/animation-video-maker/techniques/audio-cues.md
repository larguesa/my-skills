# Audio cues and phrase timing

A cue sheet is a shared clock, not permission to move something on every beat.

## Build the clock

1. Obtain the actual cleared audio file. Record sample rate, duration and any leading silence.
2. Mark the first downbeat and section boundaries by listening. Tempo estimates and onset peaks are candidates, not ground truth.
3. For steady tempo `B` beats/minute, quarter-note spacing is `60/B` seconds. If a bar has `m` quarter-note beats, `bars*m*60/B` gives duration. A time signature or tempo change needs an explicit map.
4. Store cue times in seconds or exact sample indices; derive frame numbers once, documenting rounding. Never accumulate rounded frame intervals over a long track.
5. For speech, use phrase starts, stressed words, pauses and the time needed to read. Do not quantize all speech onto a dance grid.

At 96 BPM in 4/4, eight bars take 20 seconds. The same eight bars at 120 BPM take 16 seconds. Confirm the actual meter and tempo rather than copying either number blindly.

## Sound placement and mixing

If a sound's intended transient is at local sample `k` with sample rate `R`, place the file at `event_time-k/R`. Decide whether the intended sync point is onset or peak; not every sound should be peak-aligned. Trim leading silence only with that decision recorded.

Keep speech intelligible. Use gain envelopes or measured ducking where music masks words. Prevent clipped peaks and allow headroom before encoding. Choose a loudness target for the actual destination; a single LUFS value is not mandatory for all videos. FFmpeg's `loudnorm` can measure/normalize, but preserve measured values and inspect true peaks, loudness range and listening quality. Do not infer successful mixing merely because an audio stream exists.

Original synthesis can be small and sufficient: a short tonal cue with attack/release avoids clicks better than an abrupt waveform. Use fixed seeds for noise. Create only the needed accents; silence is a useful event.

## Media handoff

Finish the deterministic silent render first. Align audio from the same zero point, then mux an explicitly mapped video and audio stream. Preserve the silent master. Specify codec, sample rate and intended duration instead of relying on defaults. Do not use automatic shortest-stream truncation to conceal a duration mismatch. Playback speed changes require explicit treatment of audio pitch, cue positions and captions.

For loops, choose a musical phrase that closes naturally. Inspect source waveform endpoints and listen after encoding; crossfades alter timing and may smear the downbeat. AAC priming or padding can affect repeated playback even when the source waveform closes. Report whether the delivered playback environment actually loops cleanly.

## Verification

- Compare visual events and audio onsets at beginning, middle and end to detect drift.
- Inspect decoded frame timestamps and audio duration; check intended sample/frame tolerance.
- Verify exact lyric text and phrase order against the recording.
- Listen for clicks, clipping, abrupt cuts and masked narration.
- Confirm licensed uses include the actual channel and delivery, with no promise that royalty-free means unrestricted.

See [cue-led miniature](../recipes/cue-led-miniature.md) for a complete creative template and [source references](../references/creative-sources.md) for FFmpeg and rights documentation.
