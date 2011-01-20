##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
import unittest
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.traversing.interfaces import ITraversable

import fanstatic
from zope.fanstatic.zopesupport import ZopeFanstaticResource
from zope.fanstatic.tests import tests

class ComputeURL(unittest.TestCase):

    layer = tests.layer

    def setUp(self):
        fanstatic.init_needed()
        self.context = object()
        self.request = TestRequest()
        self.resource_namespace  = getMultiAdapter(
            (self.context, self.request), ITraversable, name='resource')

    def test_lookup_resource(self):
        # There's a resource library registered for the name 'foo'.
        resource = self.resource_namespace.traverse('foo', [])
        self.assert_(isinstance(resource, ZopeFanstaticResource))

    def test_library_url(self):
        resource = self.resource_namespace.traverse('foo', [])
        self.assertEquals('http://127.0.0.1/fanstatic/foo', str(resource))

    def test_get(self):
        resource = self.resource_namespace.traverse('foo', [])
        a_js = resource.get('a.js')
        self.assert_(isinstance(a_js, ZopeFanstaticResource))
        self.assertEquals('http://127.0.0.1/fanstatic/foo/a.js', str(a_js))

        woekie = resource.get('bar').get('baz').get('woekie.png')
        self.assert_(isinstance(woekie, ZopeFanstaticResource))
        self.assertEquals(
            'http://127.0.0.1/fanstatic/foo/bar/baz/woekie.png', str(woekie))

    def test_getitem(self):
        resource = self.resource_namespace.traverse('foo', [])
        a_js = resource['a.js']
        self.assert_(isinstance(a_js, ZopeFanstaticResource))
        self.assertEquals('http://127.0.0.1/fanstatic/foo/a.js', str(a_js))

        woekie = resource['bar']['baz']['woekie.png']
        self.assert_(isinstance(woekie, ZopeFanstaticResource))
        self.assertEquals(
            'http://127.0.0.1/fanstatic/foo/bar/baz/woekie.png', str(woekie))

    def test_call(self):
        resource = self.resource_namespace.traverse('foo', [])
        a_js = resource.get('a.js')
        self.assertEquals(str(a_js), a_js())

