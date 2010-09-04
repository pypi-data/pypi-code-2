"""
An interface to html5lib.
"""

import urllib
from html5lib import HTMLParser as _HTMLParser
from lxml import etree
from lxml.html import _contains_block_level_tag, XHTML_NAMESPACE
from lxml.html._html5builder import TreeBuilder

# python3 compatibility
try:
    _strings = basestring
except NameError:
    _strings = (bytes, str)


class HTMLParser(_HTMLParser):
    """An html5lib HTML parser with lxml as tree."""

    def __init__(self, strict=False):
        _HTMLParser.__init__(self, strict=strict, tree=TreeBuilder)


try:
    from html5lib import XHTMLParser as _XHTMLParser
except ImportError:
    pass
else:
    class XHTMLParser(_XHTMLParser):
        """An html5lib XHTML Parser with lxml as tree."""

        def __init__(self, strict=False):
            _XHTMLParser.__init__(self, strict=strict, tree=TreeBuilder)

    xhtml_parser = XHTMLParser()


def _find_tag(tree, tag):
    elem = tree.find(tag)
    if elem is not None:
        return elem
    return tree.find('{%s}%s' % (XHTML_NAMESPACE, tag))


def document_fromstring(html, guess_charset=True, parser=None):
    """Parse a whole document into a string."""
    if not isinstance(html, _strings):
        raise TypeError('string required')

    if parser is None:
        parser = html_parser

    return parser.parse(html, useChardet=guess_charset).getroot()


def fragments_fromstring(html, no_leading_text=False,
                         guess_charset=False, parser=None):
    """Parses several HTML elements, returning a list of elements.

    The first item in the list may be a string.  If no_leading_text is true,
    then it will be an error if there is leading text, and it will always be
    a list of only elements.

    If `guess_charset` is `True` and the text was not unicode but a
    bytestring, the `chardet` library will perform charset guessing on the
    string.
    """
    if not isinstance(html, _strings):
        raise TypeError('string required')

    if parser is None:
        parser = html_parser

    children = parser.parseFragment(html, 'div', useChardet=guess_charset)
    if children and isinstance(children[0], _strings):
        if no_leading_text:
            if children[0].strip():
                raise etree.ParserError('There is leading text: %r' %
                                        children[0])
            del children[0]
    return children


def fragment_fromstring(html, create_parent=False,
                        guess_charset=False, parser=None):
    """Parses a single HTML element; it is an error if there is more than
    one element, or if anything but whitespace precedes or follows the
    element.

    If create_parent is true (or is a tag name) then a parent node
    will be created to encapsulate the HTML in a single element.
    """
    if not isinstance(html, _strings):
        raise TypeError('string required')

    if create_parent:
        container = create_parent or 'div'
        html = '<%s>%s</%s>' % (container, html, container)

    children = fragments_fromstring(html, True, guess_charset, parser)
    if not children:
        raise etree.ParserError('No elements found')
    if len(children) > 1:
        raise etree.ParserError('Multiple elements found')

    result = children[0]
    if result.tail and result.tail.strip():
        raise etree.ParserError('Element followed by text: %r' % result.tail)
    result.tail = None
    return result


def fromstring(html, guess_charset=True, parser=None):
    """Parse the html, returning a single element/document.

    This tries to minimally parse the chunk of text, without knowing if it
    is a fragment or a document.

    base_url will set the document's base_url attribute (and the tree's docinfo.URL)
    """
    if not isinstance(html, _strings):
        raise TypeError('string required')
    doc = document_fromstring(html, parser=parser,
                              guess_charset=guess_charset)

    # document starts with doctype or <html>, full document!
    start = html[:50].lstrip().lower()
    if start.startswith('<html') or start.startswith('<!doctype'):
        return doc

    head = _find_tag(doc, 'head')

    # if the head is not empty we have a full document
    if len(head):
        return doc

    body = _find_tag(doc, 'body')

    # The body has just one element, so it was probably a single
    # element passed in
    if (len(body) == 1 and (not body.text or not body.text.strip())
        and (not body[-1].tail or not body[-1].tail.strip())):
        return body[0]

    # Now we have a body which represents a bunch of tags which have the
    # content that was passed in.  We will create a fake container, which
    # is the body tag, except <body> implies too much structure.
    if _contains_block_level_tag(body):
        body.tag = 'div'
    else:
        body.tag = 'span'
    return body


def parse(filename_url_or_file, guess_charset=True, parser=None):
    """Parse a filename, URL, or file-like object into an HTML document
    tree.  Note: this returns a tree, not an element.  Use
    ``parse(...).getroot()`` to get the document root.
    """
    if parser is None:
        parser = html_parser
    if isinstance(filename_url_or_file, basestring):
        fp = urllib.urlopen(filename_url_or_file)
    else:
        fp = filename_url_or_file
    return parser.parse(fp, useChardet=guess_charset)


html_parser = HTMLParser()
