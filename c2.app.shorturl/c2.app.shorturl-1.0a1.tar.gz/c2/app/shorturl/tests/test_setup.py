#!/usr/bin/env python
# encoding: utf-8
"""
test_setup.py

Created by Manabu Terada on 2010-08-03.
Copyright (c) 2010 CMScom. All rights reserved.
"""

from Products.CMFCore.utils import getToolByName

import c2.app.shorturl
import base

class TestInstall(base.BaseTestCase):
    """ Install basic test """ 
    def afterSetUp(self):
        pass

    def testQuickInstall(self):
        qi = self.portal.portal_quickinstaller
        self.failUnless('c2.app.shorturl' in (p['id'] for p in qi.listInstallableProducts()))
        qi.installProduct('c2.app.shorturl')
        self.failUnless(qi.isProductInstalled('c2.app.shorturl'))
    
# class TestSkinInstall(base.BaseTestCase):
#     """  """
#     def afterSetUp(self):
#         qi = self.portal.portal_quickinstaller
#         qi.installProduct('c2.app.shorturl')
# 
#     def testSkinLayersInstalled(self):
#         self.skins = self.portal.portal_skins
#         # print self.skins.objectIds()
#         self.failUnless('shorturl' in self.skins.objectIds())
#         self.assertEqual(len(self.skins.shorturl.objectIds()), 1)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstall))
    # suite.addTest(makeSuite(TestSkinInstall))
    return suite
