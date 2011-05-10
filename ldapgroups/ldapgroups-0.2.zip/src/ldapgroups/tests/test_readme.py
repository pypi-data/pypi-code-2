'''
Created on 5-mei-2011

@author: jm
'''
import unittest
import doctest

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt', 
            optionflags = (
                doctest.ELLIPSIS +
                doctest.NORMALIZE_WHITESPACE +
                doctest.REPORT_NDIFF)),
                ))
