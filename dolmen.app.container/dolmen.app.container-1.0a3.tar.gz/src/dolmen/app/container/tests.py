# -*- coding: utf-8 -*-

import doctest
import unittest
import dolmen.app.container
import zope.component
from zope.component.interfaces import IComponentLookup
from zope.configuration import xmlconfig
from zope.container.interfaces import ISimpleReadContainer
from zope.container.traversal import ContainerTraversable
from zope.interface import Interface
from zope.security.management import newInteraction, endInteraction
from zope.security.testing import Principal, Participation
from zope.site.folder import rootFolder
from zope.site.hooks import getSite
from zope.site.site import LocalSiteManager, SiteManagerAdapter
from zope.testing import module
from zope.traversing.interfaces import ITraversable
from zope.traversing.testing import setUp


def SiteSetUp(test):
    module.setUp(test, 'dolmen.app.container.ftests')

    zope.component.hooks.setHooks()

    # Set up site manager adapter
    zope.component.provideAdapter(
        SiteManagerAdapter, (Interface,), IComponentLookup)

    # Set up traversal
    setUp()
    zope.component.provideAdapter(
        ContainerTraversable, (ISimpleReadContainer,), ITraversable)

    xmlconfig.file('ftesting.zcml', dolmen.app.container)

    # Set up site
    site = rootFolder()
    site.setSiteManager(LocalSiteManager(site))
    zope.component.hooks.setSite(site)

    # Creating a simple interaction with "manager"
    participation = Participation(Principal('zope.mgr'))
    newInteraction(participation)


def tearDown(test):
    module.tearDown(test)
    endInteraction()
    zope.component.hooks.resetHooks()
    zope.component.hooks.setSite()


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt', setUp=SiteSetUp, tearDown=tearDown,
        globs={"getSite": getSite},
        optionflags=(doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE),
        )
    #readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
