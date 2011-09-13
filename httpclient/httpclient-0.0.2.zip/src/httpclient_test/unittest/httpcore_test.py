"""
Created on Aug 18, 2011
@author: Guillaume Humbert
"""

import unittest
import gzip
import urllib.request
import urllib.parse
from urllib.error import URLError

from mockito import when, unstub, mock, any, verify

from httpclient.httpcore import HttpResponse, HttpCoreFactory, HttpCore
from httpclient.httpcore import HttpCoreException, AbstractHttpCore
    
class HttpResponseTest(unittest.TestCase):
    """
    Tests of the HttpResponse class.
    @author: Guillaume Humbert
    """

    def setUp(self):
        """Test fixtures."""

        self._http_response = HttpResponse()
        when(gzip.GzipFile).read().thenReturn(
                "ungzipped content".encode("utf-8"))

    def tearDown(self):
        """Unregisters all stubs."""
        unstub()

    def test_get_content_as_string(self):
        """Test of the 'get_content_as_string' method."""
   
        # The content of the response is gzipped, it must be ungzipped.
        self._http_response.headers = "Content-Encoding: gzip"
        self._http_response.content = "Content é".encode("utf-8")
        
        # We verify that the result is ungzipped.
        self.assertEqual("ungzipped content",
                         self._http_response.get_content_as_string())
        
        # The content of the response is not gzipped.
        self._http_response.headers = "Content-Encoding: none"
        self._http_response.content = "Content é".encode("ISO-8859-1")

        # The result must not have been modified.
        self.assertEqual("Content é",
                         self._http_response.get_content_as_string())

    def test_get_header_value(self):
        """Test of the 'get_header_value' method."""
        
        response = self._http_response
        
        # We create a reponse with some attributes.
        response.headers = "\nName:value\n\
Length  :  7  \r\n\n\r\
:val\n\
:\n\
Length : 8\n\
Content:\n\n"
        
        # Test of the return values.
        self.assertEqual("value", response.get_header_value("NamE"))
        self.assertEqual("7", response.get_header_value("  \nlEngTh "))
        self.assertEqual(None, response.get_header_value("Size"))
        self.assertEqual(None, response.get_header_value("  "))
        self.assertEqual(None, response.get_header_value(""))
        self.assertEqual(None, response.get_header_value(None))
        self.assertEqual("", response.get_header_value("Content"))

    def test_decode(self):
        """Test of the '_decode' method."""
        
        response = self._http_response
        response.headers = "Content-Type: ...; charset= xx-x\n"
        
        self.assertEqual("Ã©", response._decode("é".encode("utf-8")))
        self.assertEqual("é", response._decode("é".encode("ISO-8859-1")))
        
        response.headers = "Content-Type: ...; charset= utf-8\n"
        self.assertEqual("é", response._decode("é".encode("utf-8")))

    def test_get_charset(self):
        """Test of the 'get_charset' method."""

        response = self._http_response
        response.headers = "Name: value\n Content-Type: ...; charset= xx-x\n"
        
        self.assertEqual("xx-x", response.get_charset())
        
        response.headers = "Name:value\n\n"
        self.assertEqual("utf-8", response.get_charset())
        
        response.headers = "Content-Type: text/javascript"
        self.assertEqual("utf-8", response.get_charset())


