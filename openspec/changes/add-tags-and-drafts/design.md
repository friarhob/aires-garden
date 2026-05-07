## Status

Design decisions recorded below.

## Context

Item 5 of the project brief's implementation order — "tag index pages, draft handling per environment" — has been on the runway since `add-content-model` shipped. By now the foundations it depends on are in place:

- The content-model spec (`add-content-model`) accepts `Tags: list[non-empty-str]` and `Status ∈ {draft, published, hidden}` (per [ADR-0006](../../decisions/0006-status-enum.md)) but does not specify how either drives output.
- `add-i18n-rendering` ships translation grouping (`plugins/i18n_grouping/`), the dynamic `SITE_LANGS` computation, terminal-form `/<slug>/` URLs across languages, the per-language index pattern at `/<lang>/`, and a base-template scope switcher whose contract already covers tag-page contexts (cross-language pages behave like `/`, per-language pages behave like `/<lang>/`). It also ships the multilingual 404 with [ADR-0007](../../decisions/0007-small-clientside-js.md)'s small-inline-JS stance and a working `<section data-lang>` + `navigator.language` inference script.

What's missing is the rendering side of `Tags` and the deploy-environment side of `Status`. Concretely:

1. **Tag rendering.** Pelican's native tag mechanism (`TAG_URL`, `TAGS_URL`) emits cross-language tag pages and a cross-language all-tags index, but iterates `generator.articles` (default-lang only) and lists every article that carries the tag. Under our model that has two problems: it hides single-language non-default-lang posts (same issue `add-i18n-rendering` D4 already solved for `/`), and it shows visible duplicates of translated posts on the cross-language tag page. Both are inconsistent with the homepage's now-canonical "deduped translation groups" shape.

2. **Drafts.** `pelicanconf.py` does nothing with `Status: draft`, so Pelican's default kicks in: drafts go to `generator.drafts` and emit at `drafts/<slug>.html` — off the homepage, off language indexes, off (future) tag pages. From the author's perspective, hitting `/<slug>/` in dev returns 404 until they flip `Status: published`. The previewing loop is broken. `publishconf.py` blanks `DRAFT_URL`/`DRAFT_SAVE_AS` (and the LANG variants) without ADR-recorded rationale; behaviour-wise this is correct for prod (no draft files emitted) but the *why* isn't documented.

3. **Hidden articles.** [ADR-0006](../../decisions/0006-status-enum.md) added `Status: hidden` to the enum but no production change implemented it. A hidden post would default-emit at `hidden/<slug>.html`, contradicting [ADR-0004](../../decisions/0004-multilingual-post-frontmatter-conventions.md)'s terminal-form URL rule.

4. **Curated tag pages.** Some tags (e.g. `published-works`) are not noise-aggregators but curated collections. The author wants to write a paragraph or two of context above the auto-generated list. The two flavours of tag page (cross-language and per-language) carry materially different prose because the framing differs — "all my published works" vs "all my works published in &lt;lang&gt;" — and the cross-language page must localise to the reader's preferred language even though there's no `/<lang>/` prefix in the URL.

This change addresses all four. It introduces two new plugins (`tag_pages`, `dev_drafts`), a third content type (tag-prose), tightens the `Tags` lint rules in `frontmatter_lint`, edits the prod and dev configs explicitly, and reuses the existing 404 inference machinery via a Jinja partial extraction. Two new ADRs ([ADR-0008](../../decisions/0008-dev-drafts-promotion.md) for the dev-drafts toggle, [ADR-0009](../../decisions/0009-tag-prose-content-type.md) for the tag-prose content type) capture the project-level decisions; smaller in-change choices live in this file.

## Goals / Non-Goals

**Goals:**

- Every tag carrying ≥1 article emits four pages: cross-language single-tag, per-language single-tag (per language with at least one matching article), cross-language all-tags index, per-language all-tags indexes (per language).
- Cross-language tag and all-tags pages dedupe by `Translation_key` so translated posts appear once. Iteration unit and dedupe rule mirror `/` exactly.
- Per-language tag and all-tags pages list articles in that language only. Iteration unit and lang filter mirror `/<lang>/` exactly.
- Tags rendered on each article link to the in-language tag page (`/<article.lang>/tag/<tag-slug>/`) so readers stay in-language when drilling from a post.
- Drafts in dev appear *as published articles* — at `/<slug>/`, on the homepage, on language indexes, on tag pages — exactly as they will once the author flips the Status. In prod, drafts produce no output at all.
- `Status: hidden` articles emit at the terminal `/<slug>/` URL form per ADR-0004, while staying out of every listing/feed.
- Authored tag prose decorates tag pages on both axes (cross-language vs per-language scope, and reader-language localisation on the cross-language page). All combinations are independently optional; missing combos render the corresponding page list-only.
- `frontmatter_lint` catches the new failure modes the rendering would otherwise expose: empty-after-slugify tags, slug-colliding tags within one post, malformed tag-prose files.

