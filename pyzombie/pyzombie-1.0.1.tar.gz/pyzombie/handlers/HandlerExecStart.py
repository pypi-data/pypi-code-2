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

__all__ = ['HandlerExecStart']

import sys
import os
import io
import logging
import mimetypes
import http.client
from ..Instance import Instance
from .HandlerLeftovers import HandlerLeftovers

class HandlerExecStart(HandlerLeftovers):
    """Handle the add executable resource."""
    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/start$""",
                "GET,POST,OPTIONS,TRACE",
                "/help/RESTful")
        return cls
    
    
    def __init__(self, req, urlargs):
        urlargs["leftover"] = "ExecStart.html"
        super().__init__(req, urlargs)
    
    def get(self):
        env = [k for k in os.environ]
        env.sort()
        env = ['{0} = {1}'.format(k, os.environ[k]) for k in env]
        env = os.linesep.join(env)
        argv = ""
    
        self.status = http.client.OK
        self.headers["Content-Type"] = "text/html;UTF-8"
        file = self.filepath()
        html = open(file, 'r').read()
        html = html.format(self.executable.name, env, argv)
        self.writelines(html)
        self.flush()
        
    def post(self):
        fs = self.multipart()
        if fs:            
            environ = fs.getfirst("environ")
            environ = environ.split('\n')
            environ = [e.split('=') for e in environ]
            environ = [(l.strip(), r.strip()) for l, r in environ]
            environ = dict(environ)
            
            argv = fs.getfirst("arguments")
            argv = argv.split()
            argv = [a.strip() for a in argv]
            argv = [a for a in argv if a]
            
            self.inst = Instance(self.executable, Instance.createname(),
                environ=environ, arguments=argv)
            self.nocache = True
            self.status = http.client.CREATED
            self["Location"] = self.serverurl(self.inst.restname)
            self.flush()
            #TODO: If the accept type is HTML then do a redirect to the actual instance
        else:
            self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        


