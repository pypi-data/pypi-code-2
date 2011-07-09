import logging
from gae.sessions import get_current_session
from gae.config import get_config
from user.models import User

def get_current_user():
    '''Return current user; otherwise return unautorized user object'''
    session = get_current_session()
    if "user" not in session:
        return None # TODO: return anonimous User() object
    return session['user']

def get_login_url(back_url):
    '''Return url for user login'''
    return "/user/login?back_url=%s" % back_url

def get_logout_url(back_url):
    '''Return url for user logout'''
    return "/user/logout?back_url=%s" % back_url

def login_required(*roles):
    '''
    Decorator for logged users only.

    Args:
        roles - list of roles for users who have access to given request handler
    '''
    def wrap(handler_method):
        def check_login(self, *args, **kwargs):
            user = get_current_user()
            # not logged
            if not user:
                return self.redirect(get_login_url(self.request.path))
            # roles not specified
            if not roles:
                return handler_method(self, *args, **kwargs)
            # check role
            for role in roles:
                # allow access with given role
                if user.has_role(role):
                    return handler_method(self, *args, **kwargs)
            # access denied
            return self.error(401)
        return check_login
    return wrap