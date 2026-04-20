# site-build Specification

## Purpose

Establish the minimum Pelican skeleton that turns Markdown in `content/` into static HTML via a custom Jinja2 theme, with dev/prod config split and `make dev` / `make build` entry points. Every later change (deploy, content model, i18n, tags, theme, CLI) extends this baseline rather than restructuring it.

## Requirements

### Requirement: Repository layout conforms to the project brief

The repository SHALL provide the canonical directory structure so later changes can extend without restructuring.

#### Scenario: Canonical directories and files exist
- **WHEN** a fresh clone of the repository is inspected
- **THEN** the following paths exist and are tracked: `content/posts/`, `content/pages/`, `themes/garden/templates/`, `themes/garden/static/css/`, `plugins/`, `tools/garden/`, `openspec/`, `pelicanconf.py`, `publishconf.py`, `Makefile`, `pyproject.toml`, `.gitignore`, `README.md`.

### Requirement: Pelican configuration is split into dev and prod modules

The project SHALL separate development from production settings so later changes can layer deploy-specific values without touching the dev path.

#### Scenario: Dev configuration disables SITEURL and exposes drafts
- **WHEN** `pelicanconf.py` is imported
- **THEN** `SITEURL == ""`, `PATH == "content"`, `THEME == "themes/garden"`, `DEFAULT_LANG == "en"`, `ARTICLE_URL == "{slug}/"`, `ARTICLE_SAVE_AS == "{slug}/index.html"`, and drafts are included in the rendered output.

#### Scenario: Production configuration inherits from dev and excludes drafts
- **WHEN** `publishconf.py` is imported
- **THEN** it imports `pelicanconf` first, overrides `SITEURL` with a production placeholder, excludes drafts, and enables feeds.

### Requirement: A minimal custom theme renders index and article pages

The theme at `themes/garden/` SHALL provide the smallest set of Jinja2 templates needed for Pelican to render posts and an index page.

#### Scenario: Required templates exist
- **WHEN** `themes/garden/templates/` is inspected
- **THEN** `base.html`, `index.html`, and `article.html` exist and `base.html` links to `themes/garden/static/css/styles.css`.

#### Scenario: Templates render without errors
- **WHEN** `make build` runs against the hello-world post
- **THEN** `output/index.html` and `output/hello-world/index.html` are produced with no Jinja2 or Pelican errors.

### Requirement: A hello-world post proves the pipeline end-to-end

Content SHALL include one published Markdown post that exercises the frontmatter fields the brief defines.

#### Scenario: Hello-world post exists and builds
- **WHEN** `content/posts/hello-world/hello-world.en.md` is rendered
- **THEN** its frontmatter includes `title`, `date`, `slug`, `lang: en`, and `status: published`, and it produces `output/hello-world/index.html`.

### Requirement: Makefile exposes dev and build targets only

The `Makefile` SHALL expose exactly the two targets needed at this stage so later changes own the CLI surface explicitly.

#### Scenario: `make dev` serves the site locally
- **WHEN** a developer runs `make dev`
- **THEN** Pelican starts with autoreload and listens on `http://localhost:8000`.

#### Scenario: `make build` produces production output
- **WHEN** a developer runs `make build`
- **THEN** Pelican runs against `publishconf.py` and writes static files to `output/`.

#### Scenario: Future CLI targets are absent
- **WHEN** the `Makefile` is inspected
- **THEN** it does NOT define `new`, `translate`, `lint`, or `publish` (these are owned by `add-python-cli`).

### Requirement: Dependencies are pinned via pyproject.toml

Python dependencies SHALL be declared in `pyproject.toml` so the later Typer CLI can reuse the same package metadata.

#### Scenario: Required packages are pinned
- **WHEN** `pyproject.toml` is inspected
- **THEN** it declares `pelican` (4.x) and `markdown` as dependencies and specifies Python 3.12.

### Requirement: Repository is backed by a remote git origin

