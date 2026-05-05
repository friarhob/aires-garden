"""multilingual_404 — merge per-language 404 pages into one combined output/404.html."""
import json
from pathlib import Path

import markdown as md_lib
from pelican import signals

_article_generator = None


def _parse_page_file(path):
    """Return (metadata_dict, body_str) from a Pelican Key: Value frontmatter file."""
    with path.open(encoding="utf-8") as fh:
        lines = fh.readlines()

    metadata = {}
    body_start = len(lines)
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if not stripped:
            body_start = i + 1
            break
        if ": " in stripped:
            key, _, value = stripped.partition(": ")
            metadata[key.strip()] = value.strip()

    body = "".join(lines[body_start:])
    return metadata, body


def on_article_generator_finalized(generator):
    global _article_generator
    _article_generator = generator


def on_finalized(pelican):
    settings = pelican.settings
    content_path = Path(settings["PATH"])
    output_path = Path(settings["OUTPUT_PATH"])
    default_lang = settings.get("DEFAULT_LANG", "en")

    pages_dir = content_path / "pages"
    lang_sections = {}
    for path in sorted(pages_dir.glob("404.*.md")):
        stem = path.stem  # e.g. "404.en"
        parts = stem.split(".", 1)
        if len(parts) != 2:
            continue
        lang = parts[1]
        _metadata, body = _parse_page_file(path)
        lang_sections[lang] = md_lib.markdown(body)

    if not lang_sections:
        return

    slug_lang_map = {}
    if _article_generator is not None:
        all_articles = (
            list(getattr(_article_generator, "articles", []))
            + list(getattr(_article_generator, "translations", []))
        )
        for art in all_articles:
            slug = getattr(art, "slug", "")
            lang = getattr(art, "lang", "")
            if slug and lang:
                slug_lang_map[slug] = lang

    env = getattr(_article_generator, "env", None) if _article_generator is not None else None
    if env is None:
        return

    try:
        template = env.get_template("404.html")
    except Exception:
        return

    site_langs = _article_generator.context.get("SITE_LANGS", sorted(lang_sections.keys()))
    context = {
        "SITEURL": settings.get("SITEURL", ""),
        "SITENAME": settings.get("SITENAME", ""),
        "DEFAULT_LANG": default_lang,
        "SITE_LANGS": site_langs,
        "lang_sections": lang_sections,
        "slug_lang_map_json": json.dumps(slug_lang_map, ensure_ascii=False, separators=(",", ":")),
        "page_kind": "404",
    }

    rendered = template.render(**context)
    (output_path / "404.html").write_text(rendered, encoding="utf-8")


def register():
    signals.article_generator_finalized.connect(on_article_generator_finalized)
    signals.finalized.connect(on_finalized)
