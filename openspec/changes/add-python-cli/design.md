## Context

The garden currently has no authoring tooling. Posts, pages, and tag-prose files are created by hand: the author copies an existing file, edits frontmatter, and renames. The `add-tags-and-drafts` change introduced `Status: draft|published|hidden` and the existing `frontmatter_lint` plugin enforces schema correctness — but only at lint time, after the file is already written. ADR-0004 fixed the multilingual conventions: `Slug:` is per-language, `Translation_key:` is shared across translations and equals the directory name, `<slug>.<lang>.md` is the filename pattern, and `Lang:` is ISO 639-1 (`^[a-z]{2}$`).

The author's repeated chores: scaffold a new file (any of three types) with correct frontmatter; create a paired-language file mirroring an existing one; flip a `Status:` value as a post moves through its lifecycle. All three are mechanical and error-prone.

A small Python CLI under `garden/` replaces these chores. It uses the existing `frontmatter_lint` rules as the source of truth for what "valid" means — the CLI doesn't redefine validation, only enforces it earlier (at scaffold time, not lint time).

## Goals / Non-Goals

**Goals:**

- Scaffold posts, pages, and tag-prose with frontmatter conformant to the `content-model` spec — fail closed on invalid input.
- Mirror language pairs (`garden translate`) without manual `Translation_key`/`Slug`/`Lang` synchronisation.
- Flip `Status:` for one file or all translations atomically (`publish`/`draft`/`archive`), with `--force` as the documented escape hatch for unusual transitions.
- Replace `make lint` with `garden lint`, sharing the `frontmatter_lint` codebase (no duplicated rules).
- Be invokable both as `garden …` (entry point) and as `python -m garden …` (module fallback).
- Behave well in both interactive (TTY) and non-interactive (CI/script) contexts: missing args prompt in interactive mode, fail fast in non-interactive mode.

**Non-Goals:**

- Replacing `make build` or `make dev`. Site-build workflows stay in the Makefile; the CLI handles content workflows.
- Re-implementing or extending `frontmatter_lint`'s rules. The CLI is a producer/manipulator of valid content; lint is the enforcer. The CLI calls the existing module.
- Bulk operations (e.g. "archive every post older than X"). Out of scope; one slug at a time.
- A web UI, an admin panel, or a content database. The CLI edits files in place and that's it.
- Migration tooling (e.g. converting old frontmatter shapes to new ones). Not needed; existing content is already conformant.

## Decisions

### Decision 1: Typer over argparse and Click

Typer's type-hint-driven model gives us subcommand definitions that read like ordinary Python functions, automatic validation from `Enum` types and `Path` types, and pretty `--help` output for free. Click would also be fine but requires more decorator boilerplate. argparse handles 1–3 commands well but becomes verbose for our 6-command tree with shared flags.

Cost: one new dependency (`typer`). Typer pulls in Click as a transitive. Both are pure-Python and stable.

**Alternatives considered:**

- **argparse** (stdlib): zero dependencies but verbose subcommand setup. Rejected — `garden` will grow to 6+ subcommands with shared flags (`--all-translations`, `--force`); argparse's nested-parser pattern is harder to read.
- **Click** (decorator-based): mature, slightly more boilerplate than Typer, no type-hint inference. Rejected — Typer is strictly nicer for this size of CLI and is built on Click anyway.

### Decision 2: questionary for interactive prompts

Typer's built-in `typer.prompt()` handles single-value text input, but the CLI needs a select prompt for `--kind` (post/page/tag-prose) and yes/no prompts for `--all-translations` and `--force` confirmations. `questionary` provides nicely-styled select / confirm / text prompts and integrates well alongside Typer.

Cost: one more pure-Python dependency. Small surface, well-maintained.

**Alternatives considered:**

