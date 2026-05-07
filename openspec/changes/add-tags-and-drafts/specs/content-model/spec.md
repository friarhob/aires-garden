## MODIFIED Requirements

### Requirement: Posts have a schema-validated frontmatter

Every Markdown file under `content/posts/` SHALL declare frontmatter that conforms to the post schema. Required fields are `Title`, `Slug`, `Date`, `Lang`, `Translation_key`, and `Status`. Optional fields are `Tags`. Any other field is a validation error unless the schema is updated to accept it.

#### Scenario: All required fields are present
- **WHEN** a post file is validated
- **THEN** validation succeeds only if `Title`, `Slug`, `Date`, `Lang`, `Translation_key`, and `Status` are all present and well-typed.

#### Scenario: Slug is lowercase kebab-case
- **WHEN** a post's `Slug` is validated
- **THEN** validation succeeds only if it matches the regex `^[a-z0-9]+(-[a-z0-9]+)*$` (lowercase letters, digits, and single hyphens between segments).

#### Scenario: Translation_key follows the same shape as Slug
- **WHEN** a post's `Translation_key` is validated
- **THEN** validation succeeds only if it matches `^[a-z0-9]+(-[a-z0-9]+)*$`.

#### Scenario: Date is ISO 8601 parseable
- **WHEN** a post's `Date` is validated
- **THEN** validation succeeds only if it parses as a date or datetime in any form Pelican itself accepts (`YYYY-MM-DD`, `YYYY-MM-DD HH:MM`, `YYYY-MM-DDTHH:MM:SSZ`).

#### Scenario: Tags is a list of non-empty strings
- **WHEN** a post's `Tags` is validated
- **THEN** validation succeeds if the field is omitted, an empty list, or a list of one-or-more non-empty strings.

#### Scenario: Each tag must produce a non-empty slug under Pelican's slugify
- **WHEN** a post carries `Tags: ["!!!"]`, `Tags: ["   "]`, or any other value that produces an empty string under `pelican.utils.slugify(...)`
- **THEN** validation fails with an "empty tag slug" error naming the offending tag value.

#### Scenario: No two tags within one post may produce the same slug
- **WHEN** a post carries `Tags: [<a>, <b>]` (or more) where `slugify(a) == slugify(b)` (e.g. `Tags: ["Rant", "rant"]`, `Tags: ["DSL", "dsl"]`)
- **THEN** validation fails with a "duplicate tag slug" error naming both originating tag values and the colliding slug.

#### Scenario: Unknown fields are rejected
- **WHEN** a post carries a field not declared in the schema (e.g. `Author`, `Category`, `Cover_image`)
- **THEN** validation fails with a "unknown field" error naming the field.

### Requirement: Frontmatter validation runs at build time and aborts on error

`make build` SHALL execute the same validation as the standalone CLI; any validation error in any post, page, or tag-prose file aborts the build with a non-zero exit code, before any HTML is written to `output/`.

#### Scenario: Plugin is registered in pelicanconf.py
- **WHEN** `pelicanconf.py` is inspected
- **THEN** its `PLUGINS` list includes `frontmatter_lint` (or the equivalent module path).

#### Scenario: A bad post fails the build
- **WHEN** any post or page in `content/` fails schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report.

#### Scenario: A bad tag-prose file fails the build
- **WHEN** any file under `content/tag-prose/` fails the tag-prose schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report naming the offending tag-prose file.

#### Scenario: A clean tree passes the build
- **WHEN** every post, page, and tag-prose file in `content/` passes schema validation
- **THEN** `make build` completes successfully and produces `output/`.

#### Scenario: All errors are reported, not just the first
- **WHEN** multiple posts, pages, and/or tag-prose files have validation errors in a single run
- **THEN** the build report lists every failing file with every per-file error, not only the first failure encountered.

## ADDED Requirements

### Requirement: Tag-prose files have a schema-validated frontmatter

Every Markdown file under `content/tag-prose/<slug>/` SHALL declare frontmatter that conforms to the tag-prose schema. Required fields are `Title`, `Lang`, and `Status`. Forbidden fields are `Slug`, `Translation_key`, and `Tags`. Any other field is a validation error unless the schema is updated to accept it.

#### Scenario: All required fields are present
- **WHEN** a tag-prose file is validated
- **THEN** validation succeeds only if `Title`, `Lang`, and `Status` are all present and well-typed.

