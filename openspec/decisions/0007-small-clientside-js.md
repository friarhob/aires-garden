# ADR-0007: Small client-side JS is acceptable where the static-host constraint requires it

## Status

Accepted — 2026-04-30.

## Context

The project brief takes a default-no-JS posture:

> *Interactive components / JS islands. Pelican is templates-only; revisit if a real need emerges.*

Listed as an explicit deferral, alongside CMS-style admin UIs and image-pipeline tooling. The intent is to keep the site lean, accessible, fast, and free of the maintenance overhead that comes with shipping JavaScript on a static garden.

The `add-i18n-rendering` change surfaces the first concrete case where that posture meets a wall: GitHub Pages serves exactly one `output/404.html` for every unknown URL, and there is no server-side routing layer to pick a per-language 404 file based on the requested path. A multilingual site needs *some* mechanism to show readers a 404 in their language — at minimum, the language already encoded in the URL they typed (e.g. `/pt/missing/` should not produce an English-only 404). Static HTML+CSS alone cannot read `window.location` and prioritise per-language content; that requires JS.

Two responses are possible:

1. Accept that static-only multilingual 404 means "show all languages stacked" — never match the URL's language. Reader experience suffers (busy 404, native lang buried in a list), but the brief's posture stays unbroken.
2. Allow small inline JS for cases where the static-host constraint genuinely forces it — keeping the brief's spirit (templates-only by default) while opening a narrow, justified exception.

Without a documented decision, every future contributor who notices JS on the site has to either re-derive the rationale or treat the precedent as an open invitation.

## Decision

Small inline JS is permitted on this site, **only** where the static-host constraint genuinely prevents an HTML+CSS solution and the user-facing impact justifies the addition. Each addition crosses three bars:

1. **Static-host necessity.** The behaviour cannot be achieved by HTML+CSS alone given that the site is served by GitHub Pages with no server-side or edge-routing layer.
2. **Graceful degradation.** With JS disabled, the page must still be functional and meaningful, not broken or empty. JS enhances; it never gates basic content.
3. **Inline and small.** No bundlers, no frameworks, no external scripts loaded over HTTP. Each JS addition is a few dozen lines of inline `<script>`, reviewable in one pass.

## Consequences

**Positive:**

- The 404 page can show readers a localised message based on the URL they tried, while keeping the static-only stack underneath as a graceful-degradation fallback.
- The brief's templates-only spirit is preserved for default work — JS is the constrained escape hatch, not the default toolkit.
- Future contributors have a clear, documented bar to clear, instead of either treating "no JS, ever" as an absolute rule or taking the first JS addition as carte blanche.

**Negative:**

- The brief's "no JS" posture is now nuanced rather than binary; future-you must judge each case rather than apply a flat rule. Mitigated by the three explicit bars above.
- Any JS, however small, is a net-new attack surface and adds a small accessibility tax (screen-reader behaviour, JS-disabled visitors, slow connections). The "graceful degradation" bar exists specifically to limit this tax.
- Sets a precedent that some readers may stretch ("if 404 can have JS, why not X?"). The "static-host necessity" bar is the discriminator: if HTML+CSS plus per-page rendering can solve the case, JS is not justified, even if it would be slightly nicer.

**Examples of cases that DO pass the bar (illustrative, not exhaustive):**

- The 404 page's URL-driven language inference (the case that triggered this ADR).
- A future "copy permalink to clipboard" button — `navigator.clipboard.writeText` has no static fallback. (Acceptable if the link itself remains visible and selectable for manual copy when JS is off.)

**Examples of cases that do NOT pass the bar:**

- "Remember the reader's preferred language across visits" via `localStorage` — already solved by per-language indexes (`/<lang>/`) and the language switcher; no static-host constraint forces JS.
- Lazy-loaded images via JS — `loading="lazy"` attribute on `<img>` covers this without script.
- A search box with client-side index — could be approximated with browser-native find, or deferred until a real need; doesn't clear the necessity bar today.
- Theme toggling (light/dark) — `prefers-color-scheme` media query handles this in CSS; JS adds nothing the static path can't.

**Alternatives rejected:**

- **Strict no-JS, accept the multilingual 404 trade-off.** Rejected: the user-facing experience of "you typed a Portuguese URL, here's an English-only error message" is worse than the cost of ~15 lines of inline JS that gracefully degrades. The brief's deferral was "revisit if a real need emerges"; this is that revisit.
- **Open-ended JS allowance (no bars, just write JS when convenient).** Rejected: invites the slow drift toward heavier client-side surface that the brief was trying to avoid. The bars keep additions narrow and justified.
- **External JS file or script bundler.** Rejected: the additions contemplated are small enough to inline; an external file adds a network round-trip on the cache-cold path and a build artifact to track. If a future case ever genuinely needs more than a few dozen lines, that case is the moment to revisit, not today.
- **Move the site off GitHub Pages to a host with edge routing (Cloudflare Workers, Netlify Functions).** Rejected by [ADR-0005](0005-dns-stays-on-gandi.md)'s posture: stay on GH Pages until a real requirement justifies migration. The 404 problem alone doesn't.
