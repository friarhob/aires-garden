## Status

Design decisions recorded below.

## Context

The hostname strategy (pre-launch `garden.fernandoaires.org`, terminal apex, two-layer noindex posture) is already fixed by [ADR-0003](../../decisions/0003-custom-domain-phased-launch.md), with DNS-host corrections and edge-mechanism substitutions in [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md) (DNS stays at Gandi). This design covers only the build-and-deploy mechanics that sit under that hostname: how GitHub Actions runs Pelican, how the artifact reaches Pages, how the three static-path oddities (`CNAME`, `robots.txt`, `404.html`) land at the site root, and how repo visibility flips without surprising anyone.

Current state: site builds locally via `make build`, repo is private, no workflows, no Pages config, no DNS record. First real post (`ola-jardim.pt.md`) is committed but unpublished.

Stakeholders: the author (sole contributor); professional email contacts (indirect, via the apex staying dark per ADR-0003); search engines (must see noindex during pre-launch).

## Goals / Non-Goals

**Goals:**

- One-commit, one-push path from `git push origin main` to a live update at `garden.fernandoaires.org`, typically under 2 minutes.
- Pinned, reproducible build environment (Python 3.12, explicit action versions).
- All deploy-specific build artifacts (`CNAME`, `robots.txt`, `404.html`) produced by `make build` itself — no post-build shell steps that diverge between local and CI.
- Repo-visibility flip is explicit and reversible if the author changes their mind before first deploy.
- Noindex posture is enforced in-repo (not in CI config or at the DNS edge) so it survives any workflow change.

**Non-Goals:**

