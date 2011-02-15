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

__all__ = ['HandlerInstance']


import sys
import os
import io
import re
import string
from datetime import datetime
import json
import logging
import cgi
import mimetypes
import http.client
import http.server
from ..Handler import Handler
from ..Instance import Instance


class HandlerInstance(Handler):    
    @classmethod
    def dispatch(cls):
        cls.initdispatch(r"""^/(?P<execname>\w+)/instances/(?P<instname>\w+)/?$""",
            "GET,DELETE,OPTIONS,TRACE",
            "/help/RESTful")
        return cls
            
    def head(self):
        self.content = "Headers"
        self.get()
    
    def get(self):
        name = self.urlargs["instname"]
        inst = Instance.getcached(self.executable, name)
        if inst:
            buf = io.StringIO()
            for mediatype in self.accept:
                if mediatype == "text/html":
                    reprfunc = self.representation_html
                    break
                elif mediatype == "application/json":
                    reprfunc = self.representation_json
                    break
                elif mediatype == "application/yaml":
                    reprfunc = self.representation_yaml
                    break
            if mediatype:
                reprfunc(inst, buf)
                self["Content-Type"] = mediatype
                self.writelines(buf.getvalue())
                self.status = http.client.OK
                self.flush()
            else:
                self.error(http.client.UNSUPPORTED_MEDIA_TYPE)
        else:
            self.error(http.client.NOT_FOUND)
        
    
    def delete(self):
        name = self.urlargs["instname"]
        if name in self.executable.instances:
            inst = self.executable.instances[name]
            inst.delete()
            self.status = http.client.OK
            self.flush()
        else:
            self.error(http.client.NOT_FOUND)
        
    
    def representation_html(self, inst, fp):
        """Create an HTML representation of the instance.
        
        Parameters
        ----------
        fp
            Pointer to file type object to write the HTML representation.
        """
        inststate = inst.state(self.serverurl(path=""), urlpath="instances")
        html = """<!DOCTYPE html>
<html lang='en'>
<head>
    <title>pyzombie: {name}</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link rel="Contents" href="/"/>
</head>
<body>
    <h1>pyzombie</h1>
    <h2><a href="{self}">{name}</a></h2>
    <ul>
        <li>Result code: {returncode}</li>
        <li>Started: {start}</li>
        <li>Timeout: {timeout}</li>
        <li>Completed: {end}</li>
        <li>Remove: {remove}</li>
        <li><a href="{stdin}">stdin</a></li>
        <li><a href="{stdout}">stdout</a></li>
        <li><a href="{stderr}">stderr</a></li>
    </ul>
</body>
</html>
""".format(**inststate)
        fp.write(html)
    
    def representation_json(self, inst, fp):
        """Create a JSON representation of the instance.
        
        Parameters
        ----------
        fp
            Pointer to file type object to write the JSON representation.
        """
        state = inst.state(self.serverurl(path=""), urlpath="instances")
        json.dump(state, fp, sort_keys=True, indent=4)
    
    def representation_yaml(self, inst, fp):
        """Create a YAML representation of the instance.
        
        Parameters
        ----------
        fp
            Pointer to file type object to write the JSON representation.
        urlprefix
            The URL scheme, host, port, etc. prefix for all URLs in the representation.
        urlpath
            The additional path information between the executable name and the
            instance name.
        """
        state = inst.state(self.serverurl(path=""), urlpath="instances")

