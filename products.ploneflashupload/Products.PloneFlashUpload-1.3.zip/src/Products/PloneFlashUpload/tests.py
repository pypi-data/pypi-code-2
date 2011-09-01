import unittest
from zope.testing import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

optionflags = (doctest.NORMALIZE_WHITESPACE |
               doctest.ELLIPSIS |
               doctest.REPORT_NDIFF)

ptc.setupPloneSite()


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite('Products.PloneFlashUpload.ticket'),
        doctest.DocTestSuite('Products.PloneFlashUpload.browser'),
        doctest.DocTestSuite('Products.PloneFlashUpload.atct'),
        ZopeTestCase.FunctionalDocFileSuite(
            'functional.txt',
            optionflags=optionflags,
            test_class=ptc.FunctionalTestCase)
        ))
