# -*- coding: utf-8 -*-

import unittest
import zope.component
import dolmen.app.breadcrumbs

from zope.component import eventtesting
from zope.component.interfaces import IComponentLookup
from zope.component.testlayer import ZCMLFileLayer
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.testing import doctest
from zope.traversing.testing import setUp as traversingSetUp


class BreadcrumbTestLayer(ZCMLFileLayer):
    """The dolmen.app.breadcrumbs main test layer.
    """

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        eventtesting.setUp()
        traversingSetUp()

        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
        zope.component.hooks.setSite(site)

        return site

    def tearDown(self):
        ZCMLFileLayer.tearDown(self)
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE))
    readme.layer = BreadcrumbTestLayer(dolmen.app.breadcrumbs)
    suite.addTest(readme)
    return suite
