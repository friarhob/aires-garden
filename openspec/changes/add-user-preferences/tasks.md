## 1. Inline preference loader

- [x] 1.1 Add a synchronous inline `<script>` block to `themes/garden/templates/base.html` `<head>`, placed after the `<meta>` tags and before any `<link>` tag, that reads `garden-theme` and `garden-lang` from `localStorage` and applies them to `document.documentElement.dataset.theme` and `dataset.prefLang` respectively
- [x] 1.2 Wrap the loader's `localStorage` reads in a `try/catch` so storage-unavailable environments fall back silently
- [x] 1.3 Verify the loader script is under 10 lines

## 2. Header preference controls

- [x] 2.1 Add a `<div class="prefs">` wrapper inside `<header>` in `base.html`, placed after `.scope-switcher`
- [x] 2.2 Add `<button type="button" class="pref-theme">` inside `.prefs`, with text content rendered server-side as the opposite of the default theme (e.g. `"Light"` since dark is the default)
- [x] 2.3 Add `<button type="button" class="pref-lang">` inside `.prefs`, with text content rendered server-side as `DEFAULT_LANG | upper`
- [x] 2.4 Add CSS for `.prefs`, `.pref-theme`, `.pref-lang` in `themes/garden/static/css/styles.css` matching the `.scope-switcher` visual language (small, uppercase, muted colour, accent on hover)
- [x] 2.5 Add an active-state CSS variant (e.g. `.pref-theme[data-active]`, `.pref-lang[data-active]`) using `var(--accent)` border or background
- [x] 2.6 Sync the `data-active` attribute on each button with the current preference state in JS

## 3. Toggle behaviour script

- [x] 3.1 Create a new template partial `themes/garden/templates/_pref_controls_script.html` containing the click-handler JS for both buttons
- [x] 3.2 Implement theme-toggle handler: read current `data-theme`, flip to the opposite value, write to `localStorage` (`garden-theme`), update `dataset.theme`, update button label to the new opposite, sync `data-active`
- [x] 3.3 Implement language-cycle handler: read current `data-pref-lang` (or `DEFAULT_LANG`), find next entry in `SITE_LANGS` order (wrap around), write to `localStorage` (`garden-lang`), update `dataset.prefLang`, update button label, sync `data-active`
- [x] 3.4 Wrap all `localStorage` writes in `try/catch` so they fail silently
- [x] 3.5 Include `_pref_controls_script.html` from `base.html` near the closing `</body>` so the buttons exist before the script runs

## 4. Inference chain update

- [x] 4.1 Modify `themes/garden/templates/_lang_inference_script.html` to insert a new Stage 2 between the existing URL-prefix check (Stage 1) and `navigator.language` (was Stage 2, now Stage 3): read `document.documentElement.dataset.prefLang` and use it if it matches a known language
- [x] 4.2 Verify the inference script remains under 50 lines (ADR-0007 bar 3)

## 5. Verification

- [x] 5.1 Run `pelican content -s pelicanconf.py` and confirm build completes without errors
- [ ] 5.2 Confirm dark theme persists across page navigation when set via the toggle
- [ ] 5.3 Confirm light theme persists across page navigation when set via the toggle
- [ ] 5.4 Confirm reloading any page applies the stored theme before first paint (no FOUC)
- [ ] 5.5 Confirm the language-pref button cycles EN → PT → EN and updates `data-pref-lang` on `<html>` immediately
- [ ] 5.6 Confirm `/en/tag/published-works/` still respects URL scope (Stage 1 wins) regardless of `data-pref-lang`
- [ ] 5.7 Confirm `/tag/published-works/` (cross-lang) shows the section matching `data-pref-lang` when set
- [ ] 5.8 Confirm 404 page (`/output/404.html`) honours the new inference order
- [ ] 5.9 Confirm preference controls are not visually broken in either theme
