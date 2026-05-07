## ADDED Requirements

### Requirement: Theme preference is persisted in localStorage
The site SHALL store the reader's chosen theme (`"dark"` or `"light"`) in `localStorage` under the key `garden-theme`. Reads and writes SHALL be wrapped in `try/catch` so that environments where `localStorage` is unavailable (private browsing, storage quota exceeded) fall back silently to system-preference behaviour.

#### Scenario: Preference is saved on toggle
- **WHEN** the reader activates the theme toggle control
- **THEN** `localStorage.setItem('garden-theme', <new-value>)` is called and the `data-theme` attribute on `<html>` is updated to match

#### Scenario: Preference survives page navigation
- **WHEN** a reader sets the theme to `"light"` and navigates to a different page
- **THEN** the new page loads with `data-theme="light"` applied before first paint

#### Scenario: localStorage unavailable falls back gracefully
- **WHEN** `localStorage` throws (e.g. private browsing mode)
- **THEN** the toggle still works for the current page session; no error is thrown to the console

---

### Requirement: Language preference is persisted in localStorage
The site SHALL store the reader's preferred language code (e.g. `"en"` or `"pt"`) in `localStorage` under the key `garden-lang`. Only values present in the site's language list SHALL be stored.

#### Scenario: Preference is saved on language button click
- **WHEN** the reader clicks the language preference button
- **THEN** `localStorage.setItem('garden-lang', <new-lang>)` is called and `document.documentElement.dataset.prefLang` is updated

#### Scenario: Preference survives page navigation
- **WHEN** a reader sets the language preference to `"pt"` and navigates to a different page
- **THEN** the new page's `<html>` carries `data-pref-lang="pt"` before the lang-inference script runs

#### Scenario: Clicking does not redirect
- **WHEN** the reader clicks the language preference button on `/en/`
- **THEN** the URL remains `/en/`; only `localStorage` and `data-pref-lang` are updated

---

### Requirement: Inline loader script applies preferences before first paint
`base.html` SHALL include a synchronous inline `<script>` block in `<head>`, placed before the font and stylesheet `<link>` tags, that reads `garden-theme` and `garden-lang` from `localStorage` and applies them to `document.documentElement` immediately.

#### Scenario: Theme attribute applied before stylesheet loads
- **WHEN** any page is loaded in a browser where `garden-theme` is stored
- **THEN** `document.documentElement.dataset.theme` is set before the stylesheet link is evaluated, preventing a flash of the wrong theme

#### Scenario: Language attribute applied before inference script runs
- **WHEN** any page is loaded in a browser where `garden-lang` is stored
- **THEN** `document.documentElement.dataset.prefLang` is set before any inline inference script executes

#### Scenario: Loader script is under 10 lines
- **WHEN** the inline loader script is inspected
- **THEN** it contains fewer than 10 lines of code, consistent with ADR-0007 bar 3 (inline-and-small)

---

### Requirement: Theme toggle control is visible in the site header
The site header SHALL contain a `<button>` element with class `pref-theme` that toggles between dark and light mode. Its visible label SHALL reflect the action (the opposite of the current state), not the current state.

#### Scenario: Label reads action, not state (dark mode)
- **WHEN** the current theme is dark
- **THEN** the button label reads "Light" (switching to light is the available action)

#### Scenario: Label reads action, not state (light mode)
- **WHEN** the current theme is light
- **THEN** the button label reads "Dark"

#### Scenario: Toggle updates theme immediately
- **WHEN** the reader clicks the theme toggle
- **THEN** the page's colour scheme changes instantly without a page reload

---

### Requirement: Language preference control is visible in the site header
The site header SHALL contain a `<button>` element with class `pref-lang` that cycles through the site's available languages. Its label SHALL show the currently preferred language code in uppercase.

#### Scenario: Label shows current preference
- **WHEN** the stored preference is `"pt"`
- **THEN** the button label reads "PT"

#### Scenario: No stored preference shows default language
- **WHEN** no `garden-lang` value is stored
- **THEN** the button label shows the site's `DEFAULT_LANG` in uppercase

#### Scenario: Clicking cycles to next language
- **WHEN** the reader clicks the language button and the current preference is `"en"`
- **THEN** the preference updates to `"pt"` (the next language in `SITE_LANGS` order, wrapping around)

#### Scenario: Language button updates data-pref-lang immediately
- **WHEN** the reader clicks the language button
- **THEN** `document.documentElement.dataset.prefLang` is updated on the current page immediately

---

### Requirement: Preference controls use token-aware styles
The `.pref-theme` and `.pref-lang` buttons SHALL use CSS custom properties from the design-token layer for all colour, font, and spacing values. They SHALL share visual language with the existing `.scope-switcher` nav items (small, uppercase, muted colour, accent on hover).

#### Scenario: Controls match scope-switcher visual style
- **WHEN** the preference controls and scope-switcher are rendered side by side
- **THEN** they share the same font-size, letter-spacing, text-transform, and colour tokens

#### Scenario: Active preference is visually indicated
- **WHEN** a non-default theme or language is stored
- **THEN** the corresponding button carries a visual indicator (e.g. accent border or background) distinguishing it from the default state
