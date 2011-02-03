# -*- coding: utf-8 -*-
'''Tests for the request container/parser implementation.'''

## Created: 2010-12-24 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

import unittest

from matanui import request
from matanui.exceptions import MataNuiServiceException
from test import testdata


class RequestTest(unittest.TestCase):
    """Testing of the Request class."""
    # pylint: disable=W0212
    
    def test_split_accept_header(self):
        '''test of accept header splitting and ordering'''
        headers = [('text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    ['text/html', 'application/xhtml+xml', 'application/xml', '*/*']),
                   ('*/*;q=0.8,text/html,application/xhtml+xml,application/xml;q=0.9',
                    ['text/html', 'application/xhtml+xml', 'application/xml', '*/*']),
                   ('application/x.matanui.metadata-v0.2+json,application/x.matanui.metadata-v0.1+json',
                    ['application/x.matanui.metadata-v0.2+json', 'application/x.matanui.metadata-v0.1+json']),
                   ('application/x.matanui.metadata-v0.2+json,application/x.matanui.metadata-v0.1+json;q=0.5',
                    ['application/x.matanui.metadata-v0.2+json', 'application/x.matanui.metadata-v0.1+json']),
                   ('application/x.matanui.metadata-v0.2+json;q=1.0,application/x.matanui.metadata-v0.1+json;q=0.5',
                    ['application/x.matanui.metadata-v0.2+json', 'application/x.matanui.metadata-v0.1+json']),
                   ('application/x.matanui.metadata-v0.1+json;q=0.5,application/x.matanui.metadata-v0.2+json;q=1.0',
                    ['application/x.matanui.metadata-v0.2+json', 'application/x.matanui.metadata-v0.1+json']),
                   ('application/x.matanui.metadata-v0.1+json;q=0.5,application/x.matanui.metadata-v0.2+json',
                    ['application/x.matanui.metadata-v0.2+json', 'application/x.matanui.metadata-v0.1+json']),
                   ('', ['*/*'])
                  ]
        for (header, expected) in headers:
            env = {'HTTP_ACCEPT': header}
            a_request = request.Request({})
            a_request.environment = env
            accept_list = a_request._split_accept_header()
            self.assertEqual(len(accept_list), len(expected))
            for (hoped_for, got) in zip(expected, accept_list):
                self.assert_(hoped_for == got)
        
    
    def test_parse_accept_header_good_api(self):
        '''test of the parser for good API indicators'''
        for (item, expected) in testdata.GOOD_APIS:
            a_request = request.Request({})
            result, _ = a_request._parse_accept_type(item)
            self.assertEqual(result, expected)


    def test_parse_accept_header_wrong_api(self):
        '''test of the parser for wrong API indicators'''
        for item in testdata.WRONG_APIS:
            a_request = request.Request({})
            _, status = a_request._parse_accept_type(item)
            self.assertEquals(status[0], 406)
    
    
    def test_parse_path_with_name(self):
        '''testing of the parser for normal request'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt'}
        a_request = request.Request({})
        a_request.environment = env
        a_request._parse_path()
        self.assertEquals(a_request.path, testdata.GOOD_GRIDFS.name)
        self.assertEquals(a_request.content_request, request.CONTENT)
        
    
    def test_parse_with_oid(self):
        '''testing of the parser for object IDs'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt$id_4c81ed79634ca0c4e8445967'}
        a_request = request.Request({})
        a_request.environment = env
        a_request._parse_path()
        self.assertEquals(a_request.path, testdata.GOOD_GRIDFS.name)
        self.assertEquals(a_request.content_request, request.CONTENT)
        self.assertEquals(a_request.object_id,
                          testdata.GOOD_GRIDFS.object_id)

    
    def test_parse_multiple_oids(self):
        '''testing of the parser for multiple object IDs'''
        env = {'REQUEST_METHOD': 'GET',
               'PATH_INFO': '/spam/eggs.txt$id_4c81ed79634ca0c4e8445967$id_4c81ed79634ca0c4e8445968'}
        a_request = request.Request({})
        a_request.environment = env
        try:
            a_request._parse_path()
            self.assert_(False)
        except MataNuiServiceException as err:
            self.assertEquals(err.status[0], 400)


    def test_parse_query_parameters(self):
        '''test of parsing query parameters'''
        tests = {'foo=%22bar%22':
                     {'foo': 'bar'},
                 'foo=%22spam%22&bar=%22eggs%22':
                     {'foo': 'spam', 'bar': 'eggs'},
                 'Q=%22ultimate%22&A=42':
                     {'Q': 'ultimate', 'A': 42},
                 'metadata=%7B%22owner%22%3A+%22brian%22%7D':
                     {'metadata': {'owner': 'brian'}},
                }
        
        a_request = request.Request({})
        for query_string, expected in tests.items():
            a_request.environment = {'QUERY_STRING': query_string}
            a_request._parse_query_parameters()
            self.assertEqual(a_request.query, expected)

        
    def test_parse_query_parameters_fail_non_json(self):
        '''test of parsing query parameters with non-JSON values'''
        tests = ['foo=bar',
                 'foo=spam&bar=eggs',
                 'Q=ultimate&A=42',
                 'metadata=%7B%27owner%27%3A+%27brian%27%7D']
        a_request = request.Request({})
        for query_string in tests:
            a_request.environment = {'QUERY_STRING': query_string}
            self.assertRaises(MataNuiServiceException,
                              a_request._parse_query_parameters)



if __name__ == "__main__":
    unittest.main()
