"""
Created on Aug 14, 2011
@author: Guillaume Humbert
"""

from .httpcore import HttpCore

class HttpClient():
    """
    This class models a web browser. It allows to perform GET and POST
    requests.
    """
    
    def __init__(self):
        """Default empty constructor."""
    
    def get(self, url):
        """
        Executes a HTTP GET request on a url.
        @param url: (str) The url (e.g.: http://www.google.com).
        @raise httpclient.HttpClientException: If an error occurs.
        @return: httpclient.HtmlPage
        """
        
        try:
            httpcore = self.get_http_core()
            response_string = httpcore.do_get_string(url)
            html_page = self.get_html_page(response_string)
            
        except Exception as e:
            raise HttpClientException("An error occurred in the request " +
                                      "execution.", e)

        return html_page
    
    def post(self, url, data):
        """
        Executes a HTTP POST request on a url.
        @param url: (str) The url (e.g.: http://www.google.com).
        @param data: A list of tuples or a dictionary, e.g.: {"param":"value",
        "p":"v"} or [("param", "value"), ("p", "v")].
        @raise httpclient.HttpClientException: If an error occurs.
        @return: httpclient.HtmlPage
        """
        
        try:
            httpcore = self.get_http_core()
            response_string = httpcore.do_post_string(url, data)
            html_page = self.get_html_page(response_string)
        
        except Exception as e:
            raise HttpClientException("An error occurred in the request " +
                                      "execution.", e)

        return html_page
    
    def get_http_core(self):
        """Returns a reference to the httpclient.httpcore.HttpCore object."""
        return HttpCore()
    
    def get_html_page(self, content_string):
        """
        Builds a httpclient.Htmlpage object, and initializes it with a
        string content.
        @param content_string: (str) The content of the page.
        @return httpclient.Htmlpage
        """
        page = HtmlPage()
        page.content_as_string = content_string
        return page
        
class HtmlPage():
    """
    This class represents a HTML page (or document).
    """

    def __init__(self):
        """
        Default empty constructor.
        """
    
    @property
    def content_as_string(self):
        """(str) The raw string representation of the HTML page.""" 
        return self._content_as_string
    
    @content_as_string.setter
    def content_as_string(self, value):
        self._content_as_string = value
        
class HttpClientException(Exception):
    """
    The base exception of this module.
    """

    def __init__(self, message=None, cause=None):
        """
        Default constructor.
        @param message: (str) A description of the exception.
        @param cause: (Exception) The exception that caused this one.
        """
        self.message = message
        self.cause = cause
        
    @property
    def message(self):
        """(str) A description of the exception."""
        return self._message
    
    @message.setter
    def message(self, message):
        self._message = message
        
    @property
    def cause(self):
        """(Exception) The exception that caused this one."""
        return self._cause
    
    @cause.setter
    def cause(self, cause):
        self._cause = cause
    