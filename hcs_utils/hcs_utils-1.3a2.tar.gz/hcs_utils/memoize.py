# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
#
# Copyright (c) 2010, Christer Sjöholm -- hcs AT furuvik DOT net
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from __future__ import absolute_import

import threading

class memoize(object):
    """Decorator that caches the function's return value for each set of arguments.

    NOTE: All arguments must be hashable for the caching to work.

    Inspired by example on http://wiki.python.org/moin/PythonDecoratorLibrary

    >>> @memoize
    ... def func(*args):
    ...     print 'calculating'
    ...     return 42
    ...
    >>> func()
    calculating
    42
    >>> func()
    42
    >>> func({})
    calculating
    42
    >>> func({})
    calculating
    42
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.lock = threading.Lock()

    def __call__(self, *args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        try:
            if key in self.cache:
                val = self.cache[key]
            else:
                with self.lock: #TODO should have one lock per key
                    if key in self.cache:
                        val = self.cache[key]
                    else:
                        val = self.func(*args, **kwargs)
                        self.cache[key] = val
            return val
        except TypeError:
            # If we can't cache we don't.
            return self.func(*args, **kwargs)
