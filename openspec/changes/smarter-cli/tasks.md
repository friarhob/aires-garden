## 1. Slug normalisation

- [ ] 1.1 In `garden/commands/new.py`, update `_slugify()` to apply `unicodedata.normalize('NFD', text)` and strip combining-mark characters (category `'Mn'`) before the existing `re.sub` — add `import unicodedata` at the top
- [ ] 1.2 Add unit tests in `garden/tests/` covering accented inputs: `"Água no Balão"` → `agua-no-balao`, `"crème brûlée"` → `creme-brulee`, `"Año Nuevo"` → `ano-nuevo`; confirm plain ASCII titles are unchanged

## 2. `ContentFile` — add `title` field

- [ ] 2.1 Add `title: str` to the `ContentFile` dataclass in `garden/content_index.py`
- [ ] 2.2 In `walk_content`, read `fields.get("Title", "")` and pass it to each `ContentFile` constructor
- [ ] 2.3 Update every test fixture that constructs `ContentFile` directly to supply the `title` field (search `garden/tests/` for `ContentFile(`)

## 3. Slug picker infrastructure

- [ ] 3.1 Add `prompt_slug_picker(posts: list[ContentFile], message: str) -> str` to `garden/prompts.py` — builds choices as `f"{cf.slug} — {cf.title} ({cf.lang}, {cf.status})"` and uses `questionary.autocomplete`; returns the slug extracted from the chosen entry
- [ ] 3.2 Add unit tests for `prompt_slug_picker` (mock `questionary.autocomplete`): returns correct slug, handles Abort, raises on non-TTY

## 4. Lifecycle commands — optional slug with picker fallback

- [ ] 4.1 In `garden/commands/lifecycle.py`, change the `slug` argument in `publish`, `draft`, and `archive` from `str` to `Optional[str]` (Typer `Argument` with `default=None`)
- [ ] 4.2 In `_resolve_targets`, when `slug is None`: in TTY mode, build the content index, filter to posts only, call `prompt_slug_picker`; in non-TTY mode, exit non-zero with "slug is required in non-interactive mode"
- [ ] 4.3 Add tests: slug omitted + TTY → picker called and operation proceeds; slug omitted + non-TTY → exits non-zero with clear message; slug supplied → picker not called (unchanged path)

## 5. `translate` command — optional slug with picker fallback

- [ ] 5.1 In `garden/commands/translate.py`, change `slug` from `str` to `Optional[str]` (Typer `Argument` with `default=None`)
- [ ] 5.2 After `--to` validation, when `slug is None`: in TTY mode, build index and call `prompt_slug_picker` (all posts); in non-TTY mode, exit non-zero
- [ ] 5.3 Add tests: slug omitted + TTY → picker called; slug omitted + non-TTY → exits non-zero; slug supplied → unchanged path

## 6. `garden new` — frontmatter correctness fixes

- [ ] 6.1 In `_create_page`, remove `"Slug": slug` from the `fields` dict (the slug is still used to compute the filename; it must not appear in the frontmatter)
- [ ] 6.2 In `_create_tag_prose`, remove `"Slug": slug` from the `fields` dict; also remove `"Title": title` prompt from the tag-prose path (title is not asked for pages, should it be for tag-prose? — confirm: yes, keep Title prompt for tag-prose since the spec requires it)
- [ ] 6.3 Update tests for `garden new --kind page` to assert no `Slug:` field in the created file, and that `garden lint` exits 0 on the file
- [ ] 6.4 Update tests for `garden new --kind tag-prose` to assert no `Slug:`, no `Translation_key:`, and that `garden lint` exits 0 on the file

## 7. `garden new --kind tag-prose` — existing tag picker and skip slug

- [ ] 7.1 In `_create_tag_prose`, replace the free-text tag-name prompt with `questionary.autocomplete` over the list of existing directory names under `content/tag-prose/` plus a sentinel `"[new tag]"` option; when `"[new tag]"` is chosen, fall back to the existing free-text prompt
- [ ] 7.2 In the main `new()` function, skip the slug prompt entirely when `kind == "tag-prose"` (neither prompt nor `--slug` flag is meaningful for this kind in TTY mode; in non-TTY mode, `--slug` is accepted but silently ignored)
- [ ] 7.3 Add tests: existing tag appears in picker choices; `"[new tag]"` sentinel triggers free-text prompt; resulting file has no `Slug:` field; `garden lint` exits 0

## 8. Draft spec update

- [ ] 8.1 Create `openspec/changes/smarter-cli/specs/garden-cli/spec.md` starting from `openspec/specs/garden-cli/spec.md` and adding: (a) new Requirement for interactive slug picker; (b) updated `garden new --kind tag-prose` scenarios; (c) updated `garden new --kind page` scenario asserting no Slug in frontmatter; (d) slug normalisation requirement and scenarios

## 9. End-to-end verification

- [ ] 9.1 Install fresh (`pip install -e .`), then run `garden publish` with no arguments in TTY mode; confirm picker appears listing posts
- [ ] 9.2 Run `garden translate` with no slug in TTY mode; confirm picker appears
- [ ] 9.3 Run `garden new --kind page --title "Test Page" --slug test-page --lang en`; open the file and confirm no `Slug:` field; run `garden lint` and confirm exit 0
- [ ] 9.4 Run `garden new --kind tag-prose --lang en`; confirm picker shows existing tags (`published-works`, `tempos-fantasticos`); select one; confirm created file has no `Slug:` field and `garden lint` exits 0
- [ ] 9.5 Run `garden new --kind post --title "Água no Balão" --lang pt` (no `--slug`); confirm default slug offered is `agua-no-balao`
- [ ] 9.6 Clean up any test content created; confirm `garden lint` still exits 0
- [ ] 9.7 Run `make build` and confirm build succeeds
