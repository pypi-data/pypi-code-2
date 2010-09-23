##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import os
import unittest
import zope.interface
import zope.component
from zope.testing import doctest
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.container.interfaces import IReadContainer
from zope.app.testing import setup

import z3c.testing
import z3c.json.testing
import z3c.jsonrpc.testing
from z3c.jsonrpc.interfaces import IJSONRPCRequest
from z3c.jsontree import browser
from z3c.template.zcml import TemplateFactory
from z3c.template.interfaces import IContentTemplate
from z3c.jsontree import interfaces
from z3c.jsontree import subitem
from z3c.jsontree.browser import tree


class ResourceStub(object):
    """Resource stub"""
    zope.interface.implements(zope.interface.Interface)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, request):
        self.request = request

    def __call__(self):
        return u'http://icon'

    def url(self):
        return u''


class IconStub(object):
    """Icon stub"""
    zope.interface.implements(zope.interface.Interface)
    zope.component.adapts(zope.interface.Interface, zope.interface.Interface)

    def __init__(self, rname):
        self.rname = rname
        self.alt = u'icon'
        self.width = 16
        self.height = 16

    def __call__(self, context, request):
        self.context = context
        self.request = request
        return self


def setUpAdapters():
    # register icon resource
    zope.component.provideAdapter(ResourceStub,
        name='z3cJSONTreeCollapsedIcon')
    zope.component.provideAdapter(ResourceStub,
        name='z3cJSONTreeExpandedIcon')
    zope.component.provideAdapter(ResourceStub,
        name='z3cJSONTreeStaticIcon')

    # register icon
    zope.component.provideAdapter(IconStub('z3cJSONTreeCollapsedIcon'),
        (zope.interface.Interface, zope.interface.Interface),
        provides=zope.interface.Interface, name='z3cJSONTreeCollapsedIcon')
    zope.component.provideAdapter(IconStub('z3cJSONTreeExpandedIcon'),
        (zope.interface.Interface, zope.interface.Interface),
        provides=zope.interface.Interface, name='z3cJSONTreeExpandedIcon')
    zope.component.provideAdapter(IconStub('z3cJSONTreeStaticIcon'),
        (zope.interface.Interface, zope.interface.Interface),
        provides=zope.interface.Interface, name='z3cJSONTreeStaticIcon')

    # setup adapters
    zope.component.provideAdapter(subitem.NoneTreeItems,
        (zope.interface.Interface, IBrowserRequest, interfaces.ISubItemAware))
    zope.component.provideAdapter(subitem.ContainerTreeItems,
        (IReadContainer, IBrowserRequest, interfaces.ISubItemAware))
    zope.component.provideAdapter(subitem.NoneTreeItems,
        (zope.interface.Interface, IJSONRPCRequest, interfaces.ISubItemAware))
    zope.component.provideAdapter(subitem.ContainerTreeItems,
        (IReadContainer, IJSONRPCRequest, interfaces.ISubItemAware))


class TestSimpleJSONTree(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        setup.placefulSetUp(True)
        # setup adapters
        setUpAdapters()
        # setup json coverters
        z3c.json.testing.setUpJSONConverter()

    def tearDown(test):
        setup.placefulTearDown()

    def getTestInterface(self):
        return interfaces.ISimpleJSONTree

    def getTestClass(self):
        return tree.SimpleJSONTree

    def getTestPos(self):
        return (None, TestRequest())


class TestGenericJSONTree(z3c.testing.InterfaceBaseTest):

    def setUp(test):
        setup.placefulSetUp(True)
        
        # setup adapters
        setUpAdapters()
        # setup json coverters
        z3c.json.testing.setUpJSONConverter()

        # register tree content provider
        zope.component.provideAdapter(tree.TreeProvider, name='tree')
        zope.component.provideAdapter(tree.ULTagProvider, name='ul')
        zope.component.provideAdapter(tree.LITagProvider, name='li')

        # register tree content template
        treeTemplate = os.path.join(os.path.dirname(browser.__file__), 
            'tree.pt')
        factory = TemplateFactory(treeTemplate, 'text/html')
        zope.component.provideAdapter(factory, (zope.interface.Interface,
            zope.interface.Interface), IContentTemplate)

    def tearDown(test):
        setup.placefulTearDown()

    def getTestInterface(self):
        return interfaces.IGenericJSONTree

    def getTestClass(self):
        return tree.GenericJSONTree

    def getTestPos(self):
        return (None, TestRequest())


def setUp(test):
    # setup adapters
    setUpAdapters()
    # setup json coverters
    z3c.json.testing.setUpJSONConverter()
    

def test_suite():
    return unittest.TestSuite((
#        z3c.jsonrpc.testing.FunctionalDocFileSuite('README.txt',
#            setUp=setUp,
#            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
#            ),
        unittest.makeSuite(TestSimpleJSONTree),
        unittest.makeSuite(TestGenericJSONTree),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
