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
"""
$Id: __init__.py 97 2007-03-29 22:58:27Z rineichen $
"""

import unittest
from zope.app.testing import functional
import z3c.testing

from zam.api.interfaces import IBaseRegistryPlugin
from zamplugin.navigation import plugin

functional.defineLayer('TestLayer', 'ftesting.zcml')


class TestNavigationPlugin(z3c.testing.InterfaceBaseTest):

    def getTestInterface(self):
        return IBaseRegistryPlugin

    def getTestClass(self):
        return plugin.NavigationPlugin


def test_suite():
    suite = unittest.TestSuite()
    s = functional.FunctionalDocFileSuite('README.txt')
    s.layer = TestLayer
    suite.addTest(s)
    suite.addTest(unittest.makeSuite(TestNavigationPlugin))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
