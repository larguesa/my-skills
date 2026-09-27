---
name: animation-chalkboard
description: Animate cumulative explanations in chalk on a board.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Chalkboard animation

Teach one argument by leaving its reasoning visible on a shared board.
Chalk texture is drawn procedurally; no photographed classroom is implied.

## Use and avoid
- Use for problem framing, conceptual sequences and workshop summaries.
- Let the viewer inspect how the conclusion follows from earlier marks.
- Avoid legal fine print, dense formulas and detailed application interfaces.
- Do not use school imagery to imply credentials or scientific validation.

## Board grammar
- Choose a deep desaturated green with warm white chalk and one yellow accent.
- Keep a consistent baseline for the principal sequence.
- Draw connecting arrows between finished boxes, never through their labels.
- Use slightly imperfect parallel strokes to suggest chalk pressure.
- Add low-opacity short grains rather than a moving television-noise layer.
- Reserve yellow for the question, connective reasoning or concluding action.
- Use a clean licensed font; readability outranks handwriting authenticity.
- Let boxes be rough while text remains level and sharply rendered.
- Maintain enough empty board between the heading and the lesson.
- Do not erase earlier evidence merely to make room for a slogan.

## Storyboard
1. State the question in the upper-left board region.
2. Draw the first concept and reveal its concise explanation.
3. Complete its connector before opening the next concept.
4. Assemble the final implication beneath the accumulated reasoning.
5. Hold the entire board before the separate static call to action.

## Timing
- Write a substantial outline over 1.0–1.5 seconds.
- Fade its label in once the outline is sufficiently established.
- Allow roughly four seconds per reasoning step, including its reading hold.
- Draw connectors in 0.5–0.8 seconds; a short arrow need not take as long as a box.
- Keep completed marks stationary so the board remains a reference.
- Do not jitter the entire scene to simulate a hand-held camera.

## Construction procedure
1. Follow the [core workflow](../../SKILL.md) and identify the actual logical chain.
2. Lay out three readable concepts before writing any reveal code.
3. Establish all final box bounds and label measurements.
4. Call `A.frame` first with the dark-background flag for the correct logo.
5. Create chalk paths from explicit points, then add faint offset companions.
6. Use arc-length progress for path reveal, not point-count interpolation.
7. Seed grain positions from stable indices and confine them to the art field.
8. Derive the board's accumulated state entirely from the supplied `t`.
9. Keep art inside x96–1824 and y200–930; headings are at least 60px.
10. Keep supporting labels at least 30px and measure the longest one.
11. Add a complete English `window.TRANSCRIPT` for the argument.
12. Reuse the [runtime](../../references/runtime.md); do not implement another clock.

## QA and export
- Run the absent-scene test before implementing the player.
- Capture 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect arrowheads at 100%: repeated strokes must not become blobs.
- Confirm each concept is readable before its outgoing arrow begins.
- Check the bottom conclusion against the reserved footer band.
- Verify that grain does not reduce contrast in small supporting copy.
- Compare repeated timestamps after seeking backwards; pixels must match.
- Confirm fonts load locally and no page errors occur.
```sh
python scripts/render.py examples/chalkboard/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the encoded result; screenshots alone do not establish pacing.

## Evidence and reuse
- A drawn arrow expresses the script's relationship, not proven causation.
- Never invent experiments, measured success or institutional endorsement.
- Use authorized identities and read the [source notes](../../references/sources.md).
- The [Discovery example](../../examples/chalkboard/index.html) turns context into a pilot-plan lesson.
- Replace that example's service copy when applying the style to another topic.
