"""
DEFAULT_BLACKLIST

* script, which can contain malicious script.
* applet, embed, and object, which can automatically download and
  execute malicious code.
* meta, which can contain malicious redirects and verification code(google)
* style and link, which can contain malicious script

DEFAULT_WHITELIST

* removed all on* attributes
* removed style attributes

@TODO tag/attribute map isn't complete.

DEFAULT_SANITIZER

* sanitizer object with default settings.
"""

from htmlsanitizer.utils.sanitizer import Sanitizer


DEFAULT_BLACKLIST = [
    "script",
    "applet", "embed", "object",
    "meta",
    "link", "style",
]

DEFAULT_WHITELIST = {
    'a': ['href', 'hreflang', 'charset', 'rel', 'rev', 'target', 'title',
          'dir', 'lang', 'xml:lang'],
    'abbr': ['title', 'dir', 'lang', 'xml:lang'],
    'acronym': ['title', 'dir', 'lang', 'xml:lang'],
    'address': ['title', 'dir', 'lang', 'xml:lang'],
    'b': ['title', 'dir', 'lang', 'xml:lang'],
    'bdo': ['title', 'dir', 'lang', 'xml:lang'],
    'big': ['title', 'dir', 'lang', 'xml:lang'],
    'blockquote': ['cite', 'title', 'dir', 'lang', 'xml:lang'],
    'br': ['title'],
    'caption': ['title', 'dir', 'lang', 'xml:lang'],
    'center': ['title', 'dir', 'lang', 'xml:lang'],
    'cite': ['title', 'dir', 'lang', 'xml:lang'],
    'code': ['title', 'dir', 'lang', 'xml:lang'],
    'col': ['valign', 'span', 'width', 'title', 'dir', 'lang', 'xml:lang'],
    'colgroup': ['valign', 'span', 'width', 'title', 'dir', 'lang',
                 'xml:lang'],
    'dd': ['title', 'dir', 'lang', 'xml:lang'],
    'del': ['cite', 'datetime', 'title', 'dir', 'lang', 'xml:lang'],
    'dfn': ['title', 'dir', 'lang', 'xml:lang'],
    'div': ['xml:lang', 'lang', 'dir', 'title'],
    'dl': ['title', 'dir', 'lang', 'xml:lang'],
    'dt': ['title', 'dir', 'lang', 'xml:lang'],
    'em': ['title', 'dir', 'lang', 'xml:lang'],
    'h1': ['title', 'dir', 'lang', 'xml:lang'],
    'h2': ['title', 'dir', 'lang', 'xml:lang'],
    'h3': ['title', 'dir', 'lang', 'xml:lang'],
    'h4': ['title', 'dir', 'lang', 'xml:lang'],
    'h5': ['title', 'dir', 'lang', 'xml:lang'],
    'h6': ['title', 'dir', 'lang', 'xml:lang'],
    'hr': ['title'],
    'html': ['dir', 'lang', 'xml:lang'],
    'i': ['title', 'dir', 'lang', 'xml:lang'],
    'img': ['src', 'alt', 'width', 'height', 'title', 'dir', 'lang',
            'xml:lang'],
    'ins': ['cite', 'datetime', 'title', 'dir', 'lang', 'xml:lang'],
    'li': ['title', 'dir', 'lang', 'xml:lang'],
    'ol': ['title', 'dir', 'lang', 'xml:lang'],
    'p': ['title', 'dir', 'lang', 'xml:lang'],
    'pre': ['title', 'dir', 'lang', 'xml:lang'],
    'q': ['cite', 'title', 'dir', 'lang', 'xml:lang'],
    's': ['title', 'dir', 'lang', 'xml:lang'],
    'samp': ['title', 'dir', 'lang', 'xml:lang'],
    'small': ['title', 'dir', 'lang', 'xml:lang'],
    'span': ['title', 'dir', 'lang', 'xml:lang'],
    'strike': ['title', 'dir', 'lang', 'xml:lang'],
    'strong': ['title', 'dir', 'lang', 'xml:lang'],
    'sub': ['title', 'dir', 'lang', 'xml:lang'],
    'sup': ['title', 'dir', 'lang', 'xml:lang'],
    'table': ['border', 'cellspacing', 'cellpadding', 'width', 'title', 'dir',
              'lang', 'xml:lang'],
    'tbody': ['valign', 'title', 'dir', 'lang', 'xml:lang'],
    'td': ['colspan', 'rowspan', 'abbr', 'wrap', 'width', 'height', 'title',
           'dir', 'lang', 'xml:lang'],
    'tfoot': ['valign', 'title', 'dir', 'lang', 'xml:lang'],
    'th': ['colspan', 'rowspan', 'abbr', 'wrap', 'width', 'height', 'title',
           'dir', 'lang', 'xml:lang'],
    'thead': ['valign', 'title', 'dir', 'lang', 'xml:lang'],
    'tr': ['valign', 'title', 'dir', 'lang', 'xml:lang'],
    'tt': ['title', 'dir', 'lang', 'xml:lang'],
    'u': ['title', 'dir', 'lang', 'xml:lang'],
    'ul': ['title', 'dir', 'lang', 'xml:lang'],
    'var': ['title', 'dir', 'lang', 'xml:lang'],
}

DEFAULT_SANITIZER = Sanitizer(DEFAULT_WHITELIST, DEFAULT_BLACKLIST)