The local repository SHALL be tracked in a GitHub remote from day one to provide backup and shared history before any CI or hosting work.

#### Scenario: Remote origin exists on GitHub
- **WHEN** `git remote -v` is inspected after scaffolding
- **THEN** `origin` points to a GitHub repository named `aires-garden` and the `main` branch has been pushed.

#### Scenario: Repository starts private
- **WHEN** the GitHub repository visibility is checked immediately after creation
- **THEN** it is private; visibility is flipped to public in a later change, not this one.

### Requirement: Project context and decision log live under openspec/

Project-level context and long-lived decisions SHALL live in `openspec/` alongside the change proposals, since OpenSpec's change artifacts are per-change and have no home for project-wide rationale.

#### Scenario: Frozen project baseline exists
- **WHEN** `openspec/project.md` is inspected
- **THEN** it contains the project brief (stack, content model, repo layout, proposal order, deferrals, known gaps) as the frozen `t=0` baseline and is never edited retroactively — future deviations are recorded as ADRs rather than by overwriting this file.

#### Scenario: Decisions directory describes the ADR convention
- **WHEN** `openspec/decisions/README.md` is inspected
- **THEN** it documents the ADR format (one file per decision, filename pattern `NNNN-kebab-title.md`, sections Context / Decision / Consequences / Status) and the supersession rule (a superseding ADR marks the prior one `Superseded by NNNN`).

#### Scenario: Seed ADR captures the baseline-plus-ADRs decision
- **WHEN** `openspec/decisions/0001-project-context-baseline-plus-adrs.md` is inspected
- **THEN** it records the decision to use `openspec/project.md` + `openspec/decisions/` (option B) over pure-ADR (option C) with the alternatives considered and the reasoning, and its Status is `Accepted`.

### Requirement: Every change ships a design.md with an explicit Status line

Every OpenSpec change directory SHALL contain a `design.md` file so the presence of the artifact is evidence the design step was consciously performed — never left ambiguous by silent omission.

#### Scenario: design.md is present in every change
- **WHEN** any change directory under `openspec/changes/` is inspected
- **THEN** it contains a `design.md` file (in addition to `proposal.md`, `specs/`, and `tasks.md`).

#### Scenario: design.md begins with a Status line
- **WHEN** any `design.md` is opened
- **THEN** its first heading section is titled `Status` and its body takes exactly one of these two forms:
  1. `Design decisions recorded below.` — followed by normal Context / Options / Decision / Consequences sections.
  2. `No change-scoped design decisions.` — followed by at least one sentence naming where the reasoning *did* live (e.g. the project brief, a specific ADR, an upstream convention).

#### Scenario: scaffold-pelican-site's own design.md uses the "no decisions" form
- **WHEN** `openspec/changes/scaffold-pelican-site/design.md` is inspected
- **THEN** its Status is `No change-scoped design decisions.` and its body points to `openspec/project.md` and the ADRs under `openspec/decisions/` as the homes of the relevant reasoning.

### Requirement: .gitignore excludes build, editor, and AI-tool artifacts

The `.gitignore` SHALL keep the repository tool-agnostic so contributors can use any AI assistant or editor without polluting history.

#### Scenario: Standard build and Python artifacts are ignored
- **WHEN** `.gitignore` is inspected
- **THEN** it ignores `output/`, `cache/`, `__pycache__/`, `*.pyc`, `.venv/`, and `venv/`.

#### Scenario: macOS and editor artifacts are ignored
- **WHEN** `.gitignore` is inspected
- **THEN** it ignores `.DS_Store`, `.vscode/`, and `.idea/`.

#### Scenario: AI-assistant configuration is ignored
- **WHEN** `.gitignore` is inspected
- **THEN** it ignores at least `.claude/`, `.cursor/`, and `.windsurf/`, so each contributor regenerates their own tool's setup locally (e.g. via `openspec init --tools <theirs>`).
