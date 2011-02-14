# -*- coding: utf-8 -*-

import doctest
import unittest
import menhir.contenttype.image
import zope.component
import zope.security.management as security

from zope.component.testlayer import ZCMLFileLayer
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager
from zope.security.testing import Principal, Participation
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable


class MenhirTestLayer(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        zope.component.hooks.setHooks()

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))

        # Set up traversal
        setUp()
        zope.component.provideAdapter(
            ContainerTraversable, (ISimpleReadContainer,), ITraversable)

        zope.component.hooks.setSite(site)
        security.newInteraction(Participation(Principal('zope.mgr')))

    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
        security.endInteraction()
        ZCMLFileLayer.tearDown(self)


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        globs={"__name__": "menhir.contenttype.image"},
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    readme.layer = MenhirTestLayer(menhir.contenttype.image)
    suite.addTest(readme)
    return suite
