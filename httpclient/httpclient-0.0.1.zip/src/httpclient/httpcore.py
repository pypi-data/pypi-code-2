"""
Created on Aug 18, 2011
@author: Guillaume Humbert
"""

import re
import gzip
import io
import urllib.request
from urllib.error import URLError
import urllib.parse
from abc import abstractmethod

class AbstractHttpCore():
    """
    This class manipulates the http requests and manipulates the headers.
    """
    
    @abstractmethod
    def get_http_factory(self):
        """
        This method must return an instance of the
        httpclient.httpcore.HttpCoreFacory class.
        """
        raise NotImplementedError()

    def do_raw_http_request(self, request):
        """
        Send an HTTP (GET or POST) request, and return the headers and the
        content (if any) of the response.
        @param request: (urllib.request.Request) The HTTP request to send.
        @return: A tuple (headers, content). The headers is a string containing
        all the response headers. The content is of type 'bytes' and contains
        the content of the response.
        """
        response = None
        try:
            response = urllib.request.urlopen(request)
        except URLError as error:
            raise HttpCoreException("HTTP request failed.", error)
        
        http_headers = response.info()
        
        headers = http_headers.as_string()
        content = response.read()
        
        return (headers, content)

    def generate_response(self, request):
        """
        Send an HTTP (GET or POST) request, and return a
        httpclient.httpcore.HttpResponse object.
        @param request: (urllib.request.Request) The HTTP request to send.
        @return: httpclient.httpcore.HttpResponse
        """
        raw_response = self.do_raw_http_request(request)

        response = self.get_http_factory().create_http_response(
                raw_response[0], raw_response[1])
        
        return response

    def do_get_response(self, url):
        """
        Send a HTTP GET request and return a httpclient.httpcore.HttpResponse
        object.
        @param url: (str) The url (e.g.: http://www.google.com).
        @return: httpclient.httpcore.HttpResponse
        """
        request = self.get_http_factory().create_get_request(url)
        return self.generate_response(request)
    
    def do_post_response(self, url, data):
        """
        Send a HTTP POST request and return a httpclient.httpcore.HttpResponse
        object.
        @param url: (str) The url (e.g.: http://www.google.com).
        @param data: A list of tuples or a dictionary, e.g.: {"param":"value",
        "p":"v"} or [("param", "value"), ("p", "v")].
        @return: httpclient.httpcore.HttpResponse
        """
        params = urllib.parse.urlencode(data)
        params = params.encode('ISO-8859-1')
        request = self.get_http_factory().create_post_request(url, params)
        return self.generate_response(request)
    
    def do_get_string(self, url):
        """
        Send a HTTP GET request and return the response content as a string.
        @param url: (str) The url (e.g.: http://www.google.com).
        @return: (str) The response content as a string.
        """
        response = self.do_get_response(url)
        return response.get_content_as_string()
    
    def do_post_string(self, url, data):
        """
        Send a HTTP POST request and return the response content as a string.
        @param url: (str) The url (e.g.: http://www.google.com).
        @param data: A list of tuples or a dictionary, e.g.: {"param":"value",
        "p":"v"} or [("param", "value"), ("p", "v")].
        @return: (str) The response content as a string.
        """
        response = self.do_post_response(url, data)
        return response.get_content_as_string()


