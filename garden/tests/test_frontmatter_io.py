import pytest

from garden.frontmatter_io import read_frontmatter, write_frontmatter


SAMPLE = """\
Title: My Post
Slug: my-post
Date: 2026-05-09
Lang: en
Translation_key: my-post
Status: draft

This is the body.

With two paragraphs.
"""


def test_read_frontmatter(tmp_path):
    f = tmp_path / "post.md"
    f.write_text(SAMPLE, encoding="utf-8")
    fields, body = read_frontmatter(f)
    assert fields["Title"] == "My Post"
    assert fields["Slug"] == "my-post"
    assert fields["Status"] == "draft"
    assert body.startswith("This is the body.")


def test_round_trip(tmp_path):
    f = tmp_path / "post.md"
    f.write_text(SAMPLE, encoding="utf-8")
    fields, body = read_frontmatter(f)
    write_frontmatter(f, fields, body)
    fields2, body2 = read_frontmatter(f)
    assert fields == fields2
    assert body == body2


def test_field_order(tmp_path):
    f = tmp_path / "post.md"
    fields = {
        "Status": "draft",
        "Title": "X",
        "Lang": "en",
        "Slug": "x",
        "Date": "2026-01-01",
        "Translation_key": "x",
    }
    write_frontmatter(f, fields, "body\n")
    lines = f.read_text(encoding="utf-8").splitlines()
    keys = [line.split(":")[0] for line in lines if ":" in line]
    assert keys == ["Title", "Slug", "Date", "Lang", "Translation_key", "Status"]


def test_atomic_write(tmp_path):
    f = tmp_path / "post.md"
    f.write_text(SAMPLE, encoding="utf-8")
    fields, body = read_frontmatter(f)
    fields["Status"] = "published"
    write_frontmatter(f, fields, body)
    fields2, _ = read_frontmatter(f)
    assert fields2["Status"] == "published"
    # No stray temp files left
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == []


def test_no_body(tmp_path):
    f = tmp_path / "post.md"
    f.write_text("Title: X\nSlug: x\n\n", encoding="utf-8")
    fields, body = read_frontmatter(f)
    assert fields["Title"] == "X"
    assert body == ""
