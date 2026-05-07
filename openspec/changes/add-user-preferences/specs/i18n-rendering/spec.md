## MODIFIED Requirements

### Requirement: The 404 page infers the reader's language from the URL

The 404 page SHALL include inline JavaScript that, on load, inspects `window.location.pathname` and prioritises the matching language section by hiding the others. With JS disabled, all sections remain visible — the page degrades gracefully per [ADR-0007](../../decisions/0007-small-clientside-js.md) bar 2.

The inference chain SHALL be ordered as follows, with the first matching stage winning:
1. `/<lang>/` prefix in the URL path
2. Stored language preference (`document.documentElement.dataset.prefLang`, populated from `localStorage` by the inline loader in `base.html`)
3. `navigator.language`'s 2-letter prefix
4. The document's `data-default-lang` attribute (final fallback)

#### Scenario: `/<lang>/` prefix prioritises that language
- **WHEN** the 404 is loaded for any path starting with `/<lang>/` (where `<lang>` is one of the site's languages)
- **THEN** only the section with `data-lang="<lang>"` is visible, and the document's `<html lang>` is set to `<lang>`. Stage 1 wins regardless of any stored preference.

#### Scenario: Stored language preference is consulted when the URL has no lang prefix
- **WHEN** the 404 is loaded for a path that does not start with `/<lang>/`, and `data-pref-lang` on `<html>` matches one of the site's languages
- **THEN** the section matching `data-pref-lang` is visible, and the document's `<html lang>` is set to it. Stage 2 beats `navigator.language` and the default fallback.

#### Scenario: Browser language preference is consulted when no URL prefix and no stored preference
- **WHEN** the 404 is loaded for a path with no `/<lang>/` prefix, no `data-pref-lang` is set, and `navigator.language`'s 2-letter prefix matches one of the site's languages
- **THEN** the section matching that language is visible, and the document's `<html lang>` is set to it.

#### Scenario: Unknown paths fall back to the default language
- **WHEN** none of stages 1–3 produce a match
- **THEN** the section matching the document's `data-default-lang` attribute is visible.

#### Scenario: With JS disabled, all sections remain visible
- **WHEN** the 404 is loaded with JavaScript disabled in the browser
- **THEN** every `<section data-lang>` element is rendered visible in the page (graceful degradation per ADR-0007 bar 2).

#### Scenario: No build-time per-slug payload is embedded
- **WHEN** `output/404.html` is inspected
- **THEN** it does not contain a slug-to-language map or any other per-article structure whose size grows with post count; the inference script relies only on the URL path, the site's language list, the stored preference attribute, and `navigator.language`.

#### Scenario: Inference script is inline and small
- **WHEN** `output/404.html` is inspected
- **THEN** the inference script lives in an inline `<script>` block (no external `.js` file is loaded), is under 50 lines, and does not load any external resources at runtime — per ADR-0007 bar 3.
