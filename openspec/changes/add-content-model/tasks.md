## 1. Decision artifact (ADR-0006)

- [ ] 1.1 Create `openspec/decisions/0006-status-enum.md` with sections `## Status` (`Accepted` + today's date), `## Context` (brief listed `{draft, published}`; 404 page already uses `hidden`), `## Decision` (enum is `{draft, published, hidden}`, applied identically to posts and pages, no schema default), `## Consequences` (positive: 404 and future utility pages have a first-class value; negative: small deviation from the brief; rejected alternatives: `{draft, published}` strict-to-brief, per-content-type rule).
- [ ] 1.2 Add a line for ADR-0006 in `openspec/decisions/README.md` under `## Index`, matching the existing entries' style.

## 2. Dependencies

- [ ] 2.1 In `pyproject.toml`, add `pydantic>=2,<3` to `[project].dependencies`.
- [ ] 2.2 In `pyproject.toml`, add `langcodes>=3,<4` to `[project].dependencies`.
- [ ] 2.3 Run `pip install -e .` to install the new deps in the local venv.

## 3. Schema module (pure validation logic)

- [ ] 3.1 Create `plugins/frontmatter_lint/__init__.py` as a package marker (Pelican-specific code lands later; this file starts empty or with the `register()` stub from task 5.1).
- [ ] 3.2 Create `plugins/frontmatter_lint/schema.py` with no Pelican imports.
- [ ] 3.3 In `schema.py`, define `PostFrontmatter` (pydantic v2 `BaseModel`) with fields `Title`, `Slug` (regex `^[a-z0-9]+(-[a-z0-9]+)*$`), `Date` (`date | datetime`), `Lang` (custom validator delegating to `langcodes.tag_is_valid` and rejecting region suffixes), `Translation_key` (same regex as Slug), `Status` (`Literal["draft", "published", "hidden"]`), `Tags` (optional `list[str]`, default `[]`, coerce single string to one-element list to match Pelican's `Tags: rant` shorthand). Set `model_config = ConfigDict(extra="forbid")`.
- [ ] 3.4 In `schema.py`, define `PageFrontmatter` (pydantic v2 `BaseModel`) with fields `Title`, `Status` (same `Literal`), and optional `Lang`, `Save_as`, `URL`. Set `extra="forbid"`.
- [ ] 3.5 In `schema.py`, define a `validate_post(path, frontmatter, dir_name) -> list[ValidationError]` function that runs `PostFrontmatter` validation, then performs the filename ↔ frontmatter checks (directory-name == `Translation_key`, filename stem == `Slug`, filename lang segment == `Lang`).
- [ ] 3.6 In `schema.py`, define a `validate_page(path, frontmatter) -> list[ValidationError]` function that runs `PageFrontmatter` validation only.
- [ ] 3.7 In `schema.py`, define a `validate_post_group(dir_name, files) -> list[ValidationError]` function that checks Translation_key consistency within a directory and `(Slug, Lang)` uniqueness across siblings.
- [ ] 3.8 In `schema.py`, define a `format_errors(errors) -> str` function that groups errors by file, sorts by path, and produces the indented bullet output documented in design D9.

## 4. CLI module

- [ ] 4.1 Create `plugins/frontmatter_lint/cli.py` importing only from `schema.py`, the standard library, and a small frontmatter parser (prefer `python-frontmatter` if cheap; otherwise a 20-line YAML-block reader using `yaml`).
- [ ] 4.2 Add `python-frontmatter` to `pyproject.toml` if used, pinned `>=1,<2`.
- [ ] 4.3 Implement `cli.py:main()` to walk `content/posts/<dir>/*.md` (group by parent dir, run `validate_post` per file + `validate_post_group` per dir) and `content/pages/*.md` (run `validate_page` per file).
- [ ] 4.4 Implement `cli.py` so it accepts an optional positional argument for the content root (defaults to `content`); print the formatted errors to stderr; exit 0 on clean, non-zero on any error.
- [ ] 4.5 Wire `python -m frontmatter_lint` to `cli.main()` by adding a `plugins/frontmatter_lint/__main__.py` that calls `cli.main()`.

## 5. Pelican plugin (build-time integration)

- [ ] 5.1 In `plugins/frontmatter_lint/__init__.py`, define `register()` that connects two Pelican signals: `article_generator_finalized` and `page_generator_finalized`.
- [ ] 5.2 In the `article_generator_finalized` handler, iterate `generator.articles + generator.translations`, group by source-file parent directory, and run `validate_post` + `validate_post_group` from `schema.py`. Append errors to a module-level list.
- [ ] 5.3 In the `page_generator_finalized` handler, iterate `generator.pages + generator.hidden_pages` and run `validate_page` from `schema.py`. Append errors to the same module-level list.
- [ ] 5.4 Have the second handler to run (or a `finalized` hook) raise `RuntimeError(format_errors(errors))` if the list is non-empty, so Pelican aborts before writing output. Verify experimentally that this propagates to a non-zero exit; if not, fall back to `sys.exit(1)` after printing.

## 6. Plugin registration

- [ ] 6.1 In `pelicanconf.py`, add `PLUGIN_PATHS = ["plugins"]` and `PLUGINS = ["frontmatter_lint"]` (verify against Pelican 4.x conventions; if a single import path is preferred, use that instead).
- [ ] 6.2 Confirm `publishconf.py` inherits the plugin (it imports `pelicanconf`), so prod builds run lint identically to dev.

## 7. Existing-content compliance

- [ ] 7.1 Run `python -m frontmatter_lint content` and `make build` against the current tree. If either fails, fix the offending frontmatter (likely candidates: `ola-jardim.pt.md` Tags shorthand if the schema doesn't coerce it; `404.md` if any unknown fields slip in).
- [ ] 7.2 Confirm the existing post `content/posts/ola-jardim/ola-jardim.pt.md` passes all post-side checks (filename matches, Lang valid, Status in enum, Translation_key matches dir name).
- [ ] 7.3 Confirm `content/pages/404.md` passes all page-side checks (Title + Status present, no unknown fields, no enforced filename).

## 8. Negative testing

- [ ] 8.1 Temporarily introduce a deliberately bad post (e.g. add a sibling file with mismatched `Slug`, or a typo in `Lang`, or an unknown field). Run `make build` and confirm it exits non-zero with a clear file-anchored report.
- [ ] 8.2 Confirm `python -m frontmatter_lint content` reports the same error and exits non-zero.
- [ ] 8.3 Revert the bad post; confirm `make build` and CLI both pass again.

## 9. Verification against specs

- [ ] 9.1 Run `openspec validate add-content-model --strict`; expect zero errors.
- [ ] 9.2 Walk each scenario in `specs/content-model/spec.md` and confirm the implementation satisfies it (manual checklist; tick each scenario off as verified).
- [ ] 9.3 Confirm the GitHub Actions deploy still passes on `main` after merging — the plugin runs in CI's `make build` for the first time, so an inadvertent CI-only failure surfaces here.
