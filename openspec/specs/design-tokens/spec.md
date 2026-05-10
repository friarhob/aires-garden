# design-tokens Specification

## Requirements

### Requirement: CSS token layer defines all visual values
The theme SHALL express every colour, typography, spacing, and layout value as a CSS custom property defined in `themes/garden/static/css/styles.css`. No hard-coded colour, font-family, or layout measurement SHALL appear outside the token block.

#### Scenario: Token block present in stylesheet
- **WHEN** the stylesheet is inspected
- **THEN** a `:root` block containing at minimum `--bg`, `--text`, `--accent`, `--font-title`, `--font-body`, and `--content-width` properties SHALL exist

#### Scenario: Component styles reference tokens
- **WHEN** any non-token CSS rule uses a colour or font-family value
- **THEN** that value SHALL be a `var(--token-name)` reference, not a literal

---

### Requirement: Dark mode token set (default)
The stylesheet SHALL define light-mode token values in `:root` as the default. Light mode uses `--bg: #FAF7F2`, `--bg-subtle: #F0EAE0`, `--text: #2A1640`, `--text-heading: #2D1A4A`, `--text-muted: #7B54A0`, `--accent: #8B6209`, `--accent-display: #EDB755`, `--border: #DDD5C8`. Dark-mode token values SHALL be declared in `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }`.

#### Scenario: Light palette applied without any attribute
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is light or unset
- **THEN** the background SHALL be `#FAF7F2` and body text SHALL be `#2A1640`

#### Scenario: Dark palette applied when OS prefers dark
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is dark
- **THEN** the background SHALL be `#130A22` and body text SHALL be `#F0EAE0`

---

### Requirement: Light mode token set (override)
The stylesheet SHALL define light-mode token overrides in `:root[data-theme="light"]` only. Dark-mode token overrides SHALL be defined in both `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`. The `@media (prefers-color-scheme: light)` block used in the previous implementation SHALL be removed.

#### Scenario: Light palette applied when OS prefers light
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is light
- **THEN** the background SHALL be `#FAF7F2` and body text SHALL be `#2A1640`

#### Scenario: Explicit light override
- **WHEN** the `<html>` element carries `data-theme="light"`
- **THEN** the light palette SHALL apply regardless of `prefers-color-scheme`

#### Scenario: Explicit dark override
- **WHEN** the `<html>` element carries `data-theme="dark"`
- **THEN** the dark palette SHALL apply regardless of `prefers-color-scheme`

---

### Requirement: Fraunces and IBM Plex Sans loaded via Google Fonts
`base.html` SHALL include `<link rel="preconnect">` tags for `fonts.googleapis.com` and `fonts.gstatic.com` (with `crossorigin`), plus a stylesheet `<link>` loading Fraunces (variable, opsz 9–144, wght 300–900, both italic and upright) and IBM Plex Sans (weights 300, 400, 500; upright and italic).

#### Scenario: Font links present in rendered HTML
- **WHEN** any page is rendered
- **THEN** the `<head>` SHALL contain the Google Fonts preconnect and stylesheet links

#### Scenario: Font fallbacks defined
- **WHEN** the Google Fonts CDN is unreachable
- **THEN** `--font-title` SHALL fall back to `Georgia, serif` and `--font-body` SHALL fall back to `system-ui, sans-serif`

---

### Requirement: Typography tokens defined
`--font-title` SHALL be `'Fraunces', Georgia, serif`. `--font-body` SHALL be `'IBM Plex Sans', system-ui, sans-serif`. `--body-size` SHALL be `clamp(16px, 1.15vw, 18px)`.

#### Scenario: Title elements use Fraunces
- **WHEN** an `h1` or article title is rendered
- **THEN** it SHALL use `var(--font-title)` as its font-family

#### Scenario: Body text uses IBM Plex Sans
- **WHEN** the `<body>` element is rendered
- **THEN** it SHALL use `var(--font-body)` as its font-family

---

