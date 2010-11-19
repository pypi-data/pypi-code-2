from django.contrib.auth import authenticate
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import AnonymousUser

from fromagerie.http import HttpResponseUnauthorized

# The following adapted from Piston by Jesper Noehr
# http://bitbucket.org/jespern/django-piston/
# Piston is Copyright (c) 2009 Jesper Noehr

class NoAuthentication(object):
    """
    Authentication handler that always returns
    True, so no authentication is needed, nor
    initiated (`challenge` is missing.)
    """
    def is_authenticated(self, request):
        return True

class HttpBasicAuthentication(object):
    """
    Basic HTTP authenticater. Synopsis:
    
    Authentication handlers must implement two methods:
     - `is_authenticated`: Will be called when checking for
        authentication. Receives a `request` object, please
        set your `User` object on `request.user`, otherwise
        return False (or something that evaluates to False.)
     - `challenge`: In cases where `is_authenticated` returns
        False, the result of this method will be returned.
        This will usually be a `HttpResponse` object with
        some kind of challenge headers and 401 code on it.
    """
    def __init__(self, auth_func=authenticate, realm='pypi'):
        self.auth_func = auth_func
        self.realm = realm

    def is_authenticated(self, request):
        auth_string = request.META.get('HTTP_AUTHORIZATION', request.META.get('AUTHORIZATION'))

        if not auth_string:
            return False
            
        (authmeth, auth) = auth_string.split(" ", 1)
        
        if not authmeth.lower() == 'basic':
            return False
        try:
            auth = auth.strip().decode('base64')
        except:
            return False
        (username, password) = auth.split(':', 1)
        
        request.user = self.auth_func(username=username, password=password) \
            or AnonymousUser()
        
        return not request.user in (False, None, AnonymousUser())
        
    def challenge(self, request):
        resp = HttpResponseUnauthorized()
        resp['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm
        return resp

class SessionAuthentication(object):
    def __init__(self, auth_func=authenticate):
        self.auth_func = auth_func

    def is_authenticated(self, request):
        return request.user.is_authenticated()

    def challenge(self, request):
        return redirect_to_login(request.path)
