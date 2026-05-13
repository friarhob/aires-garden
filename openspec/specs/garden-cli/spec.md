# garden-cli Specification

## Purpose

Define the behaviour of the `garden` CLI — a Typer-based Python tool that scaffolds, translates, and manages the lifecycle of content files in the aires-garden project. The CLI wraps all common authoring operations so that content can be created, published, drafted, and archived without manual frontmatter editing.

## Requirements

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

---

### Requirement: `garden new` scaffolds a content file for a chosen kind

The `garden new` subcommand SHALL accept `--kind`, `--title`, `--slug`, and `--lang` options. Missing required fields trigger interactive prompts in TTY mode and fail with an error in non-TTY mode. The CLI SHALL validate every field before writing: `kind ∈ {post, page, tag-prose}`, `slug` matches `^[a-z0-9]+(-[a-z0-9]+)*$`, `lang` matches `^[a-z]{2}$` (per ADR-0004), `title` is non-empty after stripping whitespace. Invalid values cause a non-zero exit before any file is written.

The `--slug` option is not applicable to `--kind tag-prose`; it SHALL be ignored silently when both are supplied.

#### Scenario: All flags supplied creates a post
- **WHEN** `garden new --kind post --title "Hello" --slug hello --lang en` is run
- **THEN** a file is created at `content/posts/hello/hello.en.md` with frontmatter containing `Title: Hello`, `Slug: hello`, `Lang: en`, `Translation_key: hello`, `Status: draft`, and `Date:` set to today's date in `YYYY-MM-DD`. The colocated directory `content/posts/hello/assets/` is also created (empty).

#### Scenario: Missing flags trigger interactive prompts in TTY mode
- **WHEN** `garden new` is run with no flags AND stdin is a TTY
- **THEN** the user is prompted (in order) for `kind` (select from post/page/tag-prose), `title` (text), `slug` (text, defaulted from a slugified title — skipped for tag-prose), `lang` (text), and the file is then created with the resulting values.

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

#### Scenario: Refuses to overwrite an existing file
- **WHEN** `garden new --kind post --title "Hello" --slug hello --lang en` is run AND `content/posts/hello/hello.en.md` already exists
- **THEN** the command exits non-zero with an error stating the file exists, and the existing file is not modified.

---

### Requirement: `garden new` generates slugs with Unicode normalisation

When `garden new` derives a default slug from a title (interactively or otherwise), it SHALL transliterate accented Latin characters to their ASCII base before applying the slug pattern. Specifically: the title is Unicode-normalised to NFD, combining diacritical marks (Unicode category `Mn`) are removed, then non-ASCII non-alphanumeric characters are replaced with hyphens, and leading/trailing hyphens are stripped.

#### Scenario: Accented title produces an ASCII slug
- **WHEN** `garden new --kind post --title "Água no Balão" --lang pt` is run interactively
- **THEN** the default slug offered is `agua-no-balao` (not `gua-no-bal-o` or any other broken form).

#### Scenario: French accents are normalised
- **WHEN** the title "Crème Brûlée" is used as the slug source
- **THEN** the default slug is `creme-brulee`.

#### Scenario: Plain ASCII titles are unchanged
- **WHEN** the title "Hello World" is used as the slug source
- **THEN** the default slug is `hello-world` (behaviour unchanged from pre-normalisation).

---

### Requirement: `garden translate` produces a paired-language file from an existing source

The `garden translate [<slug>] --to <lang>` subcommand SHALL locate the source file by per-language slug (matching against parsed `Slug:` headers in `content/`), copy it to a sibling file with the new `Lang`, swap the `Slug:` line if the user supplies a translated slug (via `--slug` flag or interactive prompt), update `Title:` to the translated value (via `--title` flag or interactive prompt), preserve `Translation_key:` from the source, and copy the body verbatim. The new file's `Status:` SHALL be `draft` regardless of the source's status.

The `<slug>` argument is optional. When omitted in TTY mode, an interactive autocomplete picker lists all posts in the content tree (format: `slug — Title (lang, status)`); the author selects the source. When omitted in non-TTY mode, the command exits non-zero with a clear error.

