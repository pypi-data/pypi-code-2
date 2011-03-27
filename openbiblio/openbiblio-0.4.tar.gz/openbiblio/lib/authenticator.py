from zope.interface import implements
from repoze.who.interfaces import IAuthenticator

from openbiblio.model import Account

class OpenIDAuthenticator(object):
    implements(IAuthenticator)
    
    def authenticate(self, environ, identity):
        if 'repoze.who.plugins.openid.userid' in identity:
            return identity.get("repoze.who.plugins.openid.userid")
        return None

