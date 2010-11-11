import unittest
from zope.testing import doctest
from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

from collective.redirect import testing

def test_suite():
    install_suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    install_suite.layer = testing.install_layer
    return install_suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
