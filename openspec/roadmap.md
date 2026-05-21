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
| `smarter-cli` | 2026-05-13 | Interactive slug picker for lifecycle/translate, Unicode slug normalisation, tag-prose picker, page/tag-prose frontmatter fixes |
| `refactor-homepage` | 2026-05-20 | Intro content kind, catalogue card layout, pagination, `garden new --kind intro` |

---

## Planned

Items are not listed in any particular order. Dependencies are noted where they exist.

### `add-l10n-rendering`

Localise all UI chrome strings so the site renders in the visitor's language rather than always in English. In scope: site title/branding, page titles, UI labels ("Also in:", "Tags:", "Posts", and any others in templates), date formats, and footer text. RSS feed labels are out of scope. All four languages (en, pt, es, fr) ship together; English is the fallback for any unimplemented language or string.

- **Scope:** medium — strings layer (format TBD at design time), theme template updates, date localisation
- **Note:** `refactor-homepage` may introduce additional strings that need localising; coordinate if both are in flight

---

### `add-optional-subtitle`

The current post format doesn't support posts to have subtitles/subheads/captions. This change introduces:

- A new field `Subtitle:` in the current post template.
- An updated CLI to contemplate that (including receiving it as param on `garden new`, or requesting in the iteration).
- An updated `frontmatter_lint` to handle the new optional field.
- An updated `styles.css` with formatting for the subtitle. Eventually this will lead to updates in `visual-identity.md`, and even `contrast_audit.py`.
- The templates should contemplate it being optional, and keep the formatting as is in case of empty subtitle.

- **Scope:** large — new element in posts, CLI scaffold addition, theme template redesign.
- **Depends on:** nothing

---

### `add-admin-ui`

A web-based admin UI for editing and publishing garden content from a browser, including mobile. Strong default lean toward adopting an existing static CMS rather than building from scratch — Git-backed, so the UI commits Markdown to the repo and the existing GitHub Actions deploy takes over. The CLI workflow continues to work in parallel. The "adopt vs build" call is not mandatory; the design phase confirms.

Candidate tools for the adopt path: **Decap CMS** (pure-static, GitHub OAuth) and **Sveltia CMS** (Decap-compatible config, modern Svelte stack). Hard constraint: must work on GitHub Pages (no backend hosting) — any auth flow that needs a server-side component must use either a free hosted bridge or a tiny serverless endpoint, to be confirmed at design time.

In scope:

- Full CRUD on posts across all configured site languages (language-agnostic per `ADR-0004`; adapts to whatever languages exist in `siteconfig`).
- Frontmatter compatibility with garden's content model (`translation_key`, `Lang`, `Tags`, `Status`, slug-per-language, directory layout).
- Authentication / identity management for the UI — only authorised users can edit and commit. Exact mechanism (GitHub OAuth, an allowlist, or another approach) to be decided at proposal time.
- Mobile-friendly editing UX.

Out of scope (initial slice):

- Image / media uploads — see `add-admin-ui-media`.
- Non-post content kinds (`tag-prose`, `intro`) — see `add-admin-ui-content-kinds`.
- Multi-author review/approval workflow.
- L10n of the admin UI chrome itself.
- Custom widgets beyond what the chosen tool offers.

- **Scope:** large — tool evaluation, integration, content-model wiring, auth flow, access control
- **Depends on:** nothing hard. Coordinate with `add-l10n-rendering` if both end up touching templates simultaneously.

---

### `add-admin-ui-media`

Extend the admin UI with image uploads so embedded media can be added from the browser without local git. Includes storage-location conventions (co-located with posts per ADR-0004's `images/` sibling pattern) and UI wiring for the figure shortcode with captions introduced by `add-content-tags`.

- **Scope:** medium
- **Depends on:** `add-admin-ui`

---

### `add-admin-ui-content-kinds`

Extend the admin UI to handle non-post content kinds: `tag-prose` (per-tag prose pages, from `add-tags-and-drafts`) and `intro` (homepage intro, from `refactor-homepage`). Each has its own frontmatter shape and lives in dedicated locations — the UI needs explicit collections per kind.

- **Scope:** medium
- **Depends on:** `add-admin-ui`

---


## Deferred

Carried forward from `project.md`; still out of scope until a real need emerges.

- **`add-image-pipeline`** — responsive images, optimisation. Deferred until image weight is a real problem.
- **Cloudflare subdomain routing** — `poetry.example.com` → `/tag/poetry/`. Pattern understood, not implemented.
- **Interactive components / JS islands** — Pelican is templates-only; revisit if a concrete need appears.
