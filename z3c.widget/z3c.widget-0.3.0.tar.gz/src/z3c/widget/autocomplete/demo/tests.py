import doctest
import unittest
from zope.app.testing import setup


def setUp(test):
    setup.placefulSetUp(True)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return doctest.DocTestSuite(
        'z3c.widget.autocomplete.demo.countries',
        setUp=setUp,tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
