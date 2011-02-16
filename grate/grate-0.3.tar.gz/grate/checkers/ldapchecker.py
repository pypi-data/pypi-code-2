from twisted.internet import defer
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernamePassword
from twisted.cred.error import UnauthorizedLogin
from twisted.python import log
from zope.interface import implements
import ldap
import gflags
from grate.mongo import User


gflags.DEFINE_string('ldap-uri', None, 'The LDAP uri. e.g. '
    'ldap://example.com')
gflags.DEFINE_string('ldap-dn', None, 'The LDAP DN')
gflags.DEFINE_boolean('ldap-tls', True, 'The LDAP TLS flag.')


class GrateLDAPChecker(object):
    credentialInterfaces = IUsernamePassword,
    implements(ICredentialsChecker)

    # uri looks like: ldap://example.com
    # dn looks like: "uid=%s,ou=people,dc=example,dc=com"
    # tls denotes if TLS should be turned on.
    def __init__(self, uri, dn, tls=True):
        """
        :param uri: The ldap URI. e.g. ldap://example.com
        :param dn: The ldap DN. e.g. uid=%s,ou=people,dc=example,dc=com
        :param tls: The flag to turn on TLS. (default True)
        """
        self.uri = uri
        self.dn = dn
        self.tls = tls

    def get_connection(self):
        """
        Fetches the ldap connection object.
        :returns: An ldap connection.
        """
        conn = ldap.initialize(self.uri)
        if self.tls:
            conn.start_tls_s()
        return conn

    def get_user(self, username):
        """
        :param username: The username.
        :returns: A User object.
        """
        user = User.objects(username=username).first()
        if not user:
            user = User(username=username)
            user.set_unusable_password()
            user.save(safe=True)
        return user

    def requestAvatarId(self, creds):
        """
        :creds: The credentials. We expect this to be `IUsernamePassword`
        :returns: The User object if successful, otherwise, a Failure.
        """
        username = creds.username
        password = creds.password
        # Form the query string.
        query = self.dn % username
        conn = None
        try:
            # Connect to ldap.
            conn = self.get_connection()
            # Try to bind as the user.
            result_type, _ = conn.simple_bind_s(query, password)
            if result_type == ldap.RES_BIND:
                # We were successful.
                return defer.succeed(self.get_user(username))
        except Exception as e:
            log.msg(str(e))
        finally:
            if conn:
                conn.unbind()
        return defer.fail(UnauthorizedLogin('Invalid password'))


def get_checker():
    FLAGS = gflags.FLAGS
    uri = getattr(FLAGS, 'ldap-uri')
    dn = getattr(FLAGS, 'ldap-dn')
    tls = getattr(FLAGS, 'ldap-tls')
    if not uri:
        log.err('LDAP URI not defined.')
    if not dn:
        log.err('LDAP DN not defined.')
    log.msg('LDAP URI %s' % uri)
    log.msg('LDAP DN  %s' % dn)
    return GrateLDAPChecker(uri, dn, tls)
