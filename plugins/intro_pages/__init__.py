"""intro_pages — expose INTRO_ALL and INTRO_LANG dicts to Pelican templates.

Reads content/intro/ at build time:
  INTRO_ALL  — {lang: rendered_html} from all.<lang>.md files
  INTRO_LANG — {lang: rendered_html} from lang.<lang>.md files
"""
from pathlib import Path

import markdown as md_lib
from pelican import signals


def _parse_intro_file(path: Path) -> tuple[dict, str]:
    """Return (metadata_dict, body_str) from a Pelican-style frontmatter file."""
    with path.open(encoding="utf-8") as fh:
        lines = fh.readlines()

    metadata: dict = {}
    body_start = len(lines)
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if not stripped:
            body_start = i + 1
            break
        if ": " in stripped:
            key, _, value = stripped.partition(": ")
            metadata[key.strip()] = value.strip()

    return metadata, "".join(lines[body_start:])


def _render_markdown(body: str, md_settings: dict) -> str:
    return md_lib.markdown(
        body,
        extensions=md_settings.get("extensions", []),
        extension_configs=md_settings.get("extension_configs", {}),
        output_format=md_settings.get("output_format", "html5"),
    )


def on_article_generator_finalized(generator) -> None:
    settings = generator.settings
    content_path = Path(settings["PATH"])
    md_settings = settings.get("MARKDOWN", {})
    intro_dir = content_path / "intro"

    intro_all: dict[str, str] = {}
    intro_lang: dict[str, str] = {}

    if intro_dir.is_dir():
        for path in sorted(intro_dir.glob("*.md")):
            stem = path.stem  # e.g. "all.en" or "lang.pt"
            parts = stem.rsplit(".", 1)
            if len(parts) != 2:
                continue
            scope, lang = parts
            _metadata, body = _parse_intro_file(path)
            rendered = _render_markdown(body, md_settings)
            if scope == "all":
                intro_all[lang] = rendered
            elif scope == "lang":
                intro_lang[lang] = rendered

    generator.context["INTRO_ALL"] = intro_all
    generator.context["INTRO_LANG"] = intro_lang


def register() -> None:
    signals.article_generator_finalized.connect(on_article_generator_finalized)
