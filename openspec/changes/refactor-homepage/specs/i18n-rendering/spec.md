# i18n-rendering Spec Delta — refactor-homepage

## ADDED Requirements

### Requirement: The cross-language home `/` renders an intro region above the catalogue when intro content exists

The cross-language home `/` SHALL render a `<section class="intro">` region between the per-page lang-links bar and the post-catalogue heading. The region contains one `<section class="intro-body" data-lang="<lang>">` block per existing `content/intro/all.<lang>.md` file, each holding that file's rendered HTML body. If no `all.<lang>.md` file exists for any language, the entire intro region SHALL be omitted from the page.

#### Scenario: One intro-body block per existing all.<lang>.md
- **WHEN** `content/intro/all.en.md` and `content/intro/all.pt.md` exist
- **THEN** the rendered `/` page contains a `<section class="intro">` with exactly two `<section class="intro-body" data-lang="en">` and `<section class="intro-body" data-lang="pt">` children. The blocks contain the rendered Markdown bodies from those files.

#### Scenario: No intro region when no all.<lang>.md exists
- **WHEN** `content/intro/` contains no `all.<scope>.md` files
- **THEN** the rendered `/` page does NOT contain any `<section class="intro">` element. The post catalogue still renders.

#### Scenario: Intro region position is between lang-links bar and catalogue heading
- **WHEN** the rendered `/` page is inspected
- **THEN** the DOM order is: `<h1>` heading → per-page lang-links bar → `<section class="intro">` (if present) → post-catalogue heading → catalogue grid. No other element appears between the lang-links bar and the intro region.

### Requirement: The cross-language home `/` resolves which intro body to display via an inline inference script

The cross-language home `/` SHALL include an inline `<script>` that, on load, selects exactly one `<section class="intro-body" data-lang>` block to show and hides the others. With JavaScript disabled, every block remains visible — graceful degradation per [ADR-0007](../../../decisions/0007-small-clientside-js.md) bar 2. The inference chain SHALL be ordered as follows, with the first matching stage winning:

1. Stored language preference (`document.documentElement.dataset.prefLang`, populated from `localStorage` by the inline loader in `base.html`).
2. `navigator.language`'s 2-letter prefix.
3. The document's `data-default-lang` attribute.
4. The alphabetically-first emitted `<section class="intro-body" data-lang>` block (terminal fallback — guarantees at least one block is visible whenever any block was emitted).

Each stage is consulted only if a matching `<section class="intro-body" data-lang>` block was emitted; otherwise the next stage is consulted.

#### Scenario: Stored preference picks the matching block
- **WHEN** the `/` page is loaded AND `data-pref-lang` on `<html>` matches an emitted `<section class="intro-body" data-lang>`
- **THEN** only the matching block is visible, and all other `<section class="intro-body" data-lang>` blocks are hidden.

#### Scenario: navigator.language picks the matching block when no stored preference
- **WHEN** the `/` page is loaded AND `data-pref-lang` is not set (or does not match an emitted block) AND `navigator.language`'s 2-letter prefix matches an emitted block
- **THEN** the matching block is visible and the others are hidden.

#### Scenario: data-default-lang picks the matching block as third fallback
- **WHEN** stages 1 and 2 do not match an emitted block AND the document's `data-default-lang` attribute matches an emitted block
- **THEN** the matching block is visible and the others are hidden.

#### Scenario: Alphabetically-first block is the terminal fallback
- **WHEN** none of stages 1–3 matches an emitted block (e.g. site has only `all.pt.md` and `all.fr.md`, default-lang is `en`, reader has no stored preference and `navigator.language` is `de`)
- **THEN** the alphabetically-first emitted block (here: `fr`) is visible and the others are hidden.

#### Scenario: With JS disabled, every intro block remains visible
- **WHEN** the `/` page is loaded with JavaScript disabled in the browser
- **THEN** every emitted `<section class="intro-body" data-lang>` block is rendered visible (graceful degradation per ADR-0007 bar 2).

#### Scenario: Inference script is inline and small
- **WHEN** `output/index.html` is inspected
- **THEN** the inference script lives in an inline `<script>` block (no external `.js` file is loaded), is under 50 lines, and does not load any external resources at runtime — per ADR-0007 bar 3.

### Requirement: The per-language home `/<lang>/` renders an intro region when its single-language file exists

The per-language home `/<lang>/` SHALL render a `<section class="intro">` region between the per-page lang-links bar and the post-catalogue heading, containing the rendered HTML body of `content/intro/lang.<lang>.md` if that file exists. If the file does not exist, the entire intro region SHALL be omitted from the page. The per-language home SHALL NOT fall back to a different language's intro body.

#### Scenario: Intro body is rendered when the matching lang.<lang>.md exists
- **WHEN** `content/intro/lang.en.md` exists AND the `/en/` page is rendered
- **THEN** the page contains a single `<section class="intro">` whose body is the rendered HTML of `content/intro/lang.en.md`. The section carries no `data-lang` toggle and no inference script.

