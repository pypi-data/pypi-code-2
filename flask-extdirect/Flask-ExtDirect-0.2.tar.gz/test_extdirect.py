import unittest
import flask

from flaskext.extdirect import ExtDirect


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        extdirect = ExtDirect(app)

        @app.route('/direct/api')
        def api():
            return extdirect.api()

        self.app = app
        self.extdirect = extdirect

    def tearDown(self):
        pass

    def test_no_method(self):
        c = self.app.test_client()
        rv = c.get('/direct/api')
        assert '"actions": {}' in rv.data

    def test_one_method(self):
        c = self.app.test_client()
        
        @self.extdirect.register
        class Testing(object):
            def test(self):
                pass
        
        rv = c.get('/direct/api')
        assert len(self.extdirect.registry) == 1
        assert 'Testing' in rv.data

if __name__ == '__main__':
    unittest.main()
