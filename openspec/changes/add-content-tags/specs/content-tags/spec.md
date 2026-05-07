## ADDED Requirements

### Requirement: Pelican Markdown configuration enables admonition and figure-caption extensions

The Pelican `MARKDOWN['extensions']` list in `pelicanconf.py` SHALL include `markdown.extensions.extra`, `markdown.extensions.admonition`, `markdown.extensions.codehilite`, and a figure-caption extension (`markdown_captions` or an equivalent in-tree shim). `publishconf.py` SHALL inherit this configuration unchanged.

#### Scenario: Admonition extension is enabled
- **WHEN** `pelicanconf.py` is imported
- **THEN** `MARKDOWN['extensions']` (or its equivalent dict-form configuration) lists `markdown.extensions.admonition`.

#### Scenario: Figure-caption extension is enabled
- **WHEN** `pelicanconf.py` is imported
- **THEN** `MARKDOWN['extensions']` lists either `markdown_captions` or the in-tree fallback module path that promotes `![alt](src "caption")` to `<figure>…</figure>`.

#### Scenario: Markdown extras are available
- **WHEN** `pelicanconf.py` is imported
- **THEN** `MARKDOWN['extensions']` lists `markdown.extensions.extra` (covering tables, attr_list, fenced_code, footnotes, abbr, def_list, md_in_html).

#### Scenario: Production inherits Markdown configuration
- **WHEN** `publishconf.py` is imported
- **THEN** the resulting `MARKDOWN` configuration is identical to `pelicanconf.py`'s `MARKDOWN` configuration (no additions, no removals).

### Requirement: Admonition syntax renders to a styled callout block

A Markdown source fragment of the form `!!! <variant> "Optional title"` followed by an indented body SHALL render to `<div class="admonition <variant>"><p class="admonition-title">…</p>…</div>` per the standard Python-Markdown admonition extension. The theme SHALL style at least the variants `note`, `warning`, `tip`, and `danger`.

#### Scenario: A note admonition renders with title
- **WHEN** a post body contains:
  ```
  !!! note "Heads up"
      Cert provisioning takes ~1 hour.
  ```
- **THEN** the rendered HTML contains `<div class="admonition note">`, a `<p class="admonition-title">Heads up</p>`, and the body paragraph in that order.

#### Scenario: A note admonition without title uses default title
- **WHEN** a post body contains `!!! note` followed by an indented paragraph and no quoted title
- **THEN** the rendered HTML contains `<div class="admonition note">` with a default title element produced by the extension (typically the variant name capitalised).

#### Scenario: Each documented variant has CSS styling
- **WHEN** `themes/garden/static/css/styles.css` is inspected
- **THEN** it defines visual rules for at least `.admonition.note`, `.admonition.warning`, `.admonition.tip`, and `.admonition.danger`, all referencing existing design tokens (no hardcoded colours).

### Requirement: Markdown image-with-title renders as a captioned figure

A Markdown image with a title attribute (`![alt](src "caption")`) SHALL render to `<figure><img src="…" alt="…"><figcaption>caption</figcaption></figure>` rather than a bare `<img>` wrapped in `<p>`. A Markdown image without a title attribute SHALL continue to render as a plain `<img>` (no `<figure>` wrapping).

#### Scenario: Image with title becomes a figure
- **WHEN** a post body contains `![Lisbon at dusk](sunset.jpg "Lisbon at dusk")`
- **THEN** the rendered HTML contains `<figure>` enclosing the `<img>` and a `<figcaption>Lisbon at dusk</figcaption>`.

#### Scenario: Image without title stays as an inline image
- **WHEN** a post body contains `![Lisbon at dusk](sunset.jpg)`
- **THEN** the rendered HTML contains an `<img>` element and no `<figure>` wrapper.

#### Scenario: Figure styling references tokens
- **WHEN** `themes/garden/static/css/styles.css` is inspected
- **THEN** it defines rules for `figure` and `figcaption` referencing existing design tokens for spacing, border, and muted text colour (no hardcoded values).

### Requirement: A `content_tags` plugin preprocesses post and page bodies before Markdown parsing

The repository SHALL ship a Pelican plugin at `plugins/content_tags/` that subscribes to a Pelican signal which fires before each post and page body is parsed by the Markdown reader, and SHALL be listed in `pelicanconf.py:PLUGINS`.

