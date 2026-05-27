## Status

Design decisions recorded below.

## Context

The intro region was introduced by `refactor-homepage` (shipped 2026-05-20) as editorial framing above the post catalogue, on both the cross-language home `/` and the per-language homes `/<lang>/`. Pagination for both indexes is produced by the custom `i18n_grouping` plugin (`on_finalized`), which chunks the post groups / per-language articles into pages and renders `index.html` / `lang_index.html` once per page, passing `page_number` and `total_pages` to each render.

Both templates currently gate the intro behind `page_number is not defined or page_number == 1`:

- [index.html:15-20](../../../themes/garden/templates/index.html) — page 1 includes `_intro_inference_script.html`; pages 2+ render `<h1>Posts</h1>`.
- [lang_index.html:13-19](../../../themes/garden/templates/lang_index.html) — page 1 renders the per-language intro section; pages 2+ render `<h1>Posts (LANG)</h1>`.

The base i18n-rendering spec encodes this with the scenario *"Intro region renders only on the first page"*. So the templates are faithfully implementing the spec — this is a **spec change**, not a template bug. The page-scoping was never argued for in `design.md` or ADR-0011; it was a default that got written down.

The open question at proposal time was purely behavioural: what should pages 2+ show where the intro currently degrades to a bare heading?

## Options

### Option A — Intro behaviour on pages 2+

1. **Full intro on every page** — emit the entire intro region (prose + language switcher / inference script) on every paginated page, identical to page 1.
2. **Title-only continuity** — page 1 keeps the full intro; pages 2+ use the intro's *title* as the page heading but omit the prose and switcher.
3. **Leave as-is** — keep page-1-only; treat the bare `<h1>Posts</h1>` fallback as the only thing to soften.

**Decision:** Option 1 (full intro on every page). Chosen by the user during proposal, with the trade-off stated explicitly: the intro prose and its inline `<script>` repeat on every page and push the catalogue down on deep pages. Accepted in exchange for consistent editorial identity across the whole catalogue and the simplest possible template change (delete a branch rather than add a condensed-render path).

### Option B — Documentation route

1. **Full `garden:propose` workflow** — change folder with proposal / design / tasks and a draft i18n-rendering spec delta, merged on finalise.
2. **Lightweight inline fix** — edit the spec scenario + templates directly in one commit.

**Decision:** Option 1 (full workflow). Chosen by the user. Because the behaviour lives in a written spec scenario, an inline template edit would silently contradict the spec; routing through the workflow keeps spec and deployed reality in sync (the WORKFLOW.md draft-spec-then-merge discipline).

## Decisions

### Decision 1: Render the full intro region on every paginated page

Remove the `page_number` gate from both templates. After the change:

- **`index.html`** unconditionally `{% include "_intro_inference_script.html" %}` (which itself no-ops when `INTRO_ALL` is empty) followed by the existing `{%- if not INTRO_ALL %}<h1>Posts</h1>{% endif %}` empty-state fallback. The `{%- else -%}<h1>Posts</h1>` branch is deleted.
- **`lang_index.html`** intro condition becomes `{% if INTRO_LANG is defined and INTRO_LANG.get(page_lang) %}`, dropping the `page_number` clause. The `{% else %}<h1>Posts (LANG)</h1>` empty-state branch is retained for the no-intro-file case.

The repeated inline inference `<script>` on the cross-language home is idempotent per page (it queries that page's own DOM), so repetition is functionally harmless.

### Decision 2: No prototype

WORKFLOW 1.3a calls for an HTML prototype on visual changes. This change introduces **no new visual design** — it re-emits the already-approved `.intro` component (designed, audited, and shipped by `refactor-homepage`) on additional pages. There is nothing to iterate on. Visual confirmation happens via `make devbuild` plus deploy validation, which is sufficient for a placement-only change. (Per the project's render-visual-candidates practice, prototypes are for *deciding* new visuals; here the visual is settled.)

### Decision 3: No ADR

ADR-0011 covers the intro content type and its language-resolution chain — neither of which changes. Page-scoping the intro was not an ADR-level decision when it was introduced, and un-scoping it is a presentational refinement, not an architectural one. No ADR is created or superseded.

### Decision 4: Pagination spec drift corrected in the same delta (folded in)

The adjacent *"The home post list is paginated"* requirement was factually wrong about the deployed mechanism (claimed Pelican's built-in paginator + `DEFAULT_PAGINATION` + default `PAGINATION_PATTERNS`; reality is the `i18n_grouping` plugin + `HOMEPAGE_PAGINATION` + manual `/page/N/` writes). At the approval gate the user chose to **fold the correction into this change** rather than spin up a separate one, so the whole section is accurate in one pass.

The correction is **documentation-only**: it rewrites the requirement prose and adjusts the `DEFAULT_PAGINATION` → `HOMEPAGE_PAGINATION` references and the "Pelican's pattern" wording across the requirement's scenarios. No pagination code changes — the spec is being realigned to what already ships (the drift dates from `refactor-homepage`, whose own design.md predicted the plugin would have to handle pagination). It rides in this change because it lives in the same requirement block we are already editing for the intro scenario.

## Risks / Trade-offs

- **Repeated prose on deep pages.** The full intro re-appears above the catalogue on every page, pushing posts further down the more pages there are. This is the accepted trade-off of Option 1; if it ever reads poorly in-browser, the title-only continuity (Option A.2) remains a cheap follow-up.
- **Repeated inline script.** The cross-language inference `<script>` is emitted on every page. It is < 50 lines, loads nothing external, and operates only on its own page's DOM, so the cost is page weight only — acceptable per ADR-0007.
- **Two concerns in one change.** Folding the pagination-spec correction in means this change touches both the intro scenario and the pagination requirement under one name. Low risk: the pagination part is doc-only (it lives entirely in the spec delta and changes no code), so the only implementation work remains the intro template edit. The two are easy to tell apart in review.
