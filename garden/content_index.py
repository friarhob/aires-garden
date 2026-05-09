from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from garden.frontmatter_io import read_frontmatter


@dataclass
class ContentFile:
    path: Path
    kind: str           # "post" | "page" | "tag-prose"
    slug: str
    lang: str
    translation_key: str
    status: str


def _infer_kind(path: Path, content_root: Path) -> str:
    rel = path.relative_to(content_root)
    parts = rel.parts
    if parts[0] == "posts":
        return "post"
    if parts[0] == "pages":
        return "page"
    return "tag-prose"


def walk_content(content_root: Path) -> list[ContentFile]:
    records: list[ContentFile] = []
    for md in sorted(content_root.rglob("*.md")):
        try:
            fields, _ = read_frontmatter(md)
        except Exception:
            continue
        slug = fields.get("Slug", "")
        lang = fields.get("Lang", "")
        if not slug or not lang:
            continue
        kind = _infer_kind(md, content_root)
        records.append(
            ContentFile(
                path=md,
                kind=kind,
                slug=slug,
                lang=lang,
                translation_key=fields.get("Translation_key", slug),
                status=fields.get("Status", ""),
            )
        )
    return records


def find_by_slug(index: list[ContentFile], slug: str) -> ContentFile | None:
    for cf in index:
        if cf.slug == slug:
            return cf
    return None


def find_translations(index: list[ContentFile], translation_key: str) -> list[ContentFile]:
    return [cf for cf in index if cf.translation_key == translation_key]
