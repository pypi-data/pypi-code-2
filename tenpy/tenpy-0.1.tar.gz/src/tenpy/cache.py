"""Code and page caching object"""

# First Created: 2010-12-29 10:21:25 +0900
# Last Modified: 2011-01-18 16:33:40 +0900

# Copyright (c) 2010 Naoya Inada<naoina@naniyueni.org>
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

from hashlib import sha1

__author__ = "Naoya Inada <naoina@naniyueni.org>"

__all__ = [
        "CodeCache", "NullCodeCache", "cachename"
        ]


class CodeCache(dict):

    PREFIX = "__tenpy_func_"

    @classmethod
    def cachename(self, *seeds):
        return cachename(CodeCache.PREFIX, *seeds)


class NullCodeCache(CodeCache):

    def __setitem__(self, k, v):
        pass


def cachename(prefix, *seeds):
    seed = ""
    for s in seeds:
        seed += str(s)
    return prefix + sha1(bytes(seed, "utf-8")).hexdigest()
