# -*- coding: utf-8 -*-

import unittest
import doctest
import dolmen.app.site
import zope.component

from zope.interface import Interface
from zope.component.interfaces import IComponentLookup
from zope.app.wsgi.testlayer import BrowserLayer
from zope.site.site import SiteManagerAdapter


class TestLayer(BrowserLayer):

    def setUp(self):
        zope.component.hooks.setHooks()

        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)

    def tearDown(test):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()


def test_suite():
    suite = unittest.TestSuite()

    app_test = doctest.DocFileSuite('README.txt',
        optionflags=(
            doctest.ELLIPSIS +
            doctest.NORMALIZE_WHITESPACE +
            doctest.REPORT_NDIFF))
    app_test.layer = TestLayer(dolmen.app.site)

    suite.addTest(app_test)
    return suite
