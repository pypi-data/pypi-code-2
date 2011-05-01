##############################################################################
#
# Copyright (c) 2004-2006 CompositePack Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: test_tool.py 238387 2011-04-30 19:58:15Z hathawsh $
"""

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Load fixture
from Testing import ZopeTestCase

from Products.CompositePack.tests import CompositePackTestCase

from Products.CompositePack.ViewletRegistry import DEFAULT
from Products.CompositePack.exceptions import CompositePackError

from Products.CompositePack.config import get_ATCT_TYPES

V0D = 'V0D'
V0D_TITLE = 'V0D_TITLE'
V1D = 'V1D'
V1D_TITLE = 'V1D_TITLE'
V2D = 'V2D'
V2D_TITLE = 'V2D_TITLE'
V0 = 'V0'
V0_TITLE = 'V0_TITLE'
V1 = 'V1'
V1_TITLE = 'V1_TITLE'
V2 = 'V2'
V2_TITLE = 'V2_TITLE'
V00 = 'V00'
V00_TITLE = 'V00_TITLE'
V11 = 'V11'
V11_TITLE = 'V11_TITLE'
V22 = 'V22'
V22_TITLE = 'V22_TITLE'

class ToolTest(CompositePackTestCase.CompositePackTestCase):

    def afterSetUp(self):
        CompositePackTestCase.CompositePackTestCase.afterSetUp(self)
        self.TEST_TYPE_1 = self.EVENT_TYPE
        self.TEST_TYPE_2 = self.FILE_TYPE
        self.TEST_TYPE_3 = self.FAVORITE_TYPE
        ct = self.composite_tool
        ct.registerAsComposable(self.TEST_TYPE_3)
        self.v0 = ct.registerViewlet(V0, V0_TITLE, V0)
        self.v1 = ct.registerViewlet(V1, V1_TITLE, V1)
        self.v2 = ct.registerViewlet(V2, V2_TITLE, V2)
        self.v00 = ct.registerViewlet(V00, V00_TITLE, V00)
        self.v11 = ct.registerViewlet(V11, V11_TITLE, V11)
        self.v22 = ct.registerViewlet(V22, V22_TITLE, V22)
        self.v0d = ct.registerViewlet(V0D, V0D_TITLE, V0D)
        self.v1d = ct.registerViewlet(V1D, V1D_TITLE, V1D)
        self.v2d = ct.registerViewlet(V2D, V2D_TITLE, V2D)

    def testRegisterForType1(self):
        ct = self.composite_tool
        ct.setDefaultViewlets([V0, V00, V0D], V0D) 
        ct.setViewletsForType(self.TEST_TYPE_1, [V1, V11, V1D], V1D) 
        ct.setViewletsForType(self.TEST_TYPE_2, [V2, V22, V2D], V2D) 
        RES1 =  {'default': {'id': V1D,
                             'title': V1D_TITLE,
                             'viewlet': self.v1d},
                 'viewlets': [{'id': V1,
                               'title': V1_TITLE,
                               'viewlet': self.v1},
                              {'id': V11,
                               'title': V11_TITLE,
                               'viewlet': self.v11}]}
        RES2 =  {'default': {'id': V2D,
                             'title': V2D_TITLE,
                             'viewlet': self.v2d},
                 'viewlets': [{'id': V22,
                               'title': V22_TITLE,
                               'viewlet': self.v22},
                              {'id': V2,
                               'title': V2_TITLE,
                               'viewlet': self.v2}]}
        RES0 =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V0,
                               'title': V0_TITLE,
                               'viewlet': self.v0},
                              {'id': V00,
                               'title': V00_TITLE,
                               'viewlet': self.v00}]}
        self.assertEquals(RES1, ct.getViewletsForType(self.TEST_TYPE_1))
        self.assertEquals(RES2, ct.getViewletsForType(self.TEST_TYPE_2))
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_3))

    def testRegisterForType2(self):
        ct = self.composite_tool
        ct.setDefaultViewlets([V0, V00, V0D], V0D) 
        ct.setViewletsForType(self.TEST_TYPE_1, [V1, V11, V0D], DEFAULT) 
        ct.setViewletsForType(self.TEST_TYPE_2, (DEFAULT,), V0D) 
        ct.setViewletsForType(self.TEST_TYPE_3, (DEFAULT,), DEFAULT) 
        RES1 =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V1,
                               'title': V1_TITLE,
                               'viewlet': self.v1},
                              {'id': V11,
                               'title': V11_TITLE,
                               'viewlet': self.v11}]}
        RES0 =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V0,
                               'title': V0_TITLE,
                               'viewlet': self.v0},
                              {'id': V00,
                               'title': V00_TITLE,
                               'viewlet': self.v00}]}

        self.assertEquals(RES1, ct.getViewletsForType(self.TEST_TYPE_1))
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_2))
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_3))

    def testRegisterForType3(self):
        ct = self.composite_tool
        ct.setDefaultViewlets([V0, V0D], V0D) 
        ct.setViewletsForType(self.TEST_TYPE_1, [V1, V11, V0D], DEFAULT) 
        ct.setViewletsForType(self.TEST_TYPE_2, (DEFAULT,), V0D) 
        ct.setViewletsForType(self.TEST_TYPE_3, (DEFAULT,), DEFAULT) 
        RES1 =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V1,
                               'title': V1_TITLE,
                               'viewlet': self.v1},
                              {'id': V11,
                               'title': V11_TITLE,
                               'viewlet': self.v11}]}
        RES0 =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V0,
                               'title': V0_TITLE,
                               'viewlet': self.v0}]}

        self.assertEquals(RES1, ct.getViewletsForType(self.TEST_TYPE_1))
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_2))
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_3))
        
        # check that changing default setup does propagate to types using default setup
        ct.setDefaultViewlets([V0, V00, V0D], V0D) 
        RES0AFTER =  {'default': {'id': V0D,
                             'title': V0D_TITLE,
                             'viewlet': self.v0d},
                 'viewlets': [{'id': V0,
                               'title': V0_TITLE,
                               'viewlet': self.v0},
                              {'id': V00,
                               'title': V00_TITLE,
                               'viewlet': self.v00}]}
        self.assertEquals(RES0AFTER, ct.getViewletsForType(self.TEST_TYPE_2))
        self.assertEquals(RES0AFTER, ct.getViewletsForType(self.TEST_TYPE_3))

    def testRegisterForType4(self):
        ct = self.composite_tool
        ct.setDefaultViewlets([V0, V00, V0D], V0D) 
        ct.setViewletsForType(self.TEST_TYPE_2, (DEFAULT,), V00) 
        RES0 =  {'default': {'id': V00,
                             'title': V00_TITLE,
                             'viewlet': self.v00},
                 'viewlets': [{'id': V0,
                               'title': V0_TITLE,
                               'viewlet': self.v0},
                              {'id': V0D,
                               'title': V0D_TITLE,
                               'viewlet': self.v0d}]}
        self.assertEquals(RES0, ct.getViewletsForType(self.TEST_TYPE_2))
        
        # check that changing default setup does propagate to types using default setup
        ct.setDefaultViewlets([V0, V0D], V0D) 
        self.assertRaises(CompositePackError, ct.getDefaultViewletForType, self.TEST_TYPE_2)

def test_suite():
    import unittest
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ToolTest))
    return suite

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
