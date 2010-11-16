from zope.app.testing import setup
import doctest
import unittest


def setUp(test):
    setup.placefulSetUp(True)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
