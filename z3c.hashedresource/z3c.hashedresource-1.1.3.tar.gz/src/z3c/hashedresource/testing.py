#############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""tests

$Id: test_directoryresource.py 95447 2009-01-29 16:28:18Z wosc $
"""
from z3c.hashedresource import interfaces
import os
import re
import shutil
import tempfile
import z3c.hashedresource.tests
import zope.app.testing.functional
import zope.publisher.browser
import zope.security.checker
import zope.site


fixture = os.path.join(
    os.path.dirname(z3c.hashedresource.tests.__file__), 'fixture')

checker = zope.security.checker.NamesChecker(
    ('get', '__getitem__', 'request', 'publishTraverse')
    )

HashedResourcesLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting-devmode.zcml'),
    __name__, 'HashedResourcesLayer', allow_teardown=True)


class TestRequest(zope.publisher.browser.TestRequest):

    zope.interface.implements(interfaces.IHashedResourceSkin)


class FunctionalTestCase(zope.app.testing.functional.FunctionalTestCase):

    layer = HashedResourcesLayer

    def assertMatches(self, regex, text):
        self.assert_(re.match(regex, text), "/%s/ did not match '%s'" % (
            regex, text))

    def setUp(self):
        super(FunctionalTestCase, self).setUp()
        self.site = zope.site.hooks.getSite()

        self.tmpdir = tempfile.mkdtemp()
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('')
        self.dirname = os.path.basename(self.tmpdir)

        self.request = TestRequest()
        self.request._vh_root = self.site
        self.directory = zope.app.publisher.browser.directoryresource.DirectoryResourceFactory(
            self.tmpdir, checker, self.dirname)(self.request)
        self.directory.__parent__ = self.site

    def tearDown(self):
        super(FunctionalTestCase, self).tearDown()
        shutil.rmtree(self.tmpdir)

    def _hash(self, text):
        return re.match('http://127.0.0.1/\+\+noop\+\+([^/]*)/.*', text).group(1)
