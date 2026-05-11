## 1. Build the contrast audit tool

- [x] 1.1 Create `tools/contrast_audit.py`: pure-stdlib Python script that defines the in-use pair list (per Decision 3 / WCAG requirement), computes WCAG relative-luminance contrast ratios, and prints a results table covering both light and dark modes with pass/fail per pair
- [x] 1.2 Run `python tools/contrast_audit.py` against the **current** token values (pre-change) and capture the baseline output so post-change drift is auditable
- [x] 1.3 Confirm the script runs in under 1s with no third-party dependencies (stdlib only — no `colorsys` workarounds needed beyond `math.pow`)

## 2. Apply the chosen off-white values

- [x] 2.1 Update light `--bg` from `#FAF7F2` to `#E7DED4` in every occurrence in `themes/garden/static/css/styles.css`
- [x] 2.2 Update light `--bg-subtle` from `#F0EAE0` to `#DCCEBD` in every occurrence
- [x] 2.3 Update dark `--text` from `#F0EAE0` to `#DCCEBD` in every occurrence
- [x] 2.4 Update dark `--text-heading` from `#F0EAE0` to `#DCCEBD` in every occurrence
- [x] 2.5 Run `python tools/contrast_audit.py` and capture the results; identify any failing pairs

## 3. Resolve audit failures (apply Decision 4)

- [x] 3.1 For each failing pair, attempt a foreground adjustment first (`--text-muted`, `--accent`, `--admonition-*` colour) within the same hue family; re-run the audit after each adjustment
- [x] 3.2 If a foreground adjustment cannot resolve the failure without breaking another pair or pushing the colour off-spec, revise `--bg` or `--bg-subtle` toward the next-lighter candidate from `tools/colour-candidates.html` (light `--bg`: η L=88% → γ'' L=90% → γ' L=92%; light `--bg-subtle`: E L=82% → D L=83% → C+ L=84%); re-run the audit
- [x] 3.3 Update `openspec/changes/refactor-colour-scheme/specs/design-tokens/spec.md` to reflect any final hex changes from steps 3.1/3.2 (the spec must match the values that land in CSS)
- [x] 3.4 Repeat until the audit reports zero failing pairs in both modes; commit the final audit output as part of the change record

## 4. Dedupe the token blocks

- [x] 4.1 Collapse the two light blocks (`:root` and `:root[data-theme="light"]`) into a single grouped-selector block: `:root, :root[data-theme="light"] { ... }`. Each light token name appears exactly once after this step.
- [x] 4.2 Verify the dark side remains as two blocks (the `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` branch and the explicit `:root[data-theme="dark"]` override) — per Decision 5, dark cannot be fully deduped in plain CSS
- [x] 4.3 Confirm no `@media (prefers-color-scheme: light)` block remains anywhere in the stylesheet
- [ ] 4.4 Toggle-test the rendered output in a browser: no preference → OS light → OS dark → `data-theme="light"` → `data-theme="dark"` → back to no preference. In each state, sample the computed `--bg`, `--bg-subtle`, `--text`, and `--text-heading` values against expected.

## 5. Author docs/visual-identity.md

- [ ] 5.1 Create `docs/` directory (does not yet exist) and add `docs/visual-identity.md`
- [ ] 5.2 Section: **Palette** — table of token name, hex, role, with light and dark values side-by-side. Use inline `<span>` swatches; if rendering is unreliable, fall back to hex-only (Open Question — decide in apply)
- [ ] 5.3 Section: **Token naming conventions** — what each token name means, and the rule for when to add a new token versus extend an existing one
- [ ] 5.4 Section: **Mode strategy** — how the three states resolve (default light, OS-driven dark, explicit `data-theme` override); reference the archived `default-light-mode` change for full rationale
- [ ] 5.5 Section: **Typography tokens** — list `--font-title`, `--font-body`, `--body-size`; rationale for Fraunces and IBM Plex Sans; opsz/weight conventions
- [ ] 5.6 Section: **Contrast targets and audit results** — state WCAG AA threshold (4.5:1 body, 3:1 large/non-text); paste the final audit table from `tools/contrast_audit.py`; show the script invocation so the reader can refresh it; note `--accent-display` exemption

## 6. Update the design-tokens base spec

- [ ] 6.1 Run `openspec validate refactor-colour-scheme` and resolve any structural warnings
- [ ] 6.2 Confirm the delta spec at `openspec/changes/refactor-colour-scheme/specs/design-tokens/spec.md` reflects the as-shipped hex values (any adjustments from §3 must be mirrored here before archive)

## 7. Verification and cleanup

- [ ] 7.1 Run `make devbuild` (or the equivalent Pelican build) and confirm the build succeeds with no CSS warnings
- [ ] 7.2 Visually verify on a published page: landing, an article with an admonition of each variant (note/tip/warning/danger), a tag-chip hover state, a list page. Compare light and dark side-by-side.
- [ ] 7.3 Decide whether to retain `tools/colour-candidates.html` post-archive (Open Question in design.md). Default: remove on archive since the chosen values now live in `styles.css` and `docs/visual-identity.md`.
- [ ] 7.4 Final sanity check: `git grep -n "#F0EAE0\|#FAF7F2"` returns zero hits inside `themes/`, `docs/`, and `openspec/specs/` (matches in `openspec/changes/archive/` are expected and fine)
