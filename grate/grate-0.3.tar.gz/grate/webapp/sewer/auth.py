from django.conf import settings
from grate.mongo import User
try:
    import ldap
except ImportError:
    pass


class AuthBackend(object):

    def authenticate(self, username=None, password=None):
        if not username or not password:
            return None
        user = User.objects(username=username).first()
        if user and user.check_password(password):
            return user

    def get_user(self, user_id):
        return User.objects.with_id(user_id)


class TestAuthBackend(object):

    def authenticate(self, username=None, password=None):
        if not username:
            return None
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
        return user

    def get_user(self, user_id):
        return User.objects.with_id(user_id)


class LDAPAuthBackend(object):

    @staticmethod
    def ldap_match(username, password):
        try:
            # Connect to LDAP
            conn = ldap.initialize(settings.LDAP_HOST)
            # Try to bind as the user.
            result = conn.simple_bind_s(settings.LDAP_DN % username, password)
            # Check the result code (for 97).
            return result[0] == ldap.RES_BIND
        except ldap.LDAPError, e:
            return False

    def find(self, username):
        conn = ldap.initialize(settings.LDAP_HOST)
        result = conn.search_s('ou=people,%s' % settings.LDAP_DN,
            ldap.SCOPE_SUBTREE, '(cn=%s)' % username)
        return result

    def authenticate(self, username=None, password=None):
        if not username or not password:
            return None
        if self.ldap_match(username, password):
            user = User.objects(username=username).first()
            if not user:
                user = User()
                user.username = username
                user.password = '!'
                user.save()
            return user

    def get_user(self, user_id):
        return User.objects.with_id(user_id)
