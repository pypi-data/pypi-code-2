from Products.Five import zcml
from Products.Five import fiveconfigure

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_collective_portlet_wordpress():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for this package and its dependencies

    fiveconfigure.debug_mode = True
    import collective.portlet.wordpress
    zcml.load_config('configure.zcml', collective.portlet.wordpress)
    fiveconfigure.debug_mode = False

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_collective_portlet_wordpress()
ptc.setupPloneSite(products=['collective.portlet.wordpress'])


class PortletWordPressBlogTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
