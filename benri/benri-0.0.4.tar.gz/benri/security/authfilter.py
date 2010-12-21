# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from benri.app import WSGIApp

class AuthFilter(WSGIApp):
    """
    Middleware that returns 401 Unathorized when an X.509 authenticated 
    user is not allowed to access the wrapped application.
    """

    def __init__(self, app, authservice, host=None, port=443, exclude_http_methods=['GET']):
        """
        Wraps a WSGI-application and filters out any requests which are not
        authorized according to an authentication service. Sets the Location-
        header to a SSL/TLS server if the `HTTP_SSL_CLIENT_S_DN`- or 
        `SSL_CLIENT_S_DN`-variable is not set. It is possible to define HTTP 
        methods which should not be filtered using the `exclude_http_methods`-
        argument.
        
        - `app`: the wrapped WSGI application
        - `authservice`: an instance of an `AuthorizationService`.
        - `host`: specifies a host that runs an SSL/TLS-server. Uses the 
                  `HTTP_HOST` environment-variable if `None`.
        - `port`: port where the SSL/TLS-server is running. Defaults to 443.
        - `exclude_http_methods`: list of HTTP methods for which authorization is
                                  unnecessary. Defaults to ['GET'].
        """
        self.app = app
        
        self.auth = authservice
        self.host = host
        self.port = port
        self.exclude_http_methods = exclude_http_methods
        
    def __call__(self, env, response):
        if env['REQUEST_METHOD'] in self.exclude_http_methods:
            return self.app(env, response)
        
        if not self.host:
            host = env['HTTP_HOST'].split(':')[0]

        port = self.port
        
        client_dn = 'HTTP_SSL_CLIENT_S_DN'
        
        try:
            env[client_dn]
        except KeyError:
            client_dn = 'SSL_CLIENT_S_DN'
            
        plain_text = ('Content-Type', 'text/plain')
        if not client_dn in env:
            headers = [('Location', 'https://' + host + ':' + str(port))]
            headers.append(plain_text)
            response('401 UNAUTHORIZED', headers)
            return ['%s is only allowed via HTTPS\r\n' %(env['REQUEST_METHOD'])]
        
        if client_dn in env and self.auth.isAuthorized(env[client_dn]):
            env['benri.ssl_user'] = env[client_dn]
            return self.app(env, response)
        
        log.debug('User %s was not allowed to %s to the resource.' % (env[client_dn], env['REQUEST_METHOD']))
        # user is not allowed to access the service using this certificate
        response('401 UNAUTHORIZED', [plain_text])
        return ['User %s is not authorized to access the service.\r\n' %(env[client_dn])]
            
