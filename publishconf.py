import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *  # noqa: F401, F403

SITEURL = "https://fernandoaires.org"
RELATIVE_URLS = False

DRAFT_URL = ""
DRAFT_SAVE_AS = ""
DRAFT_LANG_URL = ""
DRAFT_LANG_SAVE_AS = ""

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"
