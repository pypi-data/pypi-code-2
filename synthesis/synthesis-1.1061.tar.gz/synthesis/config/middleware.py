"""Pylons middleware initialization"""
import os
from beaker.middleware import SessionMiddleware
from paste.cascade import Cascade
from paste.registry import RegistryManager
from paste.urlparser import StaticURLParser
from paste.deploy.converters import asbool
from pylons.wsgiapp import PylonsApp
from routes.middleware import RoutesMiddleware
#from app.lib.mymiddleware import MyMiddleware

from synthesis.config.environment import load_environment
from synthesis.lib.eatexceptions import EatExceptions


def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    #print "test1"
    #print "test2"
    #start the server (non wsgi) loop
    child_pid = os.fork()
    if child_pid == 0:
        from synthesis.mainprocessor import MainProcessor
        MainProcessor()
    
    #main parent process
    else:
        """Create a Pylons WSGI application and return it
    
        ``global_conf``
            The inherited configuration for this application. Normally from
            the [DEFAULT] section of the Paste ini file.
    
        ``full_stack``
            Whether this application provides a full WSGI stack (by default,
            meaning it handles its own exceptions and errors). Disable
            full_stack when this application is "managed" by another WSGI
            middleware.
    
        ``static_files``
            Whether this application serves its own static files; disable
            when another web server is responsible for serving them.
    
        ``app_conf``
            The application's local configuration. Normally specified in
            the [app:<name>] section of the Paste ini file (where <name>
            defaults to main).
    
        """
        # Configure the Pylons environment
        config = load_environment(global_conf, app_conf)
    
        # The Pylons WSGI app
        app = PylonsApp(config=config)
    
        # Routing/Session/Cache Middleware
        app = RoutesMiddleware(app, config['routes.map'], singleton=False)
        
        app = SessionMiddleware(app, config)
    
        # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
        
        #ECJ 12112010 playing
        #app = MyMiddleware(app)
        
        if asbool(full_stack):
            # Handle Python exceptions
            #ECJ 12112010 adding custom middleware to handle header missing boundary 500 Internal Server Error
            app = EatExceptions(app)
            
            #app = ErrorHandler(app, global_conf, **config['pylons.errorware'])
           
            #ECJ 11152010 Commented out all the StatusCodeRedirection, because it was just wrapping my errors in html, and this is a web service, so not needed
            # Display error documents for 401, 403, 404 status codes (and
            # 500 when debug is disabled)
            #if asbool(config['debug']):
                #app = StatusCodeRedirect(app)
            #else:
                #app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])
    
        # Establish the Registry for this application
        app = RegistryManager(app)
    
        if asbool(static_files):
            # Serve static files
            static_app = StaticURLParser(config['pylons.paths']['static_files'])
            app = Cascade([static_app, app])
        app.config = config
        
        return app
