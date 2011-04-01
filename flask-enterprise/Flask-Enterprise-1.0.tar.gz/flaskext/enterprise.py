# -*- coding: utf-8 -*-
"""
    flaskext.enterprise
    ~~~~~~~~~~~~~~~~~~~

    To be described.


    :copyright: (c) 2011 by Massive of Rock Inc.
    :license: CDDL, see LICENSE for more details.
"""
from __future__ import absolute_import

import sys
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher as XMLRPCDispatcher

from suds.client import Client as SudsClient

from soaplib.core import Application
from soaplib.core.service import rpc, DefinitionBase
from soaplib.core.model import primitive, clazz, binary
from soaplib.core.server import wsgi

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.wrappers import Request, Response


def make_enterprise_controller(app):
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    rv = app.extensions['enterprise'] = EnterpriseController(app)
    return rv


class EnterpriseController(object):

    def __init__(self, app):
        self.app = app
        self.services = {}
        self.real_wsgi_app = app.wsgi_app
        app.wsgi_app = self.wsgi_app

    def register_soap_service(self, service):
        soap_app = Application([service], service.__soap_target_namespace__)
        wsgi_app = wsgi.Application(soap_app)
        self.services[service.__soap_server_address__] = wsgi_app

    def register_xmlrpc_service(self, service_class):
        service = service_class()
        for key in dir(service):
            value = getattr(service, key, None)
            if not callable(value):
                continue
            method_name = getattr(value, '__xmlrpc_name__', None)
            if method_name is None:
                continue
            service.register_function(value, method_name)
        self.services[service.__xmlrpc_server_address__] = service

    def wsgi_app(self, environ, start_response):
        dispatcher = DispatcherMiddleware(self.real_wsgi_app, self.services)
        return dispatcher(environ, start_response)


class EnterpriseSOAPService(DefinitionBase):
    __soap_target_namespace__ = 'tns'
    __soap_server_address__ = '/_enterprise/soap'


class EnterpriseXMLRPCService(XMLRPCDispatcher, object):
    __xmlrpc_server_address__ = '/_enterprise/xmlrpc'

    def __init__(self):
        if sys.version_info[:2] < (2, 5):
            XMLRPCDispatcher.__init__(self)
        else:
            XMLRPCDispatcher.__init__(self, True, 'utf-8')

    def __call__(self, environ, start_response):
        request = Request(environ)
        data = self._marshaled_dispatch(request.data)
        resp = Response(data, content_type='text/xml')
        return resp(environ, start_response)


def mark_xmlrpc(name):
    def decorator(f):
        f.__xmlrpc_name__ = name
        return f
    return decorator


class Enterprise(object):

    def __init__(self, app):
        self.app = app
        self.controller = make_enterprise_controller(app)

        class _BoundSOAPService(EnterpriseSOAPService):
            class __metaclass__(type):
                def __new__(cls, name, bases, d):
                    rv = type.__new__(cls, name, bases, d)
                    self.controller.register_soap_service(rv)
                    return rv

        class _BoundXMLRPCService(EnterpriseXMLRPCService):
            class __metaclass__(type):
                def __new__(cls, name, bases, d):
                    rv = type.__new__(cls, name, bases, d)
                    self.controller.register_xmlrpc_service(rv)
                    return rv

        self.SOAPService = _BoundSOAPService
        self.XMLRPCService = _BoundXMLRPCService
        self.connect_to_soap_server = SudsClient
        self.connect_to_xmlrpc_server = xmlrpclib.ServerProxy
        self._sp = primitive
        self._scls = clazz
        self._sb = binary
        self.soap = rpc
        self.xmlrpc = mark_xmlrpc
