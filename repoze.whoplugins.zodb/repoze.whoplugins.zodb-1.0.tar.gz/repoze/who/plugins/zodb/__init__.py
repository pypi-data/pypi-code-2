try:
    import hashlib
except ImportError: # pragma: no cover  # Python < 2.5
    import sha # pragma: no cover
    _sha = sha.new # pragma: no cover
else:
    _sha = hashlib.sha1 # pragma: no cover

from zope.interface import implements

from repoze.who.interfaces import IMetadataProvider
from repoze.who.interfaces import IAuthenticator
from repoze.who.utils import resolveDotted

from repoze.zodbconn.finder import dbfactory_from_uri

from repoze.who.plugins.zodb.users import get_sha_password
from repoze.who.plugins.zodb.users import Users

import transaction

CONNECTION_KEY = 'repoze.zodbconn.connection'

class ZODBPlugin:
    implements(IAuthenticator, IMetadataProvider)
    dbfactory = staticmethod(dbfactory_from_uri) # for testing override

    def __init__(self, zodb_uri, users_finder, connection_key=CONNECTION_KEY):
        self.zodb_uri = zodb_uri
        self.users_finder = users_finder
        self.db = None
        self.connection_key = connection_key

    def _getdb(self):
        if self.db is None:
            if self.zodb_uri is None:
                raise ValueError('zodb_uri must not be None')
            dbfactory = self.dbfactory(self.zodb_uri)
            self.db = dbfactory()
        return self.db

    def get_connection(self, environ):
        conn = environ.get(self.connection_key)
        if conn is not None:
            from_environ = True
        else:
            from_environ = False
            conn = self._getdb().open()
        return conn, from_environ

    def get_users(self, conn):
        root = conn.root()
        return self.users_finder(root)

    def authenticate(self, environ, identity):
        if not 'login' in identity:
            return None
        conn, from_environ = self.get_connection(environ)
        try:
            users = self.get_users(conn)
            info = users.get(login=identity['login'])
            if info:
                sha_password = get_sha_password(identity['password'])
                if sha_password == info.get('password'):
                    return info['id']
        finally:
            if not from_environ:
                conn.transaction_manager.abort()
                conn.close()

    def add_metadata(self, environ, identity):
        userid = identity['repoze.who.userid']
        conn, from_environ = self.get_connection(environ)
        try:
            users = self.get_users(conn)
            info = users.get(userid)
            if not info:
                return
            identity['groups'] = [group for group in info['groups']]
        finally:
            if not from_environ:
                conn.transaction_manager.abort()
                conn.close()


def make_plugin(zodb_uri=None, users_finder=None,
        connection_key=CONNECTION_KEY):
    if users_finder is None:
        raise ValueError('users_finder must not be None')
    users_finder = resolveDotted(users_finder)
    return ZODBPlugin(zodb_uri, users_finder, connection_key)

def default_users_finder(root, transaction=transaction):
    if not 'users' in root:
        root['users'] = Users()
        transaction.commit()
    return root['users']


