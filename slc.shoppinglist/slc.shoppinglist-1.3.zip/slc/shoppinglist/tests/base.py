from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite

class SLCShoppinglistLayer(SiteLayer):
    @classmethod
    def setUp(cls):
        """Set up additional products and ZCML required to test this product.
        """
        ptc.setupPloneSite(products=['slc.shoppinglist'])

        # Load the ZCML configuration for this package and its dependencies

        fiveconfigure.debug_mode = True
        import slc.shoppinglist
        zcml.load_config('configure.zcml', slc.shoppinglist)
        fiveconfigure.debug_mode = False

        # We need to tell the testing framework that these products
        # should be available. This can't happen until after we have loaded
        # the ZCML.

        ztc.installPackage('slc.shoppinglist')
        SiteLayer.setUp()

# The order here is important: We first call the deferred function and then 
# let PloneTestCase install it during Plone site setup

class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    layer = SLCShoppinglistLayer

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    layer = SLCShoppinglistLayer
