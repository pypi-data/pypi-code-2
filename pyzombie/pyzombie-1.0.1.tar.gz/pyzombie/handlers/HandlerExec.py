#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler returning the representation of an
executable."""
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

__all__ = ['HandlerExec']


import sys
import os
import re
import string
from datetime import datetime
import logging
import cgi
import mimetypes
import http.client
import http.server
from ..Handler import Handler


class HandlerExec(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/?$""",
                "GET,PUT,DELETE,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        self.writefile(self.executable.binpath)
        self.status = http.client.OK
        self.flush()
        
    def put(self):
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        if ctype != self.executable.mediatype[0]:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        self.executable.writeimage(self.rfile_safe())
        self.status = http.client.OK
        self.flush()

    def delete(self):
        self.executable.delete()
        self.status = http.client.OK
        self.flush()
        

