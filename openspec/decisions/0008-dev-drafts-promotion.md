# ADR-0008: Dev-drafts promotion via a settings-flag toggle

## Status

Accepted — 2026-05-07.

## Context

The project uses a `Status` enum (`draft`, `published`, `hidden`) defined by ADR-0006. Pelican's default behaviour places draft articles in a separate `drafts/` output path and excludes them from all index and feed pages. This is correct for production but obstructs local development: an author writing a new post cannot see it in context alongside published articles, cannot check that translation grouping works, and cannot verify that tag pages include the draft before it goes live.

Three broad approaches were considered:

1. **Settings-flag toggle** (`DRAFTS_AS_PUBLISHED`). Set `True` in `pelicanconf.py` (the dev config) and `False` in `publishconf.py` (the production config). A small plugin (`dev_drafts`) reads the flag at `article_generator_pretaxonomy` and, when the flag is truthy, moves articles from `generator.drafts` into `generator.articles` and marks each one `status = "published"`. Downstream plugins (including `i18n_grouping`) then see the promoted articles as normal published articles.

2. **Environment-variable approach**. The plugin reads an env var (e.g. `PELICAN_DRAFTS=1`) instead of a Pelican setting. This decouples the behaviour from the config file, which could be useful in CI, but makes the toggle invisible to readers of `pelicanconf.py` and harder to discover.

3. **Two-plugin variant**. One plugin for dev promotion, one for production suppression. Logically equivalent to option 1 but doubles the registration surface and puts a hard coupling across two plugin files with no added value.

4. **Template-level draft handling**. Templates check `article.status == "draft"` and render a notice. This leaves drafts in `drafts/` output paths, so they don't appear on index, tag, or language-index pages — only the stub URL works.

## Decision

Use a settings-flag toggle: `DRAFTS_AS_PUBLISHED = True` in `pelicanconf.py`, `DRAFTS_AS_PUBLISHED = False` in `publishconf.py`. The `dev_drafts` plugin hooks `article_generator_pretaxonomy` to promote drafts before any downstream plugin processes the article list. Signal ordering is enforced by listing `dev_drafts` before `i18n_grouping` in `PLUGINS` (the list is processed top-to-bottom).

## Consequences

**Positive:**

- Dev and prod behaviour differ by one flag, not by plugin presence. Reviewers can audit the difference by diffing `pelicanconf.py` with `publishconf.py`.
- Promoted drafts are fully visible to `i18n_grouping`, `tag_pages`, and any future plugin — they behave exactly like published articles in dev.
- The `dev_drafts` plugin is trivially testable: pass `DRAFTS_AS_PUBLISHED = False` and it is a no-op; pass `True` and it promotes.

**Negative / risks:**

- A signal-ordering regression (plugin registered in the wrong order) would silently leave drafts unpromoted. The plugin guards against this with a post-promotion warning if any `status == "draft"` articles remain after the promotion pass.
- `publishconf.py` must always override the flag to `False`. If the file is lost or the import is broken, a production build could include drafts. This is acceptable given that `publishconf.py` is version-controlled and its correctness is checked by the build-verification tasks.

**Rejected alternatives:**

- Environment variable (option 2): less discoverable; the dev/prod contract is less visible.
- Two-plugin variant (option 3): unnecessary complexity.
- Template-level handling (option 4): leaves drafts excluded from index and tag pages, defeating the purpose of being able to review a draft in full context.
