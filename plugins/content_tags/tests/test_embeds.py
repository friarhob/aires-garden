"""Tests for the embed registry and individual embed renderers."""

import pytest
from content_tags import embeds  # noqa: F401 — trigger registrations
from content_tags.registry import REGISTRY
from content_tags.parser import parse_args, iter_candidate_lines, EMBED_RE


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_registry_contains_youtube_and_iframe():
    assert 'youtube' in REGISTRY
    assert 'iframe' in REGISTRY


def test_registry_has_required_attrs():
    for name, tag in REGISTRY.items():
        assert hasattr(tag, 'required_args')
        assert hasattr(tag, 'optional_args')
        assert callable(tag.render)


def test_registry_args_are_tuples():
    for name, tag in REGISTRY.items():
        assert isinstance(tag.required_args, tuple)
        assert isinstance(tag.optional_args, tuple)


def test_registry_is_immutable():
    tag = REGISTRY['youtube']
    with pytest.raises((AttributeError, TypeError)):
        tag.required_args = ('new',)  # type: ignore[misc]


# ---------------------------------------------------------------------------
# YouTube renderer
# ---------------------------------------------------------------------------

def test_youtube_renders_basic():
    tag = REGISTRY['youtube']
    html = tag.render({'id': 'dQw4w9WgXcQ'})
    assert 'youtube-nocookie.com/embed/dQw4w9WgXcQ?rel=0' in html
    assert 'loading="lazy"' in html
    assert 'allowfullscreen' in html
    assert 'class="embed embed-youtube"' in html


def test_youtube_renders_with_start():
    tag = REGISTRY['youtube']
    html = tag.render({'id': 'abc', 'start': '42'})
    assert '&amp;start=42' in html


def test_youtube_without_start_has_no_start_param():
    tag = REGISTRY['youtube']
    html = tag.render({'id': 'abc'})
    assert 'start=' not in html


def test_youtube_required_args():
    assert REGISTRY['youtube'].required_args == ('id',)


def test_youtube_optional_args():
    assert REGISTRY['youtube'].optional_args == ('start',)


# ---------------------------------------------------------------------------
# iframe renderer
# ---------------------------------------------------------------------------

def test_iframe_renders_basic():
    tag = REGISTRY['iframe']
    html = tag.render({'src': 'https://example.com', 'title': 'Demo'})
    assert 'src="https://example.com"' in html
    assert 'title="Demo"' in html
    assert 'loading="lazy"' in html
    assert 'sandbox=' in html
    assert 'height: 400px' in html
    assert 'class="embed embed-iframe"' in html


def test_iframe_custom_height():
    tag = REGISTRY['iframe']
    html = tag.render({'src': 'https://example.com', 'title': 'Demo', 'height': '600'})
    assert 'height: 600px' in html


def test_iframe_default_height():
    tag = REGISTRY['iframe']
    html = tag.render({'src': 'https://example.com', 'title': 'Demo'})
    assert 'height: 400px' in html


def test_iframe_required_args():
    assert REGISTRY['iframe'].required_args == ('src', 'title')


def test_iframe_optional_args():
    assert REGISTRY['iframe'].optional_args == ('height',)


# ---------------------------------------------------------------------------
# HTML escaping
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('char,escaped', [
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
])
def test_youtube_id_is_html_escaped(char, escaped):
    tag = REGISTRY['youtube']
    html = tag.render({'id': f'abc{char}123'})
    assert escaped in html
    assert f'abc{char}123' not in html


@pytest.mark.parametrize('char,escaped', [
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"', '&quot;'),
])
def test_iframe_src_is_html_escaped(char, escaped):
    tag = REGISTRY['iframe']
    html = tag.render({'src': f'https://example.com/{char}', 'title': 'Demo'})
    assert escaped in html


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def test_parse_args_simple():
    assert parse_args(' id="abc"') == {'id': 'abc'}


def test_parse_args_multiple():
    assert parse_args(' id="abc" start="42"') == {'id': 'abc', 'start': '42'}


def test_parse_args_quoted_with_spaces():
    result = parse_args(' src="https://example.com/foo bar" title="My demo"')
    assert result['src'] == 'https://example.com/foo bar'
    assert result['title'] == 'My demo'


def test_embed_re_matches_valid():
    assert EMBED_RE.match('[!youtube id="abc"]') is not None
    assert EMBED_RE.match('  [!youtube id="abc"]') is not None


def test_embed_re_rejects_four_space_indent():
    assert EMBED_RE.match('    [!youtube id="abc"]') is None


def test_embed_re_rejects_inline():
    assert EMBED_RE.match('Watch: [!youtube id="abc"] now.') is None


def test_embed_re_rejects_missing_bracket():
    assert EMBED_RE.match('[!youtube id="abc"') is None


def test_iter_candidate_lines_skips_fenced_code():
    source = '```\n[!youtube id="abc"]\n```\n'
    lines = list(iter_candidate_lines(source))
    assert all('[!youtube' not in line for _, line in lines)


def test_iter_candidate_lines_skips_indented_code():
    source = '    [!youtube id="abc"]\n'
    lines = list(iter_candidate_lines(source))
    assert lines == []


def test_iter_candidate_lines_yields_normal_lines():
    source = 'Hello world\n[!youtube id="abc"]\n'
    lines = list(iter_candidate_lines(source))
    line_texts = [line for _, line in lines]
    assert 'Hello world' in line_texts
    assert '[!youtube id="abc"]' in line_texts
