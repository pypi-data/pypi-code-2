# coding=UTF-8

import unittest
import urllib
import base64

import formencode
import cherrypy

from turbogears import testutil, database, identity, config, startup, expose
from turbogears.controllers import Controller, RootController
from turbogears.identity import (SecureObject, SecureResource,
    in_group, in_all_groups, in_any_group, not_anonymous,
    has_permission, has_all_permissions, has_any_permission,
    from_host, from_any_host, Any, All, NotAny)
from turbogears.identity.conditions import _remoteHost
from turbogears.identity.soprovider import TG_User, TG_Group, TG_Permission
from turbogears.identity.exceptions import (IdentityConfigurationException,
    RequestRequiredException)
from turbogears.identity.visitor import IdentityVisitPlugin

# hub = database.AutoConnectHub("sqlite:///:memory:")
hub = database.PackageHub('turbogears.identity')


def mycustomencrypt(password):
    """A custom password encryption function."""
    return password + '_custom'


class MockIdentity(object):
    """Identity mock object."""

    anonymous = False
    groups = ('admin', 'edit')
    permissions = ('read', 'write')

mock_identity = MockIdentity()


class TestPredicates(unittest.TestCase):

    def met(self, predicate):
        return predicate.eval_with_object(mock_identity)

    def test_in_group(self):
        """Test the predicate for requiring a group."""
        assert self.met(in_group('admin'))
        assert not self.met(in_group('guest'))

    def test_in_all_groups(self):
        """Test the predicate for requiring a number of group."""
        assert self.met(in_all_groups('admin', 'edit'))
        assert not self.met(in_all_groups('admin', 'guest', 'edit'))

    def test_in_any_group(self):
        """Test the predicate for requiring at least one group."""
        assert self.met(in_any_group('guest', 'edit', 'user'))
        assert not self.met(in_all_groups('guest', 'user'))

    def test_anonymous(self):
        """Test predicate for checking anonymous visitors."""
        assert self.met(not_anonymous())

    def test_has_permission(self):
        """Test predicate for checking particular permissions."""
        assert self.met(has_permission('read'))
        assert not self.met(has_permission('delete'))

    def test_has_all_permissions(self):
        """Test the predicate for requiring a number of permissions."""
        assert self.met(has_all_permissions('read', 'write'))
        assert not self.met(has_all_permissions('read', 'delete', 'write'))

    def test_has_any_permission(self):
        """Test the predicate for requiring at least one permission."""
        assert self.met(has_any_permission('delete', 'write', 'update'))
        assert not self.met(has_any_permission('delete', 'update'))

    def test_any(self):
        """Test the Any predicate."""
        yes = in_group('edit')
        no1, no2 = in_group('guest'), in_group('user')
        met = self.met
        assert met(Any(yes))
        assert not met(Any(no1, no2))
        assert met(Any(no1, yes, no2))

    def test_all(self):
        """Test the All predicate."""
        yes1, yes2 = in_group('admin'), in_group('edit')
        no = in_group('guest')
        met = self.met
        assert not met(All(no))
        assert met(All(yes1, yes2))
        assert not met(All(yes1, no, yes2))

    def test_not_any(self):
        """Test the Not Any predicate."""
        yes = in_group('edit')
        no1, no2 = in_group('guest'), in_group('user')
        met = self.met
        assert not met(NotAny(yes))
        assert met(NotAny(no1, no2))
        assert not met(NotAny(no1, yes, no2))

    def test_remote_host_request_required(self):
        """Test that _remoteHost raises exception when request is not available.
        """
        self.assertRaises(RequestRequiredException, _remoteHost)


class TestSecureObject(unittest.TestCase):

    def test_secure_object_proxies_cp_attributes(self):
        """Test that SecureObject properly proxies CherryPy (_cp) attributes."""

        test_filters = ['filter1', 'filter2']

        class TestObject(object):
            _cp_filters = test_filters

        test_object = SecureObject(TestObject(), None)
        assert test_object._cp_filters == test_filters

        test_object = SecureObject(RootController(), None)
        test_object._cp_filters = test_filters
        assert test_object._cp_filters == test_filters

    def test_secure_object_proxies_setattr(self):
        """Test that SecureObject also proxies attributes assigned later."""

        class TestObject(object):
            pass

        test_object = SecureObject(TestObject(), None)
        assert isinstance(test_object._object, TestObject)

        test_object.value = 'value'
        assert test_object._object.value == 'value'


