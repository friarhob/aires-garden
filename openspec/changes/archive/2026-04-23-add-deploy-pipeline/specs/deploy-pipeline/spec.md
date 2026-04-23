## ADDED Requirements

### Requirement: Push to `main` publishes the site to GitHub Pages

The repository SHALL contain a GitHub Actions workflow that, on every push to `main`, builds the Pelican site against `publishconf.py` and deploys the output to GitHub Pages. A manual trigger SHALL also exist so a deploy can be re-run without a commit.

#### Scenario: Workflow triggers on push to main
- **WHEN** a commit lands on the `main` branch
- **THEN** `.github/workflows/deploy.yml` runs automatically, builds `output/`, and deploys it to GitHub Pages.

#### Scenario: Workflow can be manually re-run
- **WHEN** a maintainer clicks "Run workflow" on the Actions UI
- **THEN** the same build-and-deploy job executes without requiring a new commit.

#### Scenario: Concurrent deploys are serialized
- **WHEN** two pushes arrive in quick succession
- **THEN** the workflow's concurrency group cancels the older in-flight deploy in favor of the newer one, so the live site reflects the latest commit.

#### Scenario: Workflow uses least privilege
- **WHEN** `.github/workflows/deploy.yml` is inspected
- **THEN** its `permissions:` block grants only `contents: read`, `pages: write`, and `id-token: write`.

### Requirement: The site is served at the pre-launch subdomain

GitHub Pages SHALL serve the site at `https://garden.fernandoaires.org`. The apex domain `fernandoaires.org` remains unconfigured for web during pre-launch, per ADR-0003.

#### Scenario: CNAME file pins the custom domain
- **WHEN** the built output is inspected
- **THEN** `output/CNAME` contains exactly the hostname `garden.fernandoaires.org` (no scheme, no path).

#### Scenario: DNS resolves the subdomain to GitHub Pages
- **WHEN** `garden.fernandoaires.org` is resolved
- **THEN** it points (via CNAME) to `friarhob.github.io`.

#### Scenario: Production SITEURL matches the live hostname
- **WHEN** `publishconf.py` is imported
- **THEN** `SITEURL == "https://garden.fernandoaires.org"`.

### Requirement: Pre-launch noindex posture ships in two layers

Per ADR-0003, the site SHALL serve two independent noindex signals during pre-launch so search engines and well-behaved crawlers do not index the build-up state.

#### Scenario: robots.txt disallows all user-agents
- **WHEN** `https://garden.fernandoaires.org/robots.txt` is fetched
- **THEN** the response body contains `User-agent: *` and `Disallow: /`.

#### Scenario: Every rendered page carries a noindex meta tag
- **WHEN** any HTML page produced by `make build` is inspected
- **THEN** its `<head>` contains `<meta name="robots" content="noindex, nofollow">`.

#### Scenario: Noindex removal is gated on a future change
- **WHEN** the `launch-to-apex` change is not yet applied
- **THEN** both noindex layers remain active; neither is removed in isolation.

### Requirement: Unknown paths render a custom 404 page

The build SHALL produce an `output/404.html` so GitHub Pages serves a themed error page instead of its default.

#### Scenario: 404 source exists under content/pages
- **WHEN** `content/pages/404.md` is inspected
- **THEN** it carries frontmatter with `status: hidden` (so it doesn't appear in indexes) and renders through the same base template as articles.

#### Scenario: Build output includes 404.html at the root
- **WHEN** `make build` finishes
- **THEN** `output/404.html` exists and is a full HTML document (not a fragment).

### Requirement: Repository is public and GitHub Pages is enabled

GitHub Pages on the free plan requires a public repository. The `aires-garden` repository SHALL be public, and Pages SHALL be configured to deploy from GitHub Actions with the custom domain set to the pre-launch subdomain.

#### Scenario: Repository visibility is public
- **WHEN** `gh repo view friarhob/aires-garden --json visibility` is inspected
- **THEN** visibility is `PUBLIC`.

#### Scenario: Pages source is GitHub Actions
- **WHEN** the Pages settings are inspected
- **THEN** the build-and-deploy source is "GitHub Actions" (not "Deploy from a branch").

#### Scenario: Pages custom domain matches the CNAME file
- **WHEN** the Pages settings are inspected
- **THEN** the custom domain is `garden.fernandoaires.org`, matching `output/CNAME`.

### Requirement: Deploy workflow pins build environment

The workflow SHALL pin Python and action versions so a green deploy today reproduces tomorrow.

#### Scenario: Python version is pinned to the project baseline
- **WHEN** `.github/workflows/deploy.yml` is inspected
- **THEN** it uses `actions/setup-python` with `python-version: "3.12"`, matching `pyproject.toml`.

#### Scenario: Pages actions are pinned to major versions
- **WHEN** `.github/workflows/deploy.yml` is inspected
- **THEN** it uses `actions/upload-pages-artifact@v3` and `actions/deploy-pages@v4`.

#### Scenario: Dependencies install from pyproject.toml
- **WHEN** the workflow's install step runs
- **THEN** it runs `pip install -e .` (or equivalent) so the same dependency set used locally is used in CI.

### Requirement: `launch-to-apex` is the documented path out of pre-launch

Leaving the pre-launch posture SHALL require a single future change named `launch-to-apex`, per ADR-0003. This change does NOT itself perform that cutover.

#### Scenario: Noindex removal is not attempted here
- **WHEN** this change's diff is reviewed
- **THEN** `robots.txt` and the meta-robots tag remain in place — neither is removed or neutered. (Per [ADR-0005](../../../decisions/0005-dns-stays-on-gandi.md), the originally-optional edge `X-Robots-Tag` layer from ADR-0003 is dropped entirely.)

#### Scenario: Apex DNS is not configured here
- **WHEN** DNS is inspected after this change applies
- **THEN** no A/AAAA record for the apex points at GitHub Pages; the apex remains unconfigured for web.