### Requirement: Heading colour token distinct from body text
A dedicated `--text-heading` token SHALL exist and SHALL be used by all heading elements (`h1`, article titles, list titles). In light mode `--text-heading` SHALL be `#2D1A4A`; in dark mode it SHALL inherit the same value as `--text` (`#F0EAE0`).

#### Scenario: Light mode headings use --text-heading
- **WHEN** a heading is rendered in light mode
- **THEN** its colour SHALL be `var(--text-heading)` (`#2D1A4A`), visually distinct from body text (`#2A1640`)

#### Scenario: Dark mode headings inherit --text
- **WHEN** a heading is rendered in dark mode
- **THEN** its colour SHALL be `var(--text-heading)` which resolves to `#F0EAE0`, the same as body text

---

### Requirement: Heading weight and letter-spacing conventions
Title headings (`h1`, article titles) SHALL use lighter Fraunces weights (≤500) with neutral or slightly positive letter-spacing to avoid character crowding. List titles (article-list `h2`) SHALL use weight ≤300.

#### Scenario: h1 uses open spacing
- **WHEN** an `h1` is rendered
- **THEN** its `letter-spacing` SHALL be ≥ `0em` (not negative) and `font-weight` SHALL be ≤ 500

#### Scenario: Article title legible at large size
- **WHEN** an article title is rendered at large optical size
- **THEN** `font-weight` SHALL be ≤ 500 and `letter-spacing` SHALL be ≥ `-0.015em`

---

### Requirement: Responsive content column
`--content-width` SHALL be `clamp(600px, 55vw, 900px)`. The main content area SHALL be centred and constrained to `var(--content-width)`, ensuring proportional scaling on large (4K) displays.

#### Scenario: Column width on large display
- **WHEN** the viewport is 3840px wide
- **THEN** the content column width SHALL be 900px (the `clamp` maximum)

#### Scenario: Column width on typical laptop
- **WHEN** the viewport is 1440px wide
- **THEN** the content column width SHALL be approximately 792px (`55vw`)

---

### Requirement: WCAG AA contrast on interactive accent
`--accent` in both modes SHALL meet WCAG AA contrast ratio (≥4.5:1) against `--bg` for normal-weight body text. `--accent-display` is exempt (decorative use only).

#### Scenario: Light mode accent contrast
- **WHEN** `--accent` (`#8B6209`) is rendered on `--bg` (`#FAF7F2`)
- **THEN** the contrast ratio SHALL be ≥ 4.5:1

#### Scenario: Dark mode accent contrast
- **WHEN** `--accent` (`#F0C060`) is rendered on `--bg` (`#130A22`)
- **THEN** the contrast ratio SHALL be ≥ 4.5:1

---

### Requirement: Admonition semantic tokens defined

Four semantic tokens SHALL express the accent colour for each admonition variant in both dark and light modes.

| Token | Dark value | Light value |
|---|---|---|
| `--admonition-note` | `#4AADBA` (teal) | `#1A7A8A` |
| `--admonition-tip` | `#3ABAA0` (mint) | `#207860` |
| `--admonition-warning` | `#F0C060` (matches `--accent`) | `#8B6209` (matches `--accent`) |
| `--admonition-danger` | `#C04040` | `#A02020` |

These tokens SHALL be defined in all four token blocks (`:root`, `@media prefers-color-scheme: light`, `:root[data-theme="light"]`, `:root[data-theme="dark"]`). Admonition CSS rules SHALL reference these tokens exclusively — no direct colour literals SHALL appear in admonition rules.

#### Scenario: Admonition tokens present in all token blocks
- **WHEN** the stylesheet is inspected
- **THEN** `--admonition-note`, `--admonition-tip`, `--admonition-warning`, and `--admonition-danger` are defined in all four token blocks with values matching the table above

#### Scenario: Admonition rules use only token references
- **WHEN** the admonition CSS rules are inspected
- **THEN** every colour value references a `var(--admonition-*)` token — no hardcoded hex values appear in admonition rules
