import unittest

from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc

from Products.PloneTestCase.layer import onsetup
import collective.geo.mapcontent

@onsetup
def setup_product():
    """
       Set up the package and its dependencies.
    """
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.geo.mapcontent)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.geo.mapcontent')

setup_product()
ptc.setupPloneSite(products=['collective.geo.mapcontent'])

class TestCase(ptc.PloneTestCase): pass

def setUp(test): pass

def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'README.txt', package='collective.geo.mapcontent',
            test_class=TestCase,
            setUp=setUp,
            globs=globals(),
        ),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
