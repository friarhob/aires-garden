## Status

Design decisions recorded below.

## Context

The header language picker today (shipped in `add-user-preferences`) is a **preference-toggle**: the popover lists every entry in `SITE_LANGS`, clicking writes `localStorage["garden-lang"]` and `data-pref-lang`, and that's it. The visible URL never changes. The popover JS lives in `themes/garden/templates/_pref_controls_script.html`.

Three other surfaces already do navigation between language scopes:

1. The **"Available in" line** on article and page templates lists existing translations as plain `<a>` links (built from `article.translation_group` / `page.translations`).
2. The **per-page lang-links bar** added in `add-page-lang-links` lives on every non-article page (cross-lang home, per-lang home, cross-lang tag, per-lang tag, tags-list, per-lang tags-list) and offers `All · EN · PT · …` navigation between language scopes.
3. The **multilingual 404 page** uses inline JS (`_lang_inference_script.html`) to read the URL `/<lang>/` prefix, the stored preference, then `navigator.language`, then `data-default-lang`, to choose which `<section data-lang>` to show. It is the only page in the build whose canonical language is genuinely unknown until the client runs.

The grouping data the new switcher needs already exists:

- `i18n_grouping/__init__.py` builds `article.translation_group`, populates `SITE_LANGS`, and writes per-language indexes via `on_finalized`.
- `tag_pages/__init__.py` (not read in detail here, but referenced) renders the per-language tag indexes and the cross-language tag indexes; it owns `tag_langs` in their context.
- Pages get `page.translations` for free from Pelican core.

What's missing is a **template-side contract** the header partial can consult: a per-page mapping `{lang: url, ...}` of where each language entry should navigate to.

## Goals / Non-Goals

**Goals:**

- Clicking the header language picker takes the reader to the equivalent page in the chosen language when one exists.
- The picker only lists languages that have an existing target on the current page (mirrors the "Available in" line).
- The reader's choice persists in `localStorage["garden-lang"]` so language-inference pages (404, multi-lang tag-prose) honour it on the next visit.
- Pages whose primary content is split into `<section data-lang>` blocks (404, cross-lang tag pages with multi-lang tag-prose) keep the existing in-page section-toggle behaviour — there is no single canonical target to navigate to.
- Graceful degradation: the picker remains usable with JS disabled (entries are real `<a href>` links).

**Non-Goals:**

- Removing or merging the per-page lang-links bar from `add-page-lang-links`. The user has chosen to keep both surfaces; collapsing them is deferred.
- Introducing a new content kind, plugin, or signal hook. Existing plugin contexts and Jinja `{% set %}` blocks are sufficient.
- Cross-tag inference. If the reader is on `/en/tag/poetry/` and PT has no `poetry` tag with posts, we do **not** try to map to `/pt/tag/poesia/` — the entry is simply absent (per the "hide missing entries" choice).
- Changing the URL of any page. This is purely a behavioural change to the header picker.
- Internationalising the picker labels. The language code remains the label.

## Decisions

### D1 — Templates publish `header_lang_links`; the header partial consumes it

**Decision:** Each page template sets a Jinja variable `header_lang_links` — a dict of `{lang_code: target_url, ...}` listing the languages the picker should offer for *this* page, with their navigation targets. The header partial in `base.html` reads this variable; when set and non-empty, it renders `<a href>` entries; when unset (or empty), it falls back to the existing section-toggle behaviour over `SITE_LANGS`.

**Rationale:** Each template already knows what its peers in other languages look like (`article.translation_group`, `tag_langs` + `tag_slug`, `SITE_LANGS`, `page.translations`). Pushing the mapping into the template keeps the contract local and inspectable; the header partial stays dumb. No new plugin signal is needed; we only extend the *contexts* the existing plugins inject.

**Alternatives considered:**

- *Compute on the JS side* (read all available `<a>` links from the page to build the popover): brittle, page-shape-dependent, breaks if the "Available in" line is ever restyled.
- *Compute in a brand-new plugin*: needless; the data lives in three contexts already, and a plugin would have to special-case each page kind anyway.
- *One-mapping-fits-all `LANG_LINKS` global*: impossible — the mapping varies per page (article, lang index, tag index, …).

### D2 — Two modes: navigation vs. section-toggle, selected by `header_lang_links` presence

**Decision:** The header partial has exactly two rendering modes:

| Mode | Trigger | Picker entries | Click behaviour |
|---|---|---|---|
| Navigation | `header_lang_links` is set & non-empty | one `<a href>` per entry in `header_lang_links` | Browser navigates; JS also writes `localStorage["garden-lang"]` + `data-pref-lang` to the chosen lang before navigation. |
| Section-toggle | `header_lang_links` not set | one `<button>` per entry in `SITE_LANGS` (current behaviour) | JS toggles `<section data-lang>` visibility, writes `localStorage` + `data-pref-lang`, no navigation. |