class HttpCore(AbstractHttpCore):
    """Implement the AbstractHttpCore class. This class is a singleton."""
    
    _instance = None
    """The unique instance of this class."""
    
    def __new__(cls, *args, **kwargs):
        """Singleton."""
        if not cls._instance:
            cls._instance = super(HttpCore, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    def get_http_factory(self):
        """Returns the real http factory."""
        return HttpCoreFactory()
    
    

class HttpCoreFactory():
    """This class instanciates urllib requests and HttpResponse objects."""
    
    _instance = None
    """The unique instance of this class."""
    
    def __new__(cls, *args, **kwargs):
        """Singleton."""
        if not cls._instance:
            cls._instance = super(HttpCoreFactory, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    def create_get_request(self, url):
        """
        Create a urllib GET request, with the Firefox headers.
        @param url: (str) The URL the request will be sent to.
        @return: urllib.request.Request
        """
        request = self.create_post_request(url, None)
        
        return request
    
    def create_post_request(self, url, data):
        """
        Create a urllib POST request, with the Firefox headers.
        @param url: (str) The URL the request will be sent to.
        @param data: (bytes) The post data to send.
        @return: urllib.request.Request
        """
        
        request = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; U; Linux x86_64; "
                + "en-US; rv:1.9.2.18) Gecko/20110628 Ubuntu/10.10 "
                + "(maverick) Firefox/3.6.18",
            "Accept-Language": "en-us,en;q=0.7,fr;q=0.3",
            "Accept-Encoding": "gzip",
            "Accept-Charset": "UTF-8,*"}, data=data)
        
        return request
    
    def create_http_response(self, headers_string = None, content_bytes = None):
        """
        Create a HttpResponse object and initializes its attributes.
        @param headers_string: (str) The headers of the response, as a big
        string.
        @param content_bytes: (bytes) The encoded content of the response, the
        same that the web server send to a client. 
        """
        response = HttpResponse()
        response.headers = headers_string
        response.content = content_bytes
        return response

class HttpResponse():
    """
    This is a HTTP response. It is composed by headers and an optional content.
    @author: Guillaume Humbert
    """

    def __init__(self):
        """Default empty constructor."""
        pass
    
    def get_content_as_string(self):
        """
        Get the content response as a string. Returns None if there isn't any
        content.
        """
        
        # The content of the response. We don't know if it is gzipped yet.
        data = self.content
        
        # Here we retrieve the Content-Encoding value.
        content_encoding = self.get_header_value("Content-Encoding")
        
        # If the Content-Encoding value contains "gzip", then we ungzip this
        # content.
        if content_encoding is not None and \
            content_encoding.rfind("gzip") is not - 1:                
                bytes_io = io.BytesIO(self.content)
                gzip_file = gzip.GzipFile(fileobj=bytes_io)
                data = gzip_file.read()
        
        data = self._decode(data)
        return data
    
    def get_header_value(self, header_name):
        """Get the value of a header, or None if there's no such header."""
        
        # The header_name param must be a non empty string.
        if not isinstance(header_name, str) or header_name.strip() == "":
            return None
        
        headers_lines = self.headers.split("\n")
        for line in headers_lines:
            elems = line.split(":", 1)

            if elems[0].strip().upper() == header_name.strip().upper():
                return elems[1].strip()
        
        return None
    
    @property
    def headers(self):
        """Returns the headers of the response as a string."""
        return self._headers
    
    @headers.setter
    def headers(self, _headers):
        """Sets the headers of the response. Must be a string."""
        self._headers = _headers
    
    @property
    def content(self):
        """Returns the content of the response a bytes object."""
        return self._content
    
    @content.setter
    def content(self, _content):
        """Sets the content of the response. Must be of type bytes."""
        self._content = _content
    
    def _decode(self, encoded_string):
        """
        Decode the 'encoded_string' using the charset specified in the response
        headers. If the decoding operation failed, try to decode with
        'ISO-8859-1' encoding.
        """
        
        charset = self.get_charset()

        try:
            decoded_string = encoded_string.decode(charset)
        except (UnicodeDecodeError, LookupError):
            decoded_string = encoded_string.decode("ISO-8859-1")
        
        return decoded_string
                
    
    def get_charset(self):
        """
        Try to find the charset in the HTTP headers. If not defined, return
        "utf-8".
        """
        
        content_type = self.get_header_value("Content-Type")
        
        if content_type is None:
            return "utf-8"
        
        matcher = re.search(r"charset\s*=\s*([^\s]+)", content_type)
        if matcher is not None:
            charset = matcher.group(1)
            return charset
        
        return "utf-8"
    

class HttpCoreException(Exception):
    """The main exception of this module. Is thrown when an error occurs."""
    
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