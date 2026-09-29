# Release notes

## 0.2.0: creative production layers

This release keeps the original 20 T2S examples and adds original creative recipes, motion direction, execution-route guidance and brand-neutral demonstrations. The root now separates appearance, choreography, narrative and production tooling.

### Library changes

- Two additional visual languages: product interface and generative geometry.
- A reusable creative-brief template with source claims, asset rights, output contract, budget and attempt ceiling.
- An explicit local direction matrix and curated external sources. Jev remains optional.
- A complete style catalog at `references/style-catalog.json`. `references/catalog.json` retains its original role as the 20-entry T2S example manifest; consumers must not confuse the two.
- Generative and hybrid planning guidance is distinguished from the tested local Canvas export path. No paid video provider is silently installed or invoked.

### Incremental production checks

- Added a reusable LOOK visual card and a minimum smoke-test procedure using existing tools.
- Added an optional product-launch narrative linked to the existing product-proof safeguards.
- Documented native FFmpeg scene-change triage as advisory, not defect detection. No renderer behavior, dependency or framework changed.

### Compatibility

- Keep the whole directory when installing. Nested skill auto-discovery is not required; the root uses relative document paths.
- The original examples, brand rights exclusions and font notices remain in place.
- `scripts/check_examples.py` is the checker for the legacy T2S gallery, not a universal checker for arbitrary creative videos. New demos have their own real-player and stream tests.
- The renderer remains a local tool for trusted/reviewed input, not a sandbox for hostile HTML.
- A template can be production-ready as a brief without its provider route having been empirically validated. The validation report makes that distinction explicit.

See [expansion validation](references/validation-0.2.md), [original validation](references/validation.md) and [rights notices](NOTICE.md).
