# garden-cli Spec Delta — refactor-homepage

## MODIFIED Requirements

### Requirement: The `garden` CLI is invokable as both a console script and a Python module

The repository SHALL ship a Python package at `garden/` that registers a `garden` console-script entry point in `pyproject.toml`'s `[project.scripts]` table, AND provides a `garden/__main__.py` so that `python -m garden` produces identical behaviour. The CLI SHALL accept the same arguments and produce the same output regardless of which invocation form is used.

#### Scenario: Console script entry point is installed
- **WHEN** the project is installed in editable mode (`pip install -e .`) into a virtual environment
- **THEN** the `garden` command is available on PATH and `garden --help` lists the available subcommands.

#### Scenario: Module invocation works without entry point
- **WHEN** `python -m garden --help` is run from the repository root with the virtual environment active
- **THEN** the same help output is produced as `garden --help`.

#### Scenario: Top-level help lists every subcommand
- **WHEN** `garden --help` is run
- **THEN** the output names each of: `new`, `translate`, `publish`, `draft`, `archive`, `lint`, with a one-line description for each.

#### Scenario: `new --help` lists every supported kind
- **WHEN** `garden new --help` is run
- **THEN** the `--kind` option's help text names exactly: `post`, `page`, `tag-prose`, `intro`.

### Requirement: `garden new` scaffolds a content file for a chosen kind

The `garden new` subcommand SHALL accept `--kind`, `--title`, `--slug`, `--lang`, and `--scope` options. Missing required fields trigger interactive prompts in TTY mode and fail with an error in non-TTY mode. The CLI SHALL validate every field before writing: `kind ∈ {post, page, tag-prose, intro}`, `slug` matches `^[a-z0-9]+(-[a-z0-9]+)*$`, `lang` matches `^[a-z]{2}$` (per ADR-0004), `title` is non-empty after stripping whitespace, `scope ∈ {all, lang}` when supplied. Invalid values cause a non-zero exit before any file is written.

The `--slug` option is not applicable to `--kind tag-prose` or `--kind intro`; it SHALL be ignored silently when supplied with either kind. The `--scope` option is only applicable to `--kind intro`; it SHALL be ignored silently when supplied with another kind.

#### Scenario: All flags supplied creates a post
- **WHEN** `garden new --kind post --title "Hello" --slug hello --lang en` is run
- **THEN** a file is created at `content/posts/hello/hello.en.md` with frontmatter containing `Title: Hello`, `Slug: hello`, `Lang: en`, `Translation_key: hello`, `Status: draft`, and `Date:` set to today's date in `YYYY-MM-DD`. The colocated directory `content/posts/hello/assets/` is also created (empty).

#### Scenario: Missing flags trigger interactive prompts in TTY mode
- **WHEN** `garden new` is run with no flags AND stdin is a TTY
- **THEN** the user is prompted (in order) for `kind` (select from post/page/tag-prose/intro), `title` (text), `scope` (select from all/lang — only for intro), `slug` (text, defaulted from a slugified title — skipped for tag-prose and intro), `lang` (text), and the file is then created with the resulting values.

#### Scenario: Missing flags fail in non-TTY mode
- **WHEN** `garden new` is run with no flags AND stdin is NOT a TTY
- **THEN** the command exits non-zero with an error naming each missing required field.

#### Scenario: Invalid slug rejected
- **WHEN** `garden new --kind post --title "Hello" --slug "Hello World" --lang en` is run
- **THEN** the command exits non-zero with an error citing the slug pattern, and no file is written.

#### Scenario: Invalid lang rejected
- **WHEN** `garden new --kind post --title "Hello" --slug hello --lang english` is run
- **THEN** the command exits non-zero with an error citing the ISO 639-1 pattern, and no file is written.

#### Scenario: Empty title rejected
- **WHEN** `garden new --kind post --title "" --slug hello --lang en` is run
- **THEN** the command exits non-zero with an error stating the title cannot be empty, and no file is written.

#### Scenario: Page kind uses flat layout with no Slug in frontmatter
- **WHEN** `garden new --kind page --title "About" --slug about --lang en` is run
- **THEN** a file is created at `content/pages/about.en.md` with frontmatter containing only `Title: About`, `Lang: en`, `Status: hidden`. No `Slug:` field appears in the frontmatter. No per-page directory is created.

#### Scenario: Tag-prose kind shows existing-tag picker
- **WHEN** `garden new --kind tag-prose --lang en` is run AND stdin is a TTY
- **THEN** the user is presented with an autocomplete picker listing the tag directories that already exist under `content/tag-prose/`, plus a `[new tag]` option. The user selects a tag (or creates a new one), is prompted for the prose-file shape, and the resulting file is created at `content/tag-prose/<tag>/<shape>.<lang>.md` with frontmatter containing only `Title`, `Lang`, and `Status: hidden` — no `Slug:`, no `Translation_key:`.

