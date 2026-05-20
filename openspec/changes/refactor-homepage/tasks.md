## 1. Intro schema and lint integration

- [x] 1.1 Add `IntroFrontmatter` Pydantic model in `plugins/frontmatter_lint/schema.py`: required `Title`, `Lang`, `Status` (literal `"hidden"`); `extra="forbid"`; same `Lang` validator used by post/tag-prose
- [x] 1.2 Add an `IntroFilenameContract` parser (mirroring the tag-prose one) that splits `<scope>.<lang>.md` and validates `scope ∈ {all, lang}`, lang ISO 639-1; rejects nested paths under `content/intro/`
- [x] 1.3 In `plugins/frontmatter_lint/cli.py`, add discovery pass for `content/intro/`; emit grouped, file-anchored errors using the same formatter as posts/tag-prose
- [x] 1.4 In `plugins/frontmatter_lint/__init__.py`, register the intro pass so `make build` validates intro files
- [x] 1.5 Add unit tests in `plugins/frontmatter_lint/tests/`: valid `all.en.md` passes; missing `Title` fails; `Status: published` fails; `Slug` field rejected; mismatched filename lang rejected; nested-path rejected; duplicate `(scope, lang)` rejected
- [ ] 1.6 Confirm `garden lint` exits 0 on an empty `content/intro/` and on `content/intro/` populated with seed files (added in section 3)

## 2. `garden new --kind intro` flow

- [ ] 2.1 In `garden/commands/new.py`, add `intro` to the `--kind` enum/choices; add `--scope` Typer option (`Optional[str]`, default `None`, validated against `{all, lang}`)
- [ ] 2.2 Implement `_create_intro(scope: str, lang: str, title: str)`: writes `content/intro/<scope>.<lang>.md` with only `Title`, `Lang`, `Status: hidden`; refuses to overwrite
- [ ] 2.3 In the main `new()` function: when `kind == "intro"`, skip the slug prompt; prompt for `scope` (questionary select between `all` and `lang`) in TTY mode; require `--scope` in non-TTY mode; silently ignore `--slug` if supplied
- [ ] 2.4 Update `garden --help` and `garden new --help` so the `--kind` option lists exactly `post`, `page`, `tag-prose`, `intro`
- [ ] 2.5 Add unit tests in `garden/tests/`:
  - `garden new --kind intro --title "X" --scope all --lang en` writes a lint-passing file with no `Slug:`
  - Non-TTY without `--scope` exits non-zero with a clear message
  - Invalid `--scope tag` exits non-zero citing the value set
  - `--slug` is silently ignored
  - TTY flow prompts for scope (mock `questionary.select`)
- [ ] 2.6 End-to-end check: `garden new --kind intro --title "Welcome" --scope all --lang en` → file at `content/intro/all.en.md` → `garden lint` exits 0

## 3. Seed intro content

- [ ] 3.1 Author `content/intro/all.en.md`: short editorial passage for the cross-language root (≤ 80 words; 2–3 short paragraphs)
- [ ] 3.2 Author `content/intro/all.pt.md`: Portuguese version of the same framing
- [ ] 3.3 Author `content/intro/lang.en.md`: short editorial passage framing the English corner of the garden
- [ ] 3.4 Author `content/intro/lang.pt.md`: Portuguese version of the same per-language framing
- [ ] 3.5 Run `garden lint` and confirm exit 0
- [ ] 3.6 Commit seed content separately from plugin/template changes for a clean diff

## 4. Pelican plugin: intro discovery

- [ ] 4.1 Create `plugins/intro_pages/__init__.py` (or extend an existing plugin if a clear fit exists): walk `content/intro/` on Pelican's `generator_init` (or equivalent) signal; parse each file's frontmatter + body
- [ ] 4.2 Group files by `(scope, lang)`; expose two settings to templates: `INTRO_ALL` (dict of `lang → rendered HTML`) and `INTRO_LANG` (dict of `lang → rendered HTML`)
- [ ] 4.3 Use Pelican's Markdown reader (or `markdown` directly) so the rendered HTML matches Pelican's other output exactly (same extensions, `smarty`, `attr_list`, etc.)
- [ ] 4.4 Register the plugin in `pelicanconf.py` `PLUGINS` list
- [ ] 4.5 Add unit tests in `plugins/intro_pages/tests/`: empty `content/intro/` → both dicts empty; one `all.en.md` → `INTRO_ALL == {"en": "<rendered>"}`; one `lang.pt.md` → `INTRO_LANG == {"pt": "<rendered>"}`
- [ ] 4.6 Confirm `make devbuild` succeeds with the plugin registered and the seed content in place

## 5. Templates: catalogue layout

- [ ] 5.1 In `themes/garden/templates/index.html`, replace `<ul>...<li>` with the catalogue markup: `<section class="catalogue">` → `<div class="catalogue-grid">` → `<a class="catalogue-card">` per group; each card carries `.card-title`, `.card-meta` with `<time datetime>` and `.langs` of `<span class="lang-chip">`
- [ ] 5.2 In `themes/garden/templates/lang_index.html`, apply the same catalogue markup; each card's `.langs` shows exactly one chip for the page language
- [ ] 5.3 Card `href` mirrors the existing homepage rules: cross-language card links to default-lang translation when available, else alphabetically-first; per-language card links to its single article
- [ ] 5.4 Confirm `make devbuild` succeeds and the new markup is present in `output/index.html` and `output/<lang>/index.html`

## 6. Templates: intro region

