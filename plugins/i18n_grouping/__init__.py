"""i18n_grouping — group articles by Translation_key and generate per-language indexes."""
from pathlib import Path

from pelican import signals

_article_generator = None


def _translation_key(article):
    return getattr(article, "translation_key", "") or ""


def _all_articles(generator):
    return list(getattr(generator, "articles", [])) + list(getattr(generator, "translations", []))


def on_article_generator_finalized(generator):
    global _article_generator
    _article_generator = generator

    articles = _all_articles(generator)
    default_lang = generator.settings.get("DEFAULT_LANG", "en")

    groups = {}
    for art in articles:
        key = _translation_key(art)
        if not key:
            continue
        groups.setdefault(key, []).append(art)

    for key in groups:
        groups[key].sort(key=lambda a: getattr(a, "lang", ""))

    for art in articles:
        key = _translation_key(art)
        art.translation_group = groups.get(key, [art])

    generator.context["TRANSLATION_GROUPS"] = groups

    homepage_groups = []
    for _key, group in sorted(groups.items()):
        canonical = next(
            (a for a in group if getattr(a, "lang", "") == default_lang),
            group[0],
        )
        homepage_groups.append({"canonical": canonical, "translations": group})
    homepage_groups.sort(key=lambda g: getattr(g["canonical"], "date", None), reverse=True)
    generator.context["HOMEPAGE_GROUPS"] = homepage_groups


def on_all_generators_finalized(generators):
    """Compute SITE_LANGS from the union of articles + pages (including hidden)."""
    article_generator = next((g for g in generators if hasattr(g, "articles")), None)
    page_generator = next(
        (g for g in generators if hasattr(g, "pages") and hasattr(g, "hidden_pages")),
        None,
    )

    langs = set()

    if article_generator:
        for art in _all_articles(article_generator):
            lang = getattr(art, "lang", "")
            if lang:
                langs.add(lang)

    if page_generator:
        all_pages = (
            list(getattr(page_generator, "pages", []))
            + list(getattr(page_generator, "hidden_pages", []))
            + list(getattr(page_generator, "translations", []))
            + list(getattr(page_generator, "hidden_translations", []))
        )
        for page in all_pages:
            lang = getattr(page, "lang", "")
            if lang:
                langs.add(lang)

    site_langs = sorted(langs)

    # All generators share the same context dict.
    if article_generator:
        article_generator.context["SITE_LANGS"] = site_langs


def _select_for_lang(articles, lang):
    matching = [a for a in articles if getattr(a, "lang", "") == lang]
    matching.sort(key=lambda a: getattr(a, "date", None), reverse=True)
    return matching


def on_finalized(pelican):
    if _article_generator is None:
        return

    site_langs = _article_generator.context.get("SITE_LANGS", [])
    if not site_langs:
        return

    articles = _all_articles(_article_generator)
    output_path = Path(pelican.settings["OUTPUT_PATH"])
    env = _article_generator.env
    try:
        template = env.get_template("lang_index.html")
    except Exception:
        return

    base_context = {
        **_article_generator.context,
        "SITEURL": pelican.settings.get("SITEURL", ""),
        "SITENAME": pelican.settings.get("SITENAME", ""),
        "DEFAULT_LANG": pelican.settings.get("DEFAULT_LANG", "en"),
    }
    base_context.pop("articles", None)

    for lang in site_langs:
        articles_for_lang = _select_for_lang(articles, lang)
        out_dir = output_path / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        rendered = template.render(
            **base_context,
            page_lang=lang,
            articles=articles_for_lang,
            page_kind="lang_index",
        )
        (out_dir / "index.html").write_text(rendered, encoding="utf-8")


def register():
    signals.article_generator_finalized.connect(on_article_generator_finalized)
    signals.all_generators_finalized.connect(on_all_generators_finalized)
    signals.finalized.connect(on_finalized)
