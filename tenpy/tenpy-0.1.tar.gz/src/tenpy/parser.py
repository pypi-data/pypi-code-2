"""Parser of presentation logic file"""

# First Created: 2010-12-25 00:02:01 +0900
# Last Modified: 2011-01-18 14:18:47 +0900

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

import re

__author__ = "Naoya Inada <naoina@naniyueni.org>"

__all__ = [
        "ParseError", "TenpyFile"
        ]


"""format:
[("selector type", "selector", "source code"),
 ("selector type", "selector", "source code"),
 .......]
"""

SELECTOR_TYPE = ["css", "xpath", "eval"]

trim_comment_func = re.compile(r"--.*$").sub
trim_comment = lambda s: trim_comment_func("", s)
selector_parser = re.compile(r"^(\S.*):\s*(.*)$").findall


class ParseError(SyntaxError):

    def __init__(self, msg, filename=None, lineno=None):
        self.msg = msg
        self.filename = filename
        self.lineno = lineno


class TenpyFile:

    def parse(self, filename):
        with open(filename) as f:
            selector = None
            stype = None
            indent = 0
            code = ""
            for lineno, line in enumerate(f):
                line = trim_comment(line)
                if not line.strip():
                    continue

                if line[0] in " \t":
                    if not selector:
                        raise ParseError("unexpected indent", filename, lineno)
                    line = line.expandtabs()
                    if not indent:
                        for c in line:
                            if c.isspace():
                                indent += 1
                            else:
                                break
                    code += line.replace(" ", "", indent)
                else:
                    if selector:
                        yield (stype, selector, code)
                        code = ""
                    (selector, stype) = self.parse_selector(line)
            yield (stype, selector, code)

    def parse_selector(self, s):
        (selector, stype) = selector_parser(s)[0]
        if not stype:
            stype = SELECTOR_TYPE[0]
        elif stype not in SELECTOR_TYPE:
            raise ParseError("unsupported selector type: " + stype)
        return (selector, stype)
