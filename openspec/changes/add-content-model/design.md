## Status

Design decisions recorded below.

## Context

The project brief lists three things `add-content-model` must deliver: a frontmatter schema, the `translation_key` convention, and a `frontmatter_lint` plugin. Two of those are already partly specified — [ADR-0004](../../decisions/0004-multilingual-post-frontmatter-conventions.md) locks down the multilingual conventions (localized slugs, `Translation_key` = first-language slug, directory name = `Translation_key`, `Lang` = ISO 639-1 two-letter codes) and even names three lint targets:

> (a) `Slug:` values are unique per `Lang:` within a directory, (b) `Translation_key:` is identical across every file in a directory and matches the directory name, (c) `Lang:` matches `^[a-z]{2}$`.

What remains for this change to decide: the rest of the schema (required vs optional fields, allowed values for `Status`, date format), the validation implementation (library choice, where it hooks into Pelican, how it aborts the build), the post-vs-page split (filename coupling, which fields apply where), and a thin CLI entrypoint that future `add-python-cli` will wrap as `make lint`.

Current state: no plugin exists. `pelicanconf.py` does not list `PLUGINS`. Two pieces of content exist in the tree — `content/posts/ola-jardim/ola-jardim.pt.md` (a real post, `Status: published`) and `content/pages/404.md` (`Status: hidden`). The latter already uses a value the brief doesn't list (`hidden`), which is the trigger for one of the decisions below.

## Goals / Non-Goals

**Goals:**

- Build-time validation: any frontmatter error in any post or page aborts `make build` with a clear, file-anchored message — locally and in CI, identically.
- Schema is one source of truth, reused by the Pelican plugin and a thin CLI entrypoint so the future `make lint` doesn't re-implement rules.
- Posts have a strict filename ↔ frontmatter contract (`<slug>.<lang>.md` inside `<translation_key>/`), enforced by the linter; ADR-0004's directory-anchor convention becomes a checked invariant, not just prose.
- The schema covers exactly today's needs (i18n, drafts, tags, the 404 page) without speculative fields.
- Existing content (`ola-jardim`, `404`) passes the schema with at most trivial frontmatter edits.

**Non-Goals:**