#### Scenario: Plugin module exists with package layout
- **WHEN** `plugins/content_tags/` is inspected
- **THEN** it contains at least `__init__.py`, `registry.py`, and a `tests/` directory with at least one test module.

#### Scenario: Plugin is registered in pelicanconf.py
- **WHEN** `pelicanconf.py:PLUGINS` is inspected
- **THEN** `content_tags` appears in the list.

#### Scenario: Preprocessing happens before Markdown parses the body
- **WHEN** a post body containing `[!youtube id="abc"]` is rendered
- **THEN** the resulting HTML contains the youtube embed's `<iframe>` directly inside the article body's HTML, NOT wrapped in a `<p>` tag introduced by Markdown around the literal `[!youtube id="abc"]` text.

### Requirement: Embed tags use the syntax `[!name key=value key2="quoted value"]`

An embed tag SHALL match the regex shape `\[!<name>(\s+<arg>)*\]` where `<name>` is `[a-z][a-z0-9_-]*` and each `<arg>` is `<key>=<value>` with `<key>` matching `[a-z][a-z0-9_-]*` and `<value>` either a non-quoted token (`[^\s\]]+`) or a double-quoted string (which MAY contain whitespace and SHALL support backslash-escaped `"` characters). A line containing an embed tag MUST contain ONLY whitespace before `[!` and ONLY whitespace after the closing `]` — no inline embeds.

#### Scenario: A bare embed line is recognised
- **WHEN** a post body line is exactly `[!youtube id="dQw4w9WgXcQ"]`
- **THEN** the line is recognised as an embed and replaced with the registered renderer's HTML output.

#### Scenario: Leading and trailing whitespace are tolerated on the line
- **WHEN** a post body line is `   [!youtube id="abc"]   ` (indented and trailing spaces)
- **THEN** the line is recognised as an embed and replaced.

#### Scenario: Inline embed is NOT recognised
- **WHEN** a post body line is `Watch this: [!youtube id="abc"] now.`
- **THEN** the line is left unchanged and the `[!youtube id="abc"]` substring is rendered as literal text by Markdown.

#### Scenario: Quoted argument values may contain spaces
- **WHEN** a post body line is `[!iframe src="https://example.com/foo bar" title="My demo"]`
- **THEN** the embed is recognised with `src` equal to `https://example.com/foo bar` and `title` equal to `My demo`.

#### Scenario: Embed tags inside fenced code are NOT expanded
- **WHEN** a post body contains a fenced code block (```` ``` ```` … ```` ``` ````) whose contents include `[!youtube id="abc"]`
- **THEN** the embed inside the fence is rendered as literal text in the resulting HTML, NOT as a YouTube iframe.

#### Scenario: Embed tags inside indented code blocks are NOT expanded
- **WHEN** a post body contains a 4-space-indented code block whose contents include `[!youtube id="abc"]`
- **THEN** the embed inside the indented block is rendered as literal text, NOT as a YouTube iframe.

### Requirement: An embed registry maps tag names to renderers with declared argument schemas

The plugin SHALL expose `plugins.content_tags.registry.REGISTRY` as a Python mapping `dict[str, EmbedTag]`, where each `EmbedTag` declares its `required_args: tuple[str, ...]` and `optional_args: tuple[str, ...]` (both immutable) and a `render(args: dict[str, str]) -> str` callable. Both `youtube` and `iframe` SHALL be present at module-import time.

#### Scenario: Registry contains youtube and iframe
- **WHEN** `plugins.content_tags.registry.REGISTRY` is inspected after import
- **THEN** the keys `youtube` and `iframe` are both present.

#### Scenario: Each registered tag declares argument schema
- **WHEN** any `REGISTRY[name]` is inspected
- **THEN** it has `required_args` and `optional_args` attributes that are tuples of strings, and a `render` attribute that is callable.

#### Scenario: Argument schemas are immutable
- **WHEN** runtime code attempts to mutate `REGISTRY[name].required_args` or `REGISTRY[name].optional_args`
- **THEN** the attempt fails (frozen dataclass / tuple semantics).

### Requirement: YouTube embeds render to a privacy-respecting iframe wrapper

