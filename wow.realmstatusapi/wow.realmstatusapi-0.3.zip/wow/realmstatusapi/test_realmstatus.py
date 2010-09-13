# -*- coding: utf-8 -*-
"""
Doctest runner for 'activity_api'
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    pass

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp,
                optionflags=optionflags,
                ),
            ))
    return suite

def mocked_get_realm_status(self, name):

    if name == "Azshara":
       return "Realm Up"
    else:
        return "Realm not found"

def mocked_get_realm_type(self, name):

    if name == "Azshara":
        return "PvP"
    else:
        return "Realm not found"

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
