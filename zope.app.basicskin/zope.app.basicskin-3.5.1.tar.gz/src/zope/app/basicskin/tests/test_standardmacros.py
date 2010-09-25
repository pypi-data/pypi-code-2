##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Basic skin standard macros

$Id: test_standardmacros.py 106671 2009-12-16 22:56:40Z hannosch $
"""
import unittest

from zope.component import getGlobalSiteManager
from zope.component.testing import PlacelessSetup
from zope.interface import implements, Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from zope.app.basicskin.standardmacros import Macros


class ViewWithMacros(object):
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pass

    def __getitem__(self, key):
        return self.pages[key]

    pages = {}

class I(Interface): pass

class C(object):
    implements(I)

class page1(ViewWithMacros):
    pages = {'foo':'page1_foo',
             'bar':'page1_bar'}

class collides_with_page1(ViewWithMacros):
    pages = {'foo':'collides_with_page1_foo',
             'baz':'collides_with_page1_baz'}

class works_with_page1(ViewWithMacros):
    pages = {'fish':'works_with_page1_fish',
             'tree':'works_with_page1_tree'}

def createMacrosInstance(pages):

    class T(Macros):
        aliases = {'afoo': 'foo', 'abar': 'bar'}

        def __init__(self, context, request):
            self.context = context
            self.request = request
        macro_pages = pages
    return T(C(), TestRequest())


def browserView(for_, name, factory):
    gsm = getGlobalSiteManager()
    for_ = (for_, ) + (IDefaultBrowserLayer,)
    gsm.registerAdapter(factory, for_, Interface, name, event=False)


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        browserView(I, 'page1', page1)
        browserView(I, 'collides_with_page1', collides_with_page1)
        browserView(I, 'works_with_page1',  works_with_page1)

    def testSinglePage(self):
        macros = createMacrosInstance(('page1',))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertRaises(KeyError, macros.__getitem__, 'fish')

    def testConcordentPages(self):
        macros = createMacrosInstance(('page1', 'works_with_page1'))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['fish'], 'works_with_page1_fish')
        self.assertEqual(macros['tree'], 'works_with_page1_tree')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')

    def testConflictingPages(self):
        macros = createMacrosInstance(('page1', 'collides_with_page1'))
        self.assertEqual(macros['foo'], 'page1_foo')
        self.assertEqual(macros['bar'], 'page1_bar')
        self.assertEqual(macros['baz'], 'collides_with_page1_baz')
        self.assertRaises(KeyError, macros.__getitem__, 'pants')

    def testMacroAliases(self):
        macros = createMacrosInstance(('page1', 'collides_with_page1'))
        self.assertEqual(macros['afoo'], 'page1_foo')
        self.assertEqual(macros['abar'], 'page1_bar')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
