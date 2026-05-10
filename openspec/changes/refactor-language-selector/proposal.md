## Why

The header language picker added in `add-user-preferences` is purely a preference-toggle: clicking PT on `/hello-garden/` (the EN version of a post that also exists as `/ola-jardim/` in PT) does nothing visible — the URL stays put, only `localStorage["garden-lang"]` and `data-pref-lang` change. Readers expect a language picker to take them to the equivalent page in that language. The current behaviour is surprising, easy to misread as broken, and forces readers to find the small "Available in" line below the title (or the per-page lang-links bar) to actually navigate.

This change refactors the header picker to be **translation-aware**: clicking a language navigates to the equivalent page when one exists, while preserving the existing in-page section-toggle behaviour on pages that genuinely have no single canonical language (the multilingual 404 page; cross-language tag pages whose tag-prose is rendered as `<section data-lang>` blocks).

## What Changes

- **BREAKING (UX):** The header language picker becomes a navigator. Clicking an entry follows a real `href` to the equivalent page in the chosen language. Supersedes the `add-user-preferences` decision D5 ("Language preference button does not redirect") via a new ADR.
- The picker on each page lists **only languages with an existing target** (mirrors the article-page "Available in" line). Single-language pages get a single-entry picker (or hidden, see design.md).
- Clicking an entry **also writes** `localStorage["garden-lang"]` and `data-pref-lang` so the choice persists for pages whose language is inferred client-side (the 404 page; cross-language tag-prose with multi-lang sections).
- Pages without an explicit canonical language — `output/404.html`, and the cross-language tag page `/tag/<slug>/` when its tag-prose has multiple `<section data-lang>` blocks — **keep current behaviour**: the picker shows all `SITE_LANGS`, clicking toggles section visibility and writes the preference (no navigation, because there is nowhere to navigate to).
- Templates expose a per-page `header_lang_links` mapping (`{lang: url, ...}`) that the base template reads; when absent, the base template falls back to the section-toggle behaviour. This is the contract between page templates and the header partial.
- The `i18n_grouping` and `tag_pages` plugins are extended to inject `header_lang_links` into the contexts of the per-language indexes and tag-language pages they render directly (everything else is computed in Jinja from existing context).
- The per-page lang-links bar from `add-page-lang-links` is **kept** alongside the new header behaviour. Two paths to the same destination is acceptable for this iteration; collapsing them is deferred.
- A new ADR (0010) records the navigator-vs-preference reversal and supersedes the relevant decisions in `add-user-preferences`.

## Capabilities

### New Capabilities

_None._

### Modified Capabilities

- `i18n-rendering`: New requirements for translation-aware header switching, including the `header_lang_links` template contract and the rule that splits navigation pages from section-toggle pages. The existing per-page lang-links-bar requirement gains a clarifying scenario noting the bar coexists with the header picker.
- `user-preferences`: The "Language preference control is visible in the site header" requirement is replaced. The new control is a translation-aware popover whose entries are real navigation links; clicking writes the preference as a side effect. The "Clicking does not redirect" scenario from `add-user-preferences` is removed (clicking now redirects when a target exists).

## Impact

- **Templates:** `base.html` switches the header lang picker from `<button>` entries to `<a href>` entries when `header_lang_links` is set; the section-toggle path is preserved as the fallback. `_pref_controls_script.html` is updated to navigate (rather than only setting `data-pref-lang`) when the entry has an href, and to keep the current toggle-and-write behaviour when it does not. `article.html`, `page.html`, `index.html`, `lang_index.html`, `tag_lang_index.html`, `tag_group_index.html`, `tags_list.html` set `header_lang_links` (via `{% set %}` or via context injection from plugins).
- **Plugins:** `i18n_grouping` injects `header_lang_links` into the per-language index context (`on_finalized` already builds these). `tag_pages` injects `header_lang_links` for tag-language and tag-group indexes. No new plugin.
- **CSS:** Switcher items become anchors; styles in `styles.css` need to cover `a` selectors alongside `button` selectors for the popover entries. No new tokens.
- **No content changes.** No URL changes. No build pipeline changes.
- **Decision log:** ADR-0010 records the navigator-vs-preference reversal and lists the superseded D5 decision in `add-user-preferences/design.md`. ADR README is updated.
- **Specs touched:** `i18n-rendering` (multiple new requirements + one modified scenario), `user-preferences` (one requirement modified, one scenario removed, one scenario added).
