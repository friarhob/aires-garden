## ADDED Requirements

### Requirement: Articles are grouped by `Translation_key` and the group is exposed to templates

A Pelican plugin SHALL walk all articles and translations at build time, group them by `Translation_key`, and attach the resulting group to each article so templates can render translation-aware UI without re-doing the join.

#### Scenario: Group attribute exists on every article
- **WHEN** any article object is rendered by a Jinja template
- **THEN** the article has an attribute (e.g. `article.translation_group`) that is a list of all articles sharing its `Translation_key`, including itself.

#### Scenario: A single-language post has a one-element group
- **WHEN** an article exists in only one language (e.g. the existing PT-only `ola-jardim`)
- **THEN** its group contains exactly one element — itself — and the rest of the rendering pipeline treats it correctly (it appears on the homepage and in the relevant per-language index).

#### Scenario: A multi-language post group contains every translation
- **WHEN** a post has been authored in two or more languages (sibling files in the same `<translation_key>/` directory)
- **THEN** every article's group lists every translation, regardless of which file is the entry point being rendered.

### Requirement: All language versions of an article live at `/<slug>/`

Pelican's URL settings SHALL produce the same terminal `<slug>/index.html` form for every article regardless of `Lang`. No language-suffixed URL form is emitted.

#### Scenario: Default-language article URL
- **WHEN** an article with `Lang` matching `DEFAULT_LANG` is built
- **THEN** it is written to `output/<slug>/index.html` and its `article.url` is `<slug>/`.

#### Scenario: Non-default-language article URL
- **WHEN** an article with a `Lang` other than `DEFAULT_LANG` is built (e.g. the PT post `ola-jardim`)
- **THEN** it is written to `output/<slug>/index.html` and its `article.url` is `<slug>/`. No `<slug>-<lang>.html` artefact is produced.

#### Scenario: Different translations don't collide
- **WHEN** two translations of one post (e.g. `ola-jardim` PT, `hello-garden` EN) are built
- **THEN** they live at distinct paths (`output/ola-jardim/index.html` and `output/hello-garden/index.html`) because their localised slugs differ per ADR-0004.

### Requirement: A scope switcher appears in the site header on every page

The site header SHALL render a scope switcher containing an "All" entry plus one entry per language found on the site. The switcher's behaviour is page-context-aware.

#### Scenario: "All" entry is always present and links to `/`
- **WHEN** any page (post, aggregate index, per-language index, 404) is rendered
- **THEN** the switcher contains an "All" entry that links to `/`, regardless of page type.

#### Scenario: "All" entry is highlighted on the aggregate homepage only
- **WHEN** the aggregate homepage `/` is rendered
- **THEN** the "All" entry carries a "current" indicator (e.g. `class="lang-current"`) and no per-language entry is highlighted.

#### Scenario: Per-language entries on post pages link to translations
- **WHEN** a post page is rendered
- **THEN** for each lang in the site's union of languages: if the post has a sibling translation in that lang, the entry is an enabled link to that sibling's URL; otherwise the entry is rendered in a visibly disabled state.

#### Scenario: Per-language entries on non-post pages link to per-language indexes
- **WHEN** any non-post page is rendered (aggregate `/`, per-lang `/<lang>/`, the 404)
- **THEN** every per-language entry is an enabled link to its `/<lang>/` index. No entry is disabled.

#### Scenario: Current language is highlighted on per-language indexes and posts
- **WHEN** a per-language index `/<lang>/` is rendered, OR a post page is rendered
- **THEN** the entry for that language carries the "current" indicator.

#### Scenario: Lang list is computed dynamically from content
- **WHEN** the switcher is rendered on any page
- **THEN** the list of per-language entries is the union of `Lang` values across all articles on the site, sorted alphabetically. No static `KNOWN_LANGS` setting is consulted.

### Requirement: Each post page shows an "Available in" line listing existing translations

