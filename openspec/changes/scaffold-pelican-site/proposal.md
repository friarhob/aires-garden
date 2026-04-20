## Why

We need a working Pelican build before any other feature can be shipped. Every later change (deploy pipeline, content model, i18n, tags, theme, CLI, custom tags) assumes the site already generates locally from Markdown. This proposal establishes the minimum skeleton so subsequent proposals can be verified end-to-end against real output.

This is deliberately thin: just enough repo structure, configuration, theme, and a single "hello-world" post that `pelican` turns into HTML on a local machine. Everything else is explicitly deferred to its own proposal.

## What Changes

- **Create the GitHub repository** (e.g. `gh repo create aires-garden --private --source . --remote origin`) and push the initial commit. Starts private; flipped to public later once there's content worth showing. This gives us version-control backup from day one without committing to any hosting/CI decisions (those land in `add-deploy-pipeline`).
- Add project dependency management: `pyproject.toml` pinning `pelican` (target latest stable 4.x) and `markdown`, plus a virtualenv convention documented in `README.md`. (Chose `pyproject.toml` over `requirements.txt` because the Typer CLI proposal will need package metadata anyway — one file to maintain, not two.)
- Create the canonical directory layout from the brief: `content/posts/`, `content/pages/`, `themes/garden/{templates,static/css}/`, `plugins/`, `tools/garden/` (empty placeholder), `openspec/` (already present).
- Add `pelicanconf.py` with dev defaults: `SITEURL = ""`, `PATH = "content"`, `THEME = "themes/garden"`, `DEFAULT_LANG = "en"`, `ARTICLE_URL = "{slug}/"`, `ARTICLE_SAVE_AS = "{slug}/index.html"`, drafts visible.
- Add `publishconf.py` that imports `pelicanconf` and overrides for production: real `SITEURL` placeholder, drafts excluded, feeds enabled. (Actual prod URL wiring is completed in `add-deploy-pipeline`.)
- Add a minimal theme at `themes/garden/`: `base.html`, `article.html`, `index.html` Jinja2 templates with no styling beyond a plain HTML skeleton. A stub `static/css/styles.css` is linked but design tokens are out of scope here.
- Add `Makefile` with `dev` (`pelican --autoreload --listen`) and `build` (pelican with `publishconf.py`) targets only. `new`, `translate`, `lint`, `publish` targets are deferred to `add-python-cli`.
- Add `content/posts/hello-world/hello-world.en.md` — a trivial Markdown post with frontmatter (title, date, slug, lang, status: published) that proves the pipeline end-to-end.
- Add `.gitignore` covering: Python artifacts (`__pycache__/`, `*.pyc`, `.venv/`, `venv/`), Pelican build output (`output/`, `cache/`), macOS (`.DS_Store`), common editor dirs (`.vscode/`, `.idea/`), and AI-assistant config (`.claude/`, `.cursor/`, `.windsurf/`, etc. — so any contributor can regenerate their own tool's setup via `openspec init --tools <theirs>` without conflict).
- Add a top-level `README.md` with: prerequisites (Python 3.12, virtualenv), quickstart (`make dev`), and a pointer to `openspec/` for the change-proposal workflow.
- **Persist project context and decision log.** Commit `openspec/project.md` containing the project brief as the frozen baseline (what we thought at `t=0`: stack choice, proposal order, deferrals, known gaps). Create `openspec/decisions/` with a `README.md` describing the ADR (Architecture Decision Record) convention: one file per decision, `NNNN-kebab-title.md`, sections Context / Decision / Consequences / Status, supersede by adding a new ADR and marking the old one `Superseded by NNNN`. Seed with `0001-project-context-baseline-plus-adrs.md` capturing today's decision to use "baseline brief + ADR deltas" over pure-ADR (alternatives considered, rationale). Rationale: OpenSpec's artifacts are per-change; project-level decisions have nowhere to live otherwise.
- **Adopt `design.md`-always-present convention.** Every change directory SHALL contain a `design.md` starting with a `Status` line taking one of two forms: `Design decisions recorded below.` (followed by normal design sections) or `No change-scoped design decisions.` + one sentence naming where the reasoning lived (brief, specific ADR, upstream convention). Treats `design.md` as a process-checkpoint artifact — presence is evidence the design step was consciously performed, and the Status line keeps stubs informational rather than boilerplate. Codified as ADR-0002 and applied to this proposal's own `design.md` (which takes the "no decisions" form, pointing at `openspec/project.md` and ADR-0001/ADR-0002).

**Explicitly out of scope (each deferred to its own proposal):**
- GitHub Actions deploy, CNAME, production `SITEURL`, 404 page → `add-deploy-pipeline`
- Frontmatter schema, translation_key, `frontmatter_lint` → `add-content-model`
- Language switcher, per-language RSS → `add-i18n-rendering`
- Tag index pages, draft environment split → `add-tags-and-drafts`
- Design tokens, gallery homepage, real styling → `add-design-tokens`
- Typer CLI, `make new`/`translate`/`lint`/`publish` → `add-python-cli`
- Custom `{{ tagname }}` preprocessor → `add-content-tags`
- Responsive image pipeline → `add-image-pipeline`

## Capabilities

### New Capabilities
- `site-build`: The site generator turns Markdown in `content/` into static HTML in `output/` using a custom Jinja2 theme, with clean per-slug URLs, configurable via separate dev and prod config modules, and runnable via `make dev` / `make build`.

### Modified Capabilities
(none — this is the first change)

## Impact

- **New code**: `pelicanconf.py`, `publishconf.py`, `Makefile`, `themes/garden/` (templates + stub CSS), `pyproject.toml`, `.gitignore`, `README.md`, one hello-world post.
- **Dependencies**: Pin Pelican (4.x) and Markdown. No Cloudflare, GitHub Actions, or Python CLI dependencies yet.
- **External side effects (one-time)**: Creating the GitHub repo and pushing `main`. No CI, Pages, DNS, or CNAME configuration yet.
- **Local tooling**: Developer needs Python 3.12 + a virtualenv. `make dev` must serve at `http://localhost:8000` with hot reload.
- **Nothing deployed yet**: the deploy-pipeline proposal is the immediate next step so every later proposal can be verified live.
- **Contracts established for later proposals**: URL structure (`{slug}/`), theme directory location, config-split pattern (pelicanconf vs publishconf), content path conventions, `.gitignore` policy of treating per-tool AI configs as local-only, the project-context convention (`openspec/project.md` as frozen baseline, `openspec/decisions/` as append-only ADR log), and the `design.md`-always-present-with-Status convention (ADR-0002). Later proposals extend rather than rewrite these.