- Apex cutover and noindex removal — owned by the future `launch-to-apex` change per ADR-0003. Its `garden.* → apex` redirect lands as a Gandi Web Forwarding entry (not a Cloudflare Redirect Rule) per [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md); the edge `X-Robots-Tag` layer is dropped entirely per the same ADR.
- Preview deploys for PRs (not useful until there are external contributors).
- Build caching across runs (build time is <30s; cache complexity is not justified yet).
- Custom deploy notifications (GitHub's built-in workflow status is sufficient for a one-person project).
- Dependency lock files beyond `pyproject.toml`'s version pins (no need for `requirements.txt` or `uv.lock` while the dep set is tiny).

## Decisions

### D1: GitHub Actions workflow over `gh-pages` branch

GitHub Pages supports two deploy sources: (a) "Deploy from a branch" — typically commits build output to a `gh-pages` branch, or (b) "GitHub Actions" — uploads an artifact that Pages serves directly. We pick (b).

- Pollutes no branch with build output; `main` stays human-readable.
- Build and deploy are in one place (one YAML file) instead of split across a workflow that commits to `gh-pages` and Pages' branch-deploy machinery.
- The official actions (`upload-pages-artifact`, `deploy-pages`) are maintained by GitHub and handle the Pages-specific plumbing (artifact format, OIDC-based deploy auth).

**Alternatives rejected:** `gh-pages` branch auto-commits (extra branch, extra noise, slower), third-party actions like `peaceiris/actions-gh-pages` (no reason to depend on a third party when GitHub's own actions suffice).

### D2: Build-and-deploy in a single job, not two

Some templates split build and deploy into two jobs (with `needs:`) so build logs stay separate from deploy logs. We collapse to one job because:

- Pelican build finishes in <30s — no reason to pay artifact-upload overhead twice.
- Failure diagnosis is simpler when logs are linear (build output, then deploy output, in one run).
- A single `permissions:` block applies cleanly.

**Alternative rejected:** Two-job split. Justified only if build produces a heavy artifact used by multiple deploy targets — not our case.

### D3: `STATIC_PATHS` handles `CNAME`, `robots.txt`, `404.html` via Pelican, not via a post-build `cp`

Three files need to land at `output/` root with no transformation:

1. `CNAME` — a single-line text file.
2. `robots.txt` — a short text file with `User-agent: * / Disallow: /`.
3. `404.html` — *built* from `content/pages/404.md` via Pelican's page mechanism, not copied.

For the first two, we put the source files in `content/extra/` and extend `STATIC_PATHS`:

```python
STATIC_PATHS = ["extra/CNAME", "extra/robots.txt"]
EXTRA_PATH_METADATA = {
    "extra/CNAME":      {"path": "CNAME"},
    "extra/robots.txt": {"path": "robots.txt"},
}
```

For the 404, we use Pelican's standard page mechanism — `content/pages/404.md` with a custom `save_as` — so the 404 inherits the theme automatically:

```markdown
Title: Not found
Status: hidden
Save_as: 404.html
URL: 404.html
```

**Alternatives rejected:**

- **Commit pre-built `CNAME`/`robots.txt` at `output/` root in git** — fails because `output/` is gitignored; also fights Pelican, which re-creates `output/` each build.
- **Post-build shell step in the workflow that copies files from repo root into `output/`** — works but duplicates intent across local and CI; a contributor running `make build` locally wouldn't see the same output tree as CI.
- **Serve a static 404 via a post-build `cp` of a pre-rendered HTML file** — loses theme inheritance; the 404 would stop matching the rest of the site when the theme changes.

### D4: Noindex meta lives in `base.html`, not a conditional

Two options for the `<meta name="robots">` tag:

- **Always present** — ship the tag unconditionally in `base.html`. Removal is a theme edit tracked by the `launch-to-apex` change.
- **Conditional on a Pelican setting** — something like `{% if NOINDEX %}<meta ...>{% endif %}` and flip `NOINDEX = True` in `publishconf.py`.

We pick "always present." Reasoning:

- The conditional creates a path where someone later removes the setting but forgets the template guard (or vice versa) and ships noindex silently. A single hardcoded tag has one place to edit.
- `launch-to-apex` already needs to touch `robots.txt` and DNS; editing one template line is not extra complexity.
- Dev builds (`make dev`) also serve with `noindex` — which is correct, since local builds shouldn't be indexed if someone accidentally exposes them.

**Alternative rejected:** Edge-injected `X-Robots-Tag: noindex` header — ADR-0003 already marked this optional, and [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md) drops it entirely (Gandi offers no equivalent to Cloudflare Transform Rules, and the two in-repo layers are sufficient).

### D5: `workflow_dispatch` is on; `push: [main]` is the primary trigger

- `push: branches: [main]` — primary trigger. Every commit to main deploys.
- `workflow_dispatch` — manual re-run from the Actions UI. Useful for re-deploying after a Pages outage or pushing without a commit.
- NOT triggering on tags, PRs, or schedule. A PR trigger would need a preview-deploy story, which is a non-goal.

### D6: Concurrency group cancels in-flight deploys

```yaml
concurrency:
  group: pages
  cancel-in-progress: true
```

If two pushes arrive close together, the older build's deploy is cancelled in favor of the newer one. Rationale: we want the live site to reflect the *latest* commit, not some arbitrary interleaving. The small cost (a cancelled build) is acceptable for a personal site with low push frequency.

**Alternative rejected:** Serialize deploys (`cancel-in-progress: false`) — would queue deploys. For low push volume this is functionally fine but slower to surface bugs; cancellation biases toward "latest is truth," which fits a garden better than a queue.

### D7: Repo visibility flip sequence

Order matters because the visibility flip is the one truly irreversible-ish step (the repo URL becomes indexable even without Pages — codepaths, commits, and issues all become public).

Pre-flip checklist:

1. No commits contain secrets or credentials (`git log -p | grep -Ei "password|secret|token|api[_-]?key"` returns nothing suspicious).
2. No private personal info in commit messages or file contents.
3. `.gitignore` excludes `.claude/`, editor configs, and any machine-local tool state.
4. First post (`ola-jardim.pt.md`) is OK to be publicly visible (already confirmed: user published intentionally).

Flip command:
```
gh repo edit --visibility public --accept-visibility-change-consequences
```

Only after the flip do we enable Pages. If the pre-flip review surfaces anything to clean up, we clean up before flipping — not after.

### D8: DNS record is a plain CNAME at Gandi

Per [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md), DNS stays on Gandi LiveDNS. For the pre-launch subdomain we add a plain `CNAME garden → friarhob.github.io.` record, nothing else:

- Gandi LiveDNS serves the record directly; there is no proxy/edge layer in the path to GitHub Pages. Let's Encrypt cert issuance for the custom domain talks to GitHub Pages end-to-end, with no intermediary to interfere.
- No apex change is needed here — `launch-to-apex` owns the apex record (ALIAS-style record at Gandi, or GitHub Pages' published A/AAAA addresses; the choice is deferred to that change).
- Email infrastructure on Gandi (MX, SPF, DKIM, DMARC, Google Workspace vanity CNAMEs) is untouched.

**Alternative considered:** migrate the zone to Cloudflare now to enable a proxied/edge posture later — rejected by ADR-0005 as YAGNI for the current roadmap; the door remains open if a future requirement justifies it.

## Risks / Trade-offs

- **Cert issuance delay on Pages setup** → GitHub Pages provisions the Let's Encrypt cert for `garden.fernandoaires.org` *after* DNS is configured and the custom domain is accepted. This can take anywhere from a few minutes to ~24h. **Mitigation:** configure DNS first, wait for `dig CNAME garden.fernandoaires.org` to show `friarhob.github.io`, then set the custom domain in Pages settings — this ordering gives Pages a valid CNAME to verify immediately, minimizing cert-wait. If the cert stalls, use the Pages settings "Check again" button.

- **`workflow_dispatch` not visible until the workflow exists on `main`** → GitHub doesn't expose manual re-runs for workflows that only exist on feature branches. **Mitigation:** land the workflow via merge (or direct push) to `main`; first deploy then triggers automatically, and `workflow_dispatch` becomes available.

- **Repo visibility flip is *not* reversible without data loss of public attention** → Once public, any URL shared externally (even briefly) can be cached/indexed. **Mitigation:** D7's pre-flip checklist; plus the noindex posture on the site itself (ADR-0003).

- **First deploy fails because `STATIC_PATHS` misses a file** → Pelican logs warnings for missing static paths but still builds, producing an `output/` without `CNAME`. GitHub Pages then 404s the custom domain. **Mitigation:** add a scenario-backed check (the spec requires `output/CNAME` to exist after build) and eyeball the first deploy's logs.

- **Pages custom-domain setting drifts from `output/CNAME`** → If someone edits the Pages UI to set a different domain, or removes the `CNAME` file, the two fall out of sync and Pages either 404s or redirects unexpectedly. **Mitigation:** specs/scenarios assert equality; treat `output/CNAME` as the source of truth; avoid editing the Pages UI custom-domain field except at `launch-to-apex` cutover.

- **Ephemeral `friarhob.github.io/aires-garden/` URL exposure window** → Between enabling Pages and setting the custom domain, the site is briefly reachable at the default URL. **Mitigation:** set the custom domain immediately after enabling Pages; noindex is already in-repo so even a cached crawl from that URL respects it.

- **`garden.* → apex` 301 for the cutover is not configured here** → When `launch-to-apex` flips the site to the apex, RSS subscribers and external backlinks to `garden.*` URLs will break unless the redirect lands. **Mitigation:** ADR-0003 already puts this redirect on the `launch-to-apex` checklist; [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md) specifies the mechanism as a Gandi Web Forwarding entry (not a Cloudflare Redirect Rule). No action needed in this change.

- **Pinned action versions use Node.js 20, which GitHub is retiring** → The four actions we pin (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`) all run on Node.js 20 today. GitHub is flipping runner defaults to Node.js 24 on **2026-06-02** and removing Node.js 20 from the runner entirely on **2026-09-16**. Surfaced as a workflow annotation on the first green deploy. **Mitigation:** tracked as a separate follow-up change (tentatively `upgrade-actions-node24`) to bump each action to its Node 24-compatible major version before 2026-09-16. Escape hatches in the meantime: `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` to opt in early, or (post-flip) `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` to temporarily defer. Scope-excluded from this change because the pipeline works today and action-version bumps are cleaner as independently-reviewable diffs.

## Migration Plan

No migration — this is the first deploy. Rollback: revert the commit that introduces the workflow and push; Pages stops re-deploying but keeps serving the last successful artifact until GH Pages is manually disabled.
