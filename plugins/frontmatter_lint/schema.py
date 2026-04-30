"""Frontmatter schema and validation logic. No Pelican imports."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Literal, Union

import langcodes
from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Error type
# ---------------------------------------------------------------------------

@dataclass
class LintError:
    path: Path
    message: str


# ---------------------------------------------------------------------------
# Lang validator (shared between models)
# ---------------------------------------------------------------------------

def _validate_lang(v: object) -> str:
    s = str(v)
    if len(s) != 2 or not s.isalpha():
        raise ValueError(
            f"Lang must be a 2-letter ISO 639-1 alpha-2 code (no region suffix), got '{s}'"
        )
    if not langcodes.tag_is_valid(s):
        raise ValueError(f"'{s}' is not a valid ISO 639-1 language code")
    return s.lower()


_SLUG_PATTERN = r"^[a-z0-9]+(-[a-z0-9]+)*$"


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class PostFrontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: Annotated[str, Field(alias="Title")]
    slug: Annotated[str, Field(alias="Slug", pattern=_SLUG_PATTERN)]
    pub_date: Annotated[Union[date, datetime], Field(alias="Date")]
    lang: Annotated[str, Field(alias="Lang")]
    translation_key: Annotated[str, Field(alias="Translation_key", pattern=_SLUG_PATTERN)]
    status: Annotated[Literal["draft", "published", "hidden"], Field(alias="Status")]
    tags: Annotated[list[str], Field(alias="Tags", default=[])]

    @field_validator("lang", mode="before")
    @classmethod
    def check_lang(cls, v: object) -> str:
        return _validate_lang(v)

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [v] if v.strip() else []
        return list(v)  # type: ignore[arg-type]


class PageFrontmatter(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    title: Annotated[str, Field(alias="Title")]
    status: Annotated[Literal["draft", "published", "hidden"], Field(alias="Status")]
    lang: Annotated[Union[str, None], Field(alias="Lang", default=None)]
    save_as: Annotated[Union[str, None], Field(alias="Save_as", default=None)]
    url: Annotated[Union[str, None], Field(alias="URL", default=None)]

    @field_validator("lang", mode="before")
    @classmethod
    def check_lang(cls, v: object) -> Union[str, None]:
        if v is None:
            return None
        return _validate_lang(v)


# ---------------------------------------------------------------------------
# Per-file validation
# ---------------------------------------------------------------------------

def _pydantic_errors(exc: Exception) -> list[str]:
    msgs = []
    for err in getattr(exc, "errors", lambda: [])():
        loc = ".".join(str(x) for x in err.get("loc", ("?",))) or "?"
        msgs.append(f"{loc}: {err['msg']}")
    return msgs or [str(exc)]


def validate_post(path: Path, raw: dict[str, object], dir_name: str) -> list[LintError]:
    """Validate a single post: schema + filename ↔ frontmatter coupling."""
    errors: list[LintError] = []

    try:
        m = PostFrontmatter.model_validate(raw)
    except Exception as exc:
        for msg in _pydantic_errors(exc):
            errors.append(LintError(path, msg))
        return errors  # skip filename checks when fields are invalid

    # <slug>.<lang>.md coupling
    stem = path.stem  # e.g. "ola-jardim.pt" (strips only the last .md)
    parts = stem.rsplit(".", 1)
    if len(parts) != 2:
        errors.append(LintError(path, f"Filename must be <slug>.<lang>.md, got '{path.name}'"))
    else:
        slug_part, lang_part = parts
        if slug_part != m.slug:
            errors.append(LintError(
                path, f"Filename slug '{slug_part}' ≠ frontmatter Slug '{m.slug}'"
            ))
        if lang_part != m.lang:
            errors.append(LintError(
                path, f"Filename lang '{lang_part}' ≠ frontmatter Lang '{m.lang}'"
            ))

    if dir_name != m.translation_key:
        errors.append(LintError(
            path,
            f"Directory name '{dir_name}' ≠ frontmatter Translation_key '{m.translation_key}'"
        ))

    return errors


def validate_page(path: Path, raw: dict[str, object]) -> list[LintError]:
    """Validate a single page: schema only, no filename coupling."""
    errors: list[LintError] = []
    try:
        PageFrontmatter.model_validate(raw)
    except Exception as exc:
        for msg in _pydantic_errors(exc):
            errors.append(LintError(path, msg))
    return errors


# ---------------------------------------------------------------------------
# Cross-document group validation
# ---------------------------------------------------------------------------

def validate_post_group(
    dir_name: str,
    files: list[tuple[Path, dict[str, object]]],
) -> list[LintError]:
    """Check (Slug, Lang) uniqueness across siblings in a post directory."""
    errors: list[LintError] = []
    seen: dict[tuple[str, str], Path] = {}

    for path, raw in files:
        slug = str(raw.get("Slug", "")).strip()
        lang = str(raw.get("Lang", "")).strip().lower()
        if not slug or not lang:
            continue
        key = (slug, lang)
        if key in seen:
            errors.append(LintError(
                path,
                f"(Slug='{slug}', Lang='{lang}') already used by '{seen[key].name}'"
            ))
        else:
            seen[key] = path

    return errors


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def parse_frontmatter(path: Path) -> dict[str, object]:
    """Parse Pelican's Key: Value frontmatter (lines before the first blank line)."""
    metadata: dict[str, object] = {}
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                break
            if ": " in line:
                key, _, value = line.partition(": ")
                metadata[key.strip()] = value.strip()
    return metadata


def format_errors(errors: list[LintError]) -> str:
    """Group errors by file, sort by path, produce indented bullet output."""
    grouped: dict[Path, list[str]] = defaultdict(list)
    for err in errors:
        grouped[err.path].append(err.message)

    lines: list[str] = []
    for path in sorted(grouped):
        lines.append(str(path) + ":")
        for msg in grouped[path]:
            lines.append(f"  - {msg}")

    return "\n".join(lines)
