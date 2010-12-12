# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Tests for the Book Documentation Module

$Id: tests.py 115615 2010-08-10 06:58:11Z icemac $
"""
__docformat__ = "reStructuredText"

from zope.app.testing import placelesssetup, setup, ztapi
from zope.copypastemove import PrincipalClipboard
import doctest
import unittest
import zope.component
import zope.principalannotation.interfaces
import zope.principalannotation.utility


def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpTraversal()

    zope.component.provideUtility(
        zope.principalannotation.utility.PrincipalAnnotationUtility(),
        zope.principalannotation.interfaces.IPrincipalAnnotationUtility)
    zope.component.provideAdapter(
        zope.principalannotation.utility.annotations,
        adapts=(None,))
    zope.component.provideAdapter(
        PrincipalClipboard)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(default='test_suite')
