import datetime
import unittest
import twisted.internet.defer
import huck.utils
import huck.web
import assets

class Connection(object):

    def __init__(self, *args, **kwargs):
        self.xheaders = False

    def finish(self):
        pass

    def notifyFinish(self):
        d = twisted.internet.defer.Deferred()
        d.callback(None)
        return d

    def write(self, data):
        pass

class RequestHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.application = huck.utils.objectify({
            'ui_methods': {},
            'ui_modules': {},
            'settings': huck.utils.objectify({
                'cookie_secret': 'secret',
            }),
        })
        self.request = huck.http.Request(
            'GET',
            'http://localhost:8000/test',
            connection=Connection(),
        )
        self.setup_handler()

    def setup_handler(self, handler_type=huck.web.RequestHandler, just_return=False):
        handler = handler_type(self.application, self.request)
        if not just_return:
            self.handler = handler
        return handler

    def test_settings(self):
        self.assertEqual(self.handler.settings.cookie_secret, 'secret')

    def test_request_types(self):
        self.assertRaises(huck.web.HTTPError, self.handler.head)
        self.assertRaises(huck.web.HTTPError, self.handler.get)
        self.assertRaises(huck.web.HTTPError, self.handler.post)
        self.assertRaises(huck.web.HTTPError, self.handler.delete)
        self.assertRaises(huck.web.HTTPError, self.handler.put)

    def test_prepare(self):
        class RequestHandler(huck.web.RequestHandler):
            test_ok = False
            def prepare(self):
                self.test_ok = True
        self.setup_handler(RequestHandler)
        self.handler._execute([])
        self.assertTrue(self.handler.test_ok)

    def test_on_connection_close(self):
        class RequestHandler(huck.web.RequestHandler):
            test_ok = False
            def on_connection_close(self, *args, **kwargs):
                self.test_ok = True
        self.setup_handler(RequestHandler)
        self.handler._execute([])
        self.assertTrue(self.handler.test_ok)

    def test_clear(self):
        self.handler._headers = {}
        self.handler._write_buffer = ['hello world']
        self.handler._status_code = 500
        self.handler.clear()
        self.assertEqual(len(self.handler._headers), 2)
        self.assertTrue('Content-Type' in self.handler._headers)
        self.assertTrue('Server' in self.handler._headers)
        self.assertEqual(len(self.handler._write_buffer), 0)
        self.assertEqual(self.handler._status_code, 200)

    def test_set_status(self):
        self.assertEqual(self.handler._status_code, 200)
        self.handler.set_status(500)
        self.assertEqual(self.handler._status_code, 500)
        self.assertRaises(Exception, self.handler.set_status, 20)
        self.assertEqual(self.handler._status_code, 500)

    def test_set_header(self):
        self.handler.set_header('datetime', datetime.datetime(2010, 10, 10, 10, 10, 10))
        self.assertEqual(self.handler._headers['datetime'], 'Sun, 10 Oct 2010 10:10:10 GMT')
        self.handler.set_header('int', int(10))
        self.assertEqual(self.handler._headers['int'], '10')
        self.handler.set_header('float', float(10.5))
        self.assertEqual(self.handler._headers['float'], '10.5')
        self.handler.set_header('long', long(11))
        self.assertEqual(self.handler._headers['long'], '11')
        self.assertRaises(TypeError, self.handler.set_header, 'failure', object())

    def test_cookie(self):
        self.assertFalse(hasattr(self.handler, '_cookies'))
        self.handler.cookies['hello'] = 'world'
        self.assertTrue(hasattr(self.handler, '_cookies'))
        self.assertTrue('hello' in self.handler.cookies)

    def test_get_cookie(self):
        self.handler.cookies['hello'] = 'world'
        self.assertEqual(self.handler.get_cookie('hello'), 'world')

    def test_set_cookie(self):
        dt = datetime.datetime(2010, 10, 10, 10, 10, 10)
        self.handler.set_cookie('hello', 'world', 'example.org', dt, '/test')
        cookie = self.handler._new_cookies[0]['hello']
        self.assertEqual(cookie.value, 'world')
        self.assertEqual(cookie['domain'], 'example.org')
        self.assertEqual(cookie['path'], '/test')
        self.assertEqual(cookie['expires'], 'Sun, 10 Oct 2010 10:10:10 GMT')

    def test_clear_cookie(self):
        self.handler.clear_cookie('hello')
        cookie = self.handler._new_cookies[0]['hello']
        self.assertEqual(cookie.value, '')

    def test_clear_all_cookie(self):
        self.handler.cookies['hello1'] = 'world1'
        self.handler.cookies['hello2'] = 'world2'
        self.handler.clear_all_cookies()
        self.assertEqual(len(self.handler._new_cookies), 2)

    def test_set_secure_cookie(self):
        self.handler.set_secure_cookie('hello', 'world')
        cookie = self.handler._new_cookies[0]['hello']
        self.assertEqual(len(cookie.value), 60)
        # value|timestamp|signature
        self.assertEqual(cookie.value.count('|'), 2)

    def test_get_secure_cookie(self):
        self.handler.set_secure_cookie('hello', 'world')
        value = self.handler._new_cookies[0]['hello'].value
        self.setup_handler()
        self.handler.cookies['hello'] = value
        self.assertEqual(self.handler.get_secure_cookie('hello'), 'world')

    def test_cookie_signature(self):
        self.assertEqual(
            self.handler._cookie_signature('hello', 'world'),
            'e92eb69939a8b8c9843a75296714af611c73fb53',
        )
