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

from uuid import uuid4
from urlparse import urlparse
import json
import httplib
import copy
import socket
import hashlib
import platform

if platform.python_version().startswith('3'):
    IS_PY3 = True
else:
    IS_PY3 = False

class _Method(object):
    def __init__(self, call, name, username=None, password=None):
        self.call = call
        self.name = name
        self._username = username
        self._password = password

    def __call__(self, *args, **kwargs):
        request = {}
        request['id'] = str(uuid4())
        request['method'] = self.name

        if len(kwargs) is not 0:
            params = copy.copy(kwargs)
            index = 0
            for arg in args:
                params[str(index)] = arg
                index = index + 1
        elif len(args) is not 0:
            params = copy.copy(args)
        else:
            params = None
        request['params'] = params

        if self._username is not None:
            request['username'] = self._username
        if self._password is not None:
            if IS_PY3:
                request['password'] = hashlib.md5(self._password.encode()).hexdigest()
            else:
                request['password'] = hashlib.md5(self._password).hexdigest()

        resp = self.call(json.dumps(request))
        if resp is not None and resp['error'] is None and resp['id'] == request['id']:
            return resp['result']
        else:
            raise Exception('This is not supposed to happen -- btc') ########

    def __getattr__(self, name):
        return _Method(self.call, "%s.%s" % (self.name, name), self._username, self._password)

class _JSONRPCTransport(object):
    headers = {'Content-Type':'application/json',
               'Accept':'application/json'}

    def __init__(self, uri, proxy_uri=None, user_agent=None):
        self.headers['User-Agent'] = user_agent if user_agent is not None else 'AuthRPC'
        if proxy_uri is not None:
            self.connection_url = urlparse(proxy_uri)
            self.request_path = uri
        else:
            self.connection_url = urlparse(uri)
            self.request_path = self.connection_url.path
            
    def request(self, request_body):
        if self.connection_url.scheme == 'http':
            if self.connection_url.port is None:
                port = 80
            else:
                port = self.connection_url.port
            connection = httplib.HTTPConnection(self.connection_url.hostname+':'+str(port))
        elif self.connection_url.scheme == 'https':
            if self.connection_url.port is None:
                port = 443
            else:
                port = self.connection_url.port
            connection = httplib.HTTPSConnection(self.connection_url.hostname+':'+str(port))
        else:
            raise Exception('unsupported transport')
        connection.request('POST', self.request_path, body=request_body, headers=self.headers)
        return connection.getresponse()

class BadRequestException(Exception):
    """HTTP 400 - Bad Request"""
    def __init__(self):
        Exception.__init__(self,'HTTP 400 - Bad Request')

class UnauthorisedException(Exception):
    """HTTP 401 - Unauthorised"""
    def __init__(self):
        Exception.__init__(self,'HTTP 401 - Unauthorised')

class ForbiddenException(Exception):
    """HTTP 403 - Forbidden"""
    def __init__(self):
        Exception.__init__(self,'HTTP 403 - Forbidden')

class NotFoundException(Exception):
    """HTTP 404 - Not Found"""
    def __init__(self):
        Exception.__init__(self,'HTTP 404 - Not Found')

class NetworkSocketException(Exception):
    def __init__(self):
        Exception.__init__(self,'Network socket exception')

class BadGatewayException(Exception):
    """HTTP 502 - Bad Gateway"""
    def __init__(self):
        Exception.__init__(self,'HTTP 502 - Bad Gateway')

class ServerProxy(object):
    """
    A client class to communicate with a AuthRPC server
    """
    def __init__(self, uri, proxy_uri=None, user_agent=None, username=None, password=None):
        """
        uri        - the URI of a corresponding AuthRPC server
        proxy_uri  - the http proxy to use, if any
        user_agent - user agent to be used (can be used as part of authentication)
        username   - username to use in requests
        password   - password to use in requests
        """
        assert uri is not None
        self.__transport = _JSONRPCTransport(uri, proxy_uri=proxy_uri, user_agent=user_agent)
        self._username = username
        self._password = password

    def __request(self, request):
        # call a method on the remote server
        try:
            response = self.__transport.request(request)
        except socket.error:
            raise NetworkSocketException
        if response.status == 200:
            if IS_PY3:
                return json.loads(response.read().decode())
            else:
                return json.loads(response.read())
        elif response.status == 400:
            raise BadRequestException
        elif response.status == 401:
            raise UnauthorisedException
        elif response.status == 403:
            raise ForbiddenException
        elif response.status == 404:
            raise NotFoundException
        elif response.status == 500:
            if IS_PY3:
                msg = json.loads(response.read().decode())
            else:
                msg = json.loads(response.read())
            raise Exception('JSONRPCError\n%s'%msg['error']['error'])
        elif response.status == 502:
            raise BadGatewayException
        else:
            raise Exception('HTTP Status %s'%response.status)

    def __repr__(self):
        return (
            "<ServerProxy for %s%s>" %
            (self.__host, self.__handler)
            )

    __str__ = __repr__

    def __getattr__(self, name):
        # magic method dispatcher
        return _Method(self.__request, name, self._username, self._password)

