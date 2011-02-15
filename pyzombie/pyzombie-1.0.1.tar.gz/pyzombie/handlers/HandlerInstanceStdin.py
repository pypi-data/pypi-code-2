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

__all__ = ['HandlerInstanceStdin']


import sys
import os
import io
import re
import logging
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance
from .HandlerLeftovers import HandlerLeftovers


class HandlerInstanceStdin(HandlerLeftovers):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/stdin$""",
            "GET,POST,OPTIONS,TRACE",
            "/help/RESTful")
        return cls
    
    
    def __init__(self, req, urlargs):
        urlargs["leftover"] = "InstanceStdin.html"
        super().__init__(req, urlargs)
    
    def get(self):    
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        self.status = http.client.OK
        self.headers["Content-Type"] = "text/html;UTF-8"
        file = self.filepath()
        html = open(file, 'r').read()
        html = html.format(self.executable.name, inst.name)
        self.writelines(html)
        self.flush()
        
    def post(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        fp = None        
        ctype, pdict = cgi.parse_header(self.req.headers['Content-Type'])
        if ctype == 'text/plain':
            fp = self.req.rfile
        elif ctype == 'multipart/form-data':
            fs = self.multipart()
            if fs:
                fp = io.StringIO(fs['stdin'])
        
        if fp is not None:
            databuf = fp.read()
            inst.stdin.write(databuf)
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)

        
            