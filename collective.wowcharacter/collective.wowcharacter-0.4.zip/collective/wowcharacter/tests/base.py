from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():

    fiveconfigure.debug_mode = True
    import collective.wowcharacter
    zcml.load_config('configure.zcml', collective.wowcharacter)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.wowcharacter')

setup_product()
ptc.setupPloneSite(products=['collective.wowcharacter'])

class ExampleTestCase(ptc.PloneTestCase):
    """ """

class ExampleFunctionalTestCase(ptc.FunctionalTestCase):
    """ """