**Non-Goals:**

- **A "tag chip" visual treatment.** Tag links on articles are minimal HTML in this change — `<a href>` inside a "Tags:" line. Visual polish (chips, colours, hover states) belongs to `add-design-tokens`.
- **Cover images, excerpts, or per-row metadata in tag-page lists.** The list templates reuse the same minimal markup as `index.html` and `lang_index.html`. Richer cards are owned by `add-design-tokens`'s gallery overhaul.
- **A consolidated authoring guide / README documenting the schemas in human-readable form.** Discussed and deferred to `add-python-cli`, whose `garden new --kind {post,page,tag-prose}` scaffold replaces most of the README's value. (See `project_authoring_guide_deferred_to_cli` memory.)
- **Translation-key linking across tag-prose languages.** Within one scope (`all` or `lang`), the per-language files conceptually translate each other, but the plugin treats them as independent bodies — no `Translation_key` field, no schema enforcement that they cover the same ground. Authors are free to author Spanish prose with no English equivalent (or vice versa). Tightening to "must match a `Translation_key`" would force an authoring symmetry that's noise-pollution for a doc type that's already optional.
- **Tag synonyms or canonical-tag normalisation.** `Tags: poetry` and `Tags: poems` slugify differently and produce two separate tag pages. No "canonical tag" / "tag alias" concept. Authors are responsible for tag hygiene; if it bites, address with a future change.
- **A `/feeds/tag/<slug>.atom.xml` per tag.** Pelican's `TAG_FEED_ATOM` could be wired up but the audience for per-tag RSS on a personal garden is approximately zero. Rejected unless asked for.
- **`add-curated-tag-prose` as a separate proposal.** Tag prose is bundled here per the "right-shape over scope-trim" reasoning recorded during proposal iteration.

## Decisions

### D1: Two new plugins, not one combined "tags-and-drafts" package

`plugins/tag_pages/` and `plugins/dev_drafts/` ship as separate Pelican plugins, paralleling the `i18n_grouping` / `multilingual_404` split from `add-i18n-rendering` (D1).

`tag_pages` runs in `finalized` (after `i18n_grouping` has populated `TRANSLATION_GROUPS` and `SITE_LANGS` on the article generator's context) and reads articles + translations to emit four artefacts plus tag-prose decorations. `dev_drafts` runs at `article_generator_pretaxonomy` (or earliest available pre-finalised hook — verified during implementation) and mutates `generator.drafts`/`generator.drafts_translations` into `generator.articles`/`generator.translations` *before* `i18n_grouping` runs its grouping pass. Their lifecycles don't overlap; their consumers don't overlap; failure isolation is real (a `tag_pages` bug can't break draft promotion or vice versa).

**Alternatives rejected:**

- **One combined `tags_and_drafts` plugin.** Reads cleaner under one name in `PLUGINS`, but conflates two unrelated lifecycles: drafts-promotion is a one-shot mutation pre-grouping; tag emission is rendering work post-grouping. Forcing one signal hook to handle both means either the draft work runs too late (drafts are already in the wrong list) or the tag work runs too early (groups not yet computed).
- **Bundled with `i18n_grouping`.** Conflates concerns the i18n change deliberately kept separate; future readers of either would have to skim past unrelated code.

### D2: `dev_drafts` toggled by a settings flag (`DRAFTS_AS_PUBLISHED`), not env var or two-plugin trick

The `dev_drafts` plugin is registered unconditionally in `pelicanconf.py`. It runs only when `pelican.settings.get("DRAFTS_AS_PUBLISHED")` is truthy. `pelicanconf.py` sets `DRAFTS_AS_PUBLISHED = True`; `publishconf.py` overrides to `False`. Recorded as [ADR-0008](../../decisions/0008-dev-drafts-promotion.md).

The mechanism mirrors how `SITEURL` already differs across configs — settings live in pelicanconf as the dev default, publishconf overrides for prod. No new pattern.

**Alternatives rejected:**

