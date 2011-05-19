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
    zcml.load_config('configure.zcml', inqbus.folderlistings)
    fiveconfigure.debug_mode = False

    # Install the Package
    ztc.installPackage('inqbus.folderlistings')

setup_product()
ptc.setupPloneSite(products=['inqbus.folderlistings'])

class FolderlistingsTestCase(ptc.PloneTestCase):
    """
    """