## Status

Design decisions recorded below.

## Context

`openspec/project.md` (item 8 of the proposal order, "Custom content tags — MDX-equivalent for Pelican") sketched a `{{ tagname arg=value }}` preprocessor with starter tags `figure`, `youtube`, `callout`. Two refinements were made before scoping this change:

1. **Markdown can already do most of it.** Quotes, code blocks, lists, tables, headings, and basic images are all native Markdown. Callouts have a well-supported Python-Markdown extension (`admonition`). Figures-with-captions can be produced by an extension (`markdown_captions` or equivalent) that recognises Markdown's existing image-with-title syntax `![alt](src "caption")`. The genuinely-novel surface is **embedded media** (YouTube, generic iframes) — those have no Markdown expression.
2. **Tag delimiter is settled.** The `{{ }}` form proposed in the brief is fine but `[!name arg=value]` was chosen for being shorter while still unambiguous (the `!` sigil disambiguates from Markdown reference-link `[name]` and link `[text](url)` syntax).

Constraints:
- Pelican 4.x, Python-Markdown for body rendering; theme is Jinja2.
- Existing plugins (`frontmatter_lint`, `i18n_grouping`, `multilingual_404`, `dev_drafts`, `tag_pages`) live under `plugins/<name>/` and are listed in `pelicanconf.py:PLUGINS`.
- `frontmatter_lint` already gates `make build` and `make lint`; build aborts on any validation error before HTML is written.
- Multilingual: posts and pages exist per-language; embed tags must work identically across languages.
- Tokens already exist for accent / muted / border / bg-subtle (see `themes/garden/static/css/styles.css` lines 1–60).

## Goals / Non-Goals

**Goals:**
- Author ergonomics: callouts and figures use Markdown-native syntax; embeds use a short, unambiguous tag.
- Build-time safety: typos in embed tag names or missing required args fail the build with a file-anchored error before deploy.
- Theme integration: rendered HTML hooks into existing tokens; no new token surface.
- Maintainability: embed registry is one Python file; adding a new tag is < 30 lines.

**Non-Goals:**
- Inline embedding inside paragraphs. All embed tags are block-level (their own line).
- Tag bodies / closing tags (e.g. `[!quote]…[!/quote]`). All embeds are self-contained, single-line.
- Author-facing documentation. The `embeds-demo` post (Status: hidden) is the worked example until `add-python-cli` consolidates the authoring guide.
- Provider-specific oEmbed integration (e.g. auto-fetching YouTube titles). Embeds are static HTML expanded from arg values only.
- Image optimisation / responsive `srcset` for figures. Deferred to `add-image-pipeline`.

## Decisions

### Decision 1: Tag syntax is `[!name arg=value]` with key=value args, all on one line

**Decision:** Embeds use `[!name key=value key2="quoted value"]`, must be on a line by themselves (whitespace-only allowed before/after on that line), and never span multiple lines.

**Why:** Disambiguates from Markdown's `[text](url)` and `[ref]` link syntaxes via the `!` sigil. Single-line constraint keeps the regex simple and avoids the need for Markdown-paragraph-aware parsing. Block-only matches every embed use case (YouTube, iframe).

**Alternatives considered:**
- `{{ name arg=value }}` (project.md default): zero collision but two more characters per delimiter and the brace looks Jinja-ish to readers who know the template layer.
- `[name arg=value]` (plain brackets, no sigil): collides with Markdown reference links; we'd have to either constrain to "alone on a line" *and* hope no editor highlights it as a malformed link, or run the preprocessor before Markdown sees the line.
- `{{< name arg=value >}}` (Hugo shortcode): unambiguous but verbose.

### Decision 2: Preprocess BEFORE Markdown parsing via Pelican `readers.signals.readers_init`

**Decision:** The `content_tags` plugin subscribes to Pelican's reader-init signal and wraps the Markdown reader so embed tags are expanded into HTML *before* `markdown.Markdown()` parses the body. The replacement HTML uses `<div>` / `<figure>` block-level wrappers that Python-Markdown will not re-wrap in `<p>`.

**Why:** Post-Markdown rewriting (e.g. via `content_object_init`) produces `<p>[!youtube id="…"]</p>` first, then we'd have to unwrap the `<p>`. Pre-Markdown lets the rendered HTML participate cleanly in the surrounding document (so authors can put a paragraph immediately above an embed and Markdown will close that paragraph normally). Python-Markdown's "block-level HTML is left alone" rule does the right thing.

