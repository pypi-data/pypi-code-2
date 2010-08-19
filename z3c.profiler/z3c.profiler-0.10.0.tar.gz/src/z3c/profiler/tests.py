##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""z3c.profiler Test Module"""

from z3c.profiler import testing
import doctest
import unittest


def test_suite():
    suites = []
    append = suites.append
    suite = unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
    suite.layer = testing.TestLayer
    append(suite)
    return unittest.TestSuite(suites)
