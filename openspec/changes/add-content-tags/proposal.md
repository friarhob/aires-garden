## Why

Posts already render basic Markdown, but recurring authoring needs — captioned figures, callouts, and embedded media (YouTube, generic iframes) — currently demand raw HTML, which is verbose to write, easy to typo, and inconsistent across posts. We want a small, opinionated way to express these constructs that stays Markdown-native wherever possible and falls back to a tiny custom-tag preprocessor only for things Markdown literally cannot express.

This is item 8 of the planned proposal order in `openspec/project.md`, refined: we keep the goal of "MDX-equivalent reusable embeds" but lean on Python-Markdown extensions for callouts and figures rather than reinventing them.

## What Changes

- **Enable Python-Markdown extensions** in `pelicanconf.py` / `publishconf.py` `MARKDOWN` config:
  - `admonition` — fenced callouts via `!!! note "Title"` / `!!! warning` / `!!! tip` syntax (rendered as `<div class="admonition note">…</div>`).
  - A figure-with-caption extension (e.g. `markdown_captions` or equivalent) — promotes `![alt](src "caption")` to `<figure><img …><figcaption>caption</figcaption></figure>` when a Markdown title is present.
  - Confirm `attr_list` and `tables` are on (they are part of `markdown.extensions.extra`); extend if Pelican is not already enabling them.
- **Add a `content_tags` Pelican plugin** at `plugins/content_tags/` that preprocesses post and page bodies before Markdown parsing and expands a small registry of inline embed tags using the syntax `[!name arg=value arg2="value with spaces"]`.
- **Starter embed tag set:**
  - `[!youtube id="..."]` — responsive 16:9 wrapper, `youtube-nocookie.com` host, `loading="lazy"`, no auto-play.
  - `[!iframe src="..." title="..." height="..."]` — generic responsive iframe with required `title` for accessibility.
- **Extend `frontmatter_lint`** (or add a sibling content-body lint pass) to scan post/page bodies for embed tags and **fail the build** on:
  - Unknown tag names (not registered in `content_tags` registry).
  - Missing required arguments per registered tag.
  - Malformed delimiters (`[!` without a closing `]` on the same line).
- **Style** admonitions, figures, and embed iframes via `themes/garden/static/css/styles.css` using existing design tokens — no new tokens introduced.
- **Author one verification post** (`content/posts/embeds-demo/`) under `Status: hidden` exercising one of each construct (admonition, figure, youtube, iframe) so the rendering can be reviewed and regression-tested without polluting the published index.

## Capabilities

### New Capabilities
- `content-tags`: covers the enabled Markdown extensions, the embed-tag preprocessor and its registry contract, the embed lint policy, and the rendered HTML / styling shape for admonitions, figures, and embeds.

### Modified Capabilities
<!-- None. Existing specs (content-model, site-build, design-tokens) are unaffected at the requirement level. New plugin registration in pelicanconf.py is implementation detail; CSS additions consume existing tokens without redefining the token contract. -->

## Impact

- **New plugin:** `plugins/content_tags/` (registry, preprocessor, embed renderers, tests).
- **Modified config:** `pelicanconf.py` / `publishconf.py` — `PLUGINS` list grows; new `MARKDOWN` extension list configured.
- **Modified plugin:** `plugins/frontmatter_lint/` — gains a body-content scanner that walks post/page bodies for embed tags and validates them against the `content_tags` registry (reuses the registry to avoid duplication).
- **New CSS:** `themes/garden/static/css/styles.css` — rules for `.admonition`, `.admonition-title`, variant classes (`.note`, `.warning`, `.tip`), `figure` + `figcaption`, and `.embed` / `.embed-iframe` containers. All styling consumes existing tokens.
- **Dependencies:** `pyproject.toml` adds `markdown_captions` (or chosen equivalent) if the figure-caption extension is not already covered by `markdown.extensions.extra`.
- **Documentation:** none added in this change — authoring documentation is consolidated in `add-python-cli` per the deferred-authoring-guide note. The verification post under `embeds-demo/` serves as the de facto worked example until then.
- **Authors:** one new syntax to learn (`[!name arg=value]`) and one Python-Markdown idiom (`!!! note "Title"`); both are plain text and editor-friendly.
