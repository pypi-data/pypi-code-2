#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server handler giving a web form to add an
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

__all__ = ['HandlerExecAdd']

import sys
import io
import logging
import mimetypes
import http.client
from .HandlerLeftovers import HandlerLeftovers

class HandlerExecAdd(HandlerLeftovers):
    """Handle the add executable resource."""
    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/add$""",
                "GET,POST,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
    
    
    def __init__(self, req, urlargs):
        super().__init__(req, {"leftover":"ExecAdd.html"})

        
    def post(self):
        fs = self.multipart()
        if fs:
            ctype, enc = mimetypes.guess_type(fs['execfile'].filename)
            self.initexecutable(mediatype=ctype)
            datafp = fs['execfile'].file
            self.executable.writeimage(datafp)
            self.nocache = True
            self.status = http.client.CREATED
            self["Location"] = self.serverurl(self.executable.name)
            self.flush()
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        


