"""Pelican plugin: validates frontmatter for all posts and pages at build time.

Walks the filesystem directly (same logic as the CLI) so files Pelican skips
due to an invalid status are still caught. Aborts via all_generators_finalized
before any HTML output is written.
"""

import sys
from collections import defaultdict
from pathlib import Path

from pelican import signals

from .body_scanner import get_body, scan as scan_body
from .schema import (
    format_errors,
    parse_frontmatter,
    parse_tag_prose_frontmatter,
    validate_page,
    validate_post,
    validate_post_group,
    validate_tag_prose,
    validate_tag_prose_group,
)

_errors: list = []
_content_path: Path | None = None


def on_article_generator_finalized(generator: object) -> None:
    global _content_path
    _content_path = Path(getattr(generator, "settings", {}).get("PATH", "content"))
    posts_dir = _content_path / "posts"
    if not posts_dir.is_dir():
        return

    groups: dict[Path, list[tuple[Path, dict[str, object]]]] = defaultdict(list)
    for md in sorted(posts_dir.rglob("*.md")):
        raw = parse_frontmatter(md)
        dir_name = md.parent.name
        _errors.extend(validate_post(md, raw, dir_name))
        _errors.extend(scan_body(md, get_body(md)))
        groups[md.parent].append((md, raw))

    for group_dir, files in sorted(groups.items()):
        _errors.extend(validate_post_group(group_dir.name, files))


def on_page_generator_finalized(generator: object) -> None:
    content_root = Path(getattr(generator, "settings", {}).get("PATH", "content"))
    pages_dir = content_root / "pages"
    if not pages_dir.is_dir():
        return
    for md in sorted(pages_dir.glob("*.md")):
        raw = parse_frontmatter(md)
        _errors.extend(validate_page(md, raw))
        _errors.extend(scan_body(md, get_body(md)))

    tag_prose_dir = content_root / "tag-prose"
    if not tag_prose_dir.is_dir():
        return
    from collections import defaultdict as _defaultdict
    slug_dirs: dict[Path, list[Path]] = _defaultdict(list)
    for md in sorted(tag_prose_dir.rglob("*.md")):
        slug_dirs[md.parent].append(md)
    for slug_dir, files in sorted(slug_dirs.items()):
        dir_name = slug_dir.name
        for path in files:
            raw, body = parse_tag_prose_frontmatter(path)
            _errors.extend(validate_tag_prose(path, raw, dir_name))
            _errors.extend(scan_body(path, body))
        _errors.extend(validate_tag_prose_group(dir_name, files))


def on_all_generators_finalized(generators: object) -> None:
    if _errors:
        print("\nfrontmatter_lint: validation failed\n", file=sys.stderr)
        print(format_errors(_errors), file=sys.stderr)
        sys.exit(1)


def register() -> None:
    signals.article_generator_finalized.connect(on_article_generator_finalized)
    signals.page_generator_finalized.connect(on_page_generator_finalized)
    signals.all_generators_finalized.connect(on_all_generators_finalized)
