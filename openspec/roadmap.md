# aires-garden — Roadmap

> **Status:** Living document. Updated as work is planned, started, and completed.
> See `project.md` for the original frozen project brief.

---

## Shipped

| Change | Archived | Notes |
| --- | --- | --- |
| `scaffold-pelican-site` | 2026-04-20 | Repo structure, base config, minimal theme |
| `add-deploy-pipeline` | 2026-04-23 | GitHub Actions, CNAME, SITEURL, 404 |
| `add-content-model` | 2026-04-30 | Frontmatter schema, translation_key, frontmatter_lint |
| `add-i18n-rendering` | 2026-05-05 | Language switcher, per-language RSS |
| `add-design-tokens` | 2026-05-07 | tokens.css, base theme, gallery homepage |
| `add-page-lang-links` | 2026-05-07 | Language links on pages |
| `add-tags-and-drafts` | 2026-05-07 | Tag index pages, draft handling |
| `add-user-preferences` | 2026-05-07 | Dark/light mode toggle, persisted preference |
| `add-content-tags` | 2026-05-08 | Markdown extensions: admonitions, figures, embeds |
| `add-python-cli` | 2026-05-09 | `garden` CLI: new, translate, publish, draft, archive, lint |
| `fix-tag-lang-links` | 2026-05-10 | Fix tag-page language links broken by header refactor |
| `refactor-language-selector` | 2026-05-10 | Translation-aware language picker; falls back gracefully on unmatched pages |
| `default-light-mode` | 2026-05-10 | Light mode as default; dark honoured via `prefers-color-scheme`; ADR supersedes prior choice |
| `refactor-colour-scheme` | 2026-05-11 | Warm palette, WCAG AA audit across all token pairs, admonition semantic tokens, `docs/visual-identity.md` |
| `fix-typographic-punctuation` | 2026-05-11 | `smarty` extension for en/em dashes and curly quotes; updated all posts to use `--` |

---

## Planned

Items are listed in intended implementation order. Dependencies are noted where they exist.

### `add-l10n-rendering`

Localise all UI chrome strings so the site renders in the visitor's language rather than always in English. In scope: site title/branding, page titles, UI labels ("Also in:", "Tags:", "Posts", and any others in templates), date formats, and footer text. RSS feed labels are out of scope. All four languages (en, pt, es, fr) ship together; English is the fallback for any unimplemented language or string.

- **Scope:** medium — strings layer (format TBD at design time), theme template updates, date localisation
- **Note:** `refactor-homepage` may introduce additional strings that need localising; coordinate if both are in flight

---

### `refactor-homepage`

The current homepage is a flat list of recent posts. This change introduces:

- A new `intro` content kind: Markdown files per language and shape, mirroring the `tag-prose` convention. Two shapes: `all.<lang>.md` (shown on the root `/` page, which aggregates all languages) and `lang.<lang>.md` (shown on per-language roots: `/en`, `/pt`, `/es`, `/fr`). Authored via `garden new --kind intro`.
- A redesigned post list below the intro. Open design questions to resolve during the proposal: table layout vs. card/list layout; pagination vs. infinite scroll vs. "load more".

**Content dependency:** Spanish and French intro files can be authored once this change lands.

- **Scope:** large — new content kind, CLI scaffold addition, theme template redesign, pagination
- **Depends on:** nothing (but `default-light-mode` should ship first to avoid re-touching theme twice)

---

### `smarter-cli`

The current CLI requires a slug argument for every command that acts on existing content. This has two problems: the user must remember the exact slug, and omitting the slug currently fails immediately even in TTY mode (despite the spec requiring an interactive prompt).

This change improves the CLI interaction model:

- When a slug is omitted in TTY mode, show an interactive searchable list of all posts to select from, rather than erroring. Commands affected: lifecycle commands (`publish`, `draft`, `archive`) and `translate` — exact scope to confirm during design.
- Handle the case where the post list grows large: how to present and filter it is a design question to resolve during implementation.
- Shell tab completion (Typer has built-in support for this) is an alternative worth exploring during design: `garden publish <Tab>` could autocomplete slugs without changing the prompt flow at all.

- **Scope:** medium — interactive picker UX across multiple commands; design discovery on list size and exact command scope
- **Depends on:** `add-python-cli` (shipped)

---

### `add-optional-subtitle`

The current post format doesn't support posts to have subtitles/subheads/captions. This change introduces:

- A new field `Subtitle:` in the current post template.
- An updated CLI to contemplate that (including receiving it as param on `garden new`, or requesting in the iteration).
- An updated `styles.css` with formatting for the subtitle. Eventually this will lead to updates in `visual-identity.md`, and even `contrast_audit.py`.
- The templates should contemplate it being optional, and keep the formatting as is in case of empty subtitle.

- **Scope:** large — new element in posts, CLI scaffold addition, theme template redesign.
- **Depends on:** nothing

---


## Deferred

Carried forward from `project.md`; still out of scope until a real need emerges.

- **`add-image-pipeline`** — responsive images, optimisation. Deferred until image weight is a real problem.
- **Cloudflare subdomain routing** — `poetry.example.com` → `/tag/poetry/`. Pattern understood, not implemented.
- **Interactive components / JS islands** — Pelican is templates-only; revisit if a concrete need appears.
- **Web-based admin UI** — authoring is Markdown-in-Git; mobile editing via Working Copy or GitJournal.
