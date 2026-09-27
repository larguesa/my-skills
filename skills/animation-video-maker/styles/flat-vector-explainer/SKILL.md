---
name: animation-flat-vector-explainer
description: Create original flat-vector explanatory animation.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Flat-vector explainer

Explain a system with original geometric characters, objects and clear spatial roles.
This is a generic visual technique, with no studio affiliation or imitation claim.

## Use and avoid
- Use for capabilities, collaboration, process roles and introductory system stories.
- Give each illustrated object an identifiable narrative purpose.
- Avoid scientific detail that the simplified geometry cannot communicate faithfully.
- Avoid copying a recognizable studio's character language, palette or composition.

## Visual grammar
- Draw with circles, rounded rectangles and a few purposeful custom silhouettes.
- Use flat fills with a restrained palette; do not simulate material texture.
- Separate background, connecting structure and active concepts by value contrast.
- Keep stroke weights consistent when lines are needed at all.
- Use schematic figures as role symbols rather than portraits.
- Maintain generous whitespace between a figure and its caption.
- Anchor the system with one large shared object, such as a worktable.
- Put capabilities in a separate region and connect them to the shared object.
- Make a review checkpoint visually distinct from an autonomous agent.
- Use human proportions and shapes of your own design, not traced assets.

## Storyboard
1. Establish the common outcome or shared work surface.
2. Introduce complementary participant types around that shared object.
3. Reveal capabilities in a clear order while the central system stays visible.
4. Add an explicit decision or review boundary.
5. Hold the complete system, then use the shared CTA.

## Timing
- Let figures arrive in less than a second without attention-grabbing bounce.
- Reveal capability labels approximately every two seconds.
- Retain each label so earlier capabilities get a substantial reading hold.
- Draw relationships only after their endpoints exist.
- Hold the completed review boundary for at least three seconds.
- Keep resting characters still rather than adding decorative blinking loops.

## Construction procedure
1. Follow the [package workflow](../../SKILL.md) and list the actual roles in the script.
2. Distinguish conceptual role types from any factual headcount.
3. Compose the final system with a separate label column and illustration field.
4. Call `A.frame` first and stay within x96–1824, y200–930.
5. Implement small local helpers for disks, tiles and original figure silhouettes.
6. Draw background objects before foreground participants and connectors.
7. Keep the human review element separate from any agent symbol.
8. Derive reveal progress from absolute `t`, not accumulated object state.
9. Use headings of at least 60px and supporting labels of at least 30px.
10. Measure names inside their colored tiles before animating them.
11. Provide a complete transcript explaining the conceptual nature of the figures.
12. Use the [runtime API](../../references/runtime.md) without adding dependencies.

## QA and export
- Run a missing-scene contract check before implementation.
- Capture 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds.
- Inspect heads, torsos and furniture for accidental tangencies or visual mergers.
- Check that a connector never cuts through a label or a figure's face.
- Confirm color is not the sole means of identifying different roles.
- Verify no person count, approval status or performance metric is implied as real.
- Check local fonts, JavaScript errors, deterministic seeking and the held CTA.
```sh
python scripts/render.py examples/flat-vector-explainer/index.html output.mp4 --duration 20 --fps 30
```
- Inspect the actual encoded motion and not only a contact sheet.

## Originality and truth
- Do not use a studio name as the output's title, endorsement or marketing hook.
- Do not reuse third-party mascots, signature characters or copied scene layouts.
- A check symbol denotes a conceptual checkpoint, not a real completed approval.
- Verify service claims using the [source notes](../../references/sources.md).
- The [Delivery Pods example](../../examples/flat-vector-explainer/index.html) depicts role categories, not fixed staffing.
- Its workshop, figures and agent icon are original schematic Canvas drawings.
