# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import selector, signal, os, logging, sys

from threading import Thread
from paste.httpexceptions import HTTPExceptionHandler

#from benri.wsgi import ContentTypeDispatcher

from benri.wsgiserver import CherryPyWSGIServer
from benri.wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
from benri.log import initLogger

class InitFailure(Exception): pass

class Application(object):
    
    def __init__(self):
        self._wsgi_app = None
        self._apps = []
        self._app = None
            
    def add(self, app):
        self._apps.append(app)
    
    def replace(self, app):
        # this is used when applying filters by replacing the current app
        self._app = app
        
    def fixate(self):
        # use fixate when the middleware is composed
        # this will load all apps into the dispatcher
    
        if len(self._apps) > 0:
            dispatcher = selector.Selector()

            # add the any_noun pattern which consumes anything up to the ;
            dispatcher.parser.patterns['any_noun'] = '[^;]+'
            
            for app in self._apps:
                dispatcher.slurp(app.routes)
        
            self._app = dispatcher

    @property
    def application(self):
        return self._app
            
class Service(object):

    def __init__(self, config, server_threads=20):
        # takes care of benri/server-specific initialization
        # defined in the [benri] and [server] section of the cfg-file

        try:
            self.__server_threads = int(config["server"]["threads"])
        except (KeyError, ValueError):
            self.__server_threads = server_threads
        
        bind = config["server"]["bind"].split(':')        
        self.bind = bind[0], int(bind[1])

        self.server = None
        
        initLogger('benri')
        self.__log = logging.getLogger('benri')

        self.wsgi_app = None
        
        # install a signal handler for a clean shutdown when a kill is
        # received 
        signal.signal(signal.SIGTERM, self._sigterm)

    def useApplication(self, app):
        self.wsgi_app = app
        
    def _sigterm(self, signum, frame):
        raise SystemExit("Received signal SIGKILL")
                            
    def start(self):
        wsgi_app = self.wsgi_app #HTTPExceptionHandler(self.wsgi_app)
                    
        self.server = CherryPyWSGIServer(self.bind, wsgi_app, numthreads=self.__server_threads)
        self.__log.info("HTTP server started at " + self.bind[0] + ':' + str(self.bind[1]))
         
        self.server.start()

    def stop(self):
        if self.server:
            self.server.stop()
            self.__log.info("HTTP server shutdown complete")

class SecureService(object):

    def __init__(self, config, server_threads=20):
        # takes care of benri/server-specific initialization
        # defined in the [benri] and [server] section of the cfg-file

        self.__server_threads = server_threads
        
        bind = config["server"]["bind"].split(':')
        self.bind = bind[0], int(bind[1])

        self.server = None
        
        initLogger('benri')
        self.__log = logging.getLogger('benri')
        
        self.wsgi_app = None

        try:
            self.key_path = config["server"]["ssl_key_path"]
            self.cert_path = config["server"]["ssl_cert_path"]
        except KeyError, ke:
            raise InitFailure('Could not configure the secure server. Missing %s in the [server]-section.' % (str(ke)))

        try:
            self.ca_certs = config["server"]["ssl_cacert_path"]
        except KeyError, ke:
            self.ca_certs = None
            self.__log.info('Client certificates are not verified. Specify ssl_cacert_path in the [server]-section to enable client certificate verification.')

        try:
            self.verify_depth = int(config["server"]["ssl_verify_depth"])
        except KeyError, ke:
            self.verify_depth = 9

        # install a signal handler for a clean shutdown when a kill is
        # received 
        signal.signal(signal.SIGTERM, self._sigterm)

    def useApplication(self, app):
        self.wsgi_app = app
        
    def _sigterm(self, signum, frame):
        raise SystemExit("Received signal SIGKILL")
                            
    def start(self):
        wsgi_app = self.wsgi_app #HTTPExceptionHandler(self.wsgi_app)
        
        self.https_server = CherryPyWSGIServer(self.bind, wsgi_app, numthreads=self.__server_threads)

#        self.https_server.ssl_private_key = self.key_path
#        self.https_server.ssl_certificate = self.cert_path
#        self.https_server.ssl_cacert_path = self.ca_certs
#        self.https_server.ssl_verify_depth = self.verify_depth

        self.https_server.ssl_adapter = pyOpenSSLAdapter(
            self.cert_path, 
            self.key_path, 
            getattr(self, 'ssl_certificate_chain', None),
            client_CA=self.ca_certs,
            client_check_host=True,
            client_check="required")

        self.__log.info("HTTPS server started at " + self.bind[0] + ':' + str(self.bind[1]))
            
        self.https_server.start()

    def stop(self):
        if self.https_server:
            self.https_server.stop()
            self.__log.info("HTTPS server shutdown complete")
