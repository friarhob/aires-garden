"""Standalone CLI: validate frontmatter without booting Pelican.

Usage:
    python -m frontmatter_lint [content_root]

Exits 0 on a clean tree, non-zero if any file has validation errors.
Errors are printed to stderr.
"""

import sys
from collections import defaultdict
from pathlib import Path

from .body_scanner import get_body, scan as scan_body
from .schema import (
    LintError,
    format_errors,
    parse_frontmatter,
    parse_tag_prose_frontmatter,
    validate_intro,
    validate_intro_group,
    validate_page,
    validate_post,
    validate_post_group,
    validate_tag_prose,
    validate_tag_prose_group,
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
            errors.extend(scan_body(path, get_body(path)))
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
        errors.extend(scan_body(path, get_body(path)))
    return errors


def _collect_tag_prose(tag_prose_dir: Path) -> list[LintError]:
    errors: list[LintError] = []
    if not tag_prose_dir.is_dir():
        return errors

    groups: dict[Path, list[Path]] = defaultdict(list)
    for md in sorted(tag_prose_dir.rglob("*.md")):
        groups[md.parent].append(md)

    for slug_dir, files in sorted(groups.items()):
        dir_name = slug_dir.name
        for path in files:
            raw, body = parse_tag_prose_frontmatter(path)
            errors.extend(validate_tag_prose(path, raw, dir_name))
            errors.extend(scan_body(path, body))
        errors.extend(validate_tag_prose_group(dir_name, files))

    return errors


def _collect_intro(intro_dir: Path) -> list[LintError]:
    errors: list[LintError] = []
    if not intro_dir.is_dir():
        return errors

    files: list[Path] = sorted(intro_dir.rglob("*.md"))
    for path in files:
        raw = parse_frontmatter(path)
        errors.extend(validate_intro(path, raw))

    # Group only direct children for uniqueness check
    direct_files = [p for p in files if p.parent == intro_dir]
    errors.extend(validate_intro_group(direct_files))

    return errors


def main(argv: list[str] | None = None) -> None:
    args = (argv if argv is not None else sys.argv)[1:]
    content_root = Path(args[0]) if args else Path("content")

    errors = (
        _collect_posts(content_root / "posts")
        + _collect_pages(content_root / "pages")
        + _collect_tag_prose(content_root / "tag-prose")
        + _collect_intro(content_root / "intro")
    )

    if errors:
        print(format_errors(errors), file=sys.stderr)
        sys.exit(1)
