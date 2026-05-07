"""dev_drafts — promote drafts to published articles in dev builds.

Hooks article_generator_pretaxonomy so the promoted articles are visible
to every downstream plugin (including i18n_grouping, which hooks
article_generator_finalized — a later signal).
"""
import logging

from pelican import signals

logger = logging.getLogger(__name__)


def _on_pretaxonomy(generator):
    if not generator.settings.get("DRAFTS_AS_PUBLISHED"):
        return

    drafts = list(getattr(generator, "drafts", []) or [])
    drafts_translations = list(getattr(generator, "drafts_translations", []) or [])

    if not drafts and not drafts_translations:
        return

    for article in drafts + drafts_translations:
        article.status = "published"

    generator.articles = list(generator.articles) + drafts
    generator.translations = list(generator.translations) + drafts_translations
    generator.drafts = []
    generator.drafts_translations = []

    # Sanity-check: after promotion there must be no residual draft-status
    # articles — that would signal a regression in signal ordering.
    residual = [a for a in generator.articles + generator.translations if getattr(a, "status", "") == "draft"]
    if residual:
        logger.warning(
            "dev_drafts: %d article(s) still carry status='draft' after promotion — "
            "check signal-registration order (dev_drafts must precede i18n_grouping).",
            len(residual),
        )
    else:
        logger.debug(
            "dev_drafts: promoted %d draft(s) and %d draft translation(s) to published.",
            len(drafts),
            len(drafts_translations),
        )


def register():
    signals.article_generator_pretaxonomy.connect(_on_pretaxonomy)
