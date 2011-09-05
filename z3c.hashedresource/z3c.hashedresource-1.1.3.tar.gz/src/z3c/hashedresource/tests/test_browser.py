#############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""tests

$Id: test_directoryresource.py 95447 2009-01-29 16:28:18Z wosc $
"""
from z3c.hashedresource import interfaces, testing
import unittest
import zope.app.testing.functional
import zope.testbrowser.testing


class BrowserTest(zope.app.testing.functional.FunctionalTestCase):

    layer = testing.HashedResourcesLayer

    def setUp(self):
        super(BrowserTest, self).setUp()
        self.browser = zope.testbrowser.testing.Browser()
        self.directory = zope.component.getAdapter(
            zope.publisher.browser.TestRequest(), name='myresource')

    def test_traverse_atat_by_name(self):
        self.browser.open('http://localhost/@@/myresource/test.txt')
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_atat_by_hash(self):
        hash = str(
            interfaces.IResourceContentsHash(self.directory))
        self.browser.open(
            'http://localhost/++noop++%s/@@/myresource/test.txt' % hash)
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_resource_by_name(self):
        self.browser.open('http://localhost/++resource++myresource/test.txt')
        self.assertEqual('test\ndata\n', self.browser.contents)

    def test_traverse_resource_by_hash(self):
        hash = str(
            interfaces.IResourceContentsHash(self.directory))
        self.browser.open(
            'http://localhost/++noop++%s/++resource++myresource/test.txt' % hash)
        self.assertEqual('test\ndata\n', self.browser.contents)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BrowserTest))
    return suite
