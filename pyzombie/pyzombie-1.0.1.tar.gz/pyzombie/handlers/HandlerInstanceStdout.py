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

__all__ = ['HandlerInstanceStdout']


import sys
import os
import io
import re
import logging
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance


class HandlerInstanceStdout(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/stdout$""",
            "GET,OPTIONS,TRACE",
            "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        if inst and inst.returncode is not None:
            self.writefile(inst.stdout_path)
        elif inst and inst.returncode is None:
            self.writefp(inst.stdout, chunked=self.__instdone)
        else:
            self.error(http.client.NOT_FOUND)
        
    def __instdone(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        return inst.returncode is not None


