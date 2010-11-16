import doctest
import unittest
from zope.app.testing import setup


def setUp(test):
    setup.placefulSetUp()


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(
            'z3c.widget.flashupload.ticket',
            setUp=setUp,tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp,tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))
