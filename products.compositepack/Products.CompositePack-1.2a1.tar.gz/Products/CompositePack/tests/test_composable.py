##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: test_composable.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.CompositePack.tests import CompositePackTestCase

from Products.CompositePack.config import PLONE21


from cStringIO import StringIO
from cPickle import load, dump
from AccessControl import Unauthorized
from Acquisition import aq_base, aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import ZCMLLayer

def setup_local_tools(portal, out):
    from Products.Archetypes import ArchetypeTool
    from Products.Archetypes.ReferenceEngine import ReferenceCatalog
    from Products.Archetypes.UIDCatalog import UIDCatalog
    from Products.Archetypes.setuphandlers import install_uidcatalog
    from Products.Archetypes.setuphandlers import install_referenceCatalog
    public = portal.public_website
    # Hack around acquisition so that tools get setup correctly
    public = aq_base(public).__of__(aq_parent(portal))
    public.archetype_tool = ArchetypeTool()
    public.reference_catalog = ReferenceCatalog(id='reference_catalog')
    public.uid_catalog = UIDCatalog(id='uid_catalog')
    install_uidcatalog(out, public)
    install_referenceCatalog(out, public)


class ComposableTest(CompositePackTestCase.CompositePackTestCase):

    def afterSetUp(self):
        CompositePackTestCase.CompositePackTestCase.afterSetUp(self)
        self.setRoles('Manager')
        self.portal._v_skindata = None
        self.portal.setupCurrentSkin()
        self.ct = getToolByName(self.portal, 'portal_catalog')

    def beforeTearDown(self):
        CompositePackTestCase.CompositePackTestCase.beforeTearDown(self)

    def test_utf8SearchableText(self):
        # verify that change in SearchablText
        self.portal.invokeFactory('Navigation Page', 'nav')
        nav = self.portal.nav
        utf8Txt = 'UTF8 ÅÄÖ'
        nav.setTitle( utf8Txt)
        nav.setDescription( 'description' )
        self.failUnlessEqual( nav.SearchableText(), utf8Txt+' description')
        
    def test_navigation_page_rename(self):
        targets = []
        for i in range(0, 4):
            name = 'page%s' % i
            self.portal.invokeFactory('Navigation Page', name)
            targets.append(self.portal[name])
        self.portal.invokeFactory('Navigation Page', 'page')
        page = self.portal.page

        # Change to two slots layout
        page.cp_container.setLayout('two_slots')
        page.cp_container.getLayout()
        page.cp_container.generateSlots()
        slots = page.cp_container.filled_slots
        self.failUnless('first' in slots.objectIds())
        self.failUnless('second' in slots.objectIds())

        # Now to populate the slots
        # Should be able to call invokeFactory from the slot.
        slots.first.invokeFactory('CompositePack Element',
                                  '0', target=[targets[0].UID()])
        slots.first.invokeFactory('CompositePack Element',
                                  '1', target=[targets[1].UID()])
        slots.second.invokeFactory('CompositePack Element',
                                   '2', target=[targets[2].UID()])
        slots.second.invokeFactory('CompositePack Element',
                                   '3', target=[targets[3].UID()])

        self.assertEquals(slots.first.objectIds(), ['0', '1'])
        self.assertEquals(slots.second.objectIds(), ['2', '3'])
        self.assertEquals(slots.first['0'].dereference(), targets[0])
        self.assertEquals(slots.second['3'].dereference(), targets[3])

        # Do a subcommit so that rename works
        import transaction
        transaction.commit(1)

        # Rename and make sure references are still there
        self.portal.manage_renameObject('page', 'new_page')
        self.assertEquals(slots.first.objectIds(), ['0', '1'])
        self.assertEquals(slots.second.objectIds(), ['2', '3'])
        self.assertEquals(slots.first['0'].dereference(), targets[0])
        self.assertEquals(slots.second['3'].dereference(), targets[3])

        # Rebuild reference_catalog and make sure references are still there
        self.portal.reference_catalog.manage_rebuildCatalog()
        self.assertEquals(slots.first.objectIds(), ['0', '1'])
        self.assertEquals(slots.second.objectIds(), ['2', '3'])
        self.assertEquals(slots.first['0'].dereference(), targets[0])
        self.assertEquals(slots.second['3'].dereference(), targets[3])


    def test_navigation_page_staging(self):
        self.loginAsPortalOwner()
        # This is a test to demonstrate that CompositePack
        # will keep references on a staging environment using
        # ZopeVersionControl and CMFStaging. They don't use
        # direct copy, but instead make a pickle copy of the
        # object, change the internal state and then do a
        # _setObject on the destination stage.
        cats = (self.portal.portal_catalog,
                self.portal.uid_catalog,
                self.portal.reference_catalog)

        # Create some target objects for our slots
        self.portal.invokeFactory('Folder', 'private')
        private = self.portal.private
        targets = []
        for i in range(0, 4):
            name = 'page%s' % i
            self.portal.invokeFactory('Navigation Page', name)
            targets.append(self.portal[name])
        private.invokeFactory('Navigation Page', 'page')
        page = private.page

        # Create public website local versions of archetypes tools.
        self.portal.invokeFactory('Folder', 'public_website')
        public = self.portal.public_website
        setup_local_tools(self.portal, StringIO())

        pcats = (public.uid_catalog,
                 public.reference_catalog)

        self.failIf(cats[1:] == pcats)

        before = [len(cat()) for cat in cats]
        pbefore = [len(cat()) for cat in pcats]

        # Change to two slots layout
        page.cp_container.setLayout('two_slots')
        page.cp_container.generateSlots()
        slots = page.cp_container.filled_slots
        self.failUnless('first' in slots.objectIds())
        self.failUnless('second' in slots.objectIds())

        # Now to populate the slots
        # Should be able to call invokeFactory from the slot.
        slots.first.invokeFactory('CompositePack Element',
                                  '0', target=[targets[0].UID()])
        slots.first.invokeFactory('CompositePack Element',
                                  '1', target=[targets[1].UID()])
        slots.second.invokeFactory('CompositePack Element',
                                   '2', target=[targets[2].UID()])
        slots.second.invokeFactory('CompositePack Element',
                                   '3', target=[targets[3].UID()])

        # portal_catalog should get +0, uid+8, references+4
        # uid_catalog gets the four elements and the four references
        # reference_catalog gets the four references
        expected = [before[0], before[1]+8, before[2]+4]
        got = [len(cat()) for cat in cats]
        self.assertEquals(got, expected)

        # There should be no changes in the public site catalogs
        pgot = [len(cat()) for cat in pcats]
        self.assertEquals(pgot, pbefore)

        # Copy by pickle
        out = StringIO()
        dump(aq_base(private), out)
        out.seek(0)
        new_obj = load(out)
        public._setObject('private', new_obj)

        # Should have no change from previous counts
        # except for private and page
        expected = [expected[0]+2, expected[1], expected[2]]
        got = [len(cat()) for cat in cats]
        self.assertEquals(got, expected)

        # Finally, the public catalogs should have
        if PLONE21:
            # uid+11 (private has also a UID), references+4
            pexpected = [pbefore[0]+11, pbefore[1]+4]
        else:
            # uid+10, references+4
            pexpected = [pbefore[0]+10, pbefore[1]+4]
        pgot = [len(cat()) for cat in pcats]
        self.assertEquals(pgot, pexpected)
    
    def test_navigation_page_with_private_content(self):
        self.portal.invokeFactory('Navigation Page', 'navpage')
        navpage = self.portal.navpage
        navpage.cp_container.setLayout('two_slots')
        navpage.cp_container.generateSlots()
        slots = navpage.cp_container.filled_slots
        self.portal.invokeFactory('Document', 'page')
        page = self.portal.page
        slots.first.invokeFactory('CompositePack Element',
                                  '0', target=[page.UID()])
        self.setRoles(['Manager'])
        wfTool = getToolByName(self.portal, 'portal_workflow')
        wfTool.doActionFor(page, 'publish')
        wfTool.doActionFor(page, 'retract')
        self.logout()
        # This should not give us any errors now:
        try:
            result = slots.first['0'].renderInline()
        except Unauthorized, e:
            self.fail("Unauthorized error: %s" % str(e))
        # self.assertEqual(slots.first['0'].renderInline(),'')

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ComposableTest))
    suite.layer = ZCMLLayer
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
