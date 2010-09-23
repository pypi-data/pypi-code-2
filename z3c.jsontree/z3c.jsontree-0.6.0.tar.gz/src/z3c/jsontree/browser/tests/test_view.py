##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
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
$Id: __init__.py 6 2006-04-16 01:28:45Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.component
import zope.principalregistry
import zope.security
from zope.app.component import testing
from zope.component import hooks
from zope.configuration.xmlconfig import XMLConfig
from zope.pagetemplate.tests.util import check_xml
from zope.publisher.browser import TestRequest
from zope.site.folder import Folder

from z3c.testing import TestCase
from z3c.jsontree.browser.tests import util
from z3c.jsontree.browser import tree
from z3c.jsontree import tests


class SimpleJSONTreeView(tree.SimpleJSONTree):

    def __init__(self, context, request):
        self.context = context
        self.request = request

class GenericJSONTreeView(tree.GenericJSONTree):

    def __init__(self, context, request):
        self.context = context
        self.request = request


class TestJSONTreeView(testing.PlacefulSetup, TestCase):

    def setUp(self):
        testing.PlacefulSetup.setUp(self, site=True)
        self.rootFolder.__name__ = 'rootFolder'
        hooks.setSite(self.rootFolder)
        import z3c.jsonrpc
        import z3c.jsontree
        import z3c.template
        import zope.app.publication
        import zope.browsermenu
        import zope.browserpage
        import zope.browserresource
        import zope.publisher
        XMLConfig('meta.zcml', z3c.jsonrpc)()
        XMLConfig('meta.zcml', z3c.template)()
        XMLConfig('meta.zcml', zope.app.publication)()
        XMLConfig('meta.zcml', zope.browsermenu)()
        XMLConfig('meta.zcml', zope.browserpage)()
        XMLConfig('meta.zcml', zope.browserresource)()
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', zope.principalregistry)()
        XMLConfig('meta.zcml', zope.publisher)()
        XMLConfig('meta.zcml', zope.security)()
        XMLConfig('configure.zcml', z3c.jsontree)()

    def tearDown(self):
        testing.PlacefulSetup.tearDown(self)
        hooks.setSite(None)

    def test_simple_tree_view_1(self):
        context = self.rootFolder['folder1']
        request = TestRequest()
        view = SimpleJSONTreeView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_1.txt'))

    def test_simple_tree_view_2(self):
        """This test includes cyrillic letters."""
        context = self.rootFolder['folder2']['folder2_1']['folder2_1_1']
        request = TestRequest()
        view = SimpleJSONTreeView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_2.txt'))

    def test_simple_tree_view_3(self):
        """This test includes cyrillic letters and maxItems."""
        context = self.rootFolder['folder1']
        for i in range(55):
            context[str(i)] = Folder()
        
        subFolder = context['1']
        request = TestRequest()
        view = SimpleJSONTreeView(subFolder, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_3.txt'))

    def test_generic_tree_view_1(self):
        context = self.rootFolder['folder1']
        request = TestRequest()
        view = GenericJSONTreeView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_1.txt'))

    def test_generic_tree_view_2(self):
        """This test includes cyrillic letters."""
        context = self.rootFolder['folder2']['folder2_1']['folder2_1_1']
        request = TestRequest()
        view = GenericJSONTreeView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_2.txt'))

    def test_generic_tree_view_3(self):
        """This test includes cyrillic letters and maxItems."""
        context = self.rootFolder['folder1']
        for i in range(55):
            context[str(i)] = Folder()
        
        subFolder = context['1']
        request = TestRequest()
        view = GenericJSONTreeView(subFolder, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_3.txt'))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestJSONTreeView),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