- A Makefile `lint` target. The CLI entrypoint ships, but wiring `make lint` is the job of `add-python-cli` (proposal #7 in the brief).
- A web-based or interactive validator. CLI + plugin is the surface.
- Cross-content semantic checks beyond `translation_key`/`slug`/`lang` consistency (e.g. tag taxonomy validation, link-checking, image-existence checks). Those are separate concerns for separate changes.
- Image-pipeline frontmatter (`cover_image`, `srcset` hints). Deferred to `add-image-pipeline` per the brief.
- Validation of body content (Markdown structure, custom tags). Custom tags are owned by `add-content-tags`.
- Fixing the schema for fields that don't exist yet (e.g. `category`). The schema rejects unknown fields by default — adding new fields means updating the schema in the change that introduces them.
- Reopening ADR-0004's group-anchor design. The `Translation_key`-as-explicit-field convention stands; this change implements the lint check that makes it a checked invariant rather than prose.

## Decisions

### D1: Validation lives in a Pelican plugin **and** a CLI; the plugin is the source of truth

Per the user decision, both surfaces ship now. The shape:

- `plugins/frontmatter_lint/__init__.py` — registers the Pelican plugin (signal handlers + `register()`).
- `plugins/frontmatter_lint/schema.py` — pure validation logic. No Pelican imports. Takes a `(path, frontmatter_dict, content_kind)` triple, returns a list of `ValidationError` objects.
- `plugins/frontmatter_lint/cli.py` — `python -m frontmatter_lint [content_dir]` walks the content tree, parses frontmatter, calls the same validators, prints errors, exits non-zero on failure.

The plugin imports from `schema.py`; the CLI imports from `schema.py`; neither knows about the other. Future `make lint` calls the CLI; CI's `make build` runs the plugin. Same rules, two entry points.

**Alternatives rejected:**

- **Plugin only, no CLI now.** Cheaper today, but every author who wants to "check before commit" has to run a full Pelican build. The CLI is ~30 LoC on top of `schema.py` — not worth deferring.
- **CLI only, plugin pending later.** Loses the build-time guarantee: a contributor who skips `make lint` and pushes ships broken frontmatter to CI, where the absence of a plugin means CI also doesn't catch it.
- **External tool (`pre-commit` hook, schema-only with `jsonschema`).** Adds another tool to install and configure; doesn't run in CI's `make build`; no build-time guarantee for collaborators who don't install the hook.

### D2: Validation uses `pydantic` v2 + `langcodes`; reject unknown fields by default

Two new pinned deps, with distinct jobs:

- **`pydantic` v2** — schema definition and field-level validation (types, regex, enums, error aggregation).
- **`langcodes`** — authoritative source for "is this a valid ISO 639-1 code?" The `Lang` field is annotated with a custom pydantic validator that delegates to `langcodes.tag_is_valid(value)` and additionally requires a two-letter alpha-2 form (so BCP 47 region-suffixed values like `pt-br` are rejected today, per ADR-0004 rule 4).

Why pydantic over hand-rolling:

- The schema *is* the documentation: regex constraints on `Slug`, `Status: Literal["draft", "published", "hidden"]`, custom `Lang` validator, all in ~30 lines. Authors and tools both read it the same way.
- Aggregated multi-error output is built in: pydantic returns every field's failure in one `ValidationError`, so a contributor who mistypes three fields sees all three at once. Hand-rolled validators tend to fail-fast or grow ad-hoc accumulation logic.
- pydantic v2 is one well-maintained pure-Python install, no transitive surprises.
- Future `add-python-cli` (Typer) and pydantic compose well: shared models for the `garden new` command's prompts.

Why `langcodes` over a hardcoded literal or a bare regex:

- A `Literal["en", "pt", "es", "fr"]` (the brief's enumerated examples) breaks the moment the author writes a fifth language and forgets to update the schema — exactly the silent-drift failure mode the linter exists to prevent.
- The bare regex from ADR-0004 (`^[a-z]{2}$`) accepts typos: `xy`, `qq`, `pp` all pass. ISO 639-1 is the actual constraint we mean; `langcodes` knows the full set.
- `langcodes` is small (pure Python, ~tens of KB) and authoritative; it tracks the standard so we don't have to. It also future-proofs the regional-variant escape hatch ADR-0004 leaves open (rule 4: a future ADR may permit `pt-br` etc.) — switching to BCP 47 means relaxing one assertion in the validator, no parser change.

Configuration: `model_config = ConfigDict(extra="forbid")`. An unknown field is a *typo* until proven otherwise — silent acceptance is exactly the failure mode the brief calls out as the known gap.

This tightens ADR-0004's lint target (c) from "matches `^[a-z]{2}$`" to "is a valid ISO 639-1 alpha-2 code" — a strict superset of compliance (every ISO 639-1 code passes the regex), so no ADR supersession is required.

**Alternatives considered:**

- **Hand-rolled (`dataclass` + `__post_init__` checks).** Rejected: we'd reinvent error aggregation, regex constraints, enum validation, and pretty error messages for ~60% of pydantic's value.
- **`jsonschema`.** Rejected: schema lives in JSON or YAML separate from the Python that consumes it — drift surface. Less Pythonic error formatting. No structural advantage given the schema is small.
- **`attrs` + `cattrs`.** Rejected: similar power, smaller community for the validation idiom we want, and we'd still need to write the regex/enum constraints by hand.
- **Snapshot ISO 639-1 codes into an in-repo tuple instead of `langcodes`.** Rejected: zero-dep but stale-prone; trades a one-line `tag_is_valid()` call for a snapshot file plus a regenerator script plus the ongoing question of when to refresh. `langcodes` is small enough that the dep cost doesn't justify a custom mirror.
- **`pycountry` instead of `langcodes`.** Rejected: heavier (covers ISO 639-1/2/3 plus country codes plus subdivisions), and we don't need any of the extras. `langcodes` is the focused tool.

### D3: `Status` enum is `{draft, published, hidden}` — recorded as ADR-0006

Per the user decision; the brief listed only `{draft, published}`. Reasoning:

- The 404 page (`content/pages/404.md`) already uses `Status: hidden`, set by the `add-deploy-pipeline` change (deploy-pipeline spec, scenario "404 source exists under content/pages"). Forcing it to `draft` would re-include the 404 page in dev builds; forcing it to `published` would surface it in indexes/feeds. Neither is right — `hidden` is the value Pelican supports for "render this file but exclude it from listings" and is the correct one for utility pages.
- Future utility pages (`/about/`, `/colophon/`, `/now/`) may also need `hidden` — this isn't a one-off.
- Schema-level enums are easier to reason about than per-content-type rules (the third option offered to the user). `hidden` for posts is unusual but not nonsensical (e.g. an unlisted vanity URL); we don't gain much by forbidding it.

This is a deviation from the project brief, so it gets recorded as an ADR (per the project-baseline-plus-ADRs convention from ADR-0001). New file: `openspec/decisions/0006-status-enum.md`. Status: `Accepted`. The ADR also documents the rejected alternative ("per-content-type rule") for the next person who looks.

### D4: Filename ↔ frontmatter coupling — strict for posts, advisory for pages

Per the user decision. The strict-for-posts side is what makes ADR-0004's directory-anchor convention a *checked* rule, not just prose.

For **posts** (any file under `content/posts/`):

1. The file MUST live at `content/posts/<dir>/<slug>.<lang>.md`.
2. `<dir>` MUST equal frontmatter `Translation_key`.
3. `<slug>` (the filename stem before `.lang.md`) MUST equal frontmatter `Slug`.
4. `<lang>` (the second segment of the filename) MUST equal frontmatter `Lang`.

If any of those mismatch, the linter errors with the specific axis ("filename slug `hello-garden` ≠ frontmatter Slug `helo-garden`") so the author sees which side to fix.

**Why rule 2 specifically (`<dir> == Translation_key`):** `Translation_key` is the field that links translations of one post — the EN file `hello-garden.en.md` and the PT file `ola-jardim.pt.md` both carry `Translation_key: ola-jardim` to declare "we're the same post in different languages." With localized slugs (ADR-0004 rule 1), they don't share a slug, so `Translation_key` is what the future i18n plugin will group on to build the "Available in: EN, PT" badges. ADR-0004 rule 3 names the directory after the `Translation_key` so the filesystem layout is the human-readable view of the same grouping. The lint check makes the equality a hard invariant: if someone moves a file to the wrong directory, mistypes the field, or renames the directory without updating its children, the next `make build` fails with a precise diagnostic instead of letting i18n grouping silently break. Without the check, the redundancy is a footgun; with the check, the redundancy is a safety net.

For **pages** (any file under `content/pages/`):

1. Filename is unconstrained beyond `*.md`.
2. Frontmatter is validated, but no filename ↔ field relationship is enforced.
3. Pages MAY omit `Slug`, `Lang`, and `Translation_key` (they're not part of the page schema). Pages that do specify a `Lang` get it validated against the same ISO 639-1 check used for posts.

Rationale: posts are part of the multilingual pipeline; the directory anchor and filename naming are how translations find each other. Pages are flat utility documents (`404.md`, future `about.md`) — adding a fake `Translation_key` to them would be ceremony with no payoff. The price is two slightly different code paths in the linter; this is a small, well-scoped split.

### D5: Plugin hooks `article_generator_finalized` and `page_generator_finalized`

Pelican's signal options for a frontmatter linter, from earliest to latest:

- `content_object_init` — fires per-document right after metadata extraction. Good for per-document checks; bad for cross-document checks (we don't yet have the full article set).
- `article_generator_pretaxonomy` — after articles are read, before tags are computed. Adequate, but Pelican-internal-feeling.
- `article_generator_finalized` / `page_generator_finalized` — after each generator finishes; we have full sets.
- `all_generators_finalized` — after all generators finish.
- `finalized` — after writing output. Too late: we want to abort *before* writing.

We use `article_generator_finalized` for the article checks (including the cross-document `Translation_key`/directory-anchor check) and `page_generator_finalized` for page checks. Two signals instead of one (`all_generators_finalized`) lets us emit errors per content kind with the right context, and avoids running pages through post-only validators.

Errors are accumulated across both signal handlers into a module-level list and raised as a single `RuntimeError` from the second handler (or a `finalized` hook, whichever propagates cleanly in Pelican 4.x). The exception aborts Pelican; CI shows the full failure list, not just the first.

**Alternative rejected:** `content_object_init` only. Per-document fires too early for the cross-file `Translation_key` consistency check, and re-implementing "wait until everything's read" via shared state inside that hook is brittle.

### D6: Schema fields and required/optional split

Posts (required unless noted):

| Field             | Type / constraint                                  | Required | Notes                                                             |
|-------------------|----------------------------------------------------|----------|-------------------------------------------------------------------|
| `Title`           | non-empty string                                   | yes      |                                                                   |
| `Slug`            | matches `^[a-z0-9]+(-[a-z0-9]+)*$`                 | yes      | Lowercase, kebab-case. Enforces the brief's "lowercase slug" gap. |
| `Date`            | ISO 8601 date or datetime (Pelican-parseable)      | yes      | Pydantic accepts `date` and `datetime`.                           |
| `Lang`            | valid ISO 639-1 alpha-2 code via `langcodes` (D2)  | yes      | Tightens ADR-0004's `^[a-z]{2}$` to the actual standard.          |
| `Translation_key` | matches `^[a-z0-9]+(-[a-z0-9]+)*$`                 | yes      | Same shape as `Slug`. Cross-checked against directory name.       |
| `Status`          | `draft` \| `published` \| `hidden` (D3)            | yes      | No default. Authors choose explicitly.                            |
| `Tags`            | list of non-empty strings, each kebab-case-friendly| no       | Default: `[]`. Detailed tag taxonomy is `add-tags-and-drafts`.    |

Pages (required unless noted):

| Field       | Type / constraint                              | Required | Notes                                                                |
|-------------|------------------------------------------------|----------|----------------------------------------------------------------------|
| `Title`     | non-empty string                               | yes      |                                                                      |
| `Status`    | `draft` \| `published` \| `hidden` (D3)        | yes      |                                                                      |
| `Lang`      | valid ISO 639-1 alpha-2 code (same as D6 above)| no       | If present, validated; otherwise inherits Pelican's `DEFAULT_LANG`.  |
| `Save_as`   | string                                         | no       | Pelican-native; passed through. (Used by 404.)                       |
| `URL`       | string                                         | no       | Pelican-native; passed through.                                      |

`extra="forbid"` (D2) means anything else fails the lint. New fields require a schema update in the change that introduces them — making schema extensions visible in code review.

**Alternative rejected:** Default `Status` to `draft`. Ergonomic for authors (less typing) but creates a class of "I forgot to flip it" failures where draft posts ship as draft to prod and silently disappear from the site. Forcing the choice keeps the field's meaning honest.

### D7: Date format is whatever pydantic + Pelican both accept

Pydantic's `datetime`/`date` parsers accept ISO 8601 in all the forms Pelican accepts (`YYYY-MM-DD`, `YYYY-MM-DD HH:MM`, `YYYY-MM-DDTHH:MM:SSZ`). The schema uses `date | datetime`; whatever the author writes, both Pelican and the linter agree. Authors aren't pinned to one form; the linter doesn't pin it either.

**Alternative rejected:** Force a single format (`YYYY-MM-DD` only). Tidier on disk but rejects valid Pelican input — the linter would be stricter than the build, which is a wrong direction.

### D8: Cross-document checks are scoped to one directory at a time

ADR-0004 says `Translation_key` is unique per directory, identical across siblings, equal to the directory name. The linter walks `content/posts/`, groups files by their immediate parent directory, and runs the consistency checks per group:

1. Every file in `<dir>/` has `Translation_key == <dir>`.
2. Within `<dir>/`, every `(Slug, Lang)` pair is unique (no two files claim the same language with different slugs, no two files share the same slug across different languages).
3. Implied by 1+2: the `Translation_key` global-uniqueness check is the directory-uniqueness check (different dirs ⇒ different keys, by construction).

Cross-directory `Slug` collisions (two posts in different translation groups using the same slug for the same language) would break URL routing — but that's a Pelican-level error already, surfaces at build, and isn't a frontmatter-schema concern. The linter doesn't try to catch it.

### D9: Errors are file-anchored and grouped

Output format (one block per file):

```
content/posts/ola-jardim/ola-jardim.pt.md:
  - Slug must be lowercase kebab-case (got "Ola-Jardim")
  - Status must be one of {draft, published, hidden} (got "live")
content/posts/ola-jardim/hello-garden.en.md:
  - Translation_key "ola-jardim-en" must equal directory name "ola-jardim"
```

Posix-style relative paths, leading whitespace per error, sorted by path. The Pelican plugin and the CLI share this formatter. CI logs are grep-friendly; humans can scan top-down.

## Risks / Trade-offs

- **Adding pydantic + langcodes to the dep set is a one-way door for the project's "tiny dep set" posture** → Mitigation: pin `pydantic>=2,<3` and `langcodes>=3,<4` in `pyproject.toml`; revisit if either ever becomes the *only* user of its dep family and the schema stays small. Removal cost = rewrite ~50 LoC and snapshot the ISO 639-1 set.

- **Pelican may not propagate exceptions raised in `*_generator_finalized` cleanly to a non-zero exit code in all versions** → Mitigation: tasks include a deliberate "introduce a bad post, run `make build`, assert non-zero exit" check during implementation. If the signal-handler exception is swallowed, fall back to `sys.exit(1)` with a printed summary.

- **Strict `extra="forbid"` will trip authors who add a new field for a future change without updating the schema in the same PR** → Mitigation: documented behavior; the error message explicitly says "unknown field — update the schema if this is intentional." Better than silent drift.

- **The ADR-0004 directory-anchor rule means the existing `ola-jardim` directory is fine but any future single-language post still gets a directory** → Mitigation: documented (the directory IS the translation_key, even if there's only one translation). Adds one folder per post; matches the brief's repo-layout sketch already.

- **Pages without `Lang` inherit `DEFAULT_LANG` (currently `en`) — the 404 page's English copy works, but a future Portuguese-only utility page would need `Lang: pt` set explicitly** → Mitigation: documented behavior; the schema accepts the field on pages, just doesn't require it.

- **CLI walks the content tree itself rather than reusing Pelican's reader** → Mitigation: use `python-frontmatter` (small, well-maintained) or a 20-line YAML-block parser. The CLI's job is "validate without booting Pelican"; the tradeoff (tiny risk of CLI accepting something Pelican rejects) is contained because the plugin is the build-time gatekeeper.

- **`langcodes` ships its own data tables for language tags; an upstream rename or deprecation could change validation behavior between minor versions** → Mitigation: the dep is pinned to a major (`>=3,<4`); ISO 639-1 itself rarely changes. If a CI surprise occurs, we pin to a specific minor and bump deliberately.

- **Renaming a `Translation_key` after publication is expensive** → ADR-0004 already documents this: the key is stable post-creation. Rename = update directory name + every sibling file's field + any internal links + acceptance that the URL anchor your readers/RSS clients knew is gone. Mitigation: documented as known behavior; a future change can choose to add tooling (`garden rename-group <old> <new>`) if it ever happens.

## Migration Plan

In-change migration only — there's no production user surface to roll out to. Order:

1. Land schema + plugin + CLI together; verify `make build` passes against the existing two content files (or fix their frontmatter if anything trips).
2. Register the plugin in `pelicanconf.py`'s `PLUGINS` (one line).
3. Run `make build` and `python -m frontmatter_lint content` — both succeed on green content.
4. Negative-test: introduce a deliberately-bad post, confirm `make build` fails with a clear message and CI surfaces the failure. Revert.
5. ADR-0006 gets committed alongside the change (per the proposal-bundle convention).

Rollback: revert the change. The plugin and the CLI live in their own files; removing the `PLUGINS` entry in `pelicanconf.py` deactivates lint without removing any content. No content files lose data.

## Open Questions

None blocking. Two notes for downstream changes:

- `add-i18n-rendering` will read `Translation_key` to build the language switcher — its plugin imports nothing from `frontmatter_lint`; the validation contract here is "if it builds, the data is well-formed." That's the i18n plugin's only assumption.
- `add-python-cli` will wrap `python -m frontmatter_lint` as `garden lint` and the `make lint` Makefile target. No code change to `frontmatter_lint` is anticipated; the CLI's argv surface is stable from this change forward.
