import unittest
from pyramid.configuration import Configurator
from pyramid import testing

class TestNotFoundView(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def test_redirect(self):
        from jocommentatom.views import notfound_view
        request = testing.DummyRequest()
        response = notfound_view(request)
        self.assertEqual(response.status, '301 Moved Permanently')
        self.failUnless(('Location', '/') in response.headerlist)
