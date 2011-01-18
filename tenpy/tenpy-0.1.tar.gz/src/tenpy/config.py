# First Created: 2011-01-14 01:22:24 +0900
# Last Modified: 2011-01-14 01:23:18 +0900

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

__author__ = "Naoya Inada <naoina@naniyueni.org>"

__all__ = [
        "TenpyConfig"
        ]


class TenpyConfig:

    def __init__(self):
        object.__setattr__(self, "template_extensions", [".html"])
        object.__setattr__(self, "tenpy_extension",     ".tenpy")
        object.__setattr__(self, "default_tenpy_page",  "default")
        object.__setattr__(self, "tenpy_filepaths",     ["."])
        object.__setattr__(self, "tenpy_file", "{page}{tenpy_extension}")
        object.__setattr__(self, "cache", True)

    def __getitem__(self, k):
        """x.__getitem__(k) <==> x[k]
        but raise KeyError if k is not defined.
        """
        k = str(k)
        if not hasattr(self, k):
            raise KeyError("no such setting name " + k + ".")
        return object.__getattribute__(self, k)

    def __setitem__(self, k, v):
        """x.__setitem__(k, v) <==> x[k]=v
        but raise KeyError if k is not defined.
        """
        try:
            self.__setattr__(k, v)
        except AttributeError as e:
            raise KeyError(e)

    def __setattr__(self, name, value):
        """x.__setattr__(name, value) <==> x.name = value
        but raise AttributeError if name is not defined.
        """
        name = str(name)
        if not hasattr(self, name):
            raise AttributeError("no such setting name " + name + ".")
        object.__setattr__(self, name, value)
