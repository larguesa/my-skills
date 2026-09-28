# Seamless loop: recurrence with a reason

## Inputs
A recurring action, period `L`, fps `F`, opening composition, invariant object and optional cleared audio. Choose a cycle rather than forcing a conventional ending into a loop. Example: a paper ribbon carries a question around a desk and returns with its original orientation.

## Direction
A repeat should reward recognition. Show one meaningful transformation and return through a motivated action. No compulsory CTA or arbitrary fade to black. Use the [UI](ui-continuity.md) or [portal](portal-journey.md) recipe when its return is the actual story.

## Storyboard and timing
For an example eight-second cycle: 0-2 s establish and begin; 2-4 s transform; 4-6 s resolve; 6-8 s return through a path or fully covering surface. Leave reading time inside the cycle, not a duplicate frame at its boundary. If the result cannot naturally return, choose a non-looping close.

## Motion and continuity
Use `phase = 2*pi*t/L` and integer-frequency periodic functions, or explicitly close authored curves. Require position, geometry, opacity, lighting, texture phase, content, camera and velocity to agree at `t=0` and `t=L`. Seeded randomness alone does not make a sequence periodic. Hide a state reset only under verified full occlusion; entering and exiting visible motion must still agree.

For constant fps require integer `N=L*F` or adjust the agreed duration. Export samples `n/F` for `n=0..N-1`. Do not append `t=L`: the final encoded frame should normally differ from frame zero by one ordinary motion step. Equal first/last encoded images can introduce a pause.

## Assets and rights
Use original cyclic geometry or cleared footage that actually closes. Ping-pong reverses velocity abruptly at its ends unless motion settles first, and it can reverse smoke, gravity or speech implausibly. Clear looping and editing rights for audio and footage.

## Output
Editable periodic scene, period/fps manifest, transcript, silent MP4 and optional audio-muxed version. A reduced-motion preview may be a deliberate still; the video itself remains a separately labeled motion deliverable.

## Pitfalls
Matching only endpoint pixels; cursor teleport; stochastic grain phase jump; duplicate endpoint; audible click; codec padding mistaken for source continuity.

## Validation
Compare exact rendered endpoints and sample adjacent times on both sides for velocity. Inspect the encoded last-to-first transition over several repeats. Probe frame count and duration. For audio inspect waveform continuity, play the loop and account for encoder priming/padding. Report visual and audio loop status separately.
