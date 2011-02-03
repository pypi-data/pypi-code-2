# -*- coding: utf-8 -*-
'''Tests for the service implementation.'''
# pylint: disable-msg=R0904

## Created: 2010-09-12 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import unittest
from mock import Mock
from httplib import responses

from matanui.service import MataNuiService
from matanui.service import MataNuiServiceException
from matanui import request
from matanui import operations

class ServiceTest(unittest.TestCase):
    """Testing of the MataNuiService class."""
    # pylint: disable=W0212
    
    def test_invoke(self):
        '''testing the raw service invocation'''
        header_check = [('Content-type', 'text/plain'), ('Content-Length', '0')]
        a_service = MataNuiService({})
        a_service.dispatch = Mock()
        storage_operation = Mock()
        storage_operation._return_value = (200, '')
        a_service.dispatch._return_value = storage_operation
        (headers, status, _) = a_service.invoke()
        self.assert_(a_service.dispatch.called)
        self.assertEquals(headers, header_check)
        self.assertEquals(status[4:], responses[200])
        
        
    def test_invoke_with_exception(self):
        '''testing the raw service invocation in presence of an exception'''
        a_service = MataNuiService({})
        a_service.dispatch = Mock()
        a_service.dispatch.side_effect = MataNuiServiceException('blah',
                                                                  (400, 'blah'))
        (_, status, _) = a_service.invoke()
        self.assert_(a_service.dispatch.called)
        self.assert_(status[4:].startswith(responses[400]))
        
       
    def test_dispatch_get_info(self):
        '''testing of the dispatcher for an info request'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt',
               'HTTP_ACCEPT': 'application/x.matanui.info'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        a_service.request.content_request = request.INFO
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.get_info.im_func.__name__
        self.assertEqual(operation._name, method_name)

    
    def test_dispatch_get_content(self):
        '''testing of the dispatcher for a get content request'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        a_service.request.content_request = request.CONTENT
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.get_content.im_func.__name__
        self.assertEqual(operation._name, method_name)

    
    def test_dispatch_post_content(self):
        '''testing of the dispatcher for a post content request'''
        env = {'REQUEST_METHOD': 'POST',
               'PATH_INFO': '/spam/eggs.txt'}
        a_service = MataNuiService(env)
        a_service.request = a_service.request = request.Request({})
        a_service.request.content_request = request.CONTENT
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.post_content.im_func.__name__
        self.assertEqual(operation._name, method_name)


    def test_dispatch_delete_file(self):
        '''testing of the dispatcher for a delete file request'''
        env = {'REQUEST_METHOD': 'DELETE',
               'PATH_INFO': '/spam/eggs.txt'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.delete_file.im_func.__name__
        self.assertEqual(operation._name, method_name)

    
    def test_dispatch_get_metadata(self):
        '''testing of the dispatcher for a get metadata request'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        a_service.request.content_request = request.METADATA
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.get_metadata.im_func.__name__
        self.assertEqual(operation._name, method_name)

    
    def test_dispatch_set_metadata(self):
        '''testing of the dispatcher for a set metadata request'''
        env = {'REQUEST_METHOD': 'PUT',
               'PATH_INFO': '/spam/eggs.txt'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        a_service.request.content_request = request.METADATA
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.put_metadata.im_func.__name__
        self.assertEqual(operation._name, method_name)

    
    def test_dispatch_list_resources(self):
        '''testing of the dispatcher for a list resources request'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/*.txt'}
        a_service = MataNuiService(env)
        a_service.request = request.Request({})
        a_service.request.content_request = request.LIST
        operation = a_service.dispatch(Mock())
        method_name = operations.StorageOperations.list_resources.im_func.__name__
        self.assertEqual(operation._name, method_name)

    

if __name__ == "__main__":
    unittest.main()
