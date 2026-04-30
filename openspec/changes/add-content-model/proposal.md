## Why

Pelican has no built-in frontmatter schema validation, and the project brief flags this as a known gap. Without a formal schema and a build-time linter, drift is silent: a missing `lang`, a typo in `translation_key`, an invalid `status`, or a slug that disagrees with its filename will all build cleanly and break only later — when i18n linking, tag indexes, or the deploy URL structure depend on those fields. This change closes the gap before any later change (i18n rendering, tag pages, gallery homepage) starts assuming the data is well-formed.

## What Changes

- Define the canonical frontmatter schema for posts and pages (required and optional fields, allowed values, formats).
- Adopt the `translation_key` convention for linking sibling-language files of the same post.
- Ship a `frontmatter_lint` Pelican plugin that validates every Markdown file at build time and aborts the build on any error.
- Ship a thin CLI entrypoint (`python -m frontmatter_lint`) that reuses the plugin's validation logic so a future `make lint` target can call it without re-implementing rules.
- Enforce strict filename ↔ frontmatter coupling for posts (`<slug>/<slug>.<lang>.md`) and treat pages as advisory (flat layout, filename not enforced).
- Record an ADR for the `status` enum decision: extend `{draft, published}` from the project brief to `{draft, published, hidden}` so the existing 404 page and future utility pages have a first-class value (rather than a one-off exception).
- Update the existing `ola-jardim` post and `404` page to comply with the schema if they don't already.

## Capabilities

### New Capabilities
- `content-model`: frontmatter schema for posts and pages, `translation_key` convention, `frontmatter_lint` plugin and CLI wrapper, filename-to-frontmatter coupling rules.

### Modified Capabilities
<!-- None. site-build and deploy-pipeline requirements remain unchanged; this change adds a new capability rather than altering existing ones. -->

## Impact

- **New code**: `plugins/frontmatter_lint/` (the plugin and CLI), registered in `pelicanconf.py` via `PLUGINS`.
- **Config**: `pelicanconf.py` adds the plugin to `PLUGINS`. No changes to `publishconf.py` (it inherits).
- **Dependencies**: one new pinned dep in `pyproject.toml` for schema validation (likely `pydantic` v2; `jsonschema` is the alternative — design.md will pick).
- **Content**: existing `content/posts/ola-jardim/ola-jardim.pt.md` and `content/pages/404.md` must conform; any gaps are fixed in this change.
- **CI**: no workflow change — the plugin runs inside `make build`, which CI already executes.
- **Decisions**: one new ADR, `0006-status-enum.md`, recording the `{draft, published, hidden}` decision and why it deviates from the brief.
- **Future changes unblocked**: `add-i18n-rendering` (relies on `translation_key` + `lang`), `add-tags-and-drafts` (relies on `tags` + `status`), `add-python-cli` (its `make lint` will wrap the CLI shipped here).
