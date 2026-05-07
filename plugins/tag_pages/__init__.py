"""tag_pages — per-language and cross-language tag index pages plus all-tags indexes.

Page layout:
  output/<lang>/tag/<tag-slug>/index.html   — per-language tag index
  output/<lang>/tags/index.html             — per-language all-tags list
  output/tag/<tag-slug>/index.html          — cross-language tag index
  output/tags/index.html                    — cross-language all-tags list

Depends on i18n_grouping having populated TRANSLATION_GROUPS, SITE_LANGS,
and HOMEPAGE_GROUPS in generator.context before on_finalized fires.
Signal registration order: tag_pages is listed after i18n_grouping in PLUGINS.
"""
from pathlib import Path

import markdown

from pelican import signals
from pelican.settings import DEFAULT_CONFIG
from pelican.utils import slugify as _pelican_slugify

from frontmatter_lint.schema import parse_tag_prose_frontmatter

_article_generator = None
_SLUG_REGEX_SUBS = DEFAULT_CONFIG["SLUG_REGEX_SUBSTITUTIONS"]


def _tag_slug(tag_name: str) -> str:
    return _pelican_slugify(tag_name, _SLUG_REGEX_SUBS)


# ---------------------------------------------------------------------------
# Signal handlers
# ---------------------------------------------------------------------------

def on_article_generator_finalized(generator):
    global _article_generator
    _article_generator = generator


def on_finalized(pelican):
    if _article_generator is None:
        return

    generator = _article_generator
    output_path = Path(pelican.settings["OUTPUT_PATH"])
    content_path = Path(pelican.settings["PATH"])
    env = generator.env
    default_lang = pelican.settings.get("DEFAULT_LANG", "en")

    base_ctx = {
        **generator.context,
        "SITEURL": pelican.settings.get("SITEURL", ""),
        "SITENAME": pelican.settings.get("SITENAME", ""),
        "DEFAULT_LANG": default_lang,
    }
    # Remove keys that templates define themselves
    base_ctx.pop("articles", None)

    # Collect all articles (published articles + translations)
    all_articles = (
        list(getattr(generator, "articles", []))
        + list(getattr(generator, "translations", []))
    )

    # --- Task 5.1 / 5.2: discover and render tag prose ---
    tag_prose = _discover_tag_prose(content_path)

    # --- Task 3.x: per-language tag pages ---
    lang_tag_map = _build_lang_tag_map(all_articles)
    _render_lang_tag_pages(env, output_path, base_ctx, lang_tag_map, tag_prose)
    _render_lang_tags_list(env, output_path, base_ctx, lang_tag_map)

    # --- Task 4.x: cross-language tag pages ---
    translation_groups = generator.context.get("TRANSLATION_GROUPS", {})
    cross_tag_map = _build_cross_tag_map(translation_groups, default_lang)
    _render_cross_tag_pages(env, output_path, base_ctx, cross_tag_map, tag_prose)
    _render_cross_tags_list(env, output_path, base_ctx, cross_tag_map)


# ---------------------------------------------------------------------------
# Per-language helpers (tasks 3.x)
# ---------------------------------------------------------------------------

def _build_lang_tag_map(articles: list) -> dict:
    """dict[(lang, tag_slug), list[Article]] — sorted by Date descending."""
    result: dict[tuple[str, str], list] = {}
    for art in articles:
        lang = getattr(art, "lang", "") or ""
        tags = getattr(art, "tags", []) or []
        for tag in tags:
            key = (lang, _tag_slug(tag.name))
            result.setdefault(key, []).append(art)
    for key in result:
        result[key].sort(key=lambda a: getattr(a, "date", None), reverse=True)
    return result


def _render_lang_tag_pages(env, output_path, base_ctx, lang_tag_map, tag_prose):
    try:
        template = env.get_template("tag_lang_index.html")
    except Exception:
        return
    for (lang, slug), articles in sorted(lang_tag_map.items()):
        prose_html = tag_prose.get(slug, {}).get("lang", {}).get(lang)
        out_dir = output_path / lang / "tag" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        rendered = template.render(
            **base_ctx,
            articles=articles,
            page_lang=lang,
            tag_slug=slug,
            tag_prose_html=prose_html,
            page_kind="tag_lang_index",
        )
        (out_dir / "index.html").write_text(rendered, encoding="utf-8")