The `youtube` embed SHALL declare `id` as a required argument and `start` as an optional argument, and SHALL render HTML of the form:
```html
<div class="embed embed-youtube">
  <iframe src="https://www.youtube-nocookie.com/embed/{id}?rel=0[&start={start}]"
          title="YouTube video"
          loading="lazy"
          referrerpolicy="strict-origin-when-cross-origin"
          allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
</div>
```

#### Scenario: Required id renders the embed
- **WHEN** a post body line is `[!youtube id="dQw4w9WgXcQ"]`
- **THEN** the rendered HTML contains an `<iframe>` whose `src` is `https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0`, includes `loading="lazy"`, `allowfullscreen`, and is wrapped in `<div class="embed embed-youtube">`.

#### Scenario: Optional start argument adds a query parameter
- **WHEN** a post body line is `[!youtube id="abc" start="42"]`
- **THEN** the rendered iframe `src` is `https://www.youtube-nocookie.com/embed/abc?rel=0&start=42`.

#### Scenario: Argument values are HTML-escaped
- **WHEN** an embed argument contains `&`, `<`, `>`, or `"` characters that survive parsing
- **THEN** those characters appear in the rendered HTML as their corresponding entities (`&amp;`, `&lt;`, `&gt;`, `&quot;`).

### Requirement: Generic iframe embeds require src and title for accessibility

The `iframe` embed SHALL declare `src` and `title` as required arguments and `height` as an optional argument (default `400`), and SHALL render HTML of the form:
```html
<div class="embed embed-iframe">
  <iframe src="{src}"
          title="{title}"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
          style="height: {height}px"></iframe>
</div>
```

#### Scenario: Required src and title render the embed
- **WHEN** a post body line is `[!iframe src="https://example.com/demo" title="Live demo"]`
- **THEN** the rendered HTML contains an `<iframe>` whose `src` and `title` attributes match the supplied values, includes `loading="lazy"`, has the documented `sandbox` attribute, and applies `style="height: 400px"`.

#### Scenario: Custom height overrides the default
- **WHEN** a post body line is `[!iframe src="https://example.com" title="Demo" height="600"]`
- **THEN** the rendered iframe carries `style="height: 600px"`.

#### Scenario: Title is required at lint time
- **WHEN** a post body line is `[!iframe src="https://example.com"]` (no `title`)
- **THEN** lint fails with a "missing required argument 'title'" error referring to that file and line.

### Requirement: Lint fails the build on unknown embed tag names

`make build`, `make lint`, and the `python -m frontmatter_lint` CLI SHALL each fail with a non-zero exit code when any post, page, or tag-prose body contains an embed tag whose name is not present in `plugins.content_tags.registry.REGISTRY`. The error report SHALL identify the file, the line number, the offending tag name, and (if a registered name has a small Levenshtein distance to the typo) a suggested correction.

#### Scenario: Unknown tag name fails the lint
- **WHEN** a post body contains `[!fugure src="x.jpg"]` and `make lint` is run
- **THEN** the command exits non-zero with an error naming the file, line, and offending tag name `fugure`.

#### Scenario: Did-you-mean suggestion appears for close typos
- **WHEN** the unknown tag name has a Levenshtein distance ≤ 2 from a registered name (e.g. `fugure` → `figure` is not registered, but `youutube` → `youtube` is)
- **THEN** the error message includes a `did you mean: <name>?` suggestion citing the registered name.

#### Scenario: Unknown tag name aborts the build
- **WHEN** the same content is built via `make build`
- **THEN** the build exits non-zero before any HTML is written to `output/`.

### Requirement: Lint fails the build on missing required arguments

Lint SHALL fail when any embed tag is missing one or more of its registered `required_args`. The error report SHALL list every missing argument by name.

#### Scenario: youtube without id fails lint
- **WHEN** a post body contains `[!youtube]` and `make lint` is run
- **THEN** the command exits non-zero with an error naming the file, line, tag name `youtube`, and missing argument `id`.

#### Scenario: iframe missing both src and title fails lint
- **WHEN** a post body contains `[!iframe]` and `make lint` is run
- **THEN** the command exits non-zero with an error naming both missing arguments `src` and `title`.

### Requirement: Lint fails the build on unknown argument names

Lint SHALL fail when any embed tag carries an argument whose name is neither in `required_args` nor in `optional_args` for its registered tag. The error report SHALL name the tag, the offending argument, and the allowed argument set.

