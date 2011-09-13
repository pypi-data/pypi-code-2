"""
Created on Aug 25, 2011
@author: Guillaume Humbert
"""

import http.server
import io
import gzip
import threading
import re
import os.path

class TestHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Handles HTTP GET and POST requests. The response is gzipped if the client
    accepts it.
    """
    def __init__(self, request, client_address, server):
        http.server.SimpleHTTPRequestHandler.__init__(
                self, request, client_address, server)
        
        #self.protocol_version = "HTTP/1.1"
    
    def log_request(self, code='-', size='-'):
        pass
    
    def _do_request(self, post_request=False):
        """
        Perform a GET or POST request. If the post_request parameter is True,
        then it will be treated as a POST request, else as a GET request.
        @param post_request: (bool) True if it is a POST request, False if it is
        a GET. 
        """
        
        # Translates the URL path in a filesystem path.
        path = self.translate_path(self.path)
        TestHttpRequestHandler.protocol_version = "HTTP/1.1"
        # The content of the file is retrieved.
        file_content = self.get_file_content(path)
        if file_content is None:
            self.send_error(404, "File not found.")
            return
        
        # 200 means OK. We return only html.
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        
        file_content = self._replace_post_tags(file_content, post_request)
        
        file_content = self.encode_data(file_content)
        
        if (self.headers.get('Connection') == 'close'):
            self.send_header('Connection', 'close')
        
        self.send_header("Content-Length", len(file_content))
        self.end_headers()
        self.wfile.write(file_content)
        #self.wfile.close()
    
    def encode_data(self, data):
        """
        Encode (compress) the data if the client accepts it.
        @param data: (bytes) The data to encode.
        @return: (bytes) The encoded data.
        """
        
        # The Accept-Encoding header sent by the client.
        encoding = self.headers.get("Accept-Encoding")
        
        if encoding.find("gzip") != -1:
            # If the client accepts gzip, we encode the response in gzip.
            self.send_header("Content-Encoding", "gzip")
            
            bytes_io = io.BytesIO()
            gzip_file = gzip.GzipFile(fileobj=bytes_io, mode="wb")
            gzip_file.write(data)
            gzip_file.close()
            
            result = bytes_io.getvalue()
            bytes_io.close()
            
            return result
        else:
            return data
    
    def translate_path(self, path):
        
        new_path = "/src/httpclient_test/functionaltest/html/" + path
        
        return http.server.SimpleHTTPRequestHandler.translate_path(self, new_path)
    
    def _replace_post_tags(self, bytes_to_replace, post_request):
        """
        If post_request is true, all <post/> tags are replaced by the data of
        the request. Else if is replaced by an empty string.
        @param bytes_to_replace: (bytes) The bytes to search for <post/> tags.
        @param post_request: (bool) True if the request is POST, False if it is
        GET.
        @return: (bytes) The new byte sequence.
        """
        
        if post_request:
            res = re.sub(b"<post/>", self._read_data(), bytes_to_replace)
        else:
            res = re.sub(b"<post/>", b"", bytes_to_replace)
        return res
    
    def _read_data(self):
        """
        Read the data of a POST request, and set the appropriate Content-Length
        header.
        @return: (bytes) The data of a POST request.
        """
        
        data_length = self.headers.get("Content-Length")
        
        if data_length is None:
            raise IOError('No "Content-Length" header in a POST request.')
        
        data = self.rfile.read(int(data_length))
        
        return data
        
    
    def do_GET(self):
        """Handle GET requests."""
        
        self._do_request()
    
    def do_POST(self):
        """Handle POST requests."""
        
        self._do_request(post_request=True)
      
    def get_file_content(self, path):
        """
        Read a file and return its content as bytes. Return None if the file is
        a directory, is not readable or does not exist.
        @param path: (str) The path of the file in the filesystem.
        @return: The content of the file as bytes.
        """
        
        # If a request is made for a directory, a 404 error is returned.
        if os.path.isdir(path):
            return None
    
        file_io = None

        try:
            file_io = io.FileIO(path, mode="r")
        except IOError:
            return None
        
        content = file_io.read()
        file_io.close()
        
        return content

class TestHttpRequestHandlerNoGzip(TestHttpRequestHandler):
    """
    A request handler that don't gzip encode the response.
    """
    
    def encode_data(self, data):
        """
        Never encode the data.
        @param data: (bytes) The data to encode.
        @return: (bytes) The same data as the data parameter.
        """
        return data

class TestServer():
    """
    A convenient server for testing purposes.
    """

    def __init__(self):
        """Initializes the listen_port to 8080."""
        self.listen_port = 8080

    def start(self):
        """Start the server."""
        
        server = http.server.HTTPServer(("", self.listen_port),
                                              TestHttpRequestHandler)

        self._server_thread = ServerThread(server)
        self._server_thread.start()
        
    def shutdown(self):
        """Stop the server."""
        
        self._server_thread.stop()  
        self._server_thread.join()  
    
    @property
    def listen_port(self):
        """
        The port on which the server will listen.
        """
        return self._listen_port
    
    @listen_port.setter
    def listen_port(self, value):
        self._listen_port = value

    @property
    def gzip_support(self):
        return self._gzip_support

    @gzip_support.setter
    def gzip_support(self, value):

        self._gzip_support = value

        if value:
            handler = TestHttpRequestHandler
        else:
            handler = TestHttpRequestHandlerNoGzip
        
        self._server_thread._server.RequestHandlerClass = handler

        
class ServerThread(threading.Thread):
    """
    A thread that will run a HTTP server.
    """
    
    def __init__(self, server):
        """
        Initializes the HTTP server to run.
        @param server: The HTTP server to run.
        """
        threading.Thread.__init__(self)
        self._server = server
        
    def run(self):
        """
        Start the server.
        """
        self._server.serve_forever()    
        self._server.server_close()
        
    def stop(self):
        """
        Stop the server.
        """
        self._server.shutdown()