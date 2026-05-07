## Context

The Garden is a Pelican static site served via GitHub Pages with no server-side session or cookie infrastructure. All user-preference logic must live entirely in client-side JavaScript. The existing theme system uses a `data-theme` attribute on `<html>`; the existing language inference uses an inline `<script>` partial (`_lang_inference_script.html`) that reads `navigator.language`. Both touch points are already in templates and need to be extended, not replaced.

## Goals / Non-Goals

**Goals:**
- Persist theme preference across page loads and browser sessions using `localStorage`.
- Persist language preference across page loads and browser sessions using `localStorage`.
- Apply both preferences before first paint to prevent any flash of wrong theme or wrong language.
- Expose both controls as visible UI in the site header.
- Override `navigator.language` fallback in the JS lang-inference logic with the stored preference.

**Non-Goals:**
- Server-side sessions, cookies, or any backend infrastructure.
- Account system or syncing preferences across devices.
- More than two preference values per control (theme: dark/light; language: EN/PT).
- Internationalising the control labels (they use the language code itself as the label).

## Decisions

### D1 — `localStorage`, not cookies

**Decision:** Store both preferences in `localStorage` under keys `garden-theme` and `garden-lang`.

**Rationale:** `localStorage` requires no expiry management, no `Set-Cookie` header, no server round-trip, and is simpler to read synchronously in an inline script. Cookies would add complexity (expiry, path, SameSite) with no benefit for a fully static site.

**Alternatives considered:**
- *`sessionStorage`*: Doesn't persist across tabs or closed sessions. Rejected.
- *URL query params*: Would pollute links and break when sharing URLs. Rejected.

### D2 — Inline loader script in `<head>`, before any CSS or body

**Decision:** A small synchronous `<script>` block is placed in `<head>` — after the `<meta>` tags but before the font and stylesheet `<link>` tags — that reads `localStorage` and applies `data-theme` to `<html>` immediately.

**Rationale:** This is the only reliable way to prevent FOUC (flash of un-themed content). Any deferred or `DOMContentLoaded` approach will flash the default theme first.

**Structure:**
```js
(function () {
  var t = localStorage.getItem('garden-theme');
  if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
  var l = localStorage.getItem('garden-lang');
  if (l) document.documentElement.dataset.prefLang = l;
}());
```

`data-pref-lang` is set on `<html>` so the lang-inference script can read it as a DOM attribute rather than calling `localStorage` again (avoids a second storage read inside the partial).

### D3 — Controls live in the site header, right-aligned

**Decision:** The theme toggle and language selector are placed inside the existing `<header>` element, after the `.scope-switcher` nav. They are rendered as a `<div class="prefs">` containing a `<button class="pref-theme">` and a `<button class="pref-lang">`.

**Rationale:** The header is the one element present on every page. Right-aligning them keeps them accessible without cluttering the main content area.

**Theme toggle label:** Shows the opposite of the current state — "Light" when dark is active, "Dark" when light is active — so the label reads as an action, not a state.

**Language button label:** Shows the currently preferred language code (EN / PT). Clicking cycles to the other. When no preference is set, shows the default language.

### D4 — Language preference replaces `navigator.language` in the inference chain

**Decision:** The existing inference chain in `_lang_inference_script.html` is extended with one new stage that sits between the URL-prefix check and the `navigator.language` check:
```
Stage 1: /<lang>/ prefix in URL              ← existing, highest priority
Stage 2: data-pref-lang attribute on <html>  ← new, beats navigator.language
Stage 3: navigator.language                  ← existing, now a deeper fallback
Fallback: defaultLang                        ← existing
```

**Rationale:** An explicit URL scope expresses an explicit reader intent ("show me PT") and must always win. The stored preference is meaningful only as a replacement for the browser default — it improves on `navigator.language` (which can be wrong, especially on shared machines) but it does not override what the URL says.

Reading from `data-pref-lang` (set by the inline loader in D2) keeps the inference script free of direct `localStorage` calls, which is cleaner and avoids the partial needing to know about storage keys.

### D5 — Language preference button does not redirect

**Decision:** Clicking the language preference button updates `localStorage` and `data-pref-lang` on the current page only. It does not redirect the reader to a scoped URL (e.g. `/en/` → `/pt/`).

**Rationale:** A redirect on click would mix two concerns — preference setting and navigation — and would surprise readers who clicked the button just to change a default. The scope switcher (existing nav) is the established mechanism for actively navigating between language scopes; the preference button is purely a default-setter that takes effect on the next cross-language page the reader visits.

## Risks / Trade-offs

- **`localStorage` unavailable** (private browsing in some browsers, storage quota exceeded) → Wrap all storage reads/writes in `try/catch`; fall back to current behaviour silently.
- **FOUC on very slow connections** → The inline loader script is synchronous and tiny (<200 bytes minified); render-blocking is negligible.
- **Two-language assumption** → The language button cycles between exactly two languages. If a third language is ever added, the cycle logic needs updating. Acceptable for now; the `SITE_LANGS` Pelican variable already governs what languages exist and can drive the cycle list dynamically via Jinja.
- **Header crowding on small screens** → Three elements (site name, scope switcher, prefs) may be tight on mobile. A media query can hide labels and show icons only below a breakpoint; deferred to a later change.
