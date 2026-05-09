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

## Authoring content

The `garden` CLI handles all content workflows. Run `garden --help` for a full list.

```bash
garden new --kind post --title "My Post" --slug my-post --lang en   # scaffold a draft post
garden translate my-post --to pt --slug meu-post --title "Meu Post" # add a translation
garden publish my-post --all-translations                            # draft → published
garden draft my-post --no-all-translations                          # published → draft
garden archive my-post --all-translations                           # published → hidden
garden lint                                                         # validate frontmatter
```

Any argument can be omitted and the CLI will prompt interactively.

## Content syntax

Posts and pages are written in Markdown with several extensions active. See the full spec at [`openspec/specs/content-tags/spec.md`](openspec/specs/content-tags/spec.md).

### Standard Markdown extensions

The site uses [Python-Markdown Extra](https://python-markdown.github.io/extensions/extra/) plus a few additional extensions. Non-obvious syntax:

**Tables** (GFM-style):

```markdown
| Column A | Column B | Column C |
| -------- | -------- | -------- |
| Row 1    | value    | value    |
| Row 2    | value    | value    |
```

**Footnotes**:

```markdown
Here is a claim.[^1]

[^1]: And here is the footnote text.
```

**Definition lists**:

```markdown
Term
:   Definition of the term.
```

### Admonitions

Four severity levels are available:

- **Note** (blue) — neutral supplementary information.
- **Tip** (green) — a helpful suggestion or shortcut.
- **Warning** (amber) — something the reader should take care about.
- **Danger** (red) — a breaking or destructive action.

Syntax — the body must be indented by four spaces:

```markdown
!!! note "Optional title"
    Body text goes here. It may span
    multiple lines.

!!! tip
    A tip without a custom title.

!!! warning "Watch out"
    Amber-coloured caution.

!!! danger "Irreversible"
    Red-coloured danger block.
```

### Captioned figures

Add a `title` attribute to any image and the plugin promotes it to a `<figure>` with a `<figcaption>`:

```markdown
![Alt text](assets/photo.jpg){title="Caption text"}
```

### Embed tags

YouTube videos and arbitrary iframes can be embedded inline:

```markdown
[!youtube](dQw4w9WgXcQ)
[!iframe](https://example.com/widget){width=800 height=600}
```

### Colocated assets

Each post lives in its own directory alongside an `assets/` folder:

```
content/posts/my-post/
    my-post.en.md
    my-post.pt.md
    assets/
        photo.jpg
        diagram.png
```

Reference assets with a relative path from the file (`assets/photo.jpg`).

## Layout

- `content/` — Markdown posts and pages (`posts/`, `pages/`).
- `themes/garden/` — custom Jinja2 theme (templates + static assets).
- `pelicanconf.py` — dev Pelican configuration (drafts visible, no feeds, empty `SITEURL`).
- `publishconf.py` — prod Pelican configuration (absolute `SITEURL`, drafts excluded, feeds enabled).
- `Makefile` — `dev` and `build` targets.
- `pyproject.toml` — Python dependencies and project metadata.
- `garden/` — `garden` CLI for content authoring and lifecycle.
- `plugins/` — Pelican plugins (frontmatter lint, content tags, i18n grouping, etc.).
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

Development is organised through [OpenSpec](https://github.com/Fission-AI/OpenSpec). Each feature ships as a change proposal under `openspec/changes/<name>/` with four artifacts (`proposal.md`, `design.md`, `specs/`, `tasks.md`). See `openspec/project.md` for the plan and `openspec/decisions/` for project-level decisions (including the `design.md`-always-present convention — ADR-0002).

The authoring CLI, custom content tags, image pipeline, i18n rendering, design tokens, and deploy pipeline are all deferred to later proposals (see `openspec/project.md`'s "OpenSpec change proposals — implementation order").
