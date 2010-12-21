# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from beaker.middleware import SessionMiddleware
from authkit.authenticate import middleware
from authkit.permissions import RemoteUser

from stellaris.security import AUTHENTICATED_USER, PUBLIC_USER, READ, ADMIN_READ_WRITE
from stellaris.store.exceptions import Unauthorized

from paste.httpexceptions import HTTPUnauthorized

def enable_security(app, store_path, system_prefix='/system'):
    """
    Returns middleware that sets the REMOTE_USER environment variable according
    to the OpenID name.
    
    ``app`` - the wrapped application
    ``store_path`` - path to where the openid database is stored
    ``system_prefix`` - server path prefix for the system
    """
    # openid is used as a backup setting REMOTE_USER if not SSL is used
    
    # TODO: secrets must be configurable/generated
    # fix OpenID support
#    app = middleware(
#        app,
#        setup_method = 'openid, cookie',
#        openid_path_signedin = '%s/signin' % system_prefix,
#        openid_store_type = 'file',
#        openid_store_config = store_path,
#        openid_charset = 'UTF-8',
#        cookie_secret = 'secret encryption string',
#        cookie_signoutpath = '%s/signout' % system_prefix,
#    )
#    app = SessionMiddleware(
#        app, 
#        key='authkit.open_id', 
#        secret='some secret',
#    )

    def wrapped_app(env, resp):
        try:
            # remote user already set
            env['REMOTE_USER']
        except KeyError, e:
            # the remote user is not set, use public user as default
            env['REMOTE_USER'] = PUBLIC_USER

            # check different variants of the client certificate DN
            # variable
            for var in ['SSL_CLIENT_S_DN', 'HTTP_SSL_CLIENT_S_DN']:
                try:
                    env['REMOTE_USER'] = env[var]
                    break
                except KeyError, e:
                    pass
            
        return app(env, resp)
        
    return wrapped_app

def disable_security(app):
    """
    Disables security by setting ``REMOTE_USER`` to the ``AUTHENTICATED_USER``.
    
    The behaviour of a database where the security has been enabled and then
    being disabled is not specified.
    """
    def wrapped_app(env, resp):
        env['REMOTE_USER'] = AUTHENTICATED_USER
        return app(env, resp)
    
    return wrapped_app

def authorize(access_type=READ):
    """
    Middleware decorator used to authorize access to a user defined with the 
    enviroment-variable ``REMOTE_USER``. Assumes that the decorated method
    is in a class with a ``store``-attribute.
    
    ``access_type`` - Defines the type of the access. Defaults to ``READ``.
    """
    def wrapped(app):
        def middleware_app(cls, env, resp):
            # is the remote user set, if not it defaults to the public user
            user = env.get('REMOTE_USER', PUBLIC_USER)
                            
            try:
                if access_type == ADMIN_READ_WRITE:
                    if cls.store.is_admin(user):
                        return app(cls, env, resp)
                    
                    raise Unauthorized('User %s is not an admin.' % (user))
                else:
                    graph_id = cls._graph_id(env)                
                    cls.store.is_authorized(graph_id, user, access_type=access_type)
                    return app(cls, env, resp)
            except Unauthorized, e:
                # client knows it cant access the resource, it should then retry
                # with https or any way to authenticate itself
                # 'User %s is not allowed to access %s.' % (user, graph_id)
                raise HTTPUnauthorized(str(e))

        return middleware_app
    return wrapped
