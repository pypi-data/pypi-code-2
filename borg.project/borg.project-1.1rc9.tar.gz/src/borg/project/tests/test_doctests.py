import unittest
import doctest

from Testing import ZopeTestCase as ztc

from base import BorgProjectFunctionalTestCase

def test_suite():
    return unittest.TestSuite([

        ztc.ZopeDocFileSuite(
            'README.txt', package='borg.project',
            test_class=BorgProjectFunctionalTestCase,
            optionflags=(doctest.ELLIPSIS | 
                         doctest.NORMALIZE_WHITESPACE)),
            ])
        
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