#### Scenario: Slug omitted in TTY mode shows post picker
- **WHEN** `garden translate --to pt` is run with no positional slug AND stdin is a TTY
- **THEN** an autocomplete picker is shown listing all posts; the author selects one and the translate flow continues with that post as the source.

#### Scenario: Slug omitted in non-TTY mode exits non-zero
- **WHEN** `garden translate --to pt` is run with no positional slug AND stdin is NOT a TTY
- **THEN** the command exits non-zero with an error stating the slug is required in non-interactive mode.

#### Scenario: Translates an English post to Portuguese
- **WHEN** `garden translate hello --to pt --slug ola --title "Olá"` is run AND `content/posts/hello/hello.en.md` exists with `Slug: hello`, `Translation_key: hello`
- **THEN** a new file is created at `content/posts/hello/ola.pt.md` with `Title: Olá`, `Slug: ola`, `Lang: pt`, `Translation_key: hello`, `Status: draft`, the source's body content, and (if the source has a `Date:`) the same `Date:`.

#### Scenario: Refuses if target language file already exists
- **WHEN** `garden translate hello --to pt --slug ola --title "Olá"` is run AND `content/posts/hello/ola.pt.md` already exists
- **THEN** the command exits non-zero with an error stating the target file exists, and the existing file is not modified.

#### Scenario: Refuses if source slug not found
- **WHEN** `garden translate nonexistent --to pt --slug nada --title "Nada"` is run AND no file in `content/` has `Slug: nonexistent`
- **THEN** the command exits non-zero with an error stating the source slug was not found.

#### Scenario: Body content is copied verbatim
- **WHEN** the source file's body contains a multi-paragraph passage, code blocks, and embed tags
- **THEN** the translated file's body is byte-identical to the source's body (the author then translates the text).

#### Scenario: Validation errors fail without writing
- **WHEN** `garden translate hello --to PT --slug ola --title "Olá"` is run (uppercase `PT`)
- **THEN** the command exits non-zero with an error citing the lang pattern, and no file is written.

---

### Requirement: Lifecycle subcommands flip `Status:` atomically across one or many translations

The subcommands `garden publish [<slug>]`, `garden draft [<slug>]`, and `garden archive [<slug>]` SHALL flip the `Status:` field of the matched file. They accept `--all-translations` / `--no-all-translations` (boolean flag pair); if neither is supplied, the CLI prompts interactively in TTY mode and fails in non-TTY mode. When `--all-translations` is in effect, the operation includes every file sharing the matched file's `Translation_key`. The operation SHALL be atomic: if any included file is in a refusal state for the requested transition, the command exits non-zero with no file modified, and the error names every offending file. The `--force` flag SHALL bypass refusal checks and apply the transition unconditionally.

The `<slug>` positional argument is optional. When omitted in TTY mode, an interactive autocomplete picker lists all posts in the content tree (format: `slug — Title (lang, status)`); the author selects the target. When omitted in non-TTY mode, the command exits non-zero with a clear error.

#### Scenario: Slug omitted in TTY mode shows post picker
- **WHEN** any of `garden publish`, `garden draft`, or `garden archive` is run with no positional slug AND stdin is a TTY
- **THEN** an autocomplete picker is shown listing all posts; the author selects one and the lifecycle operation continues normally.

#### Scenario: Slug omitted in non-TTY mode exits non-zero
- **WHEN** any of `garden publish`, `garden draft`, or `garden archive` is run with no positional slug AND stdin is NOT a TTY
- **THEN** the command exits non-zero with an error stating the slug is required in non-interactive mode.

#### Scenario: publish flips draft to published
- **WHEN** `garden publish hello --no-all-translations` is run AND `content/posts/hello/hello.en.md` has `Status: draft`
- **THEN** the file's `Status:` becomes `published` and no other file is modified.

#### Scenario: publish refuses on a hidden file
- **WHEN** `garden publish hidden-thing --no-all-translations` is run AND the matched file has `Status: hidden`
- **THEN** the command exits non-zero with an error stating the file is hidden and suggesting `--force`. The file is not modified.

