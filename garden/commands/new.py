from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Annotated, Optional

import typer

from garden import prompts
from garden.frontmatter_io import write_frontmatter
from garden.validation import (
    KINDS,
    ValidationError,
    validate_kind,
    validate_lang,
    validate_slug,
    validate_title,
)

_CONTENT_ROOT = Path("content")

PROSE_SHAPES = ("all", "lang")


def _slugify(title: str) -> str:
    slug = unicodedata.normalize("NFD", title.lower().strip())
    slug = "".join(c for c in slug if unicodedata.category(c) != "Mn")
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    if not slug:
        raise ValidationError(f"title {title!r} produces an empty slug after normalisation")
    return slug


def new(
    kind: Annotated[Optional[str], typer.Option("--kind", help="post | page | tag-prose")] = None,
    title: Annotated[Optional[str], typer.Option("--title", help="Post title")] = None,
    slug: Annotated[Optional[str], typer.Option("--slug", help="URL slug (kebab-case)")] = None,
    lang: Annotated[Optional[str], typer.Option("--lang", help="ISO 639-1 language code")] = None,
    tag: Annotated[Optional[str], typer.Option("--tag", help="Tag name (tag-prose only)")] = None,
    shape: Annotated[Optional[str], typer.Option("--shape", help="Prose shape: all | lang (tag-prose only)")] = None,
    create_tag: Annotated[bool, typer.Option("--create-tag/--no-create-tag", help="Create tag dir if missing (tag-prose, non-interactive)")] = False,
) -> None:
    """Scaffold a new post, page, or tag-prose file."""
    # --- kind ---
    if kind is None:
        kind = prompts.prompt_select("Kind?", list(KINDS))
    try:
        validate_kind(kind)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--kind") from exc

    # --- title ---
    if title is None:
        title = prompts.prompt_text("Title?")
    try:
        validate_title(title)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--title") from exc

    # --- slug ---
    if slug is None:
        try:
            default_slug = _slugify(title)
        except ValidationError as exc:
            raise typer.BadParameter(str(exc), param_hint="--title") from exc
        if prompts.is_tty():
            slug = prompts.prompt_text("Slug?", default=default_slug)
        else:
            slug = default_slug
    try:
        validate_slug(slug)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--slug") from exc

    # --- lang ---
    if lang is None:
        lang = prompts.prompt_text("Lang? (ISO 639-1, e.g. en)")
    try:
        validate_lang(lang)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--lang") from exc

    if kind == "post":
        _create_post(title, slug, lang)
    elif kind == "page":
        _create_page(title, slug, lang)
    else:
        _create_tag_prose(title, slug, lang, tag, shape, create_tag)


def _create_post(title: str, slug: str, lang: str) -> None:
    post_dir = _CONTENT_ROOT / "posts" / slug
    target = post_dir / f"{slug}.{lang}.md"
    _refuse_if_exists(target)
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / "assets").mkdir(exist_ok=True)
    fields = {
        "Title": title,
        "Slug": slug,
        "Date": date.today().isoformat(),
        "Lang": lang,
        "Translation_key": slug,
        "Status": "draft",
        "Tags": "",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


def _create_page(title: str, slug: str, lang: str) -> None:
    pages_dir = _CONTENT_ROOT / "pages"
    target = pages_dir / f"{slug}.{lang}.md"
    _refuse_if_exists(target)
    pages_dir.mkdir(parents=True, exist_ok=True)
    fields = {
        "Title": title,
        "Slug": slug,
        "Lang": lang,
        "Status": "hidden",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


def _create_tag_prose(
    title: str,
    slug: str,
    lang: str,
    tag: str | None,
    shape: str | None,
    create_tag: bool,
) -> None:
    if tag is None:
        tag = prompts.prompt_text("Tag name?")
    if shape is None:
        shape = prompts.prompt_select("Prose shape?", list(PROSE_SHAPES))
    if shape not in PROSE_SHAPES:
        raise typer.BadParameter(
            f"shape must be one of {{{', '.join(PROSE_SHAPES)}}}, got: {shape!r}",
            param_hint="--shape",
        )

    tag_dir = _CONTENT_ROOT / "tag-prose" / tag
    if not tag_dir.exists():
        if prompts.is_tty() and not create_tag:
            confirmed = prompts.prompt_confirm(f"Tag directory {tag_dir} does not exist. Create it?", default=True)
            if not confirmed:
                raise typer.Abort()
        elif not create_tag:
            raise typer.BadParameter(
                f"Tag directory {tag_dir} does not exist. Pass --create-tag to create it.",
                param_hint="--tag",
            )
        tag_dir.mkdir(parents=True, exist_ok=True)

    target = tag_dir / f"{shape}.{lang}.md"
    _refuse_if_exists(target)
    fields = {
        "Title": title,
        "Slug": slug,
        "Lang": lang,
        "Status": "hidden",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


def _refuse_if_exists(path: Path) -> None:
    if path.exists():
        typer.echo(f"Error: {path} already exists.", err=True)
        raise typer.Exit(1)
