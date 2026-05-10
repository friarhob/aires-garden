## 1. Decision log

- [x] 1.1 Add `openspec/decisions/0010-header-lang-picker-as-navigator.md` (Status: Accepted) recording the navigator-vs-preference reversal; cite `add-user-preferences` design D5 as superseded.
- [x] 1.2 Update `openspec/decisions/README.md` index to list ADR-0010.

## 2. Header partial — two-mode picker

- [x] 2.1 In `themes/garden/templates/base.html`, replace the popover's hard-coded `{% for lang in SITE_LANGS %}` block with a conditional: when `header_lang_links` is defined and non-empty, render one `<a href="{{ url }}" data-lang="{{ lang }}">{{ lang | upper }}</a>` per `(lang, url)` pair; otherwise render the existing `<button data-lang="{{ lang }}">` per language in `SITE_LANGS`.
- [x] 2.2 Mark the active mode on the picker root (e.g. `data-picker-mode="navigation"` vs `data-picker-mode="section-toggle"`) so JS and CSS can branch off it.
- [x] 2.3 In `themes/garden/templates/_pref_controls_script.html`, branch the popover-click handler on `data-picker-mode`: in navigation mode, write `localStorage["garden-lang"]` and `data-pref-lang` then let the click follow the `href` (do not `preventDefault()` for any modifier-key clicks); in section-toggle mode, keep the existing toggle path.
- [x] 2.4 Confirm middle-click and modifier-key clicks (`cmd`/`ctrl`/`shift`) on `<a>` entries preserve the browser default (no `preventDefault`); guard with explicit checks if needed.
- [x] 2.5 Update the popover's "current" indicator logic: current lang IS included in popover entries and marked with `data-current`; trigger button also shows current lang label.

## 3. Page templates — publish `header_lang_links`

- [x] 3.1 `themes/garden/templates/article.html`: add `{% set header_lang_links = ... %}` deriving from `article.translation_group` (all langs including current) mapped to `lang -> SITEURL ~ '/' ~ t.url`.
- [x] 3.2 `themes/garden/templates/page.html`: add `{% set header_lang_links = ... %}` deriving from `page.translations` mapped to `lang -> SITEURL ~ '/' ~ t.url`.
- [x] 3.3 `themes/garden/templates/index.html`: add `{% set header_lang_links = ... %}` mapping each `lang` in `SITE_LANGS` to `SITEURL ~ '/' ~ lang ~ '/'`.
- [x] 3.4 `themes/garden/templates/lang_index.html`: add `{% set header_lang_links = ... %}` mapping each `lang` in `SITE_LANGS` (including `page_lang`) to `SITEURL ~ '/' ~ lang ~ '/'`.
- [x] 3.5 `themes/garden/templates/tags_list.html`: add `{% set header_lang_links = ... %}` covering both shapes (cross-lang `/tags/` and per-lang `/<lang>/tags/`); per-lang form includes `page_lang`.
- [x] 3.6 `themes/garden/templates/tag_lang_index.html`: add `{% set header_lang_links = ... %}` mapping each `lang` in `tag_langs` (including `page_lang`) to `SITEURL ~ '/' ~ lang ~ '/tag/' ~ tag_slug ~ '/'`.
- [x] 3.7 `themes/garden/templates/tag_group_index.html`: add `{% set header_lang_links = ... %}` only when `all_prose | length < 2` — mapping each `lang` in `tag_langs` to `SITEURL ~ '/' ~ lang ~ '/tag/' ~ tag_slug ~ '/'`. When `all_prose | length >= 2`, do not set it.
- [x] 3.8 `themes/garden/templates/404.html`: confirm `header_lang_links` is NOT set (deliberate omission so section-toggle mode wins).
- [x] 3.9 If template duplication is awkward, extract a one-line Jinja macro `header_lang_links_for(...)` in a shared partial; otherwise leave inlined. _(Kept inlined — no awkward duplication.)_

## 4. Plugins — verify nothing else needs to change

- [x] 4.1 `plugins/i18n_grouping/__init__.py`: confirm the per-language index render path in `on_finalized` already passes the context the template needs (`SITE_LANGS`, `page_lang`); no plugin code change required.
- [x] 4.2 `plugins/tag_pages/__init__.py`: confirm the tag-language and tag-group render paths already pass `tag_langs`, `tag_slug`, `all_prose`, `page_lang`; no plugin code change required.

## 5. Styles

- [x] 5.1 In `themes/garden/static/css/styles.css`, ensure `.pref-lang-menu a` is styled identically to `.pref-lang-menu button` (font, colour, padding, hover, focus).
- [x] 5.2 If a single-lang post should hide the trigger entirely, add a CSS rule that hides `.pref-lang-picker[data-empty]` (or equivalent); otherwise leave the trigger visible per design D4. _(No CSS rule added; per design D4 the trigger stays visible.)_

## 6. Manual verification (golden paths)

- [ ] 6.1 `make devbuild`, then visit `/hello-garden/` (EN) — picker popover lists `PT` only, click navigates to `/ola-jardim/`, the new page shows `PT` on the trigger and `EN` in the popover, `localStorage["garden-lang"] === "pt"`.
- [ ] 6.2 Visit `/ola-jardim/` (assumed multi-lang case) and confirm reverse direction works.
- [ ] 6.3 Visit a single-language post and confirm the popover is empty (no entries) and the trigger still shows the post's language.
- [ ] 6.4 Visit `/en/` — popover lists `PT`; click navigates to `/pt/`.
- [ ] 6.5 Visit `/tag/<slug>/` for a tag with single-lang prose — popover lists `tag_langs`; click navigates to `/<lang>/tag/<slug>/`.
- [ ] 6.6 Visit `/tag/<slug>/` for a tag with multi-lang prose — popover lists `SITE_LANGS`; click toggles `<section data-lang>` visibility, URL unchanged.
- [ ] 6.7 Visit a non-existent URL to trigger `output/404.html` — popover lists `SITE_LANGS`; click toggles section visibility, URL unchanged.
- [ ] 6.8 Per-page lang-links bar still renders on every non-article page; clicking a bar entry navigates without writing `localStorage["garden-lang"]` (verify in DevTools).
- [ ] 6.9 Disable JS in DevTools, reload the article — popover entries are still followable anchors; click navigates correctly; preference is not written (expected).
- [ ] 6.10 Cmd/middle-click an entry — opens in new tab, browser default preserved.

## 7. Spec validation

- [ ] 7.1 `openspec validate refactor-language-selector` passes (or whatever the project's validate command is).
- [ ] 7.2 `openspec status --change refactor-language-selector` reports `isComplete: true`.

## 8. Commit

- [ ] 8.1 Commit the proposal bundle (proposal + design + specs + tasks) as a single commit per the project's "Commit per proposal bundle" convention.
