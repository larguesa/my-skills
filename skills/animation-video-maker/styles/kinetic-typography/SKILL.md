---
name: animation-kinetic-typography
description: Animate meaning through type, scale and rhythm.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Kinetic typography

Make the language itself perform the explanation; movement follows meaning.
Use original layouts, not a montage of borrowed title sequences.

## Use and avoid
- Use for a short proposition, contrast, manifesto or memorable principle.
- Pick sentences that can be understood without narration.
- Avoid dense evidence, product walkthroughs and paragraphs disguised as titles.
- Do not use dramatic scale to make an uncertain claim look established.

## Typographic grammar
- Choose one heavy display face and one readable supporting face.
- Maintain a strong left edge across successive compositions.
- Build hierarchy from scale and line breaks before adding motion.
- Use one bright accent for the operative word or logical connection.
- Reserve uppercase for short display phrases, not supporting paragraphs.
- Give oversized words more room than their visible glyph outlines require.
- Use a strike only when the accompanying sentence clearly rejects the phrase.
- Let plus signs connect actual complementary ideas, not imply an equation.
- Avoid gratuitous per-letter rotation, tracking shifts and bounce effects.
- Keep a stable supporting sentence available while the headline enters.

## Three-part storyboard
1. Name a premise and visibly reject or reframe it.
2. Introduce the alternative through a structured pair of concepts.
3. Resolve with the principle that stays constant.
4. Hold the resolution long enough to read it twice.
5. Move to the shared static call to action without re-animating its typography.

## Motion score
- Reveal whole lines through rectangular masks in 0.5–0.8 seconds.
- Stagger related lines by 0.1–0.3 seconds to establish reading order.
- Keep the masked baseline below its final position, then ease upward.
- Draw a meaningful strike or underline only after the words are legible.
- Make each major composition last approximately five or six seconds.
- Do not run another large animation during a key sentence's reading hold.
- Prefer a clean editorial cut between arguments over a decorative transition.

## Implementation
1. Read the [core workflow](../../SKILL.md) and reduce the script to its verbal beats.
2. Measure every headline using the final loaded font at its intended size.
3. Rebreak or shorten a line before reducing the font to fit.
4. Call `A.frame` first, then draw within x96–1824 and y200–930.
5. Use `ctx.save`, a rectangular clip and `ctx.restore` around each reveal.
6. Derive all positions and opacity from `t`, including stage boundaries.
7. Preserve heading sizes of at least 60px and supporting copy of at least 30px.
8. Keep accidental clipped ascenders, descenders and punctuation out of final holds.
9. Put the complete reading order in `window.TRANSCRIPT`.
10. Reuse the [shared runtime](../../references/runtime.md) for playback and export.

## QA and export
- Demonstrate the missing scene failure before implementing the composition.
- Capture 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds from the real player.
- Also sample just before and after editorial cuts to inspect masks.
- Check the rightmost glyph and the lowest descender at 100% resolution.
- Test thumbnail readability and ensure the strike does not destroy comprehension.
- Confirm fonts are loaded before measurement or export.
- Verify out-of-order seek determinism and the static final three seconds.
```sh
python scripts/render.py examples/kinetic-typography/index.html output.mp4 --duration 20 --fps 30
```
- Review the encoded sequence for rushed reading or unintended blank pauses.

## Content and permissions
- Attribute quotations and obtain rights where required.
- Do not turn service positioning into a numerical promise or universal guarantee.
- Keep an evidence trail in the [source notes](../../references/sources.md).
- The [Delivery Pods example](../../examples/kinetic-typography/index.html) contrasts hours with accountable capability.
- Brand language in that example is not a required template for other subjects.
