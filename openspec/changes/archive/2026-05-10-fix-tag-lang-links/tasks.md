## 1. Plugin — compute per-tag language sets

- [x] 1.1 In `_render_lang_tag_pages`, pre-build a `slug_to_langs` dict from `lang_tag_map` keys before the render loop
- [x] 1.2 Pass `tag_langs=sorted(slug_to_langs.get(slug, set()))` to each `tag_lang_index.html` render call

- [x] 1.3 In `_render_cross_tag_pages`, derive `tag_langs` inline from `groups` (distinct `lang` values across all group translations)
- [x] 1.4 Pass `tag_langs=tag_langs` to each `tag_group_index.html` render call

## 2. Templates — use `tag_langs` instead of `SITE_LANGS`

- [x] 2.1 In `tag_group_index.html`, change the "Also in" guard condition from `SITE_LANGS | length >= 2` to `tag_langs | length >= 2`
- [x] 2.2 In `tag_group_index.html`, change the loop from `for lang in SITE_LANGS | sort` to `for lang in tag_langs`
- [x] 2.3 In `tag_lang_index.html`, change the guard condition from `SITE_LANGS | length >= 2` to `tag_langs | length >= 2`
- [x] 2.4 In `tag_lang_index.html`, change the loop from `for lang in SITE_LANGS | sort` to `for lang in tag_langs`

## 3. Verify

- [x] 3.1 Build the site locally and confirm `/tag/published-works/` lists only EN and PT links (no ES or FR)
- [x] 3.2 Confirm `/pt/tag/published-works/` shows "Also in: All · EN" (no ES or FR)
- [x] 3.3 Confirm a tag that exists in all four languages still shows all four links
