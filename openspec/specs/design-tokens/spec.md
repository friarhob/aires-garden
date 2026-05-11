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
The stylesheet SHALL define light-mode token values in `:root` as the default. Light mode uses `--bg: #E7DED4`, `--bg-subtle: #DCCEBD`, `--text: #2A1640`, `--text-heading: #2D1A4A`, `--text-muted: #6A438E`, `--accent: #735107`, `--accent-display: #EDB755`, `--border: #DDD5C8`. Dark-mode token values SHALL be declared in `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }`.

#### Scenario: Light palette applied without any attribute
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is light or unset
- **THEN** the background SHALL be `#E7DED4` and body text SHALL be `#2A1640`

#### Scenario: Dark palette applied when OS prefers dark
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is dark
- **THEN** the background SHALL be `#130A22` and body text SHALL be `#DCCEBD`

#### Scenario: Light bg and bg-subtle maintain lightness separation
- **WHEN** the light-mode `--bg` and `--bg-subtle` values are compared in HSL space
- **THEN** their lightness components SHALL differ by at least 6 percentage points so admonition surfaces remain visually distinct from the page background

---

### Requirement: Light mode token set (override)
Light-mode tokens SHALL be declared once in a grouped selector `:root, :root[data-theme="light"]`. Dark-mode token overrides SHALL be defined in both `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`. No `@media (prefers-color-scheme: light)` block SHALL appear.

#### Scenario: Light palette applied when OS prefers light
- **WHEN** the page renders without a `data-theme` attribute and `prefers-color-scheme` is light
- **THEN** the background SHALL be `#E7DED4` and body text SHALL be `#2A1640`

#### Scenario: Explicit light override
- **WHEN** the `<html>` element carries `data-theme="light"`
- **THEN** the light palette SHALL apply regardless of `prefers-color-scheme`

#### Scenario: Explicit dark override
- **WHEN** the `<html>` element carries `data-theme="dark"`
- **THEN** the dark palette SHALL apply regardless of `prefers-color-scheme`

#### Scenario: Each light token declared once
- **WHEN** the stylesheet is inspected
- **THEN** each light-mode token name SHALL appear in exactly one declaration block — the grouped `:root, :root[data-theme="light"]` selector — and not in two separate identical blocks

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
A dedicated `--text-heading` token SHALL exist and SHALL be used by all heading elements (`h1`, article titles, list titles). In light mode `--text-heading` SHALL be `#2D1A4A`; in dark mode it SHALL inherit the same value as `--text` (`#DCCEBD`).

#### Scenario: Light mode headings use --text-heading
- **WHEN** a heading is rendered in light mode
- **THEN** its colour SHALL be `var(--text-heading)` (`#2D1A4A`), visually distinct from body text (`#2A1640`)

#### Scenario: Dark mode headings inherit --text
- **WHEN** a heading is rendered in dark mode
- **THEN** its colour SHALL be `var(--text-heading)` which resolves to `#DCCEBD`, the same as body text

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

### Requirement: WCAG AA contrast on all functional pairs
Every colour pair that appears on a rendered page in either light or dark mode SHALL meet WCAG AA contrast: ≥4.5:1 for normal-weight body text and ≥3:1 for large text (≥18.66px regular or ≥14px bold) and non-text contrast (decorative borders that carry meaning, focus indicators). `--accent-display` is exempt (decorative use only, never sits on background as text).

In-scope pairs (each evaluated in both light and dark modes where both sides exist):

- `text` / `bg`
- `text-muted` / `bg`
- `text` / `bg-subtle`
- `text-muted` / `bg-subtle`
- `text-heading` / `bg`
- `accent` / `bg`
- `accent` / `bg-subtle`
- `bg` / `accent` (tag-chip hover renders `bg` text on `accent` background)
- `admonition-note` / `bg-subtle`
- `admonition-tip` / `bg-subtle`
- `admonition-warning` / `bg-subtle`
- `admonition-danger` / `bg-subtle`

