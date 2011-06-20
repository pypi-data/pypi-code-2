import os
from StringIO import StringIO

import twill
from twill import commands as web

os.environ['DJANGO_SETTINGS_MODULE'] = 'kforge.django.settings.main'

# import django.conf.settings

import unittest

import django.core.handlers.wsgi

import kforge
app = kforge.getA()

class TestBase(unittest.TestCase):

    registry = app.registry
    siteurl = 'http://local.kforge.net:8080/'

    def setUp(self):
        wsgi_app = django.core.handlers.wsgi.WSGIHandler()
        # need local.kforge.net rather than localhost for cookies to work
        twill.add_wsgi_intercept('local.kforge.net', 8080, lambda : wsgi_app)
        # while we're at it, stop twill from running off at the mouth...
        self.outp = StringIO()
        twill.set_output(self.outp)

        self.test_project = 'testproject'

    def tearDown(self):
        # remove intercept.
        twill.remove_wsgi_intercept('localhost', 8080)

    def _login(self, username, password):
        web.find('KForge - Log in') # page title
        formname = 2 # use index as name ('') does not seem to work
        web.fv(formname, 'name', username)
        web.fv(formname, 'password', password)
        web.submit()
        web.code(200)
        web.notfind('Sorry, wrong user name or password.')
        web.find('Logged in')
        web.find('You are now logged in as')
    
    def _logout(self):
        url = self.siteurl + 'logout/'
        web.go(url)
        web.code(200)
        web.find('You&rsquo;ve successfully logged out of KForge.')
     
class TestSiteSimple(TestBase):

    def test_homepage(self):
        url = self.siteurl
        web.go(url)
        web.code(200)

    def test_login(self):
        url = self.siteurl + 'login/'
        web.go(url)
        web.code(200)
        self._login('levin', 'levin')
        self._logout()

class TestLostPassword(TestBase):

    username = 'levin'
    oldpassword = 'levin'
    person = TestBase.registry.persons[username]

    def tearDown(self):
        "Need tearDown to reset password."
        unittest.TestCase.tearDown(self)
        self.person.setPassword(self.oldpassword)
        self.person.save()

    def test_lost_password(self):
        # TODO: stub mail sending class
        # local machine does not support sending email ...
        return
        url = self.siteurl + 'login/'
        web.go(url)
        web.code(200)
        web.find('KForge - Log in') # page title
        formname = 2 # use index as name ('') does not seem to work
        web.fv(formname, 'name', self.username)
        web.fv(formname, 'forgotpassword', True)
        web.submit()
        web.code(200)
        web.find('A new password has been emailed to you.')
        self.failIf(self.person.isPassword(self.oldpassword))

class TestRegisterUser(TestBase):

    test_username = 'test'

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        test_person = self.registry.persons[self.test_username]
        test_person.delete()
        test_person.purge()

    def test_register(self):
        url =  self.siteurl
        web.go(url)
        web.code(200)
        web.follow('Register')
        web.code(200)
        username = 'test'
        self._register(username)
        web.code(200)
        web.notfind('Sorry, the following problems prevented your registration from being completed.')
        self._login(username, 'pass')

    def _register(self, username):
        formname = 'login_form'
        web.fv(formname, 'name', username)
        web.fv(formname, 'password', 'pass')
        web.fv(formname, 'passwordconfirmation', 'pass')
        web.fv(formname, 'fullname', username)
        web.fv(formname, 'email', 'blah@blah.org')
        web.fv(formname, 'emailconfirmation', 'blah@blah.org')
        web.submit()

def suite():
    suites = [
        unittest.makeSuite(TestSiteSimple),
        unittest.makeSuite(TestRegisterUser),
    ]
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    # use the suites cause all kinds of weird errors
    # unittest.TextTestRunner().run(suite())
    unittest.main()
