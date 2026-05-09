import pytest

from garden.validation import (
    ValidationError,
    validate_kind,
    validate_lang,
    validate_slug,
    validate_title,
)


class TestValidateKind:
    def test_valid(self):
        assert validate_kind("post") == "post"
        assert validate_kind("page") == "page"
        assert validate_kind("tag-prose") == "tag-prose"

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_kind("article")
        with pytest.raises(ValidationError):
            validate_kind("")
        with pytest.raises(ValidationError):
            validate_kind("Post")


class TestValidateSlug:
    def test_valid(self):
        assert validate_slug("hello") == "hello"
        assert validate_slug("hello-world") == "hello-world"
        assert validate_slug("my-post-123") == "my-post-123"
        assert validate_slug("abc") == "abc"

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_slug("Hello World")
        with pytest.raises(ValidationError):
            validate_slug("hello_world")
        with pytest.raises(ValidationError):
            validate_slug("Hello")
        with pytest.raises(ValidationError):
            validate_slug("-hello")
        with pytest.raises(ValidationError):
            validate_slug("hello-")
        with pytest.raises(ValidationError):
            validate_slug("")


class TestValidateLang:
    def test_valid(self):
        assert validate_lang("en") == "en"
        assert validate_lang("pt") == "pt"
        assert validate_lang("fr") == "fr"
        assert validate_lang("es") == "es"

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_lang("EN")
        with pytest.raises(ValidationError):
            validate_lang("english")
        with pytest.raises(ValidationError):
            validate_lang("pt-br")
        with pytest.raises(ValidationError):
            validate_lang("")
        with pytest.raises(ValidationError):
            validate_lang("e")


class TestValidateTitle:
    def test_valid(self):
        assert validate_title("Hello") == "Hello"
        assert validate_title("  Hello  ") == "  Hello  "

    def test_invalid(self):
        with pytest.raises(ValidationError):
            validate_title("")
        with pytest.raises(ValidationError):
            validate_title("   ")