The 404 template and `tag_group_index.html` (only when `all_prose | length >= 2`) deliberately do **not** set `header_lang_links` and therefore stay in section-toggle mode.

**Rationale:** A single boolean flag would force the template to express both "what mode" and "what are the entries"; the dict-or-not approach collapses both into one field. It also keeps the data flow one-way: templates produce, partial consumes.

### D3 — `<a href>` for navigation entries; JS only enriches

**Decision:** In navigation mode, popover entries are `<a href="{{ target }}" data-lang="{{ lang }}">`. The popover JS:

1. Intercepts the click.
2. Writes `localStorage["garden-lang"]` and `data-pref-lang` to `data-lang`.
3. Lets the browser follow the link normally (no `preventDefault()` unless the click was on the current page itself).

If JS is disabled, the click follows the `href` directly and the preference is not updated. That is acceptable: the reader navigates, which is the headline action; the preference write is best-effort enrichment per ADR-0007 bar 2 (graceful degradation).

**Rationale:** This is the smallest surface that satisfies both goals — works without JS and persists preference with JS. Keeping the elements as `<a>` (not `<button>`) is also the right semantics: they are now navigation links, not action buttons.

### D4 — Picker contents: only languages with targets; current language is the trigger label, omitted from popover

**Decision:**

- `header_lang_links` does not include the current language. The trigger button still displays the current language (e.g. `EN`); the popover lists only alternatives.
- On a single-language post (or any page where no alternative target exists), `header_lang_links` is empty. The trigger button still renders, showing the current language; the popover is empty and never opens.
- Mirrors the "Available in" line, which already only lists existing translations.

This is the user-chosen "hide missing entries entirely" strategy.

**Alternatives considered:**

- *Show all `SITE_LANGS`, disable missing*: explicit, but requires a disabled visual state and the click-does-nothing affordance is easy to misread as broken.
- *Soft-fallback to `/<lang>/`*: never a dead end, but silently lands the reader somewhere unrelated.
- *Route via 404 inference*: pollutes 404 logs, misleading URLs.

### D5 — Implicit preference write on click

**Decision:** Clicking a navigation entry writes `localStorage["garden-lang"]` (and `data-pref-lang` for the current document) **before** the browser navigates. This is the user-chosen "navigator + implicit preference write".

**Rationale:** The 404 page and the multi-lang tag-prose page rely on the stored preference to choose which `<section data-lang>` to show first. If the reader's last cross-lang action was "click PT on `/hello-garden/` to read `/ola-jardim/`", their next visit to the 404 should default to PT — that's the principle of least surprise. Writing on the navigation click is the only place to capture that intent now that the dedicated preference button no longer exists.

