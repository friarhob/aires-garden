"""Tests for intro content type schema and filename contract validation."""
from pathlib import Path

import pytest

from frontmatter_lint.schema import (
    IntroFrontmatter,
    validate_intro,
    validate_intro_group,
)

_FLAT_PATH = Path("content/intro/all.en.md")
_VALID_INTRO_FM = {"Title": "Welcome", "Lang": "en", "Status": "hidden"}


# ---------------------------------------------------------------------------
# Valid file passes
# ---------------------------------------------------------------------------

def test_intro_valid_all_scope():
    errors = validate_intro(_FLAT_PATH, _VALID_INTRO_FM)
    assert errors == []


def test_intro_valid_lang_scope():
    path = Path("content/intro/lang.en.md")
    errors = validate_intro(path, _VALID_INTRO_FM)
    assert errors == []


# ---------------------------------------------------------------------------
# Missing required field
# ---------------------------------------------------------------------------

def test_intro_missing_title():
    raw = {"Lang": "en", "Status": "hidden"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("title" in e.message.lower() for e in errors)


def test_intro_missing_lang():
    raw = {"Title": "Welcome", "Status": "hidden"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("lang" in e.message.lower() for e in errors)


def test_intro_missing_status():
    raw = {"Title": "Welcome", "Lang": "en"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert len(errors) > 0


# ---------------------------------------------------------------------------
# Wrong status value
# ---------------------------------------------------------------------------

def test_intro_status_published_fails():
    raw = {**_VALID_INTRO_FM, "Status": "published"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("hidden" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Forbidden fields
# ---------------------------------------------------------------------------

def test_intro_forbidden_slug():
    raw = {**_VALID_INTRO_FM, "Slug": "something"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("Slug" in e.message for e in errors)


def test_intro_forbidden_translation_key():
    raw = {**_VALID_INTRO_FM, "Translation_key": "something"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("Translation_key" in e.message for e in errors)


def test_intro_forbidden_tags():
    raw = {**_VALID_INTRO_FM, "Tags": "foo"}
    errors = validate_intro(_FLAT_PATH, raw)
    assert any("Tags" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Filename ↔ frontmatter coupling — lang mismatch
# ---------------------------------------------------------------------------

def test_intro_lang_mismatch():
    path = Path("content/intro/all.pt.md")
    errors = validate_intro(path, _VALID_INTRO_FM)  # Lang: en but file is .pt.md
    assert any("lang" in e.message.lower() for e in errors)


# ---------------------------------------------------------------------------
# Invalid scope
# ---------------------------------------------------------------------------

def test_intro_invalid_scope():
    path = Path("content/intro/root.en.md")
    errors = validate_intro(path, _VALID_INTRO_FM)
    assert any("scope" in e.message for e in errors)


# ---------------------------------------------------------------------------
# Nested path rejection
# ---------------------------------------------------------------------------

def test_intro_nested_path_rejected():
    path = Path("content/intro/subdir/all.en.md")
    errors = validate_intro(path, _VALID_INTRO_FM)
    assert any("subdirector" in e.message.lower() or "directly" in e.message.lower() for e in errors)


# ---------------------------------------------------------------------------
# validate_intro_group — uniqueness
# ---------------------------------------------------------------------------

def test_intro_group_unique():
    files = [
        Path("content/intro/all.en.md"),
        Path("content/intro/all.pt.md"),
        Path("content/intro/lang.en.md"),
    ]
    assert validate_intro_group(files) == []


def test_intro_group_collision():
    files = [
        Path("content/intro/all.en.md"),
        Path("content/intro/all.en.md"),
    ]
    errors = validate_intro_group(files)
    assert len(errors) == 1
    assert "all" in errors[0].message
    assert "en" in errors[0].message
