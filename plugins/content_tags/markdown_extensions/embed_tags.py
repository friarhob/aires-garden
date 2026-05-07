"""Python-Markdown preprocessor extension that expands embed tags.

Runs at priority 24 — after fenced_code_block (25) has already replaced
fenced code blocks with placeholders, and after meta (27) has stripped
frontmatter.  Lines with 4+ spaces of indentation are skipped by the
EMBED_RE pattern itself (requires at most 3 leading spaces).
"""

from markdown import Extension
from markdown.preprocessors import Preprocessor

from content_tags.parser import EMBED_RE, parse_args
from content_tags.registry import REGISTRY


class _EmbedTagsPreprocessor(Preprocessor):
    def run(self, lines: list[str]) -> list[str]:
        result: list[str] = []
        for line in lines:
            m = EMBED_RE.match(line)
            if m:
                name = m.group(1)
                if name in REGISTRY:
                    args = parse_args(m.group(2))
                    html = REGISTRY[name].render(args)
                    result.extend(html.splitlines())
                    continue
            result.append(line)
        return result


class EmbedTagsExtension(Extension):
    def extendMarkdown(self, md: object) -> None:
        md.preprocessors.register(  # type: ignore[attr-defined]
            _EmbedTagsPreprocessor(md), 'content_tags_embeds', 24
        )


def makeExtension(**kwargs: object) -> EmbedTagsExtension:
    return EmbedTagsExtension(**kwargs)
