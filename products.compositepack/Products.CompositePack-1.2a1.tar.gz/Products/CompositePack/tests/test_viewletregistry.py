##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: test_viewletregistry.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.CompositePack.tests import CompositePackTestCase

from Products.CMFCore.utils import getToolByName

from Products.kupu.plone.plonelibrarytool import PloneKupuLibraryTool

KUPU_TOOL_ID = PloneKupuLibraryTool.id

from Products.CompositePack.config import COMPOSABLE
from Products.CompositePack.exceptions import CompositePackError

class ViewletRegistryTest(CompositePackTestCase.CompositePackTestCase):

    def afterSetUp(self):
        CompositePackTestCase.CompositePackTestCase.afterSetUp(self)
        self.TEST_TYPE = self.FILE_TYPE
        self.TEST_TYPE_2 = self.EVENT_TYPE
        self.TEST_TYPES = (self.TEST_TYPE, self.TEST_TYPE_2)
        self.kupu_tool = getToolByName(self.portal, KUPU_TOOL_ID)
        ct = self.composite_tool
        ct.unregisterAsComposable(self.TEST_TYPE)
        ct.unregisterAsComposable(self.TEST_TYPE_2)

    def testGetDefaultWhenNoDefault(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        self.assertEquals(ct.getDefaultViewletForType(self.TEST_TYPE), ct.getDefaultViewletForDefaultSetup())

    def testRegisterType(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        self.failUnless(ct.isComposable(self.TEST_TYPE))
        self.failUnless(self.TEST_TYPE in ct.getRegisteredComposables())
        self.failUnless(self.TEST_TYPE in self.kupu_tool.getPortalTypesForResourceType(COMPOSABLE)) 

    def testUnregisterType(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        ct.unregisterAsComposable(self.TEST_TYPE)
        self.failIf(ct.isComposable(self.TEST_TYPE))
        self.failIf(self.TEST_TYPE in self.kupu_tool.getPortalTypesForResourceType(COMPOSABLE)) 
        
    def testRegisterTypes(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPES)
        for test_type in self.TEST_TYPES:
            self.failUnless(ct.isComposable(test_type))
            self.failUnless(test_type in ct.getRegisteredComposables())
            self.failUnless(test_type in self.kupu_tool.getPortalTypesForResourceType(COMPOSABLE)) 

    def testUnregisterTypes(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPES)
        ct.unregisterAsComposable(self.TEST_TYPES)
        for test_type in self.TEST_TYPES:
            self.failIf(ct.isComposable(test_type))
            self.failIf(test_type in self.kupu_tool.getPortalTypesForResourceType(COMPOSABLE)) 
        
    def testRegisterTypeTwice(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        self.assertRaises(CompositePackError, ct.registerAsComposable, self.TEST_TYPE)

    def testRegisterViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        self.assertEquals(viewlet, ct.getViewletById('test_viewlet'))

    def testUnregisterViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        ct.unregisterViewlet('test_viewlet')
        self.assertEquals(None, ct.getViewletById('test_viewlet'))
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        ct.unregisterViewlet('test_viewlet')
        self.failIf('test_viewlet' in [viewlet.getId() for viewlet in ct.getRegisteredViewletsForType(self.TEST_TYPE)])

    def testRegisterViewletForType(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        self.failUnless(viewlet in ct.getRegisteredViewletsForType(self.TEST_TYPE))
        #first viewlet is setup as default
        self.failUnless(viewlet.isDefaultForType(self.TEST_TYPE))
        #it can be registered twice !
        viewlet.registerForType(self.TEST_TYPE)
        self.failUnless(viewlet.isRegisteredForType(self.TEST_TYPE))
        self.failUnless(viewlet in ct.getRegisteredViewletsForType(self.TEST_TYPE))

    def testUnregisterViewletForType(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        self.assertRaises(CompositePackError, viewlet.unregisterForType, self.TEST_TYPE)
        viewlet.unregisterForType(self.TEST_TYPE, force=True)
        self.failIf(viewlet.isRegisteredForType(self.TEST_TYPE))
        self.failIf(viewlet in ct.getRegisteredViewletsForType(self.TEST_TYPE))

    def testRegisterDefaultViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        viewlet.setDefaultForType(self.TEST_TYPE)
        self.assertEquals(viewlet, ct.getDefaultViewletForType(self.TEST_TYPE))
        self.failUnless(viewlet.isDefaultForType(self.TEST_TYPE))

    def testUnRegisterDefaultViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        viewlet.setDefaultForType(self.TEST_TYPE)
        self.assertRaises(CompositePackError, viewlet.unregisterForType, self.TEST_TYPE)

    def testClearDefaultViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        viewlet.setDefaultForType(self.TEST_TYPE)
        viewlet.clearDefaultForType(self.TEST_TYPE)
        self.assertRaises(CompositePackError, ct.getDefaultViewletForType, self.TEST_TYPE)
        self.failUnless(ct.noDefaultViewletForType(self.TEST_TYPE))

    def testForceUnRegisterDefaultViewlet(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForType(self.TEST_TYPE)
        viewlet.setDefaultForType(self.TEST_TYPE)
        viewlet.unregisterForType(self.TEST_TYPE, force=True)
        self.assertRaises(CompositePackError, ct.getDefaultViewletForType, self.TEST_TYPE)

    def testDefaultViewletNotRegistered(self):
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE)
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.setDefaultForDefaultSetup()
        self.assertEquals(ct.getDefaultViewletForType(self.TEST_TYPE), ct.getDefaultViewletForDefaultSetup())

    def testRegisterViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        self.failUnless(viewlet in ct.getRegisteredViewletsForDefaultSetup())
        #it can be registered twice !
        viewlet.registerForDefaultSetup()
        self.failUnless(viewlet.isRegisteredForDefaultSetup())
        self.failIf(viewlet.isDefaultForDefaultSetup())
        self.failUnless(viewlet in ct.getRegisteredViewletsForDefaultSetup())

    def testUnregisterViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.unregisterForDefaultSetup()
        self.failIf(viewlet.isRegisteredForDefaultSetup())
        self.failIf(viewlet in ct.getRegisteredViewletsForDefaultSetup())

    def testRegisterDefaultViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.setDefaultForDefaultSetup()
        self.assertEquals(viewlet, ct.getDefaultViewletForDefaultSetup())
        self.failUnless(viewlet.isDefaultForDefaultSetup())

    def testUnRegisterDefaultViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.setDefaultForDefaultSetup()
        self.assertRaises(CompositePackError, viewlet.unregisterForDefaultSetup)

    def testClearDefaultViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.setDefaultForDefaultSetup()
        viewlet.clearDefaultForDefaultSetup()
        self.assertRaises(CompositePackError, ct.getDefaultViewletForDefaultSetup)
        self.failUnless(ct.noDefaultViewletForDefaultSetup())

    def testForceUnRegisterDefaultViewletForDefaultSetup(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        viewlet.registerForDefaultSetup()
        viewlet.setDefaultForDefaultSetup()
        viewlet.unregisterForDefaultSetup(force=True)
        self.assertRaises(CompositePackError, ct.getDefaultViewletForDefaultSetup)

    def testStableUids(self):
        ct = self.composite_tool
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        uid = viewlet.UID()
        ct.unregisterViewlet('test_viewlet')
        viewlet = ct.registerViewlet('test_viewlet', 'Test', 'test_viewlet')
        uid2 = viewlet.UID()
        self.assertEquals(uid, uid2)

    def testUidChangesOnRenameOrCopy(self):
        self.setRoles('Manager')
        # When a viewlet is renamed or copied, the uid changes
        # and is set to the correct stable value for the new name.
        ID1 = 'test_viewlet'
        ID2 = 'new_test_viewlet'

        ct = self.composite_tool
        folder = ct.viewlets
        ct.registerViewlet(ID1, 'Test', ID1)
        v = folder['test_viewlet']
        v.__factory_meta_type__ = v.meta_type

        import transaction
        transaction.commit(1) # Must do this to be allowed to rename.

        folder.manage_renameObject(ID1, ID2)
        viewlet = folder[ID2]
        uid = viewlet.UID()
        viewlet.setStableUID()
        self.assertEquals(uid, viewlet.UID())

        clipdata = folder.manage_copyObjects(ID2)
        pasted = folder.manage_pasteObjects(clipdata)
        new_id = pasted[0]['new_id']
        viewlet2 = folder[new_id]
        uid = viewlet2.UID()
        viewlet2.setStableUID()
        self.assertEquals(uid, viewlet2.UID())

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ViewletRegistryTest))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
