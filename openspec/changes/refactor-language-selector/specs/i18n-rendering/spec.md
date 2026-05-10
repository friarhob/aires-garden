## ADDED Requirements

### Requirement: The header language picker is translation-aware on pages with an explicit canonical language

The header language picker SHALL behave as a navigator on every page whose canonical language is determined at build time. Clicking a popover entry SHALL cause the browser to follow the entry's `href` to the equivalent page in the chosen language, and SHALL also write the chosen language to `localStorage["garden-lang"]` and `document.documentElement.dataset.prefLang` before navigation. Pages whose canonical language is not determined at build time (the multilingual 404 and the cross-language tag page when its tag-prose is rendered as multiple `<section data-lang>` blocks) retain section-toggle behaviour: the picker lists every entry in `SITE_LANGS`, clicking toggles section visibility and writes the preference, and no navigation is performed.

#### Scenario: Mode is selected by template-published `header_lang_links`

- **WHEN** the header partial in `base.html` renders
- **THEN** it inspects the Jinja variable `header_lang_links`. If `header_lang_links` is defined and non-empty the picker renders in navigation mode (one `<a href>` per entry); otherwise the picker renders in section-toggle mode over `SITE_LANGS` (one `<button>` per entry — the existing behaviour).

#### Scenario: Article picker offers only existing translations

- **WHEN** the reader is on an article page (e.g. `/hello-garden/`) whose `article.translation_group` includes a peer in PT (`/ola-jardim/`)
- **THEN** the popover lists exactly one alternative entry — `PT`, with `href="{{ SITEURL }}/{{ pt_peer.url }}"`. The current-language entry (EN) is not in the popover; the trigger button shows `EN`.

#### Scenario: Single-language article shows an empty popover

- **WHEN** the reader is on a single-language article (e.g. `/ola-jardim/` when no EN translation exists)
- **THEN** `header_lang_links` is empty. The trigger button still renders showing `PT`; the popover has no entries and never opens.

#### Scenario: Per-language home picker offers other languages

- **WHEN** the reader is on `/en/` with `SITE_LANGS = ["en", "pt"]`
- **THEN** the popover lists `PT` with `href="{{ SITEURL }}/pt/"`. The trigger shows `EN`.

#### Scenario: Per-language tag page picker offers other tag-languages

- **WHEN** the reader is on `/en/tag/poetry/` and `tag_langs = ["en", "pt"]`
- **THEN** the popover lists `PT` with `href="{{ SITEURL }}/pt/tag/poetry/"`. Languages outside `tag_langs` are NOT listed even if they appear in `SITE_LANGS`.

#### Scenario: Cross-language tag page with single-lang prose navigates to per-lang tag indexes

- **WHEN** the reader is on `/tag/poetry/` and `all_prose | length < 2`
- **THEN** `header_lang_links` is set; the popover lists each entry of `tag_langs` with `href="{{ SITEURL }}/<lang>/tag/poetry/"`.

#### Scenario: Cross-language tag page with multi-lang prose retains section-toggle behaviour

- **WHEN** the reader is on `/tag/poetry/` and `all_prose | length >= 2`
- **THEN** `header_lang_links` is NOT set. The picker renders in section-toggle mode over `SITE_LANGS`; clicking toggles which `<section data-lang>` is visible (existing behaviour) and writes the preference; no navigation is performed.

#### Scenario: Multilingual 404 retains section-toggle behaviour

- **WHEN** the reader is on `output/404.html`
- **THEN** `header_lang_links` is NOT set. The picker renders in section-toggle mode and clicking toggles which `<section data-lang>` is visible — no navigation, consistent with the page having no single canonical language.

#### Scenario: Click writes the preference before navigation

- **WHEN** the reader clicks an `<a>` entry in the navigation-mode popover
- **THEN** the popover script writes `localStorage.setItem('garden-lang', <chosen-lang>)` and updates `document.documentElement.dataset.prefLang` synchronously before the browser follows the `href`. If the click event is intercepted (e.g. middle-click, modifier keys), the script SHALL NOT prevent the browser's default behaviour.

#### Scenario: Click works without JavaScript

- **WHEN** the reader has JavaScript disabled and clicks an entry in the navigation-mode popover
- **THEN** the browser follows the `href` directly. The preference is not written (no JS to write it), but the navigation still works — graceful degradation per ADR-0007 bar 2.

---

### Requirement: Page templates publish `header_lang_links` per page kind

