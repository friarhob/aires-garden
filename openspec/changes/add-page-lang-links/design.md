## Context

The header scope switcher was removed by `add-user-preferences` because its navigation behaviour had become confusing: clicking `EN` or `PT` always navigated to that language's home (`/en/` or `/pt/`), regardless of the page the reader was on. After the user-preferences change introduced a per-language toggle that *sets* the reader's preferred language without navigating, the scope switcher's job was no longer "set the language" — it was supposed to be "go to the equivalent page in this scope". But it never did that, and removing it left non-article pages with no in-page way to traverse the scope axis.

Article pages already solve this problem with an "Available in" line that lists each language the post exists in, with a link to that translation. This change applies the same pattern to non-article pages.

The affected templates are:

| Template | Scope | URL pattern |
|---|---|---|
| `index.html` | cross-language | `/` |
| `lang_index.html` | per-language | `/<lang>/` |
| `tag_group_index.html` | cross-language | `/tag/<slug>/` |
| `tag_lang_index.html` | per-language | `/<lang>/tag/<slug>/` |
| `tags_list.html` (cross) | cross-language | `/tags/` |
| `tags_list.html` (per-lang) | per-language | `/<lang>/tags/` |

`article.html` already has its "Available in" line and is **out of scope**.

## Goals / Non-Goals

**Goals:**
- Every non-article page exposes links to its equivalents in other language scopes (cross-language ↔ per-language, and per-language ↔ per-language).
- The current scope is visually distinguished from the others.
- The pattern uses the same visual language as the article-page "Available in" line so the site feels cohesive.
- Implementation is template-only; no plugin changes are required.

**Non-Goals:**
- Re-introducing the header scope switcher.
- Filtering links by per-page availability (e.g. hiding `/<lang>/tag/<slug>/` if no `<lang>` article has that tag). All `SITE_LANGS` entries are shown unconditionally, accepting that some links may 404 in degenerate cases — the multilingual 404 page handles that gracefully.
- Touching `article.html`.

## Decisions

### Decision 1: Inline URL construction in each template

Each of the five templates already has the context it needs (`page_lang`, `tag_slug`, `SITE_LANGS`) to build the URL list inline. A shared macro or include would either need to receive a URL pattern string (hacky) or be split per page-kind (no real reuse). Inline is simpler — six small blocks of templating that read straightforwardly.

**Alternative considered:** A `_page_lang_links.html` partial driven by a `page_kind` switch. Rejected because the per-template URL is one Jinja line in each case; centralising it adds indirection without saving lines.

### Decision 2: Show all `SITE_LANGS` unconditionally; do not filter by page existence

For tag pages, a per-language variant `/<lang>/tag/<slug>/` only exists if at least one article with `Lang=<lang>` carries that tag. We could pass `available_langs` from the plugin and filter the list — but this requires plugin changes contradicting the proposal's "template-only" intent.

Instead: link to all `SITE_LANGS` unconditionally. In the rare case a link points at a non-existent page, the multilingual 404 page handles the language inference (it picks up the `/<lang>/` URL prefix per Stage 1) and the reader sees a friendly "not found" in the right language.

**Alternative considered:** Pass an `available_langs` set from the tag-pages plugin and filter the list. Rejected for now because (a) it requires plugin changes, (b) the site has two languages and the degenerate case is uncommon, (c) we can revisit if it becomes a real problem.

### Decision 3: Hide the line when `SITE_LANGS` has only one entry

If the site is mono-lingual at the moment, an "Also in: All / EN" row is degenerate (the cross and the only per-language scope are the same content). Mirror the article-page rule: **hide the line if `SITE_LANGS | length < 2`**.

### Decision 4: Markup matches the article "Available in" line

Reuse the existing `p.available-in` CSS class with a slightly different wrapper class (`p.page-langs`) so the visuals stay coherent. `p.page-langs` can either alias the same CSS or carry a small variant rule. Implementation will copy/share the rule rather than reimplement it.

The current scope link gets `class="page-lang-current"` which is styled to be visually distinct (e.g. unlinked, accent colour, no underline) — the rule mirrors the popover's `[data-current]` indicator pattern from `add-user-preferences`.

### Decision 5: Scope label is "All" / `<lang>.upper()`

Use the same labels the old scope switcher used: `All` for cross-language, `EN`/`PT` for per-language. Keeps the visual idiom consistent with the lang popover button labels.

### Decision 6: The line lives near the top of content, after `<h1>`

Position the lang-links bar between the page heading and the page list/prose. This puts it where the reader would naturally look for "this page in other languages" navigation — same as where article pages put their "Available in" line.

## Risks / Trade-offs

**Some links may 404** (per Decision 2) → mitigated by the multilingual 404 page's language inference; the reader still ends up on a page that talks to them in their language.

**Visual clutter on tag pages** — tag pages already carry tag-prose, a list, and a date. Adding a lang-links bar adds a fifth visual stratum → mitigated by using the same low-emphasis muted-text style as `p.available-in`, and by keeping the bar to a single line.

**Future divergence between article and non-article patterns** — articles use "Available in: EN, PT" (lang-only, no "All"), non-article uses "Also in: All, EN, PT" (with "All" entry). The asymmetry is intentional: articles only exist per-language so there's no cross-language scope to show, whereas non-article pages have a meaningful cross/per-lang split. The two rendering rules are documented separately in the spec.

## Migration Plan

This is a template-only change with no breaking effects on existing URLs or output. Steps:
1. Add the lang-links rendering to each affected template.
2. Add CSS for `.page-langs` and `.page-lang-current`.
3. Build locally and visually inspect every page kind.
4. Commit.

Rollback: revert the template/CSS commit. No plugin or config rollback needed.

## Open Questions

None at design time.
