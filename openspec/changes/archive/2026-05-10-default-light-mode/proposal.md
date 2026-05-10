## Why

The site currently defaults to dark mode, so first-time visitors without a stored preference see a dark background — even if their OS is set to light or they have no strong preference. Light mode is a more conventional reading default for a text-heavy garden, and most of the content (typography, spacing, colour choices) was designed with light mode as the intended reading surface.

## What Changes

- The CSS `:root` token block swaps to the light palette as its baseline; dark palette becomes the system-preference and explicit-override case.
- The `@media (prefers-color-scheme: dark)` block (new) mirrors the current light-media-query structure in reverse.
- The explicit `:root[data-theme="dark"]` and `:root[data-theme="light"]` override rules are adjusted to match the new baseline.
- The theme toggle button's initial rendered label changes from `"Light"` to `"Dark"` (because the default state is now light, and the available action is to switch to dark).
- The inline loader script in `base.html` requires no logic change; it still applies the stored `garden-theme` value before first paint — the user preference system remains unchanged.

## Capabilities

### New Capabilities

*(none — this is a visual/token-layer inversion, not a new capability)*

### Modified Capabilities

- `design-tokens`: The requirement "Dark mode token set (default)" changes — light palette becomes the `:root` default; dark palette moves to `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` and `:root[data-theme="dark"]`. The requirement wording, scenarios, and explicit-override rules all need updating.
- `user-preferences`: The theme toggle scenario "Label reads action, not state (dark mode)" remains valid, but the default rendered state of the toggle button in the template changes from `"Light"` to `"Dark"` (first paint, no stored preference).

## Impact

- `themes/garden/static/css/styles.css` — token block and media query restructure
- `themes/garden/templates/base.html` — toggle button initial label (`Light` → `Dark`)
- No change to the localStorage preference system, no JS logic changes
- Existing stored preferences (`garden-theme: "dark"` or `"light"`) continue to work correctly
