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

$Id: test_field.py 119916 2011-01-25 16:46:10Z faassen $
"""
__docformat__ = "reStructuredText"

import sys

import unittest, doctest


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../field.py'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
