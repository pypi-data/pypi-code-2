from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
import collective.amberjack.core
import os

os.environ['INSTANCE_HOME'] = '/tmp'

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.amberjack.core)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.amberjack.core')
    
setup_product()
ptc.setupPloneSite(products=['collective.amberjack.core'])

class AmberjackCoreTestCase(ptc.PloneTestCase):
    """ """