#### Scenario: Unknown argument fails lint
- **WHEN** a post body contains `[!youtube id="abc" autoplay="true"]` and `make lint` is run (where `autoplay` is not registered for `youtube`)
- **THEN** the command exits non-zero with an error naming the file, line, tag name `youtube`, and offending argument `autoplay`, and listing the allowed arguments (`id`, `start`).

### Requirement: Lint fails the build on malformed embed delimiters

Lint SHALL fail when a line begins with `[!` (with leading whitespace allowed) but does not match the embed-tag grammar (e.g. missing closing `]`, missing `=` between key and value, unclosed quoted value).

#### Scenario: Missing closing bracket fails lint
- **WHEN** a post body line is `[!youtube id="abc"` (no closing `]`)
- **THEN** lint exits non-zero with a "malformed embed tag" error citing the file and line.

#### Scenario: Unclosed quoted value fails lint
- **WHEN** a post body line is `[!youtube id="abc]` (unclosed double quote)
- **THEN** lint exits non-zero with a "malformed embed tag" error citing the file and line.

#### Scenario: A line starting with `[!` but not intending to be an embed
- **WHEN** a post body deliberately contains `[!]` or any other malformed-looking sequence outside a code block
- **THEN** the author must place it inside a code fence or escape the bracket; lint will not silently ignore it.

### Requirement: Lint reuses the embed registry; renderers and lint cannot drift

The `frontmatter_lint` plugin's body-content scanner SHALL import `plugins.content_tags.registry.REGISTRY` directly when validating embeds. The lint module SHALL NOT contain its own list of valid tag names or argument names.

#### Scenario: Registry is the single source of truth
- **WHEN** `plugins/frontmatter_lint/` is grepped for hard-coded tag names (`youtube`, `iframe`) outside of test fixtures
- **THEN** the only references are imports from `plugins.content_tags.registry`.

#### Scenario: Adding a new embed automatically extends lint coverage
- **WHEN** a new embed `vimeo` is registered in `plugins/content_tags/embeds/vimeo.py` and added to the registry
- **THEN** lint accepts `[!vimeo id="…"]` without any change to `frontmatter_lint` source.

### Requirement: A hidden `embeds-demo` post exercises every starter construct

Content under `content/posts/embeds-demo/` SHALL provide at least one post (any language, `Status: hidden`) that uses each of: a `note` admonition, a captioned figure, a `[!youtube]` embed, and a `[!iframe]` embed. The post SHALL build cleanly under both `make dev` and `make build` and pass `make lint`.

#### Scenario: Demo post exists with required Status
- **WHEN** `content/posts/embeds-demo/` is inspected
- **THEN** it contains at least one Markdown file whose frontmatter declares `Status: hidden`.

#### Scenario: Demo post exercises every construct
- **WHEN** the demo post body is read
- **THEN** it contains at least one `!!! note` admonition, at least one image with a Markdown title attribute, at least one `[!youtube]` embed, and at least one `[!iframe]` embed.

#### Scenario: Demo post builds cleanly
- **WHEN** `make build` is run on the project tree
- **THEN** the demo post produces an HTML file under `output/embeds-demo/` containing rendered admonition, figure, and embed HTML, and lint reports no errors.

### Requirement: Embed HTML hooks into existing design tokens via dedicated CSS classes

`themes/garden/static/css/styles.css` SHALL define rules for `.embed`, `.embed iframe`, `.embed-youtube`, and `.embed-iframe` such that embeds are responsive (full container width, preserved aspect for `embed-youtube`) and visually consistent with the rest of the theme. All colour and spacing values SHALL reference existing design tokens.

#### Scenario: Embed CSS exists and uses tokens
- **WHEN** `themes/garden/static/css/styles.css` is inspected
- **THEN** rules for `.embed` and `.embed iframe` exist, the iframe is sized to its container (`width: 100%`), and any colour/border references use existing CSS custom properties (e.g. `--border`, `--bg-subtle`).

#### Scenario: YouTube embed maintains 16:9 aspect
- **WHEN** the `.embed-youtube` rule is inspected
- **THEN** it sets a 16:9 aspect ratio for its iframe (via `aspect-ratio: 16 / 9` or a padding-box equivalent) so the embed fills width and scales height accordingly.
