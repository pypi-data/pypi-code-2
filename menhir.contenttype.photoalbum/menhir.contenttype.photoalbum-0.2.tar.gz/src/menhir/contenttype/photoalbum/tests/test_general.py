# -*- coding: utf-8 -*-

import doctest
import fanstatic
import menhir.contenttype.photoalbum.tests
import unittest
import zope.component
import zope.security.management as security

from ZODB.interfaces import IConnection
from persistent.interfaces import IPersistent
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.fanstatic.testing import ZopeFanstaticBrowserLayer
from zope.intid import IntIds
from zope.intid.interfaces import IIntIds
from zope.keyreference.interfaces import IKeyReference
from zope.keyreference.persistent import KeyReferenceToPersistent
from zope.keyreference.persistent import connectionOfPersistent
from zope.security.testing import Principal, Participation
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp


class TestLayer(ZopeFanstaticBrowserLayer):

    def setUp(self):
        ZopeFanstaticBrowserLayer.setUp(self)
        zope.component.hooks.setHooks()

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))

        # Set up traversal
        setUp()
        zope.component.provideAdapter(
            ContainerTraversable, (ISimpleReadContainer,), ITraversable)

        zope.component.hooks.setSite(site)

        # Register some needed utilities
        zope.component.provideUtility(IntIds(), IIntIds)

        zope.component.provideAdapter(
            connectionOfPersistent, (IPersistent,), IConnection)

        zope.component.provideAdapter(
            KeyReferenceToPersistent, (IPersistent,), IKeyReference)

        security.newInteraction(Participation(Principal('zope.mgr')))

    def tearDown(self):
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
        security.endInteraction()
        ZopeFanstaticBrowserLayer.tearDown(self)

    def setup_middleware(self, app):
        return fanstatic.Injector(app)

layer = TestLayer(menhir.contenttype.photoalbum.tests)


def test_suite():
    readme = doctest.DocFileSuite(
        '../README.txt',
        globs={'__name__': 'menhir.contenttype.photoalbum.tests'},
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    readme.layer = layer
    return unittest.TestSuite([readme])
