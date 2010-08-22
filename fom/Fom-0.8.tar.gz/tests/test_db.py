import unittest

from fom.db import FluidDB, _get_body_and_type, fom_request_sent, \
    fom_response_received
from fom.errors import Fluid404Error


class TestDB(unittest.TestCase):

    def test_get_body_and_type(self):
        """
        Lets make sure we're sending the right sort of thing down the wire to
        FluidDB
        """
        # good
        # with mime-type
        content, content_type = _get_body_and_type('foo', 'text/plain')
        self.assertEquals('foo', content)
        self.assertEquals('text/plain', content_type)
        # dict -> json
        content, content_type = _get_body_and_type({'foo': 'bar'}, None)
        # returns a string representation of json
        self.assertTrue(isinstance(content, basestring))
        self.assertEquals('application/json', content_type)
        # primitive types
        values = [ 1, 1.2, 'string', u'string', ['foo', 'bar'],
                  (u'foo', u'bar'), True, False, None]
        for val in values:
            content, content_type = _get_body_and_type(val, None)
            # returns a string representation (of json)
            self.assertTrue(isinstance(content, basestring))
            self.assertEqual('application/vnd.fluiddb.value+json',
                             content_type)
        # json
        body = [{'foo': 'bar'}, 1, "two"]
        content, content_type = _get_body_and_type(body, 'application/json')
        self.assertTrue(isinstance(content, basestring))
        self.assertEquals('application/json', content_type)
        # bad
        # can't handle the type without a mime
        self.assertRaises(ValueError, _get_body_and_type, FluidDB(), None)
        # list or tuple contains something other than a string
        self.assertRaises(ValueError, _get_body_and_type, [1, 2, 3], None)

        # ToDo: test NO_CONTENT as argument

    def test_default(self):
        db = FluidDB('http://sandbox.fluidinfo.com')
        self.assertEquals(db.base_url, 'http://sandbox.fluidinfo.com')

    def test_call(self):
        db = FluidDB('http://sandbox.fluidinfo.com')
        r = db('GET', '/users/aliafshar')
        self.assertEquals(r.value['name'], u'aliafshar')

    def test_call_nasty(self):
        """
        Ensures that a path is properly "quoted" so, for example, a space
        maps to %20
        """
        db = FluidDB('http://sandbox.fluidinfo.com')
        self.assertRaises(Fluid404Error, db, 'GET', '/users/a name')

    def test_call_unicode(self):
        """
        Ensures that the path and urlargs are properly "quoted" if unicode is
        passed in.
        """
        # path
        db = FluidDB('http://sandbox.fluidinfo.com')
        self.assertRaises(Fluid404Error, db, 'GET', u'/users/nto\u03bb\u03bb')
        # urlargs
        #unicode
        self.assertRaises(Fluid404Error, db, 'GET', u'/objects',
            urlargs={u'query': u'fluidinfo/about="nto\u03bb\u03bb"'})
        # already encoded
        self.assertRaises(Fluid404Error, db, 'GET',
                            u'/users/nto\u03bb\u03bb'.encode('utf-8'))
        self.assertRaises(Fluid404Error, db, 'GET', u'/objects',
            urlargs={
                u'query': u'fluidinfo/about="nto\u03bb\u03bb"'.encode('utf-8')
                }
            )

    def test_trailing_slash_handling(self):
        """
        Make sure we get a complaint if the base URL for the instance
        of fluiddb ends with a slash.

        BAD: http://fluiddb.fluidinfo.com/
        GOOD: http://fluiddb.fluidinfo.com

        Why not knock off the trailing slash..? Well, it's easy to complain
        but hard to second guess the caller's intention
        """
        # Bad
        self.assertRaises(ValueError, FluidDB,
                          'http://sandbox.fluidinfo.com/')
        # Good
        self.assertTrue(FluidDB('http://sandbox.fluidinfo.com'))

if __name__ == '__main__':
    unittest.main()
