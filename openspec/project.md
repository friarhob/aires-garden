# aires-garden — Project Baseline

> **Status:** Frozen baseline (t=0). Do not edit retroactively. Deviations are recorded as ADRs under `openspec/decisions/`.
> **Captured:** 2026-04-20 during the `scaffold-pelican-site` change.

---

## Digital Garden — Project Brief

### Goal

Build a personal digital garden: a static, multilingual, tag-organized content site with drafts and published states, a gallery homepage, custom domain, customizable visual identity, and room to grow (including embedded iframes and potentially interactive content in the future).

### Tech stack

- **Site generator:** Pelican (Python). Chosen over Astro specifically for Python-native extensibility — plans include custom content processing, backlinks, related-posts via tag overlap, and potentially NLP-driven features later. These are all easier when the generator itself is Python.
- **Content format:** Markdown files with YAML frontmatter.
- **Templating:** Jinja2 (Pelican default) with a custom theme.
- **Authoring CLI:** Python, built with Typer. Wrapped by a Makefile for friendly commands.
- **Dev organization:** OpenSpec — each feature shipped as its own change proposal, reviewed, implemented, archived.
- **Hosting:** GitHub Pages, via GitHub Actions deploy workflow.
- **DNS / subdomain routing (future):** Cloudflare in front of GitHub Pages for DNS and optional subdomain-to-path rewrites (not part of the initial build).

### Content model

Every post is a Markdown file with frontmatter. Key fields:

- `title`
- `slug` (lowercase, URL-safe)
- `lang` — one of `en`, `pt`, `es`, `fr` (extensible)
- `translation_key` — shared across all language versions of the same post; used to link translations
- `tags` — list
- `status` — `draft` or `published`
- `date`

Translations are sibling files sharing a `translation_key`. A post can exist in any subset of the supported languages (including just one). The UI displays which languages are available for each post.

Tags aggregate into index pages. Drafts are visible in local dev but excluded from production builds.

### Repository layout

```
garden/
├── content/
│   ├── posts/
│   │   └── <slug>/
│   │       ├── <slug>.en.md
│   │       ├── <slug>.pt.md
│   │       └── images/
│   └── pages/
├── themes/garden/
│   ├── templates/
│   └── static/css/
│       ├── tokens.css        # design tokens = visual identity
│       └── styles.css
├── plugins/
│   ├── content_tags/         # custom tag preprocessor ({{ figure }}, etc.)
│   └── frontmatter_lint/     # schema validation
├── tools/garden/             # Python CLI (Typer)
├── openspec/                 # OpenSpec change proposals and specs
├── pelicanconf.py            # dev config (drafts visible)
├── publishconf.py            # prod config (drafts excluded)
├── Makefile
├── CNAME
└── .github/workflows/deploy.yml
```

### Styling

- Visual identity lives in `themes/garden/static/css/tokens.css` as CSS custom properties (colors, typography, spacing, radii).
- `styles.css` consumes the tokens. Swapping identity = editing one file.

### Custom content tags (MDX-equivalent for Pelican)

Since Pelican doesn't have MDX, we implement a custom tag syntax as a Python preprocessor to get reusable, componentized embeds (iframes, figures, callouts, videos, etc.) without writing raw HTML in every post.

- **Syntax:** `{{ tagname arg=value arg2=value2 }}` (or another syntax TBD during implementation)
- Each tag is a Python function registered in a small registry.
- Preferred integration: a Pelican reader hook / plugin that expands tags before Markdown parsing.
- **Starter set of tags:** `figure`, `youtube`, `callout`. Add more as real needs appear.
- Goal is reusable patterns only — don't overbuild; one-off HTML stays as raw HTML.

### Python CLI (`garden`)

Exposed through a Makefile. Minimum viable surface:

- `make new` — scaffold a new post (prompts for title, lang, tags; pre-fills frontmatter; generates slug and `translation_key`).
- `make translate slug=<slug> lang=<lang>` — create a translation stub sharing the same `translation_key`.
- `make lint` — validate frontmatter schema, check translation-key consistency, check tag usage. Fails build on errors.
- `make dev` — `pelican --autoreload --listen` with drafts visible.
- `make build` — production build (runs lint first, then Pelican with `publishconf.py`).
- `make publish` — wrapper that lints, runs any sanity checks, then `git push origin main`. Actual build+deploy happens in GitHub Actions.

