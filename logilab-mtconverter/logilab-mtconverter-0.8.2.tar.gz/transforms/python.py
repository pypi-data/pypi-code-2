# copyright 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-mtconverter.
#
# logilab-mtconverter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-mtconverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-mtconverter. If not, see <http://www.gnu.org/licenses/>.
"""
Original code from active state recipe
        'Colorize Python source using the built-in tokenizer'

------------------------------------
     MoinMoin - Python Source Parser
------------------------------------

 This code is part of MoinMoin (http://moin.sourceforge.net/) and converts
 Python source code to HTML markup, rendering comments, keywords, operators,
 numeric and string literals in different colors.

 It shows how to use the built-in keyword, token and tokenize modules
 to scan Python source code and re-emit it with no changes to its
 original formatting (which is the hard part).
"""

import keyword, token, tokenize
from cStringIO import StringIO

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

class Parser:
    """Python Source Parser used to get HTML colored python source
    """
    def __init__(self, raw, tags, out):
        """Store the source text"""
        self.raw = raw.expandtabs().strip()
        self.out = out
        self.tags = tags

    def format(self):
        """Parse and send the colored source"""
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find('\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))
        # parse the source and write it
        self.pos = 0
        text = StringIO(self.raw)
        self.out.write('<pre class="python">\n')
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            self.out.write("<h5 class='error>'ERROR: %s%s</h5>" % (
                msg, self.raw[self.lines[line]:]))
        self.out.write('\n</pre>\n')

    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """Token handler"""
        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)
        # handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            self.out.write('\n')
            return
        # send the original whitespace, if needed
        if newpos > oldpos:
            self.out.write(self.raw[oldpos:newpos])
        # skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return
        # map token type to a group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = 'OP'
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = 'KEYWORD'
        else:
            toktype = tokenize.tok_name[toktype]

        open_tag = self.tags.get('OPEN_'+toktype, self.tags['OPEN_TEXT'])
        close_tag = self.tags.get('CLOSE_'+toktype, self.tags['CLOSE_TEXT'])
        # send text
        self.out.write(open_tag)
        self.out.write(html_escape(toktext))
        self.out.write(close_tag)


from logilab.mtconverter.transform import Transform
from logilab.mtconverter import html_escape

class python_to_html(Transform):
    """Colorize Python source files"""

    name = "python_to_html"
    inputs  = ("text/x-python",)
    output = "text/html"

    config = {
        'OPEN_NUMBER':       '<span style="color: #0080C0;">',
        'CLOSE_NUMBER':      '</span>',
        'OPEN_OP':           '<span style="color: #0000C0;">',
        'CLOSE_OP':          '</span>',
        'OPEN_STRING':       '<span style="color: #004080;">',
        'CLOSE_STRING':      '</span>',
        'OPEN_COMMENT':      '<span style="color: #008000;">',
        'CLOSE_COMMENT':      '</span>',
        'OPEN_NAME':         '<span style="color: #000000;">',
        'CLOSE_NAME':        '</span>',
        'OPEN_ERRORTOKEN':   '<span style="color: #FF8080;">',
        'CLOSE_ERRORTOKEN':  '</span>',
        'OPEN_KEYWORD':      '<span style="color: #C00000;">',
        'CLOSE_KEYWORD':     '</span>',
        'OPEN_TEXT':         '',
        'CLOSE_TEXT':        '',
        }

    def _convert(self, trdata):
        dest = StringIO()
        Parser(trdata.data, self.config, dest).format()
        return dest.getvalue()
