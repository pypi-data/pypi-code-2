# -*- coding: utf-8 -*-
'''Tests for the implementation of the operations.'''

## Created: 2010-12-24 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import unittest
import io
import json
from mock import Mock

from matanui import operations
from matanui import inout
from matanui import request
from matanui.storerinterface import NullStorer
from matanui.storerinterface import MetadataObject
from matanui.exceptions import MataNuiServiceException
from test import testdata

class OperationsTest(unittest.TestCase):
    """Tests the service actions declared in the operations module."""

    def setUp(self): # pylint: disable=C0111
        testdata.GOOD_INPUT.data.seek(0)
        testdata.GOOD_GRIDFS.seek(0)
        

    def test_get_content(self):
        '''test retrieving content'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.content_request = request.CONTENT
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        content_object = testdata.GOOD_CONTENT
        storage_handle.get_content.return_value = content_object
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.get_content()
        self.assert_(my_storer._storage_backend.get_content.called)
        a_string = testdata.GOOD_GRIDFS.getvalue()
        self.assertEquals(an_inout.output.read(), a_string)
        self.assertEquals(an_inout.content_length, len(a_string))
        self.assertEquals(status[0], 200)
        
        
    def test_get_content_with_oid(self):
        '''test retrieving content with file name and a specific object ID'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt$id_4c81ed79634ca0c4e8445967'}
        a_request.environment = env
        a_request.content_request = request.CONTENT
        a_request.object_id = testdata.GOOD_GRIDFS.object_id
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        content_object = testdata.GOOD_CONTENT
        storage_handle.get_content.return_value = content_object
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.get_content()
        self.assert_(my_storer._storage_backend.get_content.called)
        a_string = testdata.GOOD_GRIDFS.getvalue()
        self.assertEquals(an_inout.output.read(), a_string)
        self.assertEquals(an_inout.content_length, len(a_string))
        self.assertEquals(status[0], 200)
        
        
    def test_post_content(self):
        '''test uploading content'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'POST',
               'PATH_INFO': '/spam/eggs.txt',
               'wsgi.input': testdata.GOOD_INPUT}
        a_request.environment = env
        a_request.content_request = request.CONTENT
        a_request.object_id = testdata.GOOD_GRIDFS.object_id
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        object_id_expected = '4c91b12838dd124df1000000'
        storage_handle.put_content.return_value = object_id_expected
        storage_handle.get_content.return_value = testdata.GOOD_CONTENT
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.post_content()
        self.assert_(my_storer._storage_backend.put_content.called)
        self.assert_(('x-matanui-object-id', object_id_expected)
                     in an_inout.response_headers)
        self.assert_(('ETag', testdata.GOOD_GRIDFS.md5)
                     in an_inout.response_headers)
        self.assertEquals(status[0], 201)
        
        
    def test_delete_file(self):
        '''test deleting file'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'DELETE',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.delete_file()
        self.assert_(my_storer._storage_backend.delete_file.called)
        self.assertEquals(status[0], 200)
        

    def test_get_info(self):
        '''test retrieving server info'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt',
               'HTTP_ACCEPT': 'application/x.matanui.info'}
        a_request.environment = env
        a_request.content_request = request.INFO
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        my_storer = operations.StorageOperations(a_request, an_inout)
        status = my_storer.get_info()
        content = an_inout.output.read()
        self.assert_(len(content) > 0)
        self.assertEquals(an_inout.content_length, len(content))
        self.assertEquals(status[0], 200)
        
        
    def test_get_metadata(self):
        '''test retrieving meta-data'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.content_request = request.METADATA
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        content_object = MetadataObject(testdata.GOOD_METADATA)
        storage_handle.get_metadata.return_value = (testdata.GOOD_GRIDFS.object_id,
                                                            content_object) 
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.get_metadata()
        self.assert_(my_storer._storage_backend.get_metadata.called)
        a_string = content_object.json_string
        self.assertEquals(an_inout.output.read(), a_string)
        self.assertEquals(an_inout.content_length, len(a_string))
        self.assertEquals(status[0], 200)
        
        
    def test_set_metadata(self):
        '''test setting meta-data'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'PUT',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.content_request = request.METADATA
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        an_inout.input_stream = io.BytesIO()
        an_inout.input_stream.write(json.dumps(testdata.GOOD_METADATA))
        an_inout.input_stream.seek(0)
        storage_handle = Mock(NullStorer)
        storage_handle.set_metadata.return_value = testdata.GOOD_GRIDFS.object_id
        storage_handle.is_access_allowed.return_value = True
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.put_metadata()
        self.assert_(my_storer._storage_backend.set_metadata.called)
        self.assert_(('x-matanui-object-id', testdata.GOOD_GRIDFS.object_id)
                     in an_inout.response_headers)
        self.assertEquals(status[0], 200)


    def test_set_metadata_rename(self):
        '''test setting meta-data with filename for a rename'''
        def dummy_access_allowed(user, access_mode, filename=None,
                                 object_id=None, dir_mode=False):
            if filename.startswith('/readonly/'):
                return False
            else:
                return True
        
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'PUT',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.content_request = request.METADATA
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        metadata = testdata.GOOD_METADATA.copy()
        metadata['filename'] = '/bacon/eggs.txt'
        an_inout.input_stream = io.BytesIO()
        an_inout.input_stream.write(json.dumps(testdata.GOOD_METADATA))
        an_inout.input_stream.seek(0)
        storage_handle = Mock(NullStorer)
        storage_handle.set_metadata.return_value = testdata.GOOD_GRIDFS.object_id
        storage_handle.is_access_allowed = dummy_access_allowed
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.put_metadata()
        self.assert_(my_storer._storage_backend.set_metadata.called)
        self.assert_(('x-matanui-object-id', testdata.GOOD_GRIDFS.object_id)
                     in an_inout.response_headers)
        self.assertEquals(status[0], 200)


    def test_set_metadata_rename_fail(self):
        '''test setting meta-data with filename for rename on read-only target'''
        def dummy_access_allowed(user, access_mode, filename=None,
                                 object_id=None, dir_mode=False):
            if filename.startswith('/readonly/'):
                return False
            else:
                return True
        
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'PUT',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request.environment = env
        a_request.content_request = request.METADATA
        a_request.object_id = None
        a_request.path = testdata.GOOD_GRIDFS.name
        an_inout = inout.InOut({})
        metadata = testdata.GOOD_METADATA.copy()
        metadata['filename'] = '/readonly/eggs.txt'
        an_inout.input_stream = io.BytesIO()
        an_inout.input_stream.write(json.dumps(metadata))
        an_inout.input_stream.seek(0)
        storage_handle = Mock(NullStorer)
        storage_handle.set_metadata.return_value = testdata.GOOD_GRIDFS.object_id
        storage_handle.is_access_allowed = dummy_access_allowed
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        self.assertRaises(MataNuiServiceException, my_storer.put_metadata)
        self.assertFalse(my_storer._storage_backend.set_metadata.called)


    def test_list_resources(self):
        '''test listing resources'''
        a_request = request.Request({})
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/*.txt'}
        a_request.environment = env
        a_request.content_request = request.LIST
        a_request.object_id = None
        a_request.path = env['PATH_INFO']
        an_inout = inout.InOut({})
        storage_handle = Mock(NullStorer)
        content_object = MetadataObject(testdata.make_dummy_fs_entries(testdata.TEST_ENTRIES))
        storage_handle.list_resources.return_value = content_object
        my_storer = operations.StorageOperations(a_request, an_inout)
        my_storer._storage_backend = storage_handle
        status = my_storer.list_resources()
        self.assert_(my_storer._storage_backend.list_resources.called)
        a_string = content_object.json_string
        self.assertEquals(an_inout.output.read(), a_string)
        self.assertEquals(an_inout.content_length, len(a_string))
        self.assertEquals(status[0], 200)
        
        

if __name__ == "__main__":
    unittest.main()
