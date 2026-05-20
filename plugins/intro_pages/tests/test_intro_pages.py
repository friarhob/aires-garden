"""Tests for the intro_pages plugin."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from intro_pages import on_article_generator_finalized


def _make_generator(tmp_path: Path, md_settings: dict | None = None) -> MagicMock:
    gen = MagicMock()
    gen.settings = {
        "PATH": str(tmp_path),
        "MARKDOWN": md_settings or {},
    }
    gen.context = {}
    return gen


def _write_intro(tmp_path: Path, filename: str, body: str, lang: str, scope_title: str) -> None:
    intro_dir = tmp_path / "intro"
    intro_dir.mkdir(exist_ok=True)
    (intro_dir / filename).write_text(
        f"Title: {scope_title}\nLang: {lang}\nStatus: hidden\n\n{body}",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Empty intro dir
# ---------------------------------------------------------------------------

def test_empty_intro_dir(tmp_path: Path) -> None:
    (tmp_path / "intro").mkdir()
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert gen.context["INTRO_ALL"] == {}
    assert gen.context["INTRO_LANG"] == {}


def test_missing_intro_dir(tmp_path: Path) -> None:
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert gen.context["INTRO_ALL"] == {}
    assert gen.context["INTRO_LANG"] == {}


# ---------------------------------------------------------------------------
# all.<lang>.md → INTRO_ALL
# ---------------------------------------------------------------------------

def test_all_en_populates_intro_all(tmp_path: Path) -> None:
    _write_intro(tmp_path, "all.en.md", "Hello world.", "en", "All EN")
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert "en" in gen.context["INTRO_ALL"]
    assert "Hello world" in gen.context["INTRO_ALL"]["en"]
    assert gen.context["INTRO_LANG"] == {}


def test_all_pt_populates_intro_all(tmp_path: Path) -> None:
    _write_intro(tmp_path, "all.pt.md", "Olá mundo.", "pt", "All PT")
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert "pt" in gen.context["INTRO_ALL"]
    assert gen.context["INTRO_LANG"] == {}


# ---------------------------------------------------------------------------
# lang.<lang>.md → INTRO_LANG
# ---------------------------------------------------------------------------

def test_lang_pt_populates_intro_lang(tmp_path: Path) -> None:
    _write_intro(tmp_path, "lang.pt.md", "Canto português.", "pt", "Lang PT")
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert "pt" in gen.context["INTRO_LANG"]
    assert "Canto português" in gen.context["INTRO_LANG"]["pt"]
    assert gen.context["INTRO_ALL"] == {}


# ---------------------------------------------------------------------------
# Multiple files, both scopes
# ---------------------------------------------------------------------------

def test_multiple_files_split_by_scope(tmp_path: Path) -> None:
    _write_intro(tmp_path, "all.en.md", "All EN body.", "en", "All EN")
    _write_intro(tmp_path, "all.pt.md", "All PT body.", "pt", "All PT")
    _write_intro(tmp_path, "lang.en.md", "Lang EN body.", "en", "Lang EN")
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    assert set(gen.context["INTRO_ALL"].keys()) == {"en", "pt"}
    assert set(gen.context["INTRO_LANG"].keys()) == {"en"}


# ---------------------------------------------------------------------------
# Rendered HTML is actual HTML (not raw Markdown)
# ---------------------------------------------------------------------------

def test_renders_markdown_to_html(tmp_path: Path) -> None:
    _write_intro(tmp_path, "all.en.md", "**Bold** text.", "en", "X")
    gen = _make_generator(tmp_path)
    on_article_generator_finalized(gen)
    html = gen.context["INTRO_ALL"]["en"]
    assert "<strong>Bold</strong>" in html
    assert "**" not in html