#### Scenario: Audit script reports all pairs pass
- **WHEN** `tools/contrast_audit.py` is executed against the current token values
- **THEN** every pair listed above SHALL be reported with a contrast ratio meeting its applicable threshold (4.5:1 body, 3:1 large/non-text), in both light and dark modes, with no failing rows

#### Scenario: Light mode accent against background
- **WHEN** `--accent` (`#735107`) is rendered on light `--bg` (`#E7DED4`)
- **THEN** the contrast ratio SHALL be ≥ 4.5:1

#### Scenario: Light mode accent against subtle background
- **WHEN** `--accent` is rendered on light `--bg-subtle` (`#DCCEBD`)
- **THEN** the contrast ratio SHALL be ≥ 4.5:1

#### Scenario: Dark mode accent against background
- **WHEN** `--accent` (`#F0C060`) is rendered on dark `--bg` (`#130A22`)
- **THEN** the contrast ratio SHALL be ≥ 4.5:1

---

### Requirement: Admonition semantic tokens defined

Four semantic tokens SHALL express the accent colour for each admonition variant in both dark and light modes.

| Token | Dark value | Light value |
|---|---|---|
| `--admonition-note` | `#4AADBA` (teal) | `#0D527D` |
| `--admonition-tip` | `#3ABAA0` (mint) | `#146528` |
| `--admonition-warning` | `#F0C060` (matches `--accent`) | `#735107` (matches `--accent`) |
| `--admonition-danger` | `#DE4A4A` | `#A02020` |

These tokens SHALL be defined in three token blocks: light values in the grouped `:root, :root[data-theme="light"]` selector; dark values in both `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`. Admonition CSS rules SHALL reference these tokens exclusively — no direct colour literals SHALL appear in admonition rules.

#### Scenario: Admonition tokens present in token blocks
- **WHEN** the stylesheet is inspected
- **THEN** `--admonition-note`, `--admonition-tip`, `--admonition-warning`, and `--admonition-danger` are defined in the grouped light selector and both dark blocks with values matching the table above

#### Scenario: Admonition rules use only token references
- **WHEN** the admonition CSS rules are inspected
- **THEN** every colour value references a `var(--admonition-*)` token — no hardcoded hex values appear in admonition rules

---

### Requirement: Visual identity documentation
A `docs/visual-identity.md` file SHALL exist and SHALL document the current palette, token naming conventions, mode strategy (default light, OS-driven dark via `prefers-color-scheme`, explicit `data-theme` override), typography tokens, and the WCAG AA contrast audit results.

#### Scenario: Palette table present
- **WHEN** `docs/visual-identity.md` is opened
- **THEN** it SHALL include a table mapping each token name to its hex value and role, with light-mode and dark-mode values side-by-side

#### Scenario: Token naming conventions explained
- **WHEN** the document is read
- **THEN** it SHALL describe what `--bg`, `--bg-subtle`, `--text`, `--text-heading`, `--text-muted`, `--accent`, `--accent-display`, `--border`, and `--admonition-*` each mean, and the rule for when to add a new token versus extend an existing one

#### Scenario: Mode strategy documented
- **WHEN** the document is read
- **THEN** it SHALL describe how the three theme states resolve: default light mode, OS-driven dark mode via `prefers-color-scheme`, and explicit override via `data-theme`

#### Scenario: Typography tokens covered
- **WHEN** the document is read
- **THEN** it SHALL list `--font-title`, `--font-body`, and `--body-size` with their values, the rationale for the chosen typefaces (Fraunces and IBM Plex Sans), and the `opsz`/weight conventions

#### Scenario: Contrast audit results published
- **WHEN** the document is read
- **THEN** it SHALL include a table listing every in-use colour pair, the WCAG threshold applicable to that pair, the measured contrast ratio, and a pass indication — plus the invocation that reproduces the table (`python tools/contrast_audit.py`)
