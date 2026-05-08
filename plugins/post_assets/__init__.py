"""
post_assets — copies colocated assets/ directories to the output.

Scans every directory under the content path that contains both Markdown
files with a Slug: header and an assets/ subdirectory.  Everything inside
assets/ is copied to <slug>/assets/ in the output for every language slug
defined by that post or page.  Runs on the `finalized` signal so it works
correctly after DELETE_OUTPUT_DIRECTORY rebuilds the tree.
"""

from pathlib import Path
import shutil

from pelican import signals


def _read_slug(md_file: Path) -> str | None:
    try:
        with md_file.open(encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped:
                    break
                if ":" in stripped:
                    key, _, value = stripped.partition(":")
                    if key.strip().lower() == "slug":
                        return value.strip()
    except OSError:
        pass
    return None


def _copy_post_assets(pelican):
    content_path = Path(pelican.settings["PATH"])
    output_path = Path(pelican.settings["OUTPUT_PATH"])

    for assets_dir in content_path.rglob("assets"):
        if not assets_dir.is_dir():
            continue

        slugs = {_read_slug(f) for f in assets_dir.parent.glob("*.md")} - {None}
        if not slugs:
            continue

        for asset in (f for f in assets_dir.rglob("*") if f.is_file()):
            rel = asset.relative_to(assets_dir)
            for slug in slugs:
                dest = output_path / slug / "assets" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(asset, dest)


def register():
    signals.finalized.connect(_copy_post_assets)
