# tags-and-drafts Specification

## Purpose

Define the tag index pages, tag-prose content type, draft promotion for development
builds, and the associated ADR housekeeping. Tag pages are produced entirely by the
`tag_pages` plugin; Pelican's native tag generators are disabled. Draft articles are
promoted to published status in development builds only, gated by a settings flag.

## Requirements

### Requirement: Cross-language tag index pages exist at `/tag/<slug>/` and dedupe by `Translation_key`

For every tag-slug appearing on any article anywhere on the site, a cross-language tag page SHALL be emitted at `/tag/<slug>/`. The page iterates translation groups (not individual articles) and lists every group containing at least one article that carries the tag.

#### Scenario: Page exists for every tag
- **WHEN** at least one article anywhere in the content tree carries `Tags: [<tag>]`
- **THEN** `output/tag/<slugify(tag)>/index.html` is produced.

#### Scenario: Translated posts appear once per group
- **WHEN** a post exists in two or more languages and at least one translation carries `Tags: [<tag>]`
- **THEN** the cross-language tag page lists the post's group exactly once, with language badges showing every available translation.

#### Scenario: Card link goes to the preferred translation
- **WHEN** a group with two or more translations is rendered on the cross-language tag page
- **THEN** the card's link points to the translation whose `Lang` equals `DEFAULT_LANG` if available, otherwise to the alphabetically-first translation by `Lang`.

#### Scenario: Group is included if any translation carries the tag
- **WHEN** a multi-language post tags only one of its translations (e.g. EN carries `published-works` but PT does not)
- **THEN** the post's group is still listed on `/tag/published-works/` (every translation in the group is reachable from the card via the language badges).

#### Scenario: Tag-slug is computed by Pelican's `slugify`
- **WHEN** an article carries `Tags: ["Published Works"]`
- **THEN** the tag page is emitted at `/tag/published-works/`, matching `slugify("Published Works")`.

### Requirement: Per-language tag index pages exist at `/<lang>/tag/<slug>/`

For every `(Lang, tag-slug)` pair appearing on any article, a per-language tag page SHALL be emitted at `/<lang>/tag/<slug>/`. The page iterates articles (not groups) and lists every article in that language that carries the tag.

#### Scenario: Page exists for every (lang, tag) pair
- **WHEN** at least one article with `Lang: <lang>` carries `Tags: [<tag>]`
- **THEN** `output/<lang>/tag/<slugify(tag)>/index.html` is produced.

#### Scenario: No page is emitted for languages without matching articles
- **WHEN** a tag is carried by EN articles only
- **THEN** `/en/tag/<slug>/` is produced and `/pt/tag/<slug>/` is NOT produced.

#### Scenario: Articles are sorted by Date descending
- **WHEN** two or more articles in the same language carry the same tag
- **THEN** they are listed on the per-language tag page sorted by `Date` descending.

#### Scenario: Per-language tag page lists only articles in that language
- **WHEN** a tag is carried by articles in multiple languages
- **THEN** `/<lang>/tag/<slug>/` lists only the articles whose `Lang` equals `<lang>` — translations in other languages are not surfaced on this page (they appear on the corresponding `/<other-lang>/tag/<slug>/`).

### Requirement: Cross-language all-tags index exists at `/tags/`

A single `/tags/` page SHALL list every tag-slug that has at least one article anywhere on the site, with each entry linking to its `/tag/<slug>/` page.

#### Scenario: Page exists when any tagged article exists
- **WHEN** any article in the content tree carries any tag
- **THEN** `output/tags/index.html` is produced.

#### Scenario: Each tag listed once
- **WHEN** the same tag appears on articles in multiple languages
- **THEN** the `/tags/` page lists the tag exactly once.

#### Scenario: Each entry links to the cross-language tag page
- **WHEN** a tag-slug entry is rendered on `/tags/`
- **THEN** its anchor's `href` resolves to `/tag/<slug>/`.

### Requirement: Per-language all-tags indexes exist at `/<lang>/tags/`

For every language with at least one tagged article, a per-language all-tags index SHALL be emitted at `/<lang>/tags/`, listing only the tag-slugs that have at least one article in that language.