#### Scenario: publish with --force bypasses the hidden check
- **WHEN** `garden publish hidden-thing --no-all-translations --force` is run AND the matched file has `Status: hidden`
- **THEN** the file's `Status:` becomes `published`.

#### Scenario: draft flips published to draft
- **WHEN** `garden draft hello --no-all-translations` is run AND the matched file has `Status: published`
- **THEN** the file's `Status:` becomes `draft`.

#### Scenario: draft refuses on a hidden file without --force
- **WHEN** `garden draft hidden-thing --no-all-translations` is run AND the matched file has `Status: hidden`
- **THEN** the command exits non-zero with an error stating the file is hidden and suggesting `--force`. The file is not modified.

#### Scenario: archive flips published to hidden
- **WHEN** `garden archive hello --no-all-translations` is run AND the matched file has `Status: published`
- **THEN** the file's `Status:` becomes `hidden`.

#### Scenario: archive refuses on a draft without --force
- **WHEN** `garden archive draft-thing --no-all-translations` is run AND the matched file has `Status: draft`
- **THEN** the command exits non-zero with an error stating the file is a draft and suggesting `--force`. The file is not modified.

#### Scenario: --all-translations operates on every translation
- **WHEN** `garden publish hello --all-translations` is run AND `content/posts/hello/` contains `hello.en.md` (`Status: draft`, `Translation_key: hello`) and `ola.pt.md` (`Status: draft`, `Translation_key: hello`)
- **THEN** both files have their `Status:` set to `published`.

#### Scenario: Atomic refusal: one bad file blocks the whole set
- **WHEN** `garden publish hello --all-translations` is run AND the EN file has `Status: draft` but the PT file has `Status: hidden`
- **THEN** the command exits non-zero with an error naming the PT file as the refusing file. Neither file is modified.

#### Scenario: --all-translations with --force flips every file regardless of state
- **WHEN** `garden publish hello --all-translations --force` is run with the same mixed-state setup
- **THEN** both the EN and PT files end up with `Status: published`.

#### Scenario: Omitting --all-translations triggers an interactive prompt in TTY mode
- **WHEN** `garden publish hello` is run with no `--all-translations` / `--no-all-translations` AND stdin is a TTY
- **THEN** the user is prompted with a yes/no question about including every translation, and the operation proceeds with the chosen scope.

#### Scenario: Omitting --all-translations fails in non-TTY mode
- **WHEN** `garden publish hello` is run with no `--all-translations` / `--no-all-translations` AND stdin is NOT a TTY
- **THEN** the command exits non-zero with an error stating that `--all-translations` or `--no-all-translations` must be supplied explicitly in non-interactive mode.

#### Scenario: Slug not found
- **WHEN** any of `garden publish`, `garden draft`, or `garden archive` is run with a slug that matches no file
- **THEN** the command exits non-zero with an error stating the slug was not found.

#### Scenario: Lifecycle subcommands operate only on posts
- **WHEN** any lifecycle subcommand is run with a slug that resolves to a file under `content/pages/` or `content/tag-prose/`
- **THEN** the command exits non-zero with an error stating that lifecycle commands apply only to posts.

---

### Requirement: `garden lint` runs the existing frontmatter_lint with no logic duplication

The `garden lint` subcommand SHALL invoke the existing `frontmatter_lint` Python module against `content/`, returning the same exit code and reporting the same errors. The CLI SHALL NOT contain its own copy of any lint rule.

#### Scenario: garden lint exits 0 on a clean tree
- **WHEN** `garden lint` is run AND `content/` passes `frontmatter_lint`
- **THEN** the command exits 0 and produces no error output.

#### Scenario: garden lint exits non-zero on lint failures
- **WHEN** `garden lint` is run AND `content/` contains a file with malformed frontmatter
- **THEN** the command exits non-zero with the same error report `frontmatter_lint` would have produced.

#### Scenario: garden lint and frontmatter_lint agree
- **WHEN** the same content tree is run through both `garden lint` and `python -m frontmatter_lint content`
- **THEN** the two commands produce identical exit codes and identical error reports.

