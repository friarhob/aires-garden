# content-model Spec Delta — refactor-homepage

## ADDED Requirements

### Requirement: Intro files have a schema-validated frontmatter

Every Markdown file under `content/intro/` SHALL declare frontmatter that conforms to the intro schema. Required fields are `Title`, `Lang`, and `Status`. Forbidden fields are `Slug`, `Translation_key`, and `Tags`. Any other field is a validation error unless the schema is updated to accept it.

#### Scenario: All required fields are present
- **WHEN** an intro file is validated
- **THEN** validation succeeds only if `Title`, `Lang`, and `Status` are all present and well-typed.

#### Scenario: Lang is a valid ISO 639-1 alpha-2 code
- **WHEN** an intro file's `Lang` is validated
- **THEN** validation succeeds only under the same rule applied to posts and tag-prose (a two-letter, lowercase ISO 639-1 code; region-suffixed codes rejected).

#### Scenario: Status must be exactly `hidden`
- **WHEN** an intro file declares `Status: hidden`
- **THEN** validation succeeds.

#### Scenario: Other Status values are rejected on intro files
- **WHEN** an intro file declares `Status: draft` or `Status: published`
- **THEN** validation fails with an "intro Status must be hidden" error naming the offending value. (Mirrors the tag-prose narrowing of the project-level `Status` enum.)

#### Scenario: Forbidden fields are rejected
- **WHEN** an intro file carries `Slug`, `Translation_key`, or `Tags`
- **THEN** validation fails with a "forbidden field on intro" error naming the field.

#### Scenario: Unknown fields are rejected
- **WHEN** an intro file carries any other field not declared in the intro schema
- **THEN** validation fails with a "unknown field" error naming the field.

### Requirement: Intro files have a strict filename ↔ frontmatter contract

Every intro file SHALL live at `content/intro/<scope>.<lang>.md`, where `<scope>` is one of the literal tokens `all` or `lang`, and `<lang>` equals the file's frontmatter `Lang`. The directory `content/intro/` is flat — no per-slug subdirectory exists, and any file deeper than `content/intro/<filename>.md` is a validation error.

#### Scenario: File lives directly under `content/intro/`
- **WHEN** an intro file's path is inspected
- **THEN** validation fails if the file lives in a subdirectory of `content/intro/` (e.g. `content/intro/something/all.en.md` is rejected — the directory layout is flat).

#### Scenario: Filename scope segment is `all` or `lang`
- **WHEN** an intro file is named `<stem1>.<stem2>.md`
- **THEN** validation fails if `<stem1>` is not exactly `all` or exactly `lang`.

#### Scenario: Filename lang segment equals frontmatter Lang
- **WHEN** an intro file is named `<scope>.<lang>.md`
- **THEN** validation fails if `<lang>` does not equal the file's frontmatter `Lang`.

#### Scenario: Errors name the specific axis of mismatch
- **WHEN** an intro file fails the filename ↔ frontmatter check
- **THEN** the error message names which axis (path-depth, scope token, or lang) is wrong, and shows both the on-disk value and the frontmatter value where applicable.

### Requirement: Intro files within `content/intro/` have unique `(scope, lang)` pairs

Within `content/intro/`, each `(scope, lang)` pair SHALL be unique. No two `all.<same-lang>.md` files may exist, and no two `lang.<same-lang>.md` files may exist.

#### Scenario: Duplicate (scope, lang) is rejected
- **WHEN** two files under `content/intro/` share the same parsed `(scope, lang)` pair (collision detected on parsed filename, not on frontmatter alone)
- **THEN** validation fails naming both colliding files.

## MODIFIED Requirements

### Requirement: Frontmatter validation runs at build time and aborts on error

`make build` SHALL execute the same validation as the standalone CLI; any validation error in any post, page, tag-prose, or intro file aborts the build with a non-zero exit code, before any HTML is written to `output/`.

#### Scenario: Plugin is registered in pelicanconf.py
- **WHEN** `pelicanconf.py` is inspected
- **THEN** its `PLUGINS` list includes `frontmatter_lint` (or the equivalent module path).

#### Scenario: A bad post fails the build
- **WHEN** any post or page in `content/` fails schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report.

#### Scenario: A bad tag-prose file fails the build
- **WHEN** any file under `content/tag-prose/` fails the tag-prose schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report naming the offending tag-prose file.

#### Scenario: A bad intro file fails the build
- **WHEN** any file under `content/intro/` fails the intro schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report naming the offending intro file.

#### Scenario: A clean tree passes the build
- **WHEN** every post, page, tag-prose, and intro file in `content/` passes schema validation
- **THEN** `make build` completes successfully and produces `output/`.

#### Scenario: All errors are reported, not just the first
- **WHEN** multiple posts, pages, tag-prose, and/or intro files have validation errors in a single run
- **THEN** the build report lists every failing file with every per-file error, not only the first failure encountered.

### Requirement: The standalone CLI traverses tag-prose and intro alongside posts and pages

The `python -m frontmatter_lint <content-root>` entrypoint SHALL discover and validate files under `content/tag-prose/` and `content/intro/` in addition to `content/posts/` and `content/pages/`, sharing the same schema module.

#### Scenario: CLI walks the tag-prose tree
- **WHEN** `python -m frontmatter_lint content` is run against a tree containing files under `content/tag-prose/`
- **THEN** every tag-prose file is validated against the tag-prose schema, and any errors are reported in the same file-anchored, grouped output format used for posts and pages.

#### Scenario: CLI walks the intro tree
- **WHEN** `python -m frontmatter_lint content` is run against a tree containing files under `content/intro/`
- **THEN** every intro file is validated against the intro schema, and any errors are reported in the same file-anchored, grouped output format used for posts, pages, and tag-prose.

#### Scenario: CLI exits non-zero when only tag-prose files have errors
- **WHEN** posts and pages are clean but at least one tag-prose file fails validation
- **THEN** the command exits with a non-zero status and prints the tag-prose file's per-file error block.

#### Scenario: CLI exits non-zero when only intro files have errors
- **WHEN** posts, pages, and tag-prose are clean but at least one intro file fails validation
- **THEN** the command exits with a non-zero status and prints the intro file's per-file error block.

#### Scenario: Plugin and CLI share the tag-prose schema
- **WHEN** `plugins/frontmatter_lint/` is inspected
- **THEN** the tag-prose validator lives in `schema.py` (or a sibling module imported by it) and is consumed by both the plugin (`__init__.py`) and the CLI (`cli.py`); neither duplicates the schema.

#### Scenario: Plugin and CLI share the intro schema
- **WHEN** `plugins/frontmatter_lint/` is inspected
- **THEN** the intro validator lives in `schema.py` (or a sibling module imported by it) and is consumed by both the plugin (`__init__.py`) and the CLI (`cli.py`); neither duplicates the schema.