**Alternatives considered:**
- Hook on `content_object_init` and string-replace the rendered HTML: simpler to wire but produces the `<p>`-wrap problem; would require regex-stripping `<p>…</p>` around expanded tags, which is fragile (e.g. when a tag is followed by inline text on the next line, Markdown may not insert a `<p>` boundary at all).
- Custom Markdown `BlockProcessor` extension: the most "correct" Markdown integration but pulls us into Markdown's tree API for what is otherwise a flat string substitution. Overkill for two block-level tags.

### Decision 3: Registry is a Python dict mapping name → renderer dataclass

**Decision:** `plugins/content_tags/registry.py` exposes `REGISTRY: dict[str, EmbedTag]` where `EmbedTag` is a frozen dataclass with `required_args: tuple[str, ...]`, `optional_args: tuple[str, ...]`, and `render: Callable[[dict[str, str]], str]`. Each starter embed (`youtube`, `iframe`) gets its own module under `plugins/content_tags/embeds/` registering itself at import time.

**Why:** A small registry is enough for two tags and keeps the door open for `vimeo`, `bandcamp`, `gist` later. Frozen dataclass means the registry is read-only at runtime — the lint scanner imports the same registry and cannot accidentally mutate it.

**Alternatives considered:**
- Decorator-based registration (`@register("youtube")`): equivalent functionally but adds a layer; explicit dict-write is grep-friendly.
- One mega-function with a switch: violates the "< 30 lines per new tag" goal.

### Decision 4: Lint reuses the same registry; no duplicated argument-name lists

**Decision:** `frontmatter_lint` grows a body-content scanner that imports `plugins.content_tags.registry.REGISTRY` and walks each post / page / tag-prose body looking for `[!…]` lines. For each match it validates: (a) name exists in registry, (b) all `required_args` present, (c) every supplied key is in `required_args ∪ optional_args` (unknown keys fail). Errors flow through the existing file-anchored error reporter.

**Why:** Duplicated argument lists in the lint module would inevitably drift from the renderer. Sharing the registry means renderers and lint always agree.

**Alternatives considered:**
- A separate JSON schema file for lint to consume: more ceremony, two sources of truth.
- Lint by attempting to render and catching exceptions: hides typos in argument names (renderers might silently ignore unknown keys via `**kwargs`); explicit name-set validation is more honest.

### Decision 5: YouTube uses `youtube-nocookie.com`, requires `id`, optional `start`

**Decision:** `[!youtube id="dQw4w9WgXcQ"]` renders:
```html
<div class="embed embed-youtube">
  <iframe
    src="https://www.youtube-nocookie.com/embed/{id}?rel=0[&start={start}]"
    title="YouTube video"
    loading="lazy"
    referrerpolicy="strict-origin-when-cross-origin"
    allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    allowfullscreen></iframe>
</div>
```

**Why:** Privacy-by-default (no cookies until interaction), `loading="lazy"` for perf, no `start=0` query param when omitted, `rel=0` to suppress cross-channel related videos. `id` is the minimum useful contract; `start` is the most-asked next field.

**Alternatives considered:**
- Accept full `https://youtube.com/watch?v=…` URLs and parse: more author-friendly but adds a parser; YouTube id is short and stable, just paste it.
- Default `loading="eager"`: penalises page-weight for above-the-fold pages with multiple embeds; lazy is strictly better for a digital-garden read pattern.

### Decision 6: Generic iframe requires `src` and `title`; height optional with sensible default

**Decision:** `[!iframe src="..." title="..." height="400"]` renders:
```html
<div class="embed embed-iframe">
  <iframe
    src="{src}"
    title="{title}"
    loading="lazy"
    referrerpolicy="no-referrer-when-downgrade"
    sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
    style="height: {height}px"></iframe>
</div>
```

`title` is **required** for accessibility (WCAG 4.1.2). `height` defaults to `400` if omitted. `src` is HTML-escaped but otherwise not URL-validated at lint time (intentional — author owns trust).

**Why:** Sandbox is set restrictive-by-default but allows the common cases (Bandcamp, Observable, demo iframes). Authors who need looser sandboxing can add raw HTML.

**Alternatives considered:**
- `width` + `height` percentage: `width:100%` is enforced via CSS on `.embed iframe`, so making it an arg is redundant and a footgun (mismatch with container).
- Default `sandbox="allow-scripts"` only: too restrictive for typical embed cases (Observable needs same-origin for module loading).

### Decision 7: Markdown extensions list — admonition + markdown_captions, plus extras

