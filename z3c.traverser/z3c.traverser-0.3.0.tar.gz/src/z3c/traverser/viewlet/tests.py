import doctest
import unittest

import zope.traversing.testing
from zope.app.testing import setup
from zope.traversing.browser import AbsoluteURL, SiteAbsoluteURL
from zope.traversing.browser.interfaces import IAbsoluteURL
from zope.traversing.interfaces import IContainmentRoot
from zope.traversing.testing import browserView

def setUp(test):
    root = setup.placefulSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root

    browserView(None, 'absolute_url', AbsoluteURL)
    browserView(IContainmentRoot, 'absolute_url', SiteAbsoluteURL)
    browserView(None, '', AbsoluteURL, providing=IAbsoluteURL)
    browserView(IContainmentRoot, '', SiteAbsoluteURL, providing=IAbsoluteURL)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