- **`typer.prompt()` only**: works for text but no select prompts. Would force `--kind` to a free-text prompt with manual validation. Rejected — select prompts materially improve UX for enumerated inputs.
- **`rich.prompt`**: similar feature set, larger dependency footprint (rich is huge if we don't use it elsewhere). Rejected — overkill for what we need.
- **stdlib `input()`**: too primitive; no validation, no select. Rejected.

### Decision 3: Top-level `garden/` package, not `plugins/garden_cli/`

The CLI is not a Pelican plugin — it doesn't subscribe to Pelican signals or run during `make build`. Putting it under `plugins/` would be misleading. A top-level `garden/` package is conceptually cleaner: it sits beside `plugins/`, `content/`, and `themes/` as a peer.

The package contains:
```
garden/
├── __init__.py
├── __main__.py           # enables `python -m garden`
├── cli.py                # top-level Typer app + subcommand registration
├── commands/
│   ├── __init__.py
│   ├── new.py
│   ├── translate.py
│   ├── lifecycle.py      # publish, draft, archive (shared logic)
│   └── lint.py
├── content_index.py      # walks content/ and indexes by slug, translation_key
├── frontmatter_io.py     # parse/serialise Pelican-style frontmatter
├── prompts.py            # questionary wrappers + TTY detection
├── validation.py         # field validators (kind, slug, lang, title)
└── tests/
```

### Decision 4: Frontmatter parsing without YAML

Pelican uses a key-colon-value format that is *not* YAML — it's a custom Pelican format ("Title: …", "Status: draft", etc.). Existing `frontmatter_lint` parses it with a small line-based parser. The CLI reuses that parser (or factors it into a shared module) for both reading and writing. We do not introduce PyYAML.

Writing strategy: read the file, modify the in-memory frontmatter dict, re-serialise the frontmatter block (preserving order — Title first, then Slug, Date, Lang, Translation_key, Status, Tags), and write atomically (temp file + rename) to avoid partial writes.

**Alternatives considered:**

- **Treat frontmatter as YAML and use PyYAML**: rejected — it isn't YAML, and treating it as YAML would change the on-disk format the rest of the pipeline expects.
- **Regex-based replacement** (find `Status: …` line, swap value): viable for `publish`/`draft`/`archive` (single-field swap) but doesn't handle `garden new` (full block creation) or `garden translate` (multi-field swap). Use the same parser everywhere.

### Decision 5: Slug → file resolution via content-tree walk

`garden publish my-slug` needs to find the file whose `Slug:` is `my-slug`. We walk `content/`, parse each `.md` file's frontmatter, and build a slug → file path index. The tree is small (dozens of files); a fresh walk per command is fine — no caching, no daemon.

For `--all-translations`: from the matched file, read its `Translation_key`, then re-query the index for all files with that key.

**Alternatives considered:**

- **File-name-based heuristic** (slug = filename without `.lang.md`): close but not quite — a Pelican `Slug:` header can override the filename. The frontmatter is authoritative. Rejected.
- **Maintain a slugindex cache**: speculative optimisation. The tree is small; rejected.

### Decision 6: Atomic multi-file operations via two-pass plan-then-apply

For `--all-translations` operations: pass 1 collects every target file and validates each one's current state against the requested transition. If any file would refuse and `--force` was not supplied, the operation aborts with no mutations and a clear error listing the offending files. Pass 2 applies the mutations.

This matches typical CLI safe-by-default semantics (`git rm`, `kubectl apply`) and makes the implementation easy to test: each pass is a pure function over (target files, requested transition).

### Decision 7: TTY detection for prompt-vs-fail behaviour

Missing required arguments behave one of two ways:

- **TTY (stdin is a terminal)**: prompt interactively for the missing value.
- **Non-TTY (CI, piped invocation)**: fail with a clear "missing required argument: …" error.

Detection: `sys.stdin.isatty()`. The same check controls whether `--all-translations` (when omitted) prompts a yes/no or aborts with "must be set explicitly in non-interactive mode".

### Decision 8: `garden lint` is a thin wrapper around `frontmatter_lint`

`garden lint` calls `frontmatter_lint.cli.main(["content"])` (or its function-level equivalent) and returns the same exit code. No re-implementation. The Makefile's `lint` target is removed; CI is unaffected since CI invokes `make build`, not `make lint`.

### Decision 9: Validation rules live in `garden/validation.py`, shared with `frontmatter_lint`

Field validators (kind enum, slug regex, lang regex, title non-empty) live in `garden/validation.py`. `frontmatter_lint` already has its own validators; the goal is *one source of truth*. Concretely:

- Phase 1 (this change): `garden/validation.py` is created and used by `garden`. `frontmatter_lint` keeps its existing validators.
- Phase 2 (follow-up if duplication becomes painful): factor a shared `lint_rules` module imported by both, mirroring how `content_tags.registry` is shared between the renderer and `frontmatter_lint.body_scanner`.

This avoids over-engineering now while leaving a clear path. If validators drift, a follow-up change will consolidate them.

### Decision 10: `garden new` directory and filename layout

Per ADR-0004:

- **post**: `content/posts/<translation_key>/<slug>.<lang>.md`. The `<translation_key>` directory is created if it doesn't exist; for the first language file written, `translation_key == slug`.
- **page**: `content/pages/<slug>.<lang>.md`. Pages are flat (no per-page directory) — this matches the existing `content/pages/404.en.md` / `404.pt.md` pattern.
- **tag-prose**: `content/tag-prose/<tag-slug>/<file>.<lang>.md`. The CLI prompts for which tag and which prose file (`all`, `lang`, etc. — the existing pattern under `content/tag-prose/published-works/`).

### Decision 11: Default `Date:` for `garden new`

`Date:` defaults to the current date (`YYYY-MM-DD`). The user can override interactively if they want backdated content. Pages and tag-prose typically don't carry `Date:`; the CLI omits it for those kinds.

## Risks / Trade-offs

- **[Risk] Two dependencies (`typer`, `questionary`) increase install footprint.** → Mitigation: both are pure-Python, well-maintained, and the project already depends on Pelican (much larger). Worth the ergonomics.
- **[Risk] `garden/validation.py` duplicates rules also enforced by `frontmatter_lint`.** → Mitigation: documented in Decision 9 with a follow-up plan. Tests in both places will surface drift; a future change consolidates.
- **[Risk] Atomic two-pass logic adds complexity vs. per-file processing.** → Mitigation: this is the safest default; per-file behaviour is available via `--no-all-translations` (operate on one file). Tests cover both paths.
- **[Risk] Tag-prose authoring is more nuanced than post/page** (multiple file shapes per tag: `all.<lang>.md`, `lang.<lang>.md`, etc.). → Mitigation: the CLI prompts for the prose-file shape from a known list (matching the `tag-prose` spec). If the spec evolves, the prompts update.
- **[Risk] CI/external scripts that called `make lint` break.** → Mitigation: CI only calls `make build`. Local scripts get a clear deprecation message if they hit the removed Makefile target. Document the rename in the proposal Impact.
- **[Risk] `Translation_key` is not always identical to the directory name in pages and tag-prose.** → Mitigation: `--all-translations` semantics need to handle pages (flat layout, slugs alone) and tag-prose differently from posts. Pages and tag-prose use directory-or-namespace-based grouping rather than `Translation_key`. The spec covers this explicitly.

## Migration Plan

This change ships new tooling; it doesn't modify existing content. No migration is needed. After merge:

1. Authors install (`pip install -e .` in venv) to get `garden` on PATH.
2. `make lint` is removed from the Makefile; users run `garden lint` instead.
3. Existing scripts/CI: only `make build` and `make dev` remain in the Makefile, both unchanged.

Rollback: revert the change. The Makefile's `lint` target can be reinstated trivially; no on-disk content state is touched.

## Open Questions

- **Does `garden translate` copy the body content or leave it empty?** Recommendation: copy the body verbatim (so the author has the original prose to translate from). Confirmed in spec.
- **Do tag-prose lifecycle commands (`publish`/`draft`/`archive`) make sense?** Tag-prose files use `Status: hidden` permanently (they're rendered into tag pages, not indexed as posts). Recommendation: lifecycle commands operate on posts only; pages and tag-prose are out of scope. Spec'd.
- **Should `garden new --kind tag-prose` accept a non-existent tag and create the directory, or refuse?** Recommendation: prompt for confirmation before creating a new tag directory; in non-TTY mode, accept silently with `--create-tag` flag. Spec'd as a scenario.
