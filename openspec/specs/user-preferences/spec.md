# user-preferences Specification

## Purpose
TBD - created by syncing change add-user-preferences. Update Purpose after archive.
## Requirements

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

The site SHALL store the reader's preferred language code (e.g. `"en"` or `"pt"`) in `localStorage` under the key `garden-lang`. Only values present in the site's language list SHALL be stored. The preference is written by the header language picker — both when the picker is acting as a navigator (writing immediately before the browser follows the chosen entry's `href`) and when it is acting as a section-toggle (writing alongside the in-page section visibility update). The per-page lang-links bar SHALL NOT write the preference (it is a pure navigation surface).

#### Scenario: Preference is saved on language picker click — section-toggle mode

- **WHEN** the reader clicks an entry in the header language picker on a page that has no `header_lang_links` (e.g. the multilingual 404 page or a cross-language tag page with multi-lang tag-prose)
- **THEN** `localStorage.setItem('garden-lang', <new-lang>)` is called and `document.documentElement.dataset.prefLang` is updated; the corresponding `<section data-lang>` becomes visible and the others are hidden. No navigation occurs.

#### Scenario: Preference is saved on language picker click — navigation mode

- **WHEN** the reader clicks an entry in the header language picker on a page where `header_lang_links` is set (any article, page, per-language index, per-language tag index, etc.)
- **THEN** `localStorage.setItem('garden-lang', <new-lang>)` is called and `document.documentElement.dataset.prefLang` is updated synchronously, then the browser follows the entry's `href` to the equivalent page in the chosen language. The two effects happen in this order on a single user action.

#### Scenario: Preference survives page navigation

- **WHEN** a reader sets the language preference to `"pt"` (via either picker mode) and navigates to a different page
- **THEN** the new page's `<html>` carries `data-pref-lang="pt"` before the lang-inference script runs.

#### Scenario: Preference is not written by per-page lang-links bar clicks

- **WHEN** the reader clicks any entry in the per-page lang-links bar (the navigation bar on non-article pages added in `add-page-lang-links`)
- **THEN** `localStorage["garden-lang"]` is NOT updated and `data-pref-lang` is NOT changed; the click is a pure navigation. The header language picker is the only surface that writes the preference.

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
The site header SHALL contain a `<button>` element with class `pref-theme` that toggles between dark and light mode. Its visible label SHALL reflect the action (the opposite of the current state), not the current state. The initial server-rendered label (before any JavaScript or stored preference is applied) SHALL be `"Dark"`, consistent with light mode being the site default.

#### Scenario: Label reads action, not state (dark mode)
- **WHEN** the current theme is dark
- **THEN** the button label reads "Light" (switching to light is the available action)

#### Scenario: Label reads action, not state (light mode)
- **WHEN** the current theme is light
- **THEN** the button label reads "Dark"

#### Scenario: Initial server-rendered label matches default theme
- **WHEN** a page is rendered server-side with no stored preference and no `data-theme` attribute applied
- **THEN** the toggle button's HTML label is `"Dark"` (the action available from the light default)

#### Scenario: Toggle updates theme immediately
- **WHEN** the reader clicks the theme toggle
- **THEN** the page's colour scheme changes instantly without a page reload

---

### Requirement: Language preference control is visible in the site header

The site header SHALL contain a translation-aware language picker. The trigger element is a `<button class="pref-lang">` whose visible label is the currently preferred language code in uppercase; clicking the trigger opens a popover (`<div class="pref-lang-menu">`) listing the available alternatives. The contents and click semantics of the popover SHALL depend on whether the current page publishes `header_lang_links`:

- **Navigation mode** (`header_lang_links` is set and non-empty): the popover renders one `<a href="…" data-lang="…">` per entry in `header_lang_links`. Clicking writes the preference and follows the link. The current language is shown only on the trigger; it is not in the popover.
- **Section-toggle mode** (`header_lang_links` not set): the popover renders one `<button data-lang="…">` per language in `SITE_LANGS`. Clicking writes the preference and toggles `<section data-lang>` visibility on the page. No navigation.

#### Scenario: Trigger label shows current preference

- **WHEN** the stored preference is `"pt"`
- **THEN** the trigger button label reads `PT`.

#### Scenario: No stored preference shows default language on trigger

- **WHEN** no `garden-lang` value is stored
- **THEN** the trigger button label shows the site's `DEFAULT_LANG` in uppercase.

#### Scenario: Popover entries in navigation mode are anchors

- **WHEN** the picker opens on a page with `header_lang_links = {"pt": "/ola-jardim/"}`
- **THEN** the popover contains exactly one entry, an `<a href="{{ SITEURL }}/ola-jardim/" data-lang="pt">PT</a>`. The popover does not contain `<button>` entries in this mode.

#### Scenario: Popover entries in section-toggle mode are buttons

- **WHEN** the picker opens on a page where `header_lang_links` is not defined (e.g. the multilingual 404 page)
- **THEN** the popover contains one `<button data-lang="<lang>">` per entry in `SITE_LANGS`. The popover does not contain `<a>` entries in this mode.

#### Scenario: Empty popover on single-language pages

- **WHEN** the picker opens on a page where `header_lang_links` is set but empty (e.g. a single-language article)
- **THEN** the popover has no entries; clicking the trigger may open an empty popover or — at the implementer's discretion — keep it closed. The trigger label still shows the current language.

#### Scenario: Click in navigation mode navigates and writes preference

- **WHEN** the reader clicks an `<a>` entry in navigation-mode popover
- **THEN** `localStorage["garden-lang"]` is set to the entry's `data-lang` and `document.documentElement.dataset.prefLang` is updated; then the browser navigates to the entry's `href`. Modifier-key clicks (middle-click, cmd/ctrl-click) preserve the browser's default behaviour (open in new tab/window) — the script SHALL NOT call `preventDefault()` on those.

#### Scenario: Click in section-toggle mode toggles sections without navigation

- **WHEN** the reader clicks a `<button>` entry in section-toggle-mode popover
- **THEN** `localStorage["garden-lang"]` is set, `document.documentElement.dataset.prefLang` is updated, and any `<section data-lang>` blocks on the page have their `hidden` attribute toggled so only the chosen lang's section is visible. The URL is unchanged.

#### Scenario: Picker degrades gracefully without JavaScript

- **WHEN** the reader has JavaScript disabled
- **THEN** in navigation mode the popover entries remain followable as plain anchors; clicking navigates to the chosen language's page (the preference write does not happen, but the click still works). In section-toggle mode the popover entries are buttons that have no effect (consistent with existing graceful-degradation behaviour where all sections remain visible per ADR-0007 bar 2).

---

### Requirement: Preference controls use token-aware styles
The `.pref-theme` and `.pref-lang` buttons SHALL use CSS custom properties from the design-token layer for all colour, font, and spacing values. They SHALL share visual language with the existing `.scope-switcher` nav items (small, uppercase, muted colour, accent on hover).

#### Scenario: Controls match scope-switcher visual style
- **WHEN** the preference controls and scope-switcher are rendered side by side
- **THEN** they share the same font-size, letter-spacing, text-transform, and colour tokens

#### Scenario: Active preference is visually indicated
- **WHEN** a non-default theme or language is stored
- **THEN** the corresponding button carries a visual indicator (e.g. accent border or background) distinguishing it from the default state
