## Why

The homepage today is a flat list of recent posts and nothing else. It opens with `<h1>Posts</h1>` and dives straight into the article list — there is no editorial framing, no way for a first-time reader to understand what the garden is for, and no scope variation between the cross-language root `/` and the per-language roots `/<lang>/`. The post list itself is a plain `<ul>` that reads top-to-bottom and offers no pagination, so as the garden grows it will turn into an unscannable scroll.

Two things, together, change that:

- **Editorial intro at the top of every root.** A short authored passage above the post list, sourced from a new `intro` content type. The cross-language root carries multilingual bodies (one `<section data-lang>` per available language, exactly like the multilingual 404); the per-language root carries a single body authored in the page's language.
- **A redesigned, paginated post catalogue.** The list becomes a CSS-grid "dynamic table" of cards — each card has the title (Fraunces, 3-line clamp), a dashed-rule meta row with date and language chips, hover-accent border — sitting on Pelican's built-in pagination. Prototype lives at `tools/prototype-homepage-catalogue.html`.

## What Changes

- **New `intro` content type.** Files live at `content/intro/<scope>.<lang>.md`, where `<scope> ∈ {all, lang}` and `<lang>` is an ISO 639-1 alpha-2 code matching the file's `Lang` frontmatter. Required frontmatter: `Title`, `Lang`, `Status: hidden`. Forbidden: `Slug`, `Translation_key`, `Tags`. The directory is flat (no per-slug subdirectory). Schema and filename contract are enforced by `frontmatter_lint` via a new `IntroFrontmatter` Pydantic model.
- **New ADR-0011.** Records the storage decision (fourth content type, shared `<scope>.<lang>.md` convention with tag-prose, not shared schema) and the language-resolution chain for the cross-language root's intro section.
- **`garden new --kind intro`.** Adds a new kind to the CLI: prompts for `scope` (`all`/`lang`) and `lang` interactively in TTY mode; accepts `--scope` and `--lang` flags in non-TTY mode. No slug step. Writes lint-passing frontmatter (`Title`, `Lang`, `Status: hidden`).
- **Homepage rendering — intro.** A new Pelican plugin (`intro_pages`, or merged into an existing plugin) discovers `content/intro/` at build time, makes the intro bodies available to `index.html` and `lang_index.html`. On `/`, every emitted intro is wrapped in a `<section data-lang="<lang>">` block; an inline JS picker (mirroring the 404 inference) chooses which to show. On `/<lang>/`, the single matching `lang.<lang>.md` body is rendered inline, or the intro region is omitted if no file exists.
- **Homepage rendering — catalogue.** Both `index.html` and `lang_index.html` replace the existing `<ul>` with a CSS-grid catalogue of cards. Markup changes: `<section class="catalogue">` → `<div class="catalogue-grid">` → `<a class="catalogue-card">` per entry. CSS lives in `styles.css` using existing design tokens.
- **Pagination.** Pelican's built-in pagination is enabled (`DEFAULT_PAGINATION`) for the cross-language and per-language indexes. A pagination nav block renders at the bottom of the catalogue. Static URLs (`/`, `/page/2/`, …); no JS.
- **Seed content.** EN and PT intro files are authored for both scopes (4 files total: `all.en.md`, `all.pt.md`, `lang.en.md`, `lang.pt.md`). ES and FR intros can be authored after the change lands per the roadmap dependency.
- **Spec updates.** Draft specs in `openspec/changes/refactor-homepage/specs/`:
  - `content-model/spec.md` — new requirements for the intro schema and filename contract; build-time validation extends to `content/intro/`.
  - `garden-cli/spec.md` — `--kind intro` requirements and scenarios.
  - `i18n-rendering/spec.md` — intro placement and language-resolution scenarios for `/` and `/<lang>/`; pagination requirement on the home indexes; `header_lang_links` semantics unchanged but its scenarios are re-verified.

## Capabilities

### Modified Capabilities

- **`content-model`** — new requirements for intro frontmatter schema, intro filename ↔ frontmatter contract, intro uniqueness per `(scope, lang)`, and build-time validation extending to `content/intro/`.
- **`garden-cli`** — `garden new --kind intro` flow with `--scope` flag; `kind ∈ {post, page, tag-prose, intro}`.
- **`i18n-rendering`** — intro rendering on `/` (multilingual via `<section data-lang>` + inline inference JS, alphabetic terminal fallback) and `/<lang>/` (single body, no cross-language fallback). Pagination on home indexes. Catalogue markup contract.

## Impact

- **No new runtime dependencies.** The intro plugin reuses the existing Pelican plugin pattern; pagination is built into Pelican.
- **Content tree** — new `content/intro/` directory with 4 seed files (EN + PT, both scopes). No existing content is modified.
- **`plugins/frontmatter_lint/`** — `schema.py` gains an `IntroFrontmatter` model; `__init__.py` (plugin) and `cli.py` add an intro discovery pass.
- **`themes/garden/templates/`** — `index.html` and `lang_index.html` are restructured to render the intro region above the catalogue grid; an `_intro_inference_script.html` partial is added for the `/` page.
- **`themes/garden/static/css/styles.css`** — new `.intro`, `.catalogue`, `.catalogue-grid`, `.catalogue-card`, `nav.pagination` rules (≈ 200 lines). Existing `main ul li` rules can be removed once the templates stop emitting `<ul>`.
- **`pelicanconf.py`** — adds `DEFAULT_PAGINATION` (and possibly `PAGINATED_TEMPLATES`) and registers the intro plugin.
- **`garden/commands/new.py`** — new branch for `--kind intro` with scope prompt and frontmatter writer.
- **`garden/content_index.py`** — may need to be aware of intro files for tooling (out of scope for picker, but the file walker should not error on them).
- **No deploy changes** — GHA workflow unchanged; build still runs `make build`.
- **Coordination with `add-l10n-rendering`** — the new homepage introduces at least one new English label (`Recent posts` header above the catalogue). This ships in English now; `add-l10n-rendering` will sweep it up alongside the rest of the chrome strings. The roadmap-noted coordination is addressed by ordering: `refactor-homepage` ships first.
- **Documentation** — `README.md` (authoring workflow for intros, mention of pagination), `docs/visual-identity.md` (catalogue card styling pattern) updated during implementation.
