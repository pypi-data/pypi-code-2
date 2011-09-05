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
from z3c.hashedresource import hash, testing
import os
import unittest
import zope.component


ProductionModeLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(testing.__file__), 'ftesting.zcml'),
    __name__, 'ProductionModeLayer', allow_teardown=True)


class CachingContentsHashTest(testing.FunctionalTestCase):

    layer = ProductionModeLayer

    def test_production_mode_hash_should_not_change(self):
        zope.component.provideAdapter(
            hash.CachingContentsHash,
            (zope.app.publisher.browser.directoryresource.DirectoryResource,))

        before = self._hash(self.directory())
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('foo')
        after = self._hash(self.directory())
        self.assertEqual(before, after)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CachingContentsHashTest))
    return suite
