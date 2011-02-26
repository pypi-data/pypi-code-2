"""Authentication functions are offered here.
"""

import bcrypt


###
### Password Helpers
###

BCRYPT = 'bcrypt'

PASSWD_DELIM = '|||'

def gen_hexdigest(raw_password, algorithm=BCRYPT, salt=None):
    """Takes the algorithm, salt and password and uses Python's
    hashlib to produce the hash. Currently only supports bcrypt.
    """
    if raw_password is None:
        raise ValueError('No empty passwords, fool')

    if algorithm is BCRYPT:
        # bcrypt has a special salt
        if salt is None:
            salt = bcrypt.gensalt()
        return (salt, bcrypt.hashpw(raw_password, salt))
    
    raise ValueError('Unknown password algorithm')


def build_passwd_line(algorithm, salt, digest):
    """Simply takes the inputs for a passwd entry and puts them
    into the convention for storage
    """
    return PASSWD_DELIM.join([algorithm, salt, digest])

def split_passwd_line(password_line):
    """Takes a password line and returns the line split by PASSWD_DELIM
    """
    return password_line.split(PASSWD_DELIM)


###
### Authentication decorators
###

def authenticated(method):
    """Decorate request handler methods with this to require that the user be
    logged in. Works by checking for the existence of self.current_user as set
    by a RequestHandler's prepare() function.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper
