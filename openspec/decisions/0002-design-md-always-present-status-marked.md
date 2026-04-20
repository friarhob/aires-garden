# ADR-0002: `design.md` is always present, Status-marked

## Status

Accepted — 2026-04-20.

## Context

OpenSpec's `design.md` artifact is optional per the spec-driven schema. Omitting it leaves ambiguity: future readers cannot tell whether the design step was consciously skipped (no implementation tradeoffs worth recording) or silently forgotten.

The naive fix — always write a stub `design.md` that says "no decisions" — risks the opposite failure: if every stub says the same thing, stubs decay into boilerplate and contributors learn to skip `design.md` entirely, killing the signal value of the artifact when it actually contains decisions worth reading.

## Decision

Every change directory MUST contain a `design.md`. The file MUST begin with a `## Status` heading whose body takes exactly one of two forms:

1. **`Design decisions recorded below.`** — followed by normal `## Context`, `## Options`, `## Decision`, `## Consequences` sections.
2. **`No change-scoped design decisions.`** — followed by at least one sentence naming where the reasoning *did* live (the project brief, a specific ADR, an upstream convention such as "follow Pelican defaults", etc.).

The Status line is mandatory. Stubs without a concrete "where the reasoning lived" pointer are not valid under this convention.

`design.md` carries change-scoped implementation rationale only. Project-level decisions (spanning multiple proposals or overriding the baseline) belong in ADRs under `openspec/decisions/`.

## Consequences

- Presence of `design.md` becomes evidence that the design step was consciously performed, not omitted by oversight.
- The mandatory Status line and the requirement to name *where* reasoning lived keep stubs informational rather than boilerplate: every stub is provably the work of a mind reasoning about a specific change, because it must cite a specific upstream source.
- Contributors get a one-glance signal (the Status line) for whether the file contains change-scoped decisions worth reading further.
- OpenSpec's "design is missing" validation warning goes away for every change.
- Cost: one extra file per change, ~3 sentences when there are no change-scoped decisions.

Alternatives considered:

- **Omit `design.md` when there are no change-scoped decisions** — rejected because absence is ambiguous between "skipped intentionally" and "forgotten".
- **Always write a stub with fixed boilerplate text** — rejected because identical stubs teach contributors to skip `design.md` as noise, destroying the signal when a real design doc appears.
- **Single project-wide convention document describing the stub rule** — rejected because design decisions are intrinsically change-scoped; the Status marker should live where the reasoning lives.
- **Use a different filename for "no decisions" cases** (e.g. `no-design.md`) — rejected because it invents a parallel artifact with no OpenSpec support and doubles the places contributors must look.
