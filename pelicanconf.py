PLUGIN_PATHS = ["plugins"]
PLUGINS = ["frontmatter_lint", "i18n_grouping", "multilingual_404", "dev_drafts", "tag_pages", "content_tags", "post_assets"]

MARKDOWN = {
    "extensions": [
        "markdown.extensions.extra",
        "markdown.extensions.admonition",
        "markdown.extensions.codehilite",
    ],
    "extension_configs": {
        "markdown.extensions.codehilite": {
            "css_class": "highlight",
            "linenums": False,
        },
    },
    "output_format": "html5",
}

AUTHOR = "Fernando Aires"
SITENAME = "aires-garden"
SITEURL = ""

PATH = "content"
THEME = "themes/garden"

TIMEZONE = "Europe/Lisbon"
DEFAULT_LANG = "en"

ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"
ARTICLE_LANG_URL = "{slug}/"
ARTICLE_LANG_SAVE_AS = "{slug}/index.html"

ARTICLE_EXCLUDES = ["tag-prose"]

HIDDEN_ARTICLE_URL = "{slug}/"
HIDDEN_ARTICLE_SAVE_AS = "{slug}/index.html"
HIDDEN_ARTICLE_LANG_URL = "{slug}/"
HIDDEN_ARTICLE_LANG_SAVE_AS = "{slug}/index.html"

TAG_URL = ""
TAG_SAVE_AS = ""
TAGS_URL = ""
TAGS_SAVE_AS = ""

DRAFTS_AS_PUBLISHED = True

DELETE_OUTPUT_DIRECTORY = True
DEFAULT_DATE = "fs"

STATIC_PATHS = ["extra/CNAME", "extra/robots.txt"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/robots.txt": {"path": "robots.txt"},
}

FEED_ATOM = None
TRANSLATION_FEED_ATOM = "feeds/{lang}.atom.xml"
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