Each page template whose canonical language is known at build time SHALL publish a Jinja variable `header_lang_links` — a mapping `{lang_code: target_url, ...}` — listing the languages the picker should offer for that page, with their navigation targets. Templates whose canonical language is not known at build time SHALL NOT publish `header_lang_links`. The mapping SHALL exclude the current page's own language.

#### Scenario: `article.html` publishes from `article.translation_group`

- **WHEN** `article.html` renders an article
- **THEN** `header_lang_links` contains one entry per item in `article.translation_group` whose `lang != article.lang`, mapping `lang` to `{{ SITEURL }}/{{ t.url }}`.

#### Scenario: `page.html` publishes from `page.translations`

- **WHEN** `page.html` renders a page
- **THEN** `header_lang_links` contains one entry per item in `page.translations`, mapping `lang` to `{{ SITEURL }}/{{ t.url }}`.

#### Scenario: `index.html` publishes per-language home links for every `SITE_LANGS` entry

- **WHEN** `index.html` (the cross-language home `/`) renders with `SITE_LANGS | length >= 2`
- **THEN** `header_lang_links` contains one entry per language in `SITE_LANGS`, mapping `lang` to `{{ SITEURL }}/<lang>/`.

#### Scenario: `lang_index.html` publishes per-language home links for the other languages

- **WHEN** `lang_index.html` renders for `page_lang`
- **THEN** `header_lang_links` contains one entry per language in `SITE_LANGS` other than `page_lang`, mapping `lang` to `{{ SITEURL }}/<lang>/`.

#### Scenario: `tags_list.html` publishes tags-list links

- **WHEN** `tags_list.html` renders the cross-language all-tags list `/tags/` with `SITE_LANGS | length >= 2`
- **THEN** `header_lang_links` contains one entry per language in `SITE_LANGS`, mapping `lang` to `{{ SITEURL }}/<lang>/tags/`.
- **WHEN** `tags_list.html` renders a per-language all-tags list `/<lang>/tags/`
- **THEN** `header_lang_links` contains one entry per language in `SITE_LANGS` other than the current `page_lang`, mapping `lang` to `{{ SITEURL }}/<lang>/tags/`.

#### Scenario: `tag_lang_index.html` publishes per-tag-lang links over `tag_langs`

- **WHEN** `tag_lang_index.html` renders `/<lang>/tag/<tag_slug>/`
- **THEN** `header_lang_links` contains one entry per language in `tag_langs` other than `page_lang`, mapping `lang` to `{{ SITEURL }}/<lang>/tag/<tag_slug>/`. Languages outside `tag_langs` SHALL NOT appear.

#### Scenario: `tag_group_index.html` switches modes based on prose count

- **WHEN** `tag_group_index.html` renders `/tag/<tag_slug>/` with `all_prose | length < 2`
- **THEN** `header_lang_links` is set with one entry per language in `tag_langs`, mapping `lang` to `{{ SITEURL }}/<lang>/tag/<tag_slug>/`.
- **WHEN** `tag_group_index.html` renders `/tag/<tag_slug>/` with `all_prose | length >= 2`
- **THEN** `header_lang_links` is NOT set (section-toggle mode wins because the prose itself splits across language sections).

#### Scenario: `404.html` does not publish `header_lang_links`

- **WHEN** `404.html` renders
- **THEN** `header_lang_links` is NOT set. The picker stays in section-toggle mode.

---

## MODIFIED Requirements

### Requirement: Non-article pages render a per-page lang-links navigation bar

Every non-article page kind (cross-language index, per-language index, cross-language tag index, per-language tag index, cross-language all-tags list, per-language all-tags list) SHALL render a single lang-links bar. Each entry is a plain navigation link to the equivalent page in another language scope; clicking it loads that page (it does NOT call into the header preference-write mechanism, although the header picker itself may also offer the same navigation in its popover — see the translation-aware-picker requirement). Article pages SHALL NOT render this bar — they continue to use the existing "Available in" line.

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

#### Scenario: Bar entries do not write the language preference

- **WHEN** a reader clicks any entry in the lang-links bar
- **THEN** the browser performs a normal navigation to the entry's `href`. The click does NOT update `localStorage["garden-lang"]` and does NOT toggle `<section data-lang>` visibility on the source page. The header lang picker is the single surface that writes the preference; the bar is purely navigational.

#### Scenario: Bar coexists with the translation-aware header picker

- **WHEN** a non-article page renders both the lang-links bar and the header picker
- **THEN** the two surfaces may share per-language entries (both can navigate to `/<lang>/` from the cross-language home, for instance); the bar additionally offers an "All" cross-language entry the picker does not. The two are not coupled — clicking one does not affect the other's state.
