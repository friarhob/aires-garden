# i18n-rendering Specification

## Purpose
TBD - created by archiving change add-i18n-rendering. Update Purpose after archive.
## Requirements
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

### Requirement: Non-article pages render a per-page lang-links navigation bar

Every non-article page kind (cross-language index, per-language index, cross-language tag index, per-language tag index, cross-language all-tags list, per-language all-tags list) SHALL render a single lang-links bar. Each entry is a plain navigation link to the equivalent page in another language scope; clicking it loads that page (it does NOT call into the header preference-toggle mechanism). Article pages SHALL NOT render this bar — they continue to use the existing "Available in" line.

#### Scenario: Cross-language home renders the bar
- **WHEN** the cross-language home `/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar listing one "All" entry (marked current) and one entry per language in `SITE_LANGS`. Each per-language entry is an `<a>` element whose `href` is the language home (`/<lang>/`).

#### Scenario: Per-language home renders the bar with current scope marked
- **WHEN** a per-language home `/<lang>/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar with an "All" entry whose `href` is `/`, and one entry per language in `SITE_LANGS` whose `href` is `/<other>/`. The entry for `<lang>` carries a "current" indicator (e.g. `class="page-lang-current"`); no other entry does.

#### Scenario: Cross-language tag page renders the bar
- **WHEN** a cross-language tag index `/tag/<slug>/` is rendered and two or more languages have at least one published post tagged `<slug>`
- **THEN** the page contains a lang-links bar listing entries only for those languages (`tag_langs`). Each per-language entry's `href` is `/<lang>/tag/<slug>/`.

#### Scenario: Per-language tag page renders the bar with current scope marked
- **WHEN** a per-language tag index `/<lang>/tag/<slug>/` is rendered and two or more languages have at least one published post tagged `<slug>`
- **THEN** the page contains a lang-links bar with an "All" entry whose `href` is `/tag/<slug>/`, and one entry per language in `tag_langs` (excluding `<lang>` itself) whose `href` is `/<other>/tag/<slug>/`. The entry for `<lang>` carries the "current" indicator.

#### Scenario: Tag page bar is hidden when the tag exists in only one language
- **WHEN** a tag index page is rendered and only one language has posts tagged `<slug>`
- **THEN** no lang-links bar is rendered for that tag page (a single-language bar would be degenerate).

#### Scenario: Cross-language all-tags list renders the bar
- **WHEN** the cross-language all-tags list `/tags/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar with an "All" entry (marked current) and one entry per language in `SITE_LANGS`, each `href` being `/<lang>/tags/`.

#### Scenario: Per-language all-tags list renders the bar with current scope marked
- **WHEN** a per-language all-tags list `/<lang>/tags/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar with an "All" entry whose `href` is `/tags/`, and one entry per language in `SITE_LANGS` whose `href` is `/<other>/tags/`. The entry for `<lang>` carries the "current" indicator.

#### Scenario: Bar is hidden on mono-lingual sites
- **WHEN** any non-article page is rendered on a site where `SITE_LANGS | length < 2`
- **THEN** no lang-links bar is rendered (the cross-language and the only per-language scopes would point at equivalent content, making the bar degenerate).

#### Scenario: Article pages do not render the bar
- **WHEN** an article page is rendered
- **THEN** the page does not render the per-page lang-links bar; the existing "Available in" line continues to be the article's translation-navigation surface.

#### Scenario: Non-tag pages list all `SITE_LANGS` unconditionally
- **WHEN** a non-article, non-tag page (home, per-language home, tags-list) renders the bar
- **THEN** the per-language entries are exactly the languages in `SITE_LANGS` (sorted alphabetically). Links pointing at non-existent variants resolve via the multilingual 404 page's language inference.

#### Scenario: Bar position is consistent across page kinds
- **WHEN** a non-article page renders the bar
- **THEN** the bar appears between the page's `<h1>` heading and the page's primary list/prose content (mirroring where article pages place their "Available in" line).

#### Scenario: Bar entries are independent of the header lang preference toggle
- **WHEN** a reader clicks any entry in the lang-links bar
- **THEN** the browser performs a normal navigation to the entry's `href`. The click does NOT update `localStorage["garden-lang"]` and does NOT toggle `<section data-lang>` visibility on the source page. (Section-switching and preference-setting remain the responsibility of the header lang popover.)

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

The inference chain SHALL be ordered as follows, with the first matching stage winning:
1. `/<lang>/` prefix in the URL path
2. Stored language preference (`document.documentElement.dataset.prefLang`, populated from `localStorage` by the inline loader in `base.html`)
3. `navigator.language`'s 2-letter prefix
4. The document's `data-default-lang` attribute (final fallback)

#### Scenario: `/<lang>/` prefix prioritises that language
- **WHEN** the 404 is loaded for any path starting with `/<lang>/` (where `<lang>` is one of the site's languages)
- **THEN** only the section with `data-lang="<lang>"` is visible, and the document's `<html lang>` is set to `<lang>`. Stage 1 wins regardless of any stored preference.

#### Scenario: Stored language preference is consulted when the URL has no lang prefix
- **WHEN** the 404 is loaded for a path that does not start with `/<lang>/`, and `data-pref-lang` on `<html>` matches one of the site's languages
- **THEN** the section matching `data-pref-lang` is visible, and the document's `<html lang>` is set to it. Stage 2 beats `navigator.language` and the default fallback.

#### Scenario: Browser language preference is consulted when no URL prefix and no stored preference
- **WHEN** the 404 is loaded for a path with no `/<lang>/` prefix, no `data-pref-lang` is set, and `navigator.language`'s 2-letter prefix matches one of the site's languages
- **THEN** the section matching that language is visible, and the document's `<html lang>` is set to it.

#### Scenario: Unknown paths fall back to the default language
- **WHEN** none of stages 1–3 produce a match
- **THEN** the section matching the document's `data-default-lang` attribute is visible.

#### Scenario: With JS disabled, all sections remain visible
- **WHEN** the 404 is loaded with JavaScript disabled in the browser
- **THEN** every `<section data-lang>` element is rendered visible in the page (graceful degradation per ADR-0007 bar 2).

#### Scenario: No build-time per-slug payload is embedded
- **WHEN** `output/404.html` is inspected
- **THEN** it does not contain a slug-to-language map or any other per-article structure whose size grows with post count; the inference script relies only on the URL path, the site's language list, the stored preference attribute, and `navigator.language`.

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

