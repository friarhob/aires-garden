# Visual identity

## Palette

All colours are defined as CSS custom properties in `themes/garden/static/css/styles.css`. The table below lists every design token with its light-mode and dark-mode values.

| Token | Light | Dark | Role |
|---|---|---|---|
| `--bg` | `#E7DED4` | `#130A22` | Page background |
| `--bg-subtle` | `#DCCEBD` | `#0A0515` | Admonition / panel background |
| `--text` | `#2A1640` | `#DCCEBD` | Body text |
| `--text-heading` | `#2D1A4A` | `#DCCEBD` | Heading elements (h1, article titles, list titles) |
| `--text-muted` | `#6A438E` | `#A08EC0` | Secondary text, timestamps, metadata |
| `--accent` | `#735107` | `#F0C060` | Links, interactive elements, tag chips |
| `--accent-display` | `#EDB755` | `#F0C060` | Decorative amber highlights (exempt from contrast requirements) |
| `--border` | `#DDD5C8` | `#261648` | Dividers, rule lines, image borders |
| `--admonition-note` | `#0D527D` | `#4AADBA` | Note admonition accent (teal/blue) |
| `--admonition-tip` | `#146528` | `#3ABAA0` | Tip admonition accent (forest green) |
| `--admonition-warning` | `#735107` | `#F0C060` | Warning admonition accent (matches `--accent`) |
| `--admonition-danger` | `#A02020` | `#DE4A4A` | Danger admonition accent (red) |

---

## Token naming conventions

**Surface tokens** (`--bg`, `--bg-subtle`) set backgrounds. `--bg` is the main page surface; `--bg-subtle` is one step darker in light mode and darker still in dark mode, used for inset panels such as admonitions.

**Text tokens** (`--text`, `--text-heading`, `--text-muted`) set foreground colours. Use `--text` for body copy, `--text-heading` for structural headings, `--text-muted` for supporting content (dates, captions, metadata) that should recede visually.

**Accent tokens** (`--accent`, `--accent-display`) handle interactive and decorative amber. `--accent` must always pass 4.5:1 contrast on both `--bg` and `--bg-subtle` — it is used for links and interactive states. `--accent-display` is decorative only and is exempt from contrast requirements.

**Structural token** (`--border`) is for rule lines and dividers that carry structural (not purely decorative) meaning.

**Semantic admonition tokens** (`--admonition-note`, `--admonition-tip`, `--admonition-warning`, `--admonition-danger`) express the accent colour for each admonition variant. CSS admonition rules reference these tokens exclusively — no colour literals appear in admonition rules.

**When to add a new token:** add one when a new surface or text role is introduced that cannot be expressed by an existing token without creating ambiguity. Do not add tokens for one-off colour values; prefer adjusting an existing token's value. When adding a token, add it to the WCAG audit registry in `tools/contrast_audit.py`.

---

## Mode strategy

The stylesheet implements three theme states without JavaScript:

1. **Default light mode** — `:root, :root[data-theme="light"]` declares all light-mode tokens. This is the baseline; light mode applies when no `data-theme` attribute is present and the OS preference is light or unset.

2. **OS-driven dark mode** — `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` overrides the colour tokens when the operating system requests dark mode, unless the user has explicitly chosen light via `data-theme="light"`.

3. **Explicit override** — `:root[data-theme="dark"]` forces dark mode regardless of OS preference. There is no `@media (prefers-color-scheme: light)` block; the light baseline handles that case.

Dark mode cannot be fully deduplicated in plain CSS because the explicit `:root[data-theme="dark"]` override must be a separate rule from the media-query branch. Light tokens are declared once in the grouped `:root, :root[data-theme="light"]` selector.

The `data-theme` attribute is set by the theme-toggle button in the site header and persisted to `localStorage`. See `themes/garden/static/js/prefs.js`.

---

## Typography tokens

| Token | Value | Role |
|---|---|---|
| `--font-title` | `'Fraunces', Georgia, serif` | Display headings, article titles, list item titles |
| `--font-body` | `'IBM Plex Sans', system-ui, sans-serif` | All body copy, UI controls, metadata |
| `--body-size` | `clamp(16px, 1.15vw, 18px)` | Fluid base font size |
| `--content-width` | `clamp(600px, 55vw, 900px)` | Maximum content column width |

