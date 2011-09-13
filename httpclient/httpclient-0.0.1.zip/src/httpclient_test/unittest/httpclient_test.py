"""
Created on Aug 18, 2011
@author: Guillaume Humbert
"""
from unittest import TestCase, main

from mockito import when, any, unstub, mock, verify

from httpclient import HttpClient
from httpclient.httpcore import HttpCore
from httpclient.httpclient import HttpClientException
import unittest

class HttpClientTest(TestCase):
    """Tests of the HttpClient class."""

    def setUp(self):
        """Test fixtures."""
        
        self._http_client = HttpClient()

        self._httpcore_mock = mock()
        self._response_mock = mock()
        
        when(self._http_client).get_http_core().thenReturn(
                self._httpcore_mock)

    def tearDown(self):
        """Unregisters all stubs."""
        unstub()


    def test_get(self):
        """Test of the 'get' method."""
        
        when(self._httpcore_mock).do_get_string(any()).thenReturn("response")
        when(self._httpcore_mock).do_get_string("error").thenRaise(Exception)
        
        when(self._http_client).get_html_page("response").thenReturn("page")
        
        self.assertEqual("page", self._http_client.get("url"))
        
        verify(self._httpcore_mock).do_get_string("url")
        verify(self._http_client).get_html_page("response")
        
        with self.assertRaises(HttpClientException):
            self._http_client.get("error")
        
    def test_post(self):
        """Test of the 'post' method."""
        
        when(self._httpcore_mock).do_post_string(any(), any()) \
            .thenReturn("response")
        when(self._httpcore_mock).do_post_string("error", any()) \
            .thenRaise(Exception)
        
        when(self._http_client).get_html_page("response").thenReturn("page")
        
        self.assertEqual("page", self._http_client.post("url", "data"))
        
        verify(self._httpcore_mock).do_post_string("url", "data")
        verify(self._http_client).get_html_page("response")
        
        with self.assertRaises(HttpClientException):
            self._http_client.post("error", "data")

    def test_get_http_core(self):
        """Test of the 'get_http_core' method."""
        
        http_client = HttpClient()
        
        self.assertTrue(isinstance(http_client.get_http_core(), HttpCore))
        
    def test_get_html_page(self):
        """Test of the 'get_html_page' method."""
        
        page = self._http_client.get_html_page("content")
        self.assertEqual(page.content_as_string, "content")

class HttpClientExceptionTest(unittest.TestCase):
    """Tests of the HttpClientException class."""
    
    def setUp(self):
        """Test fixtures."""
        self._http_client_exception = HttpClientException()

    def tearDown(self):
        pass
    
    def test_message(self):
        self._http_client_exception.message = "message"
        self.assertEqual("message", self._http_client_exception.message)
        
    def test_cause(self):
        self._http_client_exception.cause = "cause"
        self.assertEqual("cause", self._http_client_exception.cause)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_get_html']
    main()
