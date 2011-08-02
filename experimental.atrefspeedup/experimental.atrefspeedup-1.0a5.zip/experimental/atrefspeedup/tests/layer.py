from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc


class ATRefSpeedupLayer(BasePTCLayer):
    """ layer for integration tests """

    def afterSetUp(self):
        import experimental.atrefspeedup
        fiveconfigure.debug_mode = True
        zcml.load_config("configure.zcml", experimental.atrefspeedup)
        fiveconfigure.debug_mode = False
        ztc.installPackage("experimental.atrefspeedup", quiet=True)

        # Add us a second reference field
        from Products.ATContentTypes.content.schemata import relatedItemsField
        rel2 = relatedItemsField.copy()
        rel2.relationship = 'rel2'
        rel2.__name__ = 'rel2'

        from Products.ATContentTypes.content.document import ATDocument
        ATDocument.schema.addField(rel2)

        from Products.Archetypes.ClassGen import generateMethods as atgm
        atgm(ATDocument, (ATDocument.schema.get('rel2'), ))

        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')

    def beforeTearDown(self):
        pass


atrefspeedup = ATRefSpeedupLayer(bases=[ptc_layer])
