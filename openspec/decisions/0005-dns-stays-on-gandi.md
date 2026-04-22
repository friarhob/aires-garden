# ADR-0005: DNS stays on Gandi; tag subdomains use Gandi Web Forwarding

## Status

Accepted — 2026-04-22.

## Context

`add-deploy-pipeline` needs DNS in place to finish wiring GitHub Pages. ADR-0003's opening paragraph states "the project has a custom domain (fernandoaires.org) at Cloudflare." That was factually wrong at the time of writing: the domain is registered at Gandi, authoritative DNS is Gandi LiveDNS, and email (Google Workspace) depends on a set of Gandi-managed records (MX, SPF, DKIM, DMARC, plus vanity-redirect CNAMEs like `mail.`, `drive.`). No Cloudflare account exists.

The error matters because ADR-0003 and the `add-deploy-pipeline` design reference Cloudflare-specific mechanisms — a Transform Rule for `X-Robots-Tag`, a Redirect Rule for `garden.* → apex` at `launch-to-apex`, CNAME flattening at the apex, and the brief's planned tag-subdomain rewrite feature (e.g., `poetry.fernandoaires.org → /tag/poetry/`). With the domain actually at Gandi, each of those mechanisms either doesn't exist, requires migration, or substitutes to something else.

Migrating DNS to Cloudflare is possible but non-trivial: it requires auditing and copying every existing Gandi DNS record (email and redirect CNAMEs) into Cloudflare *before* flipping nameservers at the registrar, or mail breaks during propagation. Cloudflare's supported "delegate a single subdomain" setup is Enterprise-only, so the lightweight "Cloudflare for `garden.*` only, Gandi for everything else" hybrid is not available on free.

The tag-subdomain feature is the main argument for migrating. On closer inspection it splits on a UX question: does the subdomain URL need to **stay** in the address bar (rewrite) or is it acceptable for it to **flip** to the apex path (redirect)?

- **Rewrite** (URL stays on `poetry.fernandoaires.org`): requires an edge worker or per-subdomain reverse proxy. Cloudflare Workers is the free-tier-friendly path; Gandi offers nothing comparable.
- **Redirect** (URL flips to `garden.fernandoaires.org/tag/poetry/`): a 301 at whichever edge. Gandi Web Forwarding does this per subdomain; Cloudflare Redirect Rules do this with fewer rules via wildcards.

The feature is speculative — the brief envisions it, but no change has scoped it, and a personal garden's plans drift. The cost of migrating DNS to Cloudflare *if and when* rewrite becomes a firm requirement is the same as migrating today. The cost of not migrating today is zero if the feature never materializes, or zero if it materializes with redirect-semantics accepted.

## Decision

**DNS stays at Gandi.** `add-deploy-pipeline`'s task 3.1 adds the `garden` CNAME record at Gandi, not at Cloudflare. No Cloudflare account is created as part of this or any change in the current roadmap.

**Tag subdomains, when built, use Gandi Web Forwarding with redirect-flavored semantics.** A future `add-tag-subdomains` change owns the design and the operational how-to; the mechanism committed here is: one Gandi Web Forwarding entry per tag subdomain, path-preserving where supported, targeting the canonical tag URL at the apex (or at `garden.*` pre-launch). The browser URL flips on each request; this is an accepted UX trade.

**ADR-0003's Cloudflare-specific mechanisms substitute as follows:**

1. *CF Transform Rule injecting `X-Robots-Tag: noindex` at the edge* — dropped entirely. ADR-0003 already marked this optional; the in-repo `robots.txt` and `<meta name="robots">` layers cover the noindex posture without it.
2. *CF Redirect Rule `garden.* → apex` at launch-to-apex* — substituted with a Gandi Web Forwarding entry on `garden.fernandoaires.org` pointing to the apex. Path preservation is required. `launch-to-apex` owns the cutover and documents the exact Gandi steps then.
3. *CF CNAME flattening at the apex* — substituted with Gandi's equivalent (Gandi supports ALIAS-style apex records, or GitHub Pages' four published A/AAAA addresses can be used directly; the choice is deferred to `launch-to-apex`).
4. *CF Access / HTTP Basic Auth for pre-launch gating* — remained rejected as overkill in ADR-0003; no substitution needed.

**Migration to Cloudflare remains a cheap, reversible option** if a future requirement (rewrite-semantic tag subdomains, DDoS absorption, edge caching) concretizes and a day's focused work is justified. This ADR does not block that; it declines it today.

## Consequences

- `add-deploy-pipeline` task 3.1 reworded from Cloudflare-specific to Gandi-specific; design.md D8 similarly narrowed. The spec's scenarios already speak of "Cloudflare DNS resolves the subdomain to GitHub Pages" — tightening to "DNS resolves the subdomain to GitHub Pages" keeps the requirement provider-agnostic.
- Email infrastructure is untouched. Zero migration risk to `@fernandoaires.org` or the vanity-redirect subdomains.
- Tag subdomains, when built, ship as redirects not rewrites. URLs visibly flip from `<tag>.fernandoaires.org` to the canonical tag URL (at `garden.*` pre-launch, at the apex post-launch). This is a real UX trade — vanity subdomains function as short links, not as standalone branded namespaces.
- `launch-to-apex` owns two substituted items (Gandi web forward for `garden.*`, apex record setup). Its design work will document the exact Gandi operations; no Cloudflare sub-task appears in that change.
- If the brief's tag-subdomain feature demands rewrite semantics later, a migration-to-CF change is scoped then: audit + copy email records, flip NS at Gandi, configure Workers. ~4–8 hours of focused work. The door remains open.

Alternatives considered:

- **Migrate DNS to Cloudflare now to preserve Workers-based rewrite option** — rejected: pays the migration cost today for a speculative feature. YAGNI. Migration cost is symmetric across timing; deferring costs nothing if the feature is never built or if redirect-semantics prove acceptable.
- **Delegate `garden.fernandoaires.org` as a standalone Cloudflare zone, keep the apex at Gandi** — rejected: Cloudflare's supported subdomain-as-zone setup is Enterprise-only. Free-plan workarounds exist but rely on unsupported behavior for load-bearing infrastructure.
- **Deploy tag subdomains as independent GH Pages sites (one repo per tag)** — rejected: massive per-tag operational overhead (repo, workflow, CNAME file, DNS record, cert) for negligible benefit.
- **Use a third-party host (Netlify / Vercel) with native rewrite config** — rejected: changes deploy target entirely, re-opens multiple settled decisions, and migrating static-site hosts later is cheap — no reason to pre-optimize.
- **Full supersession of ADR-0003** — rejected: ADR-0003's phased-launch decision is unaffected. Only its Cloudflare plumbing needs substitution. A light-touch forward-pointer in ADR-0003's Status line preserves the original reasoning intact.
