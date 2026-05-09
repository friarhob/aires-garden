import os
import tempfile
from pathlib import Path

_FIELD_ORDER = ["Title", "Slug", "Date", "Lang", "Translation_key", "Status", "Tags"]


def read_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    """Return (fields_dict, body_string) for a Pelican-style Markdown file."""
    text = path.read_text(encoding="utf-8")
    fields: dict[str, str] = {}
    lines = text.splitlines(keepends=True)
    i = 0
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n").rstrip("\r")
        if not stripped:
            i += 1
            break
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            fields[key.strip()] = value.strip()
        else:
            break
    body = "".join(lines[i:])
    return fields, body


def write_frontmatter(path: Path, fields: dict[str, str], body: str) -> None:
    """Write fields + body atomically. Field order follows _FIELD_ORDER."""
    ordered_keys = [k for k in _FIELD_ORDER if k in fields]
    extra_keys = [k for k in fields if k not in _FIELD_ORDER]
    lines = [f"{k}: {fields[k]}\n" for k in ordered_keys + extra_keys]
    lines.append("\n")
    lines.append(body)
    content = "".join(lines)

    dir_ = path.parent
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
