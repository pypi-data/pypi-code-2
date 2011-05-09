"""Lets write some unit-tests...
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """Set up the package and it depencies.
    
    First of all, to set up our package we musst be sure to install
    all depencies
    """
    
    # Load all packages, wich are included via <include /> in zcml
    fiveconfigure.debug_mode = True
    import inqbus.bannerrotation
    zcml.load_config('configure.zcml', inqbus.bannerrotation)
    fiveconfigure.debug_mode = False
    
    # Install the Package
    ztc.installPackage('inqbus.bannerrotation')
    
setup_product()
ptc.setupPloneSite(products=['inqbus.bannerrotation'])

class BannerrotaionTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """
