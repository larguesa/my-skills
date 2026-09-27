---
name: animation-data-storytelling
description: Use when animating verified data or named categories.
version: 0.1.0
author: Ricardo Pupo Larguesa (larguesa), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---
# Evidence-led data storytelling

## Use and avoid
- Use for sourced comparisons, real quantities and documented categories.
- Avoid numeric chart forms when the source contains only qualitative claims.
- A useful story can be categorical without pretending to measure performance.

## Visual grammar
- Make the central question a headline rather than a dashboard title.
- Use direct labels, aligned rows and restrained emphasis.
- Distinguish a count of categories from a count of people or delivered outcomes.
- Equal-sized rows represent equal visual treatment, not equal allocation.
- Use a bracket for shared oversight only when that relationship is documented.
- Do not substitute donut slices or percentage bars for missing data.
- Keep qualifiers close to the quantity, not hidden in the transcript alone.
- Preserve generous white space around the primary count and category list.

## Storyboard
- 0–5 seconds: introduce the sourced category count and reveal the named set.
- 5–10 seconds: complete the list and add its documented shared relationship.
- 10–17 seconds: hold the interpretation and any important caveat.
- 17–20 seconds: use the shared static CTA.
- Do not animate interim numbers that viewers might mistake for observations.

## Build the actual drawing
1. Extract source labels into a fixed array and retain their provenance.
2. Compute category count from the array rather than typing a disconnected total.
3. Check for duplicate labels before treating array length as a meaningful count.
4. Draw one equally sized row per category with direct naming.
5. Reveal names in reading order without changing their apparent magnitude.
6. Put the count beside explicit text describing what is being counted.
7. Add caveats such as not fixed headcount when the context warrants them.
8. Draw any oversight bracket outside the row text region.
9. Keep explanatory captions readable at delivery resolution.
10. Compare the final rendered labels against the source, not just the code.

## Motion direction
- Reveal context before interpreting evidence.
- Keep row geometry constant as labels enter.
- Use highlighting to focus attention, not to imply ranking.
- Let the fully labeled view hold longer than the reveal sequence.
- Use no ticker values, live indicators or invented trending animations.

## Content and rights
- Record source URL, retrieval date, definitions, units and population where applicable.
- Numeric comparisons need a defensible baseline and consistent units.
- Bars start at zero unless an explicit analytical reason is disclosed.
- For role categories, avoid implying one person per role or fixed staffing ratios.
- Distinguish a published capability description from independently measured results.

## QA pitfalls
- Count the final visible categories programmatically and compare to the headline.
- Check that human oversight is not accidentally counted as another role category.
- Long descriptions must fit without silently reducing text below minimum size.
- Bracket length must not be interpreted as a quantitative axis.
- Verify qualifiers remain visible in both opening and final explanatory frames.
- Inspect the exported still without narration; its meaning must remain honest.

## Runtime and verification
- Follow the [core skill](../../SKILL.md) and [runtime contract](../../references/runtime.md).
- Implement `window.scene(t)` as a pure redraw; call `A.frame` first.
- Keep creative content inside x96–1824 and y200–930; use body text at least 30px.
- Export `window.TRANSCRIPT`; preserve the runtime's readiness and playback APIs.
- Sample 0, 2, 5, 8, 11, 14, 16.8 and 19.9 seconds; inspect actual screenshots.
- Verify loaded fonts, zero JavaScript errors and deterministic out-of-order redraws.
- Confirm the shared CTA is identical throughout the final three seconds.
- See the [example](../../examples/data-storytelling/index.html) and [source notes](../../references/sources.md).
- Render from the package root:
  `python scripts/render.py examples/data-storytelling/index.html output.mp4 --duration 20 --fps 30`
