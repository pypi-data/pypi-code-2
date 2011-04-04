# Define a common migration base class for use in all
# migration tests

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser

from Products.PloneTestCase.layer import onsetup

# Import the base test case classes
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc

from Products.CMFPlone.tests.testQueryCatalog import AddPortalTopics

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['collective.types.externalsearch',]
from OFS.Application import get_folder_permissions, get_products

@onsetup
def setup_externalsearch_types():
    import collective.types.externalsearch
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml', collective.types.externalsearch)
    zcml.load_site()
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.types.externalsearch')

setup_externalsearch_types()
ptc.setupPloneSite(products=PRODUCTS)

class Session(dict):
    def set(self, key, value):
        self[key] = value

class FakeContext(object):
    """Fake context for testing"""
    pass

class TypesTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """

    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()

    def afterSetup(self):
        #This little gem actually makes the session info
        #stick, even in doctests
        ztc.utils.setupCoreSessions(self.app)

    def makeBrowser(self):
        browser = Browser()
        browser.mech_browser.request = self.app.REQUEST

        #False shows all errors, True handles some
        browser.handleErrors = False

        return browser

class TypesFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
    def _setup(self):
        ptc.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = Session()
        
    def afterSetup(self):
        #This little gem actually makes the session info
        #stick, even in doctests
        ztc.utils.setupCoreSessions(self.app)

    def makeBrowser(self):
        browser = Browser()
        browser.mech_browser.request = self.app.REQUEST

        #False shows all errors, True handles some
        browser.handleErrors = False

        return browser
