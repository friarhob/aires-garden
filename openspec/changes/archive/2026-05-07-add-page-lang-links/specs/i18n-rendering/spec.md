## REMOVED Requirements

### Requirement: A scope switcher appears in the site header on every page

**Reason**: The header scope switcher's behaviour was inconsistent with reader expectations: per-language entries always navigated to the language home (`/<lang>/`) rather than the equivalent of the current page in that scope. The `add-user-preferences` change introduced a header language toggle that handles "set my preferred language" without navigation; the navigation role is now better served by per-page lang links (added below) that take the reader to the equivalent page in another scope.

**Migration**: The header `<nav class="scope-switcher">` block has been deleted from `base.html` and replaced with the `.prefs` controls. Per-page navigation between language scopes is provided by the new "Equivalent in other scopes" lang-links bar rendered on each non-article page (see ADDED Requirements below). The header lang toggle continues to set the preferred language and switch `<section data-lang>` content where present, but does not navigate.

## ADDED Requirements

### Requirement: Non-article pages render a per-page lang-links navigation bar

Every non-article page kind (cross-language index, per-language index, cross-language tag index, per-language tag index, cross-language all-tags list, per-language all-tags list) SHALL render a single lang-links bar. Each entry is a plain navigation link to the equivalent page in another language scope; clicking it loads that page (it does NOT call into the header preference-toggle mechanism). Article pages SHALL NOT render this bar — they continue to use the existing "Available in" line.

#### Scenario: Cross-language home renders the bar
- **WHEN** the cross-language home `/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar listing one "All" entry (marked current) and one entry per language in `SITE_LANGS`. Each per-language entry is an `<a>` element whose `href` is the language home (`/<lang>/`).

#### Scenario: Per-language home renders the bar with current scope marked
- **WHEN** a per-language home `/<lang>/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar with an "All" entry whose `href` is `/`, and one entry per language in `SITE_LANGS` whose `href` is `/<other>/`. The entry for `<lang>` carries a "current" indicator (e.g. `class="page-lang-current"`); no other entry does.

#### Scenario: Cross-language tag page renders the bar
- **WHEN** a cross-language tag index `/tag/<slug>/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar listing an "All" entry (marked current) and one entry per language in `SITE_LANGS`. Each per-language entry's `href` is `/<lang>/tag/<slug>/`.

#### Scenario: Per-language tag page renders the bar with current scope marked
- **WHEN** a per-language tag index `/<lang>/tag/<slug>/` is rendered with `SITE_LANGS` ≥ 2
- **THEN** the page contains a lang-links bar with an "All" entry whose `href` is `/tag/<slug>/`, and one entry per language in `SITE_LANGS` whose `href` is `/<other>/tag/<slug>/`. The entry for `<lang>` carries the "current" indicator.

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

#### Scenario: All `SITE_LANGS` are listed unconditionally
- **WHEN** a non-article page renders the bar
- **THEN** the per-language entries are exactly the languages in `SITE_LANGS` (sorted alphabetically), regardless of whether the equivalent page exists for every language. Links pointing at non-existent variants resolve via the multilingual 404 page's language inference.

#### Scenario: Bar position is consistent across page kinds
- **WHEN** a non-article page renders the bar
- **THEN** the bar appears between the page's `<h1>` heading and the page's primary list/prose content (mirroring where article pages place their "Available in" line).

#### Scenario: Bar entries are independent of the header lang preference toggle
- **WHEN** a reader clicks any entry in the lang-links bar
- **THEN** the browser performs a normal navigation to the entry's `href`. The click does NOT update `localStorage["garden-lang"]` and does NOT toggle `<section data-lang>` visibility on the source page. (Section-switching and preference-setting remain the responsibility of the header lang popover.)
