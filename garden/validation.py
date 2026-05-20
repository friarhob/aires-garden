import re

KINDS = ("post", "page", "tag-prose", "intro")
_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_LANG_RE = re.compile(r"^[a-z]{2}$")


class ValidationError(ValueError):
    pass


def validate_kind(value: str) -> str:
    if value not in KINDS:
        raise ValidationError(
            f"kind must be one of {{{', '.join(KINDS)}}}, got: {value!r}"
        )
    return value


def validate_slug(value: str) -> str:
    if not _SLUG_RE.match(value):
        raise ValidationError(
            f"slug must match ^[a-z0-9]+(-[a-z0-9]+)*$ (lowercase kebab-case), got: {value!r}"
        )
    return value


def validate_lang(value: str) -> str:
    if not _LANG_RE.match(value):
        raise ValidationError(
            f"lang must be a two-letter ISO 639-1 code (^[a-z]{{2}}$), got: {value!r}"
        )
    return value


def validate_title(value: str) -> str:
    if not value.strip():
        raise ValidationError("title must not be empty")
    return value
