from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from garden import prompts
from garden.content_index import find_by_slug, walk_content
from garden.frontmatter_io import read_frontmatter, write_frontmatter
from garden.validation import ValidationError, validate_lang, validate_slug, validate_title

_CONTENT_ROOT = Path("content")


def translate(
    slug: Annotated[str, typer.Argument(help="Source file's Slug value")],
    to: Annotated[str, typer.Option("--to", help="Target ISO 639-1 language code")],
    slug_new: Annotated[Optional[str], typer.Option("--slug", help="Slug for the new file")] = None,
    title_new: Annotated[Optional[str], typer.Option("--title", help="Title for the new file")] = None,
) -> None:
    """Create a paired-language file from an existing source."""
    try:
        validate_lang(to)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--to") from exc

    index = walk_content(_CONTENT_ROOT)
    source = find_by_slug(index, slug)
    if source is None:
        typer.echo(f"Error: no file found with Slug: {slug!r}", err=True)
        raise typer.Exit(1)

    # Prompt for missing optional fields
    if title_new is None:
        title_new = prompts.prompt_text(f"Title in {to!r}?")
    try:
        validate_title(title_new)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--title") from exc

    if slug_new is None:
        if prompts.is_tty():
            slug_new = prompts.prompt_text(f"Slug in {to!r}?", default=source.slug)
        else:
            slug_new = source.slug
    try:
        validate_slug(slug_new)
    except ValidationError as exc:
        raise typer.BadParameter(str(exc), param_hint="--slug") from exc

    source_fields, body = read_frontmatter(source.path)

    new_fields: dict[str, str] = {
        "Title": title_new,
        "Slug": slug_new,
        "Lang": to,
        "Translation_key": source.translation_key,
        "Status": "draft",
    }
    if "Date" in source_fields:
        new_fields["Date"] = source_fields["Date"]
    if "Tags" in source_fields:
        new_fields["Tags"] = source_fields["Tags"]

    target = _target_path(source.path, slug_new, to, source.kind)

    if target.exists():
        typer.echo(f"Error: {target} already exists.", err=True)
        raise typer.Exit(1)

    write_frontmatter(target, new_fields, body)
    typer.echo(f"Created {target}")


def _target_path(source_path: Path, slug_new: str, lang: str, kind: str) -> Path:
    filename = f"{slug_new}.{lang}.md"
    if kind == "post":
        return source_path.parent / filename
    if kind == "page":
        return source_path.parent / filename
    # tag-prose: same tag directory
    return source_path.parent / filename
