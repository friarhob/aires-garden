## 1. Pelican configuration

- [x] 1.1 In `pelicanconf.py`, set `ARTICLE_LANG_URL = "{slug}/"` and `ARTICLE_LANG_SAVE_AS = "{slug}/index.html"` so non-default-language articles use the terminal `/<slug>/` form (per ADR-0004 / D3).
- [x] 1.2 In `pelicanconf.py`, set `TRANSLATION_FEED_ATOM = "feeds/{lang}.atom.xml"` and (if needed for default-lang per-feed parity) `FEED_ATOM = "feeds/{lang}.atom.xml"` per design D9. Verify after the build that one feed per lang is emitted.
- [x] 1.3 Confirm `publishconf.py` keeps `FEED_ALL_ATOM = "feeds/all.atom.xml"` (already configured) — no edit needed beyond verification.

## 2. `i18n_grouping` plugin (article translation grouping)

- [x] 2.1 Create `plugins/i18n_grouping/__init__.py` with a `register()` function that connects to `article_generator_finalized`.
- [x] 2.2 Implement the signal handler: walk `generator.articles + generator.translations`, build a `dict[translation_key, list[Article]]`, and attach the relevant list to each article as `article.translation_group` (sorted alphabetically by `Lang` for deterministic rendering).
- [x] 2.3 Add a helper exposed to templates (e.g. via `generator.context` or as a module function used through a Jinja `globals` registration in the same plugin) that returns the union of `Lang` values across all articles, sorted alphabetically. Used by the scope switcher and by per-language index generation.
- [x] 2.4 Generate per-language index pages: emit `output/<lang>/index.html` for every lang in the union, listing articles whose `Lang == <lang>` sorted by `Date` descending. Either via Pelican's `DIRECT_TEMPLATES` mechanism per-lang, or via a small `get_writer`/`finalized` hook in this plugin that renders `themes/garden/templates/lang_index.html` per lang.
- [x] 2.5 Register `i18n_grouping` in `pelicanconf.py`'s `PLUGINS` list (alongside `frontmatter_lint`).

## 3. `multilingual_404` plugin (per-language 404 merger)

- [x] 3.1 Create `plugins/multilingual_404/__init__.py` with a `register()` function that connects to `page_generator_finalized` (or `finalized` if signal ordering makes that cleaner — verify experimentally).
- [x] 3.2 Implement the page-discovery step: scan `content/pages/` for files matching `404.<lang>.md`, parse each frontmatter via the existing `plugins.frontmatter_lint.schema.parse_frontmatter`, render each Markdown body to HTML via Pelican's reader (or `markdown.markdown(...)` directly if the reader path is awkward).
- [x] 3.3 ~~Build the slug-to-lang map~~ Superseded: the inference script consults `navigator.language` instead, so no per-article payload is built. (See revised D8.)
- [x] 3.4 Render `themes/garden/templates/404.html` (a new template, see task 4.5) with the per-lang HTML bodies. Write the result to `output/404.html` directly (no `Save_as` / `URL` on the source pages, so Pelican's default page mechanics don't emit a competing file).
- [x] 3.5 Register `multilingual_404` in `pelicanconf.py`'s `PLUGINS` list (alongside `i18n_grouping` and `frontmatter_lint`).

## 4. Templates

- [x] 4.1 Update `themes/garden/templates/base.html` to render the scope switcher per design D6: an "All" entry plus one entry per lang in the dynamic union, with the page-context-aware behaviour (post-page links to translations with disabled missing langs; non-post-page links to per-lang indexes; "All" highlighted on `/`, current lang highlighted on `/<lang>/` and post pages).
- [x] 4.2 Update `themes/garden/templates/article.html` to render the "Available in" line for posts with two or more translations. Use `article.translation_group` provided by `i18n_grouping`. Hide the line for single-language posts.
- [x] 4.3 Update `themes/garden/templates/index.html` to iterate the deduped groups (one per `Translation_key`), with each entry linking to the default-lang article (or alphabetically-first if no default exists) and surfacing the available languages. Reuse the helper from task 2.3.
- [x] 4.4 Create `themes/garden/templates/lang_index.html` for the per-language indexes. Same shape as `index.html` but iterates the filtered list rather than groups.
- [x] 4.5 Create `themes/garden/templates/404.html` template used by the `multilingual_404` plugin: emits one `<section data-lang="<lang>">` per language section the plugin passes in, plus the inline JS for two-stage language prioritisation (URL prefix → `navigator.language` → default-lang fallback). Document the `data-default-lang` attribute on `<html>`.

## 5. Inline 404 inference script

