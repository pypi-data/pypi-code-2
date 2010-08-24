import unittest
import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.annotationbrowser import testing

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def test_suite():
    suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        package='collective.annotationbrowser',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    suite.layer = testing.layer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
