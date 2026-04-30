# ADR-0006: Status enum is `{draft, published, hidden}`

## Status

Accepted — 2026-04-30.

## Context

The project brief defines the `Status` frontmatter field for posts as accepting exactly two values: `draft` and `published`. Drafts are visible in local dev and excluded from production builds; published posts are included in both.

However, the `add-deploy-pipeline` change already shipped `content/pages/404.md` with `Status: hidden` — a value Pelican supports natively to mean "render this file but exclude it from all indexes, tag pages, and feeds." The deploy-pipeline spec explicitly requires `status: hidden` for the 404 page so it doesn't appear in article listings.

This creates a contradiction: the brief's two-value enum would require the linter introduced by `add-content-model` to reject the already-live 404 page. The three options considered were:

1. Force `{draft, published}` strictly and change the 404 page to use a different mechanism (e.g. a `Save_as` + `status: published` combo with a template conditional that hides it from indexes).
2. Extend the enum to `{draft, published, hidden}`, applied identically to posts and pages.
3. Per-content-type rules: posts accept `{draft, published}`, pages accept `{draft, published, hidden}`.

## Decision

The `Status` field accepts exactly `{draft, published, hidden}`, with identical validation applied to posts and pages. There is no schema default — authors must declare the value explicitly.

## Consequences

**Positive:**

- The existing 404 page validates without modification.
- Future utility pages (`/about/`, `/colophon/`, `/now/`, `/uses/`) have a first-class status value that excludes them from indexes and feeds without requiring workarounds.
- `hidden` for posts is unusual but not forbidden; a deliberate "unlisted post" reachable by direct URL is a valid use case the schema doesn't need to prevent.
- One enum applied uniformly is simpler to lint and document than per-content-type rules.

**Negative:**

- Small deviation from the project brief. Recorded here so future readers understand why the linter accepts three values rather than two.

**Alternatives rejected:**

- **`{draft, published}` strict-to-brief:** Forces the 404 page to use a workaround (e.g. `status: published` + template exclusion logic). Adds more complexity than the extra enum value, and contradicts the deploy-pipeline spec's explicit `status: hidden` requirement.
- **Per-content-type rule (posts `{draft, published}`, pages `{draft, published, hidden}`):** More precise on paper, but adds a code branch to the linter for marginal benefit. `hidden` posts are unusual but not harmful; per-type rules penalise any future use of hidden posts (e.g. a private permalink shared directly). Uniform enum is cleaner.
