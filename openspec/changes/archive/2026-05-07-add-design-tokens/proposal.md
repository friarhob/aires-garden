## Why

The site currently has no visual identity — it renders with browser defaults. Before any further content work, the garden needs a consistent look and feel that reflects its character: a worn, personal notebook that is equally comfortable in light and dark environments.

## What Changes

- Introduce a CSS custom-property token system as the single source of truth for colour, typography, spacing, and layout values.
- Establish the "Royal Notebook" visual identity: deep purple (`#130A22`) dark mode and warm cream (`#FAF7F2`) light mode, gold accent (`#F0C060` / `#8B6209`), Fraunces serif titles, IBM Plex Sans body/UI.
- Wire the token system into the existing Garden theme so all templates consume tokens rather than hard-coded values.
- Provide a `prefers-color-scheme` media query plus a `data-theme` toggle for explicit light/dark switching.
- Add Google Fonts loading for Fraunces (variable, opsz + wght axes) and IBM Plex Sans (300, 400, 500 weights).

## Capabilities

### New Capabilities

- `design-tokens`: CSS custom-property token layer (colour, typography, spacing, layout) with light/dark mode support and the Royal Notebook visual identity.

### Modified Capabilities

- `site-build`: Theme stylesheet and base template gain a token import and font loading; no requirement changes to the build pipeline itself.

## Impact

- **Theme**: `themes/garden/static/css/styles.css` (new token layer + base styles), `themes/garden/templates/base.html` (font `<link>` tags, `data-theme` attribute).
- **Prototype**: `tools/design-prototype.html` is the confirmed reference implementation; token values are taken directly from it.
- **Dependencies added**: Google Fonts CDN (Fraunces, IBM Plex Sans) — fallbacks defined so the site degrades gracefully offline.
- No content-model, i18n, or plugin changes required.
