## MODIFIED Requirements

### Requirement: Makefile exposes dev, devbuild, and build targets

The `Makefile` SHALL expose exactly the three targets needed for local development and production builds so later changes own the CLI surface explicitly.

#### Scenario: `make dev` serves the site locally
- **WHEN** a developer runs `make dev`
- **THEN** Pelican starts with autoreload and listens on `http://localhost:8000`.

#### Scenario: `make devbuild` produces a one-shot dev build
- **WHEN** a developer runs `make devbuild`
- **THEN** Pelican runs against `pelicanconf.py` (drafts promoted, `SITEURL` unset) and writes static files to `output/`, then exits.

#### Scenario: `make build` produces production output
- **WHEN** a developer runs `make build`
- **THEN** Pelican runs against `publishconf.py` and writes static files to `output/`.

#### Scenario: Future CLI targets are absent
- **WHEN** the `Makefile` is inspected
- **THEN** it does NOT define `new`, `translate`, `lint`, or `publish` (these are owned by `add-python-cli`).