Post pages SHALL display the list of languages this post is available in, with each entry as a link to that translation. Languages the post does not have are not listed (in contrast to the switcher, which shows them disabled).

#### Scenario: Multi-language post lists every translation
- **WHEN** a post with two or more translations is rendered
- **THEN** the post body includes an "Available in" line listing each language with a link to its translation, sorted alphabetically by language code.

#### Scenario: Single-language post hides the line entirely
- **WHEN** a post has only one language version
- **THEN** no "Available in" line is rendered (it would be a degenerate "Available in: this only").

### Requirement: The aggregate homepage `/` shows each post once

The homepage SHALL deduplicate articles by `Translation_key`, displaying one entry per group. Each entry links to a deterministically-chosen translation and surfaces which languages the post is available in.

#### Scenario: Each post appears exactly once on the homepage
- **WHEN** the homepage is rendered against a content tree containing multi-language and single-language posts
- **THEN** every distinct `Translation_key` appears exactly once. No post is duplicated; no post is missing.

#### Scenario: A homepage entry links to the default-language translation when available
- **WHEN** a homepage entry is rendered for a group that has a `DEFAULT_LANG` translation
- **THEN** the entry's link target is the URL of the `DEFAULT_LANG` article in the group.

#### Scenario: A homepage entry links to the alphabetically-first translation when no default exists
- **WHEN** a homepage entry is rendered for a group with no `DEFAULT_LANG` translation (e.g. PT-only `ola-jardim` while `DEFAULT_LANG = "en"`)
- **THEN** the entry's link target is the URL of the article whose `Lang` is alphabetically first in the group.

#### Scenario: Each homepage entry surfaces its available languages
- **WHEN** a homepage entry is rendered
- **THEN** the entry displays the list of languages the post is available in (e.g. as small badges or text after the title).

### Requirement: A per-language index page exists for every language found in content

For each `Lang` value in the union across all articles, the build SHALL produce an index page at `/<lang>/index.html` listing only articles with that `Lang`.

#### Scenario: One index per existing language
- **WHEN** the site contains articles with `Lang` values `en` and `pt`
- **THEN** the build produces `output/en/index.html` and `output/pt/index.html` (and no others).

#### Scenario: Per-language index lists matching articles only
- **WHEN** `output/<lang>/index.html` is inspected
- **THEN** every link on the page is to an article whose `Lang == <lang>`. No articles in other languages are listed.

#### Scenario: Per-language index sorts by date descending
- **WHEN** `output/<lang>/index.html` lists multiple articles
- **THEN** they appear in descending order by their `Date` frontmatter value.

#### Scenario: Adding a new language auto-creates its index
- **WHEN** a French post is added to the content tree (any post with `Lang: fr`)
- **THEN** the next build produces `output/fr/index.html` without any configuration edit.

### Requirement: Per-language Atom feeds are emitted alongside the aggregate feed

Pelican SHALL emit one Atom feed per language found in content at `/feeds/<lang>.atom.xml`, in addition to the aggregate `feeds/all.atom.xml` already produced by `publishconf.py`.

#### Scenario: Aggregate feed is preserved
- **WHEN** the production build runs
- **THEN** `output/feeds/all.atom.xml` exists and lists articles in all languages.

#### Scenario: Per-language feed exists for each language
- **WHEN** the site contains articles in `en` and `pt`
- **THEN** `output/feeds/en.atom.xml` and `output/feeds/pt.atom.xml` exist.

#### Scenario: Per-language feed lists matching articles only
- **WHEN** `output/feeds/<lang>.atom.xml` is parsed
- **THEN** every entry's `<language>` (or equivalent) matches `<lang>`; no entries from other languages are present.

### Requirement: A multilingual 404 plugin produces one combined `output/404.html`

A separate Pelican plugin (distinct from the article-grouping plugin) SHALL read per-language 404 source files, render each, and write a single combined output file containing every language as a section, plus the inference machinery described below.

