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

__version__ = '0.9.7'
__version_info__ = __version__.split('.')

CTPP2_VERSION = (2, 6)

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
    string = r'(([^"]|(\"))+?)'
    pattern = r"""
        <TMPL_var\s+(_|GETTEXT)\s*
        [(]\s*
        " %s ((")|$)""" % string
    regexp = re.compile(pattern, re.IGNORECASE|re.VERBOSE)
    string_tail_pat = re.compile('^%s"' % string)
    string_part_pat = re.compile('^%s$' % string)

    lineno = 0
    buffered = None
    messages = []
    for line in fileobj:
        lineno += 1
        if buffered:
            matched = string_tail_pat.search(line)
            if matched:
                messages.append(buffered + '\n' + matched.group(1))
                for message in messages:
                    yield saved_lineno, None, message, []
                messages = []
                buffered = None
            else:
                matched = string_part_pat.search(line)
                if matched:
                    buffered += '\n' + matched.group(1)

        if not buffered:
            for matched in regexp.finditer(line):
                if not matched.group(5):
                    buffered = matched.group(2)
                    saved_lineno = lineno
                    break
                messages.append(matched.group(2))
            else:
                for message in messages:
                    yield lineno, None, message, []
                messages = []

