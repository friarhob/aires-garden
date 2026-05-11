## Context

The site's colour palette has been stable since `add-design-tokens` (2026-05-07) and was inverted to light-default by `default-light-mode` (2026-05-10). Across that period one off-white value, `#F0EAE0`, has done triple duty: it is the light-mode `--bg-subtle`, the dark-mode `--text`, and the dark-mode `--text-heading`. The light-mode `--bg` (`#FAF7F2`) is the other near-white in the palette. Both have been flagged as too bright in their respective roles.

Two related issues have accumulated alongside:

1. The `design-tokens` spec specifies `--accent` contrast against `--bg` but says nothing about other functional pairs. Whether `--text-muted` on `--bg-subtle` clears WCAG AA, for instance, has never been verified.
2. After `default-light-mode`, the token map lives in four CSS blocks: `:root`, an `@media (prefers-color-scheme: dark)` block guarded by `:not([data-theme="light"])`, an explicit `:root[data-theme="light"]` override, and an explicit `:root[data-theme="dark"]` override. The light pair is exactly identical; the dark pair is identical bar selector. Every token edit therefore touches four declarations — this change will touch many.

This change settles all three at once: replace the offending values with calmer ones (with the choice constrained by an audit, not pure eyeballing), audit and fix every functional pair, dedupe the blocks, and write the result down in `docs/visual-identity.md` so the next colour discussion starts from a documented baseline.

The change is medium-sized but contained: only `themes/garden/static/css/styles.css` and `openspec/specs/design-tokens/spec.md` are modified; `tools/contrast_audit.py` and `docs/visual-identity.md` are net-new.

## Goals / Non-Goals

**Goals:**

- Replace `#F0EAE0` (light `--bg-subtle`, dark `--text`, dark `--text-heading`) with a single calmer off-white — lower lightness, lower saturation, same warm hue family.
- Replace light `--bg` (`#FAF7F2`) with a less bright, less saturated alternative; preserve at least 6 lightness points of separation from the new `--bg-subtle`.
- Verify every in-use colour pair against WCAG AA in both modes; adjust failing tokens until all pass.
- Make the audit reproducible (script in `tools/`).
- Reduce token-block duplication so each token value is declared once per mode.
- Document the resulting palette, naming conventions, mode strategy, typography tokens, and audit results.
- Correct the stale `@media prefers-color-scheme: light` reference in the admonition requirement.

**Non-Goals:**

- No new capability or behaviour: theme toggle, language switching, `data-theme` overrides, persistence — all unchanged.
- No re-evaluation of the deep-purple/gold accent pair. The aesthetic direction is settled; only the off-whites are in question.
- No tightening to WCAG AAA. AA is the line; AAA can be a future change.
- No spacing, radii, or breakpoint tokens introduced. The palette and typography are tokenised; layout primitives are not, and inventing them is out of scope.
- No CSS preprocessor, no build-time token transformation. Plain CSS only.
- No CI gate on the contrast script. Running it manually during apply is enough for this change; automating it can be a follow-up.

## Decisions

### Decision 1: One canonical off-white, used in all three sites

Replace `#F0EAE0` with a single new value used as light `--bg-subtle`, dark `--text`, and dark `--text-heading`.

**Why one value, not three?** The three roles never sit adjacent on the page — light-mode subtle backgrounds and dark-mode text are mutually exclusive surfaces. A single value preserves palette coherence, simplifies the audit, and matches how the palette has read since `add-design-tokens`.

**Alternative considered:** Split into a "warm cream" for light backgrounds and a separate "soft cream" for dark text, tuned independently. Rejected because the divergence buys nothing the eye will notice, doubles the documentation burden, and is harder to reason about during apply-time iteration.

### Decision 2: Chosen hex values (selected via rendered candidate review)

The proposal initially planned to pin candidate sets and pick during apply. In practice, candidate review happened during the propose phase: a preview file (`tools/colour-candidates.html`) rendered three rounds of candidates against the existing palette, with the chosen pair locked before specs were written.

**Chosen values:**

