##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Vault tests

"""

import doctest
import unittest
import re
from zope.testing import renormalizing
import zope.testing.module

# these are used by setup
import transaction
import persistent
from persistent.interfaces import IPersistent
from ZODB.interfaces import IConnection
from ZODB.tests.util import DB

from zope import component, interface, event
import zope.component.interfaces
from zope.app.testing import placelesssetup
from zope.app.keyreference.persistent import (
    KeyReferenceToPersistent, connectionOfPersistent)
from zope.app.folder import rootFolder
from zope.app.component.site import LocalSiteManager
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
import zope.app.component.interfaces.registration
import zope.annotation.interfaces
import zope.annotation.attribute
import zope.app.component.hooks

def setUp(test):
    placelesssetup.setUp()
    events = test.globs['events'] = []
    event.subscribers.append(events.append)
    component.provideAdapter(KeyReferenceToPersistent, adapts=(IPersistent,))
    import zope.app.component.site
    import zope.component.interfaces
    import zope.location.interfaces
    component.provideAdapter(
        zope.app.component.site.SiteManagerAdapter,
        (zope.location.interfaces.ILocation,),
        zope.component.interfaces.IComponentLookup)
    component.provideAdapter(
        connectionOfPersistent,
        adapts=(IPersistent,),
        provides=IConnection)
    test.globs['db'] = db = DB()
    test.globs['conn'] = conn = db.open()
    test.globs['root'] = root = conn.root()
    test.globs['app'] = app = root['app'] = rootFolder()
    app.setSiteManager(LocalSiteManager(app))
    transaction.commit()
    app = test.globs['app']
    sm = app.getSiteManager()
    sm['intids'] = IntIds()
    registry = zope.component.interfaces.IComponentRegistry(sm)
    registry.registerUtility(sm['intids'], IIntIds)
    transaction.commit()
    zope.app.component.hooks.setSite(app)
    zope.app.component.hooks.setHooks()
    zope.testing.module.setUp(test, 'zc.vault.README')

def tearDown(test):
    import transaction
    transaction.abort()
    zope.testing.module.tearDown(test)
    zope.app.component.hooks.resetHooks()
    zope.app.component.hooks.setSite()
    events = test.globs.pop('events')
    assert event.subscribers.pop().__self__ is events
    del events[:] # being paranoid
    transaction.abort()
    test.globs['db'].close()
    placelesssetup.tearDown()

def objectlogSetUp(test):
    setUp(test)
    from zope.app.container.contained import NameChooser
    from zope.app.container.interfaces import IWriteContainer
    component.provideAdapter(NameChooser, adapts=(IWriteContainer,))
    from zc.vault import objectlog
    component.provideAdapter(objectlog.ManifestChangesetAdapter)
    component.provideAdapter(objectlog.RelationshipChangesetAdapter)
    component.provideHandler(objectlog.createManifestLog)
    component.provideHandler(objectlog.createRelationshipLog)
    component.provideHandler(objectlog.logRemoval)
    component.provideHandler(objectlog.logAddition)
    component.provideHandler(objectlog.logOrderChanged)
    component.provideHandler(objectlog.logCommit)
    component.provideHandler(objectlog.logVersioning)
    component.provideHandler(objectlog.logNewLocal)
    component.provideHandler(objectlog.logNewSuggested)
    component.provideHandler(objectlog.logNewModified)
    component.provideHandler(objectlog.logUpdateBegun)
    component.provideHandler(objectlog.logUpdateAborted)
    component.provideHandler(objectlog.logUpdateCompleted)
    component.provideHandler(objectlog.logVaultChanged)
    component.provideHandler(objectlog.logSelection)
    component.provideHandler(objectlog.logDeselection)
    component.provideHandler(objectlog.logObjectChanged)

def catalogSetUp(test):
    setUp(test)
    from zope.app.container.contained import NameChooser
    from zope.app.container.interfaces import IWriteContainer
    component.provideAdapter(NameChooser, adapts=(IWriteContainer,))
    from zc.vault import catalog
    component.provideHandler(catalog.makeReferences)
    component.provideHandler(catalog.updateCompleted)
    component.provideHandler(catalog.updateAborted)
    component.provideHandler(catalog.manifestCreated)
    component.provideHandler(catalog.relationshipSelected)
    component.provideHandler(catalog.relationshipDeselected)
    component.provideHandler(catalog.objectChanged)

def traversalSetUp(test):
    setUp(test)
    import zc.copy
    component.provideAdapter(zc.copy.location_copyfactory)
    import zc.freeze.copier
    component.provideAdapter(zc.freeze.copier.data_copyfactory)
    component.provideAdapter(zc.copy.ObjectCopier)
    import zc.shortcut.adapters
    component.provideAdapter(zc.shortcut.adapters.ObjectLinkerAdapter)

def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile(r'^\d+$', re.M), '1234567'),
        ])

    tests = (
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown, checker=checker),
        doctest.DocFileSuite(
            'versions.txt',
            setUp=setUp, tearDown=tearDown),
        # separate this out so this only runs if pertinent modules available?
        doctest.DocFileSuite(
            'catalog.txt',
            setUp=catalogSetUp, tearDown=tearDown),
        )

    try:
        import zc.objectlog
        tests += (
            doctest.DocFileSuite(
                'objectlog.txt',
                setUp=objectlogSetUp, tearDown=tearDown),)
    except ImportError:
        # no zc.objectlog available, so don't try to test integration with it
        pass

    try:
        import zc.shortcut
        normalize_string_checker = renormalizing.RENormalizing([
            (re.compile(r"\bu('[^']*')"), r'\1'),
            ])
        tests += (doctest.DocFileSuite(
                    'traversal.txt',
                    checker=normalize_string_checker,
                    setUp=traversalSetUp, tearDown=tearDown),)
    except ImportError:
        pass

    return unittest.TestSuite(tests)
