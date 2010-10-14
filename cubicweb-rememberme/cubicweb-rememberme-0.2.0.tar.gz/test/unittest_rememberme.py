from datetime import timedelta, datetime

from logilab.common.testlib import unittest_main
from logilab.common.decorators import clear_cache

from cubicweb.devtools.testlib import CubicWebTC

def init_auth_cookie(req, login, magicnum):
    req.cnx = None
    req.form = {}
    clear_cache(req, 'get_authorization')
    cookie = req.get_cookie()
    cookie['__cw_auth_cookie'] = '%s|__magic=%s' % (login, magicnum)
    req.set_cookie(cookie, '__cw_auth_cookie')

def init_login_password(req, login):
    req.cnx = None
    req.form = {}
    clear_cache(req, 'get_authorization')
    req.form['__login'] = login
    req.form['__password'] = login
    cookie = req.get_cookie()
    req.remove_cookie(cookie, '__cw_auth_cookie')

class RememberMeAuthenticationTC(CubicWebTC):

    def test_auth_cookie_authentication(self):
        self.create_user('user')
        self.login('user')
        req, origcnx = self.init_authentication('cookie')
        assert req.user.login == 'user'
        origcnx.login = 'user'
        # bad magic number
        init_auth_cookie(req, 'user', '1234')
        self.assertAuthFailure(req)
        # valid login / password, not asked to remember user
        init_login_password(req, 'user')
        self.assertAuthSuccess(req, origcnx)
        cookies = req.user.reverse_auth_cookie_for_user
        self.assertEqual(len(cookies), 0)
        # valid login / password, ask to remember user
        init_login_password(req, 'user')
        req.form['__setauthcookie'] = 1
        self.assertAuthSuccess(req, origcnx, nbsessions=2)
        req.user.clear_all_caches()
        cookies = req.user.reverse_auth_cookie_for_user
        self.assertEqual(len(cookies), 1)
        magicnum = cookies[0].magicnumber
        self.assertEqual(cookies[0].lifetime, timedelta(days=30))
        # bad login in auth cookie
        init_auth_cookie(req, 'admin', magicnum)
        self.assertAuthFailure(req, nbsessions=2)
        # valid auth cookie
        init_auth_cookie(req, 'user', magicnum)
        self.assertAuthSuccess(req, origcnx, nbsessions=3)
        req.user.clear_all_caches()
        cookies = req.user.reverse_auth_cookie_for_user
        self.assertEqual(len(cookies), 1)
        magicnum2 = cookies[0].magicnumber
        self.failIf(magicnum2 == magicnum)
        self.assertEqual(req.session.authinfo, {'magicnumber': magicnum2})

if __name__ == '__main__':
    unittest_main()
