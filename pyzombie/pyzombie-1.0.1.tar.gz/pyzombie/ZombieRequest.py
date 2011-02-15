#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
"""pyzombie HTTP RESTful server request handler."""
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

__all__ = []

import sys
import os
from datetime import datetime
from datetime import timedelta
import logging
import socket
import http.client
import http.server
from .Handler import Handler
from .handlers import *


DISPATCH_TABLE = [
        Handler.initdispatch(#"Server",
            r"""^\*$""",
            "OPTIONS,TRACE",
            "abc"),
        
        ### HandlerTeapot.dispatch()    See RFC 2324
        HandlerHelp.dispatch(),
        HandlerExecSet.dispatch(),
        HandlerExecAdd.dispatch(),
        HandlerExec.dispatch(),
        HandlerExecStart.dispatch(),
        HandlerInstanceSet.dispatch(),
        HandlerInstance.dispatch(),        
        HandlerInstanceStdin.dispatch(),
        HandlerInstanceStdout.dispatch(),
        HandlerInstanceStderr.dispatch(),        
        HandlerLeftovers.dispatch(),
    ]


class ZombieRequest(http.server.BaseHTTPRequestHandler):
    """Handle all Zombie REST verbs."""
    
    def __init__(self, request, client_address, server):
        self.protocol_version = "HTTP/1.1"
        self.server_version = "pyzombie/" + __version__
        super().__init__(request, client_address, server)
    
    def resolvedispatch(self):
        """Resolve the path against resource patterns. If matched then return
        the dispatch object and the dictionary of recognized path parts."""
        for zd in DISPATCH_TABLE:
            parts = zd.match(self.path)
            if parts != None:
                return (zd, parts)
        self.send_error(http.client.NOT_FOUND)
        self.end_headers()
        return (None, None)
    
    def dispatch(self, method):
        """Determine the handler for the particular resource pattern and
        dispatch to that handler.
        
        Parameters
        ----------
        method
            The HTTP method that started this call. The lower case string
            is the name of the method in the handler class that will be called.
        """
        zd, parts = self.resolvedispatch()
        if zd is not None:
            zd = zd(self, parts)
            if hasattr(zd, method.lower()):
                getattr(zd, method.lower())()
            else:
                self.send_error(http.client.METHOD_NOT_ALLOWED,
                    "{0} not allowed on resource {1}".format(self.command, self.path))
                self.end_headers()
        
    def do_OPTIONS(self):
        try:
            zd, mo = self.resolvedispatch('OPTIONS')
            if zd != None:
                self.send_response(http.client.OK)
                self.send_header("Server", "pyzombie/" + __version__)
                self.send_header("Allow", zd.allow)
                self.send_header("Location", zd.help)
                self.end_headers()
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)
    
    def do_HEAD(self):
        try:
            self.dispatch('HEAD')
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)

    def do_GET(self):
        try:
            self.dispatch('GET')
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)
    
    def do_POST(self):
        try:
            self.dispatch('POST')
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)
    
    def do_PUT(self):
        try:
            self.dispatch('PUT')
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)
    
    def do_DELETE(self):
        try:
            self.dispatch('DELETE')
        except socket.error as err:
            self.log_error("Internal socket error %s.", err)



        