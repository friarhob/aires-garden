## MODIFIED Requirements

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
