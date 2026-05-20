---
name: Garden Development Workflow
description: Complete lifecycle for proposing, implementing, and finalising changes in the aires-garden project
version: "1.0"
lastUpdated: "2026-05-11"
---

# Garden Development Workflow

This document defines the complete workflow for developing changes in the aires-garden project. It serves as the source of truth for both human developers and AI assistants.

The workflow has three phases: **Propose**, **Implement**, and **Finalise**.

---

## Phase 1: Propose

**Command:** `/garden:propose <change-name>`

The proposal phase captures the full scope of a change before implementation begins. It includes adaptive questioning, prototype iteration (for visual changes), spec validation, and artifact creation.

### 1.1 Entry & Roadmap Check

```
INPUT: User runs /garden:propose add-l10n-rendering
↓
Read openspec/roadmap.md
Search for <change-name> in the "Planned" section
↓
IF found:
  → Extract: scope, design questions, notes, dependencies, content requirements
  → Use as context for all subsequent questions
ELSE:
  → Ask user: "What do you want to build? Describe the change."
  → Extrapolate from user description
```

**Roadmap context includes:**
- Scope (small/medium/large)
- Any design questions already noted
- Dependencies on other changes
- Content authoring requirements
- Coordination notes

### 1.2 Scope Discovery

Ask user (or infer from roadmap entry) what the change touches. Mark all that apply:

```yaml
scope_tags:
  - visual: Does this change the user interface, styles, or layout?
  - specs: Does this touch existing specs? (Which ones: content-model, site-build, deploy-pipeline, etc.?)
  - cli: Does this require new CLI commands or changes to garden CLI?
  - content: Does this require seeded content before shipping?
  - deploy: Does this change how the site is deployed or built?
  - architectural: Is this an architectural decision (would warrant an ADR)?
```

**Output:** A set of tags indicating what this change affects. This determines the order of subsequent questions.

### 1.3 Adaptive Questioning

Questions are asked in semantic order based on scope tags. Ask all relevant questions; skip irrelevant ones.

#### 1.3a IF visual changes detected

1. **Show prototype approach:** "This affects the UI. I'll build an HTML prototype to iterate on. Ready?"
2. **Build prototype:** Create temporary HTML mockup showing the design direction (simple, as possible)
   - Save to `tools/` with a descriptive name (e.g., `tools/prototype-l10n-layout.html`)
   - Include minimal CSS/structure to demonstrate direction
   - Include notes on what's being explored
3. **Iterate:** Show prototype to user, ask "Does this direction work?"
   - If no: revise and repeat
   - If yes: continue to next question
4. **Keep for reference:** Prototype stays in `tools/` through implementation — you may reference it during coding
5. **Cleanup in finalise:** Delete prototype only during Phase 3 (finalisation)
6. **Capture decision:** Note the visual approach in `design.md` (created in 1.4)

#### 1.3b IF specs are touched

1. **Identify specs:** Ask which existing specs this change affects
   - Examples: `content-model`, `site-build`, `deploy-pipeline`, `design-tokens`, `garden-cli`, `user-preferences`, `content-tags`
   - User can reference `openspec/specs/` for the list
2. **Read base specs:** For each spec touched, read `openspec/specs/<spec-name>/spec.md` to understand current state
3. **Create draft specs:** For each spec that needs updating, create a draft spec in the change folder:
   - Create `openspec/changes/<change-name>/specs/<spec-name>/spec.md`
   - Start with content from the base spec
   - Make any changes needed for this change's design
   - Draft specs live in the change folder; they will be merged into base specs after deploy
4. **Note spec intent:** In `design.md` (created in 1.4), document which specs are being changed and why

#### 1.3c IF CLI or content changes detected

1. **CLI changes:** Clarify what new commands/options are needed
2. **Content seeding:** Ask if this change requires seeded content before shipping
   - If yes: note that content authoring is a blocker for verification
   - Reference memory: `project_published_works_seed.md` if `add-tags-and-drafts`-like situation

#### 1.3d IF architectural (context-dependent)

Ask: "This looks like an architectural decision. Should we create an ADR (Architecture Decision Record)?"

- Examples of architectural decisions:
  - New content types or structures
  - Changes to rendering pipeline
  - New state management patterns
  - Changes to deployment or build process
- If yes: note that ADR will be created
- If no: continue

### 1.4 Artifact Creation

Create the following artifacts in this order. All must be created before moving to implementation.

```
proposal.md              — ALWAYS: what and why (roadmap context, scope, dependencies)
design.md                — ALWAYS: how (design decisions, visual approach, spec impacts)
tasks.md                 — ALWAYS: implementation steps
specs/<spec-name>/       — IF specs touched: draft specs created in 1.3b above
                           Location: openspec/changes/<change-name>/specs/<spec-name>/spec.md
decisions/NNNN-*.md      — IF architectural decision noted (format: 0001-description-with-kebab-case.md)
                           (Find next NNNN by reading existing decisions/)
```

