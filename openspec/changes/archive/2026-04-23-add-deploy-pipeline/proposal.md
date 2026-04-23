## Why

The scaffolded site only builds locally; nothing is published. The garden needs an automated path from `git push` to a live URL so every later change (content model, i18n, theme, CLI) is validated against a real deployment instead of a dev server. ADR-0003 has already fixed the hostname strategy (pre-launch `garden.fernandoaires.org`, terminal apex `fernandoaires.org`, noindex posture in-repo), so the deploy mechanics are the only piece still missing.

## What Changes

- Add a GitHub Actions workflow that builds Pelican and publishes to GitHub Pages on every push to `main` (plus manual dispatch).
- Add a `CNAME` file at repo root pointing at `garden.fernandoaires.org` and wire `STATIC_PATHS` so it ships to `output/`.
- Add a `content/pages/404.md` that renders to `output/404.html` (GitHub Pages serves this on unknown paths).
- Add a `robots.txt` static file with `User-agent: * / Disallow: /` per ADR-0003's pre-launch noindex posture.
- Add `<meta name="robots" content="noindex, nofollow">` to the theme's `base.html` (second noindex layer per ADR-0003).
- Add a DNS record in Cloudflare: `CNAME garden → friarhob.github.io` (proxied or DNS-only; ADR-0003 allows either).
- Flip the GitHub repository from private to public (required for GitHub Pages on the free plan; ADR-0003 and the `site-build` spec anticipate this flip happening here).
- Enable GitHub Pages with "GitHub Actions" as the source and set the custom domain to `garden.fernandoaires.org`.
- Update `publishconf.py` so `SITEURL = "https://garden.fernandoaires.org"`.

**NOT in scope** (deferred to the future `launch-to-apex` change per ADR-0003): removing noindex, switching the Pages custom domain to the apex, adding apex A/AAAA records, Cloudflare Redirect Rule for `garden.*` → apex, Cloudflare Transform Rule for `X-Robots-Tag`.

## Capabilities

### New Capabilities

- `deploy-pipeline`: Automated build-and-publish from `main` to GitHub Pages, including the GH Pages custom-domain wiring, the DNS record, the pre-launch noindex layers, and the 404 page. Owns every artifact whose existence is motivated by "the site is deployed," not "the site is built."

### Modified Capabilities

None. `site-build` already anticipates that visibility is flipped "in a later change"; this is that change, but the flip does not alter any `site-build` requirement.

## Impact

- **New files:** `.github/workflows/deploy.yml`, `CNAME`, `content/pages/404.md`, `content/extra/robots.txt` (or similar; `STATIC_PATHS` handles placement).
- **Modified files:** `pelicanconf.py` (extend `STATIC_PATHS` / `EXTRA_PATH_METADATA` so `CNAME` and `robots.txt` land at `output/` root), `publishconf.py` (`SITEURL`), `themes/garden/templates/base.html` (noindex meta).
- **External systems:** Cloudflare DNS (one CNAME record), GitHub repository settings (visibility, Pages source, custom domain).
- **Dependencies:** No new Python dependencies. Adds reliance on GitHub Actions runners (`ubuntu-latest`) and two official actions (`actions/upload-pages-artifact`, `actions/deploy-pages`).
- **Reversibility:** All changes are reversible while the site has no readers, per ADR-0003's "switching hostnames is cheap while the site has no readers" framing.
