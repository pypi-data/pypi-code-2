# -*- coding: utf-8 -*-

from Products.Five                  import zcml
from Products.Five                  import fiveconfigure
from Testing                        import ZopeTestCase as ztc
from Products.PloneTestCase         import PloneTestCase as ptc
from Products.PloneTestCase.layer   import onsetup

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    
    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import Products.JYUDynaPage
    zcml.load_config('configure.zcml', Products.JYUDynaPage)
    fiveconfigure.debug_mode = False

    ztc.installPackage('Products.JYUDynaPage')

# The order here is important: We first call the (deferred) function
# which installs the products we need for the site. Then, we let
# PloneTestCase set up this product on installation.
setup_product()
ptc.setupPloneSite(products=['Products.JYUDynaPage'])

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class JYUDynaPageTestCase(TestCase):
    """ JYUDynaPage tests
    """
