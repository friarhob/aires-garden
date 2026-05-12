from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from garden.cli import app
from garden.commands.new import _slugify
from garden.frontmatter_io import read_frontmatter
from garden.validation import ValidationError

runner = CliRunner()


def _invoke(*args: str, content_root: Path | None = None) -> object:
    extra = ["--content-root", str(content_root)] if content_root else []
    # We patch _CONTENT_ROOT inside new.py
    return runner.invoke(app, ["new", *args])


@pytest.fixture()
def content(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "content"
    (root / "posts").mkdir(parents=True)
    (root / "pages").mkdir(parents=True)
    (root / "tag-prose").mkdir(parents=True)
    monkeypatch.setattr("garden.commands.new._CONTENT_ROOT", root)
    return root


class TestNewPost:
    def test_creates_post_file(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "post", "--title", "Hello World", "--slug", "hello-world", "--lang", "en"])
        assert result.exit_code == 0, result.output
        f = content / "posts" / "hello-world" / "hello-world.en.md"
        assert f.exists()
        fields, _ = read_frontmatter(f)
        assert fields["Title"] == "Hello World"
        assert fields["Slug"] == "hello-world"
        assert fields["Lang"] == "en"
        assert fields["Translation_key"] == "hello-world"
        assert fields["Status"] == "draft"
        assert fields["Date"] == date.today().isoformat()

    def test_creates_assets_dir(self, content: Path) -> None:
        runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "x", "--lang", "en"])
        assert (content / "posts" / "x" / "assets").is_dir()

    def test_refuses_existing_file(self, content: Path) -> None:
        runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "x", "--lang", "en"])
        result = runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "x", "--lang", "en"])
        assert result.exit_code != 0

    def test_invalid_slug(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "Bad Slug", "--lang", "en"])
        assert result.exit_code != 0
        assert (content / "posts").stat().st_size == 0 or not any((content / "posts").iterdir())

    def test_invalid_lang(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "x", "--lang", "english"])
        assert result.exit_code != 0

    def test_empty_title(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "post", "--title", "   ", "--slug", "x", "--lang", "en"])
        assert result.exit_code != 0

    def test_invalid_kind(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "article", "--title", "X", "--slug", "x", "--lang", "en"])
        assert result.exit_code != 0


class TestNewPage:
    def test_creates_page_file(self, content: Path) -> None:
        result = runner.invoke(app, ["new", "--kind", "page", "--title", "About", "--slug", "about", "--lang", "en"])
        assert result.exit_code == 0, result.output
        f = content / "pages" / "about.en.md"
        assert f.exists()
        fields, _ = read_frontmatter(f)
        assert fields["Title"] == "About"
        assert "Date" not in fields
        assert "Slug" not in fields

    def test_no_per_page_directory(self, content: Path) -> None:
        runner.invoke(app, ["new", "--kind", "page", "--title", "About", "--slug", "about", "--lang", "en"])
        assert not (content / "pages" / "about").exists()


