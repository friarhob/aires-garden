# Decisions

Append-only log of project-level Architecture Decision Records (ADRs) for aires-garden.

## What goes here

Project-level decisions: things that span multiple proposals, override the project baseline (`openspec/project.md`), or that future-you would want to look up by searching "why did we pick X over Y".

Change-scoped implementation tradeoffs do NOT belong here — those live in the `design.md` of the owning change.

## Format

Each ADR is a single file named `NNNN-kebab-title.md`, where `NNNN` is a monotonic four-digit integer starting at `0001`. Numbers are never reused.

Required sections (in order):

- `## Status` — one of `Accepted`, `Superseded by ADR-NNNN (YYYY-MM-DD)`, `Rejected`, or `Deprecated`, followed by the decision date.
- `## Context` — the situation and forces at play when the decision was made.
- `## Decision` — the decision itself, stated in present tense.
- `## Consequences` — positive and negative consequences, including alternatives considered and why they were rejected.

## Supersession

A newer ADR that overrides an earlier one marks it as superseded:

1. Write `0007-new-approach.md` with the new decision.
2. Edit `0003-old-approach.md`'s `## Status` to `Superseded by ADR-0007 (YYYY-MM-DD)`.

The original ADR text remains intact — supersession is recorded, not erased.

## `design.md` convention (ADR-0002)

Every change directory contains a `design.md` starting with a `## Status` heading. The body is exactly one of:

1. `Design decisions recorded below.` — followed by normal `## Context`, `## Options`, `## Decision`, `## Consequences` sections.
2. `No change-scoped design decisions.` — followed by at least one sentence naming where the reasoning *did* live (the project brief, a specific ADR, an upstream convention).

See [ADR-0002](0002-design-md-always-present-status-marked.md) for the rationale.

## Index

- [0001 — Project context uses a frozen baseline plus an ADR log](0001-project-context-baseline-plus-adrs.md)
- [0002 — `design.md` is always present, Status-marked](0002-design-md-always-present-status-marked.md)
- [0003 — Custom domain uses phased launch (`garden.` pre-launch, apex at public launch)](0003-custom-domain-phased-launch.md)
- [0004 — Multilingual post frontmatter conventions (localized slugs + `Translation_key` + `Lang` format)](0004-multilingual-post-frontmatter-conventions.md)
- [0005 — DNS stays on Gandi; tag subdomains use Gandi Web Forwarding](0005-dns-stays-on-gandi.md)