**Artifact creation follows OpenSpec schema.** Use `openspec instructions <artifact-id> --change <change-name> --json` to get the exact structure for each artifact type.

**Key constraints during proposal:**
- `proposal.md`: Reference roadmap entry if found. Capture scope, dependencies, design questions.
- `design.md`: Document what was learned during scope discovery. Note which specs are affected and why.
- `tasks.md`: Break down implementation into small, committable chunks. Remember: **commit small and often during implementation** (per project feedback).
- `specs/<spec-name>/spec.md`: Draft specs live in the change folder. They will be merged into `openspec/specs/` after deploy validation.
- `decisions/NNNN-*.md`: If architectural decision, document the decision and rationale.

### 1.5 Approval Gate

Once all artifacts are created:

1. Show user a summary:
   ```
   PROPOSAL SUMMARY
   ────────────────
   Change: add-l10n-rendering
   Scope: [tags]
   Artifacts created: proposal.md, design.md, tasks.md
   Specs updated: site-build/spec.md
   ADRs created: decisions/0011-l10n-strategy.md
   
   Visual prototype: [approved & deleted]
   
   Ready to implement with /garden:implement?
   ```

2. Ask: "Ready to implement?"
   - If yes: → ready for Phase 2
   - If no: → ask what needs adjusting, iterate in proposal phase

**Important:** Do not move to implementation until user confirms approval.

---

## Phase 2: Implement

**Command:** `/garden:implement`

The implementation phase executes the tasks defined in the proposal, with validation gates and automatic document updates.

### 2.1 Task Execution

1. Run tasks from `tasks.md` in order
2. For tasks that require human input/decision:
   - Pause and ask: "This task needs your input: [question/context]"
   - Wait for user response
   - Continue with the answer
3. **Commit small and often:** Create a commit for each logical chunk, not batches
4. **Keep `tasks.md` in sync with commits:** Before creating each commit, mark all tasks completed in that commit's scope as `- [x]`. Never let `tasks.md` fall more than one commit behind the code.

### 2.2 Document & Script Updates

As you implement, the skill watches for changes and updates:

