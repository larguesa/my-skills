---
name: animation-isometric
description: Build spatial maquettes that explain roles and systems.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Isometric spatial maquettes

Build a small functional environment, not a row of tilted cards.
Projection, contact, occlusion and purposeful objects make the space convincing.

## Use and avoid
- Use for relationships among functions, workflows, systems and review points.
- Use when a shared workspace metaphor makes coordination easier to understand.
- Avoid implying fixed staffing from the number of illustrated stations.
- Avoid camera or occlusion requirements that really need a 3D renderer.
- Avoid decorative buildings that contribute nothing to the explanation.

## Spatial grammar
- Use one projection for floors, routes, objects and contact shadows.
- A practical projection is `sx = ox + (x-y)*0.84`, `sy = oy + (x+y)*0.40-z`.
- Give the floor visible thickness and a consistent boundary.
- Shade top, left and right faces with a stable light direction.
- Anchor objects using restrained footprint shadows, not floating drop shadows.
- Give each station a distinct functional silhouette, not merely another color.
- Keep screen-space text horizontal and outside the model footprint.
- Separate human oversight from the automated or mechanical station vocabulary.
- A small travelling workpiece should explain a handoff, not imply live production.

## Spatial storyboard
1. At 0–5 seconds, assemble a workspace and introduce the first functions.
2. At 5–10 seconds, move attention or a workpiece to complementary functions.
3. At 10–17 seconds, bring the work toward a human checkpoint.
4. At 17–20 seconds, use the shared static branded closing frame.
- Let objects settle within roughly two seconds, then hold the arrangement.
- Keep the model stable so the viewer can learn its spatial relationships.
- Give each key sentence at least three seconds of clear reading time.
- Do not animate every object simultaneously after the workspace is assembled.

## Construction procedure
1. Read the [core workflow](../../SKILL.md) and list the functions the model must explain.
2. Plan the floor in world coordinates before drawing anything in screen space.
3. Implement one projection helper and use it for every vertex and route.
4. Draw the floor and low-level connectors before elevated objects.
5. Construct cuboids from separate visible faces with a shared palette convention.
6. Add original objects such as prototype blocks, monitors, plants or maintenance racks.
7. Sort separated objects from back to front; use face ordering if footprints overlap.
8. Derive lift, settling and handoff position from absolute time with clamped easing.
9. Draw a moving workpiece at the appropriate depth, not permanently above everything.
10. Call `A.frame(...)` first in strict-IIFE `window.scene(t)`; preserve safe margins.
11. Use at least 60 px headlines and 30 px supporting text in the screen plane.
12. Provide `window.TRANSCRIPT` and leave assets and controls to the [runtime](../../references/runtime.md).

## Truth and rights
- Explicitly identify a role-based model when object count is not team headcount.
- Do not represent supervised agents as autonomous owners of sensitive decisions.
- Do not invent actual equipment, client facilities or deployment architecture.
- Keep claims tied to verified service scope rather than visual wishful thinking.
- Use original geometry and retain font licenses and authorized logo assets.
- Consult [sources and rights](../../references/sources.md) before adaptation.
- The [delivery-pod example](../../examples/isometric/index.html) is a conceptual workshop.

## Inspect and export
- First run the contract test against a missing scene to establish its failure mode.
- Capture 0, 2, 5, 8, 11, 14, 16.8 and 19.9 second samples in a clean browser.
- Check all floor corners, lifted objects, face shading and contact shadows.
- Inspect routes behind objects and ensure the workpiece respects the same projection.
- Confirm each phase produces a meaningful spatial change, not only different text.
- Check model-label clearance and that no tall object enters the header.
- Verify fonts, no page errors, deterministic seeks and a static final CTA.
- From the package root:
```sh
python scripts/render.py examples/isometric/index.html output.mp4 --duration 20 --fps 30
```
- Review encoded motion and metadata separately; sampled stills do not certify the full video.
