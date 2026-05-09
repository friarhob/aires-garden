from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer

from garden import prompts
from garden.content_index import ContentFile, find_by_slug, find_translations, walk_content
from garden.frontmatter_io import read_frontmatter, write_frontmatter

_CONTENT_ROOT = Path("content")


def _resolve_targets(
    slug: str,
    all_translations: bool | None,
    content_root: Path,
) -> list[ContentFile]:
    index = walk_content(content_root)
    source = find_by_slug(index, slug)
    if source is None:
        typer.echo(f"Error: no file found with Slug: {slug!r}", err=True)
        raise typer.Exit(1)

    _require_post(source)

    if all_translations is None:
        if prompts.is_tty():
            all_translations = prompts.prompt_confirm(
                "Apply to all translations?", default=False
            )
        else:
            typer.echo(
                "Error: --all-translations or --no-all-translations must be supplied "
                "explicitly in non-interactive mode.",
                err=True,
            )
            raise typer.Exit(1)

    if all_translations:
        return find_translations(index, source.translation_key)
    return [source]


def _require_post(cf: ContentFile) -> None:
    if cf.kind != "post":
        typer.echo(
            f"Error: lifecycle commands apply only to posts; "
            f"{cf.path} is a {cf.kind!r}.",
            err=True,
        )
        raise typer.Exit(1)


def _validate_transition(
    targets: list[ContentFile],
    allowed_from: set[str],
    force: bool,
) -> list[ContentFile]:
    if force:
        return []
    refused = [t for t in targets if t.status not in allowed_from]
    return refused


def _apply_transition(targets: list[ContentFile], to_state: str) -> None:
    for cf in targets:
        fields, body = read_frontmatter(cf.path)
        fields["Status"] = to_state
        write_frontmatter(cf.path, fields, body)
        typer.echo(f"  {cf.path}: {cf.status} → {to_state}")


def _run_lifecycle(
    slug: str,
    all_translations: bool | None,
    force: bool,
    allowed_from: set[str],
    to_state: str,
    refusal_hint: str,
) -> None:
    targets = _resolve_targets(slug, all_translations, _CONTENT_ROOT)
    refused = _validate_transition(targets, allowed_from, force)
    if refused:
        typer.echo("Error: the following files cannot transition:", err=True)
        for cf in refused:
            typer.echo(f"  {cf.path}: Status is {cf.status!r}. {refusal_hint}", err=True)
        raise typer.Exit(1)
    _apply_transition(targets, to_state)


def publish(
    slug: Annotated[str, typer.Argument(help="Slug of the file to publish")],
    all_translations: Annotated[Optional[bool], typer.Option("--all-translations/--no-all-translations", help="Apply to every translation")] = None,
    force: Annotated[bool, typer.Option("--force", help="Bypass refusal checks")] = False,
) -> None:
    """Flip a draft post to published."""
    _run_lifecycle(
        slug, all_translations, force,
        allowed_from={"draft"},
        to_state="published",
        refusal_hint="Only draft files can be published. Pass --force to bypass.",
    )


def draft(
    slug: Annotated[str, typer.Argument(help="Slug of the file to revert to draft")],
    all_translations: Annotated[Optional[bool], typer.Option("--all-translations/--no-all-translations", help="Apply to every translation")] = None,
    force: Annotated[bool, typer.Option("--force", help="Bypass refusal checks")] = False,
) -> None:
    """Flip a published post back to draft."""
    _run_lifecycle(
        slug, all_translations, force,
        allowed_from={"published"},
        to_state="draft",
        refusal_hint="Only published files can be reverted to draft. Pass --force to bypass.",
    )


def archive(
    slug: Annotated[str, typer.Argument(help="Slug of the file to archive")],
    all_translations: Annotated[Optional[bool], typer.Option("--all-translations/--no-all-translations", help="Apply to every translation")] = None,
    force: Annotated[bool, typer.Option("--force", help="Bypass refusal checks")] = False,
) -> None:
    """Flip a published post to hidden (archived)."""
    _run_lifecycle(
        slug, all_translations, force,
        allowed_from={"published"},
        to_state="hidden",
        refusal_hint="Only published files can be archived. Pass --force to bypass.",
    )
