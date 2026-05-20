## Status

Design decisions recorded below.

## Context

The current homepage has two structural problems and one editorial gap:

- **Structural — no scope variation.** `index.html` (cross-language `/`) and `lang_index.html` (per-language `/<lang>/`) render essentially the same `<ul>` of `<li>` entries. The only difference is the visible scope of the list. There is no presentational distinction between "the whole garden" and "everything in EN".
- **Structural — no pagination.** Both templates iterate every article without a paginator. As the garden grows past ~30 posts the page becomes a wall of links.
- **Editorial — no framing.** A first-time reader landing on `/` sees only a heading and links. There is no place for the author to say what the garden is for, what kinds of work live here, or how to navigate to a single language.

The roadmap entry pre-declares the broad shape: introduce an `intro` content kind, mirror tag-prose conventions, redesign the post list, add pagination. The open design space at proposal time was:

- **Where intro prose is stored** — fourth content type vs. tag-prose subtype vs. page-with-marker vs. hardcode.
- **Post list visual treatment** — list rows vs. table vs. cards vs. CSS-grid catalogue.
- **Pagination mechanism** — Pelican-native static pages vs. load-more vs. infinite scroll vs. none.
- **Language fallback** when the chosen reader-language has no intro file.

## Options

### Option A — Intro storage

1. **Fourth content type** (`content/intro/<scope>.<lang>.md`) — dedicated schema, dedicated scanner, borrows the `<scope>.<lang>.md` convention from tag-prose as a shared convention.
2. **Tag-prose subtype with sentinel slug** (`content/tag-prose/home/<scope>.<lang>.md`) — reuses tag-prose schema. Requires `tag_pages` filter and consumes the `home` slug from the tag namespace.
3. **Page with marker** (`Page_kind: intro` discriminator) — reuses page tree.
4. **Hardcode in templates** — inline prose into `index.html` / `lang_index.html`.
5. **Single-language intro** — only render the default-language intro on `/`.

Decision recorded in [ADR-0011](../../decisions/0011-intro-content-type.md): **Option 1**. The shared-convention/separate-schema split is the load-bearing choice — it captures tag-prose's filename symmetry without inheriting its schema, slug regex, or `tag_pages` coupling.

### Option B — Post list visual treatment

1. **List with aligned columns** — single-row entries, date and lang badges right-aligned via CSS grid.
2. **Proper `<table>`** — title / date / langs columns; archival, directory-like feel.
3. **Stacked cards** — full-width cards, one per row, magazine-y.
4. **CSS-grid catalogue of cards** — cards arranged in a responsive grid (1 / 2 / 3 columns by viewport), each card with title clamp, dashed-rule meta footer with date and language chips.

**Decision:** Option 4 (CSS-grid catalogue). User direction: "a catalogue of sorts — like cards in a dynamic table defined by CSS." The grid form fits that brief best because it preserves card identity (each post is a distinct visual unit) while imposing tabular alignment via `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))`. The 3-line title clamp keeps cards uniform-height in a row without truncating most real titles.

Prototype: [tools/prototype-homepage-catalogue.html](../../../tools/prototype-homepage-catalogue.html) — covers both scopes, both themes (light/dark), and Pelican-default pagination.

### Option C — Pagination

1. **Pelican-native** — static `/`, `/page/2/`, …. No JS. Built into Pelican via `DEFAULT_PAGINATION`.
2. **Load more** — small JS appends pre-rendered pages.
3. **Infinite scroll** — JS observer auto-loads.
4. **No pagination** — render everything; defer.

**Decision:** Option 1 (Pelican-native). Lowest cost, no JS, aligns with ADR-0007 ("small client-side JS is acceptable *where the static-host constraint requires it*" — pagination does not require it). The prototype includes the Pelican-default pagination markup; reviewers can validate it before implementation.

