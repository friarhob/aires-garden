## Context

The stylesheet (`themes/garden/static/css/styles.css`) currently declares the dark palette in `:root` and overrides to light via `@media (prefers-color-scheme: light) { :root:not([data-theme="dark"]) }` plus an explicit `:root[data-theme="light"]` rule. The template (`themes/garden/templates/base.html`) renders the toggle button with the hard-coded label `Light` (the action available when in dark mode). No JavaScript logic change is needed — the inline loader and toggle script are agnostic to which theme is default.

## Goals / Non-Goals

**Goals:**
- Light palette is applied on first visit for users with no stored preference and no system dark-mode signal.
- Users whose OS signals `prefers-color-scheme: dark` continue to see the dark theme on first visit (system preference is still honoured).
- Stored `garden-theme` values (`"light"` / `"dark"`) continue to override correctly.
- Toggle button initial label is consistent with the new default (reads `"Dark"`, not `"Light"`).

**Non-Goals:**
- No changes to the colour palette values themselves.
- No changes to the `localStorage` key or the preference-persistence system.
- No changes to any JavaScript files.

## Decisions

### Decision: Swap `:root` baseline; introduce `prefers-color-scheme: dark` media query

Invert the structure symmetrically:

| Block | Before | After |
|---|---|---|
| `:root` | dark palette | light palette |
| `@media (prefers-color-scheme: light) :root:not([data-theme="dark"])` | light palette | *(removed — subsumed into `:root`)* |
| `@media (prefers-color-scheme: dark) :root:not([data-theme="light"])` | *(absent)* | dark palette |
| `:root[data-theme="light"]` | light palette | light palette (unchanged) |
| `:root[data-theme="dark"]` | dark palette | dark palette (unchanged) |

This is the minimal, symmetric change. The explicit override rules (`[data-theme="light"]` and `[data-theme="dark"]`) are already correct and require no modification — they remain at higher specificity than the media query.

**Alternative considered — remove media query entirely (light only):** Simpler CSS, but would ignore `prefers-color-scheme: dark` for first-time visitors who prefer dark. Rejected: respecting system preference is an existing, documented requirement.

### Decision: Template toggle button label changed to `"Dark"`

The `base.html` template hard-codes the initial toggle label. With light as the default, the available action on first render is to switch to dark, so the label must read `"Dark"`. The JS toggle logic already updates the label dynamically; only the initial server-rendered value changes.

## Risks / Trade-offs

- **Existing dark-mode visitors lose their preference on cache miss** → No: `localStorage` preference is applied by the inline loader before first paint. Only truly first-time visitors (no stored value) are affected, which is the intended change.
- **`data-theme="light"` override rule becomes redundant for most users** → Acceptable: it still serves users who stored `"light"` under the old default and ensures explicit overrides always work.
- **CSS comment header "dark mode (default)" becomes misleading** → Update the comment to "light mode (default)" as part of this change.
