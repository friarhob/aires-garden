## Why

The scope switcher in the site header was removed because it navigated to the language home (`/en/`, `/pt/`) rather than the equivalent current page, which was confusing once the language-preference toggle provided a better default-setting mechanism. Non-article pages now have no way to navigate to their per-language or cross-language counterparts.

## What Changes

- Add per-page language links to non-article templates (index, lang index, tag pages, tags list), mirroring the "Available in" pattern already used on article pages.
- Each non-article page links to its equivalent page in other language scopes: a cross-language page links to its per-language versions, and a per-language page links back to the cross-language view and to other per-language views.
- Remove the scope-switcher requirement from the `i18n-rendering` spec, replacing it with the per-page navigation requirement.

## Capabilities

### New Capabilities

_(none — this change modifies existing rendering behaviour only)_

### Modified Capabilities

- `i18n-rendering`: Remove the header scope-switcher requirement; add a per-page lang-links requirement covering cross-language and per-language index, tag, and tags-list pages.

## Impact

- Templates modified: `index.html`, `lang_index.html`, `tag_group_index.html`, `tag_lang_index.html`, `tags_list.html`
- CSS: reuse existing `p.available-in` style or add a parallel rule for non-article pages
- No plugin changes — all context variables needed are already available in each template
