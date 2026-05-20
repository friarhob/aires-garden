from __future__ import annotations

import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Annotated, Optional

import typer

from garden import prompts
from garden.frontmatter_io import read_frontmatter, write_frontmatter
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


_INTRO_SCOPES = ("all", "lang")


def new(
    kind: Annotated[Optional[str], typer.Option("--kind", help="post | page | tag-prose | intro")] = None,
    title: Annotated[Optional[str], typer.Option("--title", help="Post title")] = None,
    slug: Annotated[Optional[str], typer.Option("--slug", help="URL slug (kebab-case)")] = None,
    lang: Annotated[Optional[str], typer.Option("--lang", help="ISO 639-1 language code")] = None,
    tag: Annotated[Optional[str], typer.Option("--tag", help="Tag name (tag-prose only)")] = None,
    shape: Annotated[Optional[str], typer.Option("--shape", help="Prose shape: all | lang (tag-prose only)")] = None,
    create_tag: Annotated[bool, typer.Option("--create-tag/--no-create-tag", help="Create tag dir if missing (tag-prose, non-interactive)")] = False,
    scope: Annotated[Optional[str], typer.Option("--scope", help="Intro scope: all | lang (intro only)")] = None,
) -> None:
    """Scaffold a new post, page, tag-prose, or intro file."""
    # --- kind ---
    if kind is None:
        kind = prompts.prompt_select("Kind?", list(KINDS))
    try:
        validate_kind(kind)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--kind") from exc

    # --- title (tag-prose defers this until each tag is known) ---
    if kind not in ("tag-prose",):
        if title is None:
            title = prompts.prompt_text("Title?")
        try:
            validate_title(title)
        except ValidationError as exc:
            raise typer.BadParameter(str(exc), param_hint="--title") from exc

    # --- slug (not applicable for tag-prose or intro) ---
    if kind not in ("tag-prose", "intro"):
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
    elif kind == "intro":
        _create_intro(title, lang, scope)
    else:
        _create_tag_prose(title, lang, tag, shape, create_tag)  # title may be None here


