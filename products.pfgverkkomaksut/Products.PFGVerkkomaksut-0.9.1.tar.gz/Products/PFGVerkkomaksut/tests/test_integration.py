import unittest
import doctest
from Testing import ZopeTestCase as ztc
from Products.PFGVerkkomaksut.tests import base

class PFGVerkkomaksutIntegrationTestCase(base.PFGVerkkomaksutTestCase):
    """Base class used for test cases
    """

    def afterSetUp( self ):
        """Code that is needed is the afterSetUp of both test cases.
        """
        ## Set up sessioning objects
        ztc.utils.setupCoreSessions(self.app)

def test_suite():
    return unittest.TestSuite([

        # Integration tests for Content Types.
        ztc.ZopeDocFileSuite(
            'tests/integration/content_types_integration.txt', package='Products.PFGVerkkomaksut',
            test_class=PFGVerkkomaksutIntegrationTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

            ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
