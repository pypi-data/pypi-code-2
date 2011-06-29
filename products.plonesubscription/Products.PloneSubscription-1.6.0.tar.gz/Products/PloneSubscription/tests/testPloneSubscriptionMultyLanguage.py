# -*- coding: utf-8 -*-
## PloneSubscription with LinguaPlone
## Copyright (C) 2007 Ingeniweb
## Copyright (C)2006 redCor AG www.redcor.ch

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""
This module implements unit test for PloneSubscription with Linguaplone installed
"""
__version__ = "$Revision: 20968 $"
# $Source$
# $Id: testPloneSubscriptionMultyLanguage.py 227919 2010-12-01 11:43:20Z glenfant $
__docformat__ = 'restructuredtext'


"""
    test plone subscription together with LinguaPlone
    if LinguaPlone can not be loaded, do nothin at all
"""
if __name__ == '__main__':
    import os, sys
    execfile( os.path.join( sys.path[0], 'framework.py' ) )

try:
    from common import *
    import Products.LinguaPlone
    ZopeTestCase.installProduct('LinguaPlone')
    ZopeTestCase.installProduct('PloneLanguageTool')
    HASLINGUAPLONE = 1
except:
    HASLINGUAPLONE = 0
    print 'LinguaPlone needed to run this set of tests'

if HASLINGUAPLONE:
    from Products.CMFCore.utils import getToolByName
    from Products.CMFCore.utils import _checkPermission as checkPerm
    from Products.CMFCore  import permissions as CMFCorePermissions
    from Products.PloneSubscription import SubscriptionPermissions
    from Products.PloneSubscription.config import *
    from DateTime import DateTime
    class TestPloneSubscription(PloneSubscriptionTestCase.PloneSubscriptionTestCase):
        # Subscriptions tool tests
    
        def beforeTearDown(self):
            pass
    
        def afterSetUp( self ):
            # must be able to create
            portal = self.portal
            self.portal.portal_quickinstaller.installProduct( 'PloneLanguageTool' )
            assert 'portal_languages' in portal.objectIds()
            self.portal.portal_quickinstaller.installProduct( 'LinguaPlone' )
            assert 'LinguaPlone' in portal.portal_skins.objectIds()
    
        def testAddPortalSubscriptionCatalog(self):
            """Test adding of subscription_catalog"""
            self.failUnless('subscription_catalog' in self.portal.objectIds(),
                            "subscription_catalog was not installed")
    
    
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestPloneSubscription))
        return suite
    
    if __name__ == '__main__':
        framework()
