from Products.Five import zcml
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import PloneSite


class RichImageLayer(PloneSite):

    @classmethod
    def setUp(cls):
        ztc.installPackage('plone.app.blob', quiet=True)

    @classmethod
    def tearDown(cls):
        pass
