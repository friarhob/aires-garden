## Why

The homepage intro (the editorial framing above the post catalogue) currently appears **only on the first page** of the paginated home indexes. On `/page/2/` and beyond — and on `/<lang>/page/2/` and beyond — the intro region is dropped and the page falls back to a bare `<h1>Posts</h1>`. The garden loses its editorial identity the moment a reader pages deeper.

This was never a reasoned design decision: neither the `refactor-homepage` `design.md` nor [ADR-0011](../../decisions/0011-intro-content-type.md) discusses page-scoping the intro. The behaviour entered as a quiet template default and was codified verbatim in one i18n-rendering scenario. There is no ADR to supersede.

The chosen fix is to render the **full intro region on every paginated page**, identical to page 1 — accepting that the intro repeats and pushes posts down on deep pages, in exchange for a consistent identity across the whole catalogue.

## What Changes

- **`index.html`** — remove the `page_number == 1` gate so the cross-language intro region (`_intro_inference_script.html` include + the `<h1>Posts</h1>` empty-state fallback) renders on every page, not just the first.
- **`lang_index.html`** — remove the `page_number == 1` clause from the per-language intro condition so the per-language intro renders on every page when `INTRO_LANG[page_lang]` exists.
- **Spec update (intro).** Draft spec in `openspec/changes/intro-on-all-pages/specs/i18n-rendering/`:
  - The scenario *"Intro region renders only on the first page"* is replaced by *"Intro region renders on every paginated page"*, under the existing cross-language intro requirement (which also governs the per-language home via its "same rule applies" clause).
- **Spec correction (pagination, documentation-only).** The same draft spec corrects the *"The home post list is paginated"* requirement so it matches deployed reality: pagination is done by the `i18n_grouping` plugin (not Pelican's built-in paginator), the page-size setting is `HOMEPAGE_PAGINATION` (not `DEFAULT_PAGINATION`), and `/page/N/` directories are written by the plugin (not via Pelican's `PAGINATION_PATTERNS`). No code changes — this only realigns the spec with what already ships.
- **No new content, no new styles, no CLI change.** The `.intro` component, its CSS, the inference script, and the intro content files are all unchanged — they are simply emitted on more pages.

## Capabilities

### Modified Capabilities

- **`i18n-rendering`** — the intro region is emitted on every paginated page of both the cross-language home `/` (with its `<section data-lang>` blocks + inline inference script) and each per-language home `/<lang>/` (single body), rather than only on the first page. Additionally, the pagination requirement is corrected to describe the actual `i18n_grouping`-plugin mechanism and `HOMEPAGE_PAGINATION` setting (documentation-only realignment, no behavioural change).

## Impact

- **`themes/garden/templates/index.html`** — one conditional block simplified (lines 15–20): drop the `page_number` branch.
- **`themes/garden/templates/lang_index.html`** — one condition simplified (line 13): drop the `page_number` clause.
- **No automated tests change.** Template output is not unit-tested; the page-1-only behaviour is asserted nowhere in the test suite. Verification is by build-output inspection (`make devbuild`) and deploy validation.
- **Docs** — `README.md` and `docs/visual-identity.md` describe intro *authoring* and *structure*, neither of which changes. No doc update required (the intro markup is identical; only its page coverage widens).
- **Deploy** — unchanged; build still runs `make build`.

## Out of scope

- **No behavioural change to pagination.** The pagination *mechanism* is untouched — the only pagination work here is correcting the spec text to match it (see "Spec correction" above). The intro fix and the pagination correction share one spec section but no code.
