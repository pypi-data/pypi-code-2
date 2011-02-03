# -*- coding: utf-8 -*-
'''Main service implementation.'''
# pylint: disable=W0105

## Created: 2010-09-11 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'
__date__ = '$Date: $'

import sys
import io
from httplib import responses

from matanui import request
from matanui import inout
from matanui import operations
from matanui.exceptions import MataNuiServiceException

class MataNuiService(object):
    """
    Service object that handles the implementation of the RESTful operations.
    """
    
    def __init__(self, environ):
        """
        Constructor.
        
        @param environ: Web server environment.
        @type environ: C{dict}
        """
        self.environment = environ
        """WSGI server context environment (C{dict})."""
        
        self.status = (200, '')
        """HTTP return status, default is OK (C{int}, empty C{str})
           or giving a reason/explanation (C{int}, C(str}))."""
        
        self.request = None
        """L{matanui.request.Request} object containing data of parsed request."""

        self.inout = None
        """L{matanui.inout.InOut} object containing web server input/output context."""
        
        self.error_logger = None
        """Error logger stream for the server environment."""
        
        if 'wsgi.errors' in self.environment:
            self.error_logger = self.environment['wsgi.errors']
        else:
            self.error_logger = sys.stderr
                
                
    def invoke(self):
        """
        Invokes the service implementation. This is the method called by the
        WSGI server stub script.
        """
        self.inout = inout.InOut(self.environment)
        try:
            self.request = request.Request(self.environment)
            my_storer = operations.StorageOperations(self.request, self.inout) 
            storage_operation = self.dispatch(my_storer)
            self.status = storage_operation()
        except MataNuiServiceException as err:
            self.status = err.status
            output_string = ('Service error %s %s, reason: %s/%s'
                             % (err.status[0], responses[err.status[0]],
                                err.status[1], err.message))
            self.inout.output = io.BytesIO(str(output_string))
            self.inout.content_length = len(self.inout.output.getvalue())
            self.error_logger.write(output_string)
        
        self.inout.response_headers.append(('Content-Length',
                                            str(self.inout.content_length)))
        if self.status[1]:
            status = '%s %s: %s' % (self.status[0],
                                    responses[self.status[0]],
                                    self.status[1])
        else:
            status = '%s %s' % (self.status[0], responses[self.status[0]])
        
        return self.inout.response_headers, status, self.inout.output


    def dispatch(self, storer):
        """
        Dispatches the service call to the designated handler methods.
        
        @param storer: The storer providing the required storage operations.
        @type storer: L{matanui.operations.StorageOperations}
        """
        # In case of info ignore everything else.
        if self.request.content_request == request.INFO:
            return storer.get_info
        
        # Define operations.
        actions = {('GET', request.CONTENT): storer.get_content,
                   ('GET', request.METADATA): storer.get_metadata,
                   ('GET', request.LIST): storer.list_resources,
                   ('PUT', request.METADATA): storer.put_metadata,
                   ('POST', request.CONTENT): storer.post_content,
                   ('DELETE', request.CONTENT) : storer.delete_file}
        
        http_method = self.environment['REQUEST_METHOD'].upper()
        
        try:
            action = actions[(http_method, self.request.content_request)]
        except KeyError:
            message = ('%s request for Accept header %s not defined.'
                       % (http_method, self.environment.get('HTTP_ACCEPT', '*/*')))
            status = (501, '')
            raise MataNuiServiceException(message, status)
        return action
        
    

"""
URI scheme for this service:

http://example.org/this/is/the/file.ext
http://example.org/this/is/the/file.ext/$id_4c81ed79634ca0c4e8445967
http://example.org/this/is/the/file.ext/$metadata
http://example.org/this/is/the/file.ext/$id_4c81ed79634ca0c4e8445967/$metadata
http://example.org/$id_4c81ed79634ca0c4e8445967

Content type(s) to accept:
 - application/x.matanui.content[-v0.1] (default)
 - application/x.matanui.metadata[-v0.1]+json
 - application/x.matanui.info[-v0.1][+json]

Format for meta-data and queries: JSON

HTTP details:
 - HTTP methods:
   - GET:
     - on content objects for content (raw)
     - on meta-data and containers for meta-data (JSON)
     - for queries
   - PUT:
     - update meta-data (content object and collection)
   - POST:
     - create content object/collection (e. g. upload of file)
   - DELETE:
     - delete item incl. meta-data

 - Status codes:
   - 200 OK
   - 201 Created
   - 301 Moved Permanently
   - 302 Found (for name -> specific obj. ID redirection)
   - 400 Bad Request
   - 401 Unauthorized
   - 403 Forbidden
   - 404 Not Found
   - 405 Method Not Allowed
   - 501 Not Implemented
   - (503 Service Unavailable)

 - GET
   - Content:
     - of most recent file:
       Accept: application/x.matanui.content
       http://example.org/this/is/the/file.ext
       
     - of a specific file version:
       Accept: application/x.matanui.content
       http://example.org/$id_4c81ed79634ca0c4e8445967
       http://example.org/this/is/the/file.ext$id_4c81ed79634ca0c4e8445967
       (Last should give an error if path doesn't match for object ID.)
       
   - Meta-data of file/collection:
     Accept: application/x.matanui.metadata+json
     http://example.org/this/is/the/file.ext
     http://example.org/this/is/the
     http://example.org/$id_4c81ed79634ca0c4e8445967
     http://example.org/this/is/the/file.ext$id_4c81ed79634ca0c4e8445967
     (Last should give an error if path doesn't match for object ID.)
     
   - List:
     Accept: application/x.matanui.list+json
     http://example.org/this/is/the/path/ba?.*
     (paths starting with the path fragment, can be URL encoded/quoted)
     
   - Query (returns full set of meta-data for found objects):
     Accept: application/x.matanui.metadata
     http://example.org?filename=file.ext&owner=guy
     http://example.org?object=4c81ed79634ca0c4e8445967
     
   - Info:
     Accept: application/x.matanui.info
     http://example.org
     
 - POST:
   - Upload (new) content of file:
     Accept: application/x.matanui.content
     http://example.org/this/is/the/file.ext
     (Returns object URI. Should it copy old meta-data?)
     
   - Store on server, also for empty collection
     Accept: application/x.matanui.metadata+json
     http://example.org/this/is/the/file.ext
     http://example.org/this/is/the
     
   - /!\ TODO: What to do if collection exists?

 - PUT:
   - Update meta-data on content/collection:
     Accept: application/x.matanui.metadata+json
     http://example.org/this/is/the/file.ext
     http://example.org/this/is/the

 - DELETE:
   - Item with meta-data:
     Accept: application/x.matanui.content
     http://example.org/$id_4c81ed79634ca0c4e8445967
     http://example.org/this/is/the/file.ext
     http://example.org/this/is/the/
     
   - Just meta-data:
     Accept: application/x.matanui.metadata+json
     http://example.org/$id_4c81ed79634ca0c4e8445967
     http://example.org/this/is/the/file.ext
     http://example.org/this/is/the
     
   - /!\ TODO: Delete collection only if empty? Delete meta-data?
"""
