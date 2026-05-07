from html import escape
from content_tags.registry import REGISTRY, EmbedTag

_DEFAULT_HEIGHT = '400'


def _render(args: dict[str, str]) -> str:
    src = escape(args['src'])
    title = escape(args['title'])
    height = escape(args.get('height', _DEFAULT_HEIGHT))
    return (
        '<div class="embed embed-iframe">\n'
        f'<iframe src="{src}"\n'
        f'        title="{title}"\n'
        '        loading="lazy"\n'
        '        referrerpolicy="no-referrer-when-downgrade"\n'
        '        sandbox="allow-scripts allow-same-origin allow-popups allow-forms"\n'
        f'        style="height: {height}px"></iframe>\n'
        '</div>'
    )


REGISTRY['iframe'] = EmbedTag(
    required_args=('src', 'title'),
    optional_args=('height',),
    render=_render,
)
