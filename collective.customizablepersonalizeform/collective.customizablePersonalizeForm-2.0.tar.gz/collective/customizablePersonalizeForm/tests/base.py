"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_product():
    """Set up the package and its dependencies.
    """

    fiveconfigure.debug_mode = True
    import collective.customizablePersonalizeForm
    zcml.load_config('configure.zcml', collective.customizablePersonalizeForm)
    zcml.load_config('overrides.zcml', collective.customizablePersonalizeForm)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.customizablePersonalizeForm')

setup_product()
ptc.setupPloneSite(products=['collective.customizablePersonalizeForm'])

class CollectiveCPFTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

class CollectiveCPFFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
