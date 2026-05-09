## Why

Authoring content in this garden today means hand-rolling frontmatter, mirroring it across language pairs, and editing `Status:` lines by hand to publish/archive. The frontmatter schemas (post, page, tag-prose) live in the `content-model` spec but are easy to mis-type, and a bilingual post requires four manual edits to keep `Translation_key`, `Slug`, `Lang`, and `Date` in sync. A small Python CLI replaces those rote chores with `garden new`, `garden translate`, `garden publish`, `garden draft`, `garden archive`, and `garden lint` — keeping schemas executable rather than documented prose.

This change is also the long-deferred replacement for the consolidated authoring guide that was scoped out of `add-tags-and-drafts`: a CLI scaffold beats a README because it stays current with the code and refuses to produce invalid frontmatter.

## What Changes

- Add a `garden` Python CLI under `garden/` (top-level package) using **Typer** for argument parsing.
- CLI is invokable both as `garden …` (entry point declared in `pyproject.toml`) and as `python -m garden …` (module fallback).
- Subcommand `garden new --kind <post|page|tag-prose>`: scaffolds frontmatter for the chosen content type. Interactive prompts walk through any missing required fields (kind, title, slug, lang); flags override prompts. Validates that fields are well-formed: `kind ∈ {post, page, tag-prose}`, `slug` is lowercase kebab-case (`[a-z0-9]+(-[a-z0-9]+)*`), `lang` matches ISO 639-1 (`^[a-z]{2}$`, per ADR-0004), `title` is non-empty. Creates the colocated `assets/` directory.
- Subcommand `garden translate <slug> --to <lang>`: locates the source file by per-language slug, copies it to a sibling with the new `Lang`, swaps the `Slug:` line if the user supplies a translated slug, prompts for the translated title. Interactive prompts walk through any missing required fields; flags override prompts.
- The lifecycle subcommands `garden publish <slug>`, `garden draft <slug>`, and `garden archive <slug>` flip the file's `Status:` field. Slugs are matched per-language (one slug → one file). All three accept a `--all-translations` / `--no-all-translations` flag; if omitted, the CLI prompts interactively (yes/no). When `--all-translations` is in effect, every file sharing the target's `Translation_key` is included. The set is **atomic**: if any included file is in a refusal state for the requested transition, the whole operation fails before any file is modified, and the error names the offending file(s) and suggests `--force` to bypass the check.
- Subcommand `garden publish <slug>`: flips `draft` → `published`. Refuses if the file is currently `hidden` (use `--force` to bypass). Interactive prompts walk through any missing required fields; flags override prompts.
- Subcommand `garden draft <slug>`: flips `published` → `draft`. Symmetric counterpart to `publish`. Refuses if the file is currently `hidden` (use `--force` to bypass — `hidden` is an intentional state, not a workflow step). Interactive prompts walk through any missing required fields; flags override prompts.
- Subcommand `garden archive <slug>`: flips `published` → `hidden`. Refuses if the file is currently a `draft` (drafts are unfinished, hidden is intentionally-not-indexed; use `--force` to bypass). Interactive prompts walk through any missing required fields; flags override prompts.
- Subcommand `garden lint`: runs the existing `frontmatter_lint` against `content/`. Replaces `make lint`.
- The Makefile keeps `make build` and `make dev`. The `make lint` target is removed (the CLI replaces it). `make` is no longer the entry point for *content* workflows, only for *site* workflows.
- Add `typer` and `questionary` (for richer interactive select prompts) to `pyproject.toml` dependencies.
- Existing CI / GitHub Actions: no change (CI runs `make build`, which is unchanged).

## Capabilities

### New Capabilities

- `garden-cli`: command-line tool for content authoring and lifecycle (new/translate/publish/draft/archive/lint). Owns the contract for CLI invocation, subcommand grammar, interactive prompt behaviour, and file mutations applied to `content/`.

### Modified Capabilities

_None._ The `content-model` schemas are referenced by the CLI but unchanged; the contract for what valid frontmatter looks like already lives there. The new `garden-cli` capability spec references content-model rather than modifying it.

## Impact

- **New top-level package**: `garden/` with subcommand modules. No changes to existing `plugins/`.
- **Dependencies**: `typer` and `questionary` added to `pyproject.toml`. Both are small, pure-Python.
- **Makefile**: `lint` target removed; `dev` and `build` unchanged. README/docs (if any) referencing `make lint` get updated.
- **Content tree**: untouched by this change itself. CLI commands mutate `content/` *at user request* but the change ships no content edits.
- **Lint pipeline**: `garden lint` calls into the existing `frontmatter_lint` module — no logic duplication, no change to lint rules.
- **Tests**: new `garden/tests/` covering each subcommand against a temp `content/` tree.
