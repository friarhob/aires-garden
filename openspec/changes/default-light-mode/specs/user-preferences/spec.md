## MODIFIED Requirements

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