**Risk:** A side-effect on a navigation click is invisible (the reader doesn't see they "set a preference"). Mitigated by:

1. Keeping the existing `pref-lang-menu` UI, which means readers who poke at the picker on a section-toggle page still see and feel a preference change directly.
2. The default preference is still derived from the URL prefix, so the side-effect's effect is subtle: the reader has to reach a page without an explicit lang for the persisted value to matter.

### D6 — `header_lang_links` is computed in templates by default; plugins inject it only where they own the context

**Decision:**

- `article.html`: derives from `article.translation_group` directly in Jinja.
- `page.html`: derives from `page.translations` in Jinja.
- `index.html` (cross-lang home): derives from `SITE_LANGS` mapping each lang to `/<lang>/`.
- `tags_list.html`: derives from `SITE_LANGS` (cross-lang case → `/<lang>/tags/`; per-lang case → omitting current lang and offering `/<other>/tags/`).
- `lang_index.html`: derives from `SITE_LANGS` minus `page_lang`, mapping each to `/<lang>/`.
- `tag_lang_index.html`: derives from `tag_langs` minus `page_lang`, mapping each to `/<lang>/tag/<tag_slug>/`.
- `tag_group_index.html`: when `all_prose | length < 2`, derives from `tag_langs` mapping each to `/<lang>/tag/<tag_slug>/`. When `all_prose | length >= 2`, **does not set** `header_lang_links` (section-toggle mode for the prose).
- `404.html`: never sets `header_lang_links`.

No plugin signature changes. The contexts that already pass `tag_langs`, `tag_slug`, `page_lang`, `all_prose`, `SITE_LANGS`, `articles`, `pages`, etc. are sufficient — `header_lang_links` is one `{% set %}` away.

**Rationale:** Keeps plugin code unchanged. The cost is a small amount of repeated derivation logic in templates — acceptable, since a Jinja macro can extract any duplication.

### D7 — Per-page lang-links bar coexists with the new header picker

**Decision (per user choice):** The lang-links bar from `add-page-lang-links` stays. The bar's "All · EN · PT" affordance includes the cross-language "All" entry, which the header picker deliberately does not (the picker is a *language* picker — "All" is a *scope*). The two surfaces are not duplicates: they overlap on per-language entries but the bar offers a scope (All) that the header doesn't.

**Trade-off accepted:** Two click targets reach the same `/pt/` URL on a per-language home. We accept the visual redundancy in this iteration in exchange for a smaller change footprint and an unbroken bar that readers may already rely on. Collapsing the two surfaces is a future change (and would warrant its own ADR).

### D8 — ADR-0010 records the navigator-vs-preference reversal

**Decision:** Add `openspec/decisions/0010-header-lang-picker-as-navigator.md` (Status: Accepted), which:

- Records the reversal of `add-user-preferences` design decision D5 ("Language preference button does not redirect").
- Records that the picker is now a navigator with an implicit preference-write side-effect.
- Names the cases where current behaviour is preserved (404, multi-lang tag-prose).
- Updates `openspec/decisions/README.md` index.

Per the ADR convention in `add-page-lang-links`'s precedent, the prior decision is not edited; ADR-0010 cites it as superseded.

## Risks / Trade-offs

- **[Risk] Hidden side-effect on navigation click** (D5) → Mitigation: documented in ADR-0010; the section-toggle path on no-canonical-lang pages still gives readers an explicit, visible way to set the preference. We may revisit if telemetry suggests confusion.
- **[Risk] Navigation/preference races on slow connections** (the localStorage write happens synchronously before navigation, but on a flaky network the writer could be interrupted mid-`setItem`) → Mitigation: `setItem` is synchronous and writes complete before the navigation request is dispatched in all major browsers; the existing `try/catch` already covers private-mode failures.
- **[Risk] Two surfaces (header picker + per-page bar) drift visually or behaviourally** (D7) → Mitigation: keep the bar's spec-level "Bar entries are independent of the header lang preference toggle" scenario explicit so future changes don't accidentally couple them; revisit collapse in a future change.
- **[Risk] Missing-translation entries hidden, reader can't reach `/<lang>/` from the picker on a single-lang post** (D4) → Mitigation: the per-page lang-links bar (D7) is exactly that affordance — preserved precisely so readers retain a path to per-language scopes from any page.
- **[Trade-off] Repeated `header_lang_links` derivation across templates** (D6) → Mitigated with one Jinja macro if duplication grows; for now (six templates, simple expressions) inlined `{% set %}` blocks are clearer than an indirection.
- **[Risk] `add-user-preferences` user-preferences spec carries scenarios that contradict the new behaviour** ("Clicking does not redirect", "Clicking cycles to next language") → Mitigation: this change's user-preferences spec delta is the canonical update; both scenarios are removed/replaced as part of the spec sync at archive time.

## Migration Plan

This is a behavioural refactor of a client-side control on a small static site. There is no data migration, no schema change, no rollback target.

**Order of operations during apply:**

1. Add ADR-0010 and update the ADR README index.
2. Extend `i18n_grouping/__init__.py` per-language-index render context to inject `header_lang_links` (or do it template-side in `lang_index.html` — see tasks.md for the chosen path).
3. Extend `tag_pages/__init__.py` similarly for `tag_lang_index.html` and `tag_group_index.html`.
4. Update each page template (`article.html`, `page.html`, `index.html`, `tags_list.html`, `lang_index.html`, `tag_lang_index.html`, `tag_group_index.html`) to set `header_lang_links` per D6.
5. Update `base.html` to render the picker in navigation vs. section-toggle mode based on `header_lang_links`.
6. Update `_pref_controls_script.html` to write the preference on navigation-mode clicks before letting the browser follow the link, and preserve the section-toggle path otherwise.
7. Update `styles.css` to cover `<a>` entries alongside `<button>` entries in the popover.
8. Manual smoke test (TTY): visit `/`, `/hello-garden/`, `/ola-jardim/`, `/en/`, `/pt/`, `/tag/poetry/`, `/en/tag/poetry/`, `/pt/tag/poetry/`, `/tags/`, `/en/tags/`, `/404.html` and confirm picker behaviour matches each spec scenario.

**Rollback:** revert the change set; no external state is touched.

## Open Questions

- Should the picker's trigger button render at all when `header_lang_links` is empty *and* the page is in navigation mode (single-lang post)? Current decision in D4: yes, render the trigger as a static label, no popover. Re-visit if it looks visually broken in practice.
- The cross-lang tag page (`tag_group_index.html`) toggles between modes based on `all_prose | length`. Worth keeping in mind that adding a second-language tag-prose file on an existing single-lang tag silently flips the picker behaviour. Documented in the spec scenarios so it is not a surprise.
