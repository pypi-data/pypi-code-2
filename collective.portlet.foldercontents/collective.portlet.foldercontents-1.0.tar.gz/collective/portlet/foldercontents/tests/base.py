from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_collective_portlet_foldercontents():
    """Set up additional products and ZCML required to test this product.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for this package and its dependencies

    fiveconfigure.debug_mode = True
    import collective.portlet.foldercontents
    zcml.load_config('configure.zcml', collective.portlet.foldercontents)
    fiveconfigure.debug_mode = False


# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_collective_portlet_foldercontents()
ptc.setupPloneSite(products=['collective.portlet.foldercontents'])


class PortletFoldercontentsTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """