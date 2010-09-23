# copyright 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
"""unit tests for cubicweb.web.application"""

import base64, Cookie
import sys
from urllib import unquote

from logilab.common.testlib import TestCase, unittest_main
from logilab.common.decorators import clear_cache

from cubicweb import AuthenticationError, Unauthorized
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.fake import FakeRequest
from cubicweb.web import LogOut, Redirect, INTERNAL_FIELD_VALUE
from cubicweb.web.views.basecontrollers import ViewController

class FakeMapping:
    """emulates a mapping module"""
    def __init__(self):
        self.ENTITIES_MAP = {}
        self.ATTRIBUTES_MAP = {}
        self.RELATIONS_MAP = {}

class MockCursor:
    def __init__(self):
        self.executed = []
    def execute(self, rql, args=None, build_descr=False):
        args = args or {}
        self.executed.append(rql % args)


class FakeController(ViewController):

    def __init__(self, form=None):
        self._cw = FakeRequest()
        self._cw.form = form or {}
        self._cursor = MockCursor()
        self._cw.execute = self._cursor.execute

    def new_cursor(self):
        self._cursor = MockCursor()
        self._cw.execute = self._cursor.execute

    def set_form(self, form):
        self._cw.form = form


class RequestBaseTC(TestCase):
    def setUp(self):
        self._cw = FakeRequest()


    def test_list_arg(self):
        """tests the list_arg() function"""
        list_arg = self._cw.list_form_param
        self.assertEquals(list_arg('arg3', {}), [])
        d = {'arg1' : "value1",
             'arg2' : ('foo', INTERNAL_FIELD_VALUE,),
             'arg3' : ['bar']}
        self.assertEquals(list_arg('arg1', d, True), ['value1'])
        self.assertEquals(d, {'arg2' : ('foo', INTERNAL_FIELD_VALUE), 'arg3' : ['bar'],})
        self.assertEquals(list_arg('arg2', d, True), ['foo'])
        self.assertEquals({'arg3' : ['bar'],}, d)
        self.assertEquals(list_arg('arg3', d), ['bar',])
        self.assertEquals({'arg3' : ['bar'],}, d)


    def test_from_controller(self):
        self._cw.vreg['controllers'] = {'view': 1, 'login': 1}
        self.assertEquals(self._cw.from_controller(), 'view')
        req = FakeRequest(url='project?vid=list')
        req.vreg['controllers'] = {'view': 1, 'login': 1}
        # this assertion is just to make sure that relative_path can be
        # correctly computed as it is used in from_controller()
        self.assertEquals(req.relative_path(False), 'project')
        self.assertEquals(req.from_controller(), 'view')
        # test on a valid non-view controller
        req = FakeRequest(url='login?x=1&y=2')
        req.vreg['controllers'] = {'view': 1, 'login': 1}
        self.assertEquals(req.relative_path(False), 'login')
        self.assertEquals(req.from_controller(), 'login')


class UtilsTC(TestCase):
    """test suite for misc application utilities"""

    def setUp(self):
        self.ctrl = FakeController()

    #def test_which_mapping(self):
    #    """tests which mapping is used (application or core)"""
    #    init_mapping()
    #    from cubicweb.common import mapping
    #    self.assertEquals(mapping.MAPPING_USED, 'core')
    #    sys.modules['mapping'] = FakeMapping()
    #    init_mapping()
    #    self.assertEquals(mapping.MAPPING_USED, 'application')
    #    del sys.modules['mapping']

    def test_execute_linkto(self):
        """tests the execute_linkto() function"""
        self.assertEquals(self.ctrl.execute_linkto(), None)
        self.assertEquals(self.ctrl._cursor.executed,
                          [])

        self.ctrl.set_form({'__linkto' : 'works_for:12_13_14:object',
                              'eid': 8})
        self.ctrl.execute_linkto()
        self.assertEquals(self.ctrl._cursor.executed,
                          ['SET Y works_for X WHERE X eid 8, Y eid %s' % i
                           for i in (12, 13, 14)])

        self.ctrl.new_cursor()
        self.ctrl.set_form({'__linkto' : 'works_for:12_13_14:subject',
                              'eid': 8})
        self.ctrl.execute_linkto()
        self.assertEquals(self.ctrl._cursor.executed,
                          ['SET X works_for Y WHERE X eid 8, Y eid %s' % i
                           for i in (12, 13, 14)])


        self.ctrl.new_cursor()
        self.ctrl._cw.form = {'__linkto' : 'works_for:12_13_14:object'}
        self.ctrl.execute_linkto(eid=8)
        self.assertEquals(self.ctrl._cursor.executed,
                          ['SET Y works_for X WHERE X eid 8, Y eid %s' % i
                           for i in (12, 13, 14)])

        self.ctrl.new_cursor()
        self.ctrl.set_form({'__linkto' : 'works_for:12_13_14:subject'})
        self.ctrl.execute_linkto(eid=8)
        self.assertEquals(self.ctrl._cursor.executed,
                          ['SET X works_for Y WHERE X eid 8, Y eid %s' % i
                           for i in (12, 13, 14)])


class ApplicationTC(CubicWebTC):
    def setUp(self):
        super(ApplicationTC, self).setUp()
        def raise_hdlr(*args, **kwargs):
            raise
        self.app.error_handler = raise_hdlr

    def test_cnx_user_groups_sync(self):
        user = self.user()
        self.assertEquals(user.groups, set(('managers',)))
        self.execute('SET X in_group G WHERE X eid %s, G name "guests"' % user.eid)
        user = self.user()
        self.assertEquals(user.groups, set(('managers',)))
        self.commit()
        user = self.user()
        self.assertEquals(user.groups, set(('managers', 'guests')))
        # cleanup
        self.execute('DELETE X in_group G WHERE X eid %s, G name "guests"' % user.eid)
        self.commit()

    def test_nonregr_publish1(self):
        req = self.request(u'CWEType X WHERE X final FALSE, X meta FALSE')
        self.app.publish('view', req)

    def test_nonregr_publish2(self):
        req = self.request(u'Any count(N) WHERE N todo_by U, N is Note, U eid %s'
                           % self.user().eid)
        self.app.publish('view', req)

    def test_publish_validation_error(self):
        req = self.request()
        user = self.user()
        eid = unicode(user.eid)
        req.form = {
            'eid':       eid,
            '__type:'+eid:    'CWUser', '_cw_edited_fields:'+eid: 'login-subject',
            'login-subject:'+eid:     '', # ERROR: no login specified
             # just a sample, missing some necessary information for real life
            '__errorurl': 'view?vid=edition...'
            }
        path, params = self.expect_redirect(lambda x: self.app_publish(x, 'edit'), req)
        forminfo = req.session.data['view?vid=edition...']
        eidmap = forminfo['eidmap']
        self.assertEquals(eidmap, {})
        values = forminfo['values']
        self.assertEquals(values['login-subject:'+eid], '')
        self.assertEquals(values['eid'], eid)
        error = forminfo['error']
        self.assertEquals(error.entity, user.eid)
        self.assertEquals(error.errors['login-subject'], 'required field')


    def test_validation_error_dont_loose_subentity_data_ctrl(self):
        """test creation of two linked entities

        error occurs on the web controller
        """
        req = self.request()
        # set Y before X to ensure both entities are edited, not only X
        req.form = {'eid': ['Y', 'X'], '__maineid': 'X',
                    '__type:X': 'CWUser', '_cw_edited_fields:X': 'login-subject',
                    # missing required field
                    'login-subject:X': u'',
                    # but email address is set
                    '__type:Y': 'EmailAddress', '_cw_edited_fields:Y': 'address-subject',
                    'address-subject:Y': u'bougloup@logilab.fr',
                    'use_email-object:Y': 'X',
                    # necessary to get validation error handling
                    '__errorurl': 'view?vid=edition...',
                    }
        path, params = self.expect_redirect(lambda x: self.app_publish(x, 'edit'), req)
        forminfo = req.session.data['view?vid=edition...']
        self.assertEquals(set(forminfo['eidmap']), set('XY'))
        self.assertEquals(forminfo['eidmap']['X'], None)
        self.assertIsInstance(forminfo['eidmap']['Y'], int)
        self.assertEquals(forminfo['error'].entity, 'X')
        self.assertEquals(forminfo['error'].errors,
                          {'login-subject': 'required field'})
        self.assertEquals(forminfo['values'], req.form)


    def test_validation_error_dont_loose_subentity_data_repo(self):
        """test creation of two linked entities

        error occurs on the repository
        """
        req = self.request()
        # set Y before X to ensure both entities are edited, not only X
        req.form = {'eid': ['Y', 'X'], '__maineid': 'X',
                    '__type:X': 'CWUser', '_cw_edited_fields:X': 'login-subject,upassword-subject',
                    # already existent user
                    'login-subject:X': u'admin',
                    'upassword-subject:X': u'admin', 'upassword-subject-confirm:X': u'admin',
                    '__type:Y': 'EmailAddress', '_cw_edited_fields:Y': 'address-subject',
                    'address-subject:Y': u'bougloup@logilab.fr',
                    'use_email-object:Y': 'X',
                    # necessary to get validation error handling
                    '__errorurl': 'view?vid=edition...',
                    }
        path, params = self.expect_redirect(lambda x: self.app_publish(x, 'edit'), req)
        forminfo = req.session.data['view?vid=edition...']
        self.assertEquals(set(forminfo['eidmap']), set('XY'))
        self.assertIsInstance(forminfo['eidmap']['X'], int)
        self.assertIsInstance(forminfo['eidmap']['Y'], int)
        self.assertEquals(forminfo['error'].entity, forminfo['eidmap']['X'])
        self.assertEquals(forminfo['error'].errors,
                          {'login-subject': u'the value "admin" is already used, use another one'})
        self.assertEquals(forminfo['values'], req.form)


    def _test_cleaned(self, kwargs, injected, cleaned):
        req = self.request(**kwargs)
        page = self.app.publish('view', req)
        self.failIf(injected in page, (kwargs, injected))
        self.failUnless(cleaned in page, (kwargs, cleaned))

    def test_nonregr_script_kiddies(self):
        """test against current script injection"""
        injected = '<i>toto</i>'
        cleaned = 'toto'
        for kwargs in ({'__message': injected},
                       {'vid': injected},
                       {'vtitle': injected},
                       ):
            yield self._test_cleaned, kwargs, injected, cleaned

    def test_site_wide_eproperties_sync(self):
        # XXX work in all-in-one configuration but not in twisted for instance
        # in which case we need a kindof repo -> http server notification
        # protocol
        vreg = self.app.vreg
        # default value
        self.assertEquals(vreg.property_value('ui.language'), 'en')
        self.execute('INSERT CWProperty X: X value "fr", X pkey "ui.language"')
        self.assertEquals(vreg.property_value('ui.language'), 'en')
        self.commit()
        self.assertEquals(vreg.property_value('ui.language'), 'fr')
        self.execute('SET X value "de" WHERE X pkey "ui.language"')
        self.assertEquals(vreg.property_value('ui.language'), 'fr')
        self.commit()
        self.assertEquals(vreg.property_value('ui.language'), 'de')
        self.execute('DELETE CWProperty X WHERE X pkey "ui.language"')
        self.assertEquals(vreg.property_value('ui.language'), 'de')
        self.commit()
        self.assertEquals(vreg.property_value('ui.language'), 'en')

    def test_login_not_available_to_authenticated(self):
        req = self.request()
        ex = self.assertRaises(Unauthorized, self.app_publish, req, 'login')
        self.assertEquals(str(ex), 'log out first')

    def test_fb_login_concept(self):
        """see data/views.py"""
        self.set_option('auth-mode', 'cookie')
        self.set_option('anonymous-user', 'anon')
        self.login('anon')
        req = self.request()
        origcnx = req.cnx
        req.form['__fblogin'] = u'turlututu'
        page = self.app_publish(req)
        self.failIf(req.cnx is origcnx)
        self.assertEquals(req.user.login, 'turlututu')
        self.failUnless('turlututu' in page, page)

    # authentication tests ####################################################

    def test_http_auth_no_anon(self):
        req, origsession = self.init_authentication('http')
        self.assertAuthFailure(req)
        self.assertRaises(AuthenticationError, self.app_publish, req, 'login')
        self.assertEquals(req.cnx, None)
        authstr = base64.encodestring('%s:%s' % (origsession.login, origsession.authinfo['password']))
        req._headers['Authorization'] = 'basic %s' % authstr
        self.assertAuthSuccess(req, origsession)
        self.assertEquals(req.session.authinfo, {'password': origsession.authinfo['password']})
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEquals(len(self.open_sessions), 0)

    def test_cookie_auth_no_anon(self):
        req, origsession = self.init_authentication('cookie')
        self.assertAuthFailure(req)
        form = self.app_publish(req, 'login')
        self.failUnless('__login' in form)
        self.failUnless('__password' in form)
        self.assertEquals(req.cnx, None)
        req.form['__login'] = origsession.login
        req.form['__password'] = origsession.authinfo['password']
        self.assertAuthSuccess(req, origsession)
        self.assertEquals(req.session.authinfo, {'password': origsession.authinfo['password']})
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEquals(len(self.open_sessions), 0)

    def test_login_by_email(self):
        login = self.request().user.login
        address = login + u'@localhost'
        self.execute('INSERT EmailAddress X: X address %(address)s, U primary_email X '
                     'WHERE U login %(login)s', {'address': address, 'login': login})
        self.commit()
        # option allow-email-login not set
        req, origsession = self.init_authentication('cookie')
        req.form['__login'] = address
        req.form['__password'] = origsession.authinfo['password']
        self.assertAuthFailure(req)
        # option allow-email-login set
        origsession.login = address
        self.set_option('allow-email-login', True)
        req.form['__login'] = address
        req.form['__password'] = origsession.authinfo['password']
        self.assertAuthSuccess(req, origsession)
        self.assertEquals(req.session.authinfo, {'password': origsession.authinfo['password']})
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEquals(len(self.open_sessions), 0)

    def _reset_cookie(self, req):
        # preparing the suite of the test
        # set session id in cookie
        cookie = Cookie.SimpleCookie()
        cookie['__session'] = req.session.sessionid
        req._headers['Cookie'] = cookie['__session'].OutputString()
        clear_cache(req, 'get_authorization')
        # reset session as if it was a new incoming request
        req.session = req.cnx = None

    def _test_auth_anon(self, req):
        self.app.connect(req)
        asession = req.session
        self.assertEquals(len(self.open_sessions), 1)
        self.assertEquals(asession.login, 'anon')
        self.assertEquals(asession.authinfo['password'], 'anon')
        self.failUnless(asession.anonymous_session)
        self._reset_cookie(req)

    def _test_anon_auth_fail(self, req):
        self.assertEquals(len(self.open_sessions), 1)
        self.app.connect(req)
        self.assertEquals(req.message, 'authentication failure')
        self.assertEquals(req.session.anonymous_session, True)
        self.assertEquals(len(self.open_sessions), 1)
        self._reset_cookie(req)

    def test_http_auth_anon_allowed(self):
        req, origsession = self.init_authentication('http', 'anon')
        self._test_auth_anon(req)
        authstr = base64.encodestring('toto:pouet')
        req._headers['Authorization'] = 'basic %s' % authstr
        self._test_anon_auth_fail(req)
        authstr = base64.encodestring('%s:%s' % (origsession.login, origsession.authinfo['password']))
        req._headers['Authorization'] = 'basic %s' % authstr
        self.assertAuthSuccess(req, origsession)
        self.assertEquals(req.session.authinfo, {'password': origsession.authinfo['password']})
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEquals(len(self.open_sessions), 0)

    def test_cookie_auth_anon_allowed(self):
        req, origsession = self.init_authentication('cookie', 'anon')
        self._test_auth_anon(req)
        req.form['__login'] = 'toto'
        req.form['__password'] = 'pouet'
        self._test_anon_auth_fail(req)
        req.form['__login'] = origsession.login
        req.form['__password'] = origsession.authinfo['password']
        self.assertAuthSuccess(req, origsession)
        self.assertEquals(req.session.authinfo,
                          {'password': origsession.authinfo['password']})
        self.assertRaises(LogOut, self.app_publish, req, 'logout')
        self.assertEquals(len(self.open_sessions), 0)

    def test_non_regr_optional_first_var(self):
        req = self.request()
        # expect a rset with None in [0][0]
        req.form['rql'] = 'rql:Any OV1, X WHERE X custom_workflow OV1?'
        self.app_publish(req)

if __name__ == '__main__':
    unittest_main()
