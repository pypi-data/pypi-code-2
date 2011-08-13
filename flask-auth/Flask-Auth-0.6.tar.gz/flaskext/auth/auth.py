"""
Base module of the extension. Contains basic functions, the Auth object and the
AuthUser base class.
"""

import time, hashlib, datetime
from flask import session, abort, current_app

DEFAULT_HASH_ALGORITHM = hashlib.sha1

DEFAULT_USER_TIMEOUT = 3600

SESSION_USER_KEY = 'auth_user'
SESSION_LOGIN_KEY = 'auth_login'

def _default_not_authorized(*args, **kwargs):
    return abort(401)

class Auth(object):
    """
    Extension initialization object containing settings for the extension.
    
    Supported settings:
        - not_logged_in_callback: Function to call when a user accesses a page
        without being logged in. Normally used to redirect to the login page.
        Default: abort(401).
        - not_permitted_callback: Function to call when a user tries to access
        a page for which he doesn't have the permission. Default: abort(401).
        - hash_algorithm: Algorithm from the hashlib library used for password
        encryption. Default: sha1.
        - user_timeout: Timeout (in seconds) after which the sesion of the user
        expires. Default: 3600. A timeout of 0 means it will never expire.
        - load_role: Function to load a role. Is called with user.role as only
        parameter.
    """

    def __init__(self, app=None):
        self.not_logged_in_callback = _default_not_authorized
        self.not_permitted_callback = _default_not_authorized
        self.hash_algorithm = DEFAULT_HASH_ALGORITHM
        self.user_timeout = DEFAULT_USER_TIMEOUT
        self.load_role = lambda _: None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.auth = self
        
class AuthUser(object):
    """
    Baseclass for a user model. Contains a few convenient methods.

    Attributes:
        - username:
            Username of the user.
        - password: 
            Password of the user. By default not encrypted. The
            set_and_encrypt_password() method sets and encrypts the password.
        - password_hash: 
            Hash used for the encrytion of the password.
        - role:
            Role of this user.
    """

    role = None

    def __init__(self, username, password=None, password_hash=None, role=None):
        self.username = username
        # Encryption of the password should happen explicitly.
        self.password = password
        self.password_hash = password_hash
        self.role = role

    def set_and_encrypt_password(self, password, password_hash=str(int(time.time()))):
        """
        Encrypts and sets the password. If no password_hash is provided, a new
        one is generated.
        """
        self.password_hash = password_hash
        self.password = encrypt(password, self.password_hash)

    def authenticate(self, password):
        """
        Attempts to verify the password and log the user in. Returns true if 
        succesful.
        """
        if self.password == encrypt(password, self.password_hash):
            login(self)
            return True
        return False

def encrypt(password, password_hash=None, hash_algorithm=None):
    """Encrypts a password based on the hashing algorithm."""
    to_encrypt = password
    if password_hash is not None:
        to_encrypt += password_hash
    return current_app.auth.hash_algorithm(to_encrypt).hexdigest()

def login(user):
    """
    Logs the user in. Note that NO AUTHENTICATION is done by this function. If
    you want to authenticate a user, use the AuthUser.authenticate() method.
    """
    session[SESSION_USER_KEY] = user
    session[SESSION_LOGIN_KEY] = datetime.datetime.utcnow()

def logout():
    """Logs the currently logged in user out and returns the user (if any)."""
    session.pop(SESSION_LOGIN_KEY, None)
    return session.pop(SESSION_USER_KEY, None)
    
def get_current_user(timeout=True):
    """
    Returns the current user if there is one and he didn't time out yet. If
    timeout should be ignored, provide timeout=False.
    """
    user = session.get(SESSION_USER_KEY, None)
    if user is None:
        return None
    if not timeout:
        return user
    login_datetime = session[SESSION_LOGIN_KEY]
    now = datetime.datetime.utcnow()
    timeout = current_app.auth.user_timeout
    if timeout > 0 and (now - login_datetime).seconds > timeout:
        logout()
        return None
    return user

def login_required(callback=None):
    """
    Decorator for views that require login. Callback can be specified to
    override the default callback on the auth object.
    """
    def wrap(func):
        def decorator(*args, **kwargs):
            if get_current_user() is not None:
                return func(*args, **kwargs)
            if callback is None:
                return current_app.auth.not_logged_in_callback(*args, **kwargs)
            else:
                return callback(*args, **kwargs)
        return decorator
    return wrap
