#!/usr/bin/env python
"""NDG XACML functions unit test package 

NERC DataGrid
"""
__author__ = "P J Kershaw"
__date__ = "26/03/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = "$Id: test_matchfunctions.py 7087 2010-06-25 11:23:09Z pjkersha $"
import unittest
from os import path
import logging
logging.basicConfig(level=logging.DEBUG)

from ndg.xacml.core.functions import FunctionMap
from ndg.xacml.core.functions.v2.regexp_match import RegexpMatchBase


class FunctionTestCase(unittest.TestCase):
    """Test XACML match functions implementation
    
    The log output gives an indication of the XACML functions which are not 
    implemented yet"""
    
    def test01LoadMap(self):   
        funcMap = FunctionMap()
        funcMap.loadAll()
        anyUriMatchNs = \
            'urn:oasis:names:tc:xacml:2.0:function:anyURI-regexp-match'
            
        self.assert_(issubclass(funcMap.get(anyUriMatchNs), RegexpMatchBase))

        
if __name__ == "__main__":
    unittest.main()