# -*- coding: utf-8 -*-
'''Operations to execute from configured service backend.'''

## Created: 2010-12-24 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import io
import pprint

import matanui
from matanui import config
from matanui import exceptions
from matanui import storerinterface
from matanui import API_VERSION

class StorageOperations(object):
    """
    This class contains storage operations, making use of accessing the
    configured storage backend. All methods, except for the constructor,
    conduct the requested operation and return a tupel with the HTTP status
    code for success. In case of failure, they all raise a 
    L{matanui.errors.MataNuiServiceException}.
    """

    def __init__(self, a_request, an_inout):
        """
        Constructor.
        
        @param a_request: An object that holds the request data.
        @type a_request: L{matanui.request.Request}
        @param an_inout: An object that holds context for input/output with the
            web server.
        @type an_inout: L{matanui.inout.Response}
        """
        self.request = a_request
        self.inout = an_inout
        
        # Get an instance of the configured storage backend.
        storage_backend = config.STORAGE_BACKEND.split('.')
        package_name = '.'.join(storage_backend[:-1])
        class_name = storage_backend[-1]
        module = __import__(package_name, fromlist=[class_name])
        StorageBackend = getattr(module, class_name) # pylint: disable=C0103
        self._storage_backend = StorageBackend()
        
    
    def get_content(self):
        """
        Retrieves the target file's content.
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        try:
            content = self._storage_backend.get_content(object_id=self.request.object_id,
                                                        filename=self.request.path)
            self._check_access_allowed(storerinterface.PRIV_READ)
        except exceptions.MataNuiStorerException as err:
            status = (404, 'Storage error')
            message = err.message
            raise exceptions.MataNuiServiceException(message, status)
            
        self.inout.set_output_stream(content.data, content.block_size)
        self.inout.content_length = content.length
        self.inout.response_headers.append(('ETag', content.checksum))
        self.inout.response_headers.append(('x-matanui-object-id',
                                            str(content.object_id)))
        self.inout.response_headers.append(('Content-Type',
                                            content.content_type))
        self.inout.response_headers.append(('Last-Modified',
                                            content.last_modified))
        return (200, '')
        
    
    def get_info(self):
        """
        Returns information about the server and the call.
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        self.inout.output = io.BytesIO()
        self.inout.output.write('MataNui server version %s\n'
                                % matanui.__version__)
        self.inout.output.write('MataNui API version %s\n\n' % API_VERSION)
        self.inout.output.write('Storage back-end: %s\n'
                                % self._storage_backend.__class__.__name__)
        
        if config.VERBOSE_INFO:
            self.inout.output.write("\nServer's request environment:\n%s\n"
                                    % pprint.pformat(self.request.environment))
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())
        return (200, '')
        
        
    def post_content(self):
        """
        Stores content in the storage back-end.
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        self._check_access_allowed(storerinterface.PRIV_WRITE, dir_mode=True)
        content_object = storerinterface.ContentObject()
        content_object.data = self.inout.input_stream
        content_object.filename = self.request.path
        content_object.owner = self.request.username
        object_id = self._storage_backend.put_content(content_object,
                                                      self.request.query)
        content = self._storage_backend.get_content(object_id=object_id)
        self.inout.response_headers.append(('x-matanui-object-id',
                                            str(object_id)))
        self.inout.response_headers.append(('ETag', content.checksum))
        self.inout.output = io.BytesIO()
        self.inout.output.write('Object ID %s stored.' % object_id)
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())  
        return (201, '')
        
        
    def delete_file(self):
        """
        Deletes a file (content and meta-data) from the storage back-end.
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        try:
            self._check_access_allowed(storerinterface.PRIV_WRITE)
            object_id = self._storage_backend.delete_file(object_id=self.request.object_id,
                                                          filename=self.request.path)
        except exceptions.MataNuiStorerException as err:
            status = (404, 'Storage error')
            message = err.message
            raise exceptions.MataNuiServiceException(message, status)
        
        self.inout.output = io.BytesIO()
        self.inout.output.write('Object with ID %s deleted.' % object_id)
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())  
        return (200, '')


    def get_metadata(self):
        """
        Retrieves the target resource's meta-data. This operation returns the
        complete meta-data as stored in the storage backend ("system" level
        and custom 'metadata' stored fields).
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        try:
            oid, metadata = self._storage_backend.get_metadata(object_id=self.request.object_id,
                                                               filename=self.request.path)
            self._check_access_allowed(storerinterface.PRIV_READ)
        except exceptions.MataNuiStorerException as err:
            status = (404, 'Storage error')
            message = err.message
            raise exceptions.MataNuiServiceException(message, status)
            
        content_type = ('%(base)s%(type)s-v%(api)s+%(encoding)s' %
                        {'base': self.request.ACCEPT_HEADER_BASE,
                         'type': self.request.content_request,
                         'api': self.request.version,
                         'encoding': self.request.encoding})
        self.inout.response_headers.append(('Content-Type', content_type))
        self.inout.response_headers.append(('x-matanui-object-id', oid))
        self.inout.output = io.BytesIO()
        self.inout.output.write(metadata.json_string)
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())  
        return (200, '')


    def put_metadata(self):
        """
        Sets the target resource's meta-data. Certain items of "system"
        meta-data ('filename', 'owner', 'contentType', 'accessMode')
        only can be overwritten. The meta-data passed in will extract these
        pieces and set them accordingly. Whatever meta-data is present in
        'metadata' will replace whatever meta-data in that section was available
        previously.
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        metadata_object = storerinterface.MetadataObject()
        metadata_object.set_from_json_stream(self.inout.input_stream)
        try:
            self._check_access_allowed(storerinterface.PRIV_READ_WRITE)
            if 'filename' in metadata_object.content:
                target = metadata_object.content['filename']
                self._check_access_allowed(storerinterface.PRIV_WRITE,
                                           target=target, dir_mode=True)
            oid = self._storage_backend.set_metadata(metadata_object,
                                                     object_id=self.request.object_id,
                                                     filename=self.request.path)
        except exceptions.MataNuiStorerException as err:
            status = (400, 'Storage error')
            message = err.message
            raise exceptions.MataNuiServiceException(message, status)
            
        self.inout.response_headers.append(('x-matanui-object-id', oid))
        self.inout.output = io.BytesIO()
        self.inout.output.write('Meta-data for object ID %s set.' % oid)
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())  
        return (200, '')


    def list_resources(self):
        """
        Queries for resources satisfying a given item query. This operation 
        returns the meta-data as stored in the storage backend ("system" level
        meta-data field only, user level meta-data is stripped out to keep the
        response short).
        
        @return: HTTP return status.
        @rtype: C{tupel} of (C{int}, C(str})
        """
        try:
            if not self.request.object_id:
                self._check_access_allowed(storerinterface.PRIV_READ, dir_mode=True)
                entries = self._storage_backend.list_resources(self.request.path)
            else:
                status = (400, 'Storage error')
                message = 'Object ID not supported for list query.'
                raise exceptions.MataNuiServiceException(message, status)
        except exceptions.MataNuiStorerException as err:
            status = (400, 'Storage error')
            message = err.message
            raise exceptions.MataNuiServiceException(message, status)
            
        content_type = ('%(base)s%(type)s-v%(api)s+%(encoding)s' %
                        {'base': self.request.ACCEPT_HEADER_BASE,
                         'type': self.request.content_request,
                         'api': self.request.version,
                         'encoding': self.request.encoding})
        self.inout.response_headers.append(('Content-Type', content_type))
        self.inout.output = io.BytesIO()
        self.inout.output.write(entries.json_string)
        self.inout.output.seek(0)
        self.inout.content_length = len(self.inout.output.getvalue())  
        return (200, '')


    def _check_access_allowed(self, access_mode, target=None, dir_mode=False):
        """
        Checks whether requested access is allowed.
        
        @param access_mode: UN*X style access mode indicator.
        @type access_mode: C{int}
        @param target: Path/file name of the target of an operation (optional).
        @type target: C{str}
        @param dir_mode: Are we interested in directory level access, e. g. for
            writing a file into the directory or listing it (default: False).
        @type dir_mode: C{bool}
        
        @raise exceptions.MataNuiServiceException: If the requested operation
            is not permitted.
        """
        filename = self.request.path
        object_id = self.request.object_id
        if target is not None:
            filename = target
            object_id = None
            
        access = self._storage_backend.is_access_allowed(self.request.username,
                                                         access_mode,
                                                         filename=filename,
                                                         object_id=object_id,
                                                         dir_mode=dir_mode)
        if not access:
            access_types = {storerinterface.PRIV_READ: 'read',
                            storerinterface.PRIV_WRITE: 'write',
                            storerinterface.PRIV_READ_WRITE: 'read/write'}
            message = 'No %s access to resource.' % access_types[access_mode]
            status = (403, 'Insufficient permissions')
            raise exceptions.MataNuiServiceException(message, status)
