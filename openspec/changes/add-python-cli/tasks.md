## 1. Package scaffold and dependencies

- [ ] 1.1 Create top-level `garden/` package: `__init__.py`, `__main__.py`, `cli.py`, `commands/__init__.py`, `tests/__init__.py`
- [ ] 1.2 Add `typer` and `questionary` to `[project.dependencies]` in `pyproject.toml`
- [ ] 1.3 Register `garden = "garden.cli:app"` under `[project.scripts]` in `pyproject.toml`
- [ ] 1.4 Wire `garden/__main__.py` to call `garden.cli.app()` so `python -m garden` works
- [ ] 1.5 In `garden/cli.py`, create a `typer.Typer()` `app` instance with help text identifying the CLI; subcommands attach to this app

## 2. Shared infrastructure

- [ ] 2.1 Implement `garden/validation.py` with field validators: `validate_kind(s) -> str`, `validate_slug(s) -> str` (regex `^[a-z0-9]+(-[a-z0-9]+)*$`), `validate_lang(s) -> str` (regex `^[a-z]{2}$`), `validate_title(s) -> str` (non-empty after strip). Each raises a `ValidationError` with a clear message on rejection.
- [ ] 2.2 Implement `garden/frontmatter_io.py`: `read_frontmatter(path: Path) -> tuple[dict, str]` returning (fields, body); `write_frontmatter(path: Path, fields: dict, body: str) -> None` that writes atomically (temp file + rename) with canonical field order (Title, Slug, Date, Lang, Translation_key, Status, Tags)
- [ ] 2.3 Implement `garden/content_index.py`: `walk_content(content_root: Path) -> list[ContentFile]` returning records with `path`, `kind` (post/page/tag-prose inferred from path), `slug`, `lang`, `translation_key`, `status`. Provide helpers `find_by_slug(index, slug) -> ContentFile | None` and `find_translations(index, translation_key) -> list[ContentFile]`
- [ ] 2.4 Implement `garden/prompts.py`: `is_tty() -> bool`, `prompt_text(message, default=None) -> str`, `prompt_select(message, choices) -> str`, `prompt_confirm(message, default=None) -> bool` — wrappers over questionary. Each helper SHALL raise a clear error if called when stdin is not a TTY.
- [ ] 2.5 Add unit tests for `validation.py` (every validator: pass + fail cases) and `frontmatter_io.py` (round-trip read/write, atomic-write behaviour using a temp directory)

## 3. `garden new` subcommand

- [ ] 3.1 Implement `garden/commands/new.py` exposing a Typer command function `new(kind: str | None, title: str | None, slug: str | None, lang: str | None) -> None` and register it on `app` in `cli.py`
- [ ] 3.2 In `new`: if any required field is missing, in TTY mode prompt for it (kind via select, title/slug/lang via text), in non-TTY mode raise typer.BadParameter; validate every field via `validation.py` before any filesystem action
- [ ] 3.3 For `kind == "post"`: create directory `content/posts/<slug>/` if missing, write `<slug>.<lang>.md` with `Title`, `Slug`, `Date` (today, `YYYY-MM-DD`), `Lang`, `Translation_key` (=`slug`), `Status: draft`. Also create empty `content/posts/<slug>/assets/` directory.
- [ ] 3.4 For `kind == "page"`: write `content/pages/<slug>.<lang>.md` (no per-page directory; no `Date:`)
- [ ] 3.5 For `kind == "tag-prose"`: prompt for tag name and prose-file shape (e.g. `all`, `lang`); write `content/tag-prose/<tag>/<shape>.<lang>.md` with `Status: hidden`. If the tag directory does not exist, prompt to confirm creation in TTY mode; otherwise refuse without a `--create-tag` flag.
- [ ] 3.6 Refuse if the target file already exists; exit non-zero with a clear message
- [ ] 3.7 Add tests for `new`: happy path for each kind, every validation failure, missing-flags-in-TTY (mock prompts), missing-flags-in-non-TTY (assert failure), refuse-on-existing-file

## 4. `garden translate` subcommand

- [ ] 4.1 Implement `garden/commands/translate.py` with signature `translate(slug: str, to: str, slug_new: str | None, title_new: str | None) -> None` (Typer maps `--to`, `--slug`, `--title` to these); register on `app`
- [ ] 4.2 Resolve source via `content_index.find_by_slug`; raise BadParameter if not found
- [ ] 4.3 Refuse for `kind == "page"` and `kind == "tag-prose"` initially? — actually allow translate for all kinds; pages and tag-prose can also be translated. Confirm in tests.
- [ ] 4.4 Read source frontmatter + body; build new frontmatter dict with `Title=title_new`, `Slug=slug_new` (or original if not supplied), `Lang=to`, `Translation_key=source.translation_key`, `Status="draft"`, copy `Date:` if present; body is copied verbatim
- [ ] 4.5 Compute target path (post: same directory, new filename; page: same `pages/` dir, new filename; tag-prose: same tag dir, new filename) and refuse if it already exists
- [ ] 4.6 Validate `to`, `slug_new`, `title_new` via `validation.py`; in TTY mode prompt for missing `slug_new` and `title_new`; in non-TTY mode fail
- [ ] 4.7 Write atomically via `frontmatter_io.write_frontmatter`
- [ ] 4.8 Add tests: post translate, page translate, tag-prose translate, refuse-on-existing-target, refuse-on-missing-source, body-byte-identical-to-source

