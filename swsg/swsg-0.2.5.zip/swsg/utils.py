import re
from functools import partial
from operator import is_

is_none = partial(is_, None)

try:
    from genshi.util import striptags
except ImportError:
    # the following code is copied from genshi's source code (version 0.6) so
    # that the genshi module is not mandatory here
    _STRIPTAGS_RE = re.compile(r'(<!--.*?-->|<[^>]*>)')

    def striptags(text):
        """Return a copy of the text with any XML/HTML tags removed.

        >>> striptags('<span>Foo</span> bar')
        'Foo bar'
        >>> striptags('<span class="bar">Foo</span>')
        'Foo'
        >>> striptags('Foo<br />')
        'Foo'

        HTML/XML comments are stripped, too:

        >>> striptags('<!-- <blub>hehe</blah> -->test')
        'test'

        :param text: the string to remove tags from
        :return: the text with tags removed
        """
        return _STRIPTAGS_RE.sub('', text)
