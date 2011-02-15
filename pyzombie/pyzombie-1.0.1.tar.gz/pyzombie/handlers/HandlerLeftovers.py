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

__all__ = ['HandlerLeftovers']


import sys
import os
import mimetypes
import logging
import http.client
import http.server
from ..Handler import Handler


HTTPFILES = os.path.normpath(os.path.join(os.path.dirname(__file__), "../httpfiles"))

class HandlerLeftovers(Handler):
    """This will handle any normal file resources that are at the root of the
    server. For example '/favicon.ico' or 'base.css'. And then only if it has
    not been handled by a previous handler. All of these files must be in
    httpfiles."""

    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<leftover>.+)?$""",
            "GET,OPTIONS,TRACE", "/help/RESTful")
        return cls
    
    def filepath(self):
        """Return the normalized path to the HTTP file identified by "leftover"."""
        file = os.path.join(HTTPFILES, self.urlargs["leftover"])
        file = os.path.normpath(file)
        return file
                
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        file = self.filepath()
        self.writefile(file)
        self.flush()
            

        