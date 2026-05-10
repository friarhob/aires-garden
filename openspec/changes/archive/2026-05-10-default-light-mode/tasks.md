## 1. Stylesheet — swap token baseline

- [x] 1.1 Update `:root` comment header from "dark mode (default)" to "light mode (default)"
- [x] 1.2 Replace `:root` token values with the light palette (`--bg: #FAF7F2`, `--bg-subtle: #F0EAE0`, `--text: #2A1640`, `--text-heading: #2D1A4A`, `--text-muted: #7B54A0`, `--accent: #8B6209`, `--accent-display: #EDB755`, `--border: #DDD5C8`, light admonition tokens)
- [x] 1.3 Remove the `@media (prefers-color-scheme: light)` block
- [x] 1.4 Add `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { … } }` block with the dark palette values

## 2. Stylesheet — explicit override rules

- [x] 2.1 Verify `:root[data-theme="light"]` block contains the light palette (should be unchanged from step 1.2 values)
- [x] 2.2 Verify `:root[data-theme="dark"]` block contains the dark palette (should be correct already; confirm no change needed)

## 3. Template — initial toggle label

- [x] 3.1 In `themes/garden/templates/base.html`, change the initial `<button class="pref-theme">` label from `Light` to `Dark`

## 4. Verification

- [x] 4.1 Build the site and confirm the default (no stored preference, no OS signal) renders with light background (`#FAF7F2`)
- [x] 4.2 Confirm that setting `prefers-color-scheme: dark` in browser devtools switches to dark palette without a stored preference
- [x] 4.3 Confirm that `data-theme="light"` and `data-theme="dark"` explicit overrides still work correctly
- [x] 4.4 Confirm the toggle button reads `"Dark"` on a fresh page load and `"Light"` after switching to dark
