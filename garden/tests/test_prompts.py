from pathlib import Path
from unittest.mock import patch

import pytest
import typer

from garden.content_index import ContentFile
from garden.prompts import prompt_slug_picker


def _post(slug: str, title: str = "", lang: str = "en", status: str = "draft") -> ContentFile:
    return ContentFile(
        path=Path(f"content/posts/{slug}/{slug}.{lang}.md"),
        kind="post",
        slug=slug,
        lang=lang,
        translation_key=slug,
        status=status,
        title=title,
    )


class TestPromptSlugPicker:
    def test_returns_slug_from_selection(self) -> None:
        posts = [_post("hello", "Hello World"), _post("outro", "Outro Post", lang="pt")]
        chosen = "hello — Hello World (en, draft)"
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("questionary.autocomplete") as mock_ac:
            mock_ac.return_value.ask.return_value = chosen
            result = prompt_slug_picker(posts, "Select post:")
        assert result == "hello"

    def test_choices_include_slug_title_lang_status(self) -> None:
        posts = [_post("my-post", "My Post", lang="en", status="published")]
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("questionary.autocomplete") as mock_ac:
            mock_ac.return_value.ask.return_value = "my-post — My Post (en, published)"
            prompt_slug_picker(posts, "Select:")
        _choices = mock_ac.call_args[1]["choices"] if mock_ac.call_args[1] else mock_ac.call_args[0][1]
        assert "my-post — My Post (en, published)" in _choices

    def test_raises_abort_when_none(self) -> None:
        posts = [_post("hello")]
        with patch("garden.prompts.is_tty", return_value=True), \
             patch("questionary.autocomplete") as mock_ac:
            mock_ac.return_value.ask.return_value = None
            with pytest.raises(typer.Abort):
                prompt_slug_picker(posts, "Select:")

    def test_raises_on_non_tty(self) -> None:
        posts = [_post("hello")]
        with patch("garden.prompts.is_tty", return_value=False):
            with pytest.raises(typer.BadParameter):
                prompt_slug_picker(posts, "Select:")