def _create_post(title: str, slug: str, lang: str) -> None:
    post_dir = _CONTENT_ROOT / "posts" / slug
    target = post_dir / f"{slug}.{lang}.md"
    _refuse_if_exists(target)
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / "assets").mkdir(exist_ok=True)

    tags_str = ""
    if prompts.is_tty():
        available = _available_raw_tags(_CONTENT_ROOT)
        choices = available + [_NEW_TAG_SENTINEL]
        selected = prompts.prompt_checkbox("Tags? (optional, space to select)", choices)
        resolved: list[str] = []
        for item in selected:
            if item == _NEW_TAG_SENTINEL:
                new_tag = prompts.prompt_text("New tag name:")
                if new_tag.strip():
                    resolved.append(new_tag.strip())
            else:
                resolved.append(item)
        tags_str = ", ".join(resolved)

    fields = {
        "Title": title,
        "Slug": slug,
        "Date": date.today().isoformat(),
        "Lang": lang,
        "Translation_key": slug,
        "Status": "draft",
        "Tags": tags_str,
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
        "Lang": lang,
        "Status": "hidden",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


def _create_intro(title: str, lang: str, scope: str | None) -> None:
    if scope is None:
        if prompts.is_tty():
            scope = prompts.prompt_select("Scope?", list(_INTRO_SCOPES))
        else:
            raise typer.BadParameter(
                "--scope is required in non-interactive mode for --kind intro.",
                param_hint="--scope",
            )
    if scope not in _INTRO_SCOPES:
        raise typer.BadParameter(
            f"scope must be one of {{{', '.join(_INTRO_SCOPES)}}}, got: {scope!r}",
            param_hint="--scope",
        )
    intro_dir = _CONTENT_ROOT / "intro"
    intro_dir.mkdir(parents=True, exist_ok=True)
    target = intro_dir / f"{scope}.{lang}.md"
    _refuse_if_exists(target)
    fields = {
        "Title": title,
        "Lang": lang,
        "Status": "hidden",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


_NEW_TAG_SENTINEL = "[new tag]"


def _available_raw_tags(content_root: Path) -> list[str]:
    """Return sorted display-form tag strings from existing posts and tag-prose dirs."""
    seen: dict[str, str] = {}  # slug → first display form seen
    posts_dir = content_root / "posts"
    if posts_dir.exists():
        for md in sorted(posts_dir.rglob("*.md")):
            try:
                fields, _ = read_frontmatter(md)
                for raw in fields.get("Tags", "").split(","):
                    raw = raw.strip()
                    if raw:
                        try:
                            slug = _slugify(raw)
                            if slug not in seen:
                                seen[slug] = raw
                        except ValidationError:
                            pass
            except Exception:
                pass
    tag_prose_dir = content_root / "tag-prose"
    if tag_prose_dir.exists():
        for d in sorted(tag_prose_dir.iterdir()):
            if d.is_dir() and d.name not in seen:
                seen[d.name] = d.name
    return sorted(seen.values(), key=str.lower)


def _tag_slugs_from_posts(content_root: Path) -> set[str]:
    """Return slug forms of every tag referenced in any post frontmatter."""
    slugs: set[str] = set()
    posts_dir = content_root / "posts"
    if not posts_dir.exists():
        return slugs
    for md in posts_dir.rglob("*.md"):
        try:
            fields, _ = read_frontmatter(md)
            for raw_tag in fields.get("Tags", "").split(","):
                raw_tag = raw_tag.strip()
                if raw_tag:
                    try:
                        slugs.add(_slugify(raw_tag))
                    except ValidationError:
                        pass
        except Exception:
            pass
    return slugs


def _create_tag_prose(
    title: str | None,
    lang: str,
    tag: str | None,
    shape: str | None,
    create_tag: bool,
) -> None:
    tag_prose_root = _CONTENT_ROOT / "tag-prose"
    existing_prose_tags = {d.name for d in tag_prose_root.iterdir() if d.is_dir()} if tag_prose_root.exists() else set()
    post_tags = _tag_slugs_from_posts(_CONTENT_ROOT)
    all_tags = sorted(existing_prose_tags | post_tags)

    # 1. Resolve tag first so title suggestion can read from existing files.
    if tag is None:
        if prompts.is_tty():
            choices = all_tags + [_NEW_TAG_SENTINEL]
            chosen = prompts.prompt_select("Tag?", choices)
            if chosen == _NEW_TAG_SENTINEL:
                tag = prompts.prompt_text("New tag name (kebab-case):")
            else:
                tag = chosen
        else:
            raise typer.BadParameter("--tag is required in non-interactive mode.", param_hint="--tag")

    # 2. Suggest title from any existing file in the tag directory.
    tag_dir = _CONTENT_ROOT / "tag-prose" / tag
    title_default: str | None = None
    if tag_dir.exists():
        for existing in sorted(tag_dir.glob("*.md")):
            try:
                fields, _ = read_frontmatter(existing)
                if fields.get("Title"):
                    title_default = fields["Title"]
                    break
            except Exception:
                pass

    # 3. Resolve title (may have been passed via --title flag).
    if title is None:
        if prompts.is_tty():
            title = prompts.prompt_text("Title?", default=title_default)
        else:
            raise typer.BadParameter("--title is required in non-interactive mode.", param_hint="--title")
    try:
        validate_title(title)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--title") from exc

    if shape is None:
        shape = prompts.prompt_select("Prose shape?", list(PROSE_SHAPES))
    if shape not in PROSE_SHAPES:
        raise typer.BadParameter(
            f"shape must be one of {{{', '.join(PROSE_SHAPES)}}}, got: {shape!r}",
            param_hint="--shape",
        )

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
        "Lang": lang,
        "Status": "hidden",
    }
    write_frontmatter(target, fields, "")
    typer.echo(f"Created {target}")


def _refuse_if_exists(path: Path) -> None:
    if path.exists():
        typer.echo(f"Error: {path} already exists.", err=True)
        raise typer.Exit(1)
