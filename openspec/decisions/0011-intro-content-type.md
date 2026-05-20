# ADR-0011: Intro is a fourth content type at `content/intro/`

## Status

Accepted — 2026-05-20.

## Context

`refactor-homepage` introduces editorial prose at the top of the homepage. Two scopes need their own prose body:

- **Cross-language root `/`** — an aggregate page that lists every post regardless of language. Its intro frames the whole garden and is offered in every site language; the header lang picker (section-toggle mode) drives which body is visible, mirroring the multilingual 404.
- **Per-language root `/<lang>/`** — a single-language page. Its intro is authored in that language only.

This prose has the same two localisation axes that motivated [ADR-0009](0009-tag-prose-content-type.md) for tag pages:

- **Cross-language vs. per-language scope.** The cross-language intro may have multiple language bodies displayed via inference; the per-language intro has exactly one body in the page's language.
- **Language of the prose body.** Each body is authored in a specific language and carries a `Lang` frontmatter field.

The structural shape is therefore identical to tag-prose: a `scope × lang` two-axis filename convention with a single set of frontmatter fields (`Title`, `Lang`, `Status: hidden`). The choice is where to **store** this prose. Five options were considered:

1. **Fourth content type** (`content/intro/<scope>.<lang>.md`). New directory tree, dedicated schema, dedicated scanner. Borrows the `<scope>.<lang>.md` filename convention from tag-prose as a shared convention, not as a shared schema.

2. **Reuse tag-prose with a sentinel slug** (e.g., `content/tag-prose/home/<scope>.<lang>.md`). One fewer content type; reuses the existing schema, scanner, and lint code. Requires the `tag_pages` plugin to filter out the sentinel directory (otherwise `/tag/home/` is emitted as a real tag page), and either consumes the `home` slug from the tag namespace or relaxes the slug regex.

3. **Page with marker** (`Page_kind: intro` discriminator inside `content/pages/`). Reuse the page tree with a discriminator field. Same shape of problem ADR-0009 rejected for tag-prose: conflates two schemas that have meaningfully different required fields.

4. **Hardcode in templates.** Inline the intro text directly in `index.html` and `lang_index.html`. Updating prose requires a code change; no separation of content from theme.

5. **Single-language intro, no cross-language scope.** Show only the default-language intro on `/`. Rejects the multilingual framing that the rest of the garden already adopts (multilingual 404, cross-language tag pages with multiple `<section data-lang>` blocks).

A second policy question runs alongside the storage choice: **what happens when the reader's chosen language has no matching intro file?** The garden already answers this for the multilingual 404 page (see i18n-rendering spec, *"The 404 page infers the reader's language from the URL"*); the homepage needs the same kind of explicit chain so renderer and authors agree on the fallback.

## Decision

### Storage

Use a fourth content type: every intro file lives at `content/intro/<scope>.<lang>.md`. The `<scope>.<lang>.md` filename convention is **borrowed** from tag-prose as a shared *convention*, not as a shared schema.

- `<scope>` is exactly `all` (cross-language root `/`) or `lang` (per-language root `/<lang>/`).
- `<lang>` is an ISO 639-1 alpha-2 code, and must match the file's `Lang` frontmatter field.
- The directory `content/intro/` is flat — no per-slug subdirectory, because there is no per-slug axis. The two-axis shape is `scope × lang` only.

Required frontmatter: `Title`, `Lang`, `Status: hidden`. Forbidden: `Slug`, `Translation_key`, `Tags`. All other fields are unknown and rejected. Validation is enforced by `frontmatter_lint` at build time, using a dedicated `IntroFrontmatter` Pydantic model in `schema.py` shared between the plugin and the CLI.

A `garden new --kind intro` flow scaffolds intro files: interactive `scope` and `lang` prompts in TTY mode, `--scope` and `--lang` flags in non-TTY mode, no slug step.

### Language resolution

The cross-language root `/` and the per-language root `/<lang>/` resolve their intro body differently because they sit on different axes:

