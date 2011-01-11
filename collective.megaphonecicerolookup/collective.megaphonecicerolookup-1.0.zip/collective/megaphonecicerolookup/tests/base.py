from Products.PloneTestCase import PloneTestCase as ptc
from collective.megaphonecicerolookup.tests.layer import MegaphoneCiceroLayer

ptc.setupPloneSite()


class MegaphoneCiceroTestCase(ptc.FunctionalTestCase):
    """Base class for Megaphone-Cicero integration tests.
    """
    layer = MegaphoneCiceroLayer