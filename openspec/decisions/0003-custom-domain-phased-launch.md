# ADR-0003: Custom domain uses phased launch — `garden.` subdomain pre-launch, apex at public launch

## Status

Accepted — 2026-04-20. See [ADR-0005](0005-dns-stays-on-gandi.md) (2026-04-22) for DNS-host corrections (domain is at Gandi, not Cloudflare) and substitutions for the Cloudflare-specific mechanisms referenced below.

## Context

The project has a custom domain (`fernandoaires.org`) at Cloudflare. The `add-deploy-pipeline` change needs to pick a hostname before wiring GitHub Pages + DNS, and two questions bundle together: (1) what is the *terminal* public URL of the garden, and (2) what is the hostname during the build-up phase before the site is ready for public consumption?

Professional constraint: `@fernandoaires.org` is used as a professional email address. Contacts receiving mail from that domain occasionally navigate to the apex to learn more. Today the apex resolves to nothing — a non-signal. Deploying an incomplete garden to the apex would replace that zero-signal with a visibly work-in-progress signal, which is strictly worse for that audience.

The brief plans a future feature: Cloudflare-powered subdomain routing where `poetry.fernandoaires.org` rewrites to `/tag/poetry/` of the garden. That feature semantically reads as "the apex IS the garden; sibling subdomains are views into it." Placing the garden permanently at a subdomain would break that pattern (would yield awkward double-subdomain routing like `poetry.fernandoaires.org → garden.fernandoaires.org/tag/poetry/`).

Switching hostnames is cheap while the site has no readers, backlinks, RSS subscribers, or search indexing; it grows moderately expensive once any of those exist. So the decision is reversible *if made early*, which means this ADR commits to the terminal plan rather than to the current hostname alone.

## Decision

**Terminal state (after public launch):** the garden lives at the apex, `https://fernandoaires.org`. GitHub Pages auto-configures `www.fernandoaires.org` to redirect to the apex.

**Pre-launch state (current):** the garden deploys to `https://garden.fernandoaires.org`. The apex remains unconfigured for web (DNS-only, no web handler), so professional contacts hitting the apex see the same zero-signal as before.

**Indexing posture during pre-launch:** the site serves two noindex signals in-repo so search engines and crawlers do not index the build-up state:

1. `robots.txt` at the site root containing `User-agent: *` / `Disallow: /`.
2. `<meta name="robots" content="noindex, nofollow">` in the theme's base template.

A third layer — a Cloudflare Transform Rule injecting `X-Robots-Tag: noindex` at the edge — is optional and deferred unless noncompliant crawlers become a visible problem.

**Transition to public launch** is a future change (working title `launch-to-apex`) that MUST perform all of the following atomically:

- Remove the `Disallow` rule from `robots.txt` (or delete the file) and remove the `noindex` meta tag from the base template.
- Remove the optional `X-Robots-Tag` Cloudflare rule if it was installed.
- Update the GitHub Pages custom domain from `garden.fernandoaires.org` to `fernandoaires.org`.
- Update the `CNAME` file at repo root and `SITEURL` in `publishconf.py`.
- Replace the `garden.` CNAME DNS record with apex A/AAAA records pointing at GitHub Pages' IPs (or use Cloudflare's CNAME flattening).
- Add a Cloudflare Redirect Rule: `garden.fernandoaires.org/*` → `fernandoaires.org/$1` (301) to catch any stragglers (RSS subscribers, bookmarks, external backlinks).

The timing of the cutover is not fixed here — the user flips when content volume and quality justify public visibility.

## Consequences

- Professional email contacts see no change during build-up; the apex remains a non-signal, preserving current behavior.
- `add-deploy-pipeline` is simpler in the short term: single `CNAME` to `friarhob.github.io`, no apex A/AAAA records yet.
- One future change is anticipated by this ADR — the `launch-to-apex` migration — so the work is on the roadmap rather than rediscovered later.
- Two noindex signals ship in-repo (`robots.txt`, meta tag). Both are explicitly temporary. The cutover checklist lives in this ADR to prevent the noindex from outliving the launch.
- Social preview bots (Slack, Twitter, LinkedIn, etc.) are the one gap in the noindex strategy — they fetch URLs to generate link previews regardless of `robots.txt`. Mitigation: do not share the `garden.` URL in professional contexts during pre-launch.
- The brief's planned subdomain-routing feature (`poetry.fernandoaires.org → /tag/poetry/`) is deferred until after apex cutover. The feature makes sense only once the garden is at the apex.

Alternatives considered:

- **Deploy directly to the apex now** — rejected: the professional email audience would see an incomplete garden. The "deploy early to catch URL/path bugs" rationale works equally well against a pre-launch subdomain.
- **Deploy permanently to `garden.`, never migrate to apex** — rejected: undermines the brief's planned subdomain-routing pattern (apex = the garden, sibling subdomains = views) and commits the apex to a speculative future "hub" role that may never materialize.
- **Deploy to `www.fernandoaires.org` during pre-launch instead of `garden.`** — rejected: `www.` carries the same public-visibility implications as the apex (GitHub Pages auto-configures the pair; search engines treat them as the same site with redirects). `www.` would not give build-up the invisibility that `garden.` provides.
- **Deploy to apex with a "coming soon" landing page; build the garden privately elsewhere** — rejected: requires maintaining a separate static page (or a Cloudflare Worker) just for the apex. More moving parts than a noindex subdomain for the same outcome.
- **Deploy to apex with Cloudflare Access / HTTP Basic Auth gating the garden** — rejected: overkill for "keep casual visitors away." The concern is accidental discovery by professional contacts, not adversarial access.
- **Use a deeper pre-launch subdomain** (e.g. `staging.garden.fernandoaires.org`, `dev.fernandoaires.org`) so even `garden.` remains pristine for launch — rejected: doubles migration work (staging → `garden.` → apex) without meaningful gain. One pre-launch subdomain is enough.
- **Skip noindex during pre-launch, rely on obscurity** — rejected: obscurity fails the moment any URL is shared in a public channel. `robots.txt` + meta robots is free insurance.