## 5. Lifecycle subcommands (publish / draft / archive)

- [ ] 5.1 Implement `garden/commands/lifecycle.py` with shared internals: `_resolve_targets(slug, all_translations) -> list[ContentFile]`, `_validate_transition(targets, from_states, force) -> list[Error]`, `_apply_transition(targets, to_state)`. Single source of truth for the three commands.
- [ ] 5.2 Implement Typer commands `publish(slug, all_translations: bool | None, force: bool)`, `draft(slug, all_translations: bool | None, force: bool)`, `archive(slug, all_translations: bool | None, force: bool)`; each delegates to the shared internals with the appropriate (from, to) state set
- [ ] 5.3 Allowed-from states: `publish` → from `{draft}`, `draft` → from `{published}`, `archive` → from `{published}`. Anything else triggers refusal unless `--force`.
- [ ] 5.4 If `all_translations` is `None` (flag omitted): in TTY mode prompt yes/no; in non-TTY mode fail with a clear "must be set explicitly" error
- [ ] 5.5 Two-pass plan-then-apply: pass 1 reads each target file's `Status:` and collects refusals; if any refusal AND no `--force`, exit non-zero with all offending files named, no mutations. Pass 2 applies the new `Status:` to every target file (atomic write per file).
- [ ] 5.6 Lifecycle subcommands operate only on posts. If the resolved file is under `content/pages/` or `content/tag-prose/`, exit non-zero with a clear message.
- [ ] 5.7 Refuse if no file matches the slug; exit non-zero with a clear message
- [ ] 5.8 Add tests: each command's happy path, each refusal path (publish-on-hidden, draft-on-hidden, archive-on-draft), `--force` bypass for each, `--all-translations` happy path, atomic refusal across translations, `--all-translations` prompt in TTY mode, `--all-translations` failure in non-TTY mode, refusal when slug resolves to page or tag-prose

## 6. `garden lint` subcommand

- [ ] 6.1 Implement `garden/commands/lint.py` exposing a Typer command `lint() -> None`; register on `app`
- [ ] 6.2 Inside `lint`, import `frontmatter_lint` and call its CLI entry function with `["content"]`; propagate the exit code via `raise typer.Exit(code)`
- [ ] 6.3 Add an integration test that invokes `garden lint` against a clean fixture tree (exit 0) and a fixture tree with a known lint failure (exit non-zero, error matches `frontmatter_lint`'s output verbatim)

## 7. Makefile + docs cleanup

- [ ] 7.1 Remove the `lint` target from `Makefile`; remove `lint` from `.PHONY`
- [ ] 7.2 Search for `make lint` references in `README.md`, `CLAUDE.md`, and any other `.md` outside `openspec/changes/archive/` — replace with `garden lint`
- [ ] 7.3 If a top-level `README.md` does not yet mention the CLI, add a short "Authoring content" section describing the six subcommands

## 8. End-to-end verification

- [ ] 8.1 Install the package fresh in the venv (`pip install -e .`) and confirm `garden --help` runs from PATH and lists every subcommand
- [ ] 8.2 Confirm `python -m garden --help` produces identical output
- [ ] 8.3 Run `garden new --kind post --title "Verify" --slug verify --lang en`; confirm file is created with correct frontmatter and `assets/` directory; run `garden lint` and confirm exit 0
- [ ] 8.4 Run `garden translate verify --to pt --slug verificar --title "Verificar"`; confirm paired file exists with correct frontmatter and identical body; run `garden lint` and confirm exit 0
- [ ] 8.5 Run `garden publish verify --no-all-translations`; confirm only the EN file is `published`. Run `garden publish verify --all-translations`; confirm both EN and PT are now `published`. Run `garden archive verify --all-translations`; confirm both flip to `hidden`. Run `garden draft verify --all-translations --force`; confirm both flip back to `draft`.
- [ ] 8.6 Negative test: run `garden new --kind post --title "X" --slug "Bad Slug" --lang en` and confirm exit non-zero with a slug-pattern error and no file written. Run `garden new --kind post --title "X" --slug ok --lang english` and confirm exit non-zero with a lang-pattern error.
- [ ] 8.7 Negative test: with the EN file `hidden`, run `garden publish verify --no-all-translations` and confirm refusal with `--force` suggestion. Then run with `--force` and confirm it now flips.
- [ ] 8.8 Run `garden new < /dev/null` (no flags, stdin redirected) and confirm exit non-zero with a missing-required-argument error (no hang).
- [ ] 8.9 Clean up the verification post: `rm -rf content/posts/verify/`. Confirm `garden lint` still passes.
- [ ] 8.10 Run `make build` and confirm the build still succeeds (sanity check that nothing in this change broke the existing pipeline).
