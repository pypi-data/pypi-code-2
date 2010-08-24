import unittest

from mr.monster.drop import DropFactory
from test_url import PathAssertionEndpoint, response

class test_set_scriptname_middleware(unittest.TestCase):
    """Tests to prove the middleware that drops elements from the path works"""
    
    def test_passthrough_with_no_options(self):
        factory = DropFactory({})
        r = response()
        app = factory(PathAssertionEndpoint("/", SCRIPT_NAME=""))
        app({"PATH_INFO":"/",
             "SCRIPT_NAME":"",
             "REQUEST_METHOD":"GET",}, r.start_response)
        self.assertEqual(r.status, "200 OK")  
        
    def test_change_to_simple_path(self):
        factory = DropFactory({}, SCRIPT_NAME="/plone")
        r = response()
        app = factory(PathAssertionEndpoint("/", SCRIPT_NAME="/plone"))
        app({"PATH_INFO":"/",
             "SCRIPT_NAME":"",
             "REQUEST_METHOD":"GET",}, r.start_response)
        self.assertEqual(r.status, "200 OK")

    def test_no_doubling_of_slashes(self):
        factory = DropFactory({}, SCRIPT_NAME="/")
        r = response()
        app = factory(PathAssertionEndpoint("/", SCRIPT_NAME=""))
        app({"PATH_INFO":"/",
             "SCRIPT_NAME":"/plone",
             "REQUEST_METHOD":"GET",}, r.start_response)
        self.assertEqual(r.status, "200 OK")