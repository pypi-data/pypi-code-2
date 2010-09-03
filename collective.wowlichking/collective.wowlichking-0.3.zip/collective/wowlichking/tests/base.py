from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():

    fiveconfigure.debug_mode = True
    import wow.char
    zcml.load_config('configure.zcml', wow.char)
    import inquant.wow
    zcml.load_config('configure.zcml', inquant.wow)
    fiveconfigure.debug_mode = False

    ztc.installPackage('wow.char')
    ztc.installPackage('inquant.wow')

setup_product()
ptc.setupPloneSite(products=['wow.char', 'inquant.wow'])

class ExampleTestCase(ptc.PloneTestCase):

class ExampleFunctionalTestCase(ptc.FunctionalTestCase):
