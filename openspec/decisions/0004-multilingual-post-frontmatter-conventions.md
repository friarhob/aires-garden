# ADR-0004: Multilingual post frontmatter conventions

## Status

Accepted — 2026-04-20.

## Context

The project will publish posts in multiple languages (`en`, `pt`, `es`, `fr`, extensible per the project brief). Three questions about frontmatter conventions have to be answered before the first multilingual post ships, and before `add-content-model` introduces `frontmatter_lint` to enforce anything:

1. Should each language's URL reflect that language (localized slugs) or share one slug across all translations?
2. If slugs can diverge, what stable identifier links the translations?
3. What format does the `Lang:` field take?

Pelican's native translation support links files by matching `Slug:` across `Lang:` values. That only works if slugs are identical in every language — which forces non-default-language URLs into a language-tagged shape (`/hello-garden-pt.html` or `/pt/hello-garden/`) and keeps the slug itself in one privileged language. The project's brief introduces a `translation_key` field precisely to break that constraint, but never specifies how to *form* the field, and does not resolve an implicit contradiction with the brief's repo-layout sketch (`<slug>/<slug>.<lang>.md`, which implicitly assumes a single slug per post).

The brief also lists `Lang:` values as `en`, `pt`, `es`, `fr` but does not standardize whether regional variants (`pt-br`, `pt-pt`) are permitted — a choice that affects accessibility (`<html lang="...">`), screen-reader pronunciation, and the RSS `<language>` tag.

The reader-experience goal, stated by the author, is that opening any post shows links to its available translations in a clearly-placed UI element. Both "homogenous slug" and "localized slug" models can deliver that UI; the axis on which they differ is URL structure, not feature support.

## Decision

Four rules govern multilingual post frontmatter:

1. **`Slug:` is localized per language.** The Portuguese version of a post gets a Portuguese slug; the English version gets an English slug. URLs read native in every language — a Portuguese post lives at `/ola-jardim/`, its English translation at `/hello-garden/`.
2. **`Translation_key:` = the slug of the first-written language version, held stable across all later translations.** The key is never retroactively changed once set. If Portuguese is the first language a post is written in, the PT slug becomes the `translation_key`; any later EN/ES/FR version carries the same key even though its own `Slug:` differs.
3. **Directory name = `translation_key`; filenames = `<slug>.<lang>.md`.** One folder per translated-post-group; all translations co-locate in the same directory alongside an optional `images/` sibling. Example:
   ```
   content/posts/ola-jardim/
   ├── ola-jardim.pt.md          # Slug: ola-jardim, Lang: pt
   ├── hello-garden.en.md        # Slug: hello-garden, Lang: en
   └── images/
   ```
   This resolves the brief's repo-layout sketch in favor of localized slugs: the stable directory anchor is the `translation_key`, not any one language's slug.
4. **`Lang:` format = ISO 639-1 two-letter codes** (`en`, `pt`, `es`, `fr`), extensible to more languages as authored. Lowercase, no region suffix. Values MUST be valid as an HTML `lang` attribute (`<html lang="pt">`).

## Consequences

- URLs read native in every language — a Portuguese reader never lands on `/hello-garden-pt.html`; an English reader never lands on `/ola-jardim/`.
- `Translation_key` is stable, grepable, and survives any slug rename to any one variant. A post's identity across translations is language-independent.
- Directory-per-post-group keeps translations co-located; shared media in `images/` is referenced consistently across all language variants.
- The brief's latent contradiction (localized slugs implied by `translation_key` vs. same-slug repo-layout sketch) is resolved; the repo layout is adjusted to match rule 3.
- `Lang:` values remain simple and work directly as HTML `lang` attributes and RSS `<language>` tags without mapping.
- No regional variants can be signaled under rule 4. If the author ever writes a post whose Brazilian or European Portuguese variant matters to signal explicitly, a future ADR supersedes rule 4 to permit BCP 47 region suffixes.
- Pelican's native translation-linking (slug-matching) does not apply under rule 1 — a small plugin is required to group articles by `Translation_key:` and populate `article.translations` for Jinja templates. That plugin belongs in the future `add-i18n-rendering` change, alongside the language switcher and "Available in:" badges, which are already planned in the brief's proposal order. The incremental cost of rule 1 is therefore folded into work that was already scoped.
- `add-content-model`'s future `frontmatter_lint` plugin has a concrete target: enforce that (a) `Slug:` values are unique per `Lang:` within a directory, (b) `Translation_key:` is identical across every file in a directory and matches the directory name, (c) `Lang:` matches `^[a-z]{2}$`.

Alternatives considered:

- **Same slug across all languages (Pelican native, no `translation_key`)** — rejected: non-default-language URLs acquire a language tag in the URL (`/hello-garden-pt.html` or `/pt/hello-garden/`), privileging one language in URL-space. The translation-links UI feature the author wants is achievable under this model too (zero-code via `article.translations`), so the simplicity argument is real — but the URL-aesthetic cost was judged larger than the plugin cost, given that the plugin fits inside an already-planned proposal (`add-i18n-rendering`).
- **Opaque `translation_key` (UUID or timestamp)** — rejected: loses grep/git readability for no gain. A first-written slug is already unique in practice and human-meaningful.
- **`translation_key` always = English slug, even when EN wasn't written first** — rejected: privileges English as an anchor language, inconsistent with the brief's language-neutral stance. Also awkward when the English version doesn't exist yet (as with the first post).
- **Directory name = one arbitrary language's slug, not the translation_key** — rejected: ties the directory anchor to a specific language, making the "which file is canonical" question non-obvious. Using `translation_key` as the directory name keeps the anchor language-independent.
- **Per-post canonical language via a `Primary_lang:` field** — rejected: adds another field and another plugin to decide which translation gets the clean `/slug/` URL. Localized slugs make every translation's URL equally clean, so the `Primary_lang:` mechanism is unnecessary.
- **`Lang:` with mandatory region suffix (BCP 47 full, e.g. `pt-br`)** — rejected: this garden is personal expression, not geo-targeting. Forcing a regional choice adds per-post friction for signal nobody currently wants.
- **`Lang:` with optional region suffix (BCP 47, region-optional)** — rejected: two formats in circulation means lint has to accept both, authors drift between them, and grep across the content set becomes noisy. One format is cleaner; if regions become necessary, bulk-update via supersession.
- **Human-readable `Lang:` values (`Portuguese`, `English`)** — rejected: breaks HTML `lang` attribute compatibility, breaks RSS `<language>` tag, harder to lint, more prone to typos.
