import typer

app = typer.Typer(
    name="garden",
    help="Content authoring CLI for aires-garden.",
    no_args_is_help=True,
)


def _register_commands() -> None:
    from garden.commands import lint, new, translate, lifecycle  # noqa: F401

    app.command("new")(new.new)
    app.command("translate")(translate.translate)
    app.command("publish")(lifecycle.publish)
    app.command("draft")(lifecycle.draft)
    app.command("archive")(lifecycle.archive)
    app.command("lint")(lint.lint)


_register_commands()
