---
name: animation-whiteboard
description: Explain reasoning through progressive marker drawings.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Progressive whiteboard drawing

Let the viewer follow a thought as it becomes a drawing.
A whiteboard sequence is a cumulative explanation, not cards on white paper.

## Use and avoid
- Use for newcomer explanations, hypotheses, bounded processes and decisions.
- Use when the order of drawing teaches the relationship between ideas.
- Avoid complicated topology with many simultaneous arrows.
- Avoid a fake drawing hand or illegible handwriting used as a style shortcut.
- Do not suggest proven causality merely by connecting two symbols with an arrow.

## Marker grammar
- Use warm near-white paper, dark ink and one accent for the explanatory route.
- Keep texture sparse, stationary and much quieter than the marker line.
- Construct symbols from imperfect but intentional polylines.
- Give circles small fixed irregularities rather than animated wobble.
- Keep the same stroke width across related symbols.
- Use dark contours, colored relationships and straight readable type.
- Reveal arrow stems before their heads so direction has a physical cause.
- Place captions outside the symbol bounds; never write through a diagram.
- A bracket can gather several ideas more clearly than another enclosing box.

## Storyboard by accumulation
1. At 0–5 seconds, title the question and draw the first concept.
2. At 5–10 seconds, extend the reasoning to the next concept.
3. At 10–13 seconds, add the final concrete artifact or decision.
4. At 13–17 seconds, gather the drawing with a bracket and hold its synthesis.
5. At 17–20 seconds, switch to the shared static CTA.
- Do not erase the first concept before the viewer can compare it with the last.
- Let a completed drawing hold while its caption remains still.
- Budget at least three seconds for the final sentence.

## Path construction procedure
1. Read the [core workflow](../../SKILL.md) and outline the argument in plain language.
2. Allocate symbol centers and label rectangles before sampling any paths.
3. Store paths as local point arrays with deterministic small irregularities.
4. Compute progress from absolute time; never append points to persistent state.
5. Reveal by accumulated arc length, not by the number of sampled vertices.
6. Skip the stroke entirely at progress zero: round caps otherwise leave dots.
7. Assign a start time and duration to each contour and internal detail.
8. Draw structural contours before secondary marks and connective arrows.
9. Use `A.line` through a small guard helper, retaining runtime arc-length behavior.
10. Call `A.frame(...)` first inside `window.scene(t)` and keep all art in its safe region.
11. Use at least 60 px headings and 30 px labels with measured line widths.
12. Supply `window.TRANSCRIPT`; leave controls and fonts to the [runtime](../../references/runtime.md).

## Truth and adaptation
- A laboratory flask can stand for a hypothesis, not for a completed scientific trial.
- A prototype screen is schematic unless a real authorized screenshot is supplied.
- Do not add success stamps, invented milestones or unsupported outcomes.
- Use original symbols and authorized assets; preserve font and brand rights.
- Read [source notes](../../references/sources.md) before changing factual copy.
- The [discovery example](../../examples/whiteboard/index.html) demonstrates the grammar only.

## QA and rendering
- Watch the scene contract fail before implementation; use the same test afterward.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds in a clean browser.
- Inspect early frames for premature dots at not-yet-started path endpoints.
- Check partial contours, arrow order, label clearance and the completed bracket.
- Check the final caption is readable before the closing frame replaces it.
- Verify font loading, no page errors, backward seeks and static CTA behavior.
- Inspect the entire drawing at full size, not only a reduced contact sheet.
- Execute from the package root:
```sh
python scripts/render.py examples/whiteboard/index.html output.mp4 --duration 20 --fps 30
```
- Review the encoded video for drawing speed; still samples cannot establish temporal fluency.
