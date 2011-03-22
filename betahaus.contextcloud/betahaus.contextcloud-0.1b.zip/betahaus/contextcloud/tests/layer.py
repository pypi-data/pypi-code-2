from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import ptc
from Products.PloneTestCase import layer
from Products.Five import zcml
from Products.Five import fiveconfigure
# When using a layers capable framework (zope.testing.testrunner),
# setupPloneSite is wrapped as a deferred method
ptc.setupPloneSite(
    extension_profiles=('betahaus.contextcloud:default', )
)

class ContextCloudLayer(layer.PloneSite):
    """Configure betahaus.contextcloud"""

    @classmethod
    def setUp(cls):
        fiveconfigure.debug_mode = True
        import betahaus.contextcloud
        zcml.load_config("configure.zcml", betahaus.contextcloud)
        fiveconfigure.debug_mode = False
        ztc.installPackage("betahaus.contextcloud", quiet=1)

    @classmethod
    def tearDown(cls):
        pass
