## 1. Pelican configuration

- [x] 1.1 In `pelicanconf.py`, set `HIDDEN_ARTICLE_URL = "{slug}/"`, `HIDDEN_ARTICLE_SAVE_AS = "{slug}/index.html"`, `HIDDEN_ARTICLE_LANG_URL = "{slug}/"`, and `HIDDEN_ARTICLE_LANG_SAVE_AS = "{slug}/index.html"` so hidden articles emit at the terminal form (D13).
- [x] 1.2 In `pelicanconf.py`, set `TAG_URL = ""`, `TAG_SAVE_AS = ""`, `TAGS_URL = ""`, `TAGS_SAVE_AS = ""` to disable Pelican's native tag mechanism (D12).
- [x] 1.3 In `pelicanconf.py`, set `DRAFTS_AS_PUBLISHED = True` (dev default toggling the `dev_drafts` plugin's behaviour, D2 / ADR-0008).
- [x] 1.4 In `publishconf.py`, set `DRAFTS_AS_PUBLISHED = False`. Verify the existing `DRAFT_URL`/`DRAFT_SAVE_AS`/`DRAFT_LANG_URL`/`DRAFT_LANG_SAVE_AS` blanks remain in place; do not remove them.
- [x] 1.5 In `pelicanconf.py`, append `dev_drafts` and `tag_pages` to the `PLUGINS` list, in that order, *after* `i18n_grouping` (D15 — registration order matters because PLUGINS is processed top-to-bottom).

## 2. `dev_drafts` plugin (promote drafts to articles in dev)

- [x] 2.1 Create `plugins/dev_drafts/__init__.py` with a `register()` function that connects to `article_generator_pretaxonomy` (or, if that signal turns out to be unavailable in the pinned Pelican version, the earliest hook on the article generator that exposes both `articles` and `drafts` lists; document the choice).
- [x] 2.2 Implement the handler: when `generator.settings.get("DRAFTS_AS_PUBLISHED")` is truthy, move every article from `generator.drafts` into `generator.articles` and from `generator.drafts_translations` into `generator.translations`, and set each promoted article's `status` attribute to `"published"`. No-op when the setting is False or absent.
- [x] 2.3 Add a defensive assertion (or build-time log) in the handler that — when `DRAFTS_AS_PUBLISHED` is True and there were drafts to promote — warns if `generator.articles` already contains any item with `status == "draft"`, signalling a signal-ordering regression.
- [ ] 2.4 Verify the order empirically: with `DRAFTS_AS_PUBLISHED = True` and a `Status: draft` test article, run `make dev` and confirm `i18n_grouping` builds a `TRANSLATION_GROUPS` entry containing the promoted draft alongside any sibling translations.

## 3. `tag_pages` plugin (per-language tag pages and per-language all-tags index)

- [x] 3.1 Create `plugins/tag_pages/__init__.py` with a `register()` function that captures the article generator on `article_generator_finalized` (mirror `i18n_grouping`'s `_article_generator` module-level pattern) and connects to `finalized` for the emission pass.
- [x] 3.2 Implement a helper that walks `generator.articles + generator.translations` and produces `dict[(lang, tag_slug), list[Article]]`. Use Pelican's `pelican.utils.slugify` for the tag-slug computation. Sort each list by `Date` descending.
- [x] 3.3 In `finalized`, render `themes/garden/templates/tag_lang_index.html` once per `(lang, tag_slug)` key, writing to `output/<lang>/tag/<tag_slug>/index.html`. Pass `articles=articles_for_lang_and_tag`, `page_lang=lang`, `tag_slug`, `page_kind="tag_lang_index"`.
- [x] 3.4 Implement a helper that produces `dict[lang, list[tag_slug]]` (the per-language tag-slug union, sorted alphabetically). Render `tags_list.html` once per lang, writing to `output/<lang>/tags/index.html`. Pass `tag_slugs`, `page_lang`, `page_kind="lang_tags_list"`.

## 4. `tag_pages` plugin (cross-language tag pages and cross-language all-tags index)

- [x] 4.1 Implement a helper that produces `dict[tag_slug, list[TranslationGroup]]` from `generator.context["TRANSLATION_GROUPS"]` (D3) — a group is included if any of its articles carries the tag. Sort each value by the canonical article's `Date` descending (canonical = default-lang member if present, else alphabetically-first by Lang).
- [x] 4.2 Render `tag_group_index.html` once per tag-slug, writing to `output/tag/<tag_slug>/index.html`. Pass `groups=groups_for_tag`, `tag_slug`, `page_kind="tag_group_index"`, plus `all_prose: dict[lang, html]` (see task 5.x).
- [x] 4.3 Implement a helper that produces the cross-language tag-slug union. Render `tags_list.html` for the cross-language form, writing to `output/tags/index.html`. Pass `tag_slugs`, `page_kind="all_tags_list"` (no `page_lang`).

## 5. `tag_pages` plugin (tag-prose discovery and rendering)

- [x] 5.1 Implement a tag-prose discovery pass that walks `content/tag-prose/<slug>/` directories from `pelican.settings["PATH"]`. For each `<slug>` directory, parse every file matching `<scope>.<lang>.md` where `<scope> ∈ {all, lang}` using the new tag-prose entrypoint in `plugins.frontmatter_lint.schema` (task 7.5). Collect the body string and frontmatter for each file.
- [x] 5.2 Render each tag-prose body to HTML by calling `markdown.markdown(body, extensions=[...])` directly. Use stock CommonMark only — no extensions in this change (D16). Build `tag_prose: dict[tag_slug, dict[("all"|"lang"), dict[lang, html]]]`.
- [x] 5.3 In task 4.2 (cross-language tag rendering), pass `all_prose = tag_prose.get(slug, {}).get("all", {})` to the template. The template chooses between zero/one/N rendering based on `len(all_prose)` (see task 6.4).
- [x] 5.4 In task 3.3 (per-language tag rendering), pass `tag_prose_html = tag_prose.get(slug, {}).get("lang", {}).get(lang)` to the template. The template renders the body block when truthy, omits otherwise (see task 6.5).

## 6. Templates

- [x] 6.1 Create `themes/garden/templates/_lang_inference_script.html` containing the inline `<script>` block currently in `themes/garden/templates/404.html` (D10). Move the verbatim contents; no logic change.
- [x] 6.2 Edit `themes/garden/templates/404.html` to replace the inline `<script>` block with `{% include "_lang_inference_script.html" %}`. Verify the rendered 404 page is byte-identical to the pre-refactor output (or, if minor whitespace differs, behaviour-identical).
- [x] 6.3 Edit `themes/garden/templates/article.html` to add a "Tags:" line below the article body, hidden when `article.tags` is empty. Each tag links to `/<article.lang>/tag/<slugify(tag)>/`. Use Jinja's `slugify` filter or a passthrough variable from the plugin.
- [x] 6.4 Create `themes/garden/templates/tag_group_index.html` (extends `base.html`). Mirrors `index.html` for the list, but above the list renders prose based on `all_prose` cardinality:
  - `len(all_prose) == 0`: nothing.
  - `len(all_prose) == 1`: the single body inline (no `<section>` wrapper, no script).
  - `len(all_prose) >= 2`: one `<section data-lang="<lang>">{{ body | safe }}</section>` per entry, then `{% include "_lang_inference_script.html" %}`.
- [x] 6.5 Create `themes/garden/templates/tag_lang_index.html` (extends `base.html`). Mirrors `lang_index.html` for the list. Above the list, render `{{ tag_prose_html | safe }}` when truthy, omit otherwise. Single block, no `<section>`, no script.
- [x] 6.6 Create `themes/garden/templates/tags_list.html` (extends `base.html`). Iterates `tag_slugs`, each rendered as a link. Heading text and link target depend on `page_lang`: when set, list scoped to that language with anchors to `/<lang>/tag/<slug>/`; when unset, cross-language list with anchors to `/tag/<slug>/`.

## 7. `frontmatter_lint` schema additions

- [x] 7.1 In `plugins/frontmatter_lint/schema.py`, extend the `Tags` validation to reject any tag whose `pelican.utils.slugify(tag)` is the empty string. Error message: `"Tag {value!r} produces an empty slug under slugify"`.
- [x] 7.2 In the same module, extend the `Tags` validation to reject any post whose tag list contains two or more entries with the same `slugify(...)` value. Error message: `"Tags {a!r} and {b!r} both slugify to {slug!r}"`. Apply per post, listing every collision.
- [x] 7.3 Add fixture-style unit tests (or extend the existing test entry points) covering: empty-slug rejection, slug-collision rejection, mixed-case acceptance for distinct slugs, and existing-good-tags regression.
- [x] 7.4 Define a `parse_tag_prose_frontmatter(...)` (or analogous) function in `plugins/frontmatter_lint/schema.py`: required `Title` (non-empty string), `Lang` (ISO 639-1 alpha-2 via `langcodes`), `Status` (must be exactly `"hidden"`); forbidden `Slug`, `Translation_key`, `Tags`; reject all other fields.
- [x] 7.5 Add the filename↔frontmatter coupling check for tag-prose: directory name matches the post `Slug` regex; filename `<scope>.<lang>.md` where `<scope> ∈ {all, lang}` and `<lang>` equals the file's frontmatter `Lang`. Errors name the specific axis of mismatch (directory, scope, or lang).
- [x] 7.6 Add the per-directory uniqueness check for tag-prose: no two files in one slug directory share the same `(scope, lang)` pair.
- [x] 7.7 In `plugins/frontmatter_lint/__init__.py` (the plugin module): when scanning content, also walk `content/tag-prose/` and apply the new tag-prose validators. Errors integrate with the existing file-anchored grouped report.
- [x] 7.8 In the standalone CLI module (`plugins/frontmatter_lint/cli.py` or equivalent): when `<content-root>` contains a `tag-prose/` subdirectory, walk it and validate. Exit code and report format match the existing posts/pages flow.
- [x] 7.9 Run `python -m frontmatter_lint content` against the current tree and confirm no new errors before authoring tag-prose files (i.e. the existing tree still passes).

## 8. ADR-0008 (dev-drafts-promotion)

- [x] 8.1 Author `openspec/decisions/0008-dev-drafts-promotion.md` with `## Status: Accepted — <today>` and Context / Decision / Consequences sections. Decision: settings-flag toggle (`DRAFTS_AS_PUBLISHED`), set True in `pelicanconf.py` and False in `publishconf.py`. Rejected: env var, two-plugin variant, template-level draft handling.
- [x] 8.2 Update `openspec/decisions/README.md` to add ADR-0008 to the `## Index` section in numerical order alongside the existing ADRs.

## 9. ADR-0009 (tag-prose-content-type)

- [x] 9.1 Author `openspec/decisions/0009-tag-prose-content-type.md` with `## Status: Accepted — <today>` and Context / Decision / Consequences sections. Decision: third content type at `content/tag-prose/<slug>/<scope>.<lang>.md`, schema independent of pages. Rejected: page-with-marker (`Page_kind: tag-prose`), embed-prose-in-first-tagged-article, file-layout option II (parallel dirs), file-layout option III (filename infix).
- [x] 9.2 Update `openspec/decisions/README.md` to add ADR-0009 to the `## Index` section.

## 10. Seed content for end-to-end verification

- [ ] 10.1 Author at least one post under `content/posts/` carrying `Tags: published-works` (any lang). Real authored content if ready; otherwise a thin placeholder noting it's a seed (the placeholder body should still be coherent — the seed post is publicly visible). Conform to the existing post schema (`Title`, `Slug`, `Date`, `Lang`, `Status`, `Translation_key`, `Tags`).
- [ ] 10.2 Create `content/tag-prose/published-works/` directory.
- [ ] 10.3 Author `content/tag-prose/published-works/all.en.md` and `content/tag-prose/published-works/all.pt.md` (cross-language prose, English and Portuguese — different bodies, both framed as "all my published works" without "in &lt;lang&gt;" qualifier). Required frontmatter: `Title`, `Lang`, `Status: hidden`.
- [ ] 10.4 Author at least one `content/tag-prose/published-works/lang.<lang>.md` (recommended: `lang.en.md` and `lang.pt.md` so both per-language tag pages are exercised). Body uses "in &lt;lang&gt;" framing.
- [ ] 10.5 Run `python -m frontmatter_lint content` and confirm zero validation errors across all three trees.

## 11. Build verification

- [ ] 11.1 Run `make dev` and verify in the browser:
  - `/` lists `ola-jardim` (rant) and the published-works seed post (deduped if multilingual).
  - `/en/`, `/pt/` list each lang's articles including drafts (if any are present in the tree at this point).
  - `/tag/rant/` shows `ola-jardim` once with EN+PT badges, list-only (no prose).
  - `/tag/published-works/` shows the seed post and renders cross-language prose (EN section visible to EN browser; PT to PT browser; default-lang fallback otherwise).
  - `/en/tag/published-works/` and `/pt/tag/published-works/` render the matching `lang.<lang>.md` body above the list.
  - `/tags/` lists `rant` and `published-works`, each linking to `/tag/<slug>/`.
  - `/en/tags/` and `/pt/tags/` list the language-scoped tag set.
  - Article pages show the "Tags:" line linking to per-language tag pages.
- [ ] 11.2 With `DRAFTS_AS_PUBLISHED = True` (dev), temporarily flip the seed post's `Status` to `draft`, run `make dev`, and verify the post still appears at `/<slug>/`, on the homepage, on its language index, and on its tag pages — exactly as it did with `Status: published`. Revert the flip before commit.
- [ ] 11.3 Run `make build` (production via `publishconf.py`). Verify `output/` contains the same URLs as 11.1 EXCEPT no draft articles are emitted, and verify the four `DRAFT_*` URL slots produce nothing.
- [ ] 11.4 Inspect `output/404.html` to confirm the language-inference script is still functional after the partial extraction (browser-language match, default-lang fallback, JS-off shows all sections). Behavioural parity with the pre-refactor 404.
- [ ] 11.5 Inspect `output/tag/published-works/index.html` source and confirm the inline language-inference `<script>` (or its included partial output) is present and identical to the 404's.
