## 1. Build-side artifacts (static files + 404 page)

- [x] 1.1 Create `content/extra/CNAME` containing exactly `garden.fernandoaires.org` (single line, no scheme, no path).
- [x] 1.2 Create `content/extra/robots.txt` containing `User-agent: *` and `Disallow: /`.
- [x] 1.3 Create `content/pages/404.md` with frontmatter `Title: Not found`, `Status: hidden`, `Save_as: 404.html`, `URL: 404.html`, and a short themed body.
- [x] 1.4 Extend `pelicanconf.py` with `STATIC_PATHS = ["extra/CNAME", "extra/robots.txt"]` and `EXTRA_PATH_METADATA` mapping each to its root path (`CNAME`, `robots.txt`).
- [x] 1.5 Update `publishconf.py` so `SITEURL = "https://garden.fernandoaires.org"`.
- [x] 1.6 Add `<meta name="robots" content="noindex, nofollow">` to `themes/garden/templates/base.html` inside `<head>`.
- [x] 1.7 Run `make build` locally; verify `output/CNAME`, `output/robots.txt`, `output/404.html`, and the noindex meta on any article page.

## 2. GitHub Actions workflow

- [x] 2.1 Create `.github/workflows/deploy.yml` with `on: push: branches: [main]` and `on: workflow_dispatch: {}`.
- [x] 2.2 Set `permissions: { contents: read, pages: write, id-token: write }` at workflow level.
- [x] 2.3 Set `concurrency: { group: pages, cancel-in-progress: true }`.
- [x] 2.4 Single job `build-and-deploy` on `ubuntu-latest` with steps: checkout, setup-python@v5 (`python-version: "3.12"`), `pip install -e .`, `make build`, `actions/upload-pages-artifact@v3` (path `./output`), `actions/deploy-pages@v4`.
- [x] 2.5 Add `environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }` to the job so the Pages deploy target is explicit.
- [x] 2.6 Lint the YAML locally (`python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"` or similar) before committing.

## 3. DNS (Gandi)

- [x] 3.1 In Gandi's DNS Records UI for `fernandoaires.org`, add a record: type `CNAME`, name `garden`, value `friarhob.github.io.` (trailing dot), default TTL. Per [ADR-0005](../../decisions/0005-dns-stays-on-gandi.md), DNS stays at Gandi.
- [x] 3.2 Verify resolution: `dig +short CNAME garden.fernandoaires.org` returns `friarhob.github.io.`.

## 4. Pre-flip review and repo visibility flip

- [x] 4.1 Grep commit history for potential secrets: `git log -p | grep -Ei "password|secret|token|api[_-]?key"`; manually review any hits.
- [x] 4.2 Confirm no private personal info is in commit messages or tracked files.
- [x] 4.3 Confirm `.gitignore` already excludes `.claude/`, editor configs, and machine-local tool state.
- [x] 4.4 Confirm the author is OK with `ola-jardim.pt.md` being publicly visible (already published; sanity check).
- [x] 4.5 Commit and push the workflow + build-side changes to `main` while the repo is still private (workflow won't run for Pages because Pages isn't configured yet — the build step will run but the deploy step will fail harmlessly until Pages is on).
- [x] 4.6 Flip visibility: `gh repo edit friarhob/aires-garden --visibility public --accept-visibility-change-consequences`.
- [x] 4.7 Verify: `gh repo view friarhob/aires-garden --json visibility` returns `"visibility":"PUBLIC"`.

## 5. Enable GitHub Pages

- [x] 5.1 In repo Settings → Pages, set source to **GitHub Actions**.
- [x] 5.2 Set custom domain to `garden.fernandoaires.org`.
- [x] 5.3 Wait for GitHub Pages to verify DNS; "Enforce HTTPS" should become enablable.
- [x] 5.4 Enable "Enforce HTTPS" once the Let's Encrypt cert is provisioned (may take minutes to ~24h).

## 6. First deploy

- [x] 6.1 Trigger a deploy: either push a trivial commit to `main` or use `gh workflow run deploy.yml`.
- [x] 6.2 Watch the Actions run to green: `gh run watch` on the latest run.
- [x] 6.3 Fetch `https://garden.fernandoaires.org/` and confirm the index page renders with the noindex meta tag.
- [x] 6.4 Fetch `https://garden.fernandoaires.org/robots.txt` and confirm `Disallow: /`.
- [x] 6.5 Fetch `https://garden.fernandoaires.org/ola-jardim-pt.html` and confirm the first post renders. (Pelican-default URL for non-default-lang articles. ADR-0004's terminal form `/ola-jardim/` requires a translation-grouping plugin scoped to the future `add-i18n-rendering` change.)
- [x] 6.6 Fetch `https://garden.fernandoaires.org/does-not-exist/` and confirm the custom 404 page renders (not GitHub's default).

## 7. Verification against specs

- [x] 7.1 Run `openspec validate add-deploy-pipeline`; expect zero errors.
- [x] 7.2 Walk each scenario in `specs/deploy-pipeline/spec.md` and confirm the live site / repo state satisfies it.
- [x] 7.3 Confirm the apex (`fernandoaires.org`) still resolves to nothing web-facing (`curl -I https://fernandoaires.org/` returns connection error or a non-GH response).
