"""Tests for tag slug validation in PostFrontmatter and tag-prose schema."""
from pathlib import Path

import pytest

from frontmatter_lint.schema import (
    PostFrontmatter,
    validate_tag_prose,
    validate_tag_prose_group,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_POST = {
    "Title": "Hello",
    "Slug": "hello",
    "Date": "2025-01-01",
    "Lang": "en",
    "Translation_key": "hello",
    "Status": "published",
}


def _post(tags):
    return {**_VALID_POST, "Tags": tags}


# ---------------------------------------------------------------------------
# Task 7.1 — empty-slug rejection
# ---------------------------------------------------------------------------

def test_tag_empty_slug_bang():
    with pytest.raises(Exception, match="empty slug"):
        PostFrontmatter.model_validate(_post(["!!!"]))


def test_tag_empty_slug_spaces():
    with pytest.raises(Exception, match="empty slug"):
        PostFrontmatter.model_validate(_post(["   "]))


# ---------------------------------------------------------------------------
# Task 7.2 — slug-collision rejection
# ---------------------------------------------------------------------------

def test_tag_slug_collision_case():
    with pytest.raises(Exception, match="slugify to"):
        PostFrontmatter.model_validate(_post(["Rant", "rant"]))


def test_tag_slug_collision_acronym():
    with pytest.raises(Exception, match="slugify to"):
        PostFrontmatter.model_validate(_post(["DSL", "dsl"]))


# ---------------------------------------------------------------------------
# Task 7.3 — mixed-case acceptance for distinct slugs, regression
# ---------------------------------------------------------------------------

def test_mixed_case_distinct_slugs_accepted():
    m = PostFrontmatter.model_validate(_post(["Rant", "Published Works"]))
    assert len(m.tags) == 2


def test_existing_good_tags_regression():
    m = PostFrontmatter.model_validate(_post(["published-works", "rant"]))
    assert set(m.tags) == {"published-works", "rant"}


def test_no_tags_accepted():
    m = PostFrontmatter.model_validate(_VALID_POST)
    assert m.tags == []


# ---------------------------------------------------------------------------
# validate_tag_prose — schema validation
# ---------------------------------------------------------------------------

_FAKE_PATH = Path("content/tag-prose/some-tag/all.en.md")
_VALID_PROSE_FM = {"Title": "My tag", "Lang": "en", "Status": "hidden"}


def test_tag_prose_valid():
    errors = validate_tag_prose(_FAKE_PATH, _VALID_PROSE_FM, "some-tag")
    assert errors == []


def test_tag_prose_wrong_status():
    raw = {**_VALID_PROSE_FM, "Status": "published"}
    errors = validate_tag_prose(_FAKE_PATH, raw, "some-tag")
    assert any("hidden" in e.message for e in errors)


def test_tag_prose_forbidden_slug():
    raw = {**_VALID_PROSE_FM, "Slug": "something"}
    errors = validate_tag_prose(_FAKE_PATH, raw, "some-tag")
    assert any("Slug" in e.message for e in errors)


def test_tag_prose_forbidden_translation_key():
    raw = {**_VALID_PROSE_FM, "Translation_key": "something"}
    errors = validate_tag_prose(_FAKE_PATH, raw, "some-tag")
    assert any("Translation_key" in e.message for e in errors)


def test_tag_prose_bad_scope():
    path = Path("content/tag-prose/some-tag/foo.en.md")
    errors = validate_tag_prose(path, _VALID_PROSE_FM, "some-tag")
    assert any("scope" in e.message for e in errors)


def test_tag_prose_lang_mismatch():
    path = Path("content/tag-prose/some-tag/all.pt.md")
    errors = validate_tag_prose(path, _VALID_PROSE_FM, "some-tag")
    assert any("Lang" in e.message or "lang" in e.message for e in errors)


def test_tag_prose_bad_dir():
    errors = validate_tag_prose(_FAKE_PATH, _VALID_PROSE_FM, "INVALID_DIR")
    assert any("slug regex" in e.message for e in errors)


# ---------------------------------------------------------------------------
# validate_tag_prose_group — uniqueness
# ---------------------------------------------------------------------------

def test_tag_prose_group_unique():
    files = [
        Path("content/tag-prose/t/all.en.md"),
        Path("content/tag-prose/t/all.pt.md"),
    ]
    assert validate_tag_prose_group("t", files) == []


def test_tag_prose_group_collision():
    files = [
        Path("content/tag-prose/t/all.en.md"),
        Path("content/tag-prose/t/all.en.md"),
    ]
    errors = validate_tag_prose_group("t", files)
    assert len(errors) == 1
    assert "all" in errors[0].message
    assert "en" in errors[0].message
