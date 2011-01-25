##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""LDAPAdapter tests

$Id: test_ldapadapter.py 119916 2011-01-25 16:46:10Z faassen $
"""
__docformat__ = "reStructuredText"
import sys
import unittest, doctest
from pprint import pprint


def setUp(test):
    import fakeldap
    if sys.modules.has_key('_ldap'):
        test.old_uldap = sys.modules['_ldap']
        del sys.modules['_ldap']
    else:
        test.old_uldap = None
    if sys.modules.has_key('ldap'):
        test.old_ldap = sys.modules['ldap']
        del sys.modules['ldap']
    else:
        test.old_ldap = None
    sys.modules['ldap'] = fakeldap
    #import ldap

def tearDown(test):
    del sys.modules['ldap']
    if test.old_uldap is not None:
        sys.modules['_ldap'] = test.old_uldap
    if test.old_ldap is not None:
        sys.modules['ldap'] = test.old_ldap
    import ldap

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../README.txt',
                             setUp=setUp, tearDown=tearDown,
                             globs={'pprint': pprint},
                             optionflags=doctest.NORMALIZE_WHITESPACE),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
