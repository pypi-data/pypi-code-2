# First Created: 2011-01-14 01:03:06 +0900
# Last Modified: 2011-01-18 14:18:40 +0900

# Copyright (c) 2011 Naoya Inada<naoina@naniyueni.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import inspect
import os.path as path

from .etree import E

__author__ = "Naoya Inada <naoina@naniyueni.org>"

__all__ = [
        "A", "E", "include"
        ]


class _Attribute:

    def __init__(self, kwds):
        self.__dict__ = kwds


class _Include:

    def __init__(self, filename):
        self.filename = filename


def A(**kwds):
    return _Attribute(kwds)

def include(filename):
    frame = inspect.currentframe(1)
    while frame:
        try:
            return _Include(path.join(path.dirname(frame.f_locals["filename"]),
                filename))
        except KeyError:
            frame = frame.f_back
    raise IOError("No such file: '" + filename + "'")