#### Scenario: Page exists per language with tagged content
- **WHEN** any article with `Lang: <lang>` carries any tag
- **THEN** `output/<lang>/tags/index.html` is produced.

#### Scenario: Tags absent from a language are not listed
- **WHEN** a tag is carried only by articles in `Lang: en`
- **THEN** `/pt/tags/` does NOT list that tag.

#### Scenario: Each entry links to the per-language tag page
- **WHEN** a tag-slug entry is rendered on `/<lang>/tags/`
- **THEN** its anchor's `href` resolves to `/<lang>/tag/<slug>/`.

### Requirement: Article pages render a "Tags:" line linking to per-language tag pages

Every article page SHALL render a "Tags:" line below the body when the article's `Tags` list is non-empty. Each tag in the line SHALL link to the per-language tag page in the article's own language.

#### Scenario: Tags rendered for tagged article
- **WHEN** an article with `Tags: [a, b]` and `Lang: en` is rendered
- **THEN** the page contains a "Tags:" line with anchors to `/en/tag/<slugify(a)>/` and `/en/tag/<slugify(b)>/`, in the order the tags appear in the frontmatter list.

#### Scenario: No "Tags:" line for untagged article
- **WHEN** an article has `Tags: []` or no `Tags` field at all
- **THEN** no "Tags:" line is rendered on the page.

#### Scenario: Tag link uses article's own language
- **WHEN** a Portuguese article (`Lang: pt`) carries `Tags: [poesia]`
- **THEN** its tag link points to `/pt/tag/poesia/`, not `/tag/poesia/` and not `/en/tag/poesia/`.

### Requirement: Pelican's native tag mechanism is disabled

The build SHALL NOT emit any tag artefacts via Pelican's native tag generators; the plugin in this change is the sole producer of tag pages.

#### Scenario: TAG_URL and TAGS_URL are blanked in pelicanconf.py
- **WHEN** `pelicanconf.py` is inspected
- **THEN** `TAG_URL == ""`, `TAG_SAVE_AS == ""`, `TAGS_URL == ""`, and `TAGS_SAVE_AS == ""`.

#### Scenario: No `/tag/<slug>.html` files are emitted
- **WHEN** `make build` runs
- **THEN** no top-level `output/tag/<slug>.html` files are produced (only `output/tag/<slug>/index.html` from the plugin).

### Requirement: Tag prose is an authored content type discovered under `content/tag-prose/<slug>/`

