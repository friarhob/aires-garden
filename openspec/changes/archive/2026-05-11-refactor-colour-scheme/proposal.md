## Why

The off-white `#F0EAE0` is too hot. It does triple duty in the palette — light `--bg-subtle`, dark `--text`, dark `--text-heading` — and in every role it reads as glaring: high lightness (91%) and moderate saturation (36%) make it glow on the dark background and wash out next to the near-white light `--bg` (`#FAF7F2`). The light `--bg` itself is also too bright, sitting at 97% lightness with a warm tint that pushes it past comfortable reading. While we are settling these values, we also want a documented contrast audit (no pair has ever been verified beyond `--accent`) and a proper palette reference, so future colour changes can be made with confidence rather than by eye alone.

## What Changes

- Replace the off-white token value in all three sites (light `--bg-subtle`, dark `--text`, dark `--text-heading`) with `#DCCEBD` (HSL 33° / 31% / 80%) — selected via three rounds of rendered candidate review against the existing palette. The full preview lives at `tools/colour-candidates.html` until archive.
- Replace the light `--bg` value with `#E7DED4` (HSL 32° / 28% / 87%) — same review process. Pairing with the new `--bg-subtle` clears the ≥6 lightness-point separation rule (gap = 7).
- Audit every in-use colour pair in both modes against WCAG AA (4.5:1 for body text, 3:1 for large/heading). Pairs include `text/bg`, `text-muted/bg`, `text/bg-subtle`, `text-muted/bg-subtle`, `text-heading/bg`, `accent/bg`, `accent/bg-subtle`, `bg/accent` (tag-chip hover), and the four `admonition-*` colours as title text on `bg-subtle`. Adjust only those that fail. The audit is reproducible: a small Python script lives at `tools/contrast_audit.py` and prints a results table.
- Dedupe the four token blocks. Light tokens currently live in two identical blocks (`:root` and `:root[data-theme="light"]`); dark tokens live in two near-identical blocks (`@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` and `:root[data-theme="dark"]`). Collapse via grouped selectors so each token value is declared once per mode.
- Create `docs/visual-identity.md` (the `docs/` directory does not yet exist). Covers: palette listing (token name → hex → role), token naming conventions, mode strategy (default light, OS dark, user override), typography tokens, and contrast targets with the audit results table.
- Fix a stale reference in the `design-tokens` spec. The "Admonition semantic tokens defined" requirement still names `@media prefers-color-scheme: light` as one of four required token blocks, but `default-light-mode` removed that block. Update the requirement to reflect the actual structure (post-dedupe).
- Broaden the WCAG requirement from "interactive accent only" to "all functional pairs", with the audit table as evidence.

## Capabilities

### New Capabilities

*(none — this is a token-layer revision plus documentation, not a new capability)*

### Modified Capabilities

- `design-tokens`: Hex values in the "Dark mode token set (default)" and "Light mode token set (override)" requirements change. The "WCAG AA contrast on interactive accent" requirement broadens to cover all functional pairs. The "Admonition semantic tokens defined" requirement is updated to reference the deduped block structure (no more stale `@media prefers-color-scheme: light` mention). A new requirement adds the `docs/visual-identity.md` documentation obligation. The "Heading colour token distinct from body text" requirement updates the dark `--text-heading` hex to match the new off-white.

## Impact

- `themes/garden/static/css/styles.css` — token value updates plus block dedupe (light `:root` + `:root[data-theme="light"]` collapsed; dark media-query block + `:root[data-theme="dark"]` declarations remain separate by necessity)
- `tools/contrast_audit.py` — new file; one-shot Python script that prints a contrast table for every in-use pair in both modes
- `tools/colour-candidates.html` — new file (already created during propose); rendered preview of the candidate sets considered. Removed at archive time once `docs/visual-identity.md` carries the final palette
- `docs/visual-identity.md` — new file (creates the `docs/` directory); palette + naming + mode strategy + typography + contrast targets
- `openspec/specs/design-tokens/spec.md` — multiple requirements modified (see deltas)
- No JS changes, no template changes, no build-pipeline changes
- No localStorage migration: stored `garden-theme` values continue to work (token *values* change, not token *names* or theme-selection logic)
