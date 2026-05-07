## 1. CSS

- [x] 1.1 Add `.page-langs` rule to `themes/garden/static/css/styles.css` matching the visual language of `p.available-in` (muted text colour, accent-coloured links, sized to `0.85rem`). Position-appropriate margin so it sits cleanly under the `<h1>`.
- [x] 1.2 Add `.page-lang-current` rule that visually marks the current scope (accent colour, no underline; pattern parallels the popover's `[data-current]` indicator).

## 2. Template: cross-language home (`index.html`)

- [x] 2.1 After the `<h1>` and before the article list, add a Jinja `{% if SITE_LANGS | length >= 2 %}` block that renders a `<p class="page-langs">` containing: an "All" entry marked with `class="page-lang-current"`, and one `<a>` per language in `SITE_LANGS` with `href="{{ SITEURL }}/{{ lang }}/"`.
- [x] 2.2 Build locally and verify `output/index.html` contains the bar with "All" highlighted and EN/PT linking to `/en/` and `/pt/`.

## 3. Template: per-language home (`lang_index.html`)

- [x] 3.1 After the `<h1>` and before the article list, add the lang-links bar: an "All" entry with `href="{{ SITEURL }}/"`, and one `<a>` per language in `SITE_LANGS` with `href="{{ SITEURL }}/{{ lang }}/"`. The entry where `lang == page_lang` carries `class="page-lang-current"`.
- [x] 3.2 Build locally and verify `output/en/index.html` highlights EN and `output/pt/index.html` highlights PT, with both linking back to `/`.

## 4. Template: cross-language tag index (`tag_group_index.html`)

- [x] 4.1 After the `<h1>` and before the prose/list, add the lang-links bar: "All" marked current, one `<a>` per `SITE_LANGS` lang with `href="{{ SITEURL }}/{{ lang }}/tag/{{ tag_slug }}/"`.
- [x] 4.2 Build locally and verify `output/tag/<slug>/index.html` for an existing tag shows the bar with "All" current and per-lang links.

## 5. Template: per-language tag index (`tag_lang_index.html`)

- [x] 5.1 After the `<h1>` and before the prose/list, add the lang-links bar: an "All" entry with `href="{{ SITEURL }}/tag/{{ tag_slug }}/"`, plus one `<a>` per `SITE_LANGS` lang with `href="{{ SITEURL }}/{{ lang }}/tag/{{ tag_slug }}/"`. Entry where `lang == page_lang` carries `class="page-lang-current"`.
- [x] 5.2 Build locally and verify `output/<lang>/tag/<slug>/index.html` highlights the current language and links to the cross-language and other per-language variants.

## 6. Template: tags-list (`tags_list.html`)

- [x] 6.1 After the `<h1>` and before the tag chips, add a single `{% if SITE_LANGS | length >= 2 %}` lang-links block that branches on `page_lang is defined and page_lang`: when defined, render with "All" linking to `/tags/` and per-lang entries linking to `/<lang>/tags/` (current marked); when not defined, render with "All" marked current and per-lang entries linking to `/<lang>/tags/`.
- [x] 6.2 Build locally and verify `output/tags/index.html` and `output/<lang>/tags/index.html` each render the bar correctly.

## 7. Verification

- [x] 7.1 Confirm article pages still render only their existing "Available in" line (no `<p class="page-langs">`); the bar must not appear on `output/<slug>/index.html`.
- [x] 7.2 Confirm bar links are plain `<a>` elements with `href` only — no `onclick`, `data-lang`, or other attributes that would pull them into the header preference-toggle JS.
- [ ] 7.3 Visually inspect each page kind in the browser (light + dark theme) to confirm the current-scope marker is legible and consistent across all six page kinds.
- [ ] 7.4 Click each per-lang link from a per-lang page back to the cross-lang page and forward to a different per-lang page; confirm normal navigation occurs (no JS interception, URL changes correctly).
