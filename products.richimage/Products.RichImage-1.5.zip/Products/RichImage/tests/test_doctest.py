from unittest import TestSuite
from zope.testing import doctest
from Testing.ZopeTestCase import ZopeDocFileSuite
from Products.RichImage.tests.base import RichImageFunctionalTestCase


optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite((
        ZopeDocFileSuite(
           'browser.txt', package='Products.RichImage.tests',
           test_class=RichImageFunctionalTestCase, optionflags=optionflags),
    ))