**Decision:** Configure `MARKDOWN['extensions']` to include:
- `markdown.extensions.extra` (already implicit in many Pelican configs; explicit here): tables, attr_list, fenced_code, footnotes, abbr, def_list, md_in_html.
- `markdown.extensions.admonition`: enables `!!! note "Title"` callout blocks.
- `markdown.extensions.codehilite` (via `extra` or explicit): keeps fenced code blocks themable later (no Pygments stylesheet emitted in this change).
- `markdown_captions` (or chosen equivalent): promotes `![alt](src "caption")` to `<figure><img …><figcaption>`. If the chosen package is unmaintained or behaves badly, the fallback is a tiny in-tree extension that does the same `<img>` → `<figure>` rewrite (~30 lines).

`MARKDOWN['extension_configs']` configures `codehilite` with `css_class: highlight` and `linenums: false`.

**Why:** Admonition is the most-used Python-Markdown extension and produces clean HTML (`<div class="admonition note"><p class="admonition-title">…</p>…</div>`). Markdown's existing image-with-title syntax (`![alt](src "title")`) is the most elegant path to `<figcaption>` — extensions that promote it preserve that ergonomic.

**Alternatives considered:**
- pymdown-extensions (`!!! note "Title"` superset, plus tabs / details / superfences): bigger surface, more dependencies, but well-maintained. Reserved for if standard `admonition` is too thin in practice.

### Decision 8: Styling reuses tokens — no new token surface

**Decision:** New CSS rules in `themes/garden/static/css/styles.css` for `.admonition`, `.admonition-title`, variant classes (`.note`, `.warning`, `.tip`, `.danger`), `figure` + `figcaption`, `.embed`, `.embed iframe`. All colour, border, and font-size values reference existing tokens (`--accent`, `--text-muted`, `--border`, `--bg-subtle`, `--font-body`).

**Why:** `add-design-tokens` is the source of visual identity; adding embed-specific tokens here forks the contract. If a callout needs a colour the current palette doesn't express, that's a token-level proposal first.

**Alternatives considered:**
- Per-variant accent tokens (`--callout-note-accent`, `--callout-warning-accent`): defers a real palette decision to this change, where it doesn't belong.

## Risks / Trade-offs

- **Risk:** Pre-Markdown regex substitution mishandles a tag inside a fenced code block (where the author *wants* the literal `[!youtube id="…"]` to render).
  → **Mitigation:** The regex skips fenced-code regions by tracking ``` and indented (4-space) code blocks before scanning. Tested explicitly.

- **Risk:** Chosen figure-caption extension (`markdown_captions`) is unmaintained or has incompatible Markdown version pinning.
  → **Mitigation:** Decision 7 names the fallback (in-tree extension). The `pyproject.toml` change is reversible; we can pin a known-good version or vendor the extension.

- **Risk:** `loading="lazy"` interacts poorly with iframe-driven JS that expects a synchronous load.
  → **Mitigation:** Authors hitting this can use raw HTML; it's an escape hatch we explicitly preserve. Document in the embeds-demo post.

- **Risk:** Lint scanner mistakes a literal `[!something]` mention inside a quoted Markdown blockquote for a real embed tag and fails the build.
  → **Mitigation:** The scanner uses the same fenced-code skipping as the renderer. Blockquotes are still scanned (they're rare in author intent and the prefix `>` is easy to detect if false positives appear in practice — lint can extend then).

- **Trade-off:** Single-line tag syntax forecloses inline embeds (e.g. emoji shortcodes `[!emoji name="sparkles"]` mid-paragraph).
  → **Accepted:** No current author need; reopen if a real use case appears.

- **Trade-off:** No author-facing reference doc shipped in this change. `embeds-demo` post is the only worked example.
  → **Accepted:** Per the user-memory note "Authoring guide deferred to add-python-cli."

## Migration Plan

No migration needed. This is additive: existing posts continue to render unchanged. Once the plugin is enabled, authors can adopt admonition / figure / embed syntax incrementally. The build will fail only for content that uses the new `[!…]` syntax incorrectly — no pre-existing content uses it.

Rollback: remove the plugin from `PLUGINS`, drop the new `MARKDOWN` extensions, revert the CSS additions. Posts using `!!!` callout syntax would render as literal `!!! note` text (ugly but harmless); posts using `[!youtube …]` would render as literal `[!youtube …]` text. Author can either revert their content or re-enable the plugin.

## Open Questions

- Which figure-caption extension (`markdown_captions` vs in-tree) to pick: decided during implementation by trying `markdown_captions` first; fall back to in-tree if it misbehaves.
- Whether to pre-emptively add `vimeo` / `bandcamp` to the registry: deferred. Add when a real post needs them.