#### Scenario: No intro region when no matching lang.<lang>.md exists
- **WHEN** `content/intro/lang.en.md` does NOT exist AND the `/en/` page is rendered
- **THEN** the rendered page does NOT contain any `<section class="intro">` element. The post catalogue still renders.

#### Scenario: Per-language home does not fall back across languages
- **WHEN** `content/intro/lang.en.md` does NOT exist BUT `content/intro/lang.pt.md` exists AND the `/en/` page is rendered
- **THEN** the `/en/` page does NOT show the PT body. The intro region is omitted entirely on `/en/`.

### Requirement: The home post list is paginated

Both the cross-language home `/` and each per-language home `/<lang>/` SHALL paginate their post list when the post count exceeds the configured page size. Pagination SHALL be implemented via Pelican's built-in paginator (static URLs, no JavaScript). The page-size setting `DEFAULT_PAGINATION` SHALL be declared in `pelicanconf.py`.

#### Scenario: First page lives at the unpaginated URL
- **WHEN** the cross-language home is paginated and the first page is requested
- **THEN** it is served at `/` (i.e. `output/index.html`), not at `/page/1/`.

#### Scenario: Subsequent pages follow Pelican's pattern
- **WHEN** the cross-language home has more than `DEFAULT_PAGINATION` post groups
- **THEN** subsequent pages are emitted at `/page/2/`, `/page/3/`, …, following Pelican's default `PAGINATION_PATTERNS`.

#### Scenario: Per-language home paginates over its own articles
- **WHEN** any `/<lang>/` index has more than `DEFAULT_PAGINATION` articles
- **THEN** subsequent pages are emitted at `/<lang>/page/2/`, `/<lang>/page/3/`, … and each page lists only articles whose `Lang == <lang>`.

#### Scenario: Pagination renders a nav block with prev / numbered pages / next
- **WHEN** any paginated home page is rendered
- **THEN** the page contains a `<nav class="pagination">` element with: a previous-page link (disabled on page 1), one entry per page (the current page is marked `class="current"`), and a next-page link (disabled on the last page).

#### Scenario: Pagination is omitted when the post count fits on one page
- **WHEN** the total post-group count on `/` (or article count on `/<lang>/`) is less than or equal to `DEFAULT_PAGINATION`
- **THEN** the page does not render a `<nav class="pagination">` element.

#### Scenario: Intro region renders only on the first page
- **WHEN** the cross-language home is paginated and page 2 (`/page/2/`) is rendered
- **THEN** the intro region is NOT emitted; only the first page (`/`) carries the intro. The same rule applies to the per-language home: only the first page carries the intro.

### Requirement: The home post list renders as a CSS-grid catalogue of card entries

Both the cross-language home `/` and each per-language home `/<lang>/` SHALL render their post list as a `<section class="catalogue">` wrapper containing a `<div class="catalogue-grid">` whose children are `<a class="catalogue-card">` entries — one per post-group (cross-language) or one per article (per-language). Each card SHALL contain a `.card-title` element with the post title and a `.card-meta` element with a `<time datetime>` for the date and a `.langs` container with one `.lang-chip` element per language available for that entry.

#### Scenario: Catalogue wrapper and grid exist on each home page
- **WHEN** any paginated home page (`/`, `/<lang>/`, `/page/N/`, `/<lang>/page/N/`) is rendered
- **THEN** the page contains exactly one `<section class="catalogue">` with exactly one `<div class="catalogue-grid">` as its primary list container.

#### Scenario: Each catalogue-card carries title, date, and language chips
- **WHEN** a `<a class="catalogue-card">` element is inspected
- **THEN** it contains a `.card-title` with the post (or group canonical) title, a `<time datetime="<ISO-date>">` inside `.card-meta`, and a `.langs` element with one `<span class="lang-chip">` per available language for that entry.

#### Scenario: Cross-language card lang chips list every available language for the group
- **WHEN** a cross-language card is rendered for a translation group with EN and PT translations
- **THEN** the card's `.langs` contains exactly two `.lang-chip` elements showing `EN` and `PT` (uppercase). No other lang chips appear on that card.

#### Scenario: Per-language card lang chips show only the current language
- **WHEN** a per-language `/<lang>/` card is rendered
- **THEN** the card's `.langs` contains exactly one `.lang-chip` element showing the page's `<lang>` (uppercase).

#### Scenario: Card title respects the homepage link target rule
- **WHEN** a cross-language card is rendered for a group with a `DEFAULT_LANG` translation
- **THEN** the card's `href` attribute is the URL of the `DEFAULT_LANG` article in the group (carrying over the existing homepage-entry behaviour from the "aggregate homepage shows each post once" requirement).
