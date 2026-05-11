## MODIFIED Requirements

### Requirement: Dark mode token set (default)
The stylesheet SHALL define light-mode token values in `:root` as the default. Light mode uses `--bg: #E7DED4`, `--bg-subtle: #DCCEBD`, `--text: #2A1640`, `--text-heading: #2D1A4A`, `--text-muted: #7B54A0`, `--accent: #8B6209`, `--accent-display: #EDB755`, `--border: #DDD5C8`. Dark-mode token values SHALL be declared in `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }`. Dark mode uses `--text: #DCCEBD` and `--text-heading: #DCCEBD`.

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
The stylesheet SHALL declare light-mode token values once, in a grouped selector covering both the default and explicit-light states: `:root, :root[data-theme="light"]`. Dark-mode token overrides SHALL be defined in both `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`. No `@media (prefers-color-scheme: light)` block SHALL appear.

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

### Requirement: Heading colour token distinct from body text
A dedicated `--text-heading` token SHALL exist and SHALL be used by all heading elements (`h1`, article titles, list titles). In light mode `--text-heading` SHALL be `#2D1A4A`; in dark mode it SHALL inherit the same value as `--text` (`#DCCEBD`).

#### Scenario: Light mode headings use --text-heading
- **WHEN** a heading is rendered in light mode
- **THEN** its colour SHALL be `var(--text-heading)` (`#2D1A4A`), visually distinct from body text (`#2A1640`)

#### Scenario: Dark mode headings inherit --text
- **WHEN** a heading is rendered in dark mode
- **THEN** its colour SHALL be `var(--text-heading)` which resolves to `#DCCEBD`, the same as body text

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
- **WHEN** `--accent` (`#8B6209`) is rendered on light `--bg` (`#E7DED4`)
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
| `--admonition-note` | `#4AADBA` (teal) | `#1A7A8A` |
| `--admonition-tip` | `#3ABAA0` (mint) | `#207860` |
| `--admonition-warning` | `#F0C060` (matches `--accent`) | `#8B6209` (matches `--accent`) |
| `--admonition-danger` | `#C04040` | `#A02020` |

These tokens SHALL be defined in the post-dedupe block structure: light values in the grouped `:root, :root[data-theme="light"]` selector; dark values in both `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and `:root[data-theme="dark"]`. Admonition CSS rules SHALL reference these tokens exclusively — no direct colour literals SHALL appear in admonition rules.

#### Scenario: Admonition tokens present in post-dedupe blocks
- **WHEN** the stylesheet is inspected
- **THEN** `--admonition-note`, `--admonition-tip`, `--admonition-warning`, and `--admonition-danger` SHALL be defined in the grouped light selector and in both dark-token blocks (the media-query branch and the explicit `:root[data-theme="dark"]` override) with values matching the table above

#### Scenario: Admonition rules use only token references
- **WHEN** the admonition CSS rules are inspected
- **THEN** every colour value SHALL reference a `var(--admonition-*)` token — no hardcoded hex values SHALL appear in admonition rules

## ADDED Requirements

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
