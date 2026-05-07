"""In-tree figure-caption extension.

Promotes ``![alt](src "caption")`` to
``<figure><img …><figcaption>caption</figcaption></figure>``
when the Markdown image carries a title attribute.
"""

import xml.etree.ElementTree as ET

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class _FigureCaptionTreeprocessor(Treeprocessor):
    def run(self, root: ET.Element) -> None:
        self._process(root)

    def _process(self, element: ET.Element) -> None:
        i = 0
        while i < len(element):
            child = element[i]
            if child.tag == 'p' and self._is_solo_titled_img(child):
                element.remove(child)
                element.insert(i, self._make_figure(child))
            else:
                self._process(child)
            i += 1

    @staticmethod
    def _is_solo_titled_img(p: ET.Element) -> bool:
        children = list(p)
        if len(children) != 1 or children[0].tag != 'img':
            return False
        img = children[0]
        if not img.get('title'):
            return False
        if p.text and p.text.strip():
            return False
        if img.tail and img.tail.strip():
            return False
        return True

    @staticmethod
    def _make_figure(p: ET.Element) -> ET.Element:
        img = p[0]
        img.tail = None
        fig = ET.Element('figure')
        fig.append(img)
        caption = ET.SubElement(fig, 'figcaption')
        caption.text = img.get('title')
        fig.tail = p.tail
        return fig


class FigureCaptionExtension(Extension):
    def extendMarkdown(self, md: object) -> None:
        md.treeprocessors.register(  # type: ignore[attr-defined]
            _FigureCaptionTreeprocessor(md), 'figure_caption', 12
        )


def makeExtension(**kwargs: object) -> FigureCaptionExtension:
    return FigureCaptionExtension(**kwargs)
