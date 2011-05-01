##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: test_composable.py 18879 2006-02-02 15:27:55Z godchap $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.CMFCore.utils import getToolByName
from Products.CompositePack.tests.CompositeGSTestCase import CompositeGSTestCase
from Products.CompositePack.config import HAS_GS


class ComposableTest(CompositeGSTestCase):

    def afterSetUp(self):
        """ After setup try to get the tool, without it we are helpless """
        CompositeGSTestCase.afterSetUp(self)
        # self.setRoles('Manager')

        self.ct = getToolByName(self.portal, 'composite_tool')
        self.failUnless(self.ct)

    def beforeTearDown(self):
        CompositeGSTestCase.beforeTearDown(self)

    def test_Composites(self):
        """ Here we test if the Composites are set up correctly. We expect
            the Navigation Page content type to be registered and we expect
            it to have multiple layouts (three to be precise). Lastly we
            check the default value
        """
        composites = self.ct.getRegisteredComposites()
        self.failUnless('Navigation Page' in composites)

        layouts = self.ct.getRegisteredLayoutsForType('Navigation Page')
        self.failUnless(len(layouts) == 3 )

        layouts_names = [str(l) for l in layouts]
        self.failUnless(layouts_names == ['<Layout at two_slots>', 
                                          '<Layout at three_slots>', 
                                          '<Layout at two_columns>'])

        default = self.ct.getDefaultLayoutForType('Navigation Page')
        self.failUnless(str(default) == '<Layout at two_columns>')

    def test_Composables(self):
        """ Here we test if the Composables are set up correctly. We
            Expect many Composables to exist (11 to be precise). We
            test the default viewlet for these Composables. At the
            end we test if Image indeed has 4 different viewlet options
        """

        expected = {'File':                    '<Viewlet at title_description_with_link>',
                    'Link':                    '<Viewlet at title_description_with_link>',
                    'Image':                   '<Viewlet at image_viewlet>',
                    'Event':                   '<Viewlet at title_description_with_link>',
                    'Topic':                   '<Viewlet at topic_viewlet>',
                    'Document':                '<Viewlet at title_description_with_link>',
                    'News Item':               '<Viewlet at title_description_with_link>',
                    '(Default Setup)':         '<Viewlet at title_description_with_link>',
                    'CompositePack Titles':    '<Viewlet at title_viewlet>',
                    'CompositePack Portlet':   '<Viewlet at title_description_with_link>',
                    'CompositePack Fragments': '<Viewlet at fragment_viewlet>',}

        composables = self.ct.getRegisteredComposables()
        self.failUnless(len(composables) == 10)

        for composable in composables:
            default = self.ct.getDefaultViewletForType(composable)
            self.failUnless(str(default) == expected[composable])

        viewlets = self.ct.getRegisteredViewletsForType('Image')
        self.failUnless(len(viewlets) == 4)

        viewlets_names = [str(v) for v in viewlets]
        self.failUnless(viewlets_names == ['<Viewlet at image_viewlet>', 
                                           '<Viewlet at link_viewlet>', 
                                           '<Viewlet at image_title_viewlet>', 
                                           '<Viewlet at image_caption_viewlet>'])

    def test_viewlets(self):
        """ This tests the viewlets registered in this tool. Normally 9 
            viewlets are created and we know what to expect as id, title and 
            skin_method for each one of them, so let's be thorough in testing.
        """
        expected = {'title_description_with_link': ['Title with description',
                                                'title_description_with_link'],
                    'link_viewlet': ['Link Only', 'link_viewlet'],
                    'title_viewlet': ['Title', 'title_viewlet'],
                    'fragment_viewlet': ['HTML Fragment', 'fragment_viewlet'],
                    'title_date_viewlet': ['Title and Date', 'title_date_viewlet'],
                    'image_viewlet': ['Image', 'image_viewlet'],
                    'image_title_viewlet': ['Image with title', 
                                            'image_title_viewlet'],
                    'image_caption_viewlet': ['Image with caption', 
                                              'image_caption_viewlet'],
                    'topic_viewlet': ['Topic Listing','topic_viewlet']}

        viewlets = self.ct.getAllViewlets()
        self.failUnless(len(viewlets) == 9)

        for viewlet in viewlets:
            id = viewlet.getId()
            title = viewlet.Title()
            skin = viewlet.getSkinMethod()
            self.failUnless(title == expected[id][0])
            self.failUnless(skin == expected[id][1])

    def test_layouts(self):
        """ This tests the layouts registered in this tool. Normally 3
            layouts are created and we know what to expect as id, title and
            skin_method for each one of them, so let's be thorough in testing.
  
        """
        expected = {'two_slots': ['Two slots', 'two_slots'],
                    'three_slots': ['Three slots', 'three_slots'],
                    'two_columns': ['Two columns', 'two_columns']}

        layouts = self.ct.getAllLayouts()
        self.failUnless(len(layouts) == 3)

        for layout in layouts:
            id = layout.getId()
            title = layout.getRawTitle()
            skin = layout.getSkinMethod()
            self.failUnless(title == expected[id][0])
            self.failUnless(skin == expected[id][1])

    def test_additive_prop(self):
        """ This tests the additive property of the import function.
            When you make local changes, the import function should
            only add and not replace things
        """
        if not HAS_GS:
            return
        # We first make some custom Composite Pack modifications
        self.ct.registerLayout("custom_layout_id", "custom_layout_title", "custom_layout_skin_method")
        self.ct.registerViewlet("custom_viewlet_id", "custom_viewlet_title", "custom_viewlet_skin_method")
        viewlet = self.ct.getViewletById("custom_viewlet_id")
        self.ct.registerViewletForType(viewlet, "custom_composable_id")
        layout = self.ct.getLayoutById("custom_layout_id")
        self.ct.registerLayoutForType(layout, "custom_composite_id")

        typetool = getToolByName(self.ct, 'portal_types')
        from Products.CMFCore.TypesTool import FactoryTypeInformation
        fti = FactoryTypeInformation(id="custom_composable_id")
        typetool._setObject(fti.id, fti)

        # Now we use Generic Setup to import the default
        self.gs.setImportContext('profile-CompositePack:default')
        self.gs.runAllImportSteps()

        # Let's get the Layouts
        layouts = self.ct.getAllLayouts()
        layouts_names = [str(l) for l in layouts]

        layouts_for_custom = self.ct.getRegisteredLayoutsForType("custom_composite_id")
        layouts_for_custom_names = [str(lf) for lf in layouts_for_custom]

        # And let's get the Viewlets
        viewlets = self.ct.getAllViewlets()
        viewlets_names = [str(v) for v in viewlets]

        viewlets_for_custom = self.ct.getRegisteredViewletsForType("custom_composable_id")
        viewlets_for_custom_names = [str(lv) for lv in viewlets_for_custom]


        # Now, let us check if our customization still exists or if the import
        # replaced it all.
        self.failUnless('<Layout at custom_layout_id>' in layouts_names, 
                        "Custom layout was overwritten at import")
        self.failUnless('<Viewlet at custom_viewlet_id>' in viewlets_names,
                        "Custom viewlet was overwritten at import")
        self.failUnless('<Viewlet at custom_viewlet_id>' in viewlets_for_custom_names,
                        "Custom viewlet for composable overwritten at import")
        self.failUnless('<Layout at custom_layout_id>' in layouts_for_custom_names,
                        "Custom layout for composite overwritten at import")

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ComposableTest))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
