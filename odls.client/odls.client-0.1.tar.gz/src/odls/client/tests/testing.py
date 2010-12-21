##
## testing.py
## Login : <uli@pu.smp.net>
## Started on  Tue Aug 10 15:43:57 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
"""Testing helpers for odls.client.
"""
import cherrypy
from odls.client.http import extended_opener

SERVER_URL = 'localhost:8080'
SERVER_USERNAME = 'test'
SERVER_PASSWORD = 'test'

DEFAULT_OPENER = extended_opener(
    host=SERVER_URL,
    username=SERVER_USERNAME,
    password=SERVER_PASSWORD)


class ODLSServerApp(object):
    """A cherrypy application that mimics ODSL server behaviour.
    """
    @cherrypy.expose
    def index(self, *args, **kw):
        return "auth OK, write OK"

    def default(self):
        return "HI FROM DEFAULT"

    @cherrypy.expose
    def wrongauth(self, *args, **kw):
        return "auth NOT OK, write NOT OK"

    @cherrypy.expose
    def nowrite(self, *args, **kw):
        return "auth OK, write NOT OK"

    @cherrypy.expose
    def echo(self, *args, **kw):
        """Echo the request back.
        """
        result = 'CLIENT-REQUEST:\n'
        result += 'method: %s\n' % (cherrypy.request.method)
        keys = sorted(cherrypy.request.headers.keys())
        for key in keys:
            val = cherrypy.request.headers[key]
            result += '%s: %s\n' % (key, val)
        body = ""
        if cherrypy.request.body is not None:
            body += cherrypy.request.body
        if cherrypy.request.body_params is not None:
            body += str(cherrypy.request.body_params)
        return "%s\n%s" % (result, body)

class ODLSServer(object):
    """A HTTP server serving ODLSServerAPP.
    """

    app = None

    def __init__(self, host='localhost', port=8080, proto='http',
                 enable_digest_auth=False, enable_basic_auth=False):
        auth_realm = host
        auth_users = {'test': 'test',
                      'otheruser': 'test1'}
        cherrypy.config.update(
            {
                "log.error_file" : 'server-error.log',
                "log.access_file" : 'server.log',
                "environment" : 'embedded',
                "/echo": {'cherrypy.tools.rawRequestFilter.on':True},
                "tools.digest_auth.on": enable_digest_auth,
                "tools.digest_auth.realm": auth_realm,
                "tools.digest_auth.users": auth_users,
                "tools.basic_auth.on": enable_basic_auth,
                "tools.basic_auth.realm": auth_realm,
                "tools.basic_auth.users": auth_users,
                "tools.basic_auth.encrypt": lambda x:x,
                }
            )
        self.app = ODLSServerApp()
        cherrypy.tree.mount(self.app)
        self.engine = cherrypy.engine

    def start(self):
        self.engine.start()

    def stop(self):
        self.engine.exit()

SERVER = ODLSServer(enable_digest_auth=True)
