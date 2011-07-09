# -*- coding:utf-8 -*-

# First Created: 2011-07-03 18:30:13 +0900
# Last Modified: 2011-07-07 23:45:25 +0900

# Copyright (c) 2011 Naoya INADA <naoina@naniyueni.org>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

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

__author__ = "Naoya INADA <naoina@naniyueni.org>"

__all__ = [
        ]

from docutils.parsers.rst import directives, languages

_hatena_directive_registry = {
    "niconico": ("rst2hatena", "Niconico"),
    "google": ("rst2hatena", "Google"),
    "amazon": ("rst2hatena", "Amazon"),
    "wikipedia": ("rst2hatena", "Wikipedia"),
    "twitter": ("rst2hatena", "Twitter"),
    "map": ("rst2hatena", "Map"),
}

_hatena_directives = {
    "niconico": "niconico",
    "google": "google",
    "amazon": "amazon",
    "wikipedia": "wikipedia",
    "twitter": "twitter",
    "map": "map",
}

directives._directive_registry.update(_hatena_directive_registry)
languages.en.directives.update(_hatena_directives)


def main():
    pass

if __name__ == "__main__":
    main()
