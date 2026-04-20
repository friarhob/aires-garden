## 1. Python environment and dependencies

- [x] 1.1 Pick the latest stable Pelican 4.x release and the matching Markdown version; record versions.
- [x] 1.2 Create `pyproject.toml` declaring Python 3.12 and pinning `pelican` and `markdown`.
- [x] 1.3 Document virtualenv creation and `pip install -e .` flow in `README.md`.

## 2. Git and gitignore

- [x] 2.1 Write `.gitignore` covering Python (`__pycache__/`, `*.pyc`, `.venv/`, `venv/`), Pelican (`output/`, `cache/`), macOS (`.DS_Store`), editors (`.vscode/`, `.idea/`), and AI-assistant configs (`.claude/`, `.cursor/`, `.windsurf/`).
- [x] 2.2 Confirm `.claude/` (already on disk from `openspec init`) is ignored, not tracked.

## 3. Directory scaffolding

- [x] 3.1 Create `content/posts/` and `content/pages/` with `.gitkeep` placeholders where needed.
- [x] 3.2 Create `themes/garden/templates/` and `themes/garden/static/css/`.
- [x] 3.3 Create `plugins/` and `tools/garden/` as empty placeholders (`.gitkeep`).

## 4. Pelican configuration

- [x] 4.1 Write `pelicanconf.py` with the dev defaults required by the spec (`SITEURL`, `PATH`, `THEME`, `DEFAULT_LANG`, `ARTICLE_URL`, `ARTICLE_SAVE_AS`, drafts visible).
- [x] 4.2 Write `publishconf.py` importing `pelicanconf`, overriding `SITEURL`, excluding drafts, enabling feeds.

## 5. Minimal theme

- [x] 5.1 Write `themes/garden/templates/base.html` with an HTML skeleton and a link to `static/css/styles.css`.
- [x] 5.2 Write `themes/garden/templates/index.html` rendering the post list using `base.html`.
- [x] 5.3 Write `themes/garden/templates/article.html` rendering a single article using `base.html`.
- [x] 5.4 Add a stub `themes/garden/static/css/styles.css` (single baseline rule is fine — tokens land in `add-design-tokens`).

## 6. Hello-world content

- [x] 6.1 Create `content/posts/hello-world/hello-world.en.md` with frontmatter (`title`, `date`, `slug: hello-world`, `lang: en`, `status: published`) and a short body paragraph.

## 7. Makefile

- [x] 7.1 Write `Makefile` with a `dev` target running `pelican --autoreload --listen` against `pelicanconf.py`.
- [x] 7.2 Add a `build` target running `pelican` against `publishconf.py` writing to `output/`.
- [x] 7.3 Verify no `new`, `translate`, `lint`, or `publish` targets are present (reserved for `add-python-cli`).

## 8. Local verification

- [x] 8.1 Create a virtualenv, install dependencies, run `make dev`, confirm `http://localhost:8000` renders the index and hello-world post.
- [x] 8.2 Run `make build` and confirm `output/index.html` and `output/hello-world/index.html` exist with no errors.

## 9. README

- [x] 9.1 Write `README.md` with: project summary, prerequisites (Python 3.12), quickstart (`make dev` / `make build`), and a pointer to `openspec/` for the change-proposal workflow.

## 10. Project context and decision log

- [x] 10.1 Write `openspec/project.md` containing the project brief as the frozen `t=0` baseline. Preserve wording; trim only objectively wrong/dated phrasing. Mark the top clearly as "Baseline — do not edit retroactively; record deviations as ADRs in `openspec/decisions/`."
- [x] 10.2 Create `openspec/decisions/README.md` documenting the ADR convention: filename `NNNN-kebab-title.md`, sections Context / Decision / Consequences / Status; supersession rule (new ADR marks old one `Superseded by NNNN`); numbering is monotonic, never reused.
- [x] 10.3 Write `openspec/decisions/0001-project-context-baseline-plus-adrs.md` capturing today's decision to use `project.md` + `decisions/` (option B) over pure-ADR (option C). Include alternatives considered (A–F as discussed), rationale, and Status: `Accepted`.
- [x] 10.4 Write `openspec/decisions/0002-design-md-always-present-status-marked.md` codifying that every change ships a `design.md` with a mandatory `Status` line taking one of two forms (`Design decisions recorded below.` or `No change-scoped design decisions.` + reason pointing to where the reasoning lived). Rationale: treat `design.md` as a process checkpoint artifact, not a payload artifact — presence is evidence the design step was consciously performed, and the Status line prevents stubs from decaying into boilerplate. Status: `Accepted`.
- [x] 10.5 Extend `openspec/decisions/README.md` with a section summarizing the design.md convention so contributors encounter it before writing a new change.

## 11. GitHub remote and initial push

- [ ] 11.1 Create the GitHub repository (`gh repo create aires-garden --private --source . --remote origin`).
- [ ] 11.2 Stage the proposal bundle and all scaffold files; commit.
- [ ] 11.3 Push `main` to `origin` and confirm the remote exists (`git remote -v`).

## 12. OpenSpec validation and archive-readiness

- [ ] 12.1 Run `openspec validate scaffold-pelican-site` and confirm it passes.
- [ ] 12.2 Mark all tasks above complete and prepare the change for archival once implementation is reviewed.
