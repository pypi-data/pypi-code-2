#!/usr/bin/env python

# Copyright (c) 2011 Ben Croston
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from json import loads, dumps
import traceback
import sys
from webob import Request, Response, exc

class AuthRPCApp(object):
    """
    Serve the given object via json-rpc (http://json-rpc.org/)
    """

    def __init__(self, obj, auth=None):
        """
        obj  - a class containing functions available using jsonrpc
        auth - an authentication function (optional)
        """
        self.obj = obj
        self.auth = auth

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self._process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def _process(self, req):
        """
        Process the JSONRPC request.
        req - a webob Request object
        """
        if not req.method == 'POST':
            raise exc.HTTPMethodNotAllowed("Only POST allowed").exception

        try:
            json = loads(req.body)
        except ValueError, e:
            raise ValueError('Bad JSON: %s' % e)

        try:
            method = json['method']
            params = json['params']
            id = json['id']
            username = json['username'] if 'username' in json else None
            password = json['password'] if 'password' in json else None
        except KeyError, e:
            raise ValueError("JSON body missing parameter: %s" % e)

        if params is None:
            params = []
        if not isinstance(params, list):
            raise ValueError("Bad params %r: must be a list" % params)
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))

        obj = self.obj
        if isinstance(self.obj,tuple) or isinstance(self.obj,list):
            for x in self.obj:
                if method.startswith('%s.'%x.__class__.__name__):
                   obj = x
                   method = method.replace('%s.'%obj.__class__.__name__,'',1)
                   break
        elif method.startswith('%s.'%self.obj.__class__.__name__):
            method = method.replace('%s.'%self.obj.__class__.__name__,'',1)
        if method.startswith('_'):
            raise exc.HTTPForbidden("Bad method name %s: must not start with _" % method).exception
        try:
            method = getattr(obj, method)
        except AttributeError:
            raise ValueError("No such method %s" % method)

        if self.auth is not None:
            try:
                auth_result = self.auth(username, password, req.user_agent)
            except:
                text = traceback.format_exc()
                exc_value = sys.exc_info()[1]
                error_value = dict(
                    name='JSONRPCError',
                    code=100,
                    message=str(exc_value),
                    error=text)
                return Response(
                    status=500,
                    content_type='application/json',
                    body=dumps(dict(result=None,
                                    error=error_value,
                                    id=id)))
            if not auth_result:
                raise exc.HTTPUnauthorized().exception

        try:
            result = method(*params)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))

        return Response(
            content_type='application/json',
            body=dumps(dict(result=result,
                            error=None,
                            id=id)))

