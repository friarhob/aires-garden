## Context

The Garden theme currently has an empty `styles.css` and a minimal `base.html`. All rendered pages use browser defaults. A visual prototype (`tools/design-prototype.html`) was developed interactively and is the confirmed reference for the Royal Notebook identity — it contains the final token values, font stack, and component styles. This change translates that prototype into the live theme.

## Goals / Non-Goals

**Goals:**
- Define all visual values as CSS custom properties in a single token block.
- Implement light and dark mode; dark mode is the default per-prototype; `prefers-color-scheme` controls the automatic choice with an explicit `data-theme` override.
- Load Fraunces (variable, opsz + wght) and IBM Plex Sans (300/400/500) from Google Fonts with appropriate fallbacks.
- Apply base typography, link, header, and layout styles that all existing templates inherit.
- Keep the token layer separate from component styles so future changes can modify one without touching the other.

**Non-Goals:**
- Component-level styles for article, tag, or list views (those come in a subsequent change).
- Any JS-powered theme toggle in the live site (the prototype toggle is prototype-only chrome).
- Print stylesheet or accessibility audit beyond WCAG AA contrast on the two primary accents.

## Decisions

### D1 — CSS custom properties, no preprocessor

**Decision:** Plain CSS custom properties in `styles.css`, no Sass/Less.

**Rationale:** Pelican's static pipeline has no Node toolchain. Adding one for a variables layer is disproportionate. CSS custom properties are natively cascadeable, inspectable in DevTools, and sufficient for a single-author garden.

**Alternatives considered:**
- *Sass variables*: Would require a build step or pre-compiled output checked into the repo. Rejected — adds complexity with no gain at this scale.
- *Inline `<style>` in base.html*: Tokens in a Jinja template are harder to maintain and bypass browser caching. Rejected.

### D2 — Dark mode via `[data-theme]` attribute on `<html>`

**Decision:** `<html data-theme="dark">` (or `"light"`) as the explicit override mechanism; `@media (prefers-color-scheme)` applies when no attribute is set.

**Rationale:** Matches the prototype approach. A single attribute on the root element is the lowest-footprint toggle that survives across all templates without JS being strictly required for the default experience.

**Alternatives considered:**
- *Class on `<body>`*: Works identically but `data-theme` on `<html>` is the emerging convention (used by GitHub, MDN) and applies before body renders.
- *No toggle, media query only*: Simpler but removes the ability for users to override their system setting without changing OS preferences. Rejected as too limiting.

### D3 — Dark mode as the prototyped default; no server-side default baked in

**Decision:** The HTML ships without a `data-theme` attribute. The browser's `prefers-color-scheme` media query handles the default. No server-side or build-time default is set.

**Rationale:** The correct default is the user's OS preference. Setting `data-theme="dark"` server-side would override users who prefer light. The prototype's toggle is prototype-only chrome and does not carry over.

### D4 — Google Fonts CDN, not self-hosted

**Decision:** Load Fraunces and IBM Plex Sans via Google Fonts `<link>` in `base.html`.

**Rationale:** Self-hosting requires checking font files into the repo and maintaining subset/format coverage. For a personal garden served via GitHub Pages, Google Fonts CDN provides caching benefits at zero maintenance cost.

**Alternatives considered:**
- *System font stack only*: No external dependency, instant load. Rejected — Fraunces is integral to the Royal Notebook identity and has no close system equivalent.
- *Self-hosted via `fontsource` npm package*: Good DX but requires Node. Rejected for same reason as Sass (no build toolchain in this project).

### D5 — Token structure: three groups in one `:root` block

**Decision:** Tokens are organised into colour, typography, and layout groups within a single `:root { }` block, followed by a `[data-theme="light"]` override block and a `@media (prefers-color-scheme: light)` override block.

```
:root                           → dark defaults (Royal Notebook dark)
:root[data-theme="light"]       → explicit light override
@media (prefers-color-scheme: light) :root:not([data-theme="dark"])
                                → automatic light when OS prefers light
```

Confirmed token values:

| Token              | Dark (`#130A22` bg) | Light (`#FAF7F2` bg) |
|--------------------|---------------------|----------------------|
| `--bg`             | `#130A22`           | `#FAF7F2`            |
| `--bg-subtle`      | `#0A0515`           | `#F0EAE0`            |
| `--text`           | `#F0EAE0`           | `#2A1640`            |
| `--text-muted`     | `#A08EC0`           | `#7B54A0`            |
| `--accent`         | `#F0C060`           | `#8B6209`            |
| `--accent-display` | `#F0C060`           | `#EDB755`            |
| `--border`         | `#261648`           | `#DDD5C8`            |

**Rationale:** Dark mode is the primary designed mode; its values live in `:root` (no media query overhead). Light mode is the override. This is the inverse of the typical pattern but matches the design intent and avoids a FOUC on dark-preferring systems.

### D6 — Title colour distinct from body text in light mode

**Decision:** Headings (`h1`, article titles, list titles) use `#2D1A4A` in light mode rather than inheriting `--text` (`#2A1640`).

**Rationale:** Three options were prototyped and compared: near-black (`#2A1640`, same as body), deep purple (`#2D1A4A`), and dark-mode-bg-as-title (`#130A22`). Option B (`#2D1A4A`) was chosen — it is visually distinct from body text, clearly purple, and sits coherently between `--text` and `--bg` (dark mode) in the overall palette. A dedicated `--text-heading` token carries this value so it can be overridden independently of `--text`.

**Alternatives considered:**
- *Inherit `--text`*: No distinction between title and body — hierarchy felt flat.
- *`#130A22` (dark-mode bg)*: Maximum contrast but reads as a different black; less cohesive with the purple-tinted body text.

Body text (`--text: #2A1640`) and muted/meta text (`--text-muted: #7B54A0`) were also shifted from near-black/grey to purple-tinted values in the same session to give the light mode a warm, cohesive purple character throughout.

## Risks / Trade-offs

- **Google Fonts CDN dependency** → Fallback fonts (`Georgia`, `system-ui`) are defined on every font-family token so the site degrades gracefully if the CDN is unreachable.
- **FOUC on explicit `data-theme` toggle** → There is no toggle in the live site (D3), so no FOUC risk. If a toggle is added later, a small inline script in `<head>` will be needed to apply the saved preference before first paint.
- **Contrast on gold accent** → `#F0C060` (dark mode) and `#8B6209` (light mode) were verified against their backgrounds for WCAG AA on body text. Decorative uses of the display gold (`#EDB755`) are exempt but should not be used on interactive text in light mode.
- **Contrast on purple text** → `--text` (`#2A1640`) and `--text-heading` (`#2D1A4A`) are both near-black against cream and comfortably exceed WCAG AA. `--text-muted` (`#7B54A0`) on `#FAF7F2` sits at approximately 4.6:1 — just above the AA threshold for normal text; verify it is not used at very small sizes.

## Migration Plan

1. Write token block and base styles to `themes/garden/static/css/styles.css`.
2. Add Google Fonts `<link>` preconnect and stylesheet tags to `themes/garden/templates/base.html`.
3. Run `pelican content -s pelicanconf.py` and verify rendered pages adopt the new styles.
4. No rollback complexity — reverting `styles.css` and `base.html` restores the prior (blank) state.
