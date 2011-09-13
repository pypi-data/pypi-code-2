"""
Created on Aug 24, 2011
@author: Guillaume Humbert
"""
import unittest
import httpclient
from httpclient_test.functionaltest.server import TestServer

class HttpClientTest(unittest.TestCase):
    """Test the methods of the HttpClient class."""

    def setUp(self):
        """Test fixtures."""
        
        # The test HTTP server is started.
        self._server = TestServer()
        self._server.start()
        
        self._http_client = httpclient.HttpClient()


    def tearDown(self):
        self._server.shutdown()
        

    def test_get(self):
        """Test of the 'get' method."""
        
        page = self._http_client.get("http://localhost:8080/get.html")
        html_string = page.content_as_string
        self.assertTrue(html_string.find("<h1>GET</h1>") != -1)
        
        self._server.gzip_support = False
        
        page = self._http_client.get("http://localhost:8080/get.html")
        html_string = page.content_as_string
        self.assertTrue(html_string.find("<h1>GET</h1>") != -1)
        
    def test_post(self):
        """Test of the 'post' method."""
        
        page = self._http_client.post("http://localhost:8080/post.html",
                                      {"param": "value"})
        html_string = page.content_as_string
        self.assertTrue(html_string.find("<h1>POST</h1>") != -1)
        self.assertTrue(html_string.find("param=value") != -1)
    