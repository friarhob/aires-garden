"""Pelican plugin: custom embed-tag preprocessor + Markdown extensions."""

import content_tags.embeds  # noqa: F401 — registers youtube + iframe in REGISTRY

from content_tags.markdown_extensions.captions import FigureCaptionExtension
from content_tags.markdown_extensions.embed_tags import EmbedTagsExtension

from pelican import signals


def _on_initialized(pelican: object) -> None:
    md = pelican.settings.setdefault('MARKDOWN', {})  # type: ignore[attr-defined]
    exts: list = md.setdefault('extensions', [])
    if not any(isinstance(e, FigureCaptionExtension) for e in exts):
        exts.append(FigureCaptionExtension())
    if not any(isinstance(e, EmbedTagsExtension) for e in exts):
        exts.append(EmbedTagsExtension())


def register() -> None:
    signals.initialized.connect(_on_initialized)
