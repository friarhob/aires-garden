from html import escape
from content_tags.registry import REGISTRY, EmbedTag


def _render(args: dict[str, str]) -> str:
    vid_id = escape(args['id'])
    src = f'https://www.youtube-nocookie.com/embed/{vid_id}?rel=0'
    if 'start' in args:
        src += f'&amp;start={escape(args["start"])}'
    return (
        '<div class="embed embed-youtube">\n'
        f'<iframe src="{src}"\n'
        '        title="YouTube video"\n'
        '        loading="lazy"\n'
        '        referrerpolicy="strict-origin-when-cross-origin"\n'
        '        allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture"\n'
        '        allowfullscreen></iframe>\n'
        '</div>'
    )


REGISTRY['youtube'] = EmbedTag(
    required_args=('id',),
    optional_args=('start',),
    render=_render,
)
