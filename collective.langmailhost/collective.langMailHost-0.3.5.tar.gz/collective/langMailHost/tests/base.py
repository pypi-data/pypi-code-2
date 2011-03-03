from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_langMailHost():

    fiveconfigure.debug_mode = True
    import collective.langMailHost
    zcml.load_config('configure.zcml', collective.langMailHost)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.langMailHost')
#    ztc.installProduct('collective.MockMailHost')
    ztc.installPackage('Products.LinguaPlone')

# The order here is important: We first call the (deferred) function which
# installs the products we need for the Mall package. Then, we let 
# PloneTestCase set up this product on installation.

setup_langMailHost()
ptc.setupPloneSite(products=['collective.langMailHost'])

class MailHostTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

#    def afterSetUp( self ):
#        """Code that is needed is the afterSetUp of both test cases.
#        """

class MailHostFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