A new content tree at `content/tag-prose/<slug>/` SHALL be the home of authored Markdown prose decorating tag pages. Files are discovered by the `tag_pages` plugin (not by Pelican's article or page generators), parsed via the shared `frontmatter_lint` schema module, and rendered to HTML with the `markdown` library directly.

#### Scenario: Cross-language prose body is read from `<scope>=all` files
- **WHEN** `content/tag-prose/<slug>/all.<lang>.md` exists
- **THEN** its rendered HTML body is available to the cross-language tag page renderer keyed by `<lang>`.

#### Scenario: Per-language prose body is read from `<scope>=lang` files
- **WHEN** `content/tag-prose/<slug>/lang.<lang>.md` exists
- **THEN** its rendered HTML body is available to the per-language tag page renderer for `/<lang>/tag/<slug>/`.

#### Scenario: Tag-prose files do not produce their own URLs
- **WHEN** `make build` runs against a tree containing tag-prose files
- **THEN** no URL is emitted with a path matching `tag-prose/...` and no URL collides with the article or page namespace.

#### Scenario: Tag-prose slug is inferred from the directory name
- **WHEN** a tag-prose file lives at `content/tag-prose/<dir>/<scope>.<lang>.md`
- **THEN** the slug used for matching against tag pages equals `<dir>` exactly (no separate `Slug` frontmatter field is consulted).

### Requirement: Cross-language tag pages render localised prose with reader-language inference

When a tag has 2 or more `all.<lang>.md` files, the cross-language tag page SHALL render each as a `<section data-lang="<lang>">` block above the auto-generated list and SHALL embed the inline language-inference script reused from the multilingual 404 page (per ADR-0007). With JavaScript disabled, all sections SHALL remain visible. When only one `all.<lang>.md` file exists, its body is rendered directly with no `<section>` wrapper and no inline script. When zero exist, no prose is rendered (list-only).

#### Scenario: 2+ all-scope files render N sections plus inference script
- **WHEN** `content/tag-prose/<slug>/all.en.md` and `content/tag-prose/<slug>/all.pt.md` both exist
- **THEN** `/tag/<slug>/` contains `<section data-lang="en">` and `<section data-lang="pt">` blocks above the list, and a `<script>` block (or partial include resolving to the same script) implementing `navigator.language` matching with default-lang fallback.

#### Scenario: Browser language matches a section
- **WHEN** a reader visits `/tag/<slug>/` with `navigator.language` starting with `pt`
- **THEN** after the inline script executes, only the `<section data-lang="pt">` is visible (others have `hidden` attribute or `display: none`) and `document.documentElement.lang` is `"pt"`.

#### Scenario: Browser language does not match any section
- **WHEN** a reader visits `/tag/<slug>/` with `navigator.language` set to a language with no `all.<lang>.md` file
- **THEN** after the inline script executes, only the `data-default-lang` section is visible.

#### Scenario: JavaScript disabled keeps every section visible
- **WHEN** the same page is rendered to a reader whose browser has JavaScript disabled
- **THEN** every `<section data-lang>` remains visible (the `hidden` attribute is set only by the script).

#### Scenario: Single all-scope file renders no script
- **WHEN** only `content/tag-prose/<slug>/all.en.md` exists (no other `all.<lang>.md` siblings)
- **THEN** `/tag/<slug>/` renders the body directly above the list, with no `<section data-lang>` wrapper and no inline language-inference script.

#### Scenario: No all-scope file renders list-only
- **WHEN** no `all.<lang>.md` file exists for a tag
- **THEN** `/tag/<slug>/` renders the auto-generated list with no prose block above it.

### Requirement: Per-language tag pages render the matching `lang` prose with no script

When a per-language tag page is rendered for `<lang>`, the renderer SHALL look up `content/tag-prose/<slug>/lang.<lang>.md` only. If present, its rendered body is embedded above the list as a single block. If absent, the page is list-only. No `<section>` wrapper, no inline script, no fallback to `all.<lang>.md`.

#### Scenario: Matching lang-scope file renders its body
- **WHEN** `content/tag-prose/<slug>/lang.en.md` exists and `/en/tag/<slug>/` is rendered
- **THEN** the page contains the rendered Markdown body of `lang.en.md` above the list.

#### Scenario: Missing lang-scope file renders list-only
- **WHEN** no `lang.<lang>.md` file exists for the page's lang
- **THEN** the page is rendered list-only (no prose block, no fallback to `all.<lang>.md`).

#### Scenario: No inference script on per-language tag pages
- **WHEN** any per-language tag page is rendered
- **THEN** its HTML contains no inline `<script>` block for language inference (the page's lang is unambiguous from the URL).

### Requirement: The 404 inference script is shared with cross-language tag pages via a Jinja partial

The inline language-inference script previously embedded directly in `themes/garden/templates/404.html` SHALL live in a partial at `themes/garden/templates/_lang_inference_script.html` and SHALL be `{% include %}`'d from both `404.html` and `tag_group_index.html`.

#### Scenario: Partial template exists
- **WHEN** `themes/garden/templates/_lang_inference_script.html` is inspected
- **THEN** it contains the language-inference `<script>` block (stage 1 URL prefix → stage 2 `navigator.language` → fallback `data-default-lang`).

#### Scenario: 404.html includes the partial
- **WHEN** `themes/garden/templates/404.html` is inspected
- **THEN** it `{% include %}`s `_lang_inference_script.html` and does NOT carry the inline script verbatim.

#### Scenario: Cross-language tag template includes the partial
- **WHEN** `themes/garden/templates/tag_group_index.html` is inspected
- **THEN** it `{% include %}`s `_lang_inference_script.html` whenever 2 or more `all.<lang>.md` sections are rendered above the list.

### Requirement: Drafts are visible as full articles in development builds

In development builds (`make dev`, or any build using `pelicanconf.py` directly), every article with `Status: draft` SHALL appear as if it had `Status: published`: emitted at `/<slug>/`, listed on the homepage, listed on its language index, listed on its tag pages, and grouped with its translations. This behaviour is gated by `DRAFTS_AS_PUBLISHED = True` in `pelicanconf.py`.

#### Scenario: `DRAFTS_AS_PUBLISHED` is True in dev config
- **WHEN** `pelicanconf.py` is inspected
- **THEN** `DRAFTS_AS_PUBLISHED == True`.

#### Scenario: Draft article emits at the terminal URL
- **WHEN** an article with `Status: draft` is built via `pelicanconf.py`
- **THEN** it emits at `output/<slug>/index.html` (the same terminal-form URL it would use as `published`), not at `output/drafts/<slug>.html`.

#### Scenario: Draft article appears on the homepage
- **WHEN** an article with `Status: draft` is built via `pelicanconf.py` and the homepage is rendered
- **THEN** the article (or its translation group) is listed on `/` exactly as a published article would be.

#### Scenario: Draft article appears on tag pages
- **WHEN** an article with `Status: draft` carries `Tags: [<tag>]` and is built via `pelicanconf.py`
- **THEN** it appears on `/tag/<slug>/` (via its group) and on `/<article.lang>/tag/<slug>/` (directly).

#### Scenario: Draft article participates in translation grouping
- **WHEN** a draft article shares a `Translation_key` with a published translation
- **THEN** both appear in each other's `article.translation_group` and in the same `HOMEPAGE_GROUPS` entry.

### Requirement: Drafts are entirely absent from production builds

In production builds (`make build`, using `publishconf.py`), articles with `Status: draft` SHALL produce no output: no HTML files, no entries in any listing, no inclusion in any feed.

#### Scenario: `DRAFTS_AS_PUBLISHED` is False in prod config
- **WHEN** `publishconf.py` is inspected
- **THEN** `DRAFTS_AS_PUBLISHED == False` (overriding the dev default).

#### Scenario: Draft URL settings are blank in prod config
- **WHEN** `publishconf.py` is inspected
- **THEN** `DRAFT_URL == ""`, `DRAFT_SAVE_AS == ""`, `DRAFT_LANG_URL == ""`, and `DRAFT_LANG_SAVE_AS == ""`.

#### Scenario: No draft HTML is emitted
- **WHEN** `make build` runs against a tree containing at least one `Status: draft` article
- **THEN** no file under `output/` corresponds to that article (no `output/<slug>/index.html`, no `output/drafts/<slug>.html`, nothing).

#### Scenario: Drafts are absent from tag pages and feeds in prod
- **WHEN** the same draft article carries `Tags: [<tag>]`
- **THEN** `output/tag/<slug>/index.html` does not list it, `output/<lang>/tag/<slug>/index.html` does not list it, and no feed file references it.

### Requirement: Hidden articles emit at the terminal `/<slug>/` URL form

Articles with `Status: hidden` SHALL emit at `/<slug>/` (matching ADR-0004's terminal-form rule) for both default-language and non-default-language articles, while continuing to be excluded from listings and feeds (Pelican's default behaviour for `hidden_articles`).

#### Scenario: Hidden article URL settings use terminal form
- **WHEN** `pelicanconf.py` is inspected
- **THEN** `HIDDEN_ARTICLE_URL == "{slug}/"`, `HIDDEN_ARTICLE_SAVE_AS == "{slug}/index.html"`, `HIDDEN_ARTICLE_LANG_URL == "{slug}/"`, and `HIDDEN_ARTICLE_LANG_SAVE_AS == "{slug}/index.html"`.

#### Scenario: Hidden article emits at terminal form
- **WHEN** an article with `Status: hidden` is built (either default-lang or non-default-lang)
- **THEN** it emits at `output/<slug>/index.html`, not `output/hidden/<slug>.html` and not `output/<slug>-<lang>.html`.

#### Scenario: Hidden article is absent from listings
- **WHEN** the homepage, language indexes, tag pages, all-tags indexes, or any feed is rendered
- **THEN** none of them list a `Status: hidden` article.

### Requirement: The `tag_pages` plugin consumes `i18n_grouping`'s context, not its own grouping pass

The `tag_pages` plugin SHALL read translation groups, the language union, and homepage-group data from the article generator's context as populated by `i18n_grouping` (`TRANSLATION_GROUPS`, `SITE_LANGS`, `HOMEPAGE_GROUPS`), rather than re-walking articles to compute these structures itself.

#### Scenario: Plugin reads SITE_LANGS from context
- **WHEN** `plugins/tag_pages/__init__.py` is inspected
- **THEN** the per-language tag page generator reads its language list from `generator.context["SITE_LANGS"]` (or equivalent), not by walking articles directly.

#### Scenario: Plugin reads TRANSLATION_GROUPS from context
- **WHEN** the cross-language tag page generator iterates groups
- **THEN** it reads from `generator.context["TRANSLATION_GROUPS"]` (or `HOMEPAGE_GROUPS`) populated by `i18n_grouping`, not by re-grouping articles.

#### Scenario: Plugin order in PLUGINS list
- **WHEN** `pelicanconf.py` is inspected
- **THEN** `i18n_grouping` appears in the `PLUGINS` list before `tag_pages`.

### Requirement: `dev_drafts` runs before `i18n_grouping` so promoted drafts join translation groups

The `dev_drafts` plugin SHALL connect to a signal that fires before `article_generator_finalized`, mutating `generator.drafts` and `generator.drafts_translations` into `generator.articles` and `generator.translations` (and updating each promoted article's `status` attribute) before `i18n_grouping` builds its `TRANSLATION_GROUPS`.

#### Scenario: Dev_drafts hooks a pre-finalised signal
- **WHEN** `plugins/dev_drafts/__init__.py` is inspected
- **THEN** the plugin's `register()` connects its handler to `article_generator_pretaxonomy` (or another signal that fires before `article_generator_finalized`).

#### Scenario: Promoted draft is in articles by the time grouping runs
- **WHEN** a `Status: draft` article is processed under `DRAFTS_AS_PUBLISHED = True`
- **THEN** by the time `i18n_grouping`'s grouping handler runs, the article appears in `generator.articles` (not `generator.drafts`) and its `status` attribute is `"published"`.

#### Scenario: Plugin is a no-op when DRAFTS_AS_PUBLISHED is False
- **WHEN** the plugin runs with `DRAFTS_AS_PUBLISHED = False` (or unset)
- **THEN** `generator.drafts` is unchanged, `generator.articles` does not gain any draft entries, and no article's `status` is mutated.

### Requirement: ADR-0008 records the dev-drafts toggle decision

A new ADR SHALL be added at `openspec/decisions/0008-dev-drafts-promotion.md` recording the decision to gate dev-drafts promotion on a settings flag rather than an env var or a conditional plugin registration.

#### Scenario: ADR-0008 exists and is Accepted
- **WHEN** `openspec/decisions/0008-dev-drafts-promotion.md` is inspected
- **THEN** its `## Status` line reads `Accepted` with the decision date, and its body includes Context, Decision, and Consequences sections naming both the chosen mechanism (settings flag toggled in `publishconf.py`) and the rejected alternatives (env var, two-plugin variant, template-level handling).

#### Scenario: ADR-0008 is referenced from the decisions README
- **WHEN** `openspec/decisions/README.md` is inspected
- **THEN** its `## Index` section lists ADR-0008 alongside the existing ADRs.

### Requirement: ADR-0009 records the tag-prose content-type decision

A new ADR SHALL be added at `openspec/decisions/0009-tag-prose-content-type.md` recording the decision to introduce tag-prose as a third content type with its own directory tree and schema, rather than reusing the page schema with a marker field.

#### Scenario: ADR-0009 exists and is Accepted
- **WHEN** `openspec/decisions/0009-tag-prose-content-type.md` is inspected
- **THEN** its `## Status` line reads `Accepted` with the decision date, and its body includes Context, Decision, and Consequences sections naming both the chosen approach (third content type at `content/tag-prose/<slug>/<scope>.<lang>.md`) and the rejected alternatives (page-with-marker, embed-in-first-article, parallel-dirs layout, filename-infix layout).

#### Scenario: ADR-0009 is referenced from the decisions README
- **WHEN** `openspec/decisions/README.md` is inspected
- **THEN** its `## Index` section lists ADR-0009 alongside ADR-0008.
