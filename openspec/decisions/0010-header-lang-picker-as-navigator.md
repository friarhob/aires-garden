# ADR-0010: Header language picker is a translation-aware navigator

## Status

Accepted — 2026-05-10. Overrides `add-user-preferences` design decision D5 ("Language preference button does not redirect").

## Context

`add-user-preferences` (archived 2026-05-07) shipped a header language picker as a *preference toggle*: clicking an entry wrote `localStorage["garden-lang"]` and `data-pref-lang` and nothing else. The visible URL never changed. The intent recorded in D5 was to keep preference-setting and navigation cleanly separate — the per-page lang-links bar (`add-page-lang-links`, archived the same day) and the article "Available in" line were the navigation surfaces; the header button was for setting a default that mattered only on pages whose canonical language is determined client-side (the multilingual 404, and cross-language tag-prose pages where `<section data-lang>` blocks are toggled in-place).

In practice the separation read as a bug. Clicking the language picker in the header is the most visible language affordance on the site; readers reasonably expect it to take them to the equivalent page in the chosen language. They do not expect a silent preference change with no visible effect. The "Available in" line on articles works, but readers have to look for it; the per-page lang-links bar exists on non-article pages but is one of two visually similar mechanisms in the same viewport, and which one navigates is not discoverable from the UI itself.

The roadmap's `refactor-language-selector` entry frames the same observation: the picker shows all supported languages but doesn't navigate. The fix is to make the picker translation-aware.

The choice this ADR records is *directional*: which job is the header picker doing? Two clean answers exist (pure-navigator, pure-preference-toggle); D5 picked the latter, and we now reverse to the former with a small implicit-preference-write side-effect to preserve continuity for the pages that genuinely need a stored preference.

## Decision

The header language picker is a **translation-aware navigator**. Its behaviour splits along whether the current page has a single canonical language at build time:

1. **Navigation mode** (any page whose canonical language is known at build time — articles, pages, per-language indexes, per-language tag indexes, the cross-language home, the cross-language all-tags list, and the cross-language tag page when its tag-prose has fewer than two language sections): the picker popover lists only languages with an existing target on the current page, rendered as `<a href>` entries. Clicking writes `localStorage["garden-lang"]` and `data-pref-lang` synchronously, then lets the browser follow the `href`.
2. **Section-toggle mode** (the multilingual 404 page, and the cross-language tag page when its tag-prose has two or more language sections — i.e. pages whose canonical language is not known at build time): the picker behaves as it did under D5. The popover lists every entry in `SITE_LANGS` as `<button>` elements; clicking writes the preference and toggles `<section data-lang>` visibility. No navigation.

Mode selection is driven by a per-page Jinja variable `header_lang_links` (a `{lang: url}` mapping). When set and non-empty, the header partial renders navigation mode; when not set, it falls back to section-toggle mode.

The per-page lang-links bar from `add-page-lang-links` remains. It and the picker overlap on per-language navigation entries; the bar additionally offers a cross-language "All" entry the picker does not. Collapsing the two surfaces is deferred.

D5 of `add-user-preferences` is overridden. The user-preferences spec is updated accordingly in the change `refactor-language-selector`.

## Consequences

**Positive:**

- The header picker now does what readers expect on every page where a meaningful target exists. The principle-of-least-surprise is restored.
- Missing translations are simply absent from the popover (mirroring the article "Available in" line), so the picker contents communicate available-translation reality directly. No disabled/greyed states; no dead-end clicks.
- Section-toggle behaviour is preserved exactly where it is needed (404 + multi-lang tag-prose) — readers on those pages still get a meaningful click effect, even though no canonical target exists to navigate to.
- The `localStorage["garden-lang"]` semantics survive: the 404 inference chain and the lang-inference script in multi-lang tag-prose pages still consult the stored preference. We have only changed *who writes* the preference (the navigation click now writes it as a side effect).

**Negative:**

- A side-effect (preference write) on a navigation click is invisible — readers don't see they have set a default. Mitigated because the section-toggle path on no-canonical-lang pages still surfaces a visible, explicit preference change; readers who poke at the picker on those pages experience the write directly.
- Two surfaces (header picker + per-page lang-links bar) now overlap on navigation. The bar is retained because it offers an "All" cross-language entry the picker does not, and because removing it from a recently-shipped change costs more than the visual redundancy. A future change may consolidate.
- Reverses a deliberate UX decision shipped only days earlier (D5 was archived 2026-05-07, this ADR dates 2026-05-10). The cost of the reversal is low — readership is small, the change is local — but it does mean the site's behaviour changed twice in close succession on this surface.

**Alternatives rejected:**

- **Disabled-state for missing translations.** Rejected: a popover entry that does nothing on click reads as broken even when the disabled affordance is rendered correctly. The "hidden when missing" approach matches how the article "Available in" line already behaves and so is easier to learn.
- **Soft-fallback navigation to `/<lang>/` for missing translations.** Rejected: the click silently lands the reader somewhere unrelated; this is worse than an absent entry because the reader expected the equivalent of *this* page.
- **Pure-navigator with no preference write.** Rejected: 404 and multi-lang tag-prose pages need a stored preference to choose which `<section data-lang>` to show first. Without the implicit write on navigation, there is no other surface that captures recent reader intent.
- **Move the navigation affordance to a different surface (e.g. expand the per-page lang-links bar onto article pages too) and keep the header as a preference toggle.** Rejected: addresses the missing-navigation gap but does not fix the surprise-cost of the header picker doing nothing visible. The header is the most visible lang surface; that is the surface readers reach for.

**Examples of cases that fall out of this decision (illustrative):**

- Reader on `/hello-garden/` (EN) clicks `PT` in the header picker → browser navigates to `/ola-jardim/`; on next visit to a 404 their default is PT.
- Reader on a single-language post (only EN exists) — popover has no entries; the trigger still labels the current language. The per-page lang-links bar (on non-article pages) and "Available in" line (on articles) remain the discovery affordances for cross-language scope.
- Reader on `/tag/poetry/` where the tag-prose has both EN and PT sections — picker stays in section-toggle mode (D5-era behaviour); the per-page bar still navigates between `/tag/poetry/` and `/<lang>/tag/poetry/`.
- Reader on the multilingual 404 page — picker behaves as before this ADR; clicking writes the preference and toggles the visible section. No navigation is attempted because no canonical target URL exists.
