## MODIFIED Requirements

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
