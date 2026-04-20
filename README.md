# aires-garden

Personal digital garden — Pelican-based multilingual static site.

## Prerequisites

- Python 3.12 (tested with 3.12.4)
- `make`

## Quickstart

Create a virtualenv and install the project in editable mode:

```bash
python3.12 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
```

Run the dev server with hot reload:

```bash
make dev
```

Open [http://localhost:8000](http://localhost:8000).

Build the production output (writes to `output/`):

```bash
make build
```

## Layout

- `content/` — Markdown posts and pages (`posts/`, `pages/`).
- `themes/garden/` — custom Jinja2 theme (templates + static assets).
- `pelicanconf.py` — dev Pelican configuration (drafts visible, no feeds, empty `SITEURL`).
- `publishconf.py` — prod Pelican configuration (absolute `SITEURL`, drafts excluded, feeds enabled).
- `Makefile` — `dev` and `build` targets.
- `pyproject.toml` — Python dependencies and project metadata.
- `plugins/`, `tools/garden/` — empty placeholders populated by later OpenSpec proposals.
- `openspec/` — change proposals, specs, project baseline, and decision records.
  - `project.md` — frozen project baseline (original brief).
  - `decisions/` — append-only Architecture Decision Records.
  - `changes/` — active and archived change proposals.

## Dependencies

Declared with a range in `pyproject.toml`; pip resolves the actual version at install time.

| Package | Range | Currently resolved |
| --- | --- | --- |
| `pelican` | `>=4.10,<5` | `4.11.0.post0` |
| `markdown` | `>=3.5` | `3.10.2` |

## Workflow

Development is organized through [OpenSpec](https://github.com/Fission-AI/OpenSpec). Each feature ships as a change proposal under `openspec/changes/<name>/` with four artifacts (`proposal.md`, `design.md`, `specs/`, `tasks.md`). See `openspec/project.md` for the plan and `openspec/decisions/` for project-level decisions (including the `design.md`-always-present convention — ADR-0002).

The authoring CLI, custom content tags, image pipeline, i18n rendering, design tokens, and deploy pipeline are all deferred to later proposals (see `openspec/project.md`'s "OpenSpec change proposals — implementation order").
