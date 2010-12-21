# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import sys, os, logging

from benri.service import SecureService, Service, Application, InitFailure
#from benri.security.authorization import AuthorizationService, AuthorizeFlatFile
#from benri.security.authfilter import AuthFilter
	
from stellaris.service.graphs import Graphs
from stellaris.service.system import SystemGraphs, SystemCollections, SystemIndices
from stellaris.service.groups import Groups
from stellaris.service.query import Query
from stellaris.service.static import Static
from stellaris.store import FrontendStore
from stellaris.exceptions import ConfigAttributeMissing
from stellaris.service.security import disable_security, enable_security
from stellaris.service.collections import CollectionsFilter
from stellaris.security import ADMIN_GROUP

from paste.httpexceptions import HTTPExceptionHandler

import pprint

class LoggingMiddleware:

    def __init__(self, application):
        self.__application = application

    def __call__(self, environ, start_response):
        errors = environ['wsgi.errors']
        pprint.pprint(('REQUEST', environ), stream=errors)

        def _start_response(status, headers):
            pprint.pprint(('RESPONSE', status, headers), stream=errors)
            return start_response(status, headers)

        return self.__application(environ, _start_response)

class StellarisApp(Application):
    def __init__(self, env):
        Application.__init__(self)
            
        self.__store = FrontendStore(env)
        
        static = Static(env.static_dir, prefix=os.path.join(env.service_prefix, 'static'))
        system_graphs = SystemGraphs(self.__store, prefix=os.path.join(env.service_prefix, 'system/graphs'))
        system_collections = SystemCollections(self.__store, prefix=os.path.join(env.service_prefix, 'system/collections'))
        system_indices = SystemIndices(self.__store, prefix=os.path.join(env.service_prefix, 'system/indices[/]'))
        
        graphs = Graphs(self.__store, env.static_dir, prefix=env.service_prefix)
        groups = Groups(self.__store, prefix=os.path.join(env.service_prefix, 'system/groups'))
        query = Query(self.__store, env.static_dir, log=env.log, prefix=os.path.join(env.service_prefix, 'query'))
        
        # always put graphs last since if the prefix is '/', i.e. the root, then the
        # dispatcher will get caught on that and forward the request to the graphs app
        for app in [static, groups, system_graphs, system_collections, system_indices, query, graphs]:
            self.add(app)

        try:
            self.fixate()
        except InitFailure, e:
            env.log.info(str(e))

        app = self.application
        
        # security filter
        try:
            if env.config['security']['enabled'].lower() == 'true':

                try:
                    admin = env.config['security']['admin'].strip()
                    users = self.__store.group_retrieve(ADMIN_GROUP)
                    if not admin in users:
                        users.append(admin)

                    self.__store.group_update(ADMIN_GROUP, users=users)
                except KeyError, e:
                    # no admin defined, probably the user is settled
                    # with certificate verification as authorization
                    pass

                app = enable_security(app, env.data_dir)
            else:
                app = disable_security(app)
            
        except KeyError, e:
            app = disable_security(app)
        
        app = HTTPExceptionHandler(app)
        self.replace(app)

    def stop(self):
        self.__store.close()
                
class Serve(Service):
    """
    Initializes the applications that should be served by this service.
    """
    def __init__(self, env, server_threads=50):
        Service.__init__(self, env.config, server_threads=server_threads)

        self.__app = StellarisApp(env)
        self.useApplication(self.__app.application)
        
    def start(self):
        Service.start(self)
    
    def stop(self):
        Service.stop(self)
        self.__app.stop()

class SecureServe(SecureService):
    """
    Starts a secure server running the stellaris WSGI application.
    """
    def __init__(self, env, server_threads=50):
        SecureService.__init__(self, env.config, server_threads=server_threads)

        self.__app = StellarisApp(env)
        self.useApplication(self.__app.application)
        
    def start(self):
        SecureService.start(self)
    
    def stop(self):
        SecureService.stop(self)
        self.__app.stop()
