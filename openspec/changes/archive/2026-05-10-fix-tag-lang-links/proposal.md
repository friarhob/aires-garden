## Why

Tag pages display "Also in: EN · ES · FR · PT" language links using the global `SITE_LANGS` list, regardless of whether those languages have any posts carrying that tag. This produces broken links to non-existent pages (e.g. `/es/tag/published-works/` when no ES posts are tagged Published Works).

## What Changes

- The `tag_pages` plugin computes a per-tag language set at render time and passes it to templates as `tag_langs`.
- `tag_group_index.html` and `tag_lang_index.html` iterate `tag_langs` instead of `SITE_LANGS` when generating "Also in" links.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `i18n-rendering`: The language-switcher requirement for tag pages is narrowed — links must only be emitted for languages that have at least one published post with that tag.

## Impact

- `plugins/tag_pages/__init__.py` — `_render_lang_tag_pages` and `_render_cross_tag_pages`
- `themes/garden/templates/tag_group_index.html`
- `themes/garden/templates/tag_lang_index.html`
- No URL structure, data model, or CSS changes.
