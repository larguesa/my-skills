# UI continuity: one object, changed purpose

## Inputs
One user intention; three verified interface states or explicitly fictional states; exact labels; identity assets; target ratio; one meaningful click or drag. Record each state's bounds, radius, anchor, content and evidence. Example concept: a saved observation becomes a review card, then joins a collection.

## Direction
The viewer should recognize the same object before and after the change. Preserve an edge, accent or thumbnail, not merely the background color. Use a quiet field and one active region. An animated cursor is an explanatory reenactment, not proof that software was operated.

## Storyboard and timing
- 0-2 s: show the initial state and intention, already readable.
- 2-4 s: cursor acts; expand the carrier toward the second state's geometry.
- 4-7 s: hold the changed information. One supporting label explains the consequence.
- 7-9 s: carry the same item into a larger group or completed workflow.
- 9-12 s: hold the result. Close, or design a separate motivated return if looping.

## Motion and continuity
Author `x, y, width, height, radius` from absolute time. Keep image aspect ratios and glyph geometry independent of container stretching. Exit old labels before new labels occupy the same region. Use a bounded ease for geometry; reserve a damped spring for feedback. During a drag, the control follows the pointer directly; spring only after release, matching release position and velocity. Move the camera only when it clarifies a new scale.

## Assets and rights
Use authorized screenshots or locally authored UI. Preserve exact logos without warping. Redact private values. If screens, counts or actions are invented, mark the study illustrative. A license for an icon font does not grant rights to every brand it depicts.

## Output
Editable state table and scene, transcript, local assets and intended-format MP4. A silent version is a complete deliverable when requested. Use the code backend unless actual operation is the central claim, then use [product proof](product-proof.md).

## Pitfalls
Unrelated cards masquerading as a morph; click occurring after its effect; fake analytics; text stretched with chrome; perpetual bounce; busy camera and pointer competing for attention.

## Validation
Inspect transition start, midpoint and settled state, plus frames adjacent to the content handoff. Compare actual labels with evidence. Check pointer/control contact, clipping and reading at phone size. Repeat timestamps in reverse order. If looping, also apply the [loop boundary checks](seamless-loop.md).
