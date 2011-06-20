import unittest

from collective.fourohfour.middleware import make_handler
from paste.recursive import ForwardRequestException

def noopStartResponse(status, headers):
    pass

class TestAppRedirect:
    def __init__(self, _called_environ):
        self._called_environ = _called_environ

    def __call__(self, environ, start_response):
        if not environ.get('PATH_INFO', '').endswith('@@404-error'):
            start_response("404 Not Found", None)
            
        return self.__class__.__name__


class TestMiddleware(unittest.TestCase):
    
    def test_original_path_is_set_correctly_with_repoze_vhm(self):
        app = TestAppRedirect({})
        filter = make_handler(app, {}, **{'404': '/@@404-error'})
        
        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '80',
                   'repoze.vhm.virtual_root' : '/vhmplone',
                   'PATH_INFO': '/vhmplone/foobar/',
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(environ.get('collective.fourohfour.original_path'), '/vhmplone/foobar/')
        self.assertEqual(environ.get('collective.fourohfour.original_path_qs'), '/vhmplone/foobar/')

        
    def test_original_path_is_set_correctly_without_repoze_vhm(self):
        app = TestAppRedirect({})
        filter = make_handler(app, {}, **{'404': '/@@404-error'})

        environ = {'wsgi.url_scheme': 'http',
                   'SERVER_NAME': 'example.com',
                   'SERVER_PORT': '80',
                   'PATH_INFO': '/plone/foobar/',
                  }

        filter(environ, noopStartResponse)

        self.assertEqual(environ.get('collective.fourohfour.original_path'), '/plone/foobar/')
        self.assertEqual(environ.get('collective.fourohfour.original_path_qs'), '/plone/foobar/')
        
    

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)