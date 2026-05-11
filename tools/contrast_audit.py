#!/usr/bin/env python3
"""WCAG AA colour contrast audit for aires-garden.

Usage:
    python tools/contrast_audit.py [path/to/styles.css]

Parses token values from the stylesheet and evaluates every in-use colour pair
in both light and dark modes against WCAG AA thresholds:
  4.5:1  — normal body text  (WCAG 2.1 SC 1.4.3)
  3.0:1  — large/heading text and non-text contrast (WCAG 2.1 SC 1.4.3 / 1.4.11)

If no CSS path is supplied, defaults to themes/garden/static/css/styles.css
relative to the repo root.

References:
  WCAG 2.1 SC 1.4.3 — Contrast (Minimum): https://www.w3.org/TR/WCAG21/#contrast-minimum
  WCAG 2.1 SC 1.4.11 — Non-text Contrast:  https://www.w3.org/TR/WCAG21/#non-text-contrast
  Relative luminance formula:               https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
"""
import math
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# WCAG maths
# ---------------------------------------------------------------------------

def _linearise(c: float) -> float:
    if c <= 0.04045:
        return c / 12.92
    return math.pow((c + 0.055) / 1.055, 2.4)


def luminance(hex_colour: str) -> float:
    """WCAG relative luminance for a 6-digit hex colour (e.g. '#2A1640')."""
    h = hex_colour.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * _linearise(r) + 0.7152 * _linearise(g) + 0.0722 * _linearise(b)


def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = luminance(fg), luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------------------
# CSS parser — extracts token blocks from the stylesheet
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r'(--[\w-]+)\s*:\s*(#[0-9A-Fa-f]{3,8})\s*;')


def _strip_comments(css: str) -> str:
    return re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)


def _find_block(css: str, selector_pattern: str) -> str:
    """Return the braced block content for the first match of selector_pattern.

    Searches for `{` starting from m.start() (not m.end()) so that patterns
    which include `{` in their text still locate the correct opening brace.
    """
    m = re.search(selector_pattern, css)
    if not m:
        return ''
    start = css.index('{', m.start())
    depth, i = 0, start
    while i < len(css):
        if css[i] == '{':
            depth += 1
        elif css[i] == '}':
            depth -= 1
            if depth == 0:
                return css[start + 1:i]
        i += 1
    return ''


def _tokens_from_block(block: str) -> dict:
    return {m.group(1): m.group(2).upper() for m in _TOKEN_RE.finditer(block)}


def parse_tokens(css_path: Path) -> tuple[dict, dict]:
    """Return (light_tokens, dark_tokens) dicts parsed from css_path."""
    css = _strip_comments(css_path.read_text())

    # Light tokens: bare :root block (pre-dedupe) or grouped :root, :root[...] block (post-dedupe).
    # Pattern matches `:root {` or `:root,` at the start of a line but NOT `:root:not(` or `:root[`.
    light_block = _find_block(css, r'(?m)^\s*:root\s*[,{]')
    light = _tokens_from_block(light_block)

    # Dark tokens: inside the @media block (innermost :root selector inside it)
    media_block = _find_block(css, r'@media\s*\(\s*prefers-color-scheme\s*:\s*dark\s*\)')
    dark_block = _find_block(media_block, r':root')
    dark = _tokens_from_block(dark_block)

    if not light:
        sys.exit(f'error: no light tokens found in {css_path}')
    if not dark:
        sys.exit(f'error: no dark tokens found in {css_path}')

    return light, dark


# ---------------------------------------------------------------------------
# In-scope colour pairs
#
# This list is the project's maintained WCAG audit registry. It covers every
# colour pair that actually appears on a rendered page — not the Cartesian
# product of all tokens, only combinations that real elements use.
#
# WCAG does not prescribe which pairs to audit; that depends on the design.
# Rule of thumb: if a new component introduces a colour combination not listed
# here, add a row before merging. Use threshold 4.5 for normal-weight body
# text (<18px regular, <14px bold) and 3.0 for large text, bold headings, and
# non-text contrast elements (meaningful borders, focus rings, icons).
#
# Format: (fg_token, bg_token, threshold, human-readable role)
# ---------------------------------------------------------------------------

PAIRS = [
    # Body surface — foreground tokens on the main page background
    ('--text',               '--bg',        4.5, 'body text'),
    ('--text-muted',         '--bg',        4.5, 'muted body text'),
    ('--text-heading',       '--bg',        3.0, 'heading (large text)'),
    ('--accent',             '--bg',        4.5, 'link / accent text'),

    # Subtle surface — foreground tokens on admonition / panel backgrounds
    ('--text',               '--bg-subtle', 4.5, 'body text on subtle bg'),
    ('--text-muted',         '--bg-subtle', 4.5, 'muted text on subtle bg'),
    ('--accent',             '--bg-subtle', 4.5, 'link inside admonition'),

    # Tag-chip hover: bg-coloured label text on accent-coloured chip
    ('--bg',                 '--accent',    4.5, 'tag-chip hover (bg on accent)'),

    # Admonition title text and left border (large/bold → 3:1 threshold)
    ('--admonition-note',    '--bg-subtle', 3.0, 'admonition-note title / border'),
    ('--admonition-tip',     '--bg-subtle', 3.0, 'admonition-tip title / border'),
    ('--admonition-warning', '--bg-subtle', 3.0, 'admonition-warning title / border'),
    ('--admonition-danger',  '--bg-subtle', 3.0, 'admonition-danger title / border'),
]


# ---------------------------------------------------------------------------
# Audit runner
# ---------------------------------------------------------------------------

def audit(tokens: dict, mode_name: str) -> int:
    print(f'\n### {mode_name}')
    col_p, col_r, col_t = 44, 7, 9
    header = f'{"Pair":<{col_p}}  {"Ratio":>{col_r}}  {"Threshold":>{col_t}}  Result  Role'
    print(header)
    print('-' * len(header))
    failures = 0
    for fg_tok, bg_tok, threshold, role in PAIRS:
        if fg_tok not in tokens or bg_tok not in tokens:
            print(f'{"SKIP":<{col_p}}  {fg_tok} / {bg_tok}  (token absent in this mode)')
            continue
        ratio = contrast_ratio(tokens[fg_tok], tokens[bg_tok])
        passed = ratio >= threshold
        if not passed:
            failures += 1
        status = 'PASS' if passed else 'FAIL !'
        pair = f'{fg_tok} / {bg_tok}'
        print(f'{pair:<{col_p}}  {ratio:>{col_r}.2f}  {threshold:>{col_t}.1f}  {status}  {role}')
    print()
    if failures:
        print(f'  {failures} failing pair(s).')
    else:
        print('  All pairs pass.')
    return failures


def main() -> None:
    if len(sys.argv) > 1:
        css_path = Path(sys.argv[1])
    else:
        # Resolve relative to repo root (parent of tools/)
        css_path = Path(__file__).parent.parent / 'themes' / 'garden' / 'static' / 'css' / 'styles.css'

    if not css_path.exists():
        sys.exit(f'error: stylesheet not found: {css_path}')

    light, dark = parse_tokens(css_path)

    print('# aires-garden — WCAG AA colour contrast audit')
    print(f'# Stylesheet: {css_path}')
    print('# Thresholds: 4.5:1 normal body text / 3.0:1 large text & non-text')

    total = audit(light, 'Light mode')
    total += audit(dark, 'Dark mode')
    print(f'\n### Grand total: {total} failure(s)')


if __name__ == '__main__':
    main()
