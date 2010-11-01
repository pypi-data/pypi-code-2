import doctest
import unittest
from zope.app.testing import setup
from zope.component import provideAdapter
from zope.interface import Interface
from zope.publisher.interfaces.http import IHTTPRequest
import zope.traversing.testing

from z3c.traverser.stackinfo.traversing import UnconsumedURL

def setUp(test):
    root = setup.placefulSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root
    provideAdapter(UnconsumedURL, (Interface, IHTTPRequest), Interface,
                   name='unconsumed_url')

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
