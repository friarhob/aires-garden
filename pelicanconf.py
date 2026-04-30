PLUGIN_PATHS = ["plugins"]
PLUGINS = ["frontmatter_lint"]

AUTHOR = "Fernando Aires"
SITENAME = "aires-garden"
SITEURL = ""

PATH = "content"
THEME = "themes/garden"

TIMEZONE = "Europe/Lisbon"
DEFAULT_LANG = "en"

ARTICLE_URL = "{slug}/"
ARTICLE_SAVE_AS = "{slug}/index.html"

DELETE_OUTPUT_DIRECTORY = True
DEFAULT_DATE = "fs"

STATIC_PATHS = ["extra/CNAME", "extra/robots.txt"]
EXTRA_PATH_METADATA = {
    "extra/CNAME": {"path": "CNAME"},
    "extra/robots.txt": {"path": "robots.txt"},
}

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
