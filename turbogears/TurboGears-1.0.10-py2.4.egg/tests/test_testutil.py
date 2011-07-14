import unittest

import cherrypy
from turbogears import controllers, expose, redirect, testutil

class MyRoot(controllers.RootController):
    def set_name(self, name):
        cookies = cherrypy.response.simple_cookie
        cookies['name'] = name
        return "Hello " + name
    set_name = expose()(set_name)

    def get_name(self):
        cookies = cherrypy.request.simple_cookie
        if 'name' in cookies:
            return cookies['name'].value
        else:
            return "cookie not found"
    get_name = expose()(get_name)

    def get_unicode_name(self):
        """Return a nonsense string of non-ascii characters"""
        cherrypy.response.headers['Content-Type'] = 'text/plain; encoding=utf-8'
        return u'\u1234\u9876\u3456'.encode('utf-8')
    get_unicode_name = expose()(get_unicode_name)

    def redirect(self):
        raise redirect("foo")
    redirect = expose()(redirect)

class TestControllers(unittest.TestCase):
    def setUp(self):
        cherrypy.root = None
        cherrypy.tree.mount_points = {}
        cherrypy.tree.mount(MyRoot(), "/")
        self.root = cherrypy.root

    def tearDown(self):
        cherrypy.root = None
        cherrypy.tree.mount_points = {}

    def test_browser_session(self):
        bs = testutil.BrowsingSession()
        bs.goto('/get_name')
        assert bs.response == 'cookie not found'
        bs.goto('/set_name?name=me')
        bs.goto('/get_name')
        assert bs.response == 'me'

    def test_browser_session_for_two_users(self):
        bs1 = testutil.BrowsingSession()
        bs2 = testutil.BrowsingSession()
        bs1.goto('/set_name?name=bs1')
        bs2.goto('/set_name?name=bs2')
        bs1.goto('/get_name')
        assert bs1.response == 'bs1'
        bs2.goto('/get_name')
        assert bs2.response == 'bs2'

    def test_unicode_response(self):
        bs = testutil.BrowsingSession()
        bs.goto('/get_unicode_name')
        assert bs.response == u'\u1234\u9876\u3456'.encode('utf-8')
        assert bs.unicode_response == u'\u1234\u9876\u3456'
        assert type(bs.unicode_response) == unicode

    def test_index(self):
        "Test that call_with_request is usable if controller uses redirect"
        try:
            testutil.call(self.root.redirect)
            self.fail("no redirect exception raised")
        except cherrypy.HTTPRedirect, e:
            assert e.status in [302, 303]
            self.assertEquals(1, len(e.urls))
            assert e.urls[0].endswith("foo")