**Cross-language root `/`** — same inference pattern as the multilingual 404 page, with stage 1 dropped (there is no `/<lang>/` prefix on `/`). Build time emits one `<section data-lang="<lang>">` block per existing `content/intro/all.<lang>.md` file. Runtime ordering (first match wins):

1. **Stored language preference** — `document.documentElement.dataset.prefLang` (written by the header lang picker into `localStorage["garden-lang"]`), if a section for that language was emitted.
2. **Browser language** — `navigator.language`'s 2-letter prefix, if a section for that language was emitted.
3. **Default-language fallback** — the document's `data-default-lang` attribute, if a section for that language was emitted.
4. **Alphabetically-first existing section** — terminal fallback when none of stages 1–3 matches an emitted section. Guarantees at least one section is visible whenever any `all.<lang>.md` file exists.

With JavaScript disabled, every emitted `<section data-lang>` block remains visible — graceful degradation per [ADR-0007](0007-small-clientside-js.md) bar 2.

If no `content/intro/all.<lang>.md` file exists for any language, the intro region is omitted entirely from `/`. The post catalogue still renders.

**Per-language root `/<lang>/`** — the page's canonical language is `<lang>`. The intro body is taken from `content/intro/lang.<lang>.md` if that file exists. There is NO fallback to a different language's intro — mixing languages on a single-language page would be a worse outcome than showing no intro. If `content/intro/lang.<lang>.md` does not exist, the intro region is omitted from `/<lang>/` and the post list still renders.

## Consequences

**Positive:**

- The schema is independent of tag-prose: no discriminator fields, no conditional validation, no risk that a tag-prose schema change unintentionally alters intro semantics.
- `content/intro/` is browsable: at most eight files (4 langs × 2 scopes), with a flat directory layout that is trivially diffable.
- The `tag_pages` plugin does not need to filter out anything. Tag slugs continue to be drawn from the full tag namespace; `home` remains a valid (though unused) tag slug.
- Prose is `Status: hidden`, making it invisible to Pelican's article and page generators without any special filtering — the same mechanism tag-prose and `404.<lang>.md` already rely on.
- Future divergence is cheap: if intros ever gain unique fields (featured-post pointer, hero image, layout hint), the schema evolves without forking tag-prose.
- The language-resolution chain is explicit: authors know which files to provide for which behaviour, and readers always see a sensible result (graceful empty-state on `/` if no files exist, single-language correctness on `/<lang>/`, alphabetic terminal fallback on `/` when inference misses).

**Negative / risks:**

- Fourth content type means a fourth scanner in `frontmatter_lint` and a fourth discovery pass in the homepage plugin. Real but small maintenance surface; the pattern is established by tag-prose.
- Authors learn another folder name (`content/intro/`). Mitigated by `garden new --kind intro` being the canonical authoring entry point — authors rarely need to remember the directory path.
- The `/` inference chain duplicates the structural shape of the 404 chain. Acceptable cost — the two pages have different inputs (no URL-prefix stage on `/`) and the duplication is small. Reviewers should keep the two chains conceptually paired so they evolve together.

**Rejected alternatives:**

- **Tag-prose with sentinel slug (option 2):** would require a `tag_pages` filter exception and either consumes the `home` slug from the tag namespace or relaxes the tag-prose slug regex. Conceptually overloads "tag-prose" (which means *prose about a tag*) to also mean *prose about the homepage*. The symmetry argument (shared `<scope>.<lang>.md` convention) is preserved by Option 1 as a shared convention without inheriting the schema.
- **Page with marker (option 3):** schema conflation; harder to enforce per-type forbidden fields. Same argument ADR-0009 used to reject the marker option for tag-prose.
- **Hardcode in templates (option 4):** ties prose to theme commits; loses content/theme separation.
- **Single-language intro (option 5):** breaks parity with the rest of the multilingual surface (404, cross-language tag pages).
- **Per-language intro falls back across languages:** a missing `lang.<lang>.md` showing the closest available language would mix languages on a single-language page, which is worse than no intro. Rejected; omission is the chosen fallback.
