## Why

The site already authors multilingual posts (`add-content-model` enforces `Lang` and `Translation_key`), but readers can't see them as multilingual: there's no language switcher, no "Available in" badges linking to translations, and the URL of a non-default-language post still carries Pelican's default lang suffix (`/ola-jardim-pt.html`) instead of the terminal `/ola-jardim/` form ADR-0004 specifies. Single-language posts (like the existing PT-only `ola-jardim`) don't even appear on the homepage, because Pelican's default index iterates `DEFAULT_LANG` only. The 404 page is English-only — a Portuguese reader who mistypes a `/pt/...` URL gets a unilingual error. This change wires the multilingual data already in the tree into the actual reader experience.

## What Changes

- **Translation-grouping plugin (`plugins/i18n_grouping/`).** Pelican's native translation linking matches on shared `Slug:`, but ADR-0004's localised-slug rule (each language has its own slug) breaks that. The plugin groups articles by `Translation_key` and exposes the group on each article so templates can render switchers and badges without re-doing the join. Scope is article-only — error pages are a separate concern (see below).
- **Terminal-form URLs for all languages.** Set `ARTICLE_LANG_URL = "{slug}/"` and `ARTICLE_LANG_SAVE_AS = "{slug}/index.html"` so non-default-language articles live at `/<slug>/`, not `/<slug>-<lang>.html`. The PT post `ola-jardim` moves from `/ola-jardim-pt.html` to `/ola-jardim/`. Old URL is dropped (acceptable: site is pre-launch and noindexed).
- **Scope switcher in the site header** (rendered in `base.html`). Conceptually a scope picker rather than a pure language picker: always shows an "All" entry that points to the aggregate homepage `/`, followed by one entry per lang. The lang list is computed dynamically as the union of `Lang` values across all posts on the site (no static `KNOWN_LANGS` setting — `frontmatter_lint` already validates each `Lang` via `langcodes`, so any value in content is a real ISO 639-1 code by construction).
  - **"All" entry:** always present and enabled, links to `/`. Highlighted only when the current page is `/` itself.
  - **Per-lang entries on post pages:** each entry links to that post's translation; languages without a translation are visibly disabled.
  - **Per-lang entries on non-post pages** (main `/` aggregate, `/<lang>/` indexes, 404): each entry links to the corresponding per-language index `/<lang>/`. The current page's lang (if any) is highlighted.
- **"Available in: EN, PT" line on every post page.** Lists only languages the post actually has, each as a link to its translation.
- **Deduped homepage at `/`.** Each post appears once (one card per `Translation_key` group). The card links to the default-language version if available, else the first available translation. Makes single-language posts visible on the homepage.
- **Per-language index pages at `/<lang>/`.** One per language found in content (e.g. `/en/`, `/pt/`), each listing only posts with a translation in that language. Generated dynamically from the union-of-langs computation, so adding a French post auto-creates `/fr/`.
- **Per-language Atom feeds at `/feeds/<lang>.atom.xml`** alongside the existing aggregate at `/feeds/all.atom.xml`. Subscribers can pick either granularity.
- **Multilingual 404 plugin (`plugins/multilingual_404/`), separate from the article-grouping plugin.** Author each language as `content/pages/404.<lang>.md`. The plugin renders each body to HTML, wraps each in `<section data-lang="<lang>">`, and concatenates into a single `output/404.html`. ~25 lines of inline JS infer the target language: stage 1 reads any `/<lang>/` prefix from the requested URL; stage 2 falls back to the 2-letter prefix of `navigator.language`; final fallback is the document's `data-default-lang` attribute. The matching section is featured; the others are hidden. With JS disabled, all sections remain visible — graceful degradation per ADR-0007's second bar. Kept in its own plugin because its lifecycle (one-shot HTML stitching on the page generator) and its consumers (none — pure output transform) are orthogonal to article translation grouping.
- **Record ADR-0007** documenting the small-client-side-JS stance that the 404 mechanics depend on.

## Capabilities

### New Capabilities
- `i18n-rendering`: translation-grouping plugin (article scope), terminal-form URLs across languages, language switcher (post-context and index-context behaviour), "Available in" badges, deduped homepage, per-language index pages, per-language RSS feeds, multilingual 404 plugin with URL-driven language inference and graceful-degradation fallback.

### Modified Capabilities
<!-- None. site-build, deploy-pipeline, and content-model requirements remain unchanged.
     The deploy-pipeline tasks (archived) noted the PT post lived at /ola-jardim-pt.html as a transitional URL — that note already pointed forward to this change. Updating the URL is new behaviour added by this change, not a modification of an existing requirement. -->

## Impact

- **New code:** two separate plugins.
  - `plugins/i18n_grouping/` — article translation grouping. Reads `generator.articles + generator.translations`, groups by `Translation_key`, exposes the group on each article for templates to consume.
  - `plugins/multilingual_404/` — multilingual 404 builder. Reads `content/pages/404.<lang>.md` files, renders each body, wraps in `<section data-lang>`, embeds the inline language-inference JS, writes one combined `output/404.html`.
  - Both registered in `pelicanconf.py`'s `PLUGINS` alongside `frontmatter_lint`. Kept separate per the lifecycle/consumer split: grouping runs every build and feeds article templates; the 404 builder is a one-shot output transform with no downstream consumers.
- **Templates:** edits to `themes/garden/templates/base.html` (language switcher), `index.html` (deduped aggregate + "Available in" indicators), `article.html` ("Available in" badges); new `themes/garden/templates/lang_index.html` for per-language home pages.
- **Static asset:** the 404 inline JS (~15 lines) lives inside `themes/garden/templates/404.html` (template file used by the merger); it is not an external script.
- **Config:** `pelicanconf.py` adds both `i18n_grouping` and `multilingual_404` to `PLUGINS`; sets `ARTICLE_LANG_URL = "{slug}/"`, `ARTICLE_LANG_SAVE_AS = "{slug}/index.html"`, and `TRANSLATION_FEED_ATOM = "feeds/{lang}.atom.xml"`. `publishconf.py` keeps `FEED_ALL_ATOM = "feeds/all.atom.xml"` (already set) and inherits everything else.
- **Content migration:** the existing `content/pages/404.md` becomes `content/pages/404.en.md` (renamed). A new `content/pages/404.pt.md` is added so the multilingual rendering has at least two languages to demonstrate. Future languages: just add another file.
- **URL break, deliberate:** `/ola-jardim-pt.html` → `/ola-jardim/`. Acceptable since the site is pre-launch and noindexed (deploy-pipeline's two-layer noindex stays active). Recorded for the launch-to-apex change's sanity-check list.
- **Decision log:** new ADR-0007 (`small-clientside-js.md`) committed alongside this change, indexed in `openspec/decisions/README.md`.
- **No new dependencies.** Uses pydantic/langcodes already present (only for code path consistency where useful), Pelican's existing translation/feed plumbing, and ~15 lines of inline JS.
- **Future changes unblocked:** `add-tags-and-drafts` (tag pages will reuse the per-language index template pattern), `add-design-tokens` (the gallery design replaces the minimal homepage introduced here), `add-python-cli` (`garden translate` reuses the i18n grouping for the "what's missing" view).