- **Env var `DEV_BUILD=1`.** Out-of-band signal; doesn't survive `make build` invocations from CI without extra plumbing; conflates "is dev" with "what does dev-mode mean," which is the toggle's only real purpose.
- **Two plugins (`dev_drafts_on`, `dev_drafts_off`) with PLUGINS edits in each config.** Splits responsibility across two files for behaviour that's a single binary toggle. Plugins should encode capabilities, not policy.
- **Template-level draft handling.** Have `index.html` iterate `generator.articles + generator.drafts` in dev. Spreads draft awareness into every list template, multiplies as templates grow.

### D3: `tag_pages` consumes `i18n_grouping`'s context, doesn't re-group

`i18n_grouping` already builds `TRANSLATION_GROUPS: dict[translation_key, list[Article]]` and `SITE_LANGS: list[str]` on the article generator's context (and reproduces it via `generator.context["HOMEPAGE_GROUPS"]`). `tag_pages` reads these directly rather than re-grouping articles by translation_key.

This couples the two plugins by load order — `tag_pages.register()` must run after `i18n_grouping.register()` and `tag_pages` must hook into a signal that fires after `article_generator_finalized`. We rely on Pelican's `PLUGINS` list ordering (`i18n_grouping` is registered first in `pelicanconf.py`) and use `finalized` (the latest signal in the build) for `tag_pages`'s emission pass — same hook `i18n_grouping` itself uses for emitting `lang_index.html`. By that point the context is fully populated.

**Alternatives rejected:**

- **Re-group inside `tag_pages`.** Doubles the grouping pass. Cheap in isolation but the duplication invites drift if either plugin's grouping rules diverge from the other's later.
- **Move the grouping logic into a shared `plugins/_lib/` module.** Premature abstraction. With one consumer beyond `i18n_grouping`, the simplest reuse path is "read the result from the context the producer already populated." If a third consumer arrives, *then* extract.

### D4: Cross-language tag page = "homepage filtered by tag" (group iteration, deduped by `Translation_key`)

`/tag/<slug>/` is conceptually `/` filtered to translation groups carrying the tag on at least one of their articles. Iteration unit is the group, not the article. Card markup mirrors `index.html`: title, date, language badges. Card link goes to the group's preferred article (default-lang if available, else alphabetically-first by lang) — same rule `i18n_grouping` already uses for `HOMEPAGE_GROUPS`.

The tag-membership predicate is "any article in the group carries the tag (after slugify)." This means a translation that carries the tag in only one language still surfaces the whole group on the cross-language tag page. Acceptable: the cross-language page is a discovery surface ("posts that touch this topic, in any language"), not a strict "all translations of this tag" filter — and tags don't translate (no `Translation_key`-equivalent), so any stricter rule would either over-exclude (require all langs to carry the tag) or be incoherent.

**Alternatives rejected:**

- **List every article that carries the tag.** Cheap iteration, no group lookup needed, but emits visible duplicates (`hello-garden` + `ola-jardim` as two separate cards). Already rejected during proposal iteration.
- **Predicate "all articles in the group carry the tag."** Over-restrictive; a translation that drops a tag for length reasons would un-list the whole group from `/tag/<slug>/`.

### D5: Per-language tag page = "lang index filtered by tag" (article iteration)

`/<lang>/tag/<slug>/` is conceptually `/<lang>/` filtered to articles whose `Lang == <lang>` AND whose `Tags` (after slugify) include `<slug>`. Iteration unit is the article. Markup mirrors `lang_index.html`.

Generated dynamically from `(Lang, Tag-slug)` pairs across all articles, so adding a French post tagged `poesia` auto-creates `/fr/tag/poesia/` with no config edit. Same pattern as `i18n_grouping` D2 (dynamic union of langs, no static `KNOWN_LANGS`).

### D6: All-tags indexes at `/tags/` and `/<lang>/tags/`, not just per-language

Symmetry: the homepage at `/` has a tag-filtered counterpart at `/tag/<slug>/`, and the all-tags index `/tags/` is to `/` what `/<lang>/tags/` is to `/<lang>/`. Cross-language `/tags/` lists every tag-slug appearing anywhere on the site; per-language `/<lang>/tags/` lists every tag-slug with at least one article in `<lang>`.

Both reuse one template (`tags_list.html`) parameterised by `page_lang` — when `page_lang` is set, the listing is scoped to that language; when unset, it's the union.

**Alternative rejected:**

- **Only per-language all-tags indexes.** Asymmetric with the single-tag pages (where we ship both forms). Cheap to add the cross-language form for completeness, and there's no design tension.