**Documents to update:**
- **README.md:** If user instructions or setup changed, update immediately
- **docs/visual-identity.md:** If visual tokens, colours, or design changed, update immediately
- **decisions/*.md:** If architectural decisions change mid-implementation, update the ADR
- **Draft specs:** If specs need further updates discovered during implementation, edit the draft specs in `openspec/changes/<change-name>/specs/`
  - These are working copies; they will be merged into base specs after deploy

**Tools to verify & update:**
- Check `tools/` for scripts that are affected by the implementation (e.g., `contrast_audit.py` if colours change, helper scripts for new CLI commands, etc.)
- Update affected scripts immediately
- If new helper scripts are needed, create them (they'll be cleaned up in finalisation if temporary)

**Extensible document list:**
If during implementation you discover a new document that should be tracked here (e.g., a new `docs/X.md`), update WORKFLOW.md to include it so future changes know about it.

Updates happen as you go — don't batch them.

### 2.3 Makefile Verbs (Reference)

The project has three valid Makefile verbs:

```bash
make dev       — Start dev server (long-running)
make devbuild  — One-shot development build (use for testing)
make build     — Production build (what GHA runs)
```

If you try to run a Makefile target that doesn't exist, the skill will remind you of the valid verbs instead of attempting to run it.

**If you add a new Makefile verb**, update WORKFLOW.md to include it in this list.

### 2.4 Deploy Validation Gate

When all tasks are complete:

1. **Ask user:** "All tasks done. Ready to push and validate deploy?"
2. **If yes:**
   - Push to remote: `git push`
   - Monitor GitHub Actions for `build-and-deploy` workflow
   - Validate that the run completes successfully (green checkmark)
   - Show result to user
3. **If no:** Stay in implementation phase, ask what's left to do
4. **Once deploy validated:** Ask "Deploy validated. Ready to finalise with /garden:finalise?"

**Important:** Don't auto-archive. Validation must happen before finalisation.


---

## Phase 3: Finalise

**Command:** `/garden:finalise`

The finalisation phase merges draft specs into base specs, archives the change, updates the roadmap, and verifies all documentation.

### 3.1 Merge Draft Specs into Base Specs

1. **Find draft specs:** Look in `openspec/changes/<change-name>/specs/`
2. **For each draft spec:**
   - Read `openspec/changes/<change-name>/specs/<spec-name>/spec.md`
   - Merge its content into `openspec/specs/<spec-name>/spec.md`
     - If base spec doesn't exist, create it from the draft
     - If base spec exists, integrate the changes (don't overwrite; merge thoughtfully)
   - Fix any issues discovered during implementation
3. **Verify merge:** The base specs should now reflect all changes from this development cycle

**Example:**
```
Before:
  openspec/specs/site-build/spec.md (original)
  openspec/changes/add-l10n-rendering/specs/site-build/spec.md (draft with l10n changes)

After:
  openspec/specs/site-build/spec.md (merged, includes l10n changes)
```

### 3.2 Archive the Change

Move the entire change folder to archive with a timestamp:

```bash
mv openspec/changes/<change-name>/ openspec/changes/archive/YYYY-MM-DD-<change-name>/
```

This preserves:
- The proposal, design, tasks documents
- The draft specs as they were when the change shipped
- The full history of the change

### 3.3 Clean Up Temporary Files

Delete all temporary files created during proposal and implementation:
- Remove prototypes from `tools/` (e.g., `tools/prototype-*.html`)
- Remove any test HTML, temporary scripts, or other artifacts created during implementation
- Remove any temporary helper scripts that were used for verification but shouldn't be committed
- Keep `tools/` clean; only permanent, committed artifacts remain

### 3.4 Update Roadmap

Update `openspec/roadmap.md`:
1. Move the change from **Planned** to **Shipped** (if it was in Planned)
2. Add a table row with: change name, date archived, brief note
3. Example:
   ```markdown
   | `add-l10n-rendering` | 2026-05-12 | UI localisation for all templates, all four languages |
   ```

### 3.5 Verify Documentation

Double-check that these were updated during implementation (they should have been):

- [ ] `README.md` — User instructions, setup steps
- [ ] `docs/visual-identity.md` — Visual tokens, colour decisions, design patterns
- [ ] `openspec/specs/*.md` — Base specs merged and up to date

If any are missing, update now.

### 3.6 Completion

Once all the above are done:
- Run `openspec validate` to ensure all specs are internally consistent
- Commit the spec merges, roadmap update, prototype cleanup, and archive move
- You're done! Change is shipped.

---

## Document Consolidation

The following documents are updated at different stages:

| Document | Purpose | Created/Updated | Status |
|----------|---------|-----------------|--------|
| `README.md` | User-facing setup, instructions | Impl phase | Verified in Finalise |
| `docs/visual-identity.md` | Design tokens, visual decisions | Impl phase | Verified in Finalise |
| `openspec/roadmap.md` | Project roadmap, shipped changes | Finalise phase | Updated after deploy |
| `openspec/changes/<name>/specs/*` | Draft specifications (in-flight) | Proposal phase | Evolved during Impl |
| `openspec/specs/*` | Base specifications (deployed reality) | Finalise phase (merged) | Finalized after deploy |
| `openspec/decisions/*.md` | Architectural decisions | Proposal phase | Updated during Impl if needed |

**Key insight:** Draft specs live with the change while it's in flight. After deploy, they're merged into base specs, which become the source of truth for the next changes.

All three doc folders (`docs/`, `openspec/specs/`, `openspec/decisions/`) live together as the **project documentation**, organised by semantic purpose.

---

## Decisions & Context

### Why semantic, adaptive questioning?

The proposal phase asks different questions depending on what the change touches. A visual redesign needs prototype iteration; a CLI improvement doesn't. This avoids the frustration of repetitive questions that don't apply.

### Why draft specs during proposal, then merge after deploy?

Specs serve two purposes: as a **blueprint for implementation** and as a **record of deployed reality**. By creating draft specs in the change folder during proposal:

- **During proposal & impl:** Developers have a spec to code against (blueprint)
- **During impl:** Specs can evolve as the team discovers things (flexibility)
- **After deploy:** Draft specs are merged into base specs (record of reality)

This ensures specs describe *what actually shipped*, not just what was intended. Base specs become the source of truth for future changes.

### Why prototypes stay until finalisation?

Prototypes are reference material. Keeping them through implementation lets developers refer back to the design direction if questions arise. They're deleted only during finalisation cleanup.

### Why commit small and often?

Smaller commits are easier to review, understand, and revert if needed. Per project feedback: **prefer smaller, more frequent commits during implementation; don't batch logically-separable changes.**

### Why validate deploy before finalising?

The change isn't truly shipped until it's deployed and live. Validating the deploy before archiving ensures we know it worked.

---

## How AI Assistants Use This

When you invoke `/garden:propose`, `/garden:implement`, or `/garden:finalise`, the AI assistant reads this WORKFLOW.md and:

1. **Follows the phase definition in order** — executes steps as specified
2. **Asks questions when needed** — for scope discovery, ADR decisions, human input on tasks
3. **Validates gates** — don't move to next phase without approval
4. **Performs automatable tasks:**
   - Creates artifacts (proposal, design, tasks, specs, ADRs)
   - Builds and iterates prototypes
   - Merges specs after deploy
   - Updates documents (README, visual-identity, specs, ADRs, WORKFLOW.md if new docs discovered)
   - Identifies and updates affected `tools/` scripts
   - Archives changes and cleans up temporary files
5. **Prompts for human decisions** — pauses for user input when a task needs it

If you want to change the workflow, edit this file. The next session will read the updated version.

---

## Next Steps

This workflow covers Propose, Implement, and Finalise phases. Future additions:
- Validation/audit agents (periodic checks on spec consistency, ADR completeness)
- Custom agents for specific patterns (visual iteration, content seeding verification)
- Integration with GitHub Issues for blocked changes or blocked content authoring
