# -*- coding: utf-8 -*-

import doctest
import unittest
import dolmen.file
import zope.component
from zope.component.interfaces import IComponentLookup
from zope.component.testlayer import ZCMLFileLayer
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp


class DolmenFileLayer(ZCMLFileLayer):
    """Test layer for dolmen.file
    """

    def setUp(self):
        ZCMLFileLayer.setUp(self)

        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)

        # Set up traversal
        setUp()
        zope.component.provideAdapter(
            ContainerTraversable, (ISimpleReadContainer,), ITraversable)

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
        zope.component.hooks.setSite(site)
        return site

    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()


def test_suite():
    """Testing suite.
    """
    readme = doctest.DocFileSuite('README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE))
    readme.layer = DolmenFileLayer(dolmen.file)
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