### D7: Tag-input strictness in `frontmatter_lint`: reject, don't silently dedupe

Two new lint rules on the existing `Tags` field, both **rejected on failure** rather than silently normalised:

1. **Each tag must produce a non-empty slug under Pelican's `slugify`.** Guards against `Tags: [!!!]` or whitespace-only entries that would emit `/tag//`.
2. **No two tags within one post may produce the same slug.** Guards against `Tags: [Rant, rant]` rendering as duplicates and double-counting in tag-page lists.

Both are strict rejections. The user-facing alternative — silently deduping on slug — is the more permissive path Pelican's defaults take, but it's inconsistent with the rest of `frontmatter_lint`'s posture (unknown fields are rejected, malformed dates are rejected, region-suffixed langs are rejected). Following the same posture: surface the author's mistake, name the rule that failed, let them fix it.

The "tag must be ≥3 chars to avoid lang collision" idea raised during proposal iteration was dropped — the `/tag/` and `/<lang>/` URL prefixes already segregate the namespaces, so no real collision exists.

These rules tighten an existing field rather than introducing a project-level pattern; rationale lives here, not as an ADR.

**Alternatives rejected:**

- **Silent normalisation (slug-dedupe in the renderer, drop empty-slug tags).** Hides the author's error; the post's intent is ambiguous (`Tags: [Rant, rant]` — did they mean two distinct tags? a typo? a copy-paste?). Refusing to guess matches every other strict-by-default schema rule.
- **Warn-only on collision.** Pelican's plugin signal handlers don't have a clean warning channel; either the build aborts or it doesn't. Hybrid "warn but proceed" needs a mechanism we don't have, and exists nowhere else in the codebase.

### D8: Tag-prose as a third content type, not page-with-marker

A new content tree at `content/tag-prose/` sits alongside `content/posts/` and `content/pages/`. Files there don't go through Pelican's article or page generators — they're discovered and rendered by `tag_pages` directly. Recorded as [ADR-0009](../../decisions/0009-tag-prose-content-type.md).

The alternative was reusing the page schema with a `Page_kind: tag-prose` marker, scanning `generator.pages` and `generator.hidden_pages` for that marker. Rejected because:

- It overloads the page schema with a sub-type concept the page mental model doesn't otherwise carry. Future content kinds (notes, snippets, …) would each need their own marker, and the page schema becomes a discriminated union.
- It forces tag-prose URL emission to be suppressed (set `Save_as: ""`), which is an implementation hack rather than a design.
- The lifecycle is wrong: tag-prose is consumed by `tag_pages`, not rendered to its own URL. Treating it as a page with one foot pulled out muddles the contract.

A clean third content type with its own tiny schema, its own discovery pass in the consuming plugin, and no Pelican generator involvement is the simpler model. The ADR records this so future content-kind proposals have precedent.

### D9: Tag-prose file layout — subdirectory per slug, `<scope>.<lang>.md` files

```
content/tag-prose/<slug>/
  all.<lang>.md     → cross-language prose (one per reader-language we want to localise to)
  lang.<lang>.md    → per-language prose for /<lang>/tag/<slug>/
```

Slug is inferred from the directory name (mirrors the post pattern, where `Translation_key` = parent directory). `<scope>` is one of `all` or `lang`; the `all` token mirrors the scope switcher's "All" entry from `add-i18n-rendering` D6 and the `lang` token names what the file is for.

**Alternatives rejected:**

- **Two parallel top-level dirs (`content/tag-prose-cross/`, `content/tag-prose-lang/`).** Flatter at top level but two directories for one logical concept; less symmetric with the post pattern.
- **Filename infix (`<slug>.all.<lang>.md`, `<slug>.<lang>.md`).** Flat dir; parser has to handle two forms with implicit "lang is the default scope" magic. Adding more scopes later (e.g. `summary.<lang>.md`) means re-deciding the default. Avoid.
- **Subdir per slug with per-scope subdirs (`<slug>/all/<lang>.md`, `<slug>/lang/<lang>.md`).** One more level of nesting; gains nothing over scope-prefixed filenames at one fewer level.

### D10: Cross-language tag prose reuses the 404 language-inference script via a Jinja partial

When `content/tag-prose/<slug>/` carries 2+ `all.<lang>.md` files, `/tag/<slug>/` renders each as `<section data-lang="<lang>">…</section>` and embeds the same inline language-inference script the multilingual 404 already uses. ADR-0007's three bars (static-host necessity, graceful degradation, inline and small) are all met — same JS, same stance.