class AbstractHttpCoreTest(unittest.TestCase):
    """Tests of the HttpCore class."""

    def setUp(self):
        """Test fixtures."""
        self._http_core = AbstractHttpCore()
        self._http_core_factory_mock = mock()
        self._http_response_mock = mock()
        
        when(self._http_core).get_http_factory().thenReturn(
                    self._http_core_factory_mock)
        pass

    def tearDown(self):
        """Clear all stubs."""
        unstub()
    
    def test_get_http_factory(self):
        http_core = AbstractHttpCore()
        
        with self.assertRaises(NotImplementedError):
            http_core.get_http_factory()
    
    def test_do_raw_http_request(self):
        """Test of the 'do_raw_http_request' method."""
        
        # Mock of the urllib.response and http_header objects.
        _response_mock = mock()
        _http_headers = mock()
        
        # The HTTP requests return a dummy response. If the request is made on
        # "error", and exception is raised.
        when(urllib.request).urlopen(any()).thenReturn(_response_mock)
        when(urllib.request).urlopen("error").thenRaise(URLError("error"))
        
        # Stubs of the response object.
        when(_response_mock).info().thenReturn(_http_headers)
        when(_response_mock).read().thenReturn(b"content")
        when(_http_headers).as_string().thenReturn("headers")
        
        self.assertEqual(("headers", b"content"),
                         self._http_core.do_raw_http_request("url ..."))
        
        # The urllib.request must be called with the same url argument.
        verify(urllib.request).urlopen("url ...")
        verify(_response_mock).info()
        verify(_response_mock).read()
        verify(_http_headers).as_string()
        
        # If the urllib raises an exception, we must have a HttpCoreException.
        with self.assertRaises(HttpCoreException):
            self._http_core.do_raw_http_request("error")
        
    def test_generate_response(self):
        """Test of the 'generate_response' method."""
        
        when(self._http_core).do_raw_http_request(any()).thenReturn(
                    ("headers", b"content"))
        
        when(self._http_core_factory_mock).create_http_response(any(), any()) \
            .thenReturn("response")
        
        self.assertEqual("response", self._http_core.generate_response("dummy"))
        
        verify(self._http_core).do_raw_http_request("dummy")
        verify(self._http_core_factory_mock).create_http_response(
            "headers", b"content")

    def test_do_get_response(self):
        """Test of the 'do_get_response' method."""
        
        when(self._http_core_factory_mock).create_get_request(any()) \
            .thenReturn("request")
        
        when(self._http_core).generate_response("request") \
            .thenReturn("response")
            
        self.assertEqual("response", self._http_core.do_get_response("toto"))
                         
        verify(self._http_core_factory_mock).create_get_request("toto")
        verify(self._http_core).generate_response("request")
        
    def test_do_post_response(self):
        """Test of the 'do_post_response' method."""
        
        when(urllib.parse).urlencode(any()).thenReturn("encoded_data")
        
        when(self._http_core_factory_mock).create_post_request(any(), \
            "encoded_data".encode('ISO-8859-1')).thenReturn("request")
        when(self._http_core).generate_response("request") \
            .thenReturn("response")

        self.assertEqual("response", self._http_core.do_post_response("toto",
                                                                     "data"))
        
        verify(urllib.parse).urlencode("data")
        
        verify(self._http_core_factory_mock).create_post_request("toto",
                "encoded_data".encode('ISO-8859-1'))
        verify(self._http_core).generate_response("request")
    
    def test_do_get_string(self):
        """Test of the 'do_get_string' method."""
        
        when(self._http_core).do_get_response(any()) \
            .thenReturn(self._http_response_mock)
        
        when(self._http_response_mock).get_content_as_string() \
            .thenReturn("content")
            
        self.assertEqual("content", self._http_core.do_get_string("url"))
        
        verify(self._http_core).do_get_response("url")
        verify(self._http_response_mock).get_content_as_string()
        
    def test_do_post_string(self):
        """Test of the 'do_post_string' method."""
        
        when(self._http_core).do_post_response(any(), any()) \
            .thenReturn(self._http_response_mock)
        
        when(self._http_response_mock).get_content_as_string() \
            .thenReturn("content")
            
        self.assertEqual("content", self._http_core.do_post_string("url",
                                                                   "data"))
        
        verify(self._http_core).do_post_response("url", "data")
        verify(self._http_response_mock).get_content_as_string()
            

class HttpCoreTest(unittest.TestCase):
    """Tests of the HttpCore class."""
    
    def test_get_http_factory(self):
        """Test of the 'get_http_factory' method."""
        
        http_core = HttpCore()
        
        self.assertTrue(isinstance(http_core.get_http_factory(),
                                   HttpCoreFactory))
    

class HttpCoreFactoryTest(unittest.TestCase):
    """Tests of the HttpCoreFactory class."""
    
    def setUp(self):
        """Test fixtures."""
        self._http_core_foctory = HttpCoreFactory()

    def tearDown(self):
        pass
    
    def _assert_request(self, request):
        self.assertEqual('UTF-8,*', request.get_header('Accept-charset'))
        self.assertEqual('en-us,en;q=0.7,fr;q=0.3',
                         request.get_header('Accept-language'))
        self.assertEqual('gzip', request.get_header('Accept-encoding'))
        self.assertEqual('Mozilla/5.0 (X11; U; Linux x86_64; en-US; ' + 
                         'rv:1.9.2.18) Gecko/20110628 Ubuntu/10.10 (maverick)' +
                         ' Firefox/3.6.18', request.get_header('User-agent'))
        
        self.assertEqual(4, len(request.headers))
    
    def test_create_get_request(self):
        """Test of the 'create_get_request' method."""
        
        request = self._http_core_foctory.create_get_request("http://url")
        self._assert_request(request)
        self.assertEqual("GET", request.get_method())
        
    def test_create_post_request(self):
        """Test of the 'create_post_request' method."""
        
        request = self._http_core_foctory.create_post_request("http://url",
                                                             "data")
        
        self._assert_request(request)
        self.assertEqual("data", request.get_data())
        self.assertEqual("POST", request.get_method())
        
    def test_create_http_response(self):
        """Test of the 'create_http_response' method."""
        
        response = self._http_core_foctory.create_http_response("headers",
                                                                b"content")
        
        self.assertTrue(isinstance(response, HttpResponse))
        self.assertEqual("headers", response.headers)
        self.assertEqual(b"content", response.content)
        
class HttpCoreExceptionTest(unittest.TestCase):
    """Tests of the HttpCoreException class."""
    
    def setUp(self):
        """Test fixtures."""
        self._http_core_exception = HttpCoreException()

    def tearDown(self):
        pass
    
    def test_message(self):
        self._http_core_exception.message = "message"
        self.assertEqual("message", self._http_core_exception.message)
        
    def test_cause(self):
        self._http_core_exception.cause = "cause"
        self.assertEqual("cause", self._http_core_exception.cause)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_header_value']
    
    unittest.main()