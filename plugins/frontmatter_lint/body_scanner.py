"""Content-body scanner: validates embed tags in Markdown post/page bodies.

Imports the embed registry from content_tags so lint and renderer share
a single source of truth for valid tag names and argument schemas.
"""

import difflib
from pathlib import Path

from frontmatter_lint.schema import LintError
from content_tags.parser import EMBED_RE, MALFORMED_RE, iter_candidate_lines, parse_args
from content_tags.registry import REGISTRY


def get_body(path: Path) -> str:
    """Return the Markdown body of a file (everything after the frontmatter)."""
    with path.open(encoding='utf-8') as f:
        lines = f.read().splitlines()
    i = 0
    while i < len(lines) and lines[i].strip():
        i += 1
    while i < len(lines) and not lines[i].strip():
        i += 1
    return '\n'.join(lines[i:])


def scan(file_path: Path, body: str) -> list[LintError]:
    """Return lint errors for embed tags in the given body text."""
    errors: list[LintError] = []
    registered_names = list(REGISTRY.keys())

    for lineno, line in iter_candidate_lines(body):
        m = EMBED_RE.match(line)
        if m:
            name = m.group(1)
            args_str = m.group(2)

            if name not in REGISTRY:
                suggestion = difflib.get_close_matches(name, registered_names, n=1, cutoff=0.6)
                hint = f' (did you mean: {suggestion[0]!r}?)' if suggestion else ''
                errors.append(LintError(
                    path=file_path,
                    message=f'line {lineno}: [content-tags] unknown tag {name!r}{hint}',
                ))
                continue

            tag = REGISTRY[name]
            args = parse_args(args_str)
            allowed = set(tag.required_args) | set(tag.optional_args)

            for req in tag.required_args:
                if req not in args:
                    errors.append(LintError(
                        path=file_path,
                        message=f'line {lineno}: [content-tags] {name!r} missing required argument {req!r}',
                    ))

            for key in args:
                if key not in allowed:
                    errors.append(LintError(
                        path=file_path,
                        message=(
                            f'line {lineno}: [content-tags] {name!r} unknown argument {key!r}'
                            f' (allowed: {", ".join(sorted(allowed))})'
                        ),
                    ))
            continue

        if MALFORMED_RE.match(line):
            errors.append(LintError(
                path=file_path,
                message=f'line {lineno}: [content-tags] malformed embed tag',
            ))

    return errors
