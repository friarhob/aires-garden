## Why

The CLI shipped in `add-python-cli` requires a precise slug for every command that acts on existing content. In practice, remembering exact slugs is friction — the author has to look them up, copy them, and type them without error. Worse, omitting the slug currently fails immediately in TTY mode, which contradicts the design intent of prompting interactively for missing arguments.

A code review during proposal also surfaced two frontmatter correctness bugs in `garden new`:

- `garden new --kind page` adds `Slug:` to frontmatter, but `PageFrontmatter` has `extra="forbid"` and no Slug field → **the scaffolded file fails lint**.
- `garden new --kind tag-prose` adds `Slug:` to frontmatter — which is an explicitly **forbidden field** on tag-prose (`_TAG_PROSE_FORBIDDEN`) → **the scaffolded file fails lint**.

Two further rough edges complete the picture: slug generation silently drops accented characters (so "Água no Balão" becomes `gua-no-bal-o`, not `agua-no-balao`), and `garden new --kind tag-prose` asks for a free-text tag name instead of showing which tags already exist.

## What Changes

- **Interactive slug picker** — `garden publish`, `garden draft`, `garden archive`, and `garden translate`: when the slug argument is omitted in TTY mode, an autocomplete picker lists every post (`questionary.autocomplete`), with each entry showing `slug — Title (lang, status)`. The user can type to filter. In non-TTY mode, omitting the slug fails with a clear error (unchanged from current). Tab completion is deferred — see design.
- **Slug generation normalisation** — `_slugify()` in `garden/commands/new.py` strips accents via `unicodedata.normalize('NFD', …)` before substituting non-ASCII characters, producing `agua-no-balao` from "Água no Balão".
- **Tag-prose new — existing tag picker** — `garden new --kind tag-prose` replaces the free-text tag prompt with an autocomplete picker from the directories present under `content/tag-prose/`. The "create new tag" option remains available; `--create-tag` still works in non-TTY mode.
- **Tag-prose new — skip irrelevant slug question** — the slug argument is skipped entirely for the tag-prose flow (it has no role in tag-prose filenames or frontmatter).
- **Frontmatter correctness fixes** — `garden new` now scaffolds correct, lint-passing frontmatter for each kind:
  - **page**: remove `Slug:` from frontmatter (field is forbidden under `PageFrontmatter extra="forbid"`); slug is still used to compute the filename.
  - **tag-prose**: write only `Title`, `Lang`, `Status: hidden` — no `Slug:`, no `Translation_key:`, no other forbidden fields.
- **`ContentFile` gains `title`** — needed to build meaningful picker labels. `walk_content` is updated to read `Title:` from each file's frontmatter into the index.

## Capabilities

### Modified Capabilities

- **`garden-cli`** — updated requirements covering: (1) lifecycle and translate commands accepting an optional slug argument with interactive picker fallback in TTY mode; (2) `garden new --kind tag-prose` uses an existing-tag picker, skips the slug step, and writes only the fields the schema allows; (3) `garden new --kind page` writes lint-passing frontmatter without `Slug:`; (4) `_slugify()` normalises Unicode input.

## Impact

- **No new runtime dependencies** — `questionary` is already present; `unicodedata` is stdlib.
- **Content tree** — no existing content is modified. Frontmatter fixes apply only to newly scaffolded files.
- **`content_index.py`** — `ContentFile` gains `title: str`; test fixtures that construct `ContentFile` directly need the new field.
- **`garden/commands/new.py`** — `_slugify()` changes output for accented inputs; the tag-prose path removes the slug step and fixes frontmatter; the page path removes `Slug:` from frontmatter.
- **`garden/commands/lifecycle.py`**, **`translate.py`** — `slug` argument becomes `Optional[str]` with picker fallback.
- **Existing tests** — test fixtures constructing `ContentFile` need the new `title` field; tests for `garden new` page/tag-prose need updating to assert correct frontmatter.
- **`garden-cli` spec** — new scenarios added for picker behaviour, normalised slugs, and corrected frontmatter for page and tag-prose kinds.