class RestrictedArea(Controller, SecureResource):

    require = in_group('peon')

    @expose()
    def index(self):
        return "restricted_index"

    @expose()
    @identity.require(in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(in_group('other'))
    def in_other_group(self):
        return 'in_other_group'

    @expose()
    def in_admin_group_explicit_check(self):
        if 'admin' not in identity.current.groups:
            raise identity.IdentityFailure("You need to be an Admin")
        else:
            return 'in_admin_group'

    @expose()
    def in_other_group_explicit_check(self):
        if 'other' not in identity.current.groups:
            raise identity.IdentityException
        else:
            return 'in_other_group'

    @expose(format='json')
    def json(self):
        return dict(json="restricted_json")


class IdentityRoot(RootController):

    @expose()
    def index(self):
        return dict()

    @expose(format='html')
    def identity_failed(self, **kw):
        """Identity failure - this usually returns a login form."""
        return 'identity_failed_answer'

    @expose()
    @identity.require(not_anonymous())
    def logged_in_only(self):
        return 'logged_in_only'

    @expose()
    @identity.require(in_group('peon'))
    def in_peon_group(self):
        user = TG_User.by_user_name("samIam")
        group_ids = set((TG_Group.by_group_name("peon").id,
            TG_Group.by_group_name("other").id))
        assert identity.current.user == user
        assert identity.current.user_name == user.user_name
        assert identity.current.user_id == user.id
        assert identity.current.groups == set(('peon', 'other'))
        assert identity.current.group_ids == group_ids
        assert "samIam" == cherrypy.serving.request.identity.user_name
        return 'in_peon_group'

    @expose()
    def remote_ip(self):
        return dict(remote_ip=_remoteHost())

    @expose()
    @identity.require(from_host('127.0.0.1'))
    def from_localhost(self):
        return "localhost_only"

    @expose()
    @identity.require(from_any_host(('127.0.0.1', '127.0.0.2')))
    def from_any_host(self):
        return "hosts_on_list_only"

    @expose()
    def test_exposed_require(self):
        if not hasattr(self.in_peon_group, '_require'):
            return 'no _require attr'
        if not isinstance(self.in_peon_group._require, in_group):
            return 'not correct class'
        if 'peon' != self.in_peon_group._require.group_name:
            return 'not correct group name'
        return '_require is exposed'

    @expose()
    @identity.require(in_group('admin'))
    def in_admin_group(self):
        return 'in_admin_group'

    @expose()
    @identity.require(has_permission('chops_wood'))
    def has_chopper_permission(self):
        return 'has_chopper_permission'

    @expose()
    @identity.require(has_permission('bosses_people'))
    def has_boss_permission(self):
        return "has_boss_permission"

    @expose()
    def logout(self):
        identity.current.logout()
        return "logged out"

    @expose()
    @identity.require(not_anonymous())
    def user_email(self):
        return identity.current.user.email_address

    peon_area = RestrictedArea()

    @expose()
    def new_user_setup(self, user_name, password):
        return '%s %s' % (user_name, password)

    _test_encoded_params = ('b=krümel&d.a=klöße1')

    @expose()
    @identity.require(not_anonymous())
    def test_params(self, **kwargs):
        params = self._test_encoded_params
        # formencode's variable_decode create a datastructure
        #  but does not "decode" anything
        to_datastruct = formencode.variabledecode.variable_decode
        expected_params = to_datastruct(
            dict([p.split('=') for p in params.split('&')]))
        params_ok = True
        if not expected_params['b'].decode(
                'utf8') == cherrypy.request.params['b']:
            params_ok = False
        if not expected_params['d']['a'].decode(
                'utf8') == cherrypy.request.params['d']['a']:
            params_ok = False
        if params_ok:
            return 'params ok'
        else:
            return 'wrong params: %s\nexpected unicode objects' \
                ' for all strings' % cherrypy.request.params

    @expose()
    def is_anonymous(self):
        assert cherrypy.serving.request.identity.user_name == None
        assert cherrypy.serving.request.identity.anonymous
        assert identity.current.anonymous
        return 'is_anonymous'

    @expose(format='json')
    @identity.require(in_group('peon'))
    def json(self):
        return dict(json="restricted_json")


class TestIdentity(testutil.TGTest):

    root = IdentityRoot

    stop_tg_only = True

    def setUp(self):
        # identity requires visit and a failure_url
        test_config = {'global': {
            'visit.on': True, 'identity.on': True,
            'visit.manager': 'sqlalchemy',
            'identity.failure_url': '/identity_failed',
            'identity.force_external_redirect': False,
            'identity.soprovider.encryption_algorithm': None,
            'identity.http_basic_auth': True,
            'identity.http_auth_realm': 'test realm',
            'tg.strict_parameters': True,
            'tg.allow_json': False}}
        if not self.config:
            original_config = dict()
            for key in test_config['global']:
                original_config[key] = config.get(key)
            self.config = original_config
        config.configure_loggers(test_config)
        config.update(test_config['global'])
        super(TestIdentity, self).setUp()
        config.update({'identity.http_basic_auth': False})
        self.init_model()

    def init_model(self):
        if TG_User.select().count() == 0:
            user = TG_User(user_name='samIam',
                email_address='samiam@example.com',
                display_name='Samuel Amicus', password='secret')
            admin_group = TG_Group(group_name="admin",
                display_name="Administrator")
            peon_group = TG_Group(group_name="peon",
                display_name="Regular Peon")
            other_group = TG_Group(group_name="other",
            display_name="Another Group")
            chopper_perm = TG_Permission(permission_name='chops_wood',
                description="Wood Chopper")
            boss_perm = TG_Permission(permission_name='bosses_people',
                description="Benevolent Dictator")
            peon_group.addTG_Permission(chopper_perm)
            admin_group.addTG_Permission(boss_perm)
            user.addTG_Group(peon_group)
            user.addTG_Group(other_group)

    def test_user_password_parameters(self):
        """Test that controller can receive user_name and password parameters."""
        response = self.app.get('/new_user_setup?user_name=test&password=pw')
        assert 'test pw' in response, response

    def test_user_exists(self):
        """Test that test user is present in data base."""
        u = TG_User.by_user_name('samIam')
        assert u.email_address == 'samiam@example.com'

    def test_user_password(self):
        """Test if we can set a user password (no encryption algorithm)."""
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password='password'
        u.sync()
        assert u.password == 'password'
        hub.rollback()
        hub.end()

    def test_user_password_unicode(self):
        """Test if we can set a non-ascii user password (no encryption)."""
        config.update({'identity.soprovider.encryption_algorithm': None})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = u'garçon'
        u.sync()
        assert u.password == u'garçon'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_sha(self):
        """Test if a sha hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'sha1'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = 'password'
        u.sync()
        assert u.password =='5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_sha_unicode(self):
        """Test if a non-ascii sha hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'sha1'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = u'garçon'
        u.sync()
        assert u.password == '442edb21c491a6e6f502eb79e98614f3c7edf43e'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5(self):
        """Test if a md5 hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = 'password'
        u.sync()
        assert u.password =='5f4dcc3b5aa765d61d8327deb882cf99'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5_unicode(self):
        """Test if a non-ascii md5 hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = u'garçon'
        u.sync()
        assert u.password == 'c295c4bb2672ca8c432effc53b40bb1e'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_md5_utf8string(self):
        """Test if a md5 hashed password with unicode characters is stored in
        the database if the password is entered as str (encoded in UTF-8). This
        test ensures that the encryption algorithm does handle non-unicode
        parameters gracefully."""
        config.update({'identity.soprovider.encryption_algorithm': 'md5'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = u'garçon'.encode('UTF-8')
        u.sync()
        assert u.password == 'c295c4bb2672ca8c432effc53b40bb1e'
        hub.rollback()
        hub.end()

    def test_user_password_raw(self):
        """Test that we can store raw values in the password field
        (without being hashed)."""
        config.update({'identity.soprovider.encryption_algorithm':'sha1'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.set_password_raw('password')
        u.sync()
        assert u.password =='password'
        hub.rollback()
        hub.end()

    def test_user_password_raw_unicode(self):
        """Test that unicode passwords are encrypted correctly"""
        config.update({'identity.soprovider.encryption_algorithm':'sha1'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.set_password_raw(u'garçon')
        u.sync()
        assert u.password == u'garçon'
        hub.rollback()
        hub.end()

    def test_user_password_hashed_custom(self):
        """Test if a custom hashed password is stored in the database."""
        config.update({'identity.soprovider.encryption_algorithm': 'custom',
            'identity.custom_encryption':
                'identity.tests.test_identity.mycustomencrypt'})
        self.app.get('/')
        hub.begin()
        u = TG_User.by_user_name('samIam')
        u.password = 'password'
        u.sync()
        assert u.password =='password_custom'
        hub.rollback()
        hub.end()

    def test_anonymous_browsing(self):
        """Test if we can show up anonymously."""
        response = self.app.get('/is_anonymous')
        assert 'is_anonymous' in response, response

    def test_deny_anonymous(self):
        """Test that we have secured an url from anonymous users."""
        response = self.app.get('/logged_in_only', status=403)
        assert 'identity_failed_answer' in response, response

    def test_deny_anonymous_viewable(self):
        """Test that a logged in user can see an resource blocked
        from anonymous users."""
        response = self.app.get('/logged_in_only?'
            'user_name=samIam&password=secret&login=Login')
        assert 'logged_in_only' in response, response

    def test_external_redirect(self):
        """Test that external redirection at identity failures works."""
        config.update({'identity.failure_url': 'test_login',
            'identity.force_external_redirect': True})
        response = self.app.get('/logged_in_only?a=1&b=2', status=302)
        assert 'identity_failed_answer' not in response, response
        path, params = response.headers['Location'].split('?', 1)
        assert path.endswith('/test_login')
        params = '&'.join(sorted(params.split('&')))
        assert params == 'a=1&b=2&forward_url=%2Flogged_in_only'

    def test_external_redirect_with_funky_params(self):
        """Test that external redirection properly handles funky parameters."""
        config.update({'identity.force_external_redirect': True})
        response = self.app.get('/logged_in_only?'
            'a-0.x=1&a-0.y=2&a-1.x=3&a-1.y=4', status=302)
        assert 'identity_failed_answer' not in response, response
        path, params = response.headers['Location'].split('?', 1)
        assert path.endswith('/identity_failed')
        params = '&'.join(sorted(params.split('&')))
        assert params == ('a-0.x=1&a-0.y=2&a-1.x=3&a-1.y=4'
            '&forward_url=%2Flogged_in_only')

    def test_authenticate_header(self):
        """Test that identity returns correct WWW-Authenticate header."""
        response = self.app.get('/logged_in_only', status=403)
        assert 'WWW-Authenticate' not in response.headers
        config.update({'identity.http_basic_auth': True})
        response = self.app.get('/logged_in_only', status=401)
        assert response.headers['WWW-Authenticate'] == 'Basic realm="test realm"'

    def test_basic_authentication(self):
        """Test HTTP basic authentication mechanism."""
        config.update({'identity.http_basic_auth': True})
        credentials = base64.encodestring('samIam')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials}, status=401)
        assert 'identity_failed_answer' in response, response
        credentials = base64.encodestring('samIam:secret:appendix')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials}, status=401)
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic samIam:secret'}, status=401)
        assert 'identity_failed_answer' in response, response
        credentials = base64.encodestring('samIam:secret')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials})
        assert 'logged_in_only' in response, response

    def test_logout(self):
        """Test that logout works and session id gets invalid afterwards."""
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        session_id = response.headers['Set-Cookie']
        response = self.app.get('/logout', headers={'Cookie': session_id})
        response = self.app.get('/is_anonymous', headers={'Cookie': session_id})
        assert response.body == 'is_anonymous'

    def test_require_group(self):
        """Test that an anonymous user can not access resource protected by
        require(in_group(...))"""
        response = self.app.get('/in_peon_group', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_expose_required_permission(self):
        """Test that the decorator exposes the correct permissions via _require
        attribute on the actual method."""
        response = self.app.get('/test_exposed_require')
        assert 'require is exposed' in response, response

    def test_user_and_group_properties(self):
        """Test that the current user and group properties are set correctly."""
        user = TG_User.by_user_name("samIam")
        group_ids = set((TG_Group.by_group_name("peon").id,
            TG_Group.by_group_name("other").id))
        assert user.user_name == 'samIam'
        assert group_ids == set((2, 3))

    def test_require_group_viewable(self):
        """Test that a user with proper group membership can see a restricted url."""
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_peon_group' in response, response

    def test_user_not_in_right_group(self):
        """Test that only users in the right group have access."""
        response = self.app.get('/in_admin_group?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_permission(self):
        """Test that an anonymous user is denied access to a permission
        restricted url.
        """
        response = self.app.get('/has_chopper_permission', status=403)
        assert 'identity_failed_answer' in response, response

    def test_require_permission_viewable(self):
        """Test that a user with proper permissions can see a restricted url."""
        response = self.app.get('/has_chopper_permission?'
            'user_name=samIam&password=secret&login=Login')
        assert 'has_chopper_permission' in response, response

    def test_user_lacks_permission(self):
        """Test that a user is denied acces if they don't have the proper
        permission.
        """
        response = self.app.get('/has_boss_permission?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_user_info_available(self):
        """Test that we can see user information inside our controller."""
        response = self.app.get('/user_email?'
            'user_name=samIam&password=secret&login=Login')
        assert 'samiam@example.com' in response, response

    def test_bad_login(self):
        """Test that we are denied access if we provide a bad login."""
        response = self.app.get('/logged_in_only?'
            'user_name=samIam&password=wrong&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_restricted_subdirectory(self):
        """Test that we can restrict access to a whole subdirectory."""
        response = self.app.get('/peon_area/index', status=403)
        assert 'identity_failed_answer' in response, response

    def test_restricted_subdirectory_viewable(self):
        """Test that we can access a restricted subdirectory
        if we have proper credentials."""
        response = self.app.get('/peon_area/index?'
            'user_name=samIam&password=secret&login=Login')
        assert 'restricted_index' in response, response

    def test_decoratator_in_restricted_subdirectory(self):
        """Test that we can require a different permission
        in a protected subdirectory."""
        response = self.app.get('/peon_area/in_other_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_other_group' in response, response

    def test_decoratator_failure_in_restricted_subdirectory(self):
        """Test that we can get an identity failure from a decorator
        in a restricted subdirectory"""
        response = self.app.get('/peon_area/in_admin_group?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed_answer' in response, response

    def test_explicit_checks_in_restricted_subdirectory(self):
        """Test that explicit permission checks in a protected
        directory is handled as expected"""
        response = self.app.get('/peon_area/in_other_group_explicit_check?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_other_group' in response, response

    def test_throwing_identity_exception_in_restricted_subdirectory(self):
        """Test that throwing an IdentityException in a protected
        directory is handled as expected"""
        response = self.app.get('/peon_area/in_admin_group_explicit_check?'
            'user_name=samIam&password=secret&login=Login', status=403)
        assert 'identity_failed' in response, response

    def test_decode_filter_whenidfails(self):
        """Test that the decode filter doesn't break with nested
        variables and Identity"""
        params = urllib.quote(IdentityRoot._test_encoded_params.decode(
            'utf-8').encode('latin-1'), '=&')
        response = self.app.get('/test_params?' + params, status=403)
        assert 'identity_failed_answer' in response, response

    def test_decode_filter_whenidworks(self):
        """Test that the decode filter doesn't break with nested
        variables and Identity"""
        params = urllib.quote(IdentityRoot._test_encoded_params.decode(
            'utf-8').encode('latin-1'), '=&')
        params += '&user_name=samIam&password=secret&login=Login'
        response = self.app.get('/test_params?' + params)
        assert 'params ok' in response, response

    def test_user_unicode(self):
        """Test that we can have non-ascii user names."""
        user = TG_User(user_name=u'säm', display_name=u'Sämüel Käsfuß',
            email_address='samkas@example.com', password='geheim')
        response = self.app.get('/logged_in_only?'
            'user_name=säm&password=geheim&login=Login')
        assert 'logged_in_only' in response, response
        self.app.reset()
        credentials = base64.encodestring('säm:geheim')[:-1]
        response = self.app.get('/logged_in_only', headers={
            'Authorization': 'Basic %s' % credentials})
        assert 'logged_in_only' in response, response

    def test_json(self):
        """Test that JSON controllers return the right status codes."""
        # We check that we get an authorization error, not the server error
        # caused by the identity_failure controller not accepting JSON.
        response = self.app.get('/json', status=403)
        # we get the output of the identity_failure controller in this case
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/json?tg_format=json', status=403)
        # we get the right status code, but not the output of identity_failure
        assert 'identity_failed_answer' not in response, response
        assert 'Request forbidden' in response, response
        response = self.app.get('/peon_area/json', status=403)
        assert 'identity_failed_answer' in response, response
        response = self.app.get('/peon_area/json?tg_format=json', status=403)
        assert 'identity_failed_answer' not in response, response
        response = self.app.get('/in_peon_group?'
            'user_name=samIam&password=secret&login=Login')
        assert 'in_peon_group' in response, response
        response = self.app.get('/json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/json?tg_format=json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/peon_area/json', status=200)
        assert 'restricted_json' in response, response
        response = self.app.get('/peon_area/json?tg_format=json', status=200)
        assert 'restricted_json' in response, response

    def test_remote_ip(self):
        """Test that our client IP is detected correctly."""
        r = self.app.get('/remote_ip', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert r.raw['remote_ip'] == '127.0.0.1'
        r = self.app.get('/remote_ip',
            headers={'X-Forwarded-For': '192.168.1.100, 224.50.214.12'},
            status=200)
        assert r.raw['remote_ip'] == '224.50.214.12'

    def test_from_localhost(self):
        """Test we can connect from 127.0.0.1."""
        r = self.app.get('/from_localhost', headers={'Remote-Addr': '192.168.4.100'},
            status=403)
        assert 'identity_failed_answer' in r
        r = self.app.get('/from_localhost', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert 'localhost_only' in r

    def test_from_any_host(self):
        """Test we can connect from any host in an IP list."""
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '192.168.4.100'},
            status=403)
        assert 'identity_failed_answer' in r
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '127.0.0.1'},
            status=200)
        assert 'hosts_on_list_only' in r
        r = self.app.get('/from_any_host', headers={'Remote-Addr': '127.0.0.2'},
            status=200)
        assert 'hosts_on_list_only' in r

    def test_nested_login(self):
        """Check that we can login using a nested form."""
        config.update({
            'identity.form.user_name': 'credentials.user',
            'identity.form.password': 'credentials.pass',
            'identity.form.submit': 'log.me.in'})
        testutil.stop_server(tg_only=False)
        self.app = testutil.make_app(self.root)
        testutil.start_server()
        response = self.app.get('/logged_in_only?'
            'credentials.user=samIam&credentials.pass=secret&log.me.in=Enter')
        assert 'logged_in_only' in response, response


class TestTGUser(testutil.DBTest):

    model = TG_User

    def setUp(self):
        self._identity_on = config.get('identity.on', False)
        config.update({'identity.on': False})
        super(TestTGUser, self).setUp()

    def tearDown(self):
        testutil.stop_server()
        super(TestTGUser, self).tearDown()
        config.update({'identity.on': self._identity_on})

    def test_create_user(self):
        """Test that User can be created outside of a running identity provider."""
        u = TG_User(user_name='testcase',
            email_address='testcase@example.com',
            display_name='Test Me', password='test')
        assert u.password=='test', u.password


class TestIdentityVisitPlugin(unittest.TestCase):

    config = None

    def setUp(self):
        test_config = {'global': {
            'visit.on': True,
            'identity.on': True,
            'identity.http_basic_auth': True,
            'identity.source': 'form, http_auth, visit'}}
        if not self.config:
            original_config = dict()
            for key in test_config['global']:
                original_config[key] = config.get(key)
            self.config = original_config
        config.update(test_config['global'])

    def tearDown(self):
        config.update(self.config)

    def test_identity_source(self):
        """Test that identity.source setting is parsed correctly."""
        plug = IdentityVisitPlugin()
        assert plug.identity_from_form in plug.identity_sources
        assert plug.identity_from_http_auth in plug.identity_sources
        assert plug.identity_from_visit in plug.identity_sources

    def test_unknown_identity_source(self):
        """Test that unknown identity source raises identity configuration error."""
        config.update({'identity.source': 'bogus'})
        self.assertRaises(IdentityConfigurationException, IdentityVisitPlugin)

    def test_decode_credentials(self):
        """Test that HTTP basic auth credentials are decoded correctly."""
        plug = IdentityVisitPlugin()
        credentials = base64.encodestring('samIam:secret')[:-1]
        assert plug.decode_basic_credentials(credentials) == ['samIam', 'secret']
