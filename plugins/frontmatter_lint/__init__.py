"""Pelican plugin: validates frontmatter for all posts and pages at build time.

Walks the filesystem directly (same logic as the CLI) so files Pelican skips
due to an invalid status are still caught. Aborts via all_generators_finalized
before any HTML output is written.
"""

import sys
from collections import defaultdict
from pathlib import Path

from pelican import signals

from .schema import (
    format_errors,
    parse_frontmatter,
    validate_page,
    validate_post,
    validate_post_group,
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


def on_all_generators_finalized(generators: object) -> None:
    if _errors:
        print("\nfrontmatter_lint: validation failed\n", file=sys.stderr)
        print(format_errors(_errors), file=sys.stderr)
        sys.exit(1)


def register() -> None:
    signals.article_generator_finalized.connect(on_article_generator_finalized)
    signals.page_generator_finalized.connect(on_page_generator_finalized)
    signals.all_generators_finalized.connect(on_all_generators_finalized)