Keep the CLI small. Add commands only when a real annoyance shows up — don't over-invest in authoring tooling upfront.

### Deploy (GitHub Pages + GitHub Actions)

- **Source:** GitHub Pages configured to serve from GitHub Actions (not a `gh-pages` branch).
- **Workflow** `.github/workflows/deploy.yml` runs on push to `main`:
  1. Check out repo
  2. Set up Python 3.12, install deps
  3. `make lint && make build`
  4. Upload `output/` as the Pages artifact (`actions/upload-pages-artifact@v3`)
  5. Deploy with `actions/deploy-pages@v4`
- **`CNAME`** file at repo root containing the custom domain. Pelican config must copy it into `output/` via `STATIC_PATHS`.
- **`SITEURL`** set correctly in `publishconf.py` (production URL) — critical for RSS, sitemap, and internal links.
- **URL structure:** `ARTICLE_URL = "{slug}/"` and `ARTICLE_SAVE_AS = "{slug}/index.html"` for clean URLs.
- Add a `404.md` that generates `output/404.html`.
- **DNS:** CNAME record pointing the subdomain to `<username>.github.io` (or A records for apex).

### Reader experience

- **Homepage:** gallery of most recent published posts — title, date, tags, cover image, language availability indicators.
- **Post page:** rendered Markdown + custom-tag output, styled by tokens. "Available in: EN, PT, FR" badges link to translations. Tag links at bottom.
- **Language switcher** in the header; languages without a translation for the current post are visibly disabled.
- **Tag pages:** posts filtered by tag.
- **RSS feed** per language.

### OpenSpec change proposals — implementation order

Each is its own proposal:

1. `scaffold-pelican-site` — repo structure, base config, minimal theme, hello-world post builds locally.
2. `add-deploy-pipeline` — GitHub Actions workflow, CNAME, SITEURL, URL structure, 404 page. Get deploy working early so every later change is immediately verifiable live.
3. `add-content-model` — frontmatter schema, `translation_key` convention, `frontmatter_lint` plugin.
4. `add-i18n-rendering` — language switcher, "available in" badges, per-language RSS.
5. `add-tags-and-drafts` — tag index pages, draft handling per environment.
6. `add-design-tokens` — `tokens.css`, base theme styles, gallery homepage.
7. `add-python-cli` — `garden new`, `translate`, `lint`, `publish` wired through Makefile.
8. `add-content-tags` — custom-tag preprocessor with starter tags (`figure`, `youtube`, `callout`).
9. `add-image-pipeline` — responsive images, optimization. Deferred until image weight is a real problem.

### Explicit deferrals / out-of-scope for initial build

- Cloudflare subdomain routing (`poetry.example.com` → `/tag/poetry/`). Pattern understood, documented, not implemented. Add later if/when wanted — internal-link discipline and possibly a Cloudflare Worker for HTML rewriting would be needed.
- Image optimization pipeline.
- Web-based admin UI. Authoring is Markdown-in-Git. Mobile editing, if wanted, via Working Copy (iOS) or GitJournal (Android) — no code needed.
- Interactive components / JS islands. Pelican is templates-only; revisit if a real need emerges.

### Key decisions and their rationale (for context)

- **Pelican over Astro:** chose Python-native extensibility (custom Markdown processing, backlinks, cross-content computation, future Python library integrations) over Astro's stronger out-of-the-box schema validation and MDX.
- **Custom tag preprocessor:** replicates most of MDX's reusable-embed benefit while staying in Python.
- **Deploy pipeline second, not last:** every subsequent change ships to a live site, catching URL/path issues early.
- **GitHub Pages over Cloudflare Pages:** staying on GitHub for now for tool coherence; Cloudflare deferred to when subdomain routing is actually needed.

### Known gaps to watch for

- Pelican has no built-in frontmatter schema validation — the `frontmatter_lint` plugin is the mitigation.
- GitHub Pages is case-sensitive; macOS local filesystem is not. Lint must enforce lowercase slugs.
- `SITEURL` misconfiguration silently breaks RSS/sitemap/internal links.
- First deploy with a new custom domain can be finicky for ~1 hour while cert provisions.
