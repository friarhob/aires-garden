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
| `add-python-cli` | pending | `garden` CLI: new, translate, publish, draft, archive, lint |

---

## Planned

Items are listed in intended implementation order. Dependencies are noted where they exist.

### 1. `default-light-mode`

Switch the site default from dark mode to light mode. The `add-user-preferences` change established dark as default; this reverses that decision. Will be accompanied by a new ADR superseding the prior choice.

- **Scope:** tiny — one CSS/token change + one ADR
- **Depends on:** nothing

---

### 2. `refactor-language-selector`

The current language selector in the header shows all supported languages but doesn't navigate to the equivalent page in the selected language. Refactor it to be translation-aware: selecting a language takes the reader to the translation of the current content if one exists, or falls back gracefully. Pages without an explicit language (404, "all" tag-prose shapes) retain the current behaviour.

- **Scope:** medium — theme template update + i18n_grouping plugin logic
- **Depends on:** nothing

---

### 3. `refactor-homepage`

The current homepage is a flat list of recent posts. This change introduces:

- A new `intro` content kind: Markdown files per language and shape, mirroring the `tag-prose` convention. Two shapes: `all.<lang>.md` (shown on the root `/` page, which aggregates all languages) and `lang.<lang>.md` (shown on per-language roots: `/en`, `/pt`, `/es`, `/fr`). Authored via `garden new --kind intro`.
- A redesigned post list below the intro. Open design questions to resolve during the proposal: table layout vs. card/list layout; pagination vs. infinite scroll vs. "load more".

**Content dependency:** Spanish and French intro files can be authored once this change lands.

- **Scope:** large — new content kind, CLI scaffold addition, theme template redesign, pagination
- **Depends on:** nothing (but `default-light-mode` should ship first to avoid re-touching theme twice)

---

## Deferred

Carried forward from `project.md`; still out of scope until a real need emerges.

- **`add-image-pipeline`** — responsive images, optimisation. Deferred until image weight is a real problem.
- **Cloudflare subdomain routing** — `poetry.example.com` → `/tag/poetry/`. Pattern understood, not implemented.
- **Interactive components / JS islands** — Pelican is templates-only; revisit if a concrete need appears.
- **Web-based admin UI** — authoring is Markdown-in-Git; mobile editing via Working Copy or GitJournal.