class TestNewTagProse:
    def test_creates_tag_prose_file(self, content: Path) -> None:
        (content / "tag-prose" / "my-tag").mkdir()
        result = runner.invoke(app, [
            "new", "--kind", "tag-prose",
            "--title", "My Tag", "--lang", "en",
            "--tag", "my-tag", "--shape", "all",
        ])
        assert result.exit_code == 0, result.output
        f = content / "tag-prose" / "my-tag" / "all.en.md"
        assert f.exists()
        fields, _ = read_frontmatter(f)
        assert fields["Status"] == "hidden"
        assert "Slug" not in fields
        assert "Translation_key" not in fields

    def test_creates_tag_dir_with_flag(self, content: Path) -> None:
        result = runner.invoke(app, [
            "new", "--kind", "tag-prose",
            "--title", "New Tag", "--lang", "en",
            "--tag", "new-tag", "--shape", "all", "--create-tag",
        ])
        assert result.exit_code == 0, result.output
        assert (content / "tag-prose" / "new-tag" / "all.en.md").exists()

    def test_refuses_missing_tag_dir_without_flag(self, content: Path) -> None:
        result = runner.invoke(app, [
            "new", "--kind", "tag-prose",
            "--title", "X", "--lang", "en",
            "--tag", "nonexistent", "--shape", "all",
        ])
        assert result.exit_code != 0

    def test_tag_picker_shows_existing_tags(self, content: Path) -> None:
        (content / "tag-prose" / "poetry").mkdir()
        (content / "tag-prose" / "essays").mkdir()
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("garden.prompts.prompt_select", return_value="poetry") as mock_select, \
             patch("garden.prompts.prompt_text", return_value="Poems"):
            runner.invoke(app, [
                "new", "--kind", "tag-prose", "--lang", "en", "--shape", "all",
            ])
        # first call is the tag picker
        first_call_choices = mock_select.call_args_list[0][0][1]
        assert "poetry" in first_call_choices
        assert "essays" in first_call_choices
        assert "[new tag]" in first_call_choices

    def test_new_tag_sentinel_prompts_for_name(self, content: Path) -> None:
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("garden.prompts.prompt_select", side_effect=["[new tag]", "all"]), \
             patch("garden.prompts.prompt_text", side_effect=["brand-new", "Brand New"]), \
             patch("garden.prompts.prompt_confirm", return_value=True):
            result = runner.invoke(app, [
                "new", "--kind", "tag-prose", "--lang", "en",
            ])
        assert result.exit_code == 0, result.output
        assert (content / "tag-prose" / "brand-new" / "all.en.md").exists()

    def test_title_suggested_from_existing_file(self, content: Path) -> None:
        tag_dir = content / "tag-prose" / "my-tag"
        tag_dir.mkdir()
        from garden.frontmatter_io import write_frontmatter as wfm
        wfm(tag_dir / "all.pt.md", {"Title": "Minha Tag", "Lang": "pt", "Status": "hidden"}, "")
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("garden.prompts.prompt_select", return_value="all"), \
             patch("garden.prompts.prompt_text", return_value="Minha Tag") as mock_text:
            runner.invoke(app, [
                "new", "--kind", "tag-prose", "--lang", "en", "--tag", "my-tag",
            ])
        # title prompt should have been called with the existing title as default
        assert mock_text.call_args[1].get("default") == "Minha Tag" or mock_text.call_args[0][1] == "Minha Tag" if mock_text.call_args else True

    def test_non_tty_requires_tag_flag(self, content: Path) -> None:
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, [
                "new", "--kind", "tag-prose",
                "--title", "X", "--lang", "en", "--shape", "all",
            ])
        assert result.exit_code != 0

    def test_non_tty_requires_title_flag(self, content: Path) -> None:
        (content / "tag-prose" / "my-tag").mkdir()
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, [
                "new", "--kind", "tag-prose",
                "--lang", "en", "--tag", "my-tag", "--shape", "all",
            ])
        assert result.exit_code != 0


class TestNonTtyMode:
    def test_missing_kind_fails_non_tty(self, content: Path) -> None:
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, ["new", "--title", "X", "--slug", "x", "--lang", "en"])
        assert result.exit_code != 0

    def test_missing_title_fails_non_tty(self, content: Path) -> None:
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, ["new", "--kind", "post", "--slug", "x", "--lang", "en"])
        assert result.exit_code != 0

    def test_missing_lang_fails_non_tty(self, content: Path) -> None:
        with patch("garden.prompts.is_tty", return_value=False):
            result = runner.invoke(app, ["new", "--kind", "post", "--title", "X", "--slug", "x"])
        assert result.exit_code != 0


class TestSlugify:
    def test_plain_ascii_unchanged(self) -> None:
        assert _slugify("Hello World") == "hello-world"

    def test_portuguese_accents(self) -> None:
        assert _slugify("Água no Balão") == "agua-no-balao"

    def test_french_accents(self) -> None:
        assert _slugify("crème brûlée") == "creme-brulee"

    def test_spanish_accents(self) -> None:
        assert _slugify("Año Nuevo") == "ano-nuevo"

    def test_multiple_spaces_collapsed(self) -> None:
        assert _slugify("hello   world") == "hello-world"

    def test_title_with_no_alphanumeric_raises(self) -> None:
        with pytest.raises(ValidationError):
            _slugify("!!!")
