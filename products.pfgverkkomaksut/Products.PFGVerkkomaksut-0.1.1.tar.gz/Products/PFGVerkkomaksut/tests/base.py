from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_pfg_verkkomaksut():

    fiveconfigure.debug_mode = True

    import Products.PloneFormGen
    zcml.load_config('configure.zcml', Products.PloneFormGen)
    import Products.PFGVerkkomaksut
    zcml.load_config('configure.zcml', Products.PFGVerkkomaksut)

    fiveconfigure.debug_mode = False

#    ztc.installPackage('Products.PloneFormGen')
#    ztc.installPackage('Products.PFGVerrkkomaksut')
    ztc.installProduct('PloneFormGen')
    ztc.installProduct('PFGVerkkomaksut')

setup_pfg_verkkomaksut()
ptc.setupPloneSite(products=['PloneFormGen', 'PFGVerkkomaksut'])
class PFGVerkkomaksutTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package.
    If necessary, we can put common utility or setup code in here.
    """

class PFGVerkkomaksutFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