#### Scenario: Tag-prose kind in non-TTY mode uses --tag and --shape flags
- **WHEN** `garden new --kind tag-prose --title "Foo" --tag my-tag --shape all --lang en` is run AND stdin is NOT a TTY AND `content/tag-prose/my-tag/` exists
- **THEN** the file is created at `content/tag-prose/my-tag/all.en.md` with frontmatter containing `Title: Foo`, `Lang: en`, `Status: hidden`. No `Slug:` field.

#### Scenario: Intro kind in TTY mode prompts for scope and lang only
- **WHEN** `garden new --kind intro` is run AND stdin is a TTY
- **THEN** the user is prompted for `title` (text), `scope` (select from `all` / `lang`), and `lang` (text). No slug prompt appears. The resulting file is created at `content/intro/<scope>.<lang>.md` with frontmatter containing only `Title`, `Lang`, and `Status: hidden` — no `Slug:`, no `Translation_key:`, no `Tags:`.

#### Scenario: Intro kind in non-TTY mode uses --scope and --lang flags
- **WHEN** `garden new --kind intro --title "Welcome" --scope all --lang en` is run AND stdin is NOT a TTY
- **THEN** the file is created at `content/intro/all.en.md` with frontmatter containing `Title: Welcome`, `Lang: en`, `Status: hidden`. No `Slug:` field.

#### Scenario: Intro kind in non-TTY mode requires --scope
- **WHEN** `garden new --kind intro --title "Welcome" --lang en` is run AND stdin is NOT a TTY (no `--scope`)
- **THEN** the command exits non-zero with an error stating that `--scope` is required in non-interactive mode, and no file is written.

#### Scenario: Intro kind rejects invalid scope
- **WHEN** `garden new --kind intro --title "Welcome" --scope tag --lang en` is run
- **THEN** the command exits non-zero with an error citing the scope value-set (`all` or `lang`), and no file is written.

#### Scenario: Intro kind silently ignores --slug
- **WHEN** `garden new --kind intro --title "Welcome" --scope all --lang en --slug ignored-value` is run AND stdin is NOT a TTY
- **THEN** the file is created at `content/intro/all.en.md` with no `Slug:` field; the `--slug` value is not used anywhere and no error or warning is emitted.

#### Scenario: Refuses to overwrite an existing file
- **WHEN** `garden new --kind post --title "Hello" --slug hello --lang en` is run AND `content/posts/hello/hello.en.md` already exists
- **THEN** the command exits non-zero with an error stating the file exists, and the existing file is not modified.

### Requirement: Scaffolded files conform to the content-model spec

The frontmatter produced by `garden new` and `garden translate` SHALL pass `frontmatter_lint` without modification. Each kind writes only the fields that its schema allows:

- **post**: `Title`, `Slug`, `Date`, `Lang`, `Translation_key`, `Status`, `Tags` (in that order; `Tags:` is included even when empty).
- **page**: `Title`, `Lang`, `Status` only — no `Slug:`, no `Translation_key:`, no `Tags:`.
- **tag-prose**: `Title`, `Lang`, `Status: hidden` only — no `Slug:`, no `Translation_key:`, no `Tags:` (all three are forbidden by the content-model spec).
- **intro**: `Title`, `Lang`, `Status: hidden` only — no `Slug:`, no `Translation_key:`, no `Tags:` (all three are forbidden by the content-model spec).

#### Scenario: A scaffolded post passes lint
- **WHEN** `garden new --kind post --title "Sample" --slug sample --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0.

#### Scenario: A scaffolded page passes lint
- **WHEN** `garden new --kind page --title "About" --slug about --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0 (the file contains no `Slug:` field).

#### Scenario: A scaffolded tag-prose file passes lint
- **WHEN** `garden new --kind tag-prose --title "Published works" --tag published-works --shape all --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0 (the file contains no `Slug:`, `Translation_key:`, or `Tags:` field).

#### Scenario: A scaffolded intro file passes lint
- **WHEN** `garden new --kind intro --title "Welcome" --scope all --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0 (the file contains no `Slug:`, `Translation_key:`, or `Tags:` field).

#### Scenario: A translated file passes lint
- **WHEN** `garden translate hello --to pt --slug ola --title "Olá"` is run on an existing source, then `garden lint` is run
- **THEN** `garden lint` exits 0.

#### Scenario: Frontmatter field order matches existing content
- **WHEN** any file produced by `garden new` is opened
- **THEN** its frontmatter fields appear in canonical order for its kind, with no unexpected fields present.