---

### Requirement: The CLI distinguishes interactive and non-interactive contexts

For every subcommand, missing required arguments SHALL prompt interactively when stdin is a TTY and SHALL fail fast with a non-zero exit code when stdin is NOT a TTY. Detection SHALL use `sys.stdin.isatty()`.

#### Scenario: TTY enables prompts
- **WHEN** any subcommand is run interactively with required arguments missing AND stdin is a TTY
- **THEN** the CLI prompts for each missing argument before proceeding.

#### Scenario: Non-TTY blocks prompts
- **WHEN** any subcommand is run with stdin redirected (e.g. `garden new < /dev/null`) AND required arguments are missing
- **THEN** the command exits non-zero with a "missing required argument" error and does not hang waiting for input.

---

### Requirement: File mutations are atomic at the filesystem level

Every CLI mutation of a content file SHALL be atomic with respect to the filesystem: the new content is written to a sibling temp file, then renamed over the original. A crash or signal during the write SHALL leave the original file unmodified. Multi-file operations (`--all-translations`) SHALL use the plan-then-apply pattern: validate every file's state first, then apply mutations only after all validations pass.

#### Scenario: Single-file write is atomic
- **WHEN** `garden publish hello` is interrupted mid-write
- **THEN** the original file at `content/posts/hello/hello.en.md` is either fully unchanged or fully updated; no partial-write state is observable.

#### Scenario: Multi-file plan-then-apply
- **WHEN** `garden publish hello --all-translations` is run with two valid target files
- **THEN** both files are validated for the requested transition before any file is written, and either both are updated or neither is updated.

---

### Requirement: Scaffolded files conform to the content-model spec

The frontmatter produced by `garden new` and `garden translate` SHALL pass `frontmatter_lint` without modification. Each kind writes only the fields that its schema allows:

- **post**: `Title`, `Slug`, `Date`, `Lang`, `Translation_key`, `Status`, `Tags` (in that order; `Tags:` is included even when empty).
- **page**: `Title`, `Lang`, `Status` only — no `Slug:`, no `Translation_key:`, no `Tags:`.
- **tag-prose**: `Title`, `Lang`, `Status: hidden` only — no `Slug:`, no `Translation_key:`, no `Tags:` (all three are forbidden by the content-model spec).

#### Scenario: A scaffolded post passes lint
- **WHEN** `garden new --kind post --title "Sample" --slug sample --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0.

#### Scenario: A scaffolded page passes lint
- **WHEN** `garden new --kind page --title "About" --slug about --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0 (the file contains no `Slug:` field).

#### Scenario: A scaffolded tag-prose file passes lint
- **WHEN** `garden new --kind tag-prose --title "Published works" --tag published-works --shape all --lang en` is run, then `garden lint` is run immediately afterwards
- **THEN** `garden lint` exits 0 (the file contains no `Slug:`, `Translation_key:`, or `Tags:` field).

#### Scenario: A translated file passes lint
- **WHEN** `garden translate hello --to pt --slug ola --title "Olá"` is run on an existing source, then `garden lint` is run
- **THEN** `garden lint` exits 0.

#### Scenario: Frontmatter field order matches existing content
- **WHEN** any file produced by `garden new` is opened
- **THEN** its frontmatter fields appear in canonical order for its kind, with no unexpected fields present.

---

### Requirement: New dependencies are pinned in `pyproject.toml`

The dependencies `typer` and `questionary` SHALL be added to `pyproject.toml`'s project dependencies, with version constraints permitting current stable releases. The `[project.scripts]` table SHALL register `garden = "garden.cli:app"` (or the equivalent module path resolving to the Typer app object).

#### Scenario: Dependencies are declared
- **WHEN** `pyproject.toml` is inspected
- **THEN** `typer` and `questionary` appear in the project's runtime dependency list.

#### Scenario: Console script is registered
- **WHEN** `pyproject.toml` is inspected
- **THEN** `[project.scripts]` (or equivalent) declares `garden = "garden.cli:app"` (or the equivalent path to the Typer entry point).
