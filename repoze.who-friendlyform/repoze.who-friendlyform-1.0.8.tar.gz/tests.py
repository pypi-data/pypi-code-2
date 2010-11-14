# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009-2010, Gustavo Narea <me@gustavonarea.net> and contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test suite for the collection of :mod:`repoze.who` friendly forms."""
from StringIO import StringIO
from unittest import TestCase
from urllib import quote as original_quoter

from zope.interface.verify import verifyClass
from paste.httpexceptions import HTTPFound
from repoze.who.interfaces import IIdentifier, IChallenger

from repoze.who.plugins.friendlyform import FriendlyFormPlugin

# Let's prevent the original quote() from leaving slashes:
quote = lambda txt: original_quoter(txt, '')


class TestFriendlyFormPlugin(TestCase):

    def test_implements(self):
        verifyClass(IIdentifier, FriendlyFormPlugin)
        verifyClass(IChallenger, FriendlyFormPlugin)
    
    def test_constructor(self):
        p = self._make_one()
        self.assertEqual(p.login_counter_name, '__logins')
        self.assertEqual(p.post_login_url, None)
        self.assertEqual(p.post_logout_url, None)
    
    def test_constructor_with_loging_counter_as_None(self):
        p = self._make_one(login_counter_name=None)
        self.assertEqual(p.login_counter_name, '__logins')
    
    def test_classification(self):
        """FriendlyForm only participate when the UA is a browser."""
        p = self._make_one(login_counter_name=None)
        self.assertTrue(p.classifications)
        self.assertEqual(2, len(p.classifications))
        # It must only identify when the UA is a browser:
        self.assertTrue(IIdentifier in p.classifications)
        self.assertEqual(1, len(p.classifications[IIdentifier]))
        self.assertEqual(p.classifications[IIdentifier][0], "browser")
        # It must only challenge when the UA is a browser:
        self.assertTrue(IChallenger in p.classifications)
        self.assertEqual(1, len(p.classifications[IChallenger]))
        self.assertEqual(p.classifications[IChallenger][0], "browser")
    
    def test_repr(self):
        p = self._make_one()
        self.assertEqual(repr(p), '<FriendlyFormPlugin %s>' % id(p))
    
    def test_login_without_postlogin_page(self):
        """
        The page to be redirected to after login must include the login 
        counter.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        came_from = '/some_path'
        environ = self._make_environ('/login_handler',
                                     'came_from=%s' % quote(came_from))
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        new_redirect = came_from + '?__logins=0'
        self.assertEqual(app.location, new_redirect)
    
    def test_post_login_page_as_url(self):
        """Post-logout pages can also be defined as URLs, not only paths"""
        # --- Configuring the plugin:
        login_url = 'http://example.org/welcome'
        p = self._make_one(post_login_url=login_url)
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, login_url + '?__logins=0')
    
    def test_post_login_page_with_SCRIPT_NAME(self):
        """
        While redirecting to the post-login page, the SCRIPT_NAME must be
        taken into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, '/my-app/welcome_back?__logins=0')
    
    def test_post_login_page_with_SCRIPT_NAME_and_came_from(self):
        """
        While redirecting to the post-login page with the came_from variable, 
        the SCRIPT_NAME must be taken into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        came_from = '/something'
        environ = self._make_environ('/login_handler',
                                     'came_from=%s' % quote(came_from),
                                     SCRIPT_NAME='/my-app')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        redirect = '/my-app/welcome_back?__logins=0&came_from=%s'
        self.assertEqual(app.location, redirect % quote(came_from))
    
    def test_post_login_page_without_login_counter(self):
        """
        If there's no login counter defined, the post-login page should receive
        the counter at zero.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, '/welcome_back?__logins=0')
    
    def test_post_login_page_with_login_counter(self):
        """
        If the login counter is defined, the post-login page should receive it
        as is.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', '__logins=2',
                                     redirect='/some_path')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, '/welcome_back?__logins=2')
    
    def test_post_login_page_with_invalid_login_counter(self):
        """
        If the login counter is defined with an invalid value, the post-login 
        page should receive the counter at zero.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        environ = self._make_environ('/login_handler', '__logins=non_integer',
                                     redirect='/some_path')
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, '/welcome_back?__logins=0')
    
    def test_post_login_page_with_referrer(self):
        """
        If the referrer is defined, it should be passed along with the login
        counter to the post-login page.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_login_url='/welcome_back')
        # --- Configuring the mock environ:
        orig_redirect = '/some_path'
        came_from = quote('http://example.org')
        environ = self._make_environ(
            '/login_handler',
            '__logins=3&came_from=%s' % came_from,
            redirect=orig_redirect,
            )
        # --- Testing it:
        p.identify(environ)
        app = environ['repoze.who.application']
        new_url = '/welcome_back?__logins=3&came_from=%s' % came_from
        self.assertEqual(app.location, new_url)
    
    def test_login_page_with_login_counter(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins'.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/login', '__logins=2')
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 2)
        self.assertEqual(environ['QUERY_STRING'], '')
    
    def test_login_page_without_login_counter(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins' 
        and if it's not defined in the query string, set it to zero in the
        environ.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/login')
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 0)
        self.assertEqual(environ['QUERY_STRING'], '')
    
    def test_login_page_with_camefrom(self):
        """
        In the page where the login form is displayed, the login counter
        must be defined in the WSGI environment variable 'repoze.who.logins' 
        and hidden in the query string available in the environ.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        came_from = 'http://example.com'
        environ = self._make_environ('/login',
                                     'came_from=%s' % quote(came_from))
        # --- Testing it:
        p.identify(environ)
        self.assertEqual(environ['repoze.who.logins'], 0)
        self.assertEqual(environ['QUERY_STRING'], 
                         'came_from=%s' % quote(came_from))
    
    def test_logout_without_post_logout_page(self):
        """
        Users must be redirected to '/' on logout if there's no referrer page
        and no post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, '/')
    
    def test_logout_with_SCRIPT_NAME_and_without_post_logout_page(self):
        """
        Users must be redirected to SCRIPT_NAME on logout if there's no 
        referrer page and no post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, '/my-app')
    
    def test_logout_with_camefrom_and_without_post_logout_page(self):
        """
        Users must be redirected to the referrer page on logout if there's no
        post-logout page defined.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        environ['came_from'] = '/somewhere'
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, '/somewhere')
    
    def test_logout_with_post_logout_page(self):
        """Users must be redirected to the post-logout page, if defined"""
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, '/see_you_later')
    
    def test_logout_with_post_logout_page_as_url(self):
        """Post-logout pages can also be defined as URLs, not only paths"""
        # --- Configuring the plugin:
        logout_url = 'http://example.org/see_you_later'
        p = self._make_one(post_logout_url=logout_url)
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, logout_url)
    
    def test_logout_with_post_logout_page_and_SCRIPT_NAME(self):
        """
        Users must be redirected to the post-logout page, if defined, taking
        the SCRIPT_NAME into account.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        environ = self._make_environ('/logout_handler', SCRIPT_NAME='/my-app')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        self.assertEqual(app.location, '/my-app/see_you_later')
    
    def test_logout_with_post_logout_page_and_came_from(self):
        """
        Users must be redirected to the post-logout page, if defined, and also
        pass the came_from variable.
        
        """
        # --- Configuring the plugin:
        p = self._make_one(post_logout_url='/see_you_later')
        # --- Configuring the mock environ:
        came_from = '/the-path'
        environ = self._make_environ('/logout_handler')
        environ['came_from'] = came_from
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        redirect = '/see_you_later?came_from=%s'
        self.assertEqual(app.location, redirect % quote(came_from))
    
    def test_failed_login(self):
        """
        Users must be redirected to the login form if the tried to log in with
        the wrong credentials.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/somewhere')
        environ['repoze.who.logins'] = 1
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        came_from = 'http://example.org/somewhere'
        redirect = '/login?__logins=2&came_from=%s' % quote(came_from)
        self.assertEqual(app.location, redirect)
    
    def test_not_logout_and_not_failed_logins(self):
        """
        Do not modify the challenger unless it's handling a logout or a
        failed login.
        
        """
        # --- Configuring the plugin:
        p = self._make_one()
        # --- Configuring the mock environ:
        environ = self._make_environ('/somewhere')
        # --- Testing it:
        app = p.challenge(environ, '401 Unauthorized', [('app', '1')],
                          [('forget', '1')])
        came_from = 'http://example.org/somewhere'
        redirect = '/login?came_from=%s' % quote(came_from)
        self.assertEqual(app.location, redirect)

    def test_identify_pathinfo_miss(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/not_login_handler')
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        self.failIf(environ.get('repoze.who.application'))

    def test_identify_via_login_handler(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/login_handler',
                                        login='chris',
                                        password='password',
                                        came_from='http://example.com/')
        result = plugin.identify(environ)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 3)
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assert_("Location" in app.headers)
        self.assertEqual(app.headers['Location'],
                         'http://example.com/?__logins=0')
        self.assertEqual(app.code, 302)

    def test_identify_via_login_handler_no_username_pass(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/login_handler')
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        app = environ['repoze.who.application']
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assert_("Location" in app.headers)
        self.assertEqual(app.headers['Location'], '/?__logins=0')
        self.assertEqual(app.code, 302)

    def test_identify_with_ascii_encoding(self):
        plugin = self._makeOne()
        # Testing with ASCII arguments:
        environ_ascii = self._makeFormEnviron(
            path_info="/login_handler",
            login="gustavo",
            password="pass",
            charset="us-ascii",
            )
        result_ascii = plugin.identify(environ_ascii)
        self.assertEqual(result_ascii, {'login': "gustavo", 'password': "pass"})
        # Making sure the string sub-type is correct, to avoid getting
        # SQLAlchemy warnings:
        self.assertEqual(type(result_ascii['login']), str)
        self.assertEqual(type(result_ascii['password']), str)

    def test_identify_with_ascii_encoding_and_no_credentials(self):
        plugin = self._makeOne()
        # Testing with ASCII arguments:
        environ = self._makeFormEnviron(
            path_info="/login_handler",
            charset="us-ascii",
            )
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        app = environ['repoze.who.application']
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assert_("Location" in app.headers)
        self.assertEqual(app.headers['Location'], '/?__logins=0')
        self.assertEqual(app.code, 302)
        
    def test_identify_with_cp1252_encoding(self):
        plugin = self._makeOne()
        # Testing with ASCII arguments:
        environ_ascii = self._makeFormEnviron(
            path_info="/login_handler",
            login="gustavo",
            password="pass",
            charset="cp1252")
        result_ascii = plugin.identify(environ_ascii)
        self.assertEqual(result_ascii, {'login': "gustavo", 'password': "pass"})
        # Testing with Latin-1 arguments:
        environ_utf = self._makeFormEnviron(
            path_info="/login_handler",
            login=u"maría".encode('cp1252'),
            password=u"mañana".encode('cp1252'),
            charset="cp1252")
        result_utf = plugin.identify(environ_utf)
        self.assertEqual(result_utf, {'login': u"maría", 'password': u"mañana"})

    def test_identify_with_unicode_encoding(self):
        plugin = self._makeOne()
        # Testing with ASCII arguments:
        environ_ascii = self._makeFormEnviron(
            path_info="/login_handler",
            login="gustavo",
            password="pass",
            charset="utf-8")
        result_ascii = plugin.identify(environ_ascii)
        self.assertEqual(result_ascii,
                         {'login': u"gustavo", 'password': u"pass"})
        # Testing with UTF-8 arguments:
        environ_utf = self._makeFormEnviron(
            path_info="/login_handler",
            login="maría",
            password="mañana",
            charset="utf-8")
        result_utf = plugin.identify(environ_utf)
        self.assertEqual(result_utf, {'login': u"maría", 'password': u"mañana"})
        # Making sure the string sub-type is correct, to avoid getting
        # SQLAlchemy wanrings:
        self.assertEqual(type(result_utf['login']), unicode)
        self.assertEqual(type(result_utf['password']), unicode)

    def test_identify_with_default_encoding(self):
        """ISO-8859-1 must be assumed when no encoding is specified."""
        plugin = self._makeOne()
        # Testing with ASCII arguments:
        environ_ascii = self._makeFormEnviron(
            path_info="/login_handler",
            login="gustavo",
            password="pass")
        result_ascii = plugin.identify(environ_ascii)
        self.assertEqual(result_ascii,
                         {'login': u"gustavo", 'password': u"pass"})
        # Testing with default (Latin-1) encoded arguments:
        environ_utf = self._makeFormEnviron(
            path_info="/login_handler",
            login=u"maría".encode('latin-1'),
            password=u"mañana".encode('latin-1'))
        result_utf = plugin.identify(environ_utf)
        self.assertEqual(result_utf, {'login': u"maría", 'password': u"mañana"})

    def test_identify_with_custom_default_encoding(self):
        """The default encoding can be overridden."""
        plugin = self._makeOne(charset="utf-8")
        # Testing with UTF-8 arguments:
        environ_utf = self._makeFormEnviron(
            path_info="/login_handler",
            login=u"我不会说中文".encode("utf-8"),
            password=u"你白痴".encode("utf-8"))
        result_utf = plugin.identify(environ_utf)
        self.assertEqual(result_utf, {'login': u"我不会说中文", 'password': u"你白痴"})

    def test_identify_via_login_handler_no_came_from_no_http_referer(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/login_handler',
                                        login='chris',
                                        password='password')
        result = plugin.identify(environ)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assert_("Location" in app.headers)
        self.assertEqual(app.headers['Location'], '/?__logins=0')
        self.assertEqual(app.code, 302)

    def test_identify_via_login_handler_no_came_from(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/login_handler',
                                        login='chris',
                                        password='password')
        environ['HTTP_REFERER'] = 'http://foo.bar/'
        result = plugin.identify(environ)
        self.assertEqual(result, {'login':'chris', 'password':'password'})
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 3)
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assert_("Location" in app.headers)
        self.assertEqual(app.headers['Location'], 'http://foo.bar/?__logins=0')
        self.assertEqual(app.code, 302)

    def test_identify_via_login_handler_no_came_from_no_referer_sname(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/login_handler',
                                        script_name='/my-app',
                                        login='chris',
                                        password='password')
        plugin.identify(environ)
        app = environ['repoze.who.application']
        self.assertEqual(app.location, '/my-app?__logins=0')

    def test_identify_via_logout_handler(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/logout_handler',
                                        login='chris',
                                        password='password',
                                        came_from='http://example.com')
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 2)
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assertEqual(app.code, 401)
        self.assertEqual(environ['came_from'], 'http://example.com')

    def test_identify_via_logout_handler_no_came_from_no_http_referer(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/logout_handler',
                                        login='chris',
                                        password='password')
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 2)
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assertEqual(app.code, 401)
        self.assertEqual(environ['came_from'], '/')

    def test_identify_via_logout_handler_no_came_from_no_referer_spath(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/logout_handler',
                                        script_name='/my-app',
                                        login='chris',
                                        password='password')
        plugin.identify(environ)
        environ['repoze.who.application']
        self.assertEqual(environ['came_from'], '/my-app')

    def test_identify_via_logout_handler_no_came_from(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron(path_info='/logout_handler',
                                        login='chris',
                                        password='password')
        environ['HTTP_REFERER'] = 'http://example.com/referer'
        result = plugin.identify(environ)
        self.assertEqual(result, None)
        app = environ['repoze.who.application']
        self.assertEqual(len(app.headers), 2)
        self.assert_("Content-Type" in app.headers)
        self.assert_("Content-Length" in app.headers)
        self.assertEqual(app.code, 401)
        self.assertEqual(environ['came_from'], 'http://example.com/referer')

    def test_remember(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron()
        identity = {}
        result = plugin.remember(environ, identity)
        self.assertEqual(result, None)
        self.assertEqual(environ['repoze.who.plugins']['cookie'].remembered,
                         identity)

    def test_forget(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron()
        identity = {}
        result = plugin.forget(environ, identity)
        self.assertEqual(result, None)
        self.assertEqual(environ['repoze.who.plugins']['cookie'].forgotten,
                         identity
                         )

    def test_challenge(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron()
        app = plugin.challenge(environ, '401 Unauthorized', [('app', '1')],
                               [('forget', '1')])
        sr = DummyStartResponse()
        result = ''.join(app(environ, sr))
        self.failUnless(result.startswith('302 Found'))
        self.assertEqual(len(sr.headers), 4)
        self.assertEqual(sr.headers[1][0], 'forget')
        self.assertEqual(sr.headers[2][0], 'Location')
        url = sr.headers[2][1]
        import urlparse
        import cgi
        parts = urlparse.urlparse(url)
        parts_qsl = cgi.parse_qsl(parts[4])
        self.assertEqual(len(parts_qsl), 1)
        came_from_key, came_from_value = parts_qsl[0]
        self.assertEqual(parts[0], 'http')
        self.assertEqual(parts[1], 'example.com')
        self.assertEqual(parts[2], '/login.html')
        self.assertEqual(parts[3], '')
        self.assertEqual(came_from_key, 'came_from')
        self.assertEqual(came_from_value, 'http://www.example.com/?default=1')
        headers = sr.headers
        self.assertEqual(len(headers), 4)
        self.assertEqual(sr.headers[0][0], 'Content-Type')
        self.assertEqual(sr.headers[0][1], 'text/html; charset=UTF-8')
        self.assertEqual(sr.headers[1][0], 'forget')
        self.assertEqual(sr.headers[1][1], '1')
        self.assertEqual(sr.status, '302 Found')

    def test_challenge_came_from_in_environ(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron()
        environ['came_from'] = 'http://example.com/came_from'
        app = plugin.challenge(environ, '401 Unauthorized', [('app', '1')],
                               [('forget', '1')])
        sr = DummyStartResponse()
        result = ''.join(app(environ, sr))
        self.failUnless(result.startswith('302 Found'))
        self.assertEqual(len(sr.headers), 4)
        self.assertEqual(sr.headers[1][0], 'forget')
        self.assertEqual(sr.headers[2][0], 'Location')
        url = sr.headers[2][1]
        import urlparse
        import cgi
        parts = urlparse.urlparse(url)
        parts_qsl = cgi.parse_qsl(parts[4])
        self.assertEqual(len(parts_qsl), 1)
        came_from_key, came_from_value = parts_qsl[0]
        self.assertEqual(parts[0], 'http')
        self.assertEqual(parts[1], 'example.com')
        self.assertEqual(parts[2], '/login.html')
        self.assertEqual(parts[3], '')
        self.assertEqual(came_from_key, 'came_from')
        self.assertEqual(came_from_value, 'http://example.com/came_from')

    def test_challenge_with_setcookie_from_app(self):
        plugin = self._makeOne()
        environ = self._makeFormEnviron()
        app = plugin.challenge(
            environ,
            '401 Unauthorized',
            [('app', '1'), ('set-cookie','a'), ('set-cookie','b')],
            [])
        sr = DummyStartResponse()
        result = ''.join(app(environ, sr))
        self.failUnless(result.startswith('302 Found'))
        self.assertEqual(sr.headers[0][0], 'Content-Type')
        self.assertEqual(sr.headers[0][1], 'text/html; charset=UTF-8')
        self.assertEqual(sr.headers[1][0], 'set-cookie')
        self.assertEqual(sr.headers[1][1], 'a')
        self.assertEqual(sr.headers[2][0], 'set-cookie')
        self.assertEqual(sr.headers[2][1], 'b')
        self.assertEqual(sr.headers[3][0], 'Location')
        self.assertEqual(sr.headers[3][1],
            "http://example.com/login.html?came_from=http%3A%2F%2Fwww.example."
            "com%2F%3Fdefault%3D1")

    def test_challenge_with_non_root_script_name(self):
        """The script name must be taken into account while redirecting."""
        plugin = self._makeOne(login_form_url='/login')
        environ = self._makeFormEnviron(script_name='/app',
                                        path_info='/admin')
        came_from = 'http://www.example.com/app/admin?default=1'
        environ['came_from'] = came_from
        app = plugin.challenge(environ, '401 Unauthorized', [('app', '1')],
                               [('forget', '1')])

        login_url = '/app/login?came_from=%s' % quote(came_from)
        self.assertEqual(app.location, login_url)
    
    def _make_one(self, login_counter_name='__logins', post_login_url=None,
                  post_logout_url=None):
        p = FriendlyFormPlugin('/login', '/login_handler', post_login_url,
                               '/logout_handler', post_logout_url,
                               'whatever',
                               login_counter_name=login_counter_name)
        return p

    def _makeOne(self, login_form_url='http://example.com/login.html',
                 login_handler_path = '/login_handler',
                 logout_handler_path = '/logout_handler',
                 rememberer_name='cookie', charset="iso-8859-1"):
        # TODO: Merge this into _make_one()
        plugin = FriendlyFormPlugin(login_form_url, login_handler_path, None,
                                    logout_handler_path, None, rememberer_name,
                                    charset=charset)
        return plugin
    
    def _make_redirection(self, url):
        # TODO: Remove this method
        app = HTTPFound(url)
        return app
    
    def _make_environ(self, path_info, qs='', SCRIPT_NAME='', redirect=None,
                      charset=None):
        environ = {
            'PATH_INFO': path_info,
            'SCRIPT_NAME': SCRIPT_NAME,
            'QUERY_STRING': qs,
            'SERVER_NAME': 'example.org',
            'SERVER_PORT': '80',
            'wsgi.input': '',
            'wsgi.url_scheme': 'http',
            'CONTENT_TYPE': "application/x-www-form-urlencoded",
            }
        # TODO: Remove the ``redirect`` param
        if redirect:
            environ['repoze.who.application'] = self._make_redirection(redirect)
        return environ
    
    def _makeEnviron(self, kw=None):
        # TODO: Merge this into _make_environ
        environ = {}
        environ['wsgi.version'] = (1,0)
        if kw is not None:
            environ.update(kw)
        return environ

    def _makeFormEnviron(self, login=None, password=None, came_from=None,
                         path_info='/', identifier=None, script_name='',
                         charset=None):
        # TODO: Merge this into _make_environ
        fields = []
        if login:
            fields.append(('login', login))
        if password:
            fields.append(('password', password))
        if came_from:
            fields.append(('came_from', came_from))
        if identifier is None:
            credentials = {'login':'chris', 'password':'password'}
            identifier = DummyIdentifier(credentials)
        content_type, body = urlencode_formdata(fields, charset)
        extra = {'wsgi.input': StringIO(body),
                 'wsgi.url_scheme': 'http',
                 'SERVER_NAME': 'www.example.com',
                 'SERVER_PORT': '80',
                 'CONTENT_TYPE': content_type,
                 'CONTENT_LENGTH': len(body),
                 'REQUEST_METHOD': 'POST',
                 'repoze.who.plugins': {'cookie':identifier},
                 'QUERY_STRING': 'default=1',
                 'PATH_INFO': path_info,
                 'SCRIPT_NAME': script_name
                 }
        environ = self._makeEnviron(extra)
        return environ


#{ Utilities


def urlencode_formdata(fields, charset=None):
    variables = []
    for (key, value) in fields:
        variables.append("%s=%s" % (quote(key), quote(value)))
    body = "&".join(variables)
    
    content_type = "application/x-www-form-urlencoded"
    if charset:
        content_type += "; charset=%s" % charset
    
    return content_type, body


#{ Mock objects


class DummyStartResponse:
    def __call__(self, status, headers, exc_info=None):
        self.status = status
        self.headers = headers
        self.exc_info = exc_info
        return []


class DummyIdentifier:
    forgotten = False
    remembered = False

    def __init__(self, credentials=None, remember_headers=None,
                 forget_headers=None, replace_app=None):
        self.credentials = credentials
        self.remember_headers = remember_headers
        self.forget_headers = forget_headers
        self.replace_app = replace_app

    def identify(self, environ):
        if self.replace_app:
            environ['repoze.who.application'] = self.replace_app
        return self.credentials

    def forget(self, environ, identity):
        self.forgotten = identity
        return self.forget_headers

    def remember(self, environ, identity):
        self.remembered = identity
        return self.remember_headers

#}
