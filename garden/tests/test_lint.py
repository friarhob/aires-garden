from pathlib import Path

import pytest
from typer.testing import CliRunner

from garden.cli import app

runner = CliRunner()


@pytest.fixture()
def clean_content(tmp_path: Path) -> Path:
    """Minimal valid content tree that passes frontmatter_lint."""
    root = tmp_path / "content"
    posts = root / "posts" / "sample"
    posts.mkdir(parents=True)
    (posts / "sample.en.md").write_text(
        "Title: Sample\nSlug: sample\nDate: 2026-01-01\nLang: en\n"
        "Translation_key: sample\nStatus: published\n\nBody.\n",
        encoding="utf-8",
    )
    (root / "pages").mkdir()
    (root / "tag-prose").mkdir()
    return root


@pytest.fixture()
def dirty_content(tmp_path: Path) -> Path:
    """Content tree with a lint failure (missing Title)."""
    root = tmp_path / "content"
    posts = root / "posts" / "bad"
    posts.mkdir(parents=True)
    (posts / "bad.en.md").write_text(
        "Slug: bad\nDate: 2026-01-01\nLang: en\nTranslation_key: bad\nStatus: published\n\nBody.\n",
        encoding="utf-8",
    )
    (root / "pages").mkdir()
    (root / "tag-prose").mkdir()
    return root


def test_lint_clean_exits_zero(clean_content: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(clean_content.parent)
    result = runner.invoke(app, ["lint"])
    assert result.exit_code == 0


def test_lint_dirty_exits_nonzero(dirty_content: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(dirty_content.parent)
    result = runner.invoke(app, ["lint"])
    assert result.exit_code != 0
