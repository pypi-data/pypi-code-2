from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site


def _tagging_available():
    """Checks if ``tagging`` is installed."""
    if 'tagging' in settings.INSTALLED_APPS:
        try:
            import tagging
            return True
        except ImportError:
            pass
    return False

def _backlinks_available():
    """Checks if ``backlinks`` is installed."""
    if 'backlinks' in settings.INSTALLED_APPS:
        try:
            import backlinks
            return True
        except ImportError:
            pass
    return False

BACKLINKS_ENABLED = _backlinks_available
BLOG_NAME = lambda: Site.objects.get_current().name
DEFAULT_MARKUP_LANG = 'rawhtml'
MARKUP_LANGS = (
    ('rawhtml', _(u'Raw HTML'), 'birdland.markup.do_nothing'),
    ('plaintext', _(u'Plain Text'), 'birdland.markup.do_nothing'),
    ('linebreaks', _(u'Plain Text with Linebreaks'), 'birdland.markup.format_linebreaks'),
    ('rest', u'reStructured Text', 'birdland.markup.format_restructured_text'),
    ('textile', u'Textile', 'birdland.markup.format_textile'),
    ('markdown', u'Markdown', 'birdland.markup.format_markdown'),
)
NUM_ENTRIES_IN_FEEDS = 20
PAGINATE_BY = 20
TAGGING_ENABLED = _tagging_available


