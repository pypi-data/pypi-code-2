from Testing import ZopeTestCase as ztc

from Products.Five import zcml, fiveconfigure

from Products.PloneTestCase import layer
from Products.PloneTestCase import PloneTestCase as ptc

SiteLayer = layer.PloneSite


class BorgProjectLayer(SiteLayer):
    ptc.installProduct('CMFPlacefulWorkflow')

    @classmethod
    def getPortal(cls):
        app = ZopeTestCase.app()
        portal = app._getOb(portal_name)
        _placefulSetUp(portal)
        return portal

    @classmethod
    def setUp(cls):

        ztc.installProduct('borg.project')

        ptc.setupPloneSite(products=(
            'CMFPlacefulWorkflow', 
            ), extension_profiles=(
                u'borg.project:default',
            ))

        fiveconfigure.debug_mode = True
        import borg.project
        zcml.load_config('configure.zcml', borg.project)
        import Products.CMFPlacefulWorkflow
        zcml.load_config('configure.zcml', Products.CMFPlacefulWorkflow)
        fiveconfigure.debug_mode = False
    
        # We need to tell the testing framework that these products
        # should be available. This can't happen until after we have loaded
        # the ZCML. Notice the extra package=True argument passed to 
        # installProduct() - this tells it that these packages are *not* in the
        # Products namespace.
    
        ztc.installPackage('borg.localrole')
        ztc.installPackage('borg.project')
        SiteLayer.setUp()

class BorgProjectFunctionalTestCase(ptc.FunctionalTestCase):
    layer = BorgProjectLayer
