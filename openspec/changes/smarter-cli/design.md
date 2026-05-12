## Context

The `garden` CLI requires an exact slug for every command that operates on existing content (`publish`, `draft`, `archive`, `translate`). The spec for `add-python-cli` said: "Missing required arguments prompt interactively in TTY mode" — but the slug is declared as a positional `typer.Argument(str)` (not `Optional`), so Typer fails before the command body even runs if the slug is omitted. The TTY-prompt path for slugs was never wired up.

A frontmatter review during proposal also revealed that `garden new --kind page` and `garden new --kind tag-prose` scaffold files that fail `garden lint` immediately:
- `PageFrontmatter` has `extra="forbid"` and no `Slug` field, but `_create_page` writes `Slug:` to the file.
- `TagProseFrontmatter` explicitly lists `Slug`, `Translation_key`, and `Tags` as forbidden fields, but `_create_tag_prose` writes `Slug:` to the file.

Both are regressions from the spec (ADR-0004 and the content-model spec both document the correct schemas).

Additionally, `_slugify()` uses a simple `re.sub(r"[^a-z0-9]+", "-", ...)` which silently drops accented characters (`á` → deleted, not `a`), producing broken slugs for Portuguese, French, and Spanish titles.

## Goals / Non-Goals

**Goals:**

- When any of `publish`, `draft`, `archive`, or `translate` is run without a slug in TTY mode, present an interactive autocomplete picker of all posts so the author can find the slug without remembering it.
- Fix slug generation to transliterate accented characters before stripping non-ASCII (Unicode normalisation).
- Fix `garden new --kind page` to write lint-passing frontmatter (no `Slug:` field).
- Fix `garden new --kind tag-prose` to write lint-passing frontmatter (only `Title`, `Lang`, `Status: hidden`) and to select the tag from existing directories rather than asking for a free-text name.
- Extend `ContentFile` with a `title` field so the picker can show meaningful labels.

**Non-Goals:**

- Shell tab completion — deferred. `typer.Argument` autocomplete has known reliability issues (#334, #353 upstream); startup overhead on each Tab press is non-trivial. The interactive picker solves the same problem without those caveats. Tab completion can be added in a later change.
- Changing the lifecycle command scope — only posts are supported (unchanged). The picker only lists posts.
- Bulk operations or multi-slug pickers — one slug at a time.
- Changing the `translate` command's _output_ side (slug/title for the new file) — only the _source_ slug argument gets the picker treatment.

## Decisions

### Decision 1: `questionary.autocomplete` for the slug picker

`questionary` is already a runtime dependency. Its `autocomplete` widget accepts a list of completion choices and lets the user type to filter (fuzzy prefix match). This handles large post lists gracefully without pagination logic or a separate dependency.

The picker display format: `"slug — Title (lang, status)"`. The slug is captured from the selection so subsequent logic is unchanged.

For the tag picker in `garden new --kind tag-prose`, the same widget lists the existing tag directory names, plus an `[new tag]` sentinel option that drops back to the existing free-text prompt.

**Alternatives considered:**

- **`questionary.select`** (arrow-key only, no typing): works for ≤10 items; becomes unwieldy for large post lists. Autocomplete is strictly better here.
- **Shell tab completion (Typer built-in)**: investigated during proposal. `typer.Argument` autocomplete is less reliable than `typer.Option` (upstream issues #334, #353). Each Tab press spawns a fresh Python process, adding ~200–300ms. User also needs a one-time shell setup step. Deferred — the interactive picker delivers more value with fewer caveats.

### Decision 2: Slug normalisation via `unicodedata`

`unicodedata.normalize('NFD', text)` decomposes characters into base + combining diacritics. Filtering out `unicodedata.category(c) == 'Mn'` (Mark, Non-spacing) then leaves only the base ASCII letters. This is the standard Python approach and requires no new dependency. Applied before the existing `re.sub` in `_slugify()`.

**Alternatives considered:**

- **`unidecode`**: a third-party library with a large transliteration table. More thorough for edge cases (e.g. CJK) but overkill for the four languages in this garden (pt, en, es, fr — all Latin-script). Adds a dependency. Rejected.
- **Manual replacement table**: brittle. Rejected.

### Decision 3: Tag-prose slug argument is dropped from the `new` flow

The slug argument in `garden new` currently serves two purposes: the filename slug (for posts/pages) and the frontmatter `Slug:` value. For tag-prose, neither is applicable — the filename is `<scope>.<lang>.md` and `Slug:` is forbidden. Rather than passing a dummy slug through the flow, the tag-prose path in `new.py` is restructured to skip the slug prompt entirely. In non-TTY mode `--slug` is silently ignored if `--kind tag-prose` is also given.

### Decision 4: `ContentFile.title` added to the content index

The picker needs to show a human-readable label beside each slug. `walk_content` already reads every file's frontmatter; adding `title: str` to `ContentFile` is a one-line change. Callers that construct `ContentFile` directly (primarily tests) need to supply the new field, but this is straightforward.

### Decision 5: Interactive picker for `translate` lists all posts (not filtered by language)

When translating, the author picks a source post. Filtering by "posts that don't yet have a translation in language X" would require knowing the target language before the picker appears — but `--to` may itself be supplied interactively. The simpler approach (list all posts) is correct: the command already refuses if the target file already exists.

## Risks / Trade-offs

- **`ContentFile` is a dataclass with a new required field** — any caller that uses positional construction breaks. Tests are the main risk; they're easy to fix but easy to miss. The implementation task explicitly calls this out.
- **Unicode normalisation edge cases** — NFD + Mn-strip covers all Latin-script accents (pt/es/fr). Other scripts (CJK, Arabic, etc.) would produce unexpected results, but this garden's slug space is Latin-only. Acceptable risk; documented in the spec.
- **Tag-prose picker shows only existing tags** — a brand-new tag still requires `--create-tag` or a confirmation prompt. This is the existing behaviour; no regression.
- **Picker on a very large content tree** — `questionary.autocomplete` loads all choices upfront. At hundreds of posts this is fine; at thousands it would need rethinking. Not a concern for this garden's expected scale.
