# -*- coding: utf-8 -*-

import doctest
import unittest
import menhir.contenttype.folder
import zope.component
import zope.security.management as security

from zope.component.testlayer import ZCMLFileLayer
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager
from zope.security.testing import Principal, Participation


class MenhirTestLayer(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)
        zope.component.hooks.setHooks()

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
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
        globs={"__name__": "menhir.contenttype.folder"},
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
                     | doctest.REPORT_NDIFF))
    readme.layer = MenhirTestLayer(menhir.contenttype.folder)
    suite.addTest(readme)
    return suite
