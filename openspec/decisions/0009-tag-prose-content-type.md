# ADR-0009: Tag prose is a third content type at `content/tag-prose/<slug>/`

## Status

Accepted — 2026-05-07.

## Context

Tag index pages (`/tag/<slug>/` and `/<lang>/tag/<slug>/`) benefit from an optional introductory paragraph — a brief editorial note contextualising the tag for first-time visitors. This prose has two independent localisation axes:

- **Cross-language vs. per-language scope.** The `/tag/<slug>/` page aggregates posts in all languages; prose for it should be language-neutral in framing but may itself be offered in multiple languages (displayed with browser-language inference, as on the 404 page). The `/<lang>/tag/<slug>/` page shows only one language's posts; its prose has an "in EN" / "in PT" framing and no inference script.
- **Language of the prose body.** Each piece of prose is authored in a specific language and carries a `Lang` frontmatter field.

This created a three-way choice on how to store the content:

1. **Third content type** (`content/tag-prose/<slug>/<scope>.<lang>.md`). A new directory tree, separate schema, separate validation. Filenames encode both the scope (`all` for cross-language, `lang` for per-language) and the language, mirroring the `<slug>.<lang>.md` convention used for posts.

2. **Page with a marker** (`Page_kind: tag-prose`). Reuse `content/pages/` but add a discriminator field. Simpler in terms of directory count, but conflates two schemas that have meaningfully different required fields (pages need `Save_as`/`URL` overrides; tag-prose needs `Status: hidden` and must forbid `Slug`/`Translation_key`/`Tags`).

3. **Embed prose in the first tagged article**. Tag the lead article with a special field (e.g. `Tag_prose_for: published-works`). Tight coupling between editorial content and the first post in a tag; breaks if the post is deleted or reordered.

4. **File-layout option II — parallel directory per scope** (`content/tag-prose-all/<slug>.<lang>.md`, `content/tag-prose-lang/<slug>/<lang>.md`). Separates the two axes into two trees. Doubles the top-level directories without reducing the frontmatter surface.

5. **File-layout option III — filename infix** (`content/tag-prose/<slug>.<scope>.<lang>.md`). Flat directory under `tag-prose/`, no subdirectory per slug. Works for a small tag set but makes per-slug grouping harder as the set grows; per-directory uniqueness checks become path-level checks.

## Decision

Use a third content type: every tag-prose file lives at `content/tag-prose/<slug>/<scope>.<lang>.md`.

- `<slug>` matches the post `Slug` regex (`^[a-z0-9]+(-[a-z0-9]+)*$`) and matches the tag slug it describes.
- `<scope>` is exactly `all` (cross-language page prose) or `lang` (per-language page prose).
- `<lang>` is an ISO 639-1 alpha-2 code, and must match the file's `Lang` frontmatter field.

Required frontmatter: `Title`, `Lang`, `Status: hidden`. Forbidden: `Slug`, `Translation_key`, `Tags`. All other fields are unknown and rejected. Validation is enforced by `frontmatter_lint` at build time, using a dedicated `TagProseFrontmatter` Pydantic model in `schema.py` shared between the plugin and CLI.

## Consequences

**Positive:**

- The schema is independent of the page schema: no discriminator fields, no conditional validation.
- Filename-to-frontmatter coupling is strict (directory = slug, scope from stem, lang from stem and frontmatter) and enforceable without reading any file.
- The `content/tag-prose/` tree is browsable: one directory per tag, easy to see which tags have prose and which do not.
- Prose is `Status: hidden`, making it invisible to Pelican's article and page generators without any special filtering.

**Negative / risks:**

- Third content type means a third scanner in `frontmatter_lint` and a third discovery pass in `tag_pages`. Small but real maintenance surface.
- Authors must remember two conventions (`all.<lang>.md` vs. `lang.<lang>.md`). Mitigated by `frontmatter_lint` catching scope-token errors at build time.

**Rejected alternatives:**

- Page-with-marker (option 2): schema conflation, harder to enforce per-type forbidden fields.
- Embed in first article (option 3): tight coupling, fragile under reordering.
- Parallel directories (option 4): doubles directory count without reducing complexity.
- Flat filename infix (option 5): loses per-slug grouping, makes uniqueness checks awkward.
