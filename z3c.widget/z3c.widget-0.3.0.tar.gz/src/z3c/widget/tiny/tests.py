##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""HTML-Editor Widget unittests."""

from zope.app.testing import setup
import doctest


def setUp(test):
    setup.placefulSetUp()


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return doctest.DocTestSuite(
        'z3c.widget.tiny.widget',
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
