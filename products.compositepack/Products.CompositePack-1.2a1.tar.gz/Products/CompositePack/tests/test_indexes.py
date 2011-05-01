##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: test_composable.py 11303 2005-08-23 16:38:33Z godchap $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.CompositePack.tests import CompositePackTestCase

from Products.CMFCore.utils import getToolByName

class ComposableTest(CompositePackTestCase.CompositePackTestCase):

    def afterSetUp(self):
        CompositePackTestCase.CompositePackTestCase.afterSetUp(self)
        self.setRoles('Manager')
        self.ct = getToolByName(self.portal, 'portal_catalog')

    def beforeTearDown(self):
        CompositePackTestCase.CompositePackTestCase.beforeTearDown(self)


    def test_no_container_indexed(self):
        #check catalog works ok
        before = len(self.ct(portal_type=self.FILE_TYPE))
        self.folder.invokeFactory(self.FILE_TYPE, 'test_file')
        self.assertEqual(before+1, len(self.ct(portal_type=self.FILE_TYPE)))
        #check none of the software (viewlets, layouts,...) has been indexed
        self.failIf(len(self.ct(portal_type="CompositePack Layout Container")))
        self.failIf(len(self.ct(portal_type="CompositePack Viewlet Container")))

    def test_index_navigation_page(self):
        before = len(self.ct())
        self.portal.invokeFactory('Navigation Page', 'page')
        page = self.portal._getOb('page')
        # 1 = page (no filled_slots or composite elements)
        self.assertEquals(len(self.ct()), before+1)

    def test_index_layout(self):
        before = len(self.ct())
        ct = self.composite_tool
        layout = ct.registerLayout('test_layout', 'Test', 'test_layout')
        self.assertEquals(len(self.ct()), before)

    def test_index_viewlet(self):
        before = len(self.ct())
        ct = self.composite_tool
        layout = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        self.assertEquals(len(self.ct()), before)


def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ComposableTest))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