#### Scenario: Lang is a valid ISO 639-1 alpha-2 code
- **WHEN** a tag-prose file's `Lang` is validated
- **THEN** validation succeeds only under the same rule applied to posts (a two-letter, lowercase ISO 639-1 code; region-suffixed codes rejected).

#### Scenario: Status must be exactly `hidden`
- **WHEN** a tag-prose file declares `Status: hidden`
- **THEN** validation succeeds.

#### Scenario: Other Status values are rejected on tag-prose files
- **WHEN** a tag-prose file declares `Status: draft` or `Status: published`
- **THEN** validation fails with a "tag-prose Status must be hidden" error naming the offending value (the project-level `Status` enum from ADR-0006 still permits these for posts and pages, but tag-prose narrows the constraint).

#### Scenario: Forbidden fields are rejected
- **WHEN** a tag-prose file carries `Slug`, `Translation_key`, or `Tags`
- **THEN** validation fails with a "forbidden field on tag-prose" error naming the field.

#### Scenario: Unknown fields are rejected
- **WHEN** a tag-prose file carries any other field not declared in the tag-prose schema
- **THEN** validation fails with a "unknown field" error naming the field.

### Requirement: Tag-prose files have a strict filename ↔ frontmatter contract

Every tag-prose file SHALL live at `content/tag-prose/<slug>/<scope>.<lang>.md`, where `<slug>` is any directory name matching the post `Slug` regex, `<scope>` is one of the literal tokens `all` or `lang`, and `<lang>` equals the file's frontmatter `Lang`.

#### Scenario: Directory name matches the Slug regex
- **WHEN** a tag-prose file lives at `content/tag-prose/<dir>/...`
- **THEN** validation fails if `<dir>` does not match `^[a-z0-9]+(-[a-z0-9]+)*$` (the same regex applied to post `Slug`).

#### Scenario: Filename scope segment is `all` or `lang`
- **WHEN** a tag-prose file is named `<stem1>.<stem2>.md`
- **THEN** validation fails if `<stem1>` is not exactly `all` or exactly `lang`.

#### Scenario: Filename lang segment equals frontmatter Lang
- **WHEN** a tag-prose file is named `<scope>.<lang>.md`
- **THEN** validation fails if `<lang>` does not equal the file's frontmatter `Lang`.

#### Scenario: Errors name the specific axis of mismatch
- **WHEN** a tag-prose file fails the filename ↔ frontmatter check
- **THEN** the error message names which axis (directory-slug, scope token, or lang) is wrong, and shows both the on-disk value and the frontmatter value where applicable.

### Requirement: Tag-prose files within one slug directory have unique (scope, lang) pairs

For every directory under `content/tag-prose/`, each `(scope, lang)` pair within the directory SHALL be unique. No directory may contain two `all.<same-lang>.md` files or two `lang.<same-lang>.md` files.

#### Scenario: Sibling files have unique (scope, lang)
- **WHEN** a directory under `content/tag-prose/` contains two or more Markdown files
- **THEN** validation fails if any two files share the same `(scope, lang)` pair (collision detected on parsed filename, not on frontmatter alone).

### Requirement: The standalone CLI traverses tag-prose alongside posts and pages

The `python -m frontmatter_lint <content-root>` entrypoint SHALL discover and validate files under `content/tag-prose/` in addition to `content/posts/` and `content/pages/`, sharing the same schema module.

#### Scenario: CLI walks the tag-prose tree
- **WHEN** `python -m frontmatter_lint content` is run against a tree containing files under `content/tag-prose/`
- **THEN** every tag-prose file is validated against the tag-prose schema, and any errors are reported in the same file-anchored, grouped output format used for posts and pages.

#### Scenario: CLI exits non-zero when only tag-prose files have errors
- **WHEN** posts and pages are clean but at least one tag-prose file fails validation
- **THEN** the command exits with a non-zero status and prints the tag-prose file's per-file error block.

#### Scenario: Plugin and CLI share the tag-prose schema
- **WHEN** `plugins/frontmatter_lint/` is inspected
- **THEN** the tag-prose validator lives in `schema.py` (or a sibling module imported by it) and is consumed by both the plugin (`__init__.py`) and the CLI (`cli.py`); neither duplicates the schema.
