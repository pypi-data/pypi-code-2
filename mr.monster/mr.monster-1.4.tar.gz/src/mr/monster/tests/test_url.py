import unittest
import logging

from mr.monster.rewrite import RewriteFactory

def PathAssertionEndpoint(PATH_INFO, SCRIPT_NAME=None):
    def _(environ, start_response):
        val = True
        if SCRIPT_NAME is not None:
            val = val and environ['SCRIPT_NAME'] == SCRIPT_NAME
        val = val and environ['PATH_INFO'] == PATH_INFO
        
        if not val:
            logging.error("Expected SCRIPT_NAME %s - got %s" % (SCRIPT_NAME, environ.get('SCRIPT_NAME')))
            logging.error("Expected PATH_INFO %s - got %s" % (PATH_INFO, environ.get('PATH_INFO')))
        
        
        if val:
            start_response("200 OK", [])
        else:
            start_response("404 Not Found", [])
        return []
    return _

class response(object):
    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

class test_urls(unittest.TestCase):
    
    def test_autodetect_if_no_options(self):
        factory = RewriteFactory({})
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/127.0.0.1:8080/VirtualHostRoot/"))
        app({"SERVER_NAME":"127.0.0.1",
             "SERVER_PORT":"8080",
             "REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")
        
    def test_fail_if_host_provided_but_not_port(self):
        self.assertRaises(AttributeError, RewriteFactory, object(), host="www.example.com")

    def test_vhm_on_host_and_port(self):
        factory = RewriteFactory({}, host="www.example.com", port="80")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")

    def test_fail_if_port_provided_but_not_host(self):
        self.assertRaises(AttributeError, RewriteFactory, object(), port="80")
    
    def test_vhm_host_autodetect(self):
        factory = RewriteFactory({}, autodetect="true")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/127.0.0.1:8080/VirtualHostRoot/"))
        app({"SERVER_NAME":"127.0.0.1",
             "SERVER_PORT":"8080",
             "REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")

    def test_vhm_host_autodetect_http1_1_no_port(self):
        factory = RewriteFactory({}, autodetect="true")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/"))
        app({"HTTP_HOST":"www.example.com",
             "SERVER_NAME":"127.0.0.1",
             "SERVER_PORT":"8080",
             "REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")

    def test_vhm_host_autodetect_http1_1_explicit_port(self):
        factory = RewriteFactory({}, autodetect="true")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:8080/VirtualHostRoot/"))
        app({"HTTP_HOST":"www.example.com:8080",
             "SERVER_NAME":"127.0.0.1",
             "SERVER_PORT":"8080",
             "REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")


    def test_double_slash(self):
        factory = RewriteFactory({}, host="www.example.com", port="80", internalpath="/foo",externalpath="/supersite/")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/_vh_supersite"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/supersite"}, r.start_response)
        assert r.status.startswith("200")


    def test_root_exception(self):
        factory = RewriteFactory({}, host="www.example.com", port="80", internalpath="/foo",externalpath="/")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")

    def test_folder_on_zope_side(self):
        factory = RewriteFactory({}, host="www.example.com", port="80", internalpath="/foo")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/foo/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/"}, r.start_response)
        assert r.status.startswith("200")

    def test_folder_on_client_side(self):
        factory = RewriteFactory({}, host="www.example.com", port="80", externalpath="/bar")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/_vh_bar"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/bar"}, r.start_response)
        assert r.status.startswith("200")

    def test_accessing_resource(self):
        factory = RewriteFactory({}, host="www.example.com", port="80")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/my/thing/is/cool"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/my/thing/is/cool"}, r.start_response)
        assert r.status.startswith("200")

    def test_accessing_script(self):
        factory = RewriteFactory({}, host="www.example.com", port="80")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/isay/my/thing/is/cool"))
        app({"REQUEST_METHOD":"GET",
             "SCRIPT_NAME":"/isay",
             "PATH_INFO":"/my/thing/is/cool"}, r.start_response)
        assert r.status.startswith("200")

    def test_internalpath_at_root(self):
        factory = RewriteFactory({},host="www.example.com",port="80",internalpath="/",externalpath="/")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/",},r.start_response)
        assert r.status.startswith("200")
    
    def test_internalpath_trailing_slash(self):
        factory = RewriteFactory({},host="www.example.com",port="80",internalpath="/bees/",externalpath="/")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/http/www.example.com:80/bees/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/",},r.start_response)
        assert r.status.startswith("200")

    def test_scheme_support(self):
        factory = RewriteFactory({},host="www.example.com",port="80",scheme="https",internalpath="/",externalpath="/")
        r = response()
        app = factory(PathAssertionEndpoint("/VirtualHostBase/https/www.example.com:80/VirtualHostRoot/"))
        app({"REQUEST_METHOD":"GET",
             "PATH_INFO":"/",},r.start_response)
        assert r.status.startswith("200")