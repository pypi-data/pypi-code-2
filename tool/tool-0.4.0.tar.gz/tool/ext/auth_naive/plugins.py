from glasnaegel.bundles.models import storage

# this bundle
from models import User



class ModelsAuthenticatorPlugin(object):

    def __init__(self):
        pass

    # IAuthenticatorPlugin
    def authenticate(self, environ, identity):
        #print dir(environ['werkzeug.request'])
        try:
            username = identity['login']
            password = identity['password']
        except KeyError:
            return None
        
        users = User.objects(storage).where(username=username)
        
        if not users:
            return None
        
        assert len(users) == 1, 'expected only one user with this username'
        
        user = users[0]

        if user.check_password(password):
            return user.pk
        
        return None
