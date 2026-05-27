# i18n-rendering Spec Delta — intro-on-all-pages

## MODIFIED Requirements

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

#### Scenario: Intro region renders on every paginated page
- **WHEN** the cross-language home is paginated and page 2 (`/page/2/`) is rendered
- **THEN** the intro region IS emitted, identical to the first page (`/`): the same `<section class="intro">` containing one `<section class="intro-body" data-lang>` block per existing `all.<lang>.md` file, and the same inline inference script. The same rule applies to the per-language home: every paginated page (`/<lang>/page/2/`, …) carries its intro region whenever the matching `lang.<lang>.md` exists.

### Requirement: The home post list is paginated

Both the cross-language home `/` and each per-language home `/<lang>/` SHALL paginate their post list when the post count exceeds the configured page size. Pagination SHALL be implemented by the `i18n_grouping` plugin, which chunks the cross-language post groups (and each language's articles) into fixed-size pages and renders one static page per chunk — no JavaScript, and no use of Pelican's built-in paginator (the home indexes are emitted by the plugin in its `finalized` handler, not by Pelican's article generator). The page-size setting `HOMEPAGE_PAGINATION` SHALL be declared in `pelicanconf.py`. Each rendered page receives `page_number` (1-based) and `total_pages` template variables.

#### Scenario: First page lives at the unpaginated URL
- **WHEN** the cross-language home is paginated and the first page is requested
- **THEN** it is served at `/` (i.e. `output/index.html`), not at `/page/1/`. The same holds for each per-language home: the first page is `/<lang>/`, not `/<lang>/page/1/`.

#### Scenario: Subsequent pages are emitted under /page/N/
- **WHEN** the cross-language home has more than `HOMEPAGE_PAGINATION` post groups
- **THEN** the `i18n_grouping` plugin writes subsequent pages at `/page/2/`, `/page/3/`, … (each an `index.html` inside a `page/<n>/` directory).

#### Scenario: Per-language home paginates over its own articles
- **WHEN** any `/<lang>/` index has more than `HOMEPAGE_PAGINATION` articles
- **THEN** subsequent pages are emitted at `/<lang>/page/2/`, `/<lang>/page/3/`, … and each page lists only articles whose `Lang == <lang>`.

#### Scenario: Pagination renders a nav block with prev / numbered pages / next
- **WHEN** any paginated home page is rendered
- **THEN** the page contains a `<nav class="pagination">` element with: a previous-page link (disabled on page 1), one entry per page (the current page is marked `class="current"`), and a next-page link (disabled on the last page).

#### Scenario: Pagination is omitted when the post count fits on one page
- **WHEN** the total post-group count on `/` (or article count on `/<lang>/`) is less than or equal to `HOMEPAGE_PAGINATION` (so `total_pages` is 1)
- **THEN** the page does not render a `<nav class="pagination">` element.
