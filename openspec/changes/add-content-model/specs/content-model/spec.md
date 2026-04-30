## ADDED Requirements

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

#### Scenario: Unknown fields are rejected
- **WHEN** a post carries a field not declared in the schema (e.g. `Author`, `Category`, `Cover_image`)
- **THEN** validation fails with a "unknown field" error naming the field.

### Requirement: Pages have a schema-validated frontmatter

Every Markdown file under `content/pages/` SHALL declare frontmatter that conforms to the page schema. Required fields are `Title` and `Status`. Optional fields are `Lang`, `Save_as`, and `URL`. Any other field is a validation error unless the schema is updated to accept it.

#### Scenario: All required page fields are present
- **WHEN** a page file is validated
- **THEN** validation succeeds only if `Title` and `Status` are both present and well-typed.

#### Scenario: Page Lang is optional but validated when present
- **WHEN** a page omits `Lang`
- **THEN** validation succeeds without a `Lang` value (the page inherits Pelican's `DEFAULT_LANG` at render time).

#### Scenario: Page Lang, when present, follows the post Lang rule
- **WHEN** a page's `Lang` is set
- **THEN** validation succeeds only if it is a valid ISO 639-1 alpha-2 code (the same constraint applied to posts).

#### Scenario: Pages MAY omit Slug, Translation_key, and Tags
- **WHEN** a page omits `Slug`, `Translation_key`, or `Tags`
- **THEN** validation does not fail on their absence (these fields are post-only).

#### Scenario: Unknown page fields are rejected
- **WHEN** a page carries a field not declared in the page schema
- **THEN** validation fails with a "unknown field" error naming the field.

### Requirement: Status accepts exactly `{draft, published, hidden}`

The `Status` field SHALL accept exactly the values `draft`, `published`, and `hidden`, applying identically to posts and pages. This deviates from the project brief (which listed only `draft` and `published`) and is recorded in [ADR-0006](../../decisions/0006-status-enum.md).

#### Scenario: Each enum value is accepted
- **WHEN** a post or page sets `Status` to any of `draft`, `published`, or `hidden`
- **THEN** validation succeeds.

#### Scenario: Other values are rejected
- **WHEN** a post or page sets `Status` to any other value (e.g. `live`, `wip`, `archived`)
- **THEN** validation fails with an error listing the allowed values.

#### Scenario: Status has no schema default
- **WHEN** a post or page omits `Status` entirely
- **THEN** validation fails — authors must declare the value explicitly.

### Requirement: `Lang` is a valid ISO 639-1 alpha-2 code

The `Lang` field SHALL be a two-letter, lowercase ISO 639-1 code, validated against the `langcodes` library at lint time. BCP 47 region-suffixed values (e.g. `pt-br`) are rejected at this stage, per ADR-0004 rule 4.

#### Scenario: Documented language codes pass
- **WHEN** `Lang` is `en`, `pt`, `es`, `fr`, or any other valid ISO 639-1 alpha-2 code
- **THEN** validation succeeds.

#### Scenario: Two-letter typos are rejected
- **WHEN** `Lang` is a two-letter string that is not a valid ISO 639-1 code (e.g. `xy`, `qq`)
- **THEN** validation fails with an "invalid ISO 639-1 code" error.

#### Scenario: Region-suffixed codes are rejected
- **WHEN** `Lang` is a BCP 47 region-suffixed code (e.g. `pt-br`, `en-us`)
- **THEN** validation fails — only alpha-2 is allowed at this stage.

### Requirement: Posts have a strict filename ↔ frontmatter contract

Every post file SHALL live at `content/posts/<dir>/<slug>.<lang>.md`, where `<dir>` equals the file's `Translation_key`, `<slug>` equals its `Slug`, and `<lang>` equals its `Lang`. This makes ADR-0004's directory-anchor convention a checked invariant rather than prose.

#### Scenario: Directory name equals Translation_key
- **WHEN** a post is validated
- **THEN** validation fails if the immediate parent directory's name does not equal the file's `Translation_key`.

#### Scenario: Filename slug segment equals frontmatter Slug
- **WHEN** a post file is named `<stem>.<lang>.md`
- **THEN** validation fails if `<stem>` does not equal the file's `Slug`.

#### Scenario: Filename lang segment equals frontmatter Lang
- **WHEN** a post file is named `<stem>.<lang>.md`
- **THEN** validation fails if `<lang>` does not equal the file's `Lang`.

#### Scenario: Errors name the specific axis of mismatch
- **WHEN** a post fails the filename ↔ frontmatter check
- **THEN** the error message names which axis (directory, slug, or lang) is wrong, and shows both the on-disk value and the frontmatter value.

### Requirement: Pages have advisory filename rules only

Pages SHALL be validated only on frontmatter content; their filenames are not bound to any field.

#### Scenario: Page filenames are not enforced
- **WHEN** a page file's name is `404.md`, `about.md`, or any other `*.md`
- **THEN** validation does not check the filename against any field.

#### Scenario: Page directory layout is not enforced
- **WHEN** a page lives directly under `content/pages/` (no per-page subdirectory)
- **THEN** validation does not require a directory match.

### Requirement: `Translation_key` is consistent within each post directory

For every directory under `content/posts/`, all sibling Markdown files SHALL declare the same `Translation_key`, equal to the directory name, and each `(Slug, Lang)` pair within that directory SHALL be unique.

#### Scenario: All siblings share the same Translation_key
- **WHEN** a directory under `content/posts/` contains two or more Markdown files
- **THEN** validation fails if any pair of siblings declares different `Translation_key` values.

#### Scenario: Sibling Slug values are unique per Lang
- **WHEN** a directory under `content/posts/` contains two or more Markdown files
- **THEN** validation fails if two files declare the same `Lang` (i.e. two translations claim to be the same language) or if two files declare the same `Slug` under different `Lang` values (a slug must belong to one language within a group).

### Requirement: Frontmatter validation runs at build time and aborts on error

`make build` SHALL execute the same validation as the standalone CLI; any validation error in any post or page aborts the build with a non-zero exit code, before any HTML is written to `output/`.

#### Scenario: Plugin is registered in pelicanconf.py
- **WHEN** `pelicanconf.py` is inspected
- **THEN** its `PLUGINS` list includes `frontmatter_lint` (or the equivalent module path).

#### Scenario: A bad post fails the build
- **WHEN** any post or page in `content/` fails schema validation and `make build` is run
- **THEN** the command exits with a non-zero status and prints a file-anchored error report.

#### Scenario: A clean tree passes the build
- **WHEN** every post and page in `content/` passes schema validation
- **THEN** `make build` completes successfully and produces `output/`.

#### Scenario: All errors are reported, not just the first
- **WHEN** multiple posts and/or pages have validation errors in a single run
- **THEN** the build report lists every failing file with every per-file error, not only the first failure encountered.

### Requirement: A standalone CLI runs the same validation

A `python -m frontmatter_lint` entrypoint SHALL exist that validates the content tree without booting Pelican, sharing the same schema module the plugin uses.

#### Scenario: CLI exits zero on a clean tree
- **WHEN** `python -m frontmatter_lint content` is run against a content tree with no errors
- **THEN** the command exits with status `0` and prints no per-file error blocks.

#### Scenario: CLI exits non-zero on errors
- **WHEN** `python -m frontmatter_lint content` is run against a content tree with at least one validation error
- **THEN** the command exits with a non-zero status and prints the same file-anchored error format as the plugin.

#### Scenario: Plugin and CLI share schema code
- **WHEN** `plugins/frontmatter_lint/` is inspected
- **THEN** the plugin (`__init__.py`) and the CLI (`cli.py`) both import their validators from `schema.py`, and `schema.py` does not import from Pelican.

### Requirement: Validation errors are file-anchored and grouped

Validation output SHALL group errors by file, list every error per file, and use POSIX-style relative paths so logs are grep-friendly and humans can scan top-down.

#### Scenario: Errors are grouped per file
- **WHEN** a file has two or more validation errors
- **THEN** the report prints the file's path once, followed by an indented bullet for each error.

#### Scenario: Files are sorted by path
- **WHEN** more than one file has errors
- **THEN** the report orders files lexicographically by their POSIX-style relative path.

#### Scenario: Error message names the field and the offending value
- **WHEN** a single field fails validation
- **THEN** its bullet names the field, the rule that failed, and the value that triggered the failure.

### Requirement: Project decision log records the Status enum extension

A new ADR SHALL be added under `openspec/decisions/` recording the decision to extend the `Status` enum from the project brief's `{draft, published}` to `{draft, published, hidden}`, including the rejected alternatives.

#### Scenario: ADR-0006 exists and is Accepted
- **WHEN** `openspec/decisions/0006-status-enum.md` is inspected
- **THEN** its `## Status` line reads `Accepted` with the decision date, and its body includes Context, Decision, and Consequences sections naming both the chosen value set and the rejected per-content-type alternative.

#### Scenario: ADR is referenced from the spec
- **WHEN** the `Status accepts exactly {draft, published, hidden}` requirement is read
- **THEN** it links to `openspec/decisions/0006-status-enum.md` so future readers can follow the trail.

#### Scenario: ADR README index is updated
- **WHEN** `openspec/decisions/README.md` is inspected
- **THEN** its `## Index` section lists ADR-0006 alongside the existing ADRs.