**Fraunces** is a variable optical-size serif used for display text. The `opsz` axis is set per context: `14` in the site nav (small lockup), `18` for list titles, `36` for page h1, `72` for article titles. Weight 400 (regular) for most headings, 500 for the article title. The typeface's warm, high-contrast strokes complement the cream-and-amber palette.

**IBM Plex Sans** is a humanist sans-serif used for body copy and UI. Its open apertures maintain legibility at small sizes; the geometric regularness reads well in long-form text against the warm background.

`--body-size` uses `clamp` to stay readable on narrow viewports (floor 16px) while scaling gracefully to wider displays (cap 18px).

---

## Contrast targets and audit results

All in-use colour pairs are evaluated against **WCAG 2.1 SC 1.4.3 (Contrast Minimum)**:

- **4.5:1** — normal-weight body text and all admonition title text. Admonition titles use `font-size: 0.82rem; font-weight: 600`, which does not qualify as WCAG large text (large text requires ≥ 18.66 px regular or ≥ 14 px at weight 700+).
- **3.0:1** — retained only for `--text-heading / --bg`, as headings render at ≥ 18.66 px.
- **`--accent-display`** is exempt — decorative use only, never sits as text on any background.

To refresh this table:

```
python tools/contrast_audit.py
```

### Light mode

| Pair | Ratio | Threshold | Result | Role |
|---|---|---|---|---|
| `--text / --bg` | 12.27 | 4.5 | PASS | body text |
| `--text-muted / --bg` | 5.63 | 4.5 | PASS | muted body text |
| `--text-heading / --bg` | 11.63 | 3.0 | PASS | heading (large text) |
| `--accent / --bg` | 5.43 | 4.5 | PASS | link / accent text |
| `--text / --bg-subtle` | 10.57 | 4.5 | PASS | body text on subtle bg |
| `--text-muted / --bg-subtle` | 4.85 | 4.5 | PASS | muted text on subtle bg |
| `--accent / --bg-subtle` | 4.68 | 4.5 | PASS | link inside admonition |
| `--bg / --accent` | 5.43 | 4.5 | PASS | tag-chip hover (bg on accent) |
| `--admonition-note / --bg-subtle` | 5.40 | 4.5 | PASS | admonition-note title / border |
| `--admonition-tip / --bg-subtle` | 4.66 | 4.5 | PASS | admonition-tip title / border |
| `--admonition-warning / --bg-subtle` | 4.68 | 4.5 | PASS | admonition-warning title / border |
| `--admonition-danger / --bg-subtle` | 5.00 | 4.5 | PASS | admonition-danger title / border |

### Dark mode

| Pair | Ratio | Threshold | Result | Role |
|---|---|---|---|---|
| `--text / --bg` | 12.44 | 4.5 | PASS | body text |
| `--text-muted / --bg` | 6.51 | 4.5 | PASS | muted body text |
| `--text-heading / --bg` | 12.44 | 3.0 | PASS | heading (large text) |
| `--accent / --bg` | 11.35 | 4.5 | PASS | link / accent text |
| `--text / --bg-subtle` | 13.02 | 4.5 | PASS | body text on subtle bg |
| `--text-muted / --bg-subtle` | 6.82 | 4.5 | PASS | muted text on subtle bg |
| `--accent / --bg-subtle` | 11.87 | 4.5 | PASS | link inside admonition |
| `--bg / --accent` | 11.35 | 4.5 | PASS | tag-chip hover (bg on accent) |
| `--admonition-note / --bg-subtle` | 7.63 | 4.5 | PASS | admonition-note title / border |
| `--admonition-tip / --bg-subtle` | 8.33 | 4.5 | PASS | admonition-tip title / border |
| `--admonition-warning / --bg-subtle` | 11.87 | 4.5 | PASS | admonition-warning title / border |
| `--admonition-danger / --bg-subtle` | 4.96 | 4.5 | PASS | admonition-danger title / border |
