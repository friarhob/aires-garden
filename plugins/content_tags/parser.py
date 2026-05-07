"""Shared embed-tag parsing utilities used by both the renderer and the lint scanner."""

import re
from collections.abc import Iterator

EMBED_RE = re.compile(
    r'^[ ]{0,3}'
    r'\[!'
    r'([a-z][a-z0-9_-]*)'
    r'((?:\s+[a-z][a-z0-9_-]*=(?:[^\s\]"]+|"(?:[^"\\\\]|\\\\.)*"))*)'
    r'\s*\]'
    r'[ ]*$'
)

MALFORMED_RE = re.compile(r'^[ ]{0,3}\[!')

_FENCE_RE = re.compile(r'^[ ]{0,3}(`{3,}|~{3,})')
_ARG_RE = re.compile(r'([a-z][a-z0-9_-]*)=((?:[^\s\]"]+)|(?:"(?:[^"\\\\]|\\\\.)*"))')


def iter_candidate_lines(source: str) -> Iterator[tuple[int, str]]:
    """Yield (1-based lineno, line) skipping lines inside fenced/indented code blocks."""
    in_fence = False
    fence_char = ''
    fence_len = 0

    for lineno, line in enumerate(source.splitlines(), 1):
        stripped = line.rstrip()

        if in_fence:
            close_re = re.compile(rf'^[ ]{{0,3}}{re.escape(fence_char)}{{{fence_len},}}[ ]*$')
            if close_re.match(stripped):
                in_fence = False
            continue

        m = _FENCE_RE.match(stripped)
        if m:
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            in_fence = True
            continue

        # Skip 4-space and tab-indented code block lines
        if line.startswith('    ') or line.startswith('\t'):
            continue

        yield lineno, line


def parse_args(args_str: str) -> dict[str, str]:
    """Parse 'key=value key2="quoted value"' substring into a dict."""
    result = {}
    for m in _ARG_RE.finditer(args_str):
        key = m.group(1)
        val = m.group(2)
        if val.startswith('"'):
            val = val[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        result[key] = val
    return result
