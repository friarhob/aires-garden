## Context

The `tag_pages` plugin passes the global `base_ctx` (which contains `SITE_LANGS` — all four site languages) to both `tag_group_index.html` and `tag_lang_index.html`. Both templates iterate `SITE_LANGS` unconditionally to render "Also in" links.

The existing `i18n-rendering` spec intentionally mandated unconditional `SITE_LANGS` listing for all non-article pages, on the basis that broken links would resolve via the 404 page's language-inference machinery. For tag pages this is a poor experience: a visitor on `/pt/tag/published-works/` sees "Also in: EN · **ES** · FR", follows the ES link, and lands on a 404. Unlike home pages or the tags list — where every language root genuinely exists — a per-language tag page only exists when at least one post in that language carries that tag. The build already knows this at render time.

## Goals / Non-Goals

**Goals:**
- Emit "Also in" language links on tag pages only for languages that have at least one published post with that tag.
- Keep the fix contained to tag pages; all other non-article pages retain the current `SITE_LANGS`-unconditional behaviour.

**Non-Goals:**
- Changing the header language selector (tracked as `refactor-language-selector`).
- Filtering language links on homepage, per-language home, or tags-list pages.
- Any URL-structure or CSS changes.

## Decisions

### Pass `tag_langs` from the plugin rather than filtering in the template

**Chosen:** Compute the per-tag language set in `tag_pages/__init__.py` and pass it as a new `tag_langs` context variable to both template renders.

**Alternative considered:** Filter in the Jinja template using something like `SITE_LANGS | selectattr(...)`. Rejected because the template has no direct access to `lang_tag_map`; it would require either a custom filter or an extra round-trip to the filesystem, both of which are more complex than computing the set in the plugin where the data already lives.

**For `_render_lang_tag_pages`:** pre-build a `slug_to_langs` dict (one pass over `lang_tag_map` keys) and look up `sorted(slug_to_langs[slug])` per render call.

**For `_render_cross_tag_pages`:** derive `tag_langs` inline from `groups` — the set of distinct `lang` values across all `group["translations"]` for that slug.

### Condition on `tag_langs` length, not `SITE_LANGS` length

The "Also in" block is only rendered when there are at least two languages. The templates currently gate on `SITE_LANGS | length >= 2`. With this fix they gate on `tag_langs | length >= 2`, which is strictly correct: if only one language has posts with this tag, the "Also in" bar is degenerate and should be hidden.

## Risks / Trade-offs

- **Risk:** A future developer adds a language to the site and is surprised the new language doesn't appear in tag-page links until a post is tagged. → Low impact; this is the correct behaviour, and it aligns with how per-language tag pages are generated in the first place (they only exist when there are posts).
- **Risk:** The `tag_langs` variable name clashes with something in `base_ctx`. → Mitigated: `base_ctx` contains Pelican's standard context keys; `tag_langs` is not one of them.