def _render_lang_tags_list(env, output_path, base_ctx, lang_tag_map):
    try:
        template = env.get_template("tags_list.html")
    except Exception:
        return
    # dict[lang, list[slug]] sorted alphabetically
    lang_slugs: dict[str, set] = {}
    for (lang, slug) in lang_tag_map:
        lang_slugs.setdefault(lang, set()).add(slug)
    for lang, slugs in sorted(lang_slugs.items()):
        out_dir = output_path / lang / "tags"
        out_dir.mkdir(parents=True, exist_ok=True)
        rendered = template.render(
            **base_ctx,
            tag_slugs=sorted(slugs),
            page_lang=lang,
            page_kind="lang_tags_list",
        )
        (out_dir / "index.html").write_text(rendered, encoding="utf-8")


# ---------------------------------------------------------------------------
# Cross-language helpers (tasks 4.x)
# ---------------------------------------------------------------------------

def _build_cross_tag_map(translation_groups: dict, default_lang: str) -> dict:
    """dict[tag_slug, list[group_dict]] — sorted by canonical article Date desc."""
    result: dict[str, list] = {}
    for _key, group_articles in translation_groups.items():
        # A group is a list of Article objects sharing a Translation_key.
        # Find canonical: prefer default_lang, else alphabetically first by lang.
        canonical = next(
            (a for a in group_articles if getattr(a, "lang", "") == default_lang),
            min(group_articles, key=lambda a: getattr(a, "lang", ""), default=None),
        )
        if canonical is None:
            continue

        group_tags: set[str] = set()
        for art in group_articles:
            for tag in getattr(art, "tags", []) or []:
                group_tags.add(_tag_slug(tag.name))

        group_dict = {
            "canonical": canonical,
            "translations": group_articles,
        }
        for slug in group_tags:
            result.setdefault(slug, []).append(group_dict)

    for slug in result:
        result[slug].sort(
            key=lambda g: getattr(g["canonical"], "date", None),
            reverse=True,
        )
    return result


def _render_cross_tag_pages(env, output_path, base_ctx, cross_tag_map, tag_prose):
    try:
        template = env.get_template("tag_group_index.html")
    except Exception:
        return
    for slug, groups in sorted(cross_tag_map.items()):
        all_prose = tag_prose.get(slug, {}).get("all", {})
        out_dir = output_path / "tag" / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        rendered = template.render(
            **base_ctx,
            groups=groups,
            tag_slug=slug,
            all_prose=all_prose,
            page_kind="tag_group_index",
        )
        (out_dir / "index.html").write_text(rendered, encoding="utf-8")


def _render_cross_tags_list(env, output_path, base_ctx, cross_tag_map):
    try:
        template = env.get_template("tags_list.html")
    except Exception:
        return
    all_slugs = sorted(cross_tag_map.keys())
    out_dir = output_path / "tags"
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered = template.render(
        **base_ctx,
        tag_slugs=all_slugs,
        page_kind="all_tags_list",
    )
    (out_dir / "index.html").write_text(rendered, encoding="utf-8")


# ---------------------------------------------------------------------------
# Tag-prose discovery (tasks 5.x)
# ---------------------------------------------------------------------------

def _discover_tag_prose(content_path: Path) -> dict:
    """Walk content/tag-prose/ and return:
    dict[tag_slug, dict[scope, dict[lang, html]]]
    where scope ∈ {"all", "lang"}.
    """
    tag_prose_dir = content_path / "tag-prose"
    result: dict[str, dict[str, dict[str, str]]] = {}

    if not tag_prose_dir.is_dir():
        return result

    for slug_dir in sorted(tag_prose_dir.iterdir()):
        if not slug_dir.is_dir():
            continue
        slug = slug_dir.name
        for md_path in sorted(slug_dir.glob("*.md")):
            stem = md_path.stem
            parts = stem.rsplit(".", 1)
            if len(parts) != 2:
                continue
            scope, lang = parts
            if scope not in ("all", "lang"):
                continue
            raw, body = parse_tag_prose_frontmatter(md_path)
            html = markdown.markdown(body)
            result.setdefault(slug, {}).setdefault(scope, {})[lang] = html

    return result


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def register():
    signals.article_generator_finalized.connect(on_article_generator_finalized)
    signals.finalized.connect(on_finalized)
