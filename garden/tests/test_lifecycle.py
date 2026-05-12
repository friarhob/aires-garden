from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from garden.cli import app
from garden.frontmatter_io import read_frontmatter, write_frontmatter

runner = CliRunner()


def _make_post(root: Path, slug: str, lang: str, status: str, tk: str | None = None) -> Path:
    post_dir = root / "posts" / (tk or slug)
    post_dir.mkdir(parents=True, exist_ok=True)
    path = post_dir / f"{slug}.{lang}.md"
    write_frontmatter(path, {
        "Title": slug.capitalize(),
        "Slug": slug,
        "Date": "2026-05-09",
        "Lang": lang,
        "Translation_key": tk or slug,
        "Status": status,
    }, "")
    return path


def _make_page(root: Path, slug: str, lang: str, status: str) -> Path:
    pages_dir = root / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    path = pages_dir / f"{slug}.{lang}.md"
    write_frontmatter(path, {
        "Title": slug.capitalize(),
        "Slug": slug,
        "Lang": lang,
        "Status": status,
    }, "")
    return path


@pytest.fixture()
def content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "content"
    monkeypatch.setattr("garden.commands.lifecycle._CONTENT_ROOT", root)
    return root


class TestPublish:
    def test_draft_to_published(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        result = runner.invoke(app, ["publish", "hello", "--no-all-translations"])
        assert result.exit_code == 0, result.output
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "published"

    def test_refuses_hidden_without_force(self, content: Path) -> None:
        _make_post(content, "hello", "en", "hidden")
        result = runner.invoke(app, ["publish", "hello", "--no-all-translations"])
        assert result.exit_code != 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "hidden"

    def test_force_bypasses_hidden(self, content: Path) -> None:
        _make_post(content, "hello", "en", "hidden")
        result = runner.invoke(app, ["publish", "hello", "--no-all-translations", "--force"])
        assert result.exit_code == 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "published"

    def test_slug_not_found(self, content: Path) -> None:
        result = runner.invoke(app, ["publish", "nonexistent", "--no-all-translations"])
        assert result.exit_code != 0

    def test_refuses_page(self, content: Path) -> None:
        _make_page(content, "about", "en", "draft")
        result = runner.invoke(app, ["publish", "about", "--no-all-translations"])
        assert result.exit_code != 0


class TestDraft:
    def test_published_to_draft(self, content: Path) -> None:
        _make_post(content, "hello", "en", "published")
        result = runner.invoke(app, ["draft", "hello", "--no-all-translations"])
        assert result.exit_code == 0, result.output
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "draft"

    def test_refuses_hidden_without_force(self, content: Path) -> None:
        _make_post(content, "hello", "en", "hidden")
        result = runner.invoke(app, ["draft", "hello", "--no-all-translations"])
        assert result.exit_code != 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "hidden"

    def test_force_bypasses_hidden(self, content: Path) -> None:
        _make_post(content, "hello", "en", "hidden")
        result = runner.invoke(app, ["draft", "hello", "--no-all-translations", "--force"])
        assert result.exit_code == 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "draft"


class TestArchive:
    def test_published_to_hidden(self, content: Path) -> None:
        _make_post(content, "hello", "en", "published")
        result = runner.invoke(app, ["archive", "hello", "--no-all-translations"])
        assert result.exit_code == 0, result.output
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "hidden"

    def test_refuses_draft_without_force(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        result = runner.invoke(app, ["archive", "hello", "--no-all-translations"])
        assert result.exit_code != 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "draft"

    def test_force_bypasses_draft(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        result = runner.invoke(app, ["archive", "hello", "--no-all-translations", "--force"])
        assert result.exit_code == 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "hidden"


class TestAllTranslations:
    def test_all_translations_happy_path(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft", tk="hello")
        _make_post(content, "ola", "pt", "draft", tk="hello")
        result = runner.invoke(app, ["publish", "hello", "--all-translations"])
        assert result.exit_code == 0, result.output
        for path in [
            content / "posts" / "hello" / "hello.en.md",
            content / "posts" / "hello" / "ola.pt.md",
        ]:
            fields, _ = read_frontmatter(path)
            assert fields["Status"] == "published"

    def test_atomic_refusal_blocks_all(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft", tk="hello")
        _make_post(content, "ola", "pt", "hidden", tk="hello")
        result = runner.invoke(app, ["publish", "hello", "--all-translations"])
        assert result.exit_code != 0
        # Neither file was modified
        en_fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        pt_fields, _ = read_frontmatter(content / "posts" / "hello" / "ola.pt.md")
        assert en_fields["Status"] == "draft"
        assert pt_fields["Status"] == "hidden"

    def test_all_translations_with_force(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft", tk="hello")
        _make_post(content, "ola", "pt", "hidden", tk="hello")
        result = runner.invoke(app, ["publish", "hello", "--all-translations", "--force"])
        assert result.exit_code == 0
        for path in [
            content / "posts" / "hello" / "hello.en.md",
            content / "posts" / "hello" / "ola.pt.md",
        ]:
            fields, _ = read_frontmatter(path)
            assert fields["Status"] == "published"

    def test_non_tty_requires_explicit_flag(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, ["publish", "hello"])
        assert result.exit_code != 0

    def test_tty_prompts_for_flag(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("garden.prompts.prompt_confirm", return_value=False):
            result = runner.invoke(app, ["publish", "hello"])
        assert result.exit_code == 0
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "published"


class TestSlugPicker:
    def test_slug_omitted_non_tty_exits_nonzero(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, ["publish", "--no-all-translations"])
        assert result.exit_code != 0

    def test_slug_omitted_tty_calls_picker(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("garden.prompts.prompt_slug_picker", return_value="hello") as mock_picker:
            result = runner.invoke(app, ["publish", "--no-all-translations"])
        assert result.exit_code == 0, result.output
        mock_picker.assert_called_once()
        fields, _ = read_frontmatter(content / "posts" / "hello" / "hello.en.md")
        assert fields["Status"] == "published"

    def test_slug_supplied_skips_picker(self, content: Path) -> None:
        _make_post(content, "hello", "en", "draft")
        with patch("garden.prompts.prompt_slug_picker") as mock_picker:
            runner.invoke(app, ["publish", "hello", "--no-all-translations"])
        mock_picker.assert_not_called()
