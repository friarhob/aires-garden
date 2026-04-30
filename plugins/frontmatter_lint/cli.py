"""Standalone CLI: validate frontmatter without booting Pelican.

Usage:
    python -m frontmatter_lint [content_root]

Exits 0 on a clean tree, non-zero if any file has validation errors.
Errors are printed to stderr.
"""

import sys
from collections import defaultdict
from pathlib import Path

from .schema import (
    LintError,
    format_errors,
    parse_frontmatter,
    validate_page,
    validate_post,
    validate_post_group,
)


def _collect_posts(posts_dir: Path) -> list[LintError]:
    errors: list[LintError] = []
    if not posts_dir.is_dir():
        return errors

    # Group *.md files by immediate parent directory
    groups: dict[Path, list[Path]] = defaultdict(list)
    for md in sorted(posts_dir.rglob("*.md")):
        groups[md.parent].append(md)

    for group_dir, files in sorted(groups.items()):
        dir_name = group_dir.name
        raw_list: list[tuple[Path, dict[str, object]]] = []
        for path in files:
            raw = parse_frontmatter(path)
            errors.extend(validate_post(path, raw, dir_name))
            raw_list.append((path, raw))
        errors.extend(validate_post_group(dir_name, raw_list))

    return errors


def _collect_pages(pages_dir: Path) -> list[LintError]:
    errors: list[LintError] = []
    if not pages_dir.is_dir():
        return errors
    for path in sorted(pages_dir.glob("*.md")):
        raw = parse_frontmatter(path)
        errors.extend(validate_page(path, raw))
    return errors


def main(argv: list[str] | None = None) -> None:
    args = (argv if argv is not None else sys.argv)[1:]
    content_root = Path(args[0]) if args else Path("content")

    errors = _collect_posts(content_root / "posts") + _collect_pages(content_root / "pages")

    if errors:
        print(format_errors(errors), file=sys.stderr)
        sys.exit(1)
