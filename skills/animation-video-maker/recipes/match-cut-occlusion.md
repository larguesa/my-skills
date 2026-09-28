# Match cut and occlusion: preserve the relationship

## Inputs
Two or three cleared shots or authored scenes; a meaningful shared shape, action or screen position; cut time; camera direction; output ratio. Name what the viewer should perceive as continuous and what is intentionally changing.

## Direction
Use a shared contour to connect subjects, not disguise a missing argument. Original example: an illustrated circular seal becomes the round end of a real tool, then the tool passes close to the lens to reveal a workbench. Do not claim the illustration is footage of the real product.

## Storyboard and timing
- 0-3 s: establish object A and its purpose.
- 3-5 s: move A to a clear handoff position and scale.
- At 5 s: cut to object B with the matched anchor; preserve travel direction.
- 5-8 s: hold long enough to recognize B, then let a motivated foreground surface approach.
- 8-9 s: under complete coverage, switch to scene C.
- 9-12 s: reveal C and hold the result.

## Motion and continuity
Record source/destination anchor coordinates in output pixels after all camera transforms. Match centroid, orientation and silhouette scale near the cut; match velocity when cutting on action. Exact shape equality is unnecessary if the visual relationship is clear. For an occlusion, compute a covering surface larger than the viewport and switch hidden content only while coverage is complete. Do not use a flash to conceal a bad handoff. Keep text outside the fast transition or defer it until the new shot settles.

## Assets and rights
Clear both source shots, any people and the soundtrack. Do not remove watermarks or use a stock preview as final footage. Record real footage versus reenactment versus illustration. A matched cut can imply causation, so avoid connecting unrelated evidence into a false before/after.

## Output
Editable shot/cut table, alignment anchors, source manifest, transcript and MP4. Code compositing suits precise masks; footage editing suits genuine action. Use either, without pretending an unimplemented editor adapter is bundled.

## Pitfalls
Matching only color; inconsistent eyeline; accidental direction reversal; one-frame uncovered corners; crossfade ghosting; motion blur spanning unrelated scenes.

## Validation
Review an adjacent-frame strip around each handoff and play the cut repeatedly. Check the audience recognizes the intended relationship without narration. Verify masks at all aspect ratios, text clearance and no accidental black frame. Keep shutter sampling on the correct side of a deliberate hard cut.
