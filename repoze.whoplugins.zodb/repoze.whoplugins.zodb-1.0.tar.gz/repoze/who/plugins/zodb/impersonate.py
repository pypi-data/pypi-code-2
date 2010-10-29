
from repoze.who.interfaces import IAuthenticator
from zope.interface import implements

import logging
log = logging.getLogger(__name__)

class ImpersonatePlugin(object):
    """Provides administrators a simple way to impersonate users for testing.

    If you're a superuser, specify the name to impersonate in the login
    field and "super_login:super_pass" in the password field.

    Inspired by http://nedbatchelder.com/blog/200905/log_in_as_a_user.html
    """

    implements(IAuthenticator)

    def __init__(self, plugin_name, super_group):
        self.plugin_name = plugin_name
        self.super_group = super_group

    def authenticate(self, environ, identity):
        if not 'login' in identity:
            return None
        password = identity.get('password', '')
        if ':' in password:
            plugin = environ['repoze.who.plugins'][self.plugin_name]
            alt_login, alt_pass = password.split(':', 1)
            alt_identity = identity.copy()
            alt_identity['login'] = alt_login
            alt_identity['password'] = alt_pass
            alt_userid = plugin.authenticate(environ, alt_identity)
            if alt_userid:
                # got a valid alternate login in the password field,
                # but we don't yet know if that person is really
                # a superuser.
                return self._attempt_impersonate(
                    environ, plugin, alt_userid, identity['login'])
        return None

    def _attempt_impersonate(self, environ, plugin, real_id, effective_login):
        conn, from_environ = plugin.get_connection(environ)
        try:
            users = plugin.get_users(conn)
            if users.in_group(real_id, self.super_group):
                # authenticated real_id as a superuser, so allow impersonation
                user = users.get_by_login(effective_login)
                if user:
                    effective_id = user['id']
                    log.info(
                        "Superuser %s is impersonating %s",
                        real_id, effective_id)
                    return effective_id
            return None
        finally:
            if not from_environ:
                conn.transaction_manager.abort()
                conn.close()

def make_plugin(plugin_name, super_group):
    return ImpersonatePlugin(plugin_name, super_group)