The script lived inline inside `themes/garden/templates/404.html`. We extract it into a shared partial, `themes/garden/templates/_lang_inference_script.html`, and have both `404.html` and the new `tag_group_index.html` `{% include %}` it. Pure refactor: same emitted JS, same behaviour. Jinja includes are textual, so ADR-0007's "inline" bar is preserved.

When only one `all.<lang>.md` exists, no `<section>` wrapper is emitted (just the body) and no JS — the page is unambiguously single-language. When zero exist, list-only with no prose.

### D11: Per-language tag prose: no inference, no JS

`/<lang>/tag/<slug>/` already declares the language in the URL. Rendering reads only `lang.<lang>.md` (matched on the URL's lang segment) and embeds its body directly above the list. No `<section>` machinery, no JS, no fallback to `all.<lang>.md`.

The two scopes are *separate authored content*. Falling back from `lang.<lang>.md` (missing) to `all.<lang>.md` would render cross-language framing on a per-language page — exactly the wrong message. Better to render list-only.

### D12: Native Pelican tag mechanism disabled

`pelicanconf.py` sets `TAG_URL = ""`, `TAG_SAVE_AS = ""`, `TAGS_URL = ""`, `TAGS_SAVE_AS = ""` so Pelican emits no tag pages or all-tags index. The plugin emits the four flavours we want; native and ours would otherwise both write to `/tag/<slug>/` and the last writer wins (or worse — the build errors).

**Alternative rejected:**

- **Override the native templates and let Pelican drive emission.** Pelican's tag iteration is `generator.articles` (default-lang only) and doesn't dedupe by `Translation_key`. Bending it to our shape is more code than disabling it and writing four small generators ourselves.

### D13: Hidden articles at terminal URL form

`pelicanconf.py` sets `HIDDEN_ARTICLE_URL = "{slug}/"`, `HIDDEN_ARTICLE_SAVE_AS = "{slug}/index.html"`, and the same for `HIDDEN_ARTICLE_LANG_URL` / `HIDDEN_ARTICLE_LANG_SAVE_AS`. Mirrors the four `ARTICLE_*` settings from `add-i18n-rendering` D3.

Hidden articles don't appear in `generator.articles` (they're in `generator.hidden_articles`), so they're naturally absent from homepage, lang indexes, tag pages, and feeds. Only their URL form changes. Per ADR-0004's terminal-form rule, `/<slug>/` is the right form regardless of status.

### D14: Tag-prose `Status` field constrained to `hidden`

The tag-prose schema requires `Status` and constrains its value to `hidden` only. `draft` and `published` are valid values for the `Status` enum (per ADR-0006) but neither is meaningful for a content type that's never directly addressable.

