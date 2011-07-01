# encoding: utf-8
# Copyright (c) 2011 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

import re

try:
    from _pyctpp2 import Engine, Template
except ImportError:
    pass

__version__ = '0.11.1'
__version_info__ = __version__.split('.')

CTPP2_VERSION = (2, 7, 0)


STRING_RE = r"""(?: '(?: [^'\\] | \\. )*' | "(?: [^"\\] | \\.)*")"""

REGEXP = re.compile(r"""(?:
(?: ((?: GETTEXT) | _) (\s*) [(] (\s*) ({0}) (\s*) , (\s*) ({0}) (\s*) , ) |
(?: ((?: GETTEXT) | _) (\s*) [(] (\s*) ({0}) (\s*) , (\s*)  {0}  (\s*) [)] ) |
(?: ((?: GETTEXT) | _) (\s*) [(] (\s*) ({0})                     (\s*) [)] ) |
(\s*)
)""".format(STRING_RE), re.IGNORECASE | re.VERBOSE)


def extract_i18n_messages(fileobj, keywords, comment_tags, options):
    """Extract messages from XXX files.
    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """

    def count_newlines(elems):
        return sum([ elem.count('\n') for elem in elems if elem ])

    data = fileobj.read()
    lineno = 1
    for matched in REGEXP.finditer(data):
        lineno += count_newlines(matched.groups())
        if not matched:
            continue

        messages = (m.strip(' \t\v\f\r') for m in matched.groups() if m)
        messages = [m for m in messages if m]
        if messages and (messages[0].upper() == 'GETTEXT' or messages[0] == '_'):
            saved_lineno = lineno - count_newlines(messages)
            messages = [m[1:-1] for m in messages[1:]]
            func_name = 'gettext'
            if len(messages) > 1:
                func_name = 'ngettext'
            yield saved_lineno, func_name, messages, []


