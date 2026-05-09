import typer

from frontmatter_lint.cli import main as frontmatter_lint_main


def lint() -> None:
    """Run frontmatter and body lint against the content tree."""
    try:
        frontmatter_lint_main(["content"])
    except SystemExit as exc:
        raise typer.Exit(int(exc.code) if exc.code is not None else 0) from exc
