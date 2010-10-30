# -*- coding: iso-8859-15 -*-

################################################################
# SRMedia
#
# (C) 2006 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

import unittest

try:
    from Products.PloneTestCase import PloneTestCase
    PloneTestCase.installProduct('Five')
    PloneTestCase.installProduct('CMFPlone')
    PloneTestCase.installProduct('TextIndexNG3')

    # setup a new Plohn site    
    PloneTestCase.setupPloneSite(products=('TextIndexNG3', ))
    PTC = PloneTestCase.PloneTestCase
    _PLONE_INSTALLED = True
except ImportError:
    PTC = object
    _PLONE_INSTALLED = False


class PloneTests(PTC):

    def afterSetUp(self):
        membership = self.portal.portal_membership
        membership.addMember('god', 'god', ('Manager',), ())

        self.login('god')
        self.portal.txng_convert_indexes()

    def testSetup(self):
        c = self.portal.portal_catalog
        indexes = c.Indexes
        self.assertEqual(indexes['SearchableText'].meta_type, 'TextIndexNG3')
        self.assertEqual(indexes['Title'].meta_type, 'TextIndexNG3')


def test_suite():
    s = unittest.TestSuite()
    if _PLONE_INSTALLED:
        s.addTest(unittest.makeSuite(PloneTests))
    else:
        print 'Skipped Plone setup tests.'
    return s
