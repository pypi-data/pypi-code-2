#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler for root resource."""
__author__ = ('Lance Finn Helsten',)
__version__ = '1.0.1'
__copyright__ = """Copyright (C) 2009 Lance Finn Helsten"""
__license__ = """
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
__docformat__ = "reStructuredText en"

__all__ = ['HandlerHelp']

import sys
import os
import logging
import http.client
import http.server
from ..Handler import Handler



HELPDIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../httphelp"))


INDEX_HTML = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie Help Contents</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/add"/>
    <link rel="stylesheet" href="/help/help.css" type="text/css" media="screen"/>
</head>
<body>
  <h1>pyzombie Help</h1>
  <ol>
{0}
  </ol>
</body>
</html>
"""

INDEX_ROW = """    <li><a href="help/{0}">{0}</a></li>"""

class HandlerHelp(Handler):
    """Handle the root resource."""

    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/help(/(?P<helpfile>\w+(\.\w+)?)?)?$""",
            "GET,OPTIONS,TRACE", "/help/RESTful")
        return cls
                
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        html = None
        if self.urlargs["helpfile"] is None:
            files = [os.path.splitext(f) for f in os.listdir(HELPDIR)]
            files = [INDEX_ROW.format(f[0]) for f in files if f[1] == '.html']
            body = os.linesep.join(files)
            html = INDEX_HTML.format(body)
            self.status = http.client.OK
            self["Cache-Control"] = "public"
            self["Last-Modified"] = self.startstamprfc850
            self["Content-type"] = "text/html;UTF-8"
            self.writelines(html)
        elif os.path.splitext(self.urlargs["helpfile"])[1] == '':
            file = os.path.join(HELPDIR, self.urlargs["helpfile"] + '.html')
            file = os.path.normpath(file)
            self.writefile(file)
        else:
            file = os.path.join(HELPDIR, self.urlargs["helpfile"])
            file = os.path.normpath(file)
            self.writefile(file)
        self.flush()