| Token | New value | HSL | Was |
| --- | --- | --- | --- |
| Light `--bg` | `#E7DED4` (θ) | 32° / 28% / 87% | `#FAF7F2` (36° / 33% / 97%) |
| Light `--bg-subtle` | `#DCCEBD` (F) | 33° / 31% / 80% | `#F0EAE0` (36° / 36% / 91%) |
| Dark `--text` | `#DCCEBD` (F) | 33° / 31% / 80% | `#F0EAE0` |
| Dark `--text-heading` | `#DCCEBD` (F) | 33° / 31% / 80% | `#F0EAE0` |

Pairing: light `--bg` (L=87) − light `--bg-subtle` (L=80) = 7 points, clearing the ≥6 separation rule.

**Character of the choice.** Both values came in noticeably calmer than the proposal's initial direction. The original draft targeted off-white at L=85-88% and bg at L=92-94%. The picked pair sits at L=80% and L=87% — a stronger commitment to a sepia-leaning warm light mode rather than a "near-white with slight warmth" reading. Saturation also stayed in the 28-31% band rather than dropping to ~16-20%, preserving cream character despite the lower lightness.

**Why this exact pair?** Three rounds of preview iteration:

1. *Round 1* (sections §1-§4 of the preview file) — six off-white candidates and six bg candidates spanning two saturation appetites. C' was identified as the closest direction for off-white but still too bright; γ' was selected for `--bg`.
2. *Round 2* (§3.5-§3.6) — four further off-white candidates extending C' downward in lightness while preserving warmth. F (L=80%) was chosen.
3. *Round 3* (§3.7) — three further `--bg` candidates extending γ' downward. θ (L=87%) was chosen, settling at the structural floor (gap = 7).