- [ ] 6.1 In `themes/garden/templates/index.html`, render `<section class="intro">` containing one `<section class="intro-body" data-lang="<lang>">` per key in `INTRO_ALL`; omit the wrapper if `INTRO_ALL` is empty; place it between the per-page lang-links bar and the catalogue heading
- [ ] 6.2 In `themes/garden/templates/lang_index.html`, render `<section class="intro">` containing the single `INTRO_LANG[page_lang]` body if present; omit otherwise; same placement
- [ ] 6.3 Create `themes/garden/templates/_intro_inference_script.html`: inline `<script>` (≤ 50 lines, no external resources) implementing stages 1–4 of the inference chain (stored preference → `navigator.language` → `data-default-lang` → alphabetically-first emitted section); include only in `index.html`, never in `lang_index.html`
- [ ] 6.4 Verify the inference script: stage 1 — set `localStorage["garden-lang"] = "pt"` and reload `/`, only `<section data-lang="pt">` visible; stage 2 — clear storage, set browser language to `pt`, only `<section data-lang="pt">` visible; stage 3 — neither matches, `data-default-lang="en"` shows `en`; stage 4 — none match, alphabetically-first section visible
- [ ] 6.5 Verify JS-disabled fallback: every `<section class="intro-body" data-lang>` is visible

## 7. Styling

- [ ] 7.1 Add `.intro` and `.intro-body` rules to `themes/garden/static/css/styles.css`: left rule in `var(--accent-display)`, padding, max-width on paragraphs; `.intro-body[data-lang]:not(.is-active) { display: none; }` for the JS-driven toggle
- [ ] 7.2 Add `.catalogue`, `.catalogue-grid`, `.catalogue-card` rules: grid-template-columns `repeat(auto-fill, minmax(280px, 1fr))`; card uses `grid-template-rows: auto 1fr auto`; title clamp via `-webkit-line-clamp: 3`; meta row separated by a dashed `var(--border)` rule
- [ ] 7.3 Add `.card-title`, `.card-meta`, `time`, `.langs`, `.lang-chip` rules — reuse existing design tokens; no new tokens introduced
- [ ] 7.4 Add `nav.pagination` rules — prev/next links and numbered pages, with `.current` pill in `var(--accent)`
- [ ] 7.5 Remove obsolete `main ul li` rules from the article-list section that are no longer used (tag pages and other surfaces still use `<ul>` — keep rules that other templates depend on; only remove what's truly orphaned)
- [ ] 7.6 Visual review in `make dev`: light mode and dark mode, three viewport widths (mobile ~375px, tablet ~768px, desktop ~1200px); verify grid reflow, title clamp, dashed rule legibility, hover states
- [ ] 7.7 Run `python tools/contrast_audit.py` and confirm no regressions (no new tokens, but verify the existing pairs still pass)

## 8. Pagination

- [ ] 8.1 Add `DEFAULT_PAGINATION = 12` to `pelicanconf.py`; confirm `make devbuild` paginates `/` once post count > 12 (add temporary fake posts if needed to test, then remove)
- [ ] 8.2 Confirm Pelican emits `/page/2/`, `/page/3/`, … without additional configuration
- [ ] 8.3 Investigate per-language pagination: determine whether `i18n_grouping` plugin's `/<lang>/` output goes through Pelican's paginator. If not, extend the plugin to emit `<lang>/page/2/` pages OR switch the per-language template to a paginator-friendly approach
- [ ] 8.4 If the per-language pagination approach deviates significantly from Pelican-native, promote the decision to an ADR (`0012-home-pagination.md`) per design.md's open-question note
- [ ] 8.5 Add a `<nav class="pagination">` block to both `index.html` and `lang_index.html` rendering: prev link (disabled on page 1), numbered pages with `.current` marker, next link (disabled on last page)
- [ ] 8.6 Hide the intro region on pages other than the first (`{% if page_number == 1 %}` or equivalent — page 1 carries intro, page 2+ does not)
- [ ] 8.7 Verify rendered output: `output/index.html` has intro + catalogue + pagination; `output/page/2/index.html` has catalogue + pagination only; same for per-language

## 9. Documentation

- [ ] 9.1 Update `README.md` to mention `garden new --kind intro` in the authoring section and link to `content/intro/` for examples
- [ ] 9.2 Update `docs/visual-identity.md` to document the catalogue card pattern (grid template, card structure, dashed-rule meta footer) under a new "Patterns" or "Components" section — short, just enough that the design intent is recoverable

## 10. End-to-end verification

- [ ] 10.1 Run `garden lint` — exit 0
- [ ] 10.2 Run `make build` — succeeds with no warnings
- [ ] 10.3 Open `output/index.html` in a browser, verify: intro region with EN section visible (default-lang inference), catalogue grid with all post groups, pagination if applicable
- [ ] 10.4 Open `output/en/index.html` and `output/pt/index.html`, verify per-language intro and catalogue
- [ ] 10.5 Open `output/page/2/index.html` if pagination triggered, verify no intro region and catalogue continues
- [ ] 10.6 Click each language in the header lang picker on `/` and verify it switches the visible intro section (preference write + section-toggle)
- [ ] 10.7 Disable JavaScript in browser, reload `/`, verify all `<section class="intro-body" data-lang>` blocks are visible (graceful degradation)

## 11. Deploy validation gate

- [ ] 11.1 Push branch to remote
- [ ] 11.2 Monitor GitHub Actions `build-and-deploy` workflow; confirm green
- [ ] 11.3 Open the deployed site, repeat verification steps 10.3–10.7 against production URL
- [ ] 11.4 Ask user: "Deploy validated. Ready to finalise with /garden:finalise?"
