import doctest
import unittest

import transaction
import ZODB.DB
import ZODB.MappingStorage
import zope.app.container.tests.placelesssetup
import zope.app.testing.placelesssetup
import zope.component
import zope.component.eventtesting
import zope.component.testing
import zope.event
import zope.testing.module


def setUp(test):
    zope.app.testing.placelesssetup.setUp(test)
    events = test.globs['events'] = []
    zope.event.subscribers.append(events.append)

def tearDown(test):
    zope.app.testing.placelesssetup.tearDown(test)
    events = test.globs.pop('events')
    assert zope.event.subscribers.pop().__self__ is events
    del events[:] # being paranoid

def subscribersSetUp(test):
    import zope.locking.interfaces
    import zope.locking.utility
    import zc.freeze.testing
    zope.app.testing.placelesssetup.setUp(test)
    zope.testing.module.setUp(test, 'zc.freeze.subscribers_txt')
    test.globs['db'] = db = ZODB.DB(ZODB.MappingStorage.MappingStorage())
    test.globs['conn'] = conn = db.open()
    test.globs['Demo'] = zc.freeze.testing.Demo
    zope.component.provideAdapter(zc.freeze.testing.DemoKeyReference)
    test.globs['util'] = util = zope.locking.utility.TokenUtility()
    conn.add(util)
    zope.component.provideUtility(
        util, provides=zope.locking.interfaces.ITokenUtility)
    test.globs['events'] = events = []
    zope.event.subscribers.append(events.append)

def subscribersTearDown(test):
    zope.testing.module.tearDown(test)
    zope.app.testing.placelesssetup.tearDown(test)
    transaction.abort()
    test.globs['conn'].close()
    test.globs['db'].close()
    events = test.globs.pop('events')
    assert zope.event.subscribers.pop().__self__ is events
    del events[:] # being paranoid


def copierSetUp(test):
    zope.testing.module.setUp(test, 'zc.freeze.copier_txt')
    zope.component.testing.setUp(test)
    zope.component.eventtesting.setUp(test)
    container_setup = zope.app.container.tests.placelesssetup.PlacelessSetup()
    container_setup.setUp()

def copierTearDown(test):
    zope.testing.module.tearDown(test)
    zope.component.testing.tearDown(test)

def test_suite():
    tests = (
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'copier.txt',
            setUp=copierSetUp,
            tearDown=copierTearDown),
        )
    try:
        import zope.locking
    except ImportError:
        pass
    else:
        tests += (
            doctest.DocFileSuite(
                'subscribers.txt',
                setUp=subscribersSetUp,
                tearDown=subscribersTearDown
                ),
            )

    return unittest.TestSuite(tests)
