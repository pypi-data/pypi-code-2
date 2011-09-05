##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
from z3c.hashedresource import hash, interfaces, testing
import os
import unittest
import zope.app.publisher.browser.directoryresource
import zope.app.publisher.testing
import zope.app.testing.functional


class HashingURLTest(testing.FunctionalTestCase):

    def test_directory_url_should_contain_hash(self):
        self.assertMatches(
            'http://127.0.0.1/\+\+noop\+\+[^/]*/@@/%s' % self.dirname, self.directory())

    def test_file_url_should_contain_hash(self):
        file = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(testing.fixture, 'test.txt'), testing.checker, 'test.txt')(self.request)
        self.assertMatches(
            'http://127.0.0.1/\+\+noop\+\+[^/]*/@@/test.txt', file())

    def test_different_files_hashes_should_differ(self):
        file1 = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(testing.fixture, 'test.txt'), testing.checker, 'test.txt')(self.request)
        file2 = zope.app.publisher.browser.fileresource.FileResourceFactory(
            os.path.join(testing.fixture, 'test.pt'), testing.checker, 'test.txt')(self.request)
        self.assertNotEqual(self._hash(file1()), self._hash(file2()))

    def test_directory_contents_changed_hash_should_change(self):
        before = self._hash(self.directory())
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = self._hash(self.directory())
        self.assertNotEqual(before, after)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HashingURLTest))
    return suite
