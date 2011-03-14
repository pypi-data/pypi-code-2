# -*- coding: utf-8 -*-
'''
Created on 19.11.2010

@author: cykooz
'''

import unittest
import doctest

from zope.app.testing import setup
from zope.interface.verify import verifyClass
from zope.component import provideAdapter
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore


from interfaces import ITitle
import adapters


class InterfacesTest(unittest.TestCase):
    
    def testClassName2TitleAdapterInterface(self):
        self.assertTrue(verifyClass(ITitle, adapters.ClassName2TitleAdapter))

    def testContained2TitleAdapterInterface(self):
        self.assertTrue(verifyClass(ITitle, adapters.Contained2TitleAdapter))

    def testZDC2TitleAdapterInterface(self):
        self.assertTrue(verifyClass(ITitle, adapters.ZDC2TitleAdapter))


def setUp(test):
    site = setup.placefulSetUp(site=True)
    provideAdapter(ZDCAnnotatableAdapter, provides=IWriteZopeDublinCore)
    test.globs['rootFolder'] = site

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite([
            doctest.DocFileSuite(
                'title.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            unittest.makeSuite(InterfacesTest),
            ])
