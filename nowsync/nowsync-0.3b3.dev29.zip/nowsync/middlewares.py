"""This module was originally from http://flask.pocoo.org/snippets/8/

"""
from __future__ import with_statement

import flask

class AuthenMiddleware(object):
    """Middleware for authenticating user
    
    """
    
    def __init__(self, app, users, realm='NowSync'):
        self.app = app
        self.users = users
    
    def __call__(self, environ, start_response):
        request = flask.Request(environ)
        auth = request.authorization
        if auth:
            for username, password in self.users.iteritems():
                if auth.username == username and auth.password == password:
                    return self.app(environ, start_response)
        return self.authenticate()(environ, start_response)
    
    def authenticate(self):
        """Sends a 401 response that enables basic auth"""
        return flask.Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})
        
class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the 
    front-end server to add these headers, to let you quietly bind 
    this to a URL other than / and to an HTTP scheme that is 
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)