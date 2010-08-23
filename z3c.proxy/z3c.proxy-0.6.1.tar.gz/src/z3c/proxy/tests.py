###############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""
$Id: tests.py 115867 2010-08-23 06:16:25Z icemac $
"""
__docformat__ = 'restructuredtext'

from z3c.proxy import testing
from zope.app.testing.placelesssetup import setUp
from zope.app.testing.placelesssetup import tearDown
from zope.container.sample import SampleContainer
import doctest
import unittest


class SampleContainerTest(testing.BaseTestIContainerLocationProxy):
    """Base container test sample."""

    def getTestInterface(self):
        return testing.ISampleContainerProxy

    def getTestClass(self):
        return testing.SampleContainerProxy

    def makeTestObject(self):
        obj = SampleContainer()
        return testing.SampleContainerProxy(obj)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown),
        unittest.makeSuite(SampleContainerTest),
        ))

if __name__ == '__main__': unittest.main(SampleContainerTest)
