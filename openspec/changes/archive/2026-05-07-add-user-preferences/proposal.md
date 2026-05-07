## Why

The garden currently has no way for a visitor to express their preferences: the colour scheme follows the OS setting with no manual override, and the default language for tag page inference falls back to `navigator.language` with no memory across visits. Adding persistent controls lets each reader configure their own experience without relying on system settings or repeating choices on every session.

## What Changes

- Add a **theme toggle** button to the site header, switching between dark and light mode and persisting the choice in `localStorage`.
- Add a **language preference control** to the site header, letting the reader set a preferred language (EN or PT) that persists in `localStorage` and overrides `navigator.language` in all JS inference logic.
- Add a small **inline script** in `<head>` that reads both preferences from `localStorage` on every page load and applies them before first paint, preventing any flash of wrong theme or wrong-language content.
- Remove the `data-theme` hard-code path used during design testing (already removed; confirmed absent).

## Capabilities

### New Capabilities

- `user-preferences`: Client-side preference persistence (theme and language) using `localStorage`, with a header UI for both controls and a FOUC-prevention inline script.

### Modified Capabilities

- `i18n-rendering`: The JS language inference logic in `_lang_inference_script.html` SHALL consult the stored language preference before falling back to `navigator.language`. This is a spec-level behaviour change.

## Impact

- **Templates**: `base.html` gains the inline preference-loader script and two new header controls; `_lang_inference_script.html` gains a `localStorage` read step.
- **CSS**: Two small UI components (theme toggle button, language selector) need token-aware styles in `styles.css`.
- **No build-time changes**: all logic is client-side JS; Pelican and the plugin stack are unaffected.
- **No server or cookie infrastructure**: `localStorage` is used rather than cookies — simpler, no expiry management, no server round-trip.
