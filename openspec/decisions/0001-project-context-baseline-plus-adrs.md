# ADR-0001: Project context uses a frozen baseline plus an ADR log

## Status

Accepted — 2026-04-20.

## Context

OpenSpec's artifact set (`proposal`, `specs`, `design`, `tasks`) is per-change. Project-level context — the origin story, cross-change decisions (stack choice, deferrals, known gaps), and multi-proposal plans — has no home in that schema.

Without a convention, such context drifts between the original brief document, conversation transcripts, scattered README notes, and nowhere durable at all. Six months after t=0, future-us would struggle to reconstruct *why* particular calls were made (e.g. "why Pelican over Astro?"), and even harder to distinguish original intent from later revisions.

## Decision

Project-level context lives in two places under `openspec/`:

- **`openspec/project.md`** — the original project brief preserved as the frozen `t=0` baseline. Never edited retroactively. Captures intent and rationale at project inception: stack choice, content model, proposal order, deferrals, known gaps.
- **`openspec/decisions/`** — append-only log of Architecture Decision Records (ADRs). Each ADR is a single file `NNNN-kebab-title.md` with sections `## Status`, `## Context`, `## Decision`, `## Consequences`. Numbering is monotonic, never reused. Supersession: a newer ADR marks the older one `Superseded by ADR-NNNN (YYYY-MM-DD)`, but the older file's body is never erased.

Per-change `design.md` is reserved for change-scoped implementation rationale only. It does NOT carry project-level decisions.

## Consequences

- Six-month-future-readers get the origin story from `project.md` and scan `decisions/` for what has changed since.
- Project-level decisions are searchable as individual files rather than mixed into specs or per-change design docs.
- Supersession preserves history — we can always reconstruct the decision trail.
- Cost: two artifact conventions beyond OpenSpec's defaults.

Alternatives considered:

- **Pure-ADR (no baseline file)** — fragment the brief into ~10 ADRs. Rejected because retroactive ADRs lose the brief's narrative coherence (connective tissue between related decisions, non-decision content like specs/plans/warnings, and the "we thought of all of this together" framing) without gaining the in-the-moment freshness benefit that makes ADRs valuable.
- **Fold the brief into `README.md`** — rejected because README mixes operational content ("how to run this") with decision rationale ("why Pelican"), diluting both audiences.
- **No project-level docs; rely on conversation memory** — rejected because conversation transcripts are not durable across sessions, tools, or contributors.
- **`design.md` per proposal with cross-references to the brief** — rejected because project-level rationale fragments across per-change docs and the brief needs to live somewhere committed first.
- **Single evolving `project.md` (no ADRs, just edit the file)** — rejected because in-place edits erase the decision trail; there is no way to see *what changed* vs. *what was always intended*.
