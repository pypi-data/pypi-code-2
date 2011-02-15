#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler returning the set of available
executables."""
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

__all__ = ['HandlerExecSet']


import sys
import os
import re
import string
from datetime import datetime
import logging
import cgi
import http.client
import http.server
from ..Handler import Handler

INDEX_HTML = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie Executables</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/"/>
</head>
<body>
  <h1>pyzombie</h1>
  <h2>Executables</h2>
  <ol>
{0}
  </ol>
</body>
</html>
"""

INDEX_ROW = """    <li><a href="{0}">{0}</a></li>"""


class HandlerExecSet(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/$""",
                "GET,POST,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        mtime = datetime.utcfromtimestamp(os.path.getmtime(self.datadir))
        
        dirs = [INDEX_ROW.format(d)
                for d in os.listdir(self.datadir)
                if os.path.isdir(os.path.join(self.datadir, d))]
        body = os.linesep.join(dirs)
        html = INDEX_HTML.format(body)
        
        self.status = http.client.OK
        self["Cache-Control"] = "public max-age=3600"
        self["Last-Modified"] = mtime.strftime("%a, %d %b %Y %H:%M:%S GMT")
        self["Content-Type"] = "text/html;UTF-8"
        self.writelines(html)
        self.flush()
        
    def post(self):
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        self.initexecutable(mediatype=ctype)
        self.executable.writeimage(self.rfile_safe())
        self.nocache = True
        self.status = http.client.CREATED
        self["Location"] = self.serverurl(self.executable.name)
        self.flush()