- [x] 5.1 Inside `themes/garden/templates/404.html`, write the inline `<script>` block (under 50 lines, no external resources) implementing: stage 1 — match `^/([a-z]{2})/` against `location.pathname` and prioritise that section if the lang exists; stage 2 — read the 2-letter prefix of `navigator.language` and prioritise that section if it matches one of the site's languages; fallback — read `<html data-default-lang>` and prioritise that.
- [x] 5.2 "Prioritise" implementation: on match, set every other `<section data-lang>` to `display: none` (or `hidden` attribute) and update `document.documentElement.lang` to the matched lang. Default state (before JS runs / JS disabled): all sections visible.
- [x] 5.3 Test in the browser dev console: load `/404.html` via the dev server and verify section selection across the three branches — stage 1 (e.g. `/pt/missing/` → PT), stage 2 (`/random-typo/` with browser locale set to `pt` → PT), and fallback (`/random-typo/` with browser locale set to `de` → default-lang).

## 6. Content migration

- [x] 6.1 Rename `content/pages/404.md` to `content/pages/404.en.md`. The frontmatter stays as-is; the body is the existing English copy. (Verify `frontmatter_lint` still passes — pages do not have filename coupling per the page schema, so the rename is non-binding on field values, but `Lang: en` is added for clarity if not already present.)
- [x] 6.2 Author `content/pages/404.pt.md` with the same `Save_as: 404.html` / `URL: 404.html` frontmatter wired through the merger, `Lang: pt`, `Status: hidden`, and a Portuguese body matching the existing English message in tone.
- [x] 6.3 Verify `frontmatter_lint` accepts both files (`make build` reaches the merger stage).

## 7. ADR-0007 indexing

- [x] 7.1 Confirm `openspec/decisions/0007-small-clientside-js.md` exists with `## Status: Accepted — 2026-04-30` and Context / Decision / Consequences sections (already drafted during proposal phase — verify it's still on disk and committed alongside the bundle).
- [x] 7.2 Confirm `openspec/decisions/README.md` lists ADR-0007 under `## Index` (already added during proposal phase — verify and commit if it was lost in any rebase).

## 8. Build verification (positive cases)

- [x] 8.1 Run `make build` against the existing tree (post `ola-jardim` PT-only + future PT/EN 404 sources). Expect zero errors from `frontmatter_lint`, the build to produce: `output/ola-jardim/index.html` (no language suffix), `output/index.html` (aggregate with `ola-jardim` listed once and PT badge), `output/en/index.html` and `output/pt/index.html`, `output/feeds/all.atom.xml`, `output/feeds/en.atom.xml`, `output/feeds/pt.atom.xml`, `output/404.html` containing both `<section data-lang="en">` and `<section data-lang="pt">` plus the inline inference JS.
- [x] 8.2 Inspect `output/index.html`: confirm `ola-jardim` is the only entry and its link target is `/ola-jardim/` (not the default-lang `/hello-garden/` because no EN translation exists yet — alphabetical-first rule per D10).
- [x] 8.3 Inspect `output/en/index.html`: confirm it is empty of articles (no EN posts yet) but the page renders cleanly with the scope switcher and a "no posts in this language yet" message (or just an empty list — confirm visual is acceptable).
- [x] 8.4 Inspect `output/pt/index.html`: confirm `ola-jardim` appears with link `/ola-jardim/`.
- [x] 8.5 Inspect `output/ola-jardim/index.html`: confirm "Available in" line is hidden (single-language post), scope switcher shows "All / EN / PT" with PT highlighted and EN disabled (no EN translation exists), and the article content renders correctly.

## 9. 404 verification

- [x] 9.1 Inspect `output/404.html`: confirm both `<section data-lang="en">` and `<section data-lang="pt">` are present, the inline JS is under 50 lines with no external resource loads, and no per-article payload (slug-to-lang map or similar) is embedded.
- [x] 9.2 Test via the dev server (or by loading `output/404.html` directly): visit a `/pt/...` path and confirm only the PT section is visible. Visit a `/<unknown>/` path and confirm only the EN section (default lang) is visible. Disable JS and reload — confirm both sections are visible (graceful degradation).
- [x] 9.3 Test the `navigator.language` branch end-to-end: in DevTools Sensors (or via a browser-locale override), set the locale to `pt-BR`, then visit a non-existent path with no lang prefix (e.g. `/random-typo/`). Confirm the PT section is shown. Repeat with locale `de-DE` and confirm the default-lang (EN) section is shown.

## 10. Verification against specs

- [x] 10.1 Run `openspec validate add-i18n-rendering --strict`; expect zero errors.
- [x] 10.2 Walk each scenario in `specs/i18n-rendering/spec.md` and confirm the implementation satisfies it (manual checklist; tick each scenario off as verified).
- [x] 10.3 Confirm the GitHub Actions deploy still passes on `main` after merging — the new plugins run in CI's `make build` for the first time. Watch the run; if it fails for a CI-only reason (e.g. signal ordering surprise on a fresh Python process), surface and fix here rather than in a follow-up.
