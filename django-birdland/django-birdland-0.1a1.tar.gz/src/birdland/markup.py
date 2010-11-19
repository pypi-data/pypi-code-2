import re

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str, force_unicode
from django.core.urlresolvers import get_callable

_markups = None

# See what markup formatters are available

try:
    from docutils.core import publish_parts
except ImportError:
    publish_parts = None

try:
    from textile import textile
except ImportError:
    textile = None

try:
    from markdown2 import markdown
except ImportError:
    try:
        from markdown import markdown
    except ImportError:
        markdown = None

newline_re = re.compile(r'[\n\r\v\f]+')

# Markup formatters
do_nothing = lambda v: v

def format_linebreaks(value):
    paragraphs = newline_re.split(value)
    return '<p>%s</p>' % ('</p><p>'.join(paragraphs))

if publish_parts:
    def format_restructured_text(value):
        parts = publish_parts(source=value, writer_name='html4css1')
        return parts['fragment']

if textile:
    def format_textile(value):
        return force_unicode(textile(smart_str(value), encoding='utf-8', output='utf-8'))

if markdown:
    def format_markdown(value):
        return markdown(value, [], safe_mode=True)

def get_markups():
    """
    Return a list of 3-tuples with the db name, display name, and formatter
    callable for all available markup formatters.

    """
    global _markups
    if _markups is None:
        from birdland.conf import settings
        markup_candidates, markups = [], []
        markup_candidates.extend(getattr(settings, 'MARKUP_LANGS', []))
        markup_candidates.extend(getattr(settings, 'EXTRA_MARKUPS', []))
        for name, display, formatter in markup_candidates:
            try:
                formatter_callable = get_callable(formatter)
            except (ImportError, AttributeError):
                continue
            markups.append((name, display, formatter_callable))
        _markups = markups
    return _markups