#### Scenario: Per-language 404 source files exist
- **WHEN** `content/pages/` is inspected
- **THEN** files matching `404.<lang>.md` exist for at least the default language and the other languages the site uses (initially `404.en.md` and `404.pt.md`).

#### Scenario: Combined 404 output contains all language sections
- **WHEN** `output/404.html` is inspected after a build
- **THEN** for every `404.<lang>.md` source file, the output contains a `<section data-lang="<lang>">` element with that file's rendered HTML body.

#### Scenario: Combined 404 carries the default-lang attribute
- **WHEN** `output/404.html` is inspected
- **THEN** the document carries an attribute identifying the site's default language (e.g. `<html data-default-lang="en">` or equivalent), so the JS prioritisation has a fallback target.

#### Scenario: Plugin is registered separately from the article-grouping plugin
- **WHEN** `pelicanconf.py` is inspected
- **THEN** `PLUGINS` contains both `i18n_grouping` and `multilingual_404` as distinct entries.

### Requirement: The 404 page infers the reader's language from the URL

The 404 page SHALL include inline JavaScript that, on load, inspects `window.location.pathname` and prioritises the matching language section by hiding the others. With JS disabled, all sections remain visible — the page degrades gracefully per [ADR-0007](../../decisions/0007-small-clientside-js.md) bar 2.

#### Scenario: `/<lang>/` prefix prioritises that language
- **WHEN** the 404 is loaded for any path starting with `/<lang>/` (where `<lang>` is one of the site's languages)
- **THEN** only the section with `data-lang="<lang>"` is visible, and the document's `<html lang>` is set to `<lang>`.

#### Scenario: A known slug prioritises its authored language
- **WHEN** the 404 is loaded for a path matching `/<slug>/` where `<slug>` is in the build-time slug-to-lang map
- **THEN** the section matching the mapped lang is visible, and the document's `<html lang>` is set to that lang.

#### Scenario: Unknown paths fall back to the default language
- **WHEN** the 404 is loaded for a path that has no `/<lang>/` prefix and whose slug is not in the map
- **THEN** the section matching the document's `data-default-lang` attribute is visible.

#### Scenario: With JS disabled, all sections remain visible
- **WHEN** the 404 is loaded with JavaScript disabled in the browser
- **THEN** every `<section data-lang>` element is rendered visible in the page (graceful degradation per ADR-0007 bar 2).

#### Scenario: Slug-to-lang map is generated at build time
- **WHEN** `output/404.html` is inspected
- **THEN** it contains a build-time-emitted JSON object (in a `<script type="application/json">` block or as a JS literal) listing every article slug and its `Lang`. The object is consumed by the inline inference script.

#### Scenario: Inference script is inline and small
- **WHEN** `output/404.html` is inspected
- **THEN** the inference script lives in an inline `<script>` block (no external `.js` file is loaded), is under 50 lines, and does not load any external resources at runtime — per ADR-0007 bar 3.

### Requirement: ADR-0007 is recorded and indexed

The decision log SHALL include ADR-0007 documenting the small-client-side-JS stance that the 404 mechanics depend on.

#### Scenario: ADR-0007 exists and is Accepted
- **WHEN** `openspec/decisions/0007-small-clientside-js.md` is inspected
- **THEN** its `## Status` line reads `Accepted` with the decision date, and its body includes Context, Decision, and Consequences sections naming the three bars (static-host necessity, graceful degradation, inline-and-small).

#### Scenario: ADR-0007 is referenced from the spec
- **WHEN** the multilingual 404 requirements are read
- **THEN** they link to `openspec/decisions/0007-small-clientside-js.md` so future readers can follow the trail.

#### Scenario: ADR-0007 appears in the README index
- **WHEN** `openspec/decisions/README.md` is inspected
- **THEN** its `## Index` section lists ADR-0007 alongside the existing ADRs.