The alternative is to drop the field from the tag-prose schema entirely. We keep it for two reasons: (1) symmetry with posts and pages, where every Markdown content file carries a `Status`, makes the schema feel like a coherent extension of an existing pattern; (2) if a future change ever wants to allow tag-prose to be "drafted" (for example, authoring a tag-prose body in dev that isn't yet ready for prod tag pages), the field is already there to extend the constraint.

`frontmatter_lint` rejects any other `Status` value on a tag-prose file with an error naming `hidden` as the only allowed value.

### D15: Plugin signal ordering — `dev_drafts` before `i18n_grouping` before `tag_pages`

Three plugins now need a defined order:

1. `dev_drafts` mutates `generator.drafts` → `generator.articles` (when `DRAFTS_AS_PUBLISHED`). Must run before any plugin that reads `generator.articles`. Connect to `article_generator_pretaxonomy` (the earliest article-generator hook that exposes both lists).
2. `i18n_grouping` reads `generator.articles + generator.translations`, computes `TRANSLATION_GROUPS` and `SITE_LANGS`. Connects to `article_generator_finalized` (existing).
3. `tag_pages` reads everything `i18n_grouping` populated, plus walks `content/tag-prose/`. Emits four artefact families. Connect to `finalized` (latest hook in the build, after templates are wired up).

`pelicanconf.py`'s `PLUGINS` list is ordered `[frontmatter_lint, i18n_grouping, multilingual_404, dev_drafts, tag_pages]`. Pelican respects PLUGINS order for `register()` calls but signal dispatch order across plugins isn't guaranteed by registration order alone — they share a hook only if they connect to the *same* signal. Since the three above use different signals (`pretaxonomy` < `finalized` (article-generator) < `finalized` (top-level)), Pelican's natural build sequence guarantees the order without further tricks.

If a future change adds a plugin that hooks `article_generator_pretaxonomy` alongside `dev_drafts`, signal-priority kwargs (`signals.foo.connect(handler, sender=None, weak=False)`) become relevant. Not needed today.

### D16: Markdown rendering for tag prose uses `markdown.markdown(...)` directly, not Pelican's reader

Tag-prose bodies are rendered to HTML by calling `markdown.markdown(body, extensions=[...])` inline in the `tag_pages` plugin. The `markdown` library is already a project dependency (declared in `pyproject.toml`).

**Alternatives rejected:**

- **Pelican's article reader.** Tag-prose files aren't articles; pretending they are means setting up bogus frontmatter (Date, Slug, Translation_key) and then suppressing URL emission. More moving parts for the same result.
- **Pelican's page reader.** Same shape problem; pages do have a simpler schema but they still emit URLs that we'd have to suppress.
- **Defer Markdown extensions.** We use just stock CommonMark (no fenced-code-with-syntax-highlighting, no footnote plugin, etc.) for now. If tag prose ever needs richer Markdown, add extensions to the `markdown.markdown` call — the code path is one line.

The rendered HTML is passed to Jinja with `| safe` so the template doesn't double-escape. This is consistent with how the multilingual 404 plugin already renders its sections.

## Risks / Trade-offs

- **[Plugin ordering bug if signal hooks change]** → If a future Pelican version reshuffles signal ordering, `dev_drafts` could run after `i18n_grouping`, leaving drafts ungrouped. Mitigation: pin Pelican to the current minor range in `pyproject.toml` (already in place: `pelican >= 4.10, < 5`). Add a defensive assertion in `dev_drafts` that `generator.drafts` is non-empty when called and `generator.articles` doesn't yet contain any draft-status items — fail loudly if invariants drift.

- **[Tag visibility shifts between dev and prod]** → A tag that appears only on draft posts will surface in dev (its `/tag/<slug>/` and `/<lang>/tag/<slug>/` exist) but disappear from prod (drafts excluded → tag has zero articles → tag pages aren't generated). Accepted: that's the desired behaviour — drafts are private; their tags shouldn't leak. Authors who want a tag visible in prod must publish at least one tagged article.

- **[Pelican `slugify` version drift]** → If the Python runtime's `Pelican.utils.slugify` algorithm changes between versions, all tag URLs change. Mitigation: pin Pelican range in `pyproject.toml`; verify slug output during apply for known fixture inputs (`Rant` → `rant`, `Published Works` → `published-works`).

- **[Cross-lang tag prose with N=1 looks like a broken multilingual page]** → If only `all.en.md` exists and a Portuguese reader visits `/tag/<slug>/`, they see English prose with no language toggle. Accepted: single-section pages render the body directly (no `<section data-lang>` wrapper) — visually indistinguishable from non-localised prose. The author's choice to provide only one lang is honoured. JS-off readers see the same thing.

- **[Author writes tag-prose for a tag no article carries]** → File exists at `content/tag-prose/orphan/all.en.md` but no article carries `Tags: orphan`. The tag page is never generated (no source articles → no tag URL), so the prose is silently invisible. Mitigation: `frontmatter_lint` checks tag-prose directories against the union of slugs from articles' Tags and warns (not errors) if a directory has no carriers — author can act on the warning. Defer this check unless authoring flow shows it's needed; for the seed content (`published-works`) we'll author the article and the prose together.

- **[Tag-prose schema diverges from page schema over time]** → ADR-0009 establishes tag-prose as its own type. If both schemas evolve in similar directions (e.g. both grow a `Hero_image` field), code duplication accumulates. Trade-off accepted: convergence-via-extraction is cheaper than divergence-from-a-shared-base-that-doesn't-fit. Revisit if a third content type (notes, snippets) appears and the divergence pattern clarifies.

- **[Tag pages on the homepage have no editorial curation]** → Auto-generation means every tag with any article gets a page. A throwaway tag (`misc`, `wip`) gets the same treatment as `published-works`. Accepted: the cost is small (a generated page that few link to), and adding curation gates would mean either an explicit allowlist or a "tag-prose-required" flag — both contradict the "tags are free-form, prose is optional" model.

- **[`make build` performance under many tags]** → Each tag emits four pages plus zero/one prose Markdown render. With ~10 tags and 2 langs, that's ~40 rendered HTML files per build — well within Pelican's noise floor. Revisit if total tag count crosses ~100 (unlikely on a personal garden).
