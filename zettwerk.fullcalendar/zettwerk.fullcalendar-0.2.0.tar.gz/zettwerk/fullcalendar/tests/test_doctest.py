import unittest
import doctest

#from zope.testing import doctestunit
#from zope.component import testing, eventtesting

from Testing import ZopeTestCase as ztc

from zettwerk.fullcalendar.tests import base


def test_suite():
    return unittest.TestSuite([

        # Demonstrate the main content types
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='zettwerk.fullcalendar',
        #    test_class=base.FunctionalTestCase,
        #    optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
        #        doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # Unit tests
        #doctestunit.DocFileSuite(
        #   'README.txt', package='zettwerk.fullcalendar',
        #   setUp=testing.setUp, tearDown=testing.tearDown),
        
        #doctestunit.DocTestSuite(
        #   module='zettwerk.fullcalendar.mymodule',
        #   setUp=testing.setUp, tearDown=testing.tearDown),
        
        # Integration tests that use PloneTestCase        
        #ztc.ZopeDocFileSuite(
        #   'README.txt', package='zettwerk.fullcalendar',
        #   test_class=TestCase),
        
        #ztc.FunctionalDocFileSuite(
        #   'browser.txt', package='zettwerk.fullcalendar',
        #   test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
