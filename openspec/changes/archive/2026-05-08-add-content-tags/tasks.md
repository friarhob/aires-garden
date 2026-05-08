## 1. Pelican Markdown configuration

- [x] 1.1 Add `markdown.extensions.admonition` to `MARKDOWN['extensions']` in `pelicanconf.py` (and verify `publishconf.py` inherits it unchanged)
- [x] 1.2 Pick the figure-caption extension: try `markdown_captions` first; if it misbehaves on Markdown ≥ 3.5, drop in the in-tree fallback under `plugins/content_tags/markdown_extensions/captions.py`
- [x] 1.3 Pin the chosen figure-caption dependency in `pyproject.toml` (or commit the in-tree fallback) and refresh `requirements.txt` if one is in use
- [x] 1.4 Make the `MARKDOWN['extensions']` and `extension_configs` block explicit in `pelicanconf.py` rather than relying on Pelican defaults — list `extra`, `admonition`, `codehilite`, and the figure-caption extension by full module path

## 2. content_tags plugin scaffold

- [x] 2.1 Create `plugins/content_tags/` package: `__init__.py`, `registry.py`, `embeds/__init__.py`, `embeds/youtube.py`, `embeds/iframe.py`, `tests/__init__.py`
- [x] 2.2 Define `EmbedTag` frozen dataclass in `registry.py` with `required_args`, `optional_args`, and `render` fields, plus a `REGISTRY: dict[str, EmbedTag]` populated at module-import time by importing the embed modules for their side-effects
- [x] 2.3 Wire `plugins/content_tags/__init__.py` to subscribe to a Pelican signal that fires before Markdown parsing (`readers.signals.readers_init` wrapping the markdown reader, or equivalent) and apply the embed-line preprocessor to the source string
- [x] 2.4 Implement the embed-line preprocessor: scan source line-by-line, skipping fenced code blocks (``` and ~~~) and indented (4-space) code blocks; on each candidate line, parse with the documented grammar; on match, replace the line with the rendered HTML
- [x] 2.5 Implement the argument parser supporting unquoted tokens (`key=value`), double-quoted values (`key="value with spaces"`), and backslash-escaped quotes inside quoted values; reject malformed input with a structured error
- [x] 2.6 Add `content_tags` to the `PLUGINS` list in `pelicanconf.py`

## 3. Starter embed renderers

- [x] 3.1 Implement `embeds/youtube.py` with `required_args=("id",)`, `optional_args=("start",)`, and a `render` function that produces the documented `<div class="embed embed-youtube">…</div>` HTML, HTML-escaping `id` and `start` values
- [x] 3.2 Implement `embeds/iframe.py` with `required_args=("src", "title")`, `optional_args=("height",)`, default height `400`, and the documented `<div class="embed embed-iframe">…</div>` HTML output (sandbox + lazy + referrerpolicy attributes)
- [x] 3.3 Add unit tests under `plugins/content_tags/tests/` covering: registry contains both tags; youtube renders with and without `start`; iframe renders with and without `height`; HTML-escaping of `&`, `<`, `>`, `"` in argument values

## 4. Lint integration

- [x] 4.1 Add a body-content scanner module to `plugins/frontmatter_lint/` (e.g. `body_scanner.py`) that imports `plugins.content_tags.registry.REGISTRY` and exposes a `scan(file_path: Path, body: str) -> list[Error]` function
- [x] 4.2 Implement the same code-fence-skipping logic the renderer uses (extract to a shared helper imported by both modules — single source of truth for "what counts as a candidate embed line")
- [x] 4.3 Validate each candidate line: name in REGISTRY (else "unknown tag" with did-you-mean suggestion via difflib), all required_args present (else "missing required argument"), every supplied key in required_args ∪ optional_args (else "unknown argument" with the allowed set listed)
- [x] 4.4 Detect malformed lines (started `[!` but didn't match the grammar) as a distinct error class
- [x] 4.5 Wire the body scanner into the existing per-file walk in `plugins/frontmatter_lint/cli.py` and the Pelican-side plugin entrypoint, so both `python -m frontmatter_lint` and `make build` exercise it
- [x] 4.6 Extend the existing file-anchored error reporter to emit body-scanner errors with file path + line number + structured message
- [x] 4.7 Add tests under `plugins/frontmatter_lint/tests/` covering each error class (unknown tag, missing required arg, unknown arg, malformed delimiter) and the happy path (valid embeds pass)

## 5. Theme styling

- [x] 5.1 Add admonition CSS rules to `themes/garden/static/css/styles.css` for `.admonition`, `.admonition-title`, `.admonition.note`, `.admonition.warning`, `.admonition.tip`, `.admonition.danger`, all using existing tokens
- [x] 5.2 Add `figure` and `figcaption` rules using `--text-muted`, `--border`, and existing spacing scale
- [x] 5.3 Add `.embed`, `.embed iframe`, `.embed-youtube`, `.embed-iframe` rules — full-width iframe, 16:9 aspect for `.embed-youtube` via `aspect-ratio: 16 / 9`, sensible vertical margins
- [x] 5.4 Verify both light and dark token sets render correctly (admonition variants must remain legible against `--bg` and `--bg-subtle` in both modes)

## 6. Verification content

- [x] 6.1 Author `content/posts/embeds-demo/embeds-demo.en.md` with `Status: hidden`, exercising all four constructs: at least one `!!! note "Title"` admonition, one `![alt](src "caption")` figure, one `[!youtube id="…"]` embed (use a known stable id), and one `[!iframe src="…" title="…"]` embed
- [x] 6.2 Add a Portuguese translation `embeds-demo.pt.md` sharing the same `Translation_key` to verify embeds render identically across languages
- [x] 6.3 Place a small test image at `content/posts/embeds-demo/assets/` and reference it from both language variants

## 7. End-to-end verification

- [x] 7.1 Run `make lint` against the full content tree — expect zero errors
- [x] 7.2 Run `make build` and inspect `output/embeds-demo/index.html` — confirm admonition, figure, youtube iframe, iframe HTML are all rendered as documented in the spec
- [x] 7.3 Run `make dev`, open `/embeds-demo/` in a browser, confirm: admonition is styled per variant, figure has visible caption, YouTube embed loads in `youtube-nocookie.com` host, iframe embed loads with sandbox attribute set
- [x] 7.4 Negative-test lint: introduce a typo (`[!yotube id="abc"]`), missing required arg (`[!youtube]`), unknown arg (`[!youtube id="abc" autoplay="true"]`), and malformed delimiter (`[!youtube id="abc"`); confirm `make lint` exits non-zero with file/line/structured message for each, then revert
- [x] 7.5 Confirm fenced code block containing `[!youtube id="abc"]` renders as literal text in the output, not as an embed
- [x] 7.6 Toggle theme between light and dark in the browser and verify admonition variants and embed containers remain legible
