import sys

import questionary
import typer


def is_tty() -> bool:
    return sys.stdin.isatty()


def _require_tty(op: str) -> None:
    if not is_tty():
        raise typer.BadParameter(
            f"{op}: missing required argument — pass it as a flag in non-interactive mode."
        )


def prompt_text(message: str, default: str | None = None) -> str:
    _require_tty(message)
    result = questionary.text(message, default=default or "").ask()
    if result is None:
        raise typer.Abort()
    return result


def prompt_select(message: str, choices: list[str]) -> str:
    _require_tty(message)
    result = questionary.select(message, choices=choices).ask()
    if result is None:
        raise typer.Abort()
    return result


def prompt_confirm(message: str, default: bool | None = None) -> bool:
    _require_tty(message)
    result = questionary.confirm(message, default=default if default is not None else False).ask()
    if result is None:
        raise typer.Abort()
    return result