**Apply-time contingency.** WCAG audit (Decision 4) may surface failing pairs against these darker backgrounds. If a foreground token cannot be adjusted to clear a failing pair (Decision 4), the `--bg` or `--bg-subtle` value is revised toward the next-lighter candidate from the preview file (η at L=88%, γ'' at L=90%, or γ' at L=92% for `--bg`; E at L=82%, D at L=83%, or C+ at L=84% for `--bg-subtle`). The preview file remains in `tools/` until archive, so the fallback set is concretely available rather than re-derived.

**Alternative considered:** Pin candidate sets in the proposal and defer the pick to apply. Rejected after the user requested "discuss the colours first" — committing without rendered review proved unreliable on the first attempt. The preview iteration grounded the decision; the docs reflect the result.

### Decision 3: WCAG audit covers in-use pairs only, via a Python script

A new `tools/contrast_audit.py` enumerates every colour pair that actually appears on the rendered page (not theoretical pairs from the Cartesian product), computes the WCAG relative-luminance contrast ratio, and prints a results table for both modes.

In-scope pairs (each evaluated in both light and dark modes where both sides exist):

- `text` / `bg`
- `text-muted` / `bg`
- `text` / `bg-subtle` (admonition body text)
- `text-muted` / `bg-subtle` (figcaptions inside admonitions, if any — included for safety)
- `text-heading` / `bg`
- `accent` / `bg` (links, hover states, tag-chip text)
- `accent` / `bg-subtle` (links inside admonitions)
- `bg` / `accent` (tag-chip hover: text colour is `bg` on `accent` background)
- `admonition-note` / `bg-subtle` (title text and left border)
- `admonition-tip` / `bg-subtle`
- `admonition-warning` / `bg-subtle`
- `admonition-danger` / `bg-subtle`

Threshold: **4.5:1 for normal-weight text**, **3:1 for large text and non-text contrast** (heading-sized text, decorative borders that carry meaning).

**Why a script, not a hand-computed table?** Reproducibility. After tweaking a token to fix one failing pair, we need to re-run the entire audit to confirm nothing else regressed. Doing that by hand is tedious and error-prone. The script is ~50 lines, no dependencies beyond the standard library, and lives in `tools/` alongside `design-prototype.html`.

**Alternative considered:** Use an online tool (WebAIM contrast checker) and capture results manually. Rejected because (a) it isn't reproducible and (b) the audit table in `docs/visual-identity.md` becomes a static snapshot that drifts on the next colour change.

### Decision 4: Adjust only failing tokens; favour adjusting `--text-muted` and `--accent` over `--bg-subtle`

If the audit surfaces failing pairs, adjust the **foreground** token (text, accent, admonition) rather than the background, on the theory that backgrounds are the heaviest visual presence and changing one shifts the whole page mood while changing a foreground only shifts that role's appearance.

Likely failing pairs (light mode, on the new `bg-subtle`):

- `text-muted` (`#7B54A0`) on `bg-subtle` — currently ~5.0:1 against `#F0EAE0`; against a darker `bg-subtle` this *improves*, but verify
- `accent` (`#8B6209`) on `bg-subtle` — same dynamics, same expectation
- `admonition-warning` (`#8B6209`) on `bg-subtle` — same
- All admonition-* colours as title text on `bg-subtle` — verify

**Why this rule?** The change exists to calm the off-whites. Re-adjusting them to compensate for foreground contrast issues partly defeats the purpose. Only fall back to background tweaks if a foreground tweak would itself fail (e.g., would push a saturated colour off-spec).

**Alternative considered:** No fixed rule — adjust whichever side moves least. Rejected because "moves least" is hard to measure and produces inconsistent decisions across pairs.

### Decision 5: Dedupe via grouped selectors, no preprocessor

Collapse the four token blocks into two blocks total:

```css
:root,
:root[data-theme="light"] {
    /* light tokens — declared once */
}

@media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
        /* dark tokens — declared once */
    }
}

:root[data-theme="dark"] {
    /* dark tokens — declared again, by necessity */
}
```

The dark side cannot be fully deduped to one block because the two selectors that need the dark tokens (`@media`-gated and explicit-override) have different specificity and apply under different conditions. Combining them via a comma-separated selector list would force the explicit override into the `@media` block, which fails when `prefers-color-scheme` is light.

**Why not a preprocessor (Sass, PostCSS)?** No build step exists; introducing one for a token-deduplication is disproportionate. The grouped-selector form is plain CSS, reads clearly, and reduces four blocks to three (one light, two dark). That is the maximum dedupe achievable in plain CSS.

**Alternative considered:** Use CSS `@property` registrations or custom-property aliasing (`--off-white: #...; --bg-subtle: var(--off-white);`). The aliasing pattern has merit — a single named "off-white" referenced from three sites is more semantic than three identical literals — but it's a separate idea worth its own change. Pulling it into this one expands scope.

### Decision 6: visual-identity.md scope = colour + typography + mode strategy

The new `docs/visual-identity.md` covers:

1. **Palette** — table of token name, hex, role, with the light and dark values side-by-side.
2. **Token naming conventions** — what `--bg`, `--bg-subtle`, `--text`, `--text-heading`, `--text-muted`, `--accent`, `--accent-display`, `--border`, `--admonition-*` each mean and when to add a new token vs. extend an existing one.
3. **Mode strategy** — how the three states resolve (default light, OS-driven dark, explicit `data-theme` override) and why default-light-mode (the change) chose this structure.
4. **Typography tokens** — `--font-title`, `--font-body`, `--body-size`, the rationale for Fraunces and IBM Plex Sans, and the `opsz`/weight conventions.
5. **Contrast targets and audit results** — WCAG AA threshold statement plus the audit table (light and dark, all pairs, ratios, pass/fail).

Excluded: spacing, radii, breakpoints (none are tokenised today; documenting them would invent scope), accent-display rationale beyond "decorative, exempt from contrast".

**Alternative considered:** Smaller doc — colour only, no typography. Rejected because typography tokens are co-resident in the same `:root` block and any reader pulling up "the design tokens doc" expects to see them. Typography is one short section, not the bulk of the doc.

**Alternative considered:** Larger doc — include the change history and ADR-style decision log. Rejected because that's what `openspec/changes/archive/` is for. The doc references the relevant archived changes by name; it doesn't reproduce their content.

### Decision 7: Bundle the spec staleness fix into the dedupe wording

The "Admonition semantic tokens defined" requirement currently states tokens must be defined in `:root`, `@media prefers-color-scheme: light`, `:root[data-theme="light"]`, and `:root[data-theme="dark"]`. The first three are wrong post-`default-light-mode`. Rather than apply the fix as a standalone tweak, fold it into the dedupe wording: the requirement now states tokens must be defined in the **two** post-dedupe blocks (the grouped light selector and the dark side, where dark covers both the media-query branch and the explicit override).

**Why bundled?** The dedupe changes the block structure; the staleness is corrected as a side effect of stating the new structure. A standalone fix would describe a structure that's about to change.

## Risks / Trade-offs

- **Risk: Candidate hex set looks wrong against rendered output** → Mitigation: apply-time iteration. The candidate sets are starting points, not commitments. If all three off-white candidates feel wrong on screen, the apply step generates new candidates within the same HSL bounds (35°ish hue, 15–22% saturation, 85–88% lightness) and re-evaluates.

- **Risk: WCAG fixes ripple — adjusting one token to pass one pair fails another** → Mitigation: the audit script re-runs after every adjustment; iterate until all pairs pass. The script is fast (subsecond) so iteration is cheap.

- **Risk: Dedupe specificity bug** — `:root[data-theme="light"]` has higher specificity than bare `:root`, so when both selectors share the same declaration block via comma, the *whole block* applies at the higher specificity. This shouldn't matter because no other rule competes, but worth verifying via browser toggle-test in both modes.
  → Mitigation: explicit toggle-test step in `tasks.md` (light → dark → light → explicit-light → explicit-dark → no preference), comparing rendered colours against expected token values.

- **Risk: Doc rot — `docs/visual-identity.md` drifts from actual tokens** → Mitigation: include the audit script invocation at the top of the contrast-results section so the reader knows how to refresh it. The palette table is short enough that re-syncing is mechanical (15 rows). Future colour changes update the doc as part of their tasks (already an OpenSpec habit).

- **Trade-off: Dark side stays partially duplicated** — true single-source dark tokens would require either CSS aliasing or a preprocessor. Both expand scope. Accepting two declarations on the dark side is the price of plain CSS.

- **Trade-off: Audit covers in-use pairs only** — adding a future component that introduces a new pair (e.g. `text-muted` on `accent`) means the audit doesn't cover it. This is correct: contrast obligations attach to *what's rendered*, not to the Cartesian product. Future components run their own audit row when introduced.

## Migration Plan

- Single PR covering all changes. Pelican rebuilds CSS on next `make publish`; deployed via existing GitHub Actions pipeline.
- No data migration. Stored `garden-theme` localStorage values continue to work — only token *values* change, not token names or theme-selection logic.
- Rollback: revert the PR. The token values are isolated to one CSS file and one spec file; revert is clean.

## Open Questions

- **WCAG audit may demand foreground or background revisions.** With `--bg` at L=87% and `--bg-subtle` at L=80%, foreground tokens (`--text-muted`, `--accent`, `--admonition-warning`) sit on much darker surfaces than before. Their existing values (`#7B54A0`, `#8B6209`) cleared AA against the old `#FAF7F2`/`#F0EAE0` only by 0.5-1 points — there is no headroom for the new backgrounds. The audit will likely surface failing pairs; Decision 4 governs the response (foreground first, then bg fallback per Decision 2).
- **Should `docs/visual-identity.md` include rendered colour swatches (HTML/SVG) or just hex codes?** Markdown rendering of colour swatches is GitHub-flavoured and won't reproduce in every viewer. Decision deferred to apply: try a simple inline `<span style="background: #...">` approach; if it doesn't render well, fall back to a hex-only table.
- **Should the contrast audit be wired into CI?** Out of scope for this change. Plausible follow-up if colour churn becomes a recurring source of regressions.
- **Should the `accent-display` token earn a more specific name like `--accent-decorative`?** Not in scope here — renaming a token cascades across consumers and deserves its own change. Worth noting in the doc that this token is intentionally exempt from contrast obligations.
- **Should `tools/colour-candidates.html` be retained after archive?** It documents the decision process but isn't a tool the maintained code depends on. Default: keep until archive, then remove (the chosen values live in `styles.css` and `docs/visual-identity.md`; the candidates that were rejected don't earn ongoing space). Apply-time decision.
