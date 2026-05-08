"""Tests for frontmatter_lint body_scanner — embed tag validation."""

from pathlib import Path

import pytest

import content_tags.embeds  # noqa: F401 — populate registry
from frontmatter_lint.body_scanner import scan


FAKE_PATH = Path('content/posts/test/test.en.md')


def _scan(body: str):
    return scan(FAKE_PATH, body)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_youtube_passes():
    errors = _scan('[!youtube id="dQw4w9WgXcQ"]')
    assert errors == []


def test_valid_youtube_with_start_passes():
    errors = _scan('[!youtube id="abc" start="42"]')
    assert errors == []


def test_valid_iframe_passes():
    errors = _scan('[!iframe src="https://example.com" title="Demo"]')
    assert errors == []


def test_normal_text_passes():
    errors = _scan('Hello world\n\nSome paragraph.')
    assert errors == []


def test_embed_inside_fenced_code_passes():
    body = '```\n[!youtube id="abc"]\n```'
    errors = _scan(body)
    assert errors == []


def test_embed_inside_indented_code_passes():
    body = '    [!youtube id="abc"]'
    errors = _scan(body)
    assert errors == []


# ---------------------------------------------------------------------------
# Unknown tag
# ---------------------------------------------------------------------------

def test_unknown_tag_fails():
    errors = _scan('[!figure src="x.jpg"]')
    assert len(errors) == 1
    assert 'unknown tag' in errors[0].message
    assert 'figure' in errors[0].message


def test_unknown_tag_includes_line_number():
    body = 'First line.\n\n[!figure src="x.jpg"]'
    errors = _scan(body)
    assert len(errors) == 1
    assert 'line 3' in errors[0].message


def test_unknown_tag_did_you_mean():
    errors = _scan('[!youutube id="abc"]')
    assert any('did you mean' in e.message for e in errors)
    assert any('youtube' in e.message for e in errors)


# ---------------------------------------------------------------------------
# Missing required argument
# ---------------------------------------------------------------------------

def test_youtube_missing_id_fails():
    errors = _scan('[!youtube]')
    assert len(errors) == 1
    assert 'missing required argument' in errors[0].message
    assert "'id'" in errors[0].message


def test_iframe_missing_both_required_fails():
    errors = _scan('[!iframe]')
    assert len(errors) == 2
    messages = ' '.join(e.message for e in errors)
    assert "'src'" in messages
    assert "'title'" in messages


def test_iframe_missing_title_fails():
    errors = _scan('[!iframe src="https://example.com"]')
    assert len(errors) == 1
    assert "'title'" in errors[0].message


# ---------------------------------------------------------------------------
# Unknown argument
# ---------------------------------------------------------------------------

def test_youtube_unknown_arg_fails():
    errors = _scan('[!youtube id="abc" autoplay="true"]')
    assert len(errors) == 1
    assert 'unknown argument' in errors[0].message
    assert 'autoplay' in errors[0].message


def test_unknown_arg_lists_allowed():
    errors = _scan('[!youtube id="abc" autoplay="true"]')
    assert len(errors) == 1
    assert 'allowed:' in errors[0].message
    assert 'id' in errors[0].message


# ---------------------------------------------------------------------------
# Malformed delimiter
# ---------------------------------------------------------------------------

def test_malformed_missing_close_bracket_fails():
    errors = _scan('[!youtube id="abc"')
    assert len(errors) == 1
    assert 'malformed' in errors[0].message


def test_malformed_empty_name_fails():
    errors = _scan('[!]')
    assert len(errors) == 1
    assert 'malformed' in errors[0].message


# ---------------------------------------------------------------------------
# Registry is single source of truth
# ---------------------------------------------------------------------------

def test_no_hardcoded_tag_names():
    """body_scanner must not contain hardcoded tag name strings."""
    import inspect
    import frontmatter_lint.body_scanner as mod
    src = inspect.getsource(mod)
    assert 'youtube' not in src
    assert 'iframe' not in src
