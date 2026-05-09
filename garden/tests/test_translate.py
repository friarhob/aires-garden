from pathlib import Path

import pytest
from typer.testing import CliRunner

from garden.cli import app
from garden.frontmatter_io import read_frontmatter, write_frontmatter

runner = CliRunner()

SOURCE_FIELDS = {
    "Title": "Hello World",
    "Slug": "hello-world",
    "Date": "2026-05-09",
    "Lang": "en",
    "Translation_key": "hello-world",
    "Status": "published",
}
SOURCE_BODY = "Body paragraph one.\n\nBody paragraph two.\n"


@pytest.fixture()
def content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "content"
    post_dir = root / "posts" / "hello-world"
    post_dir.mkdir(parents=True)
    src = post_dir / "hello-world.en.md"
    write_frontmatter(src, SOURCE_FIELDS, SOURCE_BODY)

    pages_dir = root / "pages"
    pages_dir.mkdir()
    page_src = pages_dir / "about.en.md"
    write_frontmatter(page_src, {**SOURCE_FIELDS, "Slug": "about", "Translation_key": "about"}, "Page body.\n")

    tag_dir = root / "tag-prose" / "my-tag"
    tag_dir.mkdir(parents=True)
    tag_src = tag_dir / "all.en.md"
    write_frontmatter(tag_src, {**SOURCE_FIELDS, "Slug": "all", "Translation_key": "my-tag"}, "Tag body.\n")

    monkeypatch.setattr("garden.commands.translate._CONTENT_ROOT", root)
    return root


class TestTranslatePost:
    def test_creates_translation(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "hello-world", "--to", "pt", "--slug", "ola-mundo", "--title", "Olá Mundo"])
        assert result.exit_code == 0, result.output
        target = content / "posts" / "hello-world" / "ola-mundo.pt.md"
        assert target.exists()
        fields, _ = read_frontmatter(target)
        assert fields["Title"] == "Olá Mundo"
        assert fields["Slug"] == "ola-mundo"
        assert fields["Lang"] == "pt"
        assert fields["Translation_key"] == "hello-world"
        assert fields["Status"] == "draft"
        assert fields["Date"] == "2026-05-09"

    def test_body_identical_to_source(self, content: Path) -> None:
        runner.invoke(app, ["translate", "hello-world", "--to", "pt", "--slug", "ola-mundo", "--title", "Olá"])
        target = content / "posts" / "hello-world" / "ola-mundo.pt.md"
        _, body = read_frontmatter(target)
        assert body == SOURCE_BODY

    def test_refuses_existing_target(self, content: Path) -> None:
        runner.invoke(app, ["translate", "hello-world", "--to", "pt", "--slug", "ola-mundo", "--title", "Olá"])
        result = runner.invoke(app, ["translate", "hello-world", "--to", "pt", "--slug", "ola-mundo", "--title", "Olá"])
        assert result.exit_code != 0

    def test_refuses_missing_source(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "nonexistent", "--to", "pt", "--slug", "x", "--title", "X"])
        assert result.exit_code != 0

    def test_invalid_lang(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "hello-world", "--to", "PT", "--slug", "ola", "--title", "Olá"])
        assert result.exit_code != 0

    def test_invalid_slug(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "hello-world", "--to", "pt", "--slug", "Bad Slug", "--title", "Olá"])
        assert result.exit_code != 0


class TestTranslatePage:
    def test_creates_page_translation(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "about", "--to", "pt", "--slug", "sobre", "--title", "Sobre"])
        assert result.exit_code == 0, result.output
        target = content / "pages" / "sobre.pt.md"
        assert target.exists()


class TestTranslateTagProse:
    def test_creates_tag_prose_translation(self, content: Path) -> None:
        result = runner.invoke(app, ["translate", "all", "--to", "pt", "--slug", "all", "--title", "Tudo"])
        assert result.exit_code == 0, result.output
        target = content / "tag-prose" / "my-tag" / "all.pt.md"
        assert target.exists()