This decision is intentionally **not promoted to an ADR**. If implementation reveals a deviation (e.g., Pelican's `PAGINATION_PATTERNS` for per-language indexes proves awkward), revisit then. The pagination-strategy ADR question can be reopened during implementation if needed.

### Option D — Language fallback for the cross-language `/` intro

Mirrors the multilingual 404 inference (i18n-rendering spec), with stage 1 dropped because `/` has no `/<lang>/` prefix:

1. Stored language preference (`document.documentElement.dataset.prefLang`).
2. `navigator.language`'s 2-letter prefix.
3. Default-lang fallback (`data-default-lang` attribute).
4. **Terminal fallback** — alphabetically-first emitted `<section data-lang>` block.

Stages 1–3 require the chosen language to have an `all.<lang>.md` file (i.e. an emitted section). Stage 4 guarantees at least one section is visible whenever any file exists. If no `all.<lang>.md` exists at all, the intro region is omitted entirely from `/`.

For per-language root `/<lang>/`, the intro body is read from `content/intro/lang.<lang>.md` if that file exists. There is no cross-language fallback — showing a different language on a single-language page is worse than no intro. If the file does not exist, the intro region is omitted from `/<lang>/`.

Recorded in ADR-0011's Decision section so the policy lives next to the storage decision.

### Option E — Coordination with `add-l10n-rendering`

1. **refactor-homepage first** (current ordering). EN labels ship now; `add-l10n-rendering` later localises them.
2. **`add-l10n-rendering` first** (roadmap order). Localisation lands first; refactor-homepage authors all strings through the l10n layer.
3. **Parallel.** Two changes in flight.

**Decision:** Option 1. The refactor introduces one new label (`Recent posts` above the catalogue) and at most one or two more in pagination chrome (`Page 1 of N` if Pelican's default text is used). `add-l10n-rendering` will sweep these up; the cost of postponing l10n is one PR worth of label translation, not a structural rework. Order chosen by user during proposal.

## Decisions

### Decision 1: Intro storage and language resolution

See ADR-0011. The change adds `content/intro/` as a fourth content type with the same `<scope>.<lang>.md` filename convention used by tag-prose, kept as a *shared convention* rather than *shared schema*. The cross-language `/` intro uses an inline-JS inference chain mirroring the multilingual 404; the per-language `/<lang>/` intro is single-body with no cross-language fallback.

### Decision 2: CSS-grid catalogue with `repeat(auto-fill, minmax(280px, 1fr))`

Cards reflow from 1 column (≤~600px viewport) to 2 columns (~600–900px) to 3+ columns (wider) without explicit breakpoints. Each card uses `grid-template-rows: auto 1fr auto` so the meta row (date + lang chips) stays pinned to the bottom regardless of title length. Title clamp at 3 lines with `-webkit-line-clamp` keeps cards in a row uniform-height.

Card hover: `border-color: var(--accent)`, `transform: translateY(-1px)`. Reuses existing design tokens; no new tokens introduced. Contrast audit (`tools/contrast_audit.py`) does not need updating — every text/background pair on the catalogue uses tokens already in the audit.

### Decision 3: Pelican-native pagination

`DEFAULT_PAGINATION = 12` (a reasonable first-page card count: 4 rows × 3 columns at the widest viewport, or 6 rows × 2 columns). The number is tweakable during implementation as the prototype's grid behaviour is verified on real content.

The default `PAGINATION_PATTERNS` in Pelican is fine for `/` (`/`, `/page/2/`, …). The per-language home `/<lang>/` is produced by the existing `i18n_grouping` plugin, which currently does not paginate. Implementation will need to either (a) extend the plugin to emit `<lang>/page/2/` pages, or (b) switch to Pelican's per-template pagination if the plugin's article objects can be passed through Pelican's paginator. To be resolved in the implementation phase; if the deviation is large, promote to an ADR.

### Decision 4: Intro region rendering

On `/`: a `<section class="intro">` wrapper contains one `<section class="intro-body" data-lang="<lang>">` block per emitted `all.<lang>.md`. An inline `<script>` (≤ 50 lines, no external resources, per ADR-0007 bar 3) implements stages 1–4 of the inference. With JS disabled, every block stays visible (graceful degradation per ADR-0007 bar 2).

On `/<lang>/`: a `<section class="intro">` wrapper contains a single block, no inference script needed. The whole region is omitted at render time if the file is absent.

The intro is placed **between the per-page lang-links bar and the catalogue heading**, mirroring the prototype.

### Decision 5: `header_lang_links` continues unchanged

The existing i18n-rendering requirement *"`index.html` publishes per-language home links for every `SITE_LANGS` entry"* and the equivalent for `lang_index.html` are preserved. The header lang picker continues to drive navigation between scopes; the intro section's section-toggle behaviour is a separate surface (inline-JS that toggles `<section data-lang>` visibility within the intro), and does not interact with `localStorage["garden-lang"]` writes done by the header.

This separation matches how the multilingual 404 currently operates: the header picker writes the preference and may navigate; the 404's inline script reads the preference to choose a section. Same separation applies here.

### Decision 6: Seed content scope (EN + PT)

The roadmap notes: "Spanish and French intro files can be authored once this change lands." Implementation seeds 4 files: `all.en.md`, `all.pt.md`, `lang.en.md`, `lang.pt.md`. ES and FR seeding is a follow-up that can ship as a small content-only commit; refactor-homepage is not blocked on them.

Deploy-validation gate runs with the EN+PT seed in place. The fallback behaviour (no `all.es.md` exists → ES is not an option in the section-toggle picker → reader who has stored ES preference falls through to navigator.language → EN or PT) is itself a verifiable scenario.

## Risks / Trade-offs

- **`i18n_grouping` plugin pagination.** Per-language indexes (`/<lang>/`) are produced by the plugin, not by Pelican's built-in paginator. The plugin currently emits one page per language with all articles inline. Adding pagination there is non-trivial; the implementation tasks call this out explicitly and reserve the right to promote pagination strategy to an ADR if a deviation from Pelican-native is forced.
- **CSS-grid `repeat(auto-fill, minmax(280px, 1fr))` viewport behaviour.** On a 901px viewport, the grid jumps from 2 to 3 columns abruptly; cards become narrow. The 280px floor is a starting value; tunable during implementation against real content.
- **3-line title clamp truncation.** Real titles vary in length; one current post ("Produtor é preso por uso privilegiado de informações transtemporais") is right at the clamp boundary. Acceptable trade-off for uniform card height; if it ever truncates substantively, raise the clamp to 4 lines.
- **No per-language URL pattern decision for pagination yet.** `/page/2/` works for `/`; `/<lang>/page/2/` is the expected URL for per-language pagination but requires Pelican config or plugin coordination. Resolved in implementation.
- **Intro inference script duplicates the 404 script structurally.** Two separate inline scripts with the same stages 2–4. Acceptable: each script is < 50 lines and they're slightly different (no stage 1 on the homepage). If a third surface emerges, factor out.
- **Authoring friction for the section-toggle picker on `/`.** Readers who land on `/` and want to read the intro in a language other than the inferred one must use the header lang picker to toggle sections. This is exactly the multilingual 404's pattern, so the friction is already established and known.

## Open questions deferred to implementation

- The exact `DEFAULT_PAGINATION` value (start at 12, tune against content).
- Whether per-language home pagination is solved inside `i18n_grouping` or by switching templates to Pelican's paginator.
- Whether the `Recent posts` H2 above the catalogue stays or is removed once the visual rhythm is verified in-browser.
- Whether the dashed-rule separator in the card meta row reads well in dark mode at small sizes — visual call.
